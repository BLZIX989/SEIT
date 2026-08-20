"""Tests for the Phase 9 Literature Workspace. Unlike other Phase
test files, these run against the REAL repository's literature/ and
reports/l0/ content (read-only, so there's no risk of drift) --
brief section XXXII's "no mock data" rule applies here too: the
literature corpus is itself real committed content, not a fixture
that needs isolating.
"""
from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from console.api.literature import adapter as literature_adapter
from console.api.main import app

REPO_ROOT = Path(__file__).resolve().parents[3]
client = TestClient(app)


def test_get_sources_matches_real_manifest():
    manifest = json.loads((REPO_ROOT / "literature" / "manifests" / "LITERATURE_DOWNLOAD_MANIFEST.json").read_text())
    assert literature_adapter.get_sources() == manifest["acquired"]
    assert len(literature_adapter.get_sources()) == 2  # Tong + Kiritsis, as actually acquired


def test_get_items_merges_both_real_corpora_verbatim():
    items = literature_adapter.get_items()
    corpora = {item["corpus"] for item in items}
    assert corpora == {"string_theory", "general"}
    st_items = [i for i in items if i["corpus"] == "string_theory"]
    assert len(st_items) == 25  # STRING_THEORY_LITERATURE_REGISTRY.json's real item count
    assert st_items[0]["raw"]["STRING_ITEM_ID"] == st_items[0]["id"]


def test_get_crosswalk_flags_unregistered_nodes_honestly():
    nodes = {"GEOMETRY-NODE": {}, "VARIATIONAL-NODE": {}}  # a small, real-id-shaped stand-in
    rows = literature_adapter.get_crosswalk(nodes)
    assert len(rows) > 0
    registered = [r for r in rows if r["node_is_registered"]]
    unregistered = [r for r in rows if not r["node_is_registered"]]
    assert registered  # GEOMETRY-NODE/VARIATIONAL-NODE rows exist in the real CSV
    assert unregistered  # the CSV genuinely contains "(not registered)" rows too
    for r in registered:
        assert r["mdcl_node_id"] in nodes


def test_get_recoveries_reads_real_recovery_records():
    recoveries = literature_adapter.get_recoveries()
    assert len(recoveries) == 2  # RECOVERY-STR-001, RECOVERY-STR-002
    ids = {r["id"] for r in recoveries}
    assert ids == {"RECOVERY-STR-001", "RECOVERY-STR-002"}
    assert all("TARGET_NODE" in r["raw"] for r in recoveries)


# ---- API tests, against the real repository ----

def test_api_literature_sources():
    r = client.get("/api/literature/sources")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_api_literature_items():
    r = client.get("/api/literature/items")
    assert r.status_code == 200
    assert len(r.json()) == 25 + 13  # string_theory + general


def test_api_literature_crosswalk_filter_by_real_node():
    r = client.get("/api/literature/crosswalk?node_id=GEOMETRY-NODE")
    assert r.status_code == 200
    rows = r.json()
    assert len(rows) > 0
    assert all(row["mdcl_node_id"] == "GEOMETRY-NODE" for row in rows)
    assert all(row["node_is_registered"] for row in rows)  # GEOMETRY-NODE is a real registered node


def test_api_literature_recoveries():
    r = client.get("/api/literature/recoveries")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_node_detail_includes_real_literature_crosswalk():
    r = client.get("/api/nodes/GEOMETRY-NODE")
    assert r.status_code == 200
    crosswalk = r.json()["literature_crosswalk"]
    assert len(crosswalk) > 0
    assert all(row["mdcl_node_id"] == "GEOMETRY-NODE" for row in crosswalk)


def test_node_without_any_crosswalk_row_gets_empty_list():
    # A node with proofs but (almost certainly) no string-theory crosswalk entry.
    r = client.get("/api/nodes/GRAPH-G-SEED")
    assert r.status_code == 200
    assert r.json()["literature_crosswalk"] == []
