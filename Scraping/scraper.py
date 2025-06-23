from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# Setup browser options
options = Options()
options.add_argument("--headless")  # Run browser in background
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

url = "https://en.wikisource.org/wiki/The_Gates_of_Morning/Book_1/Chapter_1"
driver.get(url)
time.sleep(3)

screenshot_path = "outputs/chapter1_screenshot.png"
driver.save_screenshot(screenshot_path)
print(f"Screenshot saved at {screenshot_path}")

content_element = driver.find_element(By.ID, "mw-content-text")  # Wikisource uses this for article body
chapter_text = content_element.text

output_text_path = "outputs/raw_chapter1.txt"
with open(output_text_path, 'w', encoding='utf-8') as f:
    f.write(chapter_text)

print(f"Chapter text saved to {output_text_path}")

# Close the browser
driver.quit()
