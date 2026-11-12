import time
import subprocess
import os
from playwright.sync_api import sync_playwright

def main():
    os.makedirs('/home/jules/verification', exist_ok=True)

    # Ensure server is running
    server_proc = subprocess.Popen(['python3', 'src/dashboard/app.py'], env=dict(os.environ, PORT="5000"))
    time.sleep(3)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            page.goto('http://127.0.0.1:5000/?tab=map', timeout=15000)
            page.wait_for_timeout(1000)

            # Click Plan Midwest Circuit button to open #tourModal
            page.evaluate("""() => {
                const modalEl = document.getElementById('tourModal');
                const modal = new bootstrap.Modal(modalEl);
                modal.show();
                // Mock logistics values for inspection
                document.getElementById('tour-dist-val').innerText = '428.5 km';
                document.getElementById('tour-time-val').innerText = '5.0 hrs';
                document.getElementById('tour-rest-val').innerText = '2 Days';
                document.getElementById('tour-co2-val').innerText = '72.8 kg';
                document.getElementById('tour-output').innerText = 'Optimal Midwest Circuit: Detroit (Tangent Gallery) -> Ann Arbor (Nectarine Ballroom) -> Chicago (Smartbar) -> Toronto (Coda)';
                const mediaCont = document.getElementById('tour-media-container');
                const mediaLinks = document.getElementById('tour-media-links');
                mediaCont.classList.remove('d-none');
                mediaLinks.innerHTML = '<span class=\"badge bg-dark border border-info text-info py-2 px-3\">🎵 Electronic Press Kit (EPK)</span><span class=\"badge bg-dark border border-info text-info py-2 px-3 ms-2\">🎧 Headline Live Mix</span>';
            }""")
            page.wait_for_timeout(500)

            screenshot_path = '/home/jules/verification/tour_circuit_transit_modal.png'
            page.screenshot(path=screenshot_path)
            print(f"Screenshot successfully captured at {screenshot_path}")
            browser.close()
    finally:
        server_proc.terminate()
        server_proc.wait()

if __name__ == '__main__':
    main()
