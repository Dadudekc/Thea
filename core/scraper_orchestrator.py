#!/usr/bin/env python3
"""
Scraper Orchestrator for Dream.OS
=================================

Central orchestrator for all ChatGPT scraping operations.
Provides a clean interface for both GUI and CLI components.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from scrapers.conversation_fetcher import ConversationFetcher

logger = logging.getLogger(__name__)

@dataclass
class ConversationData:
    """Data structure for conversation information."""
    id: str
    title: str
    url: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    message_count: int = 0
    content: Optional[str] = None
    processed: bool = False

@dataclass
class ScrapingResult:
    """Result structure for scraping operations."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict] = None

class ScraperOrchestrator:
    """
    Central orchestrator for ChatGPT scraping operations.
    
    This class coordinates all scraping modules and provides a clean
    interface for both GUI and CLI components. It follows the facade
    pattern to hide complexity and provide a unified API.
    """
    
    def __init__(self, headless: bool = False, use_undetected: bool = True):
        """
        Initialize the scraper orchestrator.
        
        Args:
            headless: Whether to run browser in headless mode
            use_undetected: Whether to use undetected-chromedriver
        """
        self.headless = headless
        self.use_undetected = use_undetected
        self.driver = None
        self.is_initialized = False
        
        # Initialize component managers
        self._initialize_components()
        
        logger.info("ScraperOrchestrator initialized")
    
    def _initialize_components(self):
        """Initialize all scraping components."""
        try:
            from scrapers.browser_manager import BrowserManager
            from scrapers.cookie_manager import CookieManager
            from scrapers.login_handler import LoginHandler
            from scrapers.conversation_list_manager import ConversationListManager
            from scrapers.conversation_extractor import ConversationExtractor
            from scrapers.content_processor import ContentProcessor
            
            # Initialize managers
            self.browser_manager = BrowserManager(
                headless=self.headless, 
                use_undetected=self.use_undetected
            )
            self.cookie_manager = CookieManager('data/chatgpt_cookies.pkl')
            self.login_handler = LoginHandler()
            self.conversation_list_manager = ConversationListManager()
            self.conversation_extractor = ConversationExtractor()
            self.content_processor = ContentProcessor()
            self.fetcher = ConversationFetcher(self.conversation_extractor)
            
            logger.info("All scraping components initialized successfully")
            
        except ImportError as e:
            logger.error(f"Failed to initialize scraping components: {e}")
            raise
    
    def initialize_browser(self) -> ScrapingResult:
        """
        Initialize the browser session.
        
        Returns:
            ScrapingResult with success status and any error information
        """
        try:
            self.driver = self.browser_manager.create_driver()
            self.is_initialized = True
            logger.info("Browser initialized successfully")
            return ScrapingResult(success=True)
            
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            return ScrapingResult(success=False, error=str(e))
    
    def login_and_save_cookies(self, username: Optional[str] = None, 
                              password: Optional[str] = None) -> ScrapingResult:
        """
        Handle login process and save cookies.
        
        Reuses LoginHandler.ensure_login_with_cookies for the full cookie →
        creds → manual tri-flow instead of duplicating logic here.  This keeps
        a single source-of-truth for login behaviour while preserving the
        previous public API & return semantics expected by downstream scripts
        (namely the *requires_manual_login* metadata key).
        """
        if not self.is_initialized:
            result = self.initialize_browser()
            if not result.success:
                return result

        # Propagate credentials that may have been supplied explicitly – this
        # allows callers to override env vars without re-instantiating the
        # orchestrator.
        if username:
            self.login_handler.username = username
        if password:
            self.login_handler.password = password

        try:
            # Phase-1: Attempt cookie+credential login (manual fallback *disabled*)
            ok = self.login_handler.ensure_login_with_cookies(
                self.driver,
                self.cookie_manager,
                allow_manual=False,
            )
            if ok:
                return ScrapingResult(success=True, metadata={"method": "cookies/credentials"})

            # Phase-2: Signal to caller that manual login is required so they
            # can decide how/when to wait.  We keep the exact metadata key used
            # previously so existing scripts remain unchanged.
            return ScrapingResult(
                success=False,
                error="Manual login required",
                metadata={"requires_manual_login": True},
            )
        except Exception as e:
            logger.error(f"Login process failed: {e}")
            return ScrapingResult(success=False, error=str(e))
    
    def extract_conversations(
        self,
        max_conversations: Optional[int] = None,
        use_cache: bool = False,
        cache_file: str = "data/conversation_index.json",
        skip_before: Optional[datetime] = None,
        skip_titles: Optional[List[str]] = None,
    ) -> ScrapingResult:
        """
        Extract list of conversations.
        
        Args:
            max_conversations: Maximum number of conversations to extract
            
        Returns:
            ScrapingResult with list of ConversationData objects
        """
        if not self.is_initialized:
            return ScrapingResult(success=False, error="Browser not initialized")
        
        try:
            conversations = self.conversation_list_manager.get_conversation_list(
                self.driver,
                max_conversations=max_conversations,
                use_cache=use_cache,
                cache_file=cache_file,
                skip_before=skip_before,
                skip_titles=skip_titles,
            )
            
            # Convert to ConversationData objects
            conversation_data = []
            for conv in conversations:
                conv_data = ConversationData(
                    id=conv.get('id', ''),
                    title=conv.get('title', ''),
                    url=conv.get('url', ''),
                    created_at=conv.get('created_at'),
                    updated_at=conv.get('updated_at'),
                    message_count=conv.get('message_count', 0)
                )
                conversation_data.append(conv_data)
            
            logger.info(f"Extracted {len(conversation_data)} conversations")
            return ScrapingResult(
                success=True, 
                data=conversation_data,
                metadata={"count": len(conversation_data)}
            )
            
        except Exception as e:
            logger.error(f"Failed to extract conversations: {e}")
            return ScrapingResult(success=False, error=str(e))
    
    def extract_conversation_content(self, conversation_url: str) -> ScrapingResult:
        """
        Extract content from a specific conversation.
        
        Args:
            conversation_url: URL of the conversation to extract
            
        Returns:
            ScrapingResult with conversation content
        """
        if not self.is_initialized:
            return ScrapingResult(success=False, error="Browser not initialized")
        
        try:
            # Enter the conversation
            self.conversation_extractor.enter_conversation(self.driver, conversation_url)
            
            # Extract content
            content = self.conversation_extractor.get_conversation_content(self.driver)
            
            # Process content
            processed_content = self.content_processor.process_content(content)
            
            logger.info(f"Extracted content from conversation: {conversation_url}")
            return ScrapingResult(
                success=True,
                data=processed_content,
                metadata={"url": conversation_url}
            )
            
        except Exception as e:
            logger.error(f"Failed to extract conversation content: {e}")
            return ScrapingResult(success=False, error=str(e))

    def fetch_conversations_parallel(self, conversation_urls: List[str], workers: int = 4,
                                     force_download: bool = False) -> ScrapingResult:
        """Fetch multiple conversations in parallel with retry tracking."""
        if not self.is_initialized:
            return ScrapingResult(success=False, error="Browser not initialized")

        results: List[Dict[str, Any]] = []

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(self.fetcher.fetch, self.driver, url): url for url in conversation_urls}

            for future in as_completed(futures):
                url = futures[future]
                data = future.result()
                if data:
                    results.append(data)
                else:
                    logger.warning("Failed to fetch %s", url)

        self.fetcher.save_failures()
        result_obj = ScrapingResult(
            success=len(results) > 0,
            data=results,
            metadata={
                "total_requested": len(conversation_urls),
                "successful": len(results),
                "failed": len(conversation_urls) - len(results),
            },
        )

        self._write_summary(result_obj)
        return result_obj

    def extract_multiple_conversations(self, conversation_urls: List[str]) -> ScrapingResult:
        """
        Extract content from multiple conversations.
        
        Args:
            conversation_urls: List of conversation URLs to extract
            
        Returns:
            ScrapingResult with list of conversation contents
        """
        return self.fetch_conversations_parallel(conversation_urls)
    
    def generate_blog_post(self, conversations: List[ConversationData]) -> ScrapingResult:
        """
        Generate a blog post from conversations.
        
        Args:
            conversations: List of conversation data to process
            
        Returns:
            ScrapingResult with generated blog content
        """
        try:
            from scrapers.blog_generator import BlogGenerator
            
            blog_generator = BlogGenerator()
            
            # Extract content from conversations if not already extracted
            for conv in conversations:
                if not conv.content:
                    result = self.extract_conversation_content(conv.url)
                    if result.success:
                        conv.content = result.data
                    else:
                        logger.warning(f"Failed to extract content for {conv.url}")
            
            # Generate blog post
            blog_content = blog_generator.generate_blog_post(conversations)
            
            return ScrapingResult(
                success=True,
                data=blog_content,
                metadata={"conversations_processed": len(conversations)}
            )
            
        except Exception as e:
            logger.error(f"Failed to generate blog post: {e}")
            return ScrapingResult(success=False, error=str(e))
    
    def generate_devlog(self, conversations: List[ConversationData]) -> ScrapingResult:
        """
        Generate a devlog from conversations.
        
        Args:
            conversations: List of conversation data to process
            
        Returns:
            ScrapingResult with generated devlog content
        """
        try:
            from scrapers.devlog_generator import DevlogGenerator
            
            devlog_generator = DevlogGenerator()
            
            # Extract content from conversations if not already extracted
            for conv in conversations:
                if not conv.content:
                    result = self.extract_conversation_content(conv.url)
                    if result.success:
                        conv.content = result.data
                    else:
                        logger.warning(f"Failed to extract content for {conv.url}")
            
            # Generate devlog
            devlog_content = devlog_generator.generate_devlog(conversations)
            
            return ScrapingResult(
                success=True,
                data=devlog_content,
                metadata={"conversations_processed": len(conversations)}
            )
            
        except Exception as e:
            logger.error(f"Failed to generate devlog: {e}")
            return ScrapingResult(success=False, error=str(e))
    
    def generate_social_content(self, conversations: List[ConversationData]) -> ScrapingResult:
        """
        Generate social media content from conversations.
        
        Args:
            conversations: List of conversation data to process
            
        Returns:
            ScrapingResult with generated social content
        """
        try:
            from scrapers.social_content_generator import SocialContentGenerator
            
            social_generator = SocialContentGenerator()
            
            # Extract content from conversations if not already extracted
            for conv in conversations:
                if not conv.content:
                    result = self.extract_conversation_content(conv.url)
                    if result.success:
                        conv.content = result.data
                    else:
                        logger.warning(f"Failed to extract content for {conv.url}")
            
            # Generate social content
            social_content = social_generator.generate_social_content(conversations)
            
            return ScrapingResult(
                success=True,
                data=social_content,
                metadata={"conversations_processed": len(conversations)}
            )
            
        except Exception as e:
            logger.error(f"Failed to generate social content: {e}")
            return ScrapingResult(success=False, error=str(e))
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current orchestrator status.
        
        Returns:
            Dictionary with status information
        """
        return {
            "initialized": self.is_initialized,
            "headless": self.headless,
            "use_undetected": self.use_undetected,
            "driver_active": self.driver is not None,
            "components_loaded": hasattr(self, 'browser_manager')
        }

    def _write_summary(self, result: ScrapingResult) -> None:
        """Write a human-readable summary log for a scraping run."""
        try:
            Path("outputs").mkdir(parents=True, exist_ok=True)
            summary_path = Path("outputs/scrape_summary.md")
            with open(summary_path, "w", encoding="utf-8") as f:
                f.write(f"# Scrape Summary\n\n")
                meta = result.metadata or {}
                f.write(f"Total requested: {meta.get('total_requested')}\n\n")
                f.write(f"Successful: {meta.get('successful')}\n\n")
                f.write(f"Failed: {meta.get('failed')}\n\n")
                if self.fetcher.failures:
                    f.write("## Failures\n")
                    for fail in self.fetcher.failures:
                        f.write(f"- {fail.url} ({fail.last_error})\n")
            logger.info("Summary written to %s", summary_path)
        except Exception as e:
            logger.warning("Failed to write summary log: %s", e)
    
    def close(self):
        """Close the browser and clean up resources."""
        try:
            if self.driver:
                self.browser_manager.close_driver()
                self.driver = None
                self.is_initialized = False
                logger.info("Browser closed successfully")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close() 