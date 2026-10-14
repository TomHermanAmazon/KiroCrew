"""Argv floor for the two recursive-force ``rm`` catalog rules.

The catalog patterns ``rm -rf /.*`` and ``rm -rf ~.*`` match one spelling; a shell
runs the same wipe for ``rm -fr /``, ``rm -r -f /``, ``rm --recursive --force /`` and
``rm -rf $HOME``. This floor reads each ``rm`` command's own words: recursive and
force in any packing, order or long form, against the root or home ITSELF. A
descendant, a wrapper or an interpreter body is left to the regex and the sandbox.

Frames descend through unexpanded shell payloads (``bash -c``, ``$(...)``), kept as
written: ``\\x2f`` in shell source is text. Only an ``env -S`` or ``sed …e`` string is
also read printf-decoded. Words keep which characters were quoted, so ``'~'``,
``'$HOME'`` and ``'/*'`` are literal; comments, heredoc bodies and redirections are no
operands. A body only a data consumer receives (``echo bash -c '...'``), or a
substitution in single quotes, a comment, a quoted heredoc or after ``\\$`` in an
unquoted one, prints rather than runs.
"""

from __future__ import annotations

import os
import posixpath
import re
from typing import NamedTuple

from ..trust_patterns import ENV_ASSIGNMENT_RE
from . import shell_normalizer as _shell
from .denied_rules import BUILTIN_DENIED_RULES

#: The catalog row each wipe target maps to. The floor is gated on that row's
#: pattern, so an operator who disables the row disables the floor with it.
_RM_FLOOR_RULE_IDS: dict[str, str] = {
    "root": "local-destructive-rm-rf-root",
    "home": "local-destructive-rm-rf-home",
}
_RM_FLOOR_BY_KIND: dict[str, tuple[str, str]] = {
    kind: (rule.id, rule.pattern)
    for kind, rule_id in _RM_FLOOR_RULE_IDS.items()
    for rule in BUILTIN_DENIED_RULES
    if rule.id == rule_id
}
_RM_FLOOR_NOTE = (
    "Matched structurally on the command's argv, not by the pattern text above: "
    "rm with recursive and force flags, in any spelling, targets this directory itself."
)
_RM_FLOOR_UNREAD_NOTE = (
    "Refused because the rm floor could not read this command (too deeply nested "
    "or unparseable), so it cannot rule out a wipe of this directory. Simplify it."
)

_ROOT_RE = re.compile(r"/+")
# ``${HOME:-x}`` / ``${HOME:?}`` / ``${HOME:=x}`` are HOME whenever it is set;
# ``${HOME:+x}`` is the alternate text instead, so it is not listed.
_HOME_VAR_RE = re.compile(r"\$(?:HOME(?![A-Za-z0-9_])|\{HOME(?:\}|:?[-?=]))")
_OPERATORS = ";&|\n()"
_SUBSTITUTION_OPENERS = ("$(", "<(", ">(", "`")
# Words that end one pipeline (a ``&`` after ``|`` is ``|&``, still the same pipe),
# and the reserved words that open and close a group one pipe can read whole.
_PIPELINE_ENDS = frozenset({";", "&&", "||", "&", "\n"})
_GROUP_OPENERS = frozenset({"{", "if", "while", "until", "for", "select"})
_GROUP_CLOSERS = frozenset({"}", "fi", "done"})

#: One word: its text with quotes removed, and per character whether the shell
#: would expand it (``u`` unquoted, ``d`` inside double quotes, ``s`` literal).
_Word = tuple[str, str]


class _Scan(NamedTuple):
    words: "list[_Word]"
    #: Offsets (in the decoded text) of ``$`` / `` ` `` / ``<`` / ``>`` that can
    #: open a substitution the shell runs.
    live: "set[int]"
    text: str
    #: Quote-open/close offsets within each word, including empty quoting runs.
    quote_breaks: "dict[int, set[int]]"
    #: Indexes of words inside a ``((…))`` arithmetic expression: never a program.
    arith_words: "frozenset[int]" = frozenset()
    #: Indexes of ``)`` words after which a new command starts: a case-arm pattern
    #: close, or a group close. A ``$(`` / ``<(`` / ``>(`` or array close is not one.
    command_closes: "frozenset[int]" = frozenset()
    #: ``$(`` / ``<(`` / ``>(`` spans: the word ending in the opener -> its ``)``.
    substitutions: "dict[int, int] | None" = None
    #: Words glued to the ``)`` before them, so one shell word with it.
    glued: "frozenset[int]" = frozenset()


