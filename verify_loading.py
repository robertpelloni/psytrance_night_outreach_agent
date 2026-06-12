import sys
import os
sys.path.append(os.getcwd())
from main import load_scrapers

query_scrapers, city_scrapers = load_scrapers()
print(f"Query Scrapers: {[s.__class__.__name__ for s in query_scrapers]}")
print(f"City Scrapers: {[s.__class__.__name__ for s in city_scrapers]}")
