"""UI Selector Mapper

A lightweight CLI to help quickly discover robust Selenium selectors when the
ChatGPT (or any) web UI changes.

Usage:
    python tools/ui_selector_mapper.py --keywords "Log in,Email,Password"
"""

from __future__ import annotations

import argparse
import logging
import sys
import textwrap
import time
from pathlib import Path
from typing import Iterable, List

# Re-use BrowserManager from scrapers package
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scrapers"))

from scrapers.browser_manager import BrowserManager  # type: ignore  # noqa: E402
from selenium.webdriver.common.by import By  # noqa: E402
from selenium.webdriver.support.ui import WebDriverWait  # noqa: E402
from selenium.common.exceptions import TimeoutException  # noqa: E402

logger = logging.getLogger("ui_selector_mapper")
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def _iter_unique(elements: Iterable):
    """Yield unique elements while preserving order."""
    seen = set()
    for elem in elements:
        if elem in seen:
            continue
        seen.add(elem)
        yield elem


def _build_css_path(element):
    """Build a short (best-effort) CSS path for the element."""
    parts: List[str] = []
    current = element
    while current is not None and current.tag_name.lower() != "html":
        tag = current.tag_name.lower()
        ident = current.get_attribute("id")
        if ident:
            parts.append(f"{tag}#{ident}")
            break
        classes = current.get_attribute("class") or ""
        first_class = classes.split()[0] if classes else ""
        if first_class:
            parts.append(f"{tag}.{first_class}")
        else:
            parts.append(tag)
        # Move to parent
        try:
            current = current.find_element(By.XPATH, "..")
        except Exception:
            break
    return " > ".join(reversed(parts))


def _describe(element):
    return {
        "id": element.get_attribute("id") or "",
        "name": element.get_attribute("name") or "",
        "data-testid": element.get_attribute("data-testid") or "",
        "placeholder": element.get_attribute("placeholder") or "",
        "aria-label": element.get_attribute("aria-label") or "",
        "type": element.get_attribute("type") or "",
        "text": element.text.strip(),
    }


def scan(url: str, keywords: List[str], timeout: int = 20, headless: bool = False):
    bm = BrowserManager(headless=headless)
    driver = bm.create_driver()
    if not driver:
        logger.error("Failed to obtain webdriver instance")
        return

    logger.info("Navigating to %s", url)
    driver.get(url)

    wait = WebDriverWait(driver, timeout)
    try:
        wait.until(
            lambda drv: any(
                drv.find_elements(By.XPATH,
                                   f"//*[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), '{kw.lower()}')]")
                for kw in keywords
            )
        )
    except TimeoutException:
        logger.warning("Keywords not found within %s seconds", timeout)

    matches: List[tuple[str, any]] = []
    for kw in keywords:
        xpath = f"//*[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), '{kw.lower()}')]"
        for elem in _iter_unique(driver.find_elements(By.XPATH, xpath)):
            matches.append((kw, elem))

    if not matches:
        logger.info("No matching elements found for keywords: %s", ", ".join(keywords))
        bm.close_driver()
        return

    print("\n=== Selector cheat-sheet ===")
    for kw, elem in matches:
        attrs = _describe(elem)
        css_path = _build_css_path(elem)
        quick_css = (
            f"#{attrs['id']}" if attrs["id"] else
            (f"[data-testid='{attrs['data-testid']}']" if attrs["data-testid"] else
             (f"[name='{attrs['name']}']" if attrs["name"] else
              (f"input[type='{attrs['type']}']" if attrs["type"] else css_path)))
        )
        print(textwrap.dedent(
            f"""
            ───────────────────────────────────────────────
            Keyword        : {kw}
            Tag            : {elem.tag_name.lower()}
            Text           : {attrs['text']}
            Quick CSS      : {quick_css}
            Text-XPath     : //*[normalize-space(text())='{kw}']
            Contains-XPath : //*[contains(text(), '{kw}')]
            Full CSS Path  : {css_path}
            Attrs          : id={attrs['id']} name={attrs['name']} data-testid={attrs['data-testid']} placeholder={attrs['placeholder']}
            """
        ))

    if not headless:
        logger.info("Leaving browser open for 30 s so you can inspect – close it sooner to finish.")
        time.sleep(30)

    bm.close_driver()


def main():
    parser = argparse.ArgumentParser(description="Discover reliable Selenium selectors for updated web UIs.")
    parser.add_argument("--url", default="https://chat.openai.com", help="Target page (default: ChatGPT home)")
    parser.add_argument("--keywords", default="Log in,Email,Password", help="Comma-separated keywords to search for")
    parser.add_argument("--timeout", type=int, default=20, help="Seconds to wait for first keyword")
    parser.add_argument("--headless", action="store_true", help="Run Chrome in headless mode")

    args = parser.parse_args()
    kw_list = [k.strip() for k in args.keywords.split(",") if k.strip()]
    scan(args.url, kw_list, args.timeout, args.headless)


if __name__ == "__main__":
    main() 