def _heredoc_end(source: str, start: int, tags: "list[tuple[str, bool, bool]]") -> int:
    """Offset just past the heredoc bodies that begin at *start*."""
    pos = start
    for tag, strip_tabs, _expands in tags:
        while pos < len(source):
            end = source.find("\n", pos)
            line = source[pos : len(source) if end == -1 else end]
            pos = len(source) if end == -1 else end + 1
            if (line.lstrip("\t") if strip_tabs else line) == tag:
                break
    return pos


_MAX_MATH_DEPTH = 64
_SPLIT_FLAGS = frozenset({"-S", "-s", "--split-string"})
_SPLIT_GLUED_RE = re.compile(r"-[sS](?=.)|--split-string=")
#: In an unquoted-tag heredoc body ``\$`` / ``\``` print; ``\\`` is one backslash.
_HEREDOC_OPENER_RE = re.compile(r"\\[$`\\\n]|[$`]")


def _opens_expansion(text: "list[str]", kinds: "list[str]") -> bool:
    """True when *text* ends in an unpaired unquoted ``$``: ``$$`` is the PID."""
    run = 0
    while run < len(text) and text[-1 - run] == "$" and kinds[-1 - run] == "u":
        run += 1
    return run % 2 == 1


def _scan(source: str) -> _Scan:
    """Split one command line into words and control operators, keeping quote kinds.

    ANSI-C and locale quoting are resolved first by the shared decoder, which
    re-quotes any value that must stay literal. An unquoted ``#`` at a word start
    drops the rest of the line, and a heredoc body is dropped through its tag line;
    an unquoted-tag heredoc body still expands substitutions, a quoted one does not.
    """
    source = _shell._decode_shell_quoted_literals(_shell._fold_line_continuations(source))
    words: list[_Word] = []
    quote_breaks: dict[int, set[int]] = {}
    live: set[int] = set()
    text: list[str] = []
    kinds: list[str] = []
    started = False
    # (tag, strip tabs, body expands)
    tags: list[tuple[str, bool, bool]] = []
    base = 0
    # One entry per unclosed ``(``, True inside ``((`` / ``$((`` arithmetic, where
    # ``<<`` is a shift: no heredoc tag is read there. A ``$(`` or subshell keeps them.
    parens: list[bool] = []
    # (offset, first word) per unclosed ``(``. Bash reads ``((`` as arithmetic only
    # when its inner ``(`` closes right before the outer one: ``((a))`` is math,
    # ``((a) )`` and ``((a) || (b))`` are subshells.
    opens: list[tuple[int, int]] = []
    arith_words: set[int] = set()
    # One entry per unclosed ``(``: the opener word of a substitution, -1 for a
    # command group (its ``)`` lets a new command follow), -2 for an array.
    open_kinds: list[int] = []
    command_closes: set[int] = set()
    substitutions: dict[int, int] = {}
    glued: set[int] = set()
    # The closers of the unclosed ``${`` / ``$[`` the current word is inside.
    braces: list[str] = []
    # Live offsets inside the current word.
    word_live: list[int] = []

    def _end() -> None:
        nonlocal started
        if started:
            word = ("".join(text), "".join(kinds))
            arith = bool(parens and parens[-1])
            prev = words[-1] if words and not arith else ("", "")
            # Any quote in the tag, even an empty ``E''OF``, makes the body literal.
            breaks = quote_breaks.get(len(words), set())
            count = len(tags)
            if prev[0] in ("<<", "<<-") and prev[1] in ("uu", "uuu"):
                tags.append((word[0], prev[0] == "<<-", set(word[1]) <= {"u"} and not breaks))
            elif word[0].startswith("<<") and word[1][:2] == "uu" and word[0][2:3] != "<":
                marker = _shell._heredoc_marker(word[0])
                if marker and not arith:
                    dash = word[0].startswith("<<-")
                    cut = 3 if dash else 2
                    plain = set(word[1][cut:]) <= {"u"} and all(at < cut for at in breaks)
                    tags.append((marker, dash, plain))
            if len(tags) > count:
                # A delimiter only loses its quotes: ``<<"$(x)"`` runs nothing.
                live.difference_update(word_live)
            words.append(word)
        text.clear()
        kinds.clear()
        word_live.clear()
        started = False

    while base <= len(source):
        restart = None
        for step in _shell._iter_shell_chars(source[base:]):
            char = step.char
            at = base + step.offset
            if len(step.text) == 1 and step.state != 1 and char in "$`<>":
                live.add(at)
                word_live.append(at)
            if len(step.text) == 2 or step.trailing_escape:
                # In double quotes a backslash escapes only these; before any
                # other character it stays, so ``"\/"`` is the name ``\/``.
                if len(step.text) == 2 and step.state == 2 and char not in '$`"\\\n':
                    text.append("\\")
                    kinds.append("s")
                text.append(char)
                kinds.append("s")
                started = True
            elif char in "'\"" and (step.active or step.state == 0):
                quote_breaks.setdefault(len(words), set()).add(len(text))
                started = True
            elif not step.active:
                text.append(char)
                kinds.append("d" if step.state == 2 else "s")
            elif braces or (
                char in "{["
                and _opens_expansion(text, kinds)
                # ``${ cmd; }`` / ``${| cmd; }`` run a command (bash 5.3): not a word.
                and (char == "[" or source[at + 1 : at + 2].strip() not in ("", "|"))
            ):
                # ``${…}`` / ``$[…]`` is one word up to its closer: a space, an
                # operator or ``<<`` inside it splits nothing (``$[ 1 << 2 ]``).
                if braces and char == braces[-1]:
                    braces.pop()
                elif char in "{[" and _opens_expansion(text, kinds):
                    braces.append("}" if char == "{" else "]")
                text.append(char)
                kinds.append("u")
                started = True
            elif char == "#" and not started:
                # A comment runs to the newline whatever quotes it holds: resume
                # unquoted there (``# don't`` opens no quote).
                newline = source.find("\n", at)
                restart = None if newline == -1 else newline
                break
            elif char == "`" and (close := _shell._backtick_closer(source, at + 1)) != -1:
                # One word with the enclosing argv; its body is a frame of its own.
                text.extend(source[at : close + 1])
                kinds.extend("s" * (close + 1 - at))
                started = True
                restart = close + 1
                break
            elif char.isspace() and char != "\n":
                _end()
            elif (
                char == "&"
                and source[at + 1 : at + 2] == ">"
                or (char == "&" and text and text[-1] in "<>")
            ):
                text.append(char)
                kinds.append("u")
                started = True
            elif char == "(" and text and text[-1] == "=":
                # ``a=(...)`` is an array assignment, not a subshell.
                text.append(char)
                kinds.append("u")
                parens.append(False)
                opens.append((at, len(words)))
                open_kinds.append(-2)
            elif char in _OPERATORS:
                substitution = char == "(" and bool(text) and text[-1] in "$<>" and kinds[-1] == "u"
                _end()
                if char == "(":
                    parens.append(bool(parens and parens[-1]) or source[at + 1 : at + 2] == "(")
                    opens.append((at, len(words)))
                    open_kinds.append(len(words) - 1 if substitution else -1)
                elif char == ")" and parens:
                    parens.pop()
                    inner, _first = opens.pop()
                    kind = open_kinds.pop()
                    if kind == -1:
                        command_closes.add(len(words))
                    elif kind >= 0:
                        substitutions[kind] = len(words)
                        after = source[at + 1 : at + 2]
                        if after and not after.isspace() and after not in _OPERATORS + "<>":
                            glued.add(len(words) + 1)
                    if opens and opens[-1][0] == inner - 1 and source[at + 1 : at + 2] == ")":
                        # Through both closing ``)``: this one and the next, glued.
                        arith_words.update(range(opens[-1][1], len(words) + 2))
                elif char == ")":
                    # Unmatched: a case-arm pattern, ``x) rm …``.
                    command_closes.add(len(words))
                if words and words[-1] == (char, "u") and char in "&|":
                    words[-1] = (char * 2, "uu")
                else:
                    words.append((char, "u"))
                if char == "\n" and tags:
                    # Bodies follow in tag order; only an unquoted tag's body expands.
                    restart = at + 1
                    for tag in tags:
                        end = _heredoc_end(source, restart, [tag])
                        if tag[2]:
                            body = _HEREDOC_OPENER_RE.finditer(source, restart, end)
                            live |= {m.start() for m in body if len(m.group()) == 1}
                        restart = end
                    tags.clear()
                    break
            else:
                text.append(char)
                kinds.append("u")
                started = True
        if restart is None:
            break
        base = restart
    _end()
    return _Scan(
        words,
        live,
        source,
        quote_breaks,
        frozenset(arith_words),
        frozenset(command_closes),
        substitutions,
        frozenset(glued),
    )


