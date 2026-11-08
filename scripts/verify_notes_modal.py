import time
from playwright.sync_api import sync_playwright

def verify_notes_modal():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 1000})

        # Navigate to dashboard pipeline pending leads
        page.goto("http://localhost:5000/?tab=pipeline&view=pending")
        page.wait_for_load_state("networkidle")
        time.sleep(1)

        # Click the 'Notes' button on the first lead card
        notes_btn = page.locator("button:has-text('📝 Notes')").first
        if notes_btn.is_visible():
            notes_btn.click()
            time.sleep(1)

            # Type a note in the modal
            note_input = page.locator("#modal-note-content")
            if note_input.is_visible():
                note_input.fill("Acoustic setup: 4-point Void Acoustics. Door policy 21+, curfew 4am.")
                # Click Add Note
                page.locator("button:has-text('Add Note')").click()
                time.sleep(1)

        screenshot_path = "/home/jules/verification/venue_notes_modal_ui.png"
        page.screenshot(path=screenshot_path)
        print(f"Captured screenshot at {screenshot_path}")
        browser.close()

if __name__ == "__main__":
    verify_notes_modal()
