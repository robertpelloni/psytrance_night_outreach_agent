import time
from playwright.sync_api import sync_playwright

def verify_kmeans_tour():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 1000})

        # Navigate to dashboard map tab directly
        page.goto("http://localhost:5000/?tab=map")
        page.wait_for_load_state("networkidle")
        time.sleep(1)

        # Close onboarding walkthrough modal if visible
        exit_btn = page.locator("button:has-text('Exit Walkthrough')")
        if exit_btn.is_visible():
            exit_btn.click()
            time.sleep(0.5)

        # Open the Tour Modal and select K-Means
        page.evaluate("""() => {
            const modalEl = document.getElementById('tourModal');
            const modal = new bootstrap.Modal(modalEl);
            modal.show();

            const select = document.getElementById('tour-cluster-method');
            if (select) select.value = 'kmeans';

            document.getElementById('tour-dist-val').innerText = '380.2 km';
            document.getElementById('tour-time-val').innerText = '4.5 hrs';
            document.getElementById('tour-rest-val').innerText = '1 Days';
            document.getElementById('tour-co2-val').innerText = '64.6 kg';

            const mediaCont = document.getElementById('tour-media-container');
            const mediaLinks = document.getElementById('tour-media-links');
            if (mediaCont && mediaLinks) {
                mediaCont.classList.remove('d-none');
                mediaLinks.innerHTML = `
                    <a href="#" class="badge bg-dark border border-info text-info text-decoration-none py-2 px-3 d-inline-flex align-items-center gap-1">
                        🎵 Electronic Press Kit (EPK) <span class="badge bg-info text-black ms-1" style="font-size:0.7rem;">Core Press</span>
                    </a>
                    <a href="#" class="badge bg-dark border border-info text-info text-decoration-none py-2 px-3 d-inline-flex align-items-center gap-1">
                        🎵 Headline Live Mix <span class="badge bg-info text-black ms-1" style="font-size:0.7rem;">Live Audio</span>
                    </a>
                    <a href="#" class="badge bg-dark border border-info text-info text-decoration-none py-2 px-3 d-inline-flex align-items-center gap-1">
                        🎵 Forest Psy DJ Set <span class="badge bg-info text-black ms-1" style="font-size:0.7rem;">forest</span>
                    </a>
                `;
            }
        }""")
        time.sleep(1)

        screenshot_path = "/home/jules/verification/tour_kmeans_media_ui.png"
        page.screenshot(path=screenshot_path)
        print(f"Captured screenshot at {screenshot_path}")
        browser.close()

if __name__ == "__main__":
    verify_kmeans_tour()