def _split_redirect(word: _Word) -> "tuple[_Word | None, bool]":
    """The operand glued before an unquoted redirection, and whether a target follows.

    ``~>/dev/null`` is the operand ``~`` plus a redirection; ``2>x`` is only a
    redirection (a leading fd number is part of the operator).
    """
    text, kinds = word
    cut = next((i for i, (c, k) in enumerate(zip(text, kinds)) if c in "<>" and k == "u"), -1)
    if cut == -1:
        return word, False
    if cut and text[cut - 1] == "&" and kinds[cut - 1] == "u":
        cut -= 1
    head = text[:cut]
    operand = None if not head or head.isdigit() else (head, kinds[:cut])
    # The LAST redirection decides: ``0</dev/null<`` still takes the next word.
    tail = len(text) - len(text.rstrip("<>&"))
    return operand, bool(tail) and "u" * tail == kinds[-tail:] and "&" != text[-tail:]


def _flag_kinds(token: str) -> "set[str]":
    """The ``recursive`` / ``force`` meanings an ``rm`` option word carries."""
    if token.startswith("--"):
        # GNU accepts any unambiguous prefix of a long option; three characters
        # is the shortest prefix that names only one of these two.
        name = token.split("=", 1)[0]
        if len(name) >= 3 and "--recursive".startswith(name):
            return {"recursive"}
        if len(name) >= 3 and "--force".startswith(name):
            return {"force"}
        return set()
    kinds = set()
    if "r" in token[1:] or "R" in token[1:]:
        kinds.add("recursive")
    if "f" in token[1:]:
        kinds.add("force")
    return kinds


