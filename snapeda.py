from rich import console, print
from rich.console import Console
from rich.progress import Progress, TaskID, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn, MofNCompleteColumn
import requests
import pandas as pd
import json
import random
import os
import sys
from playwright.sync_api import sync_playwright, Page, TimeoutError


class PlaywrightManager:
    def __init__(self, headless: bool = False, slow_mo: int | None = None):
        self.headless = headless
        self.slow_mo = slow_mo or 1000
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def start(self):
        if self.playwright is None:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                slow_mo=self.slow_mo,
                # proxy=self.proxy_server
            )
        return self

    def ensure_started(self):
        """Ensure Playwright and browser are started before using contexts/pages."""
        if self.playwright is None or self.browser is None:
            self.start()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.stop()

    def new_context(self, storage_state: str | None = None):
        # Close existing page/context safely
        try:
            if self.page:
                self.page.close()
        except Exception:
            pass
        finally:
            self.page = None
        try:
            if self.context:
                self.context.close()
        except Exception:
            pass
        finally:
            self.context = None
        # Create new context/page
        self.ensure_started()
        if storage_state:
            self.context = self.browser.new_context(storage_state=storage_state, accept_downloads=True)
            self.context.set_default_timeout(90000)
        else:
            self.context = self.browser.new_context(accept_downloads=True)
            self.context.set_default_timeout(90000)
        self.page = self.context.new_page()
        return self.page

    def close_context(self):
        try:
            if self.page:
                self.page.close()
        except Exception:
            pass
        finally:
            self.page = None
        try:
            if self.context:
                self.context.close()
        except Exception:
            pass
        finally:
            self.context = None

    def stop(self):
        # Close context
        self.close_context()
        # Close browser and stop playwright
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


class SnapEDA:
    def __init__(self):
        self.console = Console()
        self.progress = None
        self.task_id = None
        
        
        self.headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'en-BD,en-US;q=0.9,en;q=0.8',
            'priority': 'u=1, i',
            'referer': 'https://www.snapeda.com',
            'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        
        # Robust Playwright lifecycle manager
        self.pw = PlaywrightManager(headless=False, slow_mo=1000)
    
    
    def get_details(self, manufacturer, part_number):
        # Start browser and open part page
        self.pw.start()
        cookies = get_random_cookie()
        self.pw.new_context(storage_state=cookies)
        page = self.pw.page
        url = f'https://www.snapeda.com/parts/{part_number.replace('#','%23')}/{manufacturer}/view-part/'
        print(url)
        page.goto(url, timeout=90000)
        
        not_found = page.locator('div#view-part-content h1')
        if not_found.is_visible():
            not_found = not_found.inner_text()
            if 'Oh snap' in not_found:
                print(f'Part Not Found: {part_number}')
                self.pw.stop()
                return '', 'not found'
        
        package_name = page.locator('span.package_name')
        if package_name.is_visible():
            package_name = package_name.inner_text()
        else:
            package_name = ''
        datasheet_link = page.locator('a#library-add-remove+a.datasheet-link')
        if datasheet_link.is_visible():
            datasheet_link = datasheet_link.get_attribute('href')
        else:
            datasheet_link = ''
        
        pdf_link = ''
        page.goto(f'https://www.snapeda.com{datasheet_link}', timeout=90000)
        
        pdf_link = page.locator('object.me-iframe')
        if pdf_link.is_visible():
            pdf_link = pdf_link.get_attribute('data')
            download_file(pdf_link, part_number)
            
        
        self.pw.stop()
        return package_name, pdf_link
    

