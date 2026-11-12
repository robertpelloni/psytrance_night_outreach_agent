import time
from playwright.sync_api import sync_playwright

def verify_export_controls():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 1000})

        # Navigate to dashboard analytics tab to inspect Export JSON button
        page.goto("http://localhost:5000/?tab=analytics")
        page.wait_for_load_state("networkidle")
        time.sleep(1)

        # Scroll to conversion funnel card with Export CSV and Export JSON buttons
        funnel_card = page.locator("text=Outreach Conversion Funnel")
        funnel_card.scroll_into_view_if_needed()
        time.sleep(1)

        screenshot_path = "/home/jules/verification/export_buttons_ui.png"
        page.screenshot(path=screenshot_path)
        print(f"Captured screenshot at {screenshot_path}")
        browser.close()

if __name__ == "__main__":
    verify_export_controls()
