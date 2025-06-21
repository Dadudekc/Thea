"""
Digital Dreamscape - Memory Nexus Models
The ORM artifacts that bind the sacred runes to Python objects
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
import json
from datetime import datetime
from typing import List, Dict, Optional, Any

Base = declarative_base()

class Conversation(Base):
    """The main chronicles - represents a ChatGPT conversation"""
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), unique=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    message_count = Column(Integer, default=0)
    word_count = Column(Integer, default=0)
    source = Column(String(50), default='chatgpt')
    status = Column(String(50), default='active')
    conversation_metadata = Column(Text)  # JSON string - renamed from metadata
    tags = Column(Text)  # JSON array of tag IDs
    
    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    analysis_results = relationship("AnalysisResult", back_populates="conversation", cascade="all, delete-orphan")
    conversation_tags = relationship("ConversationTag", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, title='{self.title}', messages={self.message_count})>"
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata as dictionary"""
        if self.conversation_metadata:
            return json.loads(self.conversation_metadata)
        return {}
    
    def set_metadata(self, metadata: Dict[str, Any]):
        """Set metadata from dictionary"""
        self.conversation_metadata = json.dumps(metadata)
    
    def get_tag_ids(self) -> List[int]:
        """Get tag IDs as list"""
        if self.tags:
            return json.loads(self.tags)
        return []
    
    def set_tag_ids(self, tag_ids: List[int]):
        """Set tag IDs from list"""
        self.tags = json.dumps(tag_ids)
    
    def add_tag(self, tag_id: int):
        """Add a tag to this conversation"""
        current_tags = self.get_tag_ids()
        if tag_id not in current_tags:
            current_tags.append(tag_id)
            self.set_tag_ids(current_tags)
    
    def remove_tag(self, tag_id: int):
        """Remove a tag from this conversation"""
        current_tags = self.get_tag_ids()
        if tag_id in current_tags:
            current_tags.remove(tag_id)
            self.set_tag_ids(current_tags)

class Message(Base):
    """The individual scrolls within each chronicle - represents a single message"""
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'), nullable=False)
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=func.now())
    message_index = Column(Integer, nullable=False)  # Order within conversation
    word_count = Column(Integer, default=0)
    token_estimate = Column(Integer, default=0)
    message_metadata = Column(Text)  # JSON string - renamed from metadata
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    
    def __repr__(self):
        return f"<Message(id={self.id}, role='{self.role}', index={self.message_index})>"
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata as dictionary"""
        if self.message_metadata:
            return json.loads(self.message_metadata)
        return {}
    
    def set_metadata(self, metadata: Dict[str, Any]):
        """Set metadata from dictionary"""
        self.message_metadata = json.dumps(metadata)
    
    def calculate_word_count(self):
        """Calculate and set word count"""
        self.word_count = len(self.content.split())
    
    def estimate_tokens(self):
        """Rough token estimation (4 chars per token)"""
        self.token_estimate = len(self.content) // 4

class Tag(Base):
    """The classification runes - represents a tag for organizing conversations"""
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    color = Column(String(7), default='#007bff')  # Hex color
    description = Column(Text)
    created_at = Column(DateTime, default=func.now())
    usage_count = Column(Integer, default=0)
    
    # Relationships
    conversation_tags = relationship("ConversationTag", back_populates="tag", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}', usage={self.usage_count})>"

class ConversationTag(Base):
    """The binding runes - junction table for conversation-tag relationships"""
    __tablename__ = 'conversation_tags'
    
    conversation_id = Column(Integer, ForeignKey('conversations.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags.id'), primary_key=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    conversation = relationship("Conversation", back_populates="conversation_tags")
    tag = relationship("Tag", back_populates="conversation_tags")
    
    def __repr__(self):
        return f"<ConversationTag(conversation_id={self.conversation_id}, tag_id={self.tag_id})>"

class AnalysisResult(Base):
    """The insight crystals - represents analysis results for conversations"""
    __tablename__ = 'analysis_results'
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'), nullable=False)
    analysis_type = Column(String(50), nullable=False)  # 'summary', 'sentiment', 'topics', 'custom'
    result_data = Column(Text, nullable=False)  # JSON result
    created_at = Column(DateTime, default=func.now())
    template_used = Column(String(200))  # Which template was used
    processing_time = Column(Float)  # Time taken in seconds
    
    # Relationships
    conversation = relationship("Conversation", back_populates="analysis_results")
    
    def __repr__(self):
        return f"<AnalysisResult(id={self.id}, type='{self.analysis_type}', conversation_id={self.conversation_id})>"
    
    def get_result_data(self) -> Dict[str, Any]:
        """Get result data as dictionary"""
        if self.result_data:
            return json.loads(self.result_data)
        return {}
    
    def set_result_data(self, result_data: Dict[str, Any]):
        """Set result data from dictionary"""
        self.result_data = json.dumps(result_data)

class Template(Base):
    """The Jinja Forge artifacts - represents analysis templates"""
    __tablename__ = 'templates'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    template_content = Column(Text, nullable=False)
    category = Column(String(50), default='general')
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    usage_count = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<Template(id={self.id}, name='{self.name}', category='{self.category}')>"

class Setting(Base):
    """The configuration scrolls - represents application settings"""
    __tablename__ = 'settings'
    
    key = Column(String(100), primary_key=True)
    value = Column(Text, nullable=False)
    description = Column(Text)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Setting(key='{self.key}', value='{self.value}')>"
    
    def get_value_as_bool(self) -> bool:
        """Get value as boolean"""
        return self.value.lower() in ('true', '1', 'yes', 'on')
    
    def get_value_as_int(self) -> int:
        """Get value as integer"""
        try:
            return int(self.value)
        except (ValueError, TypeError):
            return 0
    
    def get_value_as_float(self) -> float:
        """Get value as float"""
        try:
            return float(self.value)
        except (ValueError, TypeError):
            return 0.0

# Database session factory
def create_database_session(db_path: str):
    """Create database engine and session factory"""
    engine = create_engine(f'sqlite:///{db_path}', echo=False)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal

# Convenience function to get database session
def get_db_session(db_path: str):
    """Get a database session"""
    SessionLocal = create_database_session(db_path)
    return SessionLocal() 