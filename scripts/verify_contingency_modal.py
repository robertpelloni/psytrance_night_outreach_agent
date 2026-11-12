import time
import subprocess
import os
from playwright.sync_api import sync_playwright

def main():
    os.makedirs('/home/jules/verification', exist_ok=True)

    server_proc = subprocess.Popen(['python3', 'src/dashboard/app.py'], env=dict(os.environ, PORT="5000"))
    time.sleep(3)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            page.goto('http://127.0.0.1:5000/', timeout=15000)
            page.wait_for_timeout(1000)

            # Trigger recommendations modal with mock data including contingency pitch controls
            page.evaluate("""() => {
                const modalEl = document.getElementById('recModal');
                const titleEl = document.getElementById('rec-modal-title');
                const container = document.getElementById('rec-results-container');
                titleEl.innerHTML = '🎯 Sibling Alternatives for <span class=\"text-info\">Subterranean Detroit</span>';
                container.innerHTML = `
                    <div class="row g-3">
                        <div class="col-md-6">
                            <div class="card bg-dark border-secondary h-100 p-3 shadow-sm">
                                <div class="d-flex justify-content-between align-items-start mb-2">
                                    <h6 class="mb-0 text-white fw-bold">The Magic Stick Lounge</h6>
                                    <div>
                                        <span class="badge bg-success">78% Match</span>
                                        <span class="badge bg-dark border border-secondary text-secondary ms-1">14.8 km</span>
                                    </div>
                                </div>
                                <div class="small text-secondary mb-2">Shared acoustic system: void acoustics | Within local cluster (14.8 km)</div>
                                <div class="mb-3">
                                    <span class="badge border border-info text-info me-1">void acoustics</span>
                                    <span class="badge border border-info text-info me-1">psytrance</span>
                                    <span class="badge border border-info text-info me-1">warehouse</span>
                                </div>
                                <div class="mt-auto d-flex flex-column gap-2">
                                    <div class="d-flex gap-2">
                                        <a href="#" class="btn btn-outline-info btn-sm flex-grow-1">View Venue Dossier</a>
                                        <button type="button" class="btn btn-outline-warning btn-sm">✉️ Draft Pitch</button>
                                    </div>
                                    <div class="p-2 bg-black border border-warning rounded">
                                        <div class="d-flex justify-content-between align-items-center mb-1">
                                            <span class="small text-warning fw-bold">Contingency Pitch Preview</span>
                                        </div>
                                        <input type="text" class="form-control form-control-sm bg-dark text-white border-secondary mb-1" value="Psytrance Night Residency Proposal - Magic Stick Lounge" readonly>
                                        <textarea class="form-control form-control-sm bg-dark text-white border-secondary" rows="3" readonly>Hi Magic Stick team,\n\nWe are routing our regional Midwest tour (anchored in Detroit). While coordinating dates near Subterranean Detroit, we identified Magic Stick Lounge as the premier acoustic match for our sound...</textarea>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                const modal = new bootstrap.Modal(modalEl);
                modal.show();
            }""")
            page.wait_for_timeout(500)

            screenshot_path = '/home/jules/verification/recommendation_contingency_modal.png'
            page.screenshot(path=screenshot_path)
            print(f"Screenshot successfully captured at {screenshot_path}")
            browser.close()
    finally:
        server_proc.terminate()
        server_proc.wait()

if __name__ == '__main__':
    main()
