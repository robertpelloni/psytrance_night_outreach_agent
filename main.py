import os
import importlib.util
import sys
from dotenv import load_dotenv
from src.db_manager import DatabaseManager
from src.scrapers.base_scraper import ContactExtractor
from src.ai_engine import AIEngine
from src.config_manager import ConfigManager
from src.outreach_engine import OutreachEngine
from src.follow_up_engine import FollowUpEngine
from src.geocoding import GeocodingUtility

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
    config = ConfigManager()
    outreach = OutreachEngine()
    follow_up = FollowUpEngine()
    geocoder = GeocodingUtility()
    scrapers = load_scrapers()

    print(f"Loaded {len(scrapers)} scrapers: {[s.__class__.__name__ for s in scrapers]}")

    cities = config.get("cities")
    vibe_threshold = config.get("vibe_threshold")

    for city in cities:
        if db.is_city_processed(city):
            print(f"Skipping {city} - Already processed in this cycle.")
            continue

        print(f"\n--- Processing {city} ---")

        raw_venues = []
        for scraper in scrapers:
            try:
                raw_venues.extend(scraper.search_venues(city))
            except Exception as e:
                print(f"Error running scraper {scraper.__class__.__name__}: {e}")

        for v_data in raw_venues:
            # OPTIMIZATION: Check if venue and lead already exist before burning AI tokens
            existing_id = db.venue_exists_by_name(v_data['name'], v_data['city'])
            if existing_id:
                v_id = existing_id
                # Check if we already have a lead for this venue to avoid re-qualifying
                existing_lead = db.get_lead_by_venue_id(v_id)
                if existing_lead:
                    print(f"Skipping {v_data['name']} - Lead already exists.")
                    continue
            else:
                v_id = v_data['id']
                db.add_venue(v_data)

            enriched_text = v_data.get('raw_about_text', "")
            if v_data.get('website'):
                contact_info = ContactExtractor.scrape_website(v_data['website'])
                if contact_info:
                    if contact_info.get('about_text'):
                        enriched_text = contact_info['about_text']

                    insta = ", ".join(contact_info.get('instagrams', []))
                    db.add_contact({
                        'venue_id': v_id,
                        'email': ", ".join(contact_info.get('emails', [])),
                        'instagram_handle': insta
                    })

                    # NEW: Get contextual social context to enrich AI prompt
                    social_context = ContactExtractor.get_social_context(insta)
                    if social_context:
                        enriched_text += f"\nSocial Media Context: {social_context}"

                    # NEW: Get contextual social context to enrich AI prompt
                    social_context = ContactExtractor.get_social_context(insta)
                    if social_context:
                        enriched_text += f"\nSocial Media Context: {social_context}"

            # Only perform AI vibe check if it's a new lead
            vibe_result = ai.vibe_check(v_data['name'], enriched_text)

            # NEW: Extract technical and atmospheric traits for personalization
            traits = ai.extract_venue_traits(enriched_text)
            db.update_venue_traits(v_id, traits)

            # NEW: Geocode venue for mapping
            lat, lon = geocoder.geocode_venue(v_data['name'], v_data['city'])
            if lat and lon:
                db.update_venue_location(v_id, lat, lon)

            pitch = ""
            if vibe_result['vibe_score'] >= vibe_threshold:
                pitch = ai.generate_pitch(
                    v_data['name'],
                    vibe_result['justification'],
                    epk_link=config.get("epk_link"),
                    mix_link=config.get("mix_link"),
                    traits=traits,
                    media_library=config.get("media_library")
                )
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

        db.mark_city_processed(city)

    print("\nScraping and qualification complete. Running outreach and follow-up cycles...")
    outreach.run_outreach_cycle()
    follow_up.run_follow_up_cycle()

    print("\nPipeline run complete.")
    db.log_system_event("PIPELINE", "SUCCESS", "Full outreach cycle completed")

if __name__ == "__main__":
    main()
