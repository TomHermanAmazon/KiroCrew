"""The slot-detail incremental-read cursor (``slot_detail_delta``)."""

from __future__ import annotations

import pytest
from aiohttp.test_utils import TestClient, TestServer
from chat_test_helpers import _make_app, _make_state

from kiro_crew.dashboard.slot_detail_delta import (
    DeltaCursor,
    DeltaQueryError,
    parse_delta_query,
    plan_page,
    span_digest,
)


def _state(tmp_path, monkeypatch, name: str, count: int):
    monkeypatch.setattr("kiro_crew.dashboard.state.config_dir", lambda: tmp_path)
    state = _make_state(tmp_path)
    slot = state.get_or_create_slot(name)
    for i in range(count):
        state.conversation_log.append(f"dashboard:{name}", "user", f"msg {i}")
        slot.append("user", f"msg {i}")
    slot.drain()
    return state, slot


def _echo(cursor: dict) -> str:
    return f"from={cursor['from']}&since={cursor['since']}&digest={cursor['digest']}"


class TestCursorReads:
    @pytest.mark.asyncio
    async def test_cursor_read_serves_the_same_page_plus_a_cursor(self, tmp_path, monkeypatch):
        state, _ = _state(tmp_path, monkeypatch, "c", 30)
        async with TestClient(TestServer(_make_app(state))) as client:
            plain = await (await client.get("/api/chat/slots/c?limit=10")).json()
            first = await (await client.get("/api/chat/slots/c?limit=10&cursor=1")).json()
        assert first["messages"] == plain["messages"]
        assert (first["total"], first["has_more"], first["next_before"]) == (30, True, 20)
        assert first["cursor"]["from"] == 20 and first["cursor"]["since"] == 29
        assert "delta" not in first
        assert "cursor" not in plain

    @pytest.mark.asyncio
    async def test_echoed_cursor_gets_only_the_new_rows(self, tmp_path, monkeypatch):
        state, slot = _state(tmp_path, monkeypatch, "d", 30)
        async with TestClient(TestServer(_make_app(state))) as client:
            first = await (await client.get("/api/chat/slots/d?limit=10&cursor=1")).json()
            for i in range(30, 33):
                state.conversation_log.append("dashboard:d", "user", f"msg {i}")
                slot.append("user", f"msg {i}")
            slot.drain()
            resp = await client.get(f"/api/chat/slots/d?limit=10&{_echo(first['cursor'])}")
            nxt = await resp.json()
        assert resp.status == 200
        assert nxt["delta"] == {"from": 20, "since": 29}
        # The held last row (29) is always re-sent, then the three new ones.
        assert [m["content"] for m in nxt["messages"]] == ["msg 29", "msg 30", "msg 31", "msg 32"]
        # The window slid: the reader drops rows before the new start.
        assert (nxt["total"], nxt["next_before"], nxt["has_more"]) == (33, 23, True)
        assert nxt["cursor"]["from"] == 23 and nxt["cursor"]["since"] == 32

    @pytest.mark.asyncio
    async def test_a_row_edited_in_place_falls_back_to_the_full_page(self, tmp_path, monkeypatch):
        state, slot = _state(tmp_path, monkeypatch, "e", 30)
        async with TestClient(TestServer(_make_app(state))) as client:
            first = await (await client.get("/api/chat/slots/e?limit=10&cursor=1")).json()
            # A row well inside the held span changes (an approval resolved, a
            # card patched): only the hash notices.
            target = slot.messages[25]
            slot.update_message(
                target["ts"], content="edited", mid=(target.get("meta") or {}).get("mid")
            )
            nxt = await (
                await client.get(f"/api/chat/slots/e?limit=10&{_echo(first['cursor'])}")
            ).json()
        # A full replacement page: no delta, and the edit is in it.
        assert "delta" not in nxt
        assert len(nxt["messages"]) == 10
        assert "edited" in [m["content"] for m in nxt["messages"]]

    @pytest.mark.asyncio
    async def test_a_forged_digest_is_a_full_page(self, tmp_path, monkeypatch):
        state, _ = _state(tmp_path, monkeypatch, "f", 30)
        async with TestClient(TestServer(_make_app(state))) as client:
            nxt = await (
                await client.get("/api/chat/slots/f?limit=10&from=20&since=29&digest=" + "0" * 32)
            ).json()
        assert "delta" not in nxt
        assert [m["content"] for m in nxt["messages"]] == [f"msg {i}" for i in range(20, 30)]

    @pytest.mark.asyncio
    async def test_a_cursor_without_limit_is_still_a_bounded_read(self, tmp_path, monkeypatch):
        state, _ = _state(tmp_path, monkeypatch, "g", 250)
        async with TestClient(TestServer(_make_app(state))) as client:
            data = await (await client.get("/api/chat/slots/g?cursor=1")).json()
        assert len(data["messages"]) == 200
        assert data["next_before"] == 50

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "query",
        [
            "from=1&since=2",
            "from=x&since=2&digest=" + "0" * 32,
            "from=3&since=2&digest=" + "0" * 32,
            "from=1&since=2&digest=nothex",
            "cursor=1&before=5",
        ],
    )
    async def test_a_malformed_cursor_is_a_bad_request(self, tmp_path, monkeypatch, query):
        state, _ = _state(tmp_path, monkeypatch, "h", 5)
        async with TestClient(TestServer(_make_app(state))) as client:
            resp = await client.get(f"/api/chat/slots/h?limit=5&{query}")
            assert resp.status == 400
            assert (await resp.json())["code"] == "invalid_query_params"


class TestPlanPage:
    def test_misaligned_fragments_serve_the_page_with_no_cursor(self):
        plan = plan_page(["a", "b"], page_start=0, total=3, window=10, cursor=None)
        assert plan.fragments == ["a", "b"] and plan.cursor is None and plan.delta is None

    def test_a_dropped_row_inside_the_span_issues_no_cursor(self):
        plan = plan_page(["a", None, "c"], page_start=0, total=3, window=10, cursor=None)
        assert plan.cursor is None
        assert plan.fragments == ["a", "c"]

    def test_a_dropped_last_row_still_issues_a_cursor(self):
        plan = plan_page(["a", "b", None], page_start=0, total=3, window=10, cursor=None)
        assert plan.cursor == {"from": 0, "since": 2, "digest": span_digest(["a", "b"], 0, 2)}

    def test_the_digest_is_bound_to_position(self):
        assert span_digest(["a"], 0, 1) != span_digest(["a"], 1, 2)

    def test_an_empty_session_has_a_cursor_too(self):
        plan = plan_page([], page_start=0, total=0, window=10, cursor=None)
        assert plan.cursor is not None and plan.cursor["since"] == 0
        nxt = plan_page(
            ["a"],
            page_start=0,
            total=1,
            window=10,
            cursor=DeltaCursor(0, 0, plan.cursor["digest"]),
        )
        assert nxt.delta == {"from": 0, "since": 0} and nxt.fragments == ["a"]

    def test_a_cursor_behind_the_composed_page_is_a_full_page(self):
        cursor = DeltaCursor(0, 2, span_digest(["a", "b"], 0, 2))
        plan = plan_page(["b", "c"], page_start=1, total=3, window=2, cursor=cursor)
        assert plan.delta is None and plan.fragments == ["b", "c"]

    def test_parse_requires_all_three(self):
        assert parse_delta_query({}) == (None, False)
        assert parse_delta_query({"cursor": "1"}) == (None, True)
        with pytest.raises(DeltaQueryError):
            parse_delta_query({"from": "1", "digest": "0" * 32})
