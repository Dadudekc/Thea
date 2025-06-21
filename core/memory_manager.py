"""
Digital Dreamscape - Memory Nexus Manager
The central repository for storing and retrieving conversation chronicles
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path
from sqlalchemy.sql import func

from .models import (
    Conversation, Message, Tag, ConversationTag, AnalysisResult, 
    Template, Setting, create_database_session, get_db_session
)

class MemoryNexus:
    """The Memory Nexus - central repository for conversation data"""
    
    def __init__(self, db_path: str = None):
        """Initialize the Memory Nexus with database path"""
        if db_path is None:
            # Default to data directory
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)
            db_path = str(data_dir / "dreamscape.db")
        
        self.db_path = db_path
        self.SessionLocal = create_database_session(db_path)
        
        # Ensure database exists and has default data
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database with schema and default data"""
        # Create tables
        engine = self.SessionLocal().bind
        from .models import Base
        Base.metadata.create_all(engine)
        
        # Initialize with default data if empty
        with self.SessionLocal() as session:
            # Check if we have any templates
            template_count = session.query(Template).count()
            if template_count == 0:
                self._create_default_templates(session)
            
            # Check if we have any settings
            setting_count = session.query(Setting).count()
            if setting_count == 0:
                self._create_default_settings(session)
    
    def _create_default_templates(self, session):
        """Create default analysis templates"""
        default_templates = [
            {
                'name': 'Basic Summary',
                'description': 'Generate a basic summary of the conversation',
                'template_content': '''Please provide a concise summary of this conversation, highlighting the key points and main takeaways.

Conversation Title: {{ conversation.title }}
Message Count: {{ conversation.message_count }}''',
                'category': 'summary',
                'is_default': True
            },
            {
                'name': 'Topic Analysis',
                'description': 'Extract main topics and themes from the conversation',
                'template_content': '''Analyze this conversation and identify the main topics, themes, and key concepts discussed.

Conversation Title: {{ conversation.title }}
Please provide:
1. Main topics (3-5 key areas)
2. Important themes
3. Key insights or conclusions''',
                'category': 'analysis',
                'is_default': True
            },
            {
                'name': 'Action Items',
                'description': 'Extract action items and next steps from the conversation',
                'template_content': '''Review this conversation and identify any action items, tasks, or next steps mentioned.

Conversation Title: {{ conversation.title }}
Please list:
1. Action items with assignees (if mentioned)
2. Deadlines or timeframes
3. Dependencies or blockers
4. Priority levels''',
                'category': 'actions',
                'is_default': True
            }
        ]
        
        for template_data in default_templates:
            template = Template(**template_data)
            session.add(template)
        
        session.commit()
    
    def _create_default_settings(self, session):
        """Create default application settings"""
        default_settings = [
            {'key': 'database_version', 'value': '1.0', 'description': 'Current database schema version'},
            {'key': 'max_conversations', 'value': '10000', 'description': 'Maximum number of conversations to store'},
            {'key': 'auto_analyze', 'value': 'false', 'description': 'Automatically analyze new conversations'},
            {'key': 'default_template', 'value': '1', 'description': 'Default template ID for new analyses'},
            {'key': 'backup_enabled', 'value': 'true', 'description': 'Enable automatic database backups'},
            {'key': 'backup_interval_hours', 'value': '24', 'description': 'Hours between automatic backups'}
        ]
        
        for setting_data in default_settings:
            setting = Setting(**setting_data)
            session.add(setting)
        
        session.commit()
    
    # Conversation Management
    def save_conversation(self, conversation_data: Dict[str, Any]) -> int:
        """Save a conversation to the database"""
        with self.SessionLocal() as session:
            # Check if conversation already exists
            existing = session.query(Conversation).filter_by(url=conversation_data.get('url')).first()
            if existing:
                # Update existing conversation
                existing.title = conversation_data.get('title', existing.title)
                existing.updated_at = datetime.now()
                if 'metadata' in conversation_data:
                    existing.set_metadata(conversation_data['metadata'])
                conversation_id = existing.id
            else:
                # Create new conversation
                conversation = Conversation(
                    title=conversation_data.get('title', 'Untitled'),
                    url=conversation_data.get('url'),
                    source=conversation_data.get('source', 'chatgpt'),
                    status=conversation_data.get('status', 'active')
                )
                if 'metadata' in conversation_data:
                    conversation.set_metadata(conversation_data['metadata'])
                session.add(conversation)
                session.flush()  # Get the ID
                conversation_id = conversation.id
            # Save messages if provided
            if 'messages' in conversation_data:
                self._save_messages(session, conversation_id, conversation_data['messages'])
                session.flush()  # Ensure messages are written
                # Update message_count and word_count after saving messages
                conv = session.query(Conversation).filter_by(id=conversation_id).first()
                conv.message_count = session.query(Message).filter_by(conversation_id=conversation_id).count()
                conv.word_count = session.query(Message).filter_by(conversation_id=conversation_id).with_entities(func.sum(Message.word_count)).scalar() or 0
                session.commit()  # Commit after updating counts
                session.refresh(conv)  # Refresh to ensure up-to-date
            else:
                session.commit()
            return conversation_id
    
    def _save_messages(self, session, conversation_id: int, messages: List[Dict[str, Any]]):
        """Save messages for a conversation"""
        # Clear existing messages
        session.query(Message).filter_by(conversation_id=conversation_id).delete()
        
        # Add new messages
        for i, msg_data in enumerate(messages):
            message = Message(
                conversation_id=conversation_id,
                role=msg_data.get('role', 'user'),
                content=msg_data.get('content', ''),
                message_index=i,
                timestamp=msg_data.get('timestamp', datetime.now())
            )
            
            # Calculate word count and token estimate
            message.calculate_word_count()
            message.estimate_tokens()
            
            if 'metadata' in msg_data:
                message.set_metadata(msg_data['metadata'])
            
            session.add(message)
        session.flush()  # Ensure all messages are added
    
    def get_conversation(self, conversation_id: int) -> Optional[Dict[str, Any]]:
        """Get a conversation by ID with all its messages"""
        with self.SessionLocal() as session:
            conversation = session.query(Conversation).filter_by(id=conversation_id).first()
            if not conversation:
                return None
            
            # Get messages
            messages = session.query(Message).filter_by(conversation_id=conversation_id).order_by(Message.message_index).all()
            
            return {
                'id': conversation.id,
                'title': conversation.title,
                'url': conversation.url,
                'created_at': conversation.created_at,
                'updated_at': conversation.updated_at,
                'message_count': conversation.message_count,
                'word_count': conversation.word_count,
                'source': conversation.source,
                'status': conversation.status,
                'metadata': conversation.get_metadata(),
                'tags': conversation.get_tag_ids(),
                'messages': [
                    {
                        'id': msg.id,
                        'role': msg.role,
                        'content': msg.content,
                        'timestamp': msg.timestamp,
                        'message_index': msg.message_index,
                        'word_count': msg.word_count,
                        'token_estimate': msg.token_estimate,
                        'metadata': msg.get_metadata()
                    }
                    for msg in messages
                ]
            }
    
    def get_conversations(self, limit: int = 100, offset: int = 0, 
                         source: str = None, status: str = None) -> List[Dict[str, Any]]:
        """Get list of conversations with optional filtering"""
        with self.SessionLocal() as session:
            query = session.query(Conversation)
            
            if source:
                query = query.filter_by(source=source)
            if status:
                query = query.filter_by(status=status)
            
            conversations = query.order_by(Conversation.updated_at.desc()).limit(limit).offset(offset).all()
            
            return [
                {
                    'id': conv.id,
                    'title': conv.title,
                    'url': conv.url,
                    'created_at': conv.created_at,
                    'updated_at': conv.updated_at,
                    'message_count': conv.message_count,
                    'word_count': conv.word_count,
                    'source': conv.source,
                    'status': conv.status,
                    'metadata': conv.get_metadata(),
                    'tags': conv.get_tag_ids()
                }
                for conv in conversations
            ]
    
    def search_conversations(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search conversations by title and content (case-insensitive, SQLite-compatible)"""
        with self.SessionLocal() as session:
            session.commit()  # Ensure all data is committed before search
            q = f"%{query.lower()}%"
            # Search in conversation titles (case-insensitive)
            title_results = session.query(Conversation).filter(
                func.lower(Conversation.title).like(q)
            ).all()
            # Search in message content (case-insensitive)
            content_results = session.query(Conversation).join(Message).filter(
                func.lower(Message.content).like(q)
            ).distinct().all()
            # Combine and deduplicate results
            all_results = list(set(title_results + content_results))
            # Convert to dictionaries
            results = []
            for conv in all_results[:limit]:
                results.append({
                    'id': conv.id,
                    'title': conv.title,
                    'url': conv.url,
                    'created_at': conv.created_at,
                    'updated_at': conv.updated_at,
                    'message_count': conv.message_count,
                    'word_count': conv.word_count,
                    'source': conv.source,
                    'status': conv.status,
                    'metadata': conv.get_metadata(),
                    'tags': conv.get_tag_ids()
                })
            return results
    
    def delete_conversation(self, conversation_id: int) -> bool:
        """Delete a conversation and all its data"""
        with self.SessionLocal() as session:
            conversation = session.query(Conversation).filter_by(id=conversation_id).first()
            if not conversation:
                return False
            
            session.delete(conversation)
            session.commit()
            return True
    
    # Tag Management
    def create_tag(self, name: str, color: str = '#007bff', description: str = None) -> int:
        """Create a new tag"""
        with self.SessionLocal() as session:
            tag = Tag(name=name, color=color, description=description)
            session.add(tag)
            session.flush()
            tag_id = tag.id
            session.commit()
            return tag_id
    
    def get_tags(self) -> List[Dict[str, Any]]:
        """Get all tags"""
        with self.SessionLocal() as session:
            tags = session.query(Tag).order_by(Tag.name).all()
            return [
                {
                    'id': tag.id,
                    'name': tag.name,
                    'color': tag.color,
                    'description': tag.description,
                    'usage_count': tag.usage_count,
                    'created_at': tag.created_at
                }
                for tag in tags
            ]
    
    def add_tag_to_conversation(self, conversation_id: int, tag_id: int) -> bool:
        """Add a tag to a conversation"""
        with self.SessionLocal() as session:
            # Check if both exist
            conversation = session.query(Conversation).filter_by(id=conversation_id).first()
            tag = session.query(Tag).filter_by(id=tag_id).first()
            if not conversation or not tag:
                return False
            # Check if relationship already exists
            existing = session.query(ConversationTag).filter_by(
                conversation_id=conversation_id, tag_id=tag_id
            ).first()
            if not existing:
                conversation_tag = ConversationTag(
                    conversation_id=conversation_id,
                    tag_id=tag_id
                )
                session.add(conversation_tag)
                # Update conversation's tag list
                tag_ids = conversation.get_tag_ids()
                if tag_id not in tag_ids:
                    tag_ids.append(tag_id)
                    conversation.set_tag_ids(tag_ids)
                session.commit()
            return True
    
    def remove_tag_from_conversation(self, conversation_id: int, tag_id: int) -> bool:
        """Remove a tag from a conversation"""
        with self.SessionLocal() as session:
            conversation_tag = session.query(ConversationTag).filter_by(
                conversation_id=conversation_id, tag_id=tag_id
            ).first()
            conversation = session.query(Conversation).filter_by(id=conversation_id).first()
            if conversation_tag:
                session.delete(conversation_tag)
                # Update conversation's tag list
                if conversation:
                    tag_ids = conversation.get_tag_ids()
                    if tag_id in tag_ids:
                        tag_ids.remove(tag_id)
                        conversation.set_tag_ids(tag_ids)
                session.commit()
                return True
            return False
    
    # Analysis Management
    def save_analysis_result(self, conversation_id: int, analysis_type: str, 
                           result_data: Dict[str, Any], template_used: str = None,
                           processing_time: float = None) -> int:
        """Save an analysis result"""
        with self.SessionLocal() as session:
            analysis = AnalysisResult(
                conversation_id=conversation_id,
                analysis_type=analysis_type,
                result_data=json.dumps(result_data),
                template_used=template_used,
                processing_time=processing_time
            )
            session.add(analysis)
            session.flush()
            analysis_id = analysis.id
            session.commit()
            return analysis_id
    
    def get_analysis_results(self, conversation_id: int) -> List[Dict[str, Any]]:
        """Get all analysis results for a conversation"""
        with self.SessionLocal() as session:
            results = session.query(AnalysisResult).filter_by(
                conversation_id=conversation_id
            ).order_by(AnalysisResult.created_at.desc()).all()
            
            return [
                {
                    'id': result.id,
                    'analysis_type': result.analysis_type,
                    'result_data': result.get_result_data(),
                    'created_at': result.created_at,
                    'template_used': result.template_used,
                    'processing_time': result.processing_time
                }
                for result in results
            ]
    
    # Template Management
    def get_templates(self, category: str = None) -> List[Dict[str, Any]]:
        """Get templates, optionally filtered by category"""
        with self.SessionLocal() as session:
            query = session.query(Template)
            if category:
                query = query.filter_by(category=category)
            
            templates = query.order_by(Template.name).all()
            return [
                {
                    'id': template.id,
                    'name': template.name,
                    'description': template.description,
                    'template_content': template.template_content,
                    'category': template.category,
                    'is_default': template.is_default,
                    'usage_count': template.usage_count,
                    'created_at': template.created_at,
                    'updated_at': template.updated_at
                }
                for template in templates
            ]
    
    def create_template(self, name: str, template_content: str, description: str = None,
                       category: str = 'general', is_default: bool = False) -> int:
        """Create a new template"""
        with self.SessionLocal() as session:
            template = Template(
                name=name,
                description=description,
                template_content=template_content,
                category=category,
                is_default=is_default
            )
            session.add(template)
            session.flush()
            template_id = template.id
            session.commit()
            return template_id
    
    # Settings Management
    def get_setting(self, key: str, default: str = None) -> str:
        """Get a setting value"""
        with self.SessionLocal() as session:
            setting = session.query(Setting).filter_by(key=key).first()
            return setting.value if setting else default
    
    def set_setting(self, key: str, value: str, description: str = None):
        """Set a setting value"""
        with self.SessionLocal() as session:
            setting = session.query(Setting).filter_by(key=key).first()
            if setting:
                setting.value = value
                setting.updated_at = datetime.now()
                if description:
                    setting.description = description
            else:
                setting = Setting(key=key, value=value, description=description)
                session.add(setting)
            
            session.commit()
    
    # Statistics and Analytics
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        with self.SessionLocal() as session:
            total_conversations = session.query(Conversation).count()
            total_messages = session.query(Message).count()
            total_words = session.query(Conversation).with_entities(
                func.sum(Conversation.word_count)
            ).scalar() or 0
            total_tags = session.query(Tag).count()
            total_analyses = session.query(AnalysisResult).count()
            
            # Recent activity (last 7 days)
            week_ago = datetime.now() - timedelta(days=7)
            recent_conversations = session.query(Conversation).filter(
                Conversation.created_at >= week_ago
            ).count()
            
            return {
                'total_conversations': total_conversations,
                'total_messages': total_messages,
                'total_words': total_words,
                'total_tags': total_tags,
                'total_analyses': total_analyses,
                'recent_conversations': recent_conversations
            }
    
    def backup_database(self, backup_path: str = None) -> bool:
        """Create a backup of the database"""
        if backup_path is None:
            backup_dir = Path("data/backups")
            backup_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = str(backup_dir / f"dreamscape_backup_{timestamp}.db")
        
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            return True
        except Exception as e:
            print(f"Backup failed: {e}")
            return False 