def _is_dir_itself(rest: str) -> bool:
    """True when *rest*, after a directory spelling, still names that directory."""
    # ``${HOME}.`` is a sibling named ``<home>.``: only ``/`` starts a path inside it.
    return (not rest or rest[0] == "/") and bool(_ROOT_RE.fullmatch(posixpath.normpath("/" + rest)))


def _folded(path: str) -> str:
    # Only a Windows path ignores case and takes either separator; a POSIX path
    # keeps its case and its literal backslashes.
    if os.name == "nt":
        return posixpath.normpath(path.replace("\\", "/")).casefold()
    return posixpath.normpath(path)


def _expansion_end(text: str, kinds: str, start: int) -> int:
    """Offset just past the ``$HOME`` / ``${HOME…}`` reference matched up to *start*.

    Bash matches the braces of a default (``${HOME:-${USERPROFILE}}``, ``${HOME:-{a}}``),
    counting only those quoted like the opening ``$``; an escaped ``\\}`` is text.
    -1 when the braces never close.
    """
    if not text.startswith("${") or text[start - 1] == "}":
        return start
    depth = 1
    for at in range(start, len(text)):
        if kinds[at] != kinds[0]:
            continue
        depth += {"{": 1, "}": -1}.get(text[at], 0)
        if depth == 0:
            return at + 1
    return -1


