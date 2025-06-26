#!/usr/bin/env python3
"""
Content Processor for DevLog Generator
Handles message processing and content block creation.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ContentBlock:
    """Represents a block of content from the conversation."""
    type: str  # 'question', 'explanation', 'code', 'error', 'solution'
    content: str
    metadata: Dict[str, Any]
    timestamp: datetime

class ContentProcessor:
    """Handles content processing and block creation."""
    
    def __init__(self):
        """Initialize the content processor."""
        pass
    
    def process_message(self, message: Dict[str, Any]) -> Optional[ContentBlock]:
        """Process a single message into a content block."""
        content = message.get("content", "").strip()
        if not content:
            return None
            
        # Determine message type and metadata
        metadata = {}
        msg_type = "explanation"  # default type
        
        # Check for code blocks
        if "```" in content:
            msg_type = "code"
            metadata["language"] = self._detect_language(content)
            
        # Check for errors/exceptions
        elif any(err in content.lower() for err in ["error", "exception", "failed"]):
            msg_type = "error"
            
        # Check for solutions
        elif any(sol in content.lower() for sol in ["solution", "fixed", "resolved"]):
            msg_type = "solution"
            
        # Check for questions
        elif content.strip().endswith("?"):
            msg_type = "question"
            
        # Extract additional metadata
        metadata.update(self._extract_metadata(content))
        
        return ContentBlock(
            type=msg_type,
            content=content,
            metadata=metadata,
            timestamp=datetime.fromisoformat(message.get("timestamp", datetime.now().isoformat()))
        )
    
    def _detect_language(self, content: str) -> str:
        """Detect programming language from code block."""
        if "```" not in content:
            return ""
        
        # Extract language identifier
        start = content.find("```") + 3
        end = content.find("\n", start)
        if start < end:
            return content[start:end].strip()
        return ""
    
    def _extract_metadata(self, content: str) -> Dict[str, Any]:
        """Extract additional metadata from content."""
        metadata = {}
        # Add metadata extraction logic here
        return metadata 

    def process_content(self, raw: dict) -> dict:
        """Return raw conversation content as-is.

        ScraperOrchestrator currently expects a `process_content` helper. Adding
        this lightweight passthrough keeps existing workflow intact while
        allowing future enrichment (e.g. message re-formatting, metadata
        extraction) without breaking callers.
        """
        return raw 