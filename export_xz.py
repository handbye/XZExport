import os
import time
import argparse
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import sys

class XZExporter:
    def __init__(self, log_callback=None):
        self.log_callback = log_callback

    def log(self, message):
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)

    def init_driver(self):
        """Initialize Chrome WebDriver with headless options."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920,1080")
        # Set a common user agent to avoid detection
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Handle PyInstaller path for chromedriver if needed, but webdriver_manager usually handles it.
        # However, we need to make sure we don't rely on local paths that might not exist in the app bundle.
        
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            return driver
        except Exception as e:
            self.log(f"Error initializing driver: {e}")
            raise

    def download_image(self, img_url, output_dir, headers=None, cookies=None):
        """Download image and return local filename."""
        try:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            # Parse filename from URL
            parsed_url = urlparse(img_url)
            filename = os.path.basename(parsed_url.path)
            if not filename or '.' not in filename:
                filename = f"image_{int(time.time() * 1000)}.png"
                
            # Handle query parameters in filename if any
            if '?' in filename:
                filename = filename.split('?')[0]
                
            local_path = os.path.join(output_dir, filename)
            
            # If file already exists, maybe append timestamp to avoid overwrite
            if os.path.exists(local_path):
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{int(time.time())}{ext}"
                local_path = os.path.join(output_dir, filename)

            # Use session with headers and cookies
            session = requests.Session()
            if headers:
                session.headers.update(headers)
            if cookies:
                session.cookies.update(cookies)

            response = session.get(img_url, stream=True, timeout=10)
            if response.status_code == 200:
                with open(local_path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                return local_path
            else:
                self.log(f"Failed to download image: {img_url} (Status: {response.status_code})")
                return None
        except Exception as e:
            self.log(f"Error downloading image {img_url}: {e}")
            return None

    def export(self, url, output_dir):
        self.log(f"Initializing WebDriver...")
        driver = None
        try:
            driver = self.init_driver()
            
            self.log(f"Navigating to {url}...")
            driver.get(url)
            
            # Wait for the author info to appear, which means the WAF is passed and content loaded
            self.log("Waiting for page content to load...")
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "detail_info"))
            )
            
            # Give it a little extra time for dynamic content/images
            time.sleep(2)
            
            # Get cookies and headers from driver to use in requests
            selenium_cookies = driver.get_cookies()
            cookies = {c['name']: c['value'] for c in selenium_cookies}
            headers = {
                "User-Agent": driver.execute_script("return navigator.userAgent;"),
                "Referer": url
            }
            
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract Title
            # Try multiple selectors for title
            title = "Untitled Article"
            
            # Extract Title
            # Selector 1: .detail_title (found via inspection)
            title_elem = soup.select_one('.detail_title')
            
            # Selector 2: .topic-title
            if not title_elem:
                title_elem = soup.select_one('.topic-title')
                
            # Selector 3: Preceding sibling of detail_info
            if not title_elem:
                detail_info = soup.find('div', class_='detail_info')
                if detail_info:
                    for sibling in detail_info.previous_siblings:
                        if sibling.name in ['h1', 'h2', 'div', 'span'] and len(sibling.get_text(strip=True)) > 0:
                            title_elem = sibling
                            break
                            
            if title_elem:
                title = title_elem.get_text(strip=True)
                
            self.log(f"Found Title: {title}")
            
            # Sanitize title for filename
            safe_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c in (' ', '-', '_')]).strip()
            if not safe_title:
                safe_title = "article"
            
            # Create article directory
            article_dir = os.path.join(output_dir, safe_title)
            if not os.path.exists(article_dir):
                os.makedirs(article_dir)
            self.log(f"Created article directory: {article_dir}")
                
            # Extract Content
            # Improved selector based on inspection
            content_div = soup.select_one('#markdown-body')
            
            if not content_div:
                # Fallback to previous method
                detail_info = soup.find('div', class_='detail_info')
                if detail_info:
                    content_container = detail_info.parent
                    content_soup = BeautifulSoup("<div></div>", 'html.parser')
                    content_div = content_soup.div
                    for sibling in detail_info.find_next_siblings():
                        if sibling.name == 'div' and ('comment' in sibling.get('class', []) or 'topic-operate' in sibling.get('class', [])):
                            break
                        content_div.append(sibling)
                else:
                    self.log("Error: Could not find article content.")
                    return

            # Pre-process content to handle custom tags (ne-h1, ne-h2, etc.)
            # Convert ne-tags to standard HTML tags for markdownify
            for tag in content_div.find_all(True):
                if tag.name.startswith('ne-'):
                    new_name = tag.name.replace('ne-', '')
                    # Map specific ne-tags if needed, but usually ne-h2 -> h2 works
                    if new_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'li', 'blockquote', 'code', 'pre']:
                        tag.name = new_name
            
            # Handle code blocks - convert ne-card codeblock to standard <pre><code>
            codeblock_cards = content_div.find_all('ne-card', attrs={'data-card-name': 'codeblock'})
            for card in codeblock_cards:
                try:
                    # Extract language type
                    lang_elem = card.select_one('.CodeMirror-code-name span')
                    language = lang_elem.get_text(strip=True) if lang_elem else ''
                    
                    # Extract code content from cm-line divs
                    code_lines = card.select('.cm-line')
                    code_content = []
                    for line in code_lines:
                        line_text = line.get_text(strip=True)
                        if line_text:
                            code_content.append(line_text)
                    
                    if code_content:
                        # Create standard <pre><code> structure
                        pre_tag = soup.new_tag('pre')
                        code_tag = soup.new_tag('code')
                        if language and language != 'Plain Text':
                            code_tag['class'] = [f'language-{language}']
                        code_tag.string = '\n'.join(code_content)
                        pre_tag.append(code_tag)
                        
                        # Replace the ne-card with the standard structure
                        card.replace_with(pre_tag)
                except Exception as e:
                    self.log(f"Error processing codeblock: {e}")
            
            # Handle Images
            images_dir = os.path.join(article_dir, "images")
            images = content_div.find_all('img')
            
            if images:
                self.log(f"Found {len(images)} images. Downloading...")
                for img in images:
                    src = img.get('src')
                    if src:
                        # Handle relative URLs
                        full_url = urljoin(url, src)
                        local_path = self.download_image(full_url, images_dir, headers=headers, cookies=cookies)
                        if local_path:
                            # Update src to relative path for markdown
                            rel_path = os.path.relpath(local_path, article_dir)
                            img['src'] = rel_path
                            
            # Convert to Markdown
            self.log("Converting to Markdown...")
            markdown_content = md(str(content_div), heading_style="ATX")
            
            # Add Title
            final_markdown = f"# {title}\n\nOriginal URL: {url}\n\n{markdown_content}"
            
            output_file = os.path.join(article_dir, f"{safe_title}.md")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(final_markdown)
                
            self.log(f"Successfully exported to {output_file}")
            
        except Exception as e:
            self.log(f"An error occurred: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if driver:
                driver.quit()

def main():
    parser = argparse.ArgumentParser(description="Export xz.aliyun.com article to Markdown")
    parser.add_argument("url", help="URL of the article")
    parser.add_argument("-o", "--output", help="Output directory", default=".")
    args = parser.parse_args()

    exporter = XZExporter()
    exporter.export(args.url, args.output)

if __name__ == "__main__":
    main()