def _target_kind(word: _Word, homes: "frozenset[str]", quote_breaks: "set[int]") -> "str | None":
    """``"root"`` or ``"home"`` when *word* names that directory or the glob over it."""
    text, kinds = word
    if text.endswith("/*") and kinds[-1] == "u":
        text, kinds = text[:-1], kinds[:-1]
    if not text:
        return None
    if text.startswith("/") and _ROOT_RE.fullmatch(posixpath.normpath(text)):
        return "root"
    # Bash expands ``~`` only at the word's start with the prefix up to the first
    # ``/`` all unquoted, so ``~''`` and ``''~`` are a literal ``~``.
    if (
        text.startswith("~")
        and kinds[0] == "u"
        and (len(text) == 1 or text[1] == "/")
        and not any(at <= 1 for at in quote_breaks)
    ):
        return "home" if _is_dir_itself(text[1:]) else None
    match = _HOME_VAR_RE.match(text)
    # The ``$``, brace and name must come from ONE quoting run: ``"$HO""ME"`` expands
    # HO then ME. A quote inside a ``${HOME:-"x"}`` default still expands HOME.
    name_end = 6 if text.startswith("${") else 5
    end = _expansion_end(text, kinds, match.end()) if match else -1
    if (
        end != -1
        and len(set(kinds[:name_end])) == 1
        and kinds[0] != "s"
        and not any(0 < at < name_end for at in quote_breaks)
    ):
        return "home" if _is_dir_itself(text[end:]) else None
    # Literal home paths also count; the Windows word split can read backslashes
    # as escapes, so ``homes`` includes that spelling.
    if _folded(text) in homes:
        return "home"
    return None


def _shell_words(scan: _Scan) -> "tuple[list[_Word], list[int]]":
    """*scan*'s words with each substitution span, and words glued to it, as ONE word.

    ``rm -fr $(true) ~`` passes the substitution's output as one argument; its body
    is read as a frame of its own. The span reads as the text before its opener
    plus ``\\0``, which names no directory and no program.
    """
    spans = scan.substitutions or {}
    words: list[_Word] = []
    origin: list[int] = []
    index = 0
    while index < len(scan.words):
        if index not in spans:
            words.append(scan.words[index])
            origin.append(index)
            index += 1
            continue
        end = spans[index]
        while end + 1 in scan.glued:
            after = end + 1
            # A glued word ending in another opener continues through that span.
            end = spans.get(after, after)
            if after not in spans:
                break
        text, kinds = scan.words[index]
        words.append((text[:-1] + "\0", kinds[:-1] + "s"))
        origin.append(index)
        index = end + 1
    return words, origin


def _frame_targets(scan: _Scan, homes: "frozenset[str]") -> "set[str]":
    """Which of root / home a recursive-force ``rm`` in one command line deletes."""
    words, origin = _shell_words(scan)
    # An empty quoted word (``''``) is an argument bash passes, never an operator.
    # Words inside ``((…))`` are math: an argument like any other, never a program.
    math = {i for i, at in enumerate(origin) if at in scan.arith_words}
    ends = [
        bool(text)
        and i not in math
        and (_shell._ends_argv(text) or text == ")")
        and set(kinds) <= {"u"}
        for i, (text, kinds) in enumerate(words)
    ]
    # A quoted word that merely LOOKS like an operator is data; an unquoted reserved
    # word in command position (``then``, ``!``, ``time -p``) passes it to the next word.
    # Before the program, assignments and redirections (``2>/dev/null rm``,
    # ``X=1 > log rm``) pass it on as well; a case-arm ``x)`` starts a command.
    base = _shell._KEEPS_COMMAND_POSITION
    names, at_command, keep = [], True, base
    prefix, redirect_target = True, False
    for i, (text, kinds) in enumerate(words):
        redirect = False
        if prefix and i not in math:
            operand, takes = _split_redirect((text, kinds))
            redirect = redirect_target or operand is None
            redirect_target = operand is None and takes
        reserved = at_command and set(kinds) <= {"u"} and text in keep
        kept = reserved or redirect
        keep = base | {"-p", "--"} if reserved and text == "time" else base
        at_command = reserved or ends[i]
        name_end = text.find("=") + 1
        assignment = bool(ENV_ASSIGNMENT_RE.match(text)) and set(kinds[:name_end]) <= {"u"}
        prefix = kept or ends[i] or (prefix and assignment)
        plain_word = i not in math and (ends[i] or not _shell._ends_argv(text))
        closes = origin[i] in scan.command_closes and i not in math
        names.append(";" if kept or closes else text if plain_word else "_")
    programs = _shell._argv_programs(names)
    found: set[str] = set()
    flags: set[str] = set()
    targets: set[str] = set()
    options_done = False
    skip_next = False
    for index, word in enumerate(words):
        is_rm_argument = (
            index > 0
            and programs[index].lower() == "rm"
            and programs[index - 1].lower() == "rm"
            and not ends[index]
        )
        if is_rm_argument and skip_next:
            skip_next = False
        elif is_rm_argument:
            operand, skip_next = _split_redirect(word)
            text = operand[0] if operand else ""
            if operand is None:
                pass
            elif not options_done and text == "--":
                options_done = True
            elif not options_done and text.startswith("-") and len(text) > 1:
                flags |= _flag_kinds(text)
            else:
                breaks = scan.quote_breaks.get(origin[index], set())
                target = _target_kind(operand, homes, breaks)
                if target:
                    targets.add(target)
        if ends[index] or index + 1 == len(words):
            if {"recursive", "force"} <= flags:
                found |= targets
            flags, targets, options_done, skip_next = set(), set(), False, False
    return found


