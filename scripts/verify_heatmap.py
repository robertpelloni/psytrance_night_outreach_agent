import time
from playwright.sync_api import sync_playwright

def verify_activity_heatmap():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 1000})

        # Navigate to dashboard analytics tab
        page.goto("http://localhost:5000/?tab=analytics")
        page.wait_for_load_state("networkidle")
        time.sleep(1)

        # Scroll to the Outreach Timing Matrix card
        heatmap_card = page.locator("text=Outreach Timing Matrix & Response Velocity")
        heatmap_card.scroll_into_view_if_needed()
        time.sleep(1)

        # Capture screenshot
        screenshot_path = "/home/jules/verification/activity_heatmap_matrix.png"
        page.screenshot(path=screenshot_path)
        print(f"Captured screenshot at {screenshot_path}")
        browser.close()

if __name__ == "__main__":
    verify_activity_heatmap()
