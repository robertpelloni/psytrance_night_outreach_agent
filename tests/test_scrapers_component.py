import unittest
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import requests
from src.scrapers.base_scraper import ContactExtractor

class MockWebsiteHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html = """
        <html>
            <body>
                <h1>Welcome to The Bunker</h1>
                <p>Contact us at booking@bunker-club.com or info@bunker-club.com</p>
                <p>Follow us on <a href="https://instagram.com/bunker_official">Instagram</a></p>
                <div class="about">The Bunker is an underground techno space in Detroit.</div>
            </body>
        </html>
        """
        self.wfile.write(html.encode())

class TestScrapersComponent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start a local HTTP server
        cls.server = HTTPServer(('localhost', 8081), MockWebsiteHandler)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever)
        cls.server_thread.daemon = True
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_contact_extractor_real_html(self):
        # This test ensures that ContactExtractor works with a real (local) HTTP response
        # and that all regex and imports are functional.
        url = "http://localhost:8081"
        data = ContactExtractor.scrape_website(url)

        self.assertIn("booking@bunker-club.com", data['emails'])
        self.assertIn("info@bunker-club.com", data['emails'])
        self.assertIn("bunker_official", data['instagrams'])
        self.assertIn("underground techno space", data['about_text'])

if __name__ == "__main__":
    unittest.main()
