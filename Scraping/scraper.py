from playwright.sync_api import sync_playwright

def scrape_chapter(url, screenshot_path, text_path):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        page.goto(url)
        page.wait_for_load_state("networkidle")
        print(f"Scraping chapter from: {url}")
        
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"Screenshot saved at: {screenshot_path}")
        content = page.query_selector("#mw-content-text")
        chapter_text = content.inner_text() if content else ""
        
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(chapter_text)
        print(f"Chapter text saved at: {text_path}")
        page.close()
        browser.close()

if __name__ == "__main__":
    chapter_url = input("Enter the chapter URL: ").strip()
    screenshot_file = "Scraping/screenshot/chapter1_screenshot.png"
    text_file = "outputs/raw_chapter1.txt"
    
    scrape_chapter(chapter_url, screenshot_file, text_file)
