"""Incremental slot-detail reads: a cursor a polling reader echoes back.

A reader that polls the newest page of a session (the app-sdk ``ChatEmbed``)
already holds almost every row the next read returns. With a cursor it asks only
for what may have changed:

* A paged read that passes ``cursor=1`` gets ``cursor: {from, since, digest}``
  back. ``from`` is the absolute row index of the page's first row, ``since`` the
  index of its last row, and ``digest`` a hash of the rendered rows in
  ``[from, since)`` exactly as they were served.
* The next read passes those three values back (``from``, ``since``, ``digest``
  query parameters). The server composes the page as before, renders the rows in
  ``[from, since)`` again and compares their hash. Equal means the reader's copy
  of those rows is current, so the response carries only rows from ``since`` on,
  echoed as ``delta: {from, since}``. Anything else -- a row edited in place
  (an approval resolved, a card patched), a rewind, a rotation, a different
  redaction context -- fails the comparison and the response is the full page,
  with no ``delta``, which the reader takes as a replacement.

The last row is never inside the hashed span: the folded streaming row changes on
every chunk, so it is always re-sent. The hash covers the rendered output, not
the stored rows, so anything that changes what a reader would see changes it.
The digest is an integrity check, not a secret: a reader that forges one only
corrupts its own copy, and every row it is served is rendered and redacted as on
a full read.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

# Matches the slot-detail handler's ceiling (``chat_utils.SLOT_DETAIL_MAX_LIMIT``):
# a reader's held page is never wider than one page, so a span wider than this is
# not a cursor this server issued. Such a request is answered with a full page.
DELTA_MAX_SPAN = 500
_DIGEST_RE = re.compile(r"[0-9a-f]{32}")


@dataclass(frozen=True)
class DeltaCursor:
    """The ``from``/``since``/``digest`` triple a reader echoes back."""

    start: int
    since: int
    digest: str


@dataclass(frozen=True)
class PagePlan:
    """What one cursor-mode response serves and reports."""

    fragments: list[str]
    next_before: int
    has_more: bool
    delta: dict[str, int] | None
    cursor: dict[str, Any] | None


class DeltaQueryError(ValueError):
    """A malformed cursor query; the handler answers 400."""


def parse_delta_query(query: Mapping[str, str]) -> tuple[DeltaCursor | None, bool]:
    """``(cursor, cursor_mode)`` from a slot-detail query string.

    ``cursor_mode`` is true when the response must carry a ``cursor`` (``cursor=1``
    or an echoed cursor). The three echo parameters come together or not at all.
    """
    names = ("from", "since", "digest")
    present = [n for n in names if n in query]
    want = query.get("cursor") == "1"
    if not present:
        return None, want
    if len(present) != len(names):
        raise DeltaQueryError("from, since and digest must be passed together")
    try:
        start = int(query["from"])
        since = int(query["since"])
    except ValueError as exc:
        raise DeltaQueryError("from and since must be integers") from exc
    digest = query["digest"]
    if start < 0 or since < start or not _DIGEST_RE.fullmatch(digest):
        raise DeltaQueryError("from/since/digest is not a cursor this server issues")
    return DeltaCursor(start=start, since=since, digest=digest), True


def read_limit(window: int, cursor: DeltaCursor | None) -> int:
    """Rows to compose so the page reaches back to the cursor's ``from``.

    The page must hold the reader's span ``[from, since)`` to check it, plus up
    to *window* newer rows. A span wider than any page this server serves is not
    honoured, so it costs no wider read either.
    """
    if cursor is None or cursor.since - cursor.start > DELTA_MAX_SPAN:
        return window
    return window + (cursor.since - cursor.start)


def span_digest(fragments: Sequence[str], start: int, since: int) -> str:
    """Hash of the rendered rows ``[start, since)``, bound to their position."""
    h = hashlib.blake2b(digest_size=16)
    h.update(f"{start}:{since}\n".encode("ascii"))
    for fragment in fragments:
        h.update(fragment.encode("utf-8"))
        h.update(b"\x1e")
    return h.hexdigest()


def plan_page(
    fragments: Sequence[str | None],
    *,
    page_start: int,
    total: int,
    window: int,
    cursor: DeltaCursor | None,
) -> PagePlan:
    """Decide what a cursor-mode response serves.

    *fragments* are the page's rendered rows, one per collapsed row starting at
    absolute index *page_start*; ``None`` is a row that renders as nothing (an
    empty streaming run). *window* is the reader's page size.

    When the fragments do not line up one-to-one with ``[page_start, total)`` no
    position can be trusted: the whole composed page is served as a replacement
    and no cursor is issued, so the reader's next read is a plain full one.
    """
    if len(fragments) != total - page_start:
        return PagePlan(
            fragments=[f for f in fragments if f is not None],
            next_before=page_start,
            has_more=page_start > 0,
            delta=None,
            cursor=None,
        )

    def _span(a: int, b: int) -> list[str] | None:
        seg = fragments[a - page_start : b - page_start]
        return None if any(f is None for f in seg) else [f for f in seg if f is not None]

    new_from = max(page_start, total - window)
    applied = False
    if (
        cursor is not None
        and cursor.since - cursor.start <= DELTA_MAX_SPAN
        and page_start <= cursor.start
        and cursor.since <= total
    ):
        held = _span(cursor.start, cursor.since)
        applied = (
            held is not None and span_digest(held, cursor.start, cursor.since) == cursor.digest
        )
    serve_from = max(cursor.since, new_from) if applied and cursor is not None else new_from
    served = [f for f in fragments[serve_from - page_start :] if f is not None]

    next_since = max(new_from, total - 1)
    next_span = _span(new_from, next_since)
    next_cursor = (
        {
            "from": new_from,
            "since": next_since,
            "digest": span_digest(next_span, new_from, next_since),
        }
        if next_span is not None
        else None
    )
    return PagePlan(
        fragments=served,
        next_before=new_from,
        has_more=new_from > 0,
        delta=(
            {"from": cursor.start, "since": cursor.since}
            if applied and cursor is not None
            else None
        ),
        cursor=next_cursor,
    )
