#!/usr/bin/env python3
"""
Conversation List Manager for ChatGPT Scraper
Handles conversation listing and discovery operations.
"""

import logging
from typing import List, Dict
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
import time
import random

logger = logging.getLogger(__name__)

class ConversationListManager:
    """Handles conversation list extraction and management."""
    
    def __init__(self, timeout: int = 30):
        """
        Initialize the conversation list manager.
        
        Args:
            timeout: Timeout for web operations
        """
        self.timeout = timeout
        self.max_scroll_attempts = 150  # Increased from 10
        self.scroll_pause_time = 1.5
        self.burst_scroll_threshold = 3  # Number of attempts with no new conversations before burst
    
    def get_conversation_list(self, driver, max_conversations: int | None = None) -> List[Dict[str, str]]:
        """
        Get list of available conversations with improved scrolling.
        
        Args:
            driver: Selenium webdriver instance
            max_conversations: Maximum number of conversations to return
            
        Returns:
            List of conversation dictionaries
        """
        if not driver:
            logger.warning("No driver provided for conversation list")
            return []
            
        try:
            logger.info("Extracting conversation list (sidebar scroll)…")

            # ------------------------------------------------------------------
            # Ensure sidebar shows *all time* conversations – ChatGPT sometimes
            # defaults to a 30-day filter which would cap results at ~30.
            # We look for a dropdown/button that contains the text "Last" and
            # then pick the option labelled "All time" if present.
            # ------------------------------------------------------------------
            self._ensure_all_time_filter(driver)

            conversations: list[dict[str, str]] = []

            container = self._locate_scroll_container(driver)
            if container is None:
                logger.warning("Could not locate conversation sidebar container – falling back to page scroll")
                container = driver

            no_new_conv_count = 0

            for scroll_count in range(self.max_scroll_attempts):
                prev_len = len(conversations)

                # Extract visible convos
                conversations = self._extract_visible_conversations(driver, conversations)

                # Early-exit if we have enough
                if max_conversations and len(conversations) >= max_conversations:
                    break

                if len(conversations) == prev_len:
                    no_new_conv_count += 1
                else:
                    no_new_conv_count = 0

                # Click "Show more" buttons if present
                self._click_show_more(driver)

                # Perform scroll
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", container)
                time.sleep(self.scroll_pause_time)

                if no_new_conv_count >= self.burst_scroll_threshold:
                    logger.info("No new conversations after %s iterations – stopping", no_new_conv_count)
                    break

            # Trim to max_conversations if requested
            if max_conversations is not None:
                conversations = conversations[:max_conversations]

            logger.info("✅ Extracted %s conversations", len(conversations))
            return conversations
            
        except Exception as e:
            logger.error(f"❌ Failed to extract conversation list: {e}")
            return []
    
    def _extract_visible_conversations(self, driver, existing_conversations: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Extract currently visible conversations."""
        try:
            # Find all conversation links
            conversation_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/c/']")
            
            # Process each link
            for link in conversation_links:
                try:
                    href = link.get_attribute('href')
                    if not href or '/c/' not in href:
                        continue
                    
                    # Extract conversation ID from URL
                    conversation_id = href.split('/c/')[-1].split('?')[0]
                    
                    # Skip if already processed
                    if any(conv['id'] == conversation_id for conv in existing_conversations):
                        continue
                    
                    # Get conversation title
                    title = link.text.strip()
                    if not title:
                        title = f"Conversation {conversation_id[:8]}"
                    
                    existing_conversations.append({
                        'id': conversation_id,
                        'title': title,
                        'url': href
                    })
                    
                except StaleElementReferenceException:
                    logger.warning("Stale element reference, skipping")
                    continue
                except Exception as e:
                    logger.warning(f"Error extracting conversation: {e}")
                    continue
            
            return existing_conversations
            
        except Exception as e:
            logger.error(f"Error extracting visible conversations: {e}")
            return existing_conversations
    
    def _burst_scroll(self, driver) -> bool:
        """
        Perform burst scrolling to try to load more content.
        
        Args:
            driver: Selenium webdriver instance
            
        Returns:
            True if new content might be available, False if definitely at end
        """
        try:
            initial_height = driver.execute_script("return document.documentElement.scrollHeight")
            
            # Perform 3-5 quick scrolls with random distances
            for _ in range(random.randint(3, 5)):
                scroll_amount = random.randint(500, 1500)
                driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                time.sleep(0.3)  # Quick pause between bursts
            
            # Scroll back up a bit to trigger any lazy loading
            driver.execute_script("window.scrollBy(0, -500);")
            time.sleep(0.5)
            
            # Check if height changed
            new_height = driver.execute_script("return document.documentElement.scrollHeight")
            return new_height > initial_height
            
        except Exception as e:
            logger.error(f"Error during burst scroll: {e}")
            return False

    # NEW HELPERS ---------------------------------------------------------

    def _locate_scroll_container(self, driver):
        """Find the sidebar element that actually scrolls."""
        selectors = [
            "nav[data-testid='left-sidebar']",
            "nav[aria-label='Chat history']",
            "div[aria-label='Chat history']",
            "nav[role='navigation']",
            "aside div[role='navigation']",
            "aside",
        ]
        for sel in selectors:
            try:
                elem = driver.find_element(By.CSS_SELECTOR, sel)
                if elem:
                    return elem
            except Exception:
                continue
        return None

    def _click_show_more(self, driver):
        """Click any 'Show more' or 'Load more' button present in the sidebar."""
        try:
            buttons = driver.find_elements(By.XPATH, "//button[normalize-space(text())='Show more' or normalize-space(text())='Load more']")
            for btn in buttons:
                try:
                    btn.click()
                    time.sleep(0.5)
                except Exception:
                    continue
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Filter helpers
    # ------------------------------------------------------------------

    def _ensure_all_time_filter(self, driver):
        """If a date-range filter is visible (e.g. 'Last 30 days'), switch to 'All time'."""
        try:
            # Locate the filter button
            filter_btn = None
            for text in ["Last", "Past", "Previous"]:
                try:
                    filter_btn = driver.find_element(By.XPATH, f"//button[contains(text(), '{text}')]")
                    if filter_btn.is_displayed():
                        break
                except Exception:
                    continue

            if not filter_btn:
                return  # no filter detected → assume already all time

            filter_text = filter_btn.text.strip()
            if "All time" in filter_text:
                return  # already correct

            driver.execute_script("arguments[0].click();", filter_btn)
            time.sleep(0.5)

            # Click the menu item – varies by UI; search for option element or button/div
            try:
                option = driver.find_element(By.XPATH, "//div[contains(text(), 'All time')]")
            except Exception:
                try:
                    option = driver.find_element(By.XPATH, "//button[contains(text(), 'All time')]")
                except Exception:
                    option = None

            if option:
                driver.execute_script("arguments[0].click();", option)
                time.sleep(0.5)
                logger.info("Switched history filter to 'All time'")
        except Exception:
            # Silent failure – non-critical
            pass