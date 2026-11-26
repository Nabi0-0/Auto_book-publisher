import unittest
from unittest.mock import MagicMock, patch

from Scraping import scraper


class TestScrapeChapter(unittest.TestCase):

    def test_invalid_url_raises_before_playwright_starts(self):
        with patch.object(scraper, "sync_playwright") as mock_playwright:
            with self.assertRaises(ValueError):
                scraper.scrape_chapter(
                    "not-a-url",
                    "screenshot.png",
                    "chapter.txt",
                )

            mock_playwright.assert_not_called()

    def test_browser_closes_when_navigation_fails(self):
        playwright = MagicMock()
        browser = MagicMock()
        page = MagicMock()

        playwright.chromium.launch.return_value = browser
        browser.new_page.return_value = page
        page.goto.side_effect = RuntimeError("Navigation failed")

        with patch.object(scraper, "sync_playwright") as sync_playwright:
            sync_playwright.return_value.__enter__.return_value = playwright

            with self.assertRaisesRegex(RuntimeError, "Navigation failed"):
                scraper.scrape_chapter(
                    "https://example.com/chapter",
                    "screenshot.png",
                    "chapter.txt",
                )

        browser.close.assert_called_once()
        page.goto.assert_called_once_with(
            "https://example.com/chapter",
            wait_until="domcontentloaded",
            timeout=30000,
        )

    def test_empty_chapter_text_raises_and_closes_browser(self):
        playwright = MagicMock()
        browser = MagicMock()
        page = MagicMock()
        content = MagicMock()

        playwright.chromium.launch.return_value = browser
        browser.new_page.return_value = page
        page.query_selector.return_value = content
        content.inner_text.return_value = "   \n "

        with patch.object(scraper, "sync_playwright") as sync_playwright:
            sync_playwright.return_value.__enter__.return_value = playwright

            with self.assertRaisesRegex(ValueError, "No chapter text found"):
                scraper.scrape_chapter(
                    "https://example.com/chapter",
                    "screenshot.png",
                    "chapter.txt",
                )

        browser.close.assert_called_once()
        
    def test_successful_scrape_saves_chapter_text(self):
        playwright = MagicMock()
        browser = MagicMock()
        page = MagicMock()
        content = MagicMock()

        playwright.chromium.launch.return_value = browser
        browser.new_page.return_value = page
        page.query_selector.return_value = content
        content.inner_text.return_value = "This is a chapter."

        with patch.object(scraper, "sync_playwright") as sync_playwright:
            sync_playwright.return_value.__enter__.return_value = playwright
            with patch("builtins.open", unittest.mock.mock_open()) as mock_file:
                scraper.scrape_chapter(
                    "https://example.com/chapter",
                    "screenshot.png",
                    "chapter.txt",
                )

        page.screenshot.assert_called_once_with(
            path="screenshot.png",
            full_page=True,
        )
        mock_file.assert_called_once_with("chapter.txt", "w", encoding="utf-8")
        mock_file().write.assert_called_once_with("This is a chapter.")
        browser.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()