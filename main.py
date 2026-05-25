import os
import importlib.util
import sys
from dotenv import load_dotenv
from src.db_manager import DatabaseManager
from src.scrapers.base_scraper import ContactExtractor
from src.ai_engine import AIEngine

def load_scrapers():
    scrapers = []
    scrapers_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src/scrapers'))

    # Add scrapers directory to path for imports
    if scrapers_dir not in sys.path:
        sys.path.append(scrapers_dir)

    for filename in os.listdir(scrapers_dir):
        if filename.endswith('.py') and filename not in ['__init__.py', 'base_scraper.py']:
            module_name = filename[:-3]
            try:
                # Use standard import for modules in the path
                module = importlib.import_module(f"src.scrapers.{module_name}")

                # Look for classes that seem like scrapers (ends with Scraper)
                for attr in dir(module):
                    cls = getattr(module, attr)
                    if isinstance(cls, type) and attr.endswith('Scraper') and attr not in ['BaseScraper', 'GoogleMapsScraper', 'ResidentAdvisorScraper']:
                        scrapers.append(cls())
            except Exception as e:
                print(f"Error loading module {module_name}: {e}")

    return scrapers

def main():
    load_dotenv()
    db = DatabaseManager()
    ai = AIEngine()
    scrapers = load_scrapers()

    print(f"Loaded {len(scrapers)} scrapers: {[s.__class__.__name__ for s in scrapers]}")

    cities = ["Detroit"] # Limit for test

    for city in cities:
        print(f"\n--- Processing {city} ---")

        raw_venues = []
        for scraper in scrapers:
            try:
                raw_venues.extend(scraper.search_venues(city))
            except Exception as e:
                print(f"Error running scraper {scraper.__class__.__name__}: {e}")

        for v_data in raw_venues:
            existing_id = db.venue_exists_by_name(v_data['name'], v_data['city'])
            if existing_id:
                v_id = existing_id
            else:
                v_id = v_data['id']
                db.add_venue(v_data)

            enriched_text = v_data.get('raw_about_text', "")
            if v_data.get('website'):
                contact_info = ContactExtractor.scrape_website(v_data['website'])
                if contact_info:
                    if contact_info.get('about_text'):
                        enriched_text = contact_info['about_text']

                    db.add_contact({
                        'venue_id': v_id,
                        'email': ", ".join(contact_info.get('emails', [])),
                        'instagram_handle': ", ".join(contact_info.get('instagrams', []))
                    })

            vibe_result = ai.vibe_check(v_data['name'], enriched_text)

            pitch = ""
            if vibe_result['vibe_score'] >= 7:
                pitch = ai.generate_pitch(v_data['name'], vibe_result['justification'])
                status = 'PENDING_REVIEW'
            else:
                status = 'PENDING_QUALIFICATION'

            lead_data = {
                'venue_id': v_id,
                'vibe_score': vibe_result['vibe_score'],
                'qualification_justification': vibe_result['justification'],
                'generated_pitch': pitch,
                'pipeline_status': status
            }
            db.add_lead(lead_data)

    print("\nPipeline run complete.")

if __name__ == "__main__":
    main()
