"""
Context Injection System for Dream.OS

Handles intelligent context selection, formatting, and token optimization
for prompt generation. Ensures relevant context is injected while maintaining
token limits and preserving context priority.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import tiktoken
from collections import defaultdict

from .context_manager import Context, ContextManager

@dataclass
class ContextPriority:
    CRITICAL = 1.0
    HIGH = 0.8
    MEDIUM = 0.5
    LOW = 0.2

@dataclass
class TokenLimits:
    GPT_3_5_TURBO = 4096
    GPT_4 = 8192
    GPT_4_32K = 32768

@dataclass
class ContextConfig:
    model_name: str
    max_total_tokens: int = 4096
    max_context_tokens: int = 2048
    token_buffer: int = 500
    priority_threshold: float = 0.3
    compression_threshold: int = 1000

class ContextInjectionSystem:
    def __init__(self, context_manager: ContextManager):
        """Initialize the context injection system."""
        self.context_manager = context_manager
        self.tokenizer = tiktoken.get_encoding("cl100k_base")  # GPT-4 encoding

    def select_and_format_contexts(
        self,
        query: str,
        config: ContextConfig,
        required_context_ids: Optional[List[str]] = None
    ) -> Tuple[str, Dict]:
        """
        Select and format relevant contexts for injection.
        Returns formatted context string and metadata.
        """
        # Get relevant contexts
        contexts = self._get_relevant_contexts(query, required_context_ids)
        
        # Score and prioritize contexts
        scored_contexts = self._score_contexts(contexts, query)
        
        # Filter and format contexts within token limits
        formatted_contexts, metadata = self._format_contexts(
            scored_contexts, config
        )
        
        return formatted_contexts, metadata

    def _get_relevant_contexts(
        self,
        query: str,
        required_ids: Optional[List[str]] = None
    ) -> List[Context]:
        """Get relevant contexts, including required ones."""
        contexts = []
        
        # Add required contexts first
        if required_ids:
            for context_id in required_ids:
                context = self.context_manager.get_context(context_id)
                if context:
                    contexts.append(context)
        
        # Get additional relevant contexts
        relevant = self.context_manager.get_relevant_contexts(query)
        
        # Remove duplicates while preserving order
        seen = set(ctx.id for ctx in contexts)
        for ctx in relevant:
            if ctx.id not in seen:
                contexts.append(ctx)
                seen.add(ctx.id)
        
        return contexts

    def _score_contexts(
        self,
        contexts: List[Context],
        query: str
    ) -> List[Tuple[Context, float]]:
        """Score contexts based on relevance to query and metadata."""
        scored = []
        
        for ctx in contexts:
            # Base score is the context's relevance score
            score = ctx.relevance_score
            
            # Adjust score based on context type
            type_weights = {
                "strategic": 1.2,
                "project": 1.0,
                "conversation": 0.8,
                "task": 0.7
            }
            score *= type_weights.get(ctx.type, 1.0)
            
            # Adjust for recency if timestamp available
            if ctx.updated_at:
                time_diff = (datetime.now() - ctx.updated_at).days
                recency_factor = max(0.5, 1.0 - (time_diff / 30))  # Decay over 30 days
                score *= recency_factor
            
            # Consider relationships
            related = self.context_manager.get_related_contexts(ctx.id)
            relationship_boost = sum(strength for _, strength in related) / len(related) if related else 0
            score += relationship_boost * 0.2
            
            scored.append((ctx, score))
        
        return sorted(scored, key=lambda x: x[1], reverse=True)

    def _format_contexts(
        self,
        scored_contexts: List[Tuple[Context, float]],
        config: ContextConfig
    ) -> Tuple[str, Dict]:
        """Format contexts within token limits."""
        formatted_parts = []
        used_contexts = []
        total_tokens = 0
        metadata = {
            "included_contexts": [],
            "total_tokens": 0,
            "compression_applied": False
        }

        for context, score in scored_contexts:
            if score < config.priority_threshold:
                continue

            # Format context content
            formatted_content = self._format_single_context(context)
            tokens = len(self.tokenizer.encode(formatted_content))

            # Check if adding this context exceeds token limit
            if total_tokens + tokens > config.max_context_tokens:
                # Try compression if context is important
                if score > ContextPriority.HIGH and tokens > config.compression_threshold:
                    compressed = self._compress_context(context, config.max_context_tokens - total_tokens)
                    if compressed:
                        formatted_content = compressed
                        tokens = len(self.tokenizer.encode(compressed))
                        metadata["compression_applied"] = True
                else:
                    continue

            if total_tokens + tokens <= config.max_context_tokens:
                formatted_parts.append(formatted_content)
                total_tokens += tokens
                used_contexts.append(context.id)
                metadata["included_contexts"].append({
                    "id": context.id,
                    "type": context.type,
                    "title": context.title,
                    "tokens": tokens,
                    "score": score
                })

        metadata["total_tokens"] = total_tokens
        
        return "\n\n".join(formatted_parts), metadata

    def _format_single_context(self, context: Context) -> str:
        """Format a single context for injection."""
        # Format based on context type
        if context.type == "strategic":
            return f"Strategic Context '{context.title}':\n{context.content}"
        elif context.type == "project":
            return f"Project Context '{context.title}':\n{context.content}"
        elif context.type == "conversation":
            return f"Conversation History '{context.title}':\n{context.content}"
        elif context.type == "task":
            return f"Task Context '{context.title}':\n{context.content}"
        else:
            return f"Context '{context.title}':\n{context.content}"

    def _compress_context(self, context: Context, max_tokens: int) -> Optional[str]:
        """Compress context content to fit within token limit."""
        content = context.content
        tokens = len(self.tokenizer.encode(content))
        
        if tokens <= max_tokens:
            return content

        # Try different compression strategies
        strategies = [
            self._compress_by_truncation,
            self._compress_by_summarization,
            self._compress_by_key_points
        ]

        for strategy in strategies:
            compressed = strategy(content, max_tokens)
            if compressed:
                return compressed

        return None

    def _compress_by_truncation(self, content: str, max_tokens: int) -> Optional[str]:
        """Compress by intelligent truncation."""
        # Split into sentences
        sentences = content.split('. ')
        
        # Start with first sentence and add more until we hit token limit
        result = sentences[0]
        current_tokens = len(self.tokenizer.encode(result))
        
        for sentence in sentences[1:]:
            sentence_tokens = len(self.tokenizer.encode(sentence))
            if current_tokens + sentence_tokens + 2 <= max_tokens:  # +2 for '. '
                result += '. ' + sentence
                current_tokens += sentence_tokens + 2
            else:
                break
                
        return result + ' [truncated]' if result != content else None

    def _compress_by_summarization(self, content: str, max_tokens: int) -> Optional[str]:
        """Compress by extracting key sentences."""
        sentences = content.split('. ')
        if len(sentences) <= 3:
            return None

        # Take first and last sentence, plus one from middle
        summary_sentences = [
            sentences[0],
            sentences[len(sentences) // 2],
            sentences[-1]
        ]
        
        summary = '. '.join(summary_sentences) + ' [summarized]'
        if len(self.tokenizer.encode(summary)) <= max_tokens:
            return summary
            
        return None

    def _compress_by_key_points(self, content: str, max_tokens: int) -> Optional[str]:
        """Compress by extracting key points."""
        # Split into paragraphs
        paragraphs = content.split('\n\n')
        
        # Extract first sentence from each paragraph
        key_points = []
        for para in paragraphs:
            sentences = para.split('. ')
            if sentences:
                key_points.append(sentences[0])
                
        summary = '• ' + '\n• '.join(key_points) + ' [key points]'
        if len(self.tokenizer.encode(summary)) <= max_tokens:
            return summary
            
        return None

    def analyze_token_usage(self, content: str) -> Dict:
        """Analyze token usage of content."""
        tokens = self.tokenizer.encode(content)
        return {
            "total_tokens": len(tokens),
            "estimated_cost": len(tokens) * 0.0001,  # Example cost calculation
            "token_distribution": self._analyze_token_distribution(tokens)
        }

    def _analyze_token_distribution(self, tokens: List[int]) -> Dict:
        """Analyze distribution of token types."""
        distribution = defaultdict(int)
        
        # This is a simplified analysis
        for token in tokens:
            if token < 100:
                distribution["special"] += 1
            elif token < 1000:
                distribution["common"] += 1
            else:
                distribution["rare"] += 1
                
        return dict(distribution)