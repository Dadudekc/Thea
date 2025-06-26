"""
Context Management System for Dream.OS

Handles hierarchical storage, retrieval, and scoring of contexts for the prompt management system.
Implements intelligent context selection and pruning based on relevance and relationships.
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Context:
    id: str
    type: str
    title: str
    content: str
    parent_id: Optional[str] = None
    metadata: Dict = None
    relevance_score: float = 1.0
    created_at: datetime = None
    updated_at: datetime = None
    expires_at: Optional[datetime] = None
    is_active: bool = True

class ContextManager:
    def __init__(self, db_path: Union[str, Path]):
        """Initialize the context manager with database connection."""
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row

    def create_context(self, context: Context) -> str:
        """Create a new context entry."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO contexts (
                    id, parent_id, type, title, content, metadata,
                    relevance_score, created_at, updated_at, expires_at, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                context.id, context.parent_id, context.type, context.title,
                context.content, json.dumps(context.metadata or {}),
                context.relevance_score,
                context.created_at or datetime.now(),
                context.updated_at or datetime.now(),
                context.expires_at,
                context.is_active
            ))
            self.conn.commit()
            return context.id
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Failed to create context: {e}")

    def get_context(self, context_id: str) -> Optional[Context]:
        """Retrieve a context by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM contexts WHERE id = ?", (context_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return Context(
            id=row['id'],
            parent_id=row['parent_id'],
            type=row['type'],
            title=row['title'],
            content=row['content'],
            metadata=json.loads(row['metadata']),
            relevance_score=row['relevance_score'],
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at']),
            expires_at=datetime.fromisoformat(row['expires_at']) if row['expires_at'] else None,
            is_active=bool(row['is_active'])
        )

    def get_context_hierarchy(self, context_id: str) -> List[Context]:
        """Get the full hierarchy chain for a context."""
        contexts = []
        current_id = context_id
        
        while current_id:
            context = self.get_context(current_id)
            if not context:
                break
            contexts.append(context)
            current_id = context.parent_id
            
        return list(reversed(contexts))  # Root to leaf order

    def get_related_contexts(self, context_id: str, relationship_type: Optional[str] = None) -> List[Tuple[Context, float]]:
        """Get related contexts with their relationship strengths."""
        cursor = self.conn.cursor()
        query = """
            SELECT c.*, r.strength, r.relationship_type
            FROM contexts c
            JOIN context_relationships r ON c.id = r.target_id
            WHERE r.source_id = ?
        """
        params = [context_id]
        
        if relationship_type:
            query += " AND r.relationship_type = ?"
            params.append(relationship_type)
            
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [
            (Context(
                id=row['id'],
                parent_id=row['parent_id'],
                type=row['type'],
                title=row['title'],
                content=row['content'],
                metadata=json.loads(row['metadata']),
                relevance_score=row['relevance_score'],
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at']),
                expires_at=datetime.fromisoformat(row['expires_at']) if row['expires_at'] else None,
                is_active=bool(row['is_active'])
            ), row['strength'])
            for row in rows
        ]

    def update_context(self, context: Context) -> bool:
        """Update an existing context."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                UPDATE contexts
                SET parent_id = ?, type = ?, title = ?, content = ?,
                    metadata = ?, relevance_score = ?, updated_at = ?,
                    expires_at = ?, is_active = ?
                WHERE id = ?
            """, (
                context.parent_id, context.type, context.title,
                context.content, json.dumps(context.metadata or {}),
                context.relevance_score, datetime.now(),
                context.expires_at, context.is_active, context.id
            ))
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Failed to update context: {e}")

    def create_relationship(self, source_id: str, target_id: str, relationship_type: str, strength: float = 1.0) -> bool:
        """Create a relationship between contexts."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO context_relationships (source_id, target_id, relationship_type, strength)
                VALUES (?, ?, ?, ?)
            """, (source_id, target_id, relationship_type, strength))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Failed to create relationship: {e}")

    def update_relevance_scores(self, context_id: str, decay_factor: float = 0.9) -> None:
        """Update relevance scores for a context and its related contexts."""
        context = self.get_context(context_id)
        if not context:
            return

        # Update the main context
        context.relevance_score = min(1.0, context.relevance_score + 0.1)
        self.update_context(context)

        # Update related contexts with decay
        related = self.get_related_contexts(context_id)
        for related_context, strength in related:
            related_context.relevance_score *= decay_factor
            self.update_context(related_context)

    def prune_contexts(self, threshold: float = 0.1) -> List[str]:
        """Prune contexts with low relevance scores."""
        cursor = self.conn.cursor()
        try:
            # Get contexts to prune
            cursor.execute("""
                SELECT id FROM contexts
                WHERE relevance_score < ? AND is_active = 1
            """, (threshold,))
            to_prune = [row['id'] for row in cursor.fetchall()]

            # Deactivate contexts
            if to_prune:
                cursor.execute("""
                    UPDATE contexts
                    SET is_active = 0
                    WHERE id IN ({})
                """.format(','.join('?' * len(to_prune))), to_prune)
                self.conn.commit()

            return to_prune
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Failed to prune contexts: {e}")

    def get_relevant_contexts(self, query: str, context_type: Optional[str] = None, limit: int = 10) -> List[Context]:
        """Get most relevant contexts for a query."""
        cursor = self.conn.cursor()
        
        # Basic relevance scoring based on title and content matching
        query_terms = query.lower().split()
        query_conditions = []
        params = []
        
        for term in query_terms:
            query_conditions.extend([
                "LOWER(title) LIKE ?",
                "LOWER(content) LIKE ?"
            ])
            params.extend([f"%{term}%", f"%{term}%"])

        base_query = """
            SELECT *, 
                   (relevance_score * (
                       {relevance_conditions}
                   )) as match_score
            FROM contexts
            WHERE is_active = 1
        """.format(
            relevance_conditions=" + ".join([
                "CASE WHEN {} THEN 0.5 ELSE 0 END".format(cond)
                for cond in query_conditions
            ])
        )
        
        if context_type:
            base_query += " AND type = ?"
            params.append(context_type)
            
        base_query += " ORDER BY match_score DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(base_query, params)
        rows = cursor.fetchall()
        
        return [Context(
            id=row['id'],
            parent_id=row['parent_id'],
            type=row['type'],
            title=row['title'],
            content=row['content'],
            metadata=json.loads(row['metadata']),
            relevance_score=row['relevance_score'],
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at']),
            expires_at=datetime.fromisoformat(row['expires_at']) if row['expires_at'] else None,
            is_active=bool(row['is_active'])
        ) for row in rows]

    def __del__(self):
        """Clean up database connection."""
        if hasattr(self, 'conn'):
            self.conn.close()