class Cookie_gen():
    def __init__(self, account:dict) -> None:
        self.email = account['email']
        self.password = account['password']
        self.user_id = account['username'].replace('.', '_')
        
        # Use PlaywrightManager for consistent lifecycle management
        self.pw = PlaywrightManager(headless=False, slow_mo=1000)
        self.context = None
        self.page = None
    
    def login(self):
        """Login to SnapEDA and get cookies"""
        self.pw.start()
        self.pw.new_context()
        self.context = self.pw.context
        self.context.set_default_timeout(90000)
        self.page = self.pw.page

        self.page.goto('https://www.snapeda.com/account/login/', timeout=90000)
        
        input('Press Enter to continue...')
        self.page.locator('input#id_username').fill(self.email)
        self.page.locator('input#id_password').fill(self.password)
        self.page.locator('input.btn-submit').click()
        
        # Wait for login to complete and get cookies
        self.page.wait_for_timeout(3000)
        input('Press Enter to continue...next')
        # Save storage state including cookies to JSON file
        os.makedirs('cookies', exist_ok=True)
        self.context.storage_state(path=f'cookies/{self.user_id}.json')
        return

    def close_browser(self):
        """Close browser and playwright resources"""
        self.pw.stop()

def download_file(file_url: str, parts_name:str='', save_dir: str = "downloads"):
    """
    Downloads a file from the given URL and saves it to the specified directory.
    Automatically extracts the filename from the URL.
    """

    # Create directory if it doesn't exist
    os.makedirs(save_dir, exist_ok=True)

    # Extract filename from URL
    filename = parts_name.replace('/', '_')
    if not filename:
        filename = "downloaded_file"

    save_path = os.path.join(save_dir, f"{filename}.pdf")

    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/134.0.0.0 Safari/537.36"
        ),
    }

    try:
        print(f"Downloading: {file_url}")
        response = requests.get(file_url, headers=headers, timeout=60, stream=True)

        if response.status_code == 200:
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"✅ File downloaded successfully: {save_path}")
        else:
            print(f"❌ Failed to download file (status {response.status_code})")
            with open('error.txt', 'a') as file:
                file.write(f"{file_url}\n")

    except requests.Timeout:
        print("⚠️ Request Timeout")
        with open('error.txt', 'a') as file:
            file.write(f"{file_url}\n")
    except Exception as e:
        print(f"❌ Error: {e}")
        with open('error.txt', 'a') as file:
            file.write(f"{file_url}\n")


def get_random_cookie():
    """Get a random cookie dictionary from JSON files in cookies directory"""
    try:
        # Get list of all JSON files in cookies directory
        cookie_files = [f for f in os.listdir('cookies') if f.endswith('.json')]
        
        if not cookie_files:
            raise FileNotFoundError("No cookie files found in cookies directory")
            
        # Select a random cookie file
        random_file = random.choice(cookie_files)
        print(random_file)
        # Read and parse the JSON file
        with open(os.path.join('cookies', random_file), 'r') as f:
            cookie_dict = json.load(f)
            
        return cookie_dict
        
    except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
        print(f"Error loading cookie file: {str(e)}")
        return {}

def get_accounts():
    df = pd.read_csv('snapeda_accounts.csv') 
    df = df.to_dict(orient='records')
    
    return df

def main():
    snapeda = SnapEDA()
    console = snapeda.console
    df = pd.read_csv('sample.csv')
    parts = df.to_dict(orient='records')
    new_parts = []
    for idx, part in enumerate(parts, 1):
        part_name = part['part_name']
        manufacturer = part['supplier']
        # if part_name != 'AT-1220-TT-R':
        #     continue
        package_name, pdf_link = snapeda.get_details(manufacturer, part_name)
        part['package_name'] = package_name
        part['pdf_link'] = pdf_link
        new_parts.append(part)
        print(part)
        print(f'Part {idx} of {len(parts)}')
        # Save after each iteration
        pd.DataFrame(new_parts).to_csv('new_parts.csv', index=False)
        # break

def create_cookie():
    accounts = get_accounts()
    for account in accounts:
        print(account['email'])
        cookie_gen = Cookie_gen(account)
        cookie_gen.login()
        cookie_gen.close_browser()


if __name__ == '__main__':
    main()
    # create_cookie()

