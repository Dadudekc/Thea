"""
Prompt Template Engine for Dream.OS

Manages prompt templates, versions, and dynamic variable injection.
Supports template hierarchy, versioning, and performance tracking.
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from pathlib import Path
import jinja2
from jinja2 import Environment, BaseLoader, TemplateNotFound

@dataclass
class PromptTemplate:
    id: str
    type: str
    name: str
    content: str
    parent_id: Optional[str] = None
    description: Optional[str] = None
    variables: List[str] = None
    metadata: Dict = None
    version: str = "1.0.0"
    created_at: datetime = None
    updated_at: datetime = None
    is_active: bool = True
    success_rate: float = 0.0
    usage_count: int = 0

@dataclass
class TemplateVersion:
    template_id: str
    version: str
    content: str
    changes: Optional[str] = None
    performance_data: Dict = None
    created_at: datetime = None
    created_by: Optional[str] = None
    is_active: bool = True

class PromptTemplateEngine:
    def __init__(self, db_path: Union[str, Path]):
        """Initialize the template engine with database connection."""
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.jinja_env = Environment(
            loader=BaseLoader(),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True
        )

    def create_template(self, template: PromptTemplate) -> str:
        """Create a new prompt template."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO prompt_templates (
                    id, parent_id, type, name, description, content,
                    variables, metadata, version, created_at, updated_at,
                    is_active, success_rate, usage_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                template.id, template.parent_id, template.type,
                template.name, template.description, template.content,
                json.dumps(template.variables or []),
                json.dumps(template.metadata or {}),
                template.version,
                template.created_at or datetime.now(),
                template.updated_at or datetime.now(),
                template.is_active, template.success_rate,
                template.usage_count
            ))
            
            # Create initial version
            cursor.execute("""
                INSERT INTO template_versions (
                    template_id, version, content, created_at, is_active
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                template.id, template.version, template.content,
                datetime.now(), True
            ))
            
            self.conn.commit()
            return template.id
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Failed to create template: {e}")

    def get_template(self, template_id: str, version: Optional[str] = None) -> Optional[PromptTemplate]:
        """Retrieve a template by ID and optionally specific version."""
        cursor = self.conn.cursor()
        
        if version:
            cursor.execute("""
                SELECT t.*, v.content as version_content
                FROM prompt_templates t
                JOIN template_versions v ON t.id = v.template_id
                WHERE t.id = ? AND v.version = ?
            """, (template_id, version))
        else:
            cursor.execute("""
                SELECT t.*, v.content as version_content
                FROM prompt_templates t
                JOIN template_versions v ON t.id = v.template_id
                WHERE t.id = ? AND v.version = t.version
            """, (template_id,))
            
        row = cursor.fetchone()
        if not row:
            return None
            
        return PromptTemplate(
            id=row['id'],
            parent_id=row['parent_id'],
            type=row['type'],
            name=row['name'],
            description=row['description'],
            content=row['version_content'],
            variables=json.loads(row['variables']),
            metadata=json.loads(row['metadata']),
            version=row['version'],
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at']),
            is_active=bool(row['is_active']),
            success_rate=row['success_rate'],
            usage_count=row['usage_count']
        )

    def create_version(self, version: TemplateVersion) -> bool:
        """Create a new version of an existing template."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO template_versions (
                    template_id, version, content, changes,
                    performance_data, created_at, created_by, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                version.template_id, version.version, version.content,
                version.changes,
                json.dumps(version.performance_data or {}),
                version.created_at or datetime.now(),
                version.created_by, version.is_active
            ))
            
            # Update template's current version
            cursor.execute("""
                UPDATE prompt_templates
                SET version = ?, updated_at = ?
                WHERE id = ?
            """, (version.version, datetime.now(), version.template_id))
            
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Failed to create version: {e}")

    def render_template(self, template_id: str, variables: Dict, version: Optional[str] = None) -> str:
        """Render a template with provided variables."""
        template = self.get_template(template_id, version)
        if not template:
            raise TemplateNotFound(f"Template {template_id} not found")

        # Validate required variables
        missing_vars = set(template.variables or []) - set(variables.keys())
        if missing_vars:
            raise ValueError(f"Missing required variables: {missing_vars}")

        try:
            # Create Jinja template
            jinja_template = self.jinja_env.from_string(template.content)
            
            # Render template
            rendered = jinja_template.render(**variables)
            
            # Update usage statistics
            self._update_usage_stats(template_id)
            
            return rendered
        except Exception as e:
            raise Exception(f"Failed to render template: {e}")

    def _update_usage_stats(self, template_id: str) -> None:
        """Update template usage statistics."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                UPDATE prompt_templates
                SET usage_count = usage_count + 1,
                    updated_at = ?
                WHERE id = ?
            """, (datetime.now(), template_id))
            self.conn.commit()
        except sqlite3.Error:
            self.conn.rollback()

    def update_success_rate(self, template_id: str, success: bool) -> None:
        """Update template success rate."""
        cursor = self.conn.cursor()
        try:
            template = self.get_template(template_id)
            if not template:
                return

            # Calculate new success rate
            total_uses = template.usage_count
            current_successes = total_uses * template.success_rate
            new_success_rate = (current_successes + (1 if success else 0)) / (total_uses + 1)

            cursor.execute("""
                UPDATE prompt_templates
                SET success_rate = ?,
                    updated_at = ?
                WHERE id = ?
            """, (new_success_rate, datetime.now(), template_id))
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Failed to update success rate: {e}")

    def get_template_versions(self, template_id: str) -> List[TemplateVersion]:
        """Get all versions of a template."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM template_versions
            WHERE template_id = ?
            ORDER BY created_at DESC
        """, (template_id,))
        
        return [TemplateVersion(
            template_id=row['template_id'],
            version=row['version'],
            content=row['content'],
            changes=row['changes'],
            performance_data=json.loads(row['performance_data'] or '{}'),
            created_at=datetime.fromisoformat(row['created_at']),
            created_by=row['created_by'],
            is_active=bool(row['is_active'])
        ) for row in cursor.fetchall()]

    def get_template_hierarchy(self, template_id: str) -> List[PromptTemplate]:
        """Get the full template hierarchy chain."""
        templates = []
        current_id = template_id
        
        while current_id:
            template = self.get_template(current_id)
            if not template:
                break
            templates.append(template)
            current_id = template.parent_id
            
        return list(reversed(templates))  # Root to leaf order

    def find_templates(self, 
                      template_type: Optional[str] = None,
                      min_success_rate: Optional[float] = None,
                      active_only: bool = True) -> List[PromptTemplate]:
        """Find templates matching criteria."""
        cursor = self.conn.cursor()
        
        query = "SELECT * FROM prompt_templates WHERE 1=1"
        params = []
        
        if template_type:
            query += " AND type = ?"
            params.append(template_type)
            
        if min_success_rate is not None:
            query += " AND success_rate >= ?"
            params.append(min_success_rate)
            
        if active_only:
            query += " AND is_active = 1"
            
        cursor.execute(query, params)
        
        return [PromptTemplate(
            id=row['id'],
            parent_id=row['parent_id'],
            type=row['type'],
            name=row['name'],
            description=row['description'],
            content=row['content'],
            variables=json.loads(row['variables']),
            metadata=json.loads(row['metadata']),
            version=row['version'],
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at']),
            is_active=bool(row['is_active']),
            success_rate=row['success_rate'],
            usage_count=row['usage_count']
        ) for row in cursor.fetchall()]

    def __del__(self):
        """Clean up database connection."""
        if hasattr(self, 'conn'):
            self.conn.close()

# ---------------------------------------------------------------------------
# Backwards-compatibility helper
# ---------------------------------------------------------------------------

# Create a shared Jinja2 environment for simple template rendering
_default_jinja_env = Environment(
    loader=BaseLoader(),
    autoescape=False,
    trim_blocks=True,
    lstrip_blocks=True
)

def render_template(template_id: str, variables: Dict) -> str:
    """Render a template string or a .j2 file located in the project templates/ directory.

    This helper exists for legacy code paths that previously imported
    ``render_template`` directly from ``core.template_engine``.  It attempts
    to locate a file under ``templates/`` first; if not found, the argument is
    treated as an inline Jinja2 template string.
    """
    try:
        templates_dir = Path(__file__).parent.parent / "templates"
        potential_path = templates_dir / template_id

        if potential_path.exists() and potential_path.is_file():
            template_content = potential_path.read_text(encoding="utf-8")
        else:
            # Treat the input as raw template text
            template_content = template_id

        jinja_template = _default_jinja_env.from_string(template_content)
        return jinja_template.render(**variables)
    except Exception as e:
        # Re-raise with clearer context for callers
        raise Exception(f"Failed to render template '{template_id}': {e}")