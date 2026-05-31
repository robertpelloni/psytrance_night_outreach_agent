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
from src.outreach_predictor import OutreachPredictor

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
    predictor = OutreachPredictor()
    scrapers = load_scrapers()

    print(f"Loaded {len(scrapers)} scrapers: {[s.__class__.__name__ for s in scrapers]}")

    cities = config.get("cities")
    vibe_threshold = config.get("vibe_threshold")
    target_genres = config.get("target_genres") or ["psytrance"]

    for city in cities:
        if db.is_city_processed(city):
            print(f"Skipping {city} - Already processed in this cycle.")
            continue

        print(f"\n--- Processing {city} (All configured genres) ---")

        raw_venues = []
        for genre in target_genres:
            print(f"Hunting for: {genre}")
            db.log_system_event("DISCOVERY", "START", f"Hunting for {genre} in {city}")
            for scraper in scrapers:
                try:
                    if hasattr(scraper, 'search_venues'):
                        import inspect
                        sig = inspect.signature(scraper.search_venues)
                        if 'query' in sig.parameters:
                            # Use more specific query if possible
                            query = f"underground {genre} club"
                            results = scraper.search_venues(city, query=query)
                        else:
                            results = scraper.search_venues(city)

                        # Add metadata about which genre discovery found this venue
                        for r in results:
                            r['discovery_genre'] = genre
                        raw_venues.extend(results)
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

            # NEW: If it's an RA profile, enrich it first to get the actual website
            if "ra.co/venues/" in v_data.get('website', ''):
                from src.scrapers.resident_advisor import ResidentAdvisorWebScraper
                ra_enricher = ResidentAdvisorWebScraper()
                ra_details = ra_enricher.enrich_venue(v_data['website'])
                if ra_details.get('website'):
                    v_data['website'] = ra_details['website'] # Update to actual venue website
                if ra_details.get('description'):
                    enriched_text += f"\nResident Advisor Description: {ra_details['description']}"
                if ra_details.get('socials'):
                    # Try to find an IG handle from the social links
                    for s in ra_details['socials']:
                        if 'instagram.com' in s:
                            insta_handle = s.split('/')[-1].split('?')[0]
                            db.add_contact({
                                'venue_id': v_id,
                                'instagram_handle': insta_handle
                            })

            if v_data.get('website') and "ra.co" not in v_data['website']:
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

            # Determine which genre to use for qualification
            # If the venue was found during a specific genre hunt, use that.
            # Fallback to the first target genre.
            qualify_genre = v_data.get('discovery_genre', target_genres[0])

            # Only perform AI vibe check if it's a new lead
            vibe_result = ai.vibe_check(v_data['name'], enriched_text, genre=qualify_genre, rating=v_data.get('google_rating'))

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
                    media_library=config.get("media_library"),
                    genre=qualify_genre
                )
                status = 'PENDING_REVIEW'
            else:
                status = 'PENDING_QUALIFICATION'

            lead_data = {
                'venue_id': v_id,
                'vibe_score': vibe_result['vibe_score'],
                'qualification_justification': vibe_result['justification'],
                'generated_pitch': pitch,
                'pipeline_status': status,
                'qualified_genre': qualify_genre
            }
            db.add_lead(lead_data)

            # NEW: Calculate and cache success probability
            lead = db.get_lead_by_venue_id(v_id)
            if lead:
                predictor.predict_success_probability(lead['id'], use_cache=False)

        db.mark_city_processed(city)

    print("\nScraping and qualification complete. Running outreach and follow-up cycles...")
    outreach.run_outreach_cycle()
    follow_up.run_follow_up_cycle()

    print("\nPipeline run complete.")
    db.log_system_event("PIPELINE", "SUCCESS", "Full outreach cycle completed")

if __name__ == "__main__":
    main()
