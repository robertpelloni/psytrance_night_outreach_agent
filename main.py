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
        venues = []
        venues.extend(gm_scraper.search_venues(city))
        venues.extend(ra_scraper.search_venues(city))

        for v_data in venues:
            # 2. Add to DB
            db.add_venue(v_data)

            # 3. Enrich & Vibe Check
            vibe_result = ai.vibe_check(v_data['name'], v_data['raw_about_text'])

            # 4. Generate Pitch if vibe score is high
            pitch = ""
            if vibe_result['vibe_score'] >= 7:
                pitch = ai.generate_pitch(v_data['name'], vibe_result['justification'])
                status = 'PENDING_REVIEW'
            else:
                status = 'PENDING_QUALIFICATION'

            # 5. Save as Lead
            lead_data = {
                'venue_id': v_data['id'],
                'vibe_score': vibe_result['vibe_score'],
                'qualification_justification': vibe_result['justification'],
                'generated_pitch': pitch,
                'pipeline_status': status
            }
            db.add_lead(lead_data)

            # 6. Contact Discovery (Enrichment)
            if v_data.get('website'):
                contact_info = ContactExtractor.scrape_website(v_data['website'])
                if contact_info:
                    db.add_contact({
                        'venue_id': v_data['id'],
                        'email': ", ".join(contact_info.get('emails', [])),
                        'instagram_handle': ", ".join(contact_info.get('instagrams', []))
                    })

    print("Pipeline run complete.")

if __name__ == "__main__":
    main()
