import unittest
import os
import time
from src.scrapers.base_scraper import ProxyRotator

class TestProxyRotator(unittest.TestCase):
    def setUp(self):
        # Reset internal state for each test
        ProxyRotator._proxies = {}
        ProxyRotator._initialized = False
        self.old_proxy_list = os.environ.get("PROXY_LIST")
        os.environ["PROXY_LIST"] = "http://p1.test,http://p2.test"

    def tearDown(self):
        if self.old_proxy_list is not None:
            os.environ["PROXY_LIST"] = self.old_proxy_list
        else:
            del os.environ["PROXY_LIST"]

    def test_initialization(self):
        ProxyRotator._initialize()
        self.assertIn("http://p1.test", ProxyRotator._proxies)
        self.assertIn("http://p2.test", ProxyRotator._proxies)
        self.assertEqual(ProxyRotator._proxies["http://p1.test"]["fails"], 0)

    def test_selection_and_failure(self):
        url = ProxyRotator.get_proxy_url()
        self.assertIn(url, ["http://p1.test", "http://p2.test"])

        # Report failure and check blacklisting
        ProxyRotator.report_failure(url)
        self.assertEqual(ProxyRotator._proxies[url]["fails"], 1)

        # Next selection should pick the OTHER one (since this one is blacklisted for 10s)
        other_url = ProxyRotator.get_proxy_url()
        self.assertNotEqual(url, other_url)

    def test_exponential_backoff(self):
        url = "http://p1.test"
        ProxyRotator._initialize()

        # 1st fail: wait 10s
        ProxyRotator.report_failure(url)
        wait1 = ProxyRotator._proxies[url]["blacklist_until"] - time.time()
        self.assertTrue(5 < wait1 <= 10)

        # 2nd fail: wait 40s (2^2 * 10)
        ProxyRotator.report_failure(url)
        wait2 = ProxyRotator._proxies[url]["blacklist_until"] - time.time()
        self.assertTrue(35 < wait2 <= 40)

    def test_success_resets_fails(self):
        url = "http://p1.test"
        ProxyRotator._initialize()
        ProxyRotator.report_failure(url)
        ProxyRotator.report_failure(url)
        self.assertEqual(ProxyRotator._proxies[url]["fails"], 2)

        ProxyRotator.report_success(url)
        self.assertEqual(ProxyRotator._proxies[url]["fails"], 0)
        self.assertEqual(ProxyRotator._proxies[url]["blacklist_until"], 0)

    def test_all_blacklisted_fallback(self):
        ProxyRotator._initialize()
        ProxyRotator.report_failure("http://p1.test")
        ProxyRotator.report_failure("http://p2.test")

        # Selection should still return something even if both are blacklisted
        url = ProxyRotator.get_proxy_url()
        self.assertIsNotNone(url)

if __name__ == "__main__":
    unittest.main()
