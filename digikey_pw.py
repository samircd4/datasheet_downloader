from playwright.sync_api import sync_playwright
from selectolax.parser import HTMLParser
from rich import print
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
import pandas as pd
import time
import json
import os
import random




from playwright.sync_api import sync_playwright
import os


class PlaywrightManager:
    def __init__(
        self,
        user_data_dir: str | None = None,
        headless: bool = False,
        slow_mo: int | None = None,
    ):
        """
        Manage Playwright browser sessions with optional persistent storage.

        Args:
            user_data_dir: Directory for storing browser profile data (cookies, sessions, etc.).
            headless: Whether to run browser in headless mode.
            slow_mo: Delay between operations (ms), useful for debugging.
        """
        self.user_data_dir = user_data_dir
        self.headless = headless
        self.slow_mo = slow_mo or 1000
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def start(self):
        """Start Playwright and launch a persistent or temporary browser."""
        if self.playwright is None:
            self.playwright = sync_playwright().start()

        if self.user_data_dir:
            os.makedirs(self.user_data_dir, exist_ok=True)
            # Persistent browser — creates a permanent user profile
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                headless=self.headless,
                slow_mo=self.slow_mo,
                accept_downloads=True,
            )
            self.context.set_default_timeout(90000)
            self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
        else:
            # Non-persistent (temporary) browser
            self.browser = self.playwright.chromium.launch(
                headless=self.headless, slow_mo=self.slow_mo
            )
            self.context = self.browser.new_context(accept_downloads=True)
            self.context.set_default_timeout(90000)
            self.page = self.context.new_page()

        return self

    def ensure_started(self):
        """Ensure Playwright and browser are started before use."""
        if self.context is None:
            self.start()

    def new_page(self):
        """Open a new tab (page) in the current browser context."""
        self.ensure_started()
        self.page = self.context.new_page()
        return self.page

    def close_context(self):
        """Close current context and all associated pages."""
        try:
            if self.context:
                self.context.close()
        except Exception:
            pass
        finally:
            self.context = None
            self.page = None

    def stop(self):
        """Close everything cleanly."""
        try:
            if self.context:
                self.context.close()
        except Exception:
            pass
        finally:
            self.context = None

        try:
            if self.browser:
                self.browser.close()
        except Exception:
            pass
        finally:
            self.browser = None

        try:
            if self.playwright:
                self.playwright.stop()
        except Exception:
            pass
        finally:
            self.playwright = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.stop()


def get_html(url:str):
    pw = PlaywrightManager(headless=False, slow_mo=1000)
    pw.start()
    page = pw.new_context()
    page.goto(url)
    html = page.content()
    pw.stop()
    return html

def get_details(content:str):
    part = {}
    html = HTMLParser(content)
    
    detail_description = html.css_first('div[track-data="ref_page_event=Copy Expand Description"]').text(strip=True)
    part['detail_description'] = detail_description
    
    tbl_row = html.css('table#product-attributes tbody tr')
    for row in tbl_row:
        key = row.css_first('td').text(strip=True)
        if key == 'Supplier Device Package':
            part['supplier_device_package'] = row.css_first('td:nth-child(2)').text(strip=True)
            break
    
    # package_name = html.css_first('div.tss-css-tsu9t4-packageName').text(strip=True)
    print(part)
    return part


def main():
    df = pd.read_csv('all_parts.csv')
    urls = df.to_dict(orient='records')
    for parts in urls[600:]:
        manager = PlaywrightManager(headless=False)

        # Start with user_1
        manager.user_data_dir = "user_1"
        manager.start()
        manager.page.goto("https://www.digikey.co.uk/en/products/detail/diotec-semiconductor/1N4007/18833652")
        input("Press Enter to continue...")
        manager.stop()
        # url = parts['url']
        # print(url)
        # html = get_html(url)
        # details = get_details(html)
        # parts.update(details)
        # print(parts)
        break


if __name__ == '__main__':
    main()
    # snapeda_pw()