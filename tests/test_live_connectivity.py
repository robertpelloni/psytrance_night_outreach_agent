import unittest
import os
import requests
import smtplib
from src.ai_engine import AIEngine
from src.mailer import Mailer
from src.scrapers.base_scraper import ProxyRotator
from dotenv import load_dotenv

class TestLiveConnectivity(unittest.TestCase):
    """
    Integration tests to validate connectivity to live external services.
    Requires real environment variables to be set.
    """
    def setUp(self):
        load_dotenv()
        self.ai = AIEngine()
        self.mailer = Mailer()

    def test_openai_connectivity(self):
        if not os.getenv("OPENAI_API_KEY"):
            self.skipTest("OPENAI_API_KEY not set")

        print("Testing OpenAI Connectivity...")
        result = self.ai.vibe_check("Test Venue", "A cozy underground electronic music club.")
        self.assertIn('vibe_score', result)
        self.assertIsInstance(result['vibe_score'], int)
        print(f"OpenAI OK. Score: {result['vibe_score']}")

    def test_proxy_connectivity(self):
        proxy_list = os.getenv("PROXY_LIST")
        if not proxy_list:
            self.skipTest("PROXY_LIST not set")

        print("Testing Proxy Connectivity...")
        proxy_config = ProxyRotator.get_proxy_config()
        self.assertIsNotNone(proxy_config)

        try:
            # Try to fetch a simple page via proxy
            resp = requests.get("https://httpbin.org/ip", proxies=proxy_config, timeout=15)
            self.assertEqual(resp.status_code, 200)
            print(f"Proxy OK. IP: {resp.json().get('origin')}")
        except Exception as e:
            self.fail(f"Proxy connectivity failed: {e}")

    def test_smtp_connectivity(self):
        if not os.getenv("SMTP_SERVER"):
            self.skipTest("SMTP_SERVER not set")

        print("Testing SMTP Connectivity...")
        try:
            with smtplib.SMTP(self.mailer.smtp_server, self.mailer.smtp_port) as server:
                server.starttls()
                server.login(self.mailer.smtp_user, self.mailer.smtp_password)
                self.assertTrue(True)
            print("SMTP OK.")
        except Exception as e:
            self.fail(f"SMTP connectivity failed: {e}")

if __name__ == "__main__":
    unittest.main()
