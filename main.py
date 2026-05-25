import os
from dotenv import load_dotenv
from src.db_manager import DatabaseManager
from src.scrapers.google_maps import GoogleMapsPlaywrightScraper
from src.scrapers.resident_advisor import ResidentAdvisorWebScraper
from src.scrapers.base_scraper import ContactExtractor
from src.ai_engine import AIEngine

def main():
    load_dotenv()
    db = DatabaseManager()
    gm_scraper = GoogleMapsPlaywrightScraper()
    ra_scraper = ResidentAdvisorWebScraper()
    ai = AIEngine()

    cities = ["Detroit", "Berlin", "London"]

    for city in cities:
        print(f"--- Processing {city} ---")

        # 1. Discover Venues
        raw_venues = []
        raw_venues.extend(gm_scraper.search_venues(city))
        raw_venues.extend(ra_scraper.search_venues(city))

        for v_data in raw_venues:
            # 2. Check for existence and Add Venue to DB
            existing_id = db.venue_exists_by_name(v_data['name'], v_data['city'])
            if existing_id:
                v_id = existing_id
            else:
                v_id = v_data['id']
                db.add_venue(v_data)

            # 3. Enrichment & Contact Discovery
            enriched_text = v_data.get('raw_about_text', "")
            if v_data.get('website'):
                contact_info = ContactExtractor.scrape_website(v_data['website'])
                if contact_info:
                    # Update enriched text with website content for better AI analysis
                    if contact_info.get('about_text'):
                        enriched_text = contact_info['about_text']

                    db.add_contact({
                        'venue_id': v_id,
                        'email': ", ".join(contact_info.get('emails', [])),
                        'instagram_handle': ", ".join(contact_info.get('instagrams', []))
                    })

            # 4. Vibe Check using Enriched Text
            vibe_result = ai.vibe_check(v_data['name'], enriched_text)

            # 5. Generate Pitch if vibe score is high
            pitch = ""
            if vibe_result['vibe_score'] >= 7:
                pitch = ai.generate_pitch(v_data['name'], vibe_result['justification'])
                status = 'PENDING_REVIEW'
            else:
                status = 'PENDING_QUALIFICATION'

            # 6. Save as Lead
            lead_data = {
                'venue_id': v_id,
                'vibe_score': vibe_result['vibe_score'],
                'qualification_justification': vibe_result['justification'],
                'generated_pitch': pitch,
                'pipeline_status': status
            }
            db.add_lead(lead_data)

    print("Pipeline run complete.")

if __name__ == "__main__":
    main()