def _live_substitution_bodies(scan: _Scan, source: str) -> "set[str]":
    """Substitution bodies of *source* that run: one with at least one live opener."""
    text = scan.text
    # Bodies come from the scanned text the live offsets index, so a ``$'…'`` value
    # is its decoded literal. Each body starts at a LIVE opener, so a quoted ``'$('``
    # cannot swallow a live one after it; a body nested in one already taken is read
    # by that body's own frame. An empty body runs nothing.
    spots: dict[str, list[int]] = {}
    taken = 0
    for spot in sorted(scan.live):
        if spot < taken:
            continue
        if text.startswith(_SUBSTITUTION_OPENERS[:3], spot):
            end, proven = _shell._matching_close_paren(text, spot + 2)
            body = text[spot + 2 : end - 1] if proven else text[spot + 2 :]
        elif text[spot] == "`":
            end, proven = _shell._matching_close_backtick(text, spot + 1)
            body = text[spot + 1 : end - 1] if proven else text[spot + 1 :]
        else:
            continue
        taken = end
        spots.setdefault(body, []).append(spot)
    bodies: set[str] = set()
    for body, at in spots.items():
        # Only ``$((…))`` is math; a `` `(…)` `` or ``<(…)`` body is a subshell.
        if _is_math(body) and all(text.startswith("$(", spot) for spot in at):
            bodies |= _math_bodies(body)
        elif body:
            bodies.add(body)
    return bodies


def _is_math(body: str) -> bool:
    """True when ``$(`` + *body* + ``)`` is ``$((…))``: the inner ``(`` closes last."""
    if not body.startswith("("):
        return False
    end, proven = _shell._matching_close_paren(body, 1)
    return proven and end == len(body)


def _math_bodies(body: str, depth: int = 0) -> "set[str]":
    """The substitutions inside a ``$((…))`` expression, nested math unwrapped."""
    if depth > _MAX_MATH_DEPTH:
        raise RecursionError("arithmetic nesting past the rm floor's depth cap")
    found: set[str] = set()
    for inner in set(_shell._substitution_bodies(body[1:-1])) - {""}:
        found |= _math_bodies(inner, depth + 1) if _is_math(inner) else {inner}
    return found


def _unquoted_ops(word: _Word) -> str:
    """*word* with each quoted ``;`` ``&`` ``|`` masked: in quotes they start no command."""
    return "".join("_" if c in ";&|\n" and k != "u" else c for c, k in zip(*word))


def _group_depths(tokens: "list[str]", plain: "list[bool]") -> "list[int] | None":
    """Per token, how many groups enclose it; None when the nesting cannot be read.

    A reserved word opens or closes a group only at command position, so
    ``echo done`` closes nothing. A ``case`` arm closes on an unmatched ``)``, so a
    frame with ``case`` (or any unbalanced group) is not read.
    """
    depth, at_command, depths = 0, True, []
    for token, is_plain in zip(tokens, plain):
        word = token if is_plain else ""
        if at_command and word == "case":
            return None
        if word == ")" or (at_command and word in _GROUP_CLOSERS):
            depth -= 1
            if depth < 0:
                return None
        depths.append(depth)
        if word == "(" or (at_command and word in _GROUP_OPENERS):
            depth += 1
        at_command = bool(word) and (
            _shell._ends_argv(word) or word in _shell._KEEPS_COMMAND_POSITION or word == ")"
        )
    return depths if depth == 0 else None


