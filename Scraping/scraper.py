from urllib.parse import urlsplit
from pathlib import Path
from playwright.sync_api import sync_playwright


def scrape_chapter(url, screenshot_path, text_path):
    parsed_url = urlsplit(url)

    if parsed_url.scheme not in {"http", "https"} or not parsed_url.hostname:
        raise ValueError("URL must be a valid HTTP or HTTPS URL.")

    Path(screenshot_path).parent.mkdir(parents=True, exist_ok=True)
    Path(text_path).parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        try:
            page = browser.new_page()

            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=30000,
            )
            print(f"Scraping chapter from: {url}")

            page.screenshot(path=screenshot_path, full_page=True)
            print(f"Screenshot saved at: {screenshot_path}")

            content = page.query_selector("#mw-content-text")
            chapter_text = content.inner_text() if content else ""
            
            if not chapter_text.strip():
                raise ValueError("No chapter text found on the page.")

            with open(text_path, "w", encoding="utf-8") as file:
                file.write(chapter_text)

            print(f"Chapter text saved at: {text_path}")

        finally:
            browser.close()


if __name__ == "__main__":
    chapter_url = input("Enter the chapter URL: ").strip()
    screenshot_file = "Scraping/screenshot/chapter1_screenshot.png"
    text_file = "outputs/raw_chapter1.txt"

    scrape_chapter(chapter_url, screenshot_file, text_file)