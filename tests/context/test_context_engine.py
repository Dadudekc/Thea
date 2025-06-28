#!/usr/bin/env python3
"""Unit-tests for ContextManager – fulfils Beta checklist task.

Creates an in-memory SQLite DB, bootstraps the expected tables, then
asserts core operations: create, hierarchy fetch, relationships, and
relevance-score update.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime

from core.context_manager import ContextManager, Context


def _bootstrap_schema(conn: sqlite3.Connection):
    conn.executescript(
        """
        CREATE TABLE contexts (
            id TEXT PRIMARY KEY,
            parent_id TEXT,
            type TEXT,
            title TEXT,
            content TEXT,
            metadata TEXT,
            relevance_score REAL,
            created_at TEXT,
            updated_at TEXT,
            expires_at TEXT,
            is_active INTEGER
        );
        CREATE TABLE context_relationships (
            source_id TEXT,
            target_id TEXT,
            relationship_type TEXT,
            strength REAL
        );
        """
    )
    conn.commit()


def _new_manager() -> ContextManager:
    cm = ContextManager(":memory:")
    _bootstrap_schema(cm.conn)
    return cm


def test_create_and_fetch_context():
    cm = _new_manager()

    root = Context(
        id="ctx_root",
        type="episode",
        title="Episode 1",
        content="The beginning of the Dreamscape",
        metadata={},
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    cm.create_context(root)
    fetched = cm.get_context("ctx_root")

    assert fetched is not None
    assert fetched.title == "Episode 1"
    assert fetched.relevance_score == 1.0


def test_hierarchy_and_relationships():
    cm = _new_manager()

    parent = Context(id="p", type="topic", title="Parent", content="parent")
    child = Context(id="c", type="topic", title="Child", content="child", parent_id="p")
    cm.create_context(parent)
    cm.create_context(child)
    cm.create_relationship("p", "c", "child", 0.8)

    chain = cm.get_context_hierarchy("c")
    # root then child
    assert [c.id for c in chain] == ["p", "c"]

    related = cm.get_related_contexts("p")
    assert related and related[0][0].id == "c"


def test_relevance_score_update_and_prune():
    cm = _new_manager()
    ctx = Context(id="a", type="note", title="A", content="x", relevance_score=0.05)
    cm.create_context(ctx)

    cm.update_relevance_scores("a")
    updated = cm.get_context("a")
    assert updated.relevance_score > 0.05  # increased

    pruned = cm.prune_contexts(threshold=0.9)
    # After increase, score ~0.15 so still below 0.9 – should have been pruned (inactive)
    assert "a" in pruned 