def _pipeline_disqualified(scan: _Scan) -> "list[bool]":
    """Per word: whether its own pipeline refuses the data-consumer exemption.

    ``echo bash -c '…'; echo : | sh`` pipes only the second command into ``sh``.
    A group (``{ …; } | sh``, ``do … done | sh``) feeds every inner command to its
    pipe, so a pipeline is cut only outside any group; a frame whose groups cannot
    be read is judged whole. A quoted ``'|'`` is printed text, so it is masked.
    """
    words = scan.words
    tokens = [_unquoted_ops(word) for word in words]
    plain = [set(kinds) <= {"u"} for _text, kinds in words]
    depths = _group_depths(tokens, plain)
    if depths is None:
        return [_shell._data_consumer_command_disqualified(tokens)] * len(tokens)
    verdicts: list[bool] = []
    start = 0
    for index in range(len(tokens) + 1):
        cut = index == len(tokens) or (
            plain[index]
            and depths[index] == 0
            and tokens[index] in _PIPELINE_ENDS
            and not (index and tokens[index - 1] == "|")
        )
        if cut:
            verdict = _shell._data_consumer_command_disqualified(tokens[start:index])
            verdicts += [verdict] * (index - start) + ([True] if index < len(tokens) else [])
            start = index + 1
    return verdicts


def _executed_children(
    scan: _Scan, source: str, tokens: "list[str]", joined: "set[str]"
) -> "set[str]":
    """The bodies this frame RUNS: every payload except one only a data consumer receives."""
    payloads = _shell._nested_shell_payloads(
        tokens, allow_join=source not in joined, joined_out=joined
    )
    programs = _shell._argv_programs(tokens)
    disqualified = _pipeline_disqualified(scan) if payloads else []
    positions: dict[str, list[int]] = {}
    for index, token in enumerate(tokens):
        positions.setdefault(token, []).append(index)
    children: set[str] = set()
    interpreted: "set[str] | None" = None
    for payload in payloads:
        occurrences = positions.get(payload, [])
        if occurrences and all(
            _shell._data_consumer_exempt(
                i,
                _unquoted_ops(scan.words[i]),
                programs,
                tokens,
                command_disqualified=disqualified[i],
            )
            for i in occurrences
        ):
            continue
        # Piped printf text arrives decoded; env -S / sed e strings are read both ways.
        children.add(payload)
        if interpreted is None:
            interpreted = {_shell._sed_exec_replacement(t) for t in tokens}
            interpreted |= {b for a, b in zip(tokens, tokens[1:]) if a in _SPLIT_FLAGS}
            interpreted |= {t[m.end() :] for t in tokens if (m := _SPLIT_GLUED_RE.match(t))}
        if payload in interpreted:
            children.add(_shell._decode_printf_escapes(payload))
    return children | _live_substitution_bodies(scan, source)


def _rm_wipe_targets(text: str) -> "set[str]":
    """Which of root / home a recursive-force ``rm`` in *text* deletes.

    *text* is the command as submitted: ``$HOME`` is case-sensitive, so a
    lowercased copy would read an unrelated ``$home`` variable as home.
    """
    home = os.path.expanduser("~")
    homes = frozenset({_folded(home), _folded(home.replace("\\", ""))}) - {".", "~"}
    pending = [text]
    seen = {text}
    # Joining an eval suffix again would build a quadratic chain of frames.
    joined: set[str] = set()
    found: set[str] = set()
    while pending:
        source = pending.pop()
        scan = _scan(source)
        found |= _frame_targets(scan, homes)
        tokens = [word for word, _kinds in scan.words]
        for child in _executed_children(scan, source, tokens, joined):
            # Unexpanded bodies shrink at every step, regardless of HOME's length.
            if len(child) < len(source) and child not in seen:
                seen.add(child)
                pending.append(child)
    return found
