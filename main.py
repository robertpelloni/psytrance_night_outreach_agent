import os
import importlib.util
import sys
import random
from dotenv import load_dotenv
from src.db_manager import DatabaseManager
from src.scrapers.base_scraper import ContactExtractor
from src.ai_engine import AIEngine
from src.config_manager import ConfigManager
from src.outreach_engine import OutreachEngine
from src.follow_up_engine import FollowUpEngine
from src.geocoding import GeocodingUtility
from src.outreach_predictor import OutreachPredictor
from src.analytics import AnalyticsEngine


def load_scrapers():
    """Dynamically discovers and loads all scraper classes from src/scrapers/."""
    scrapers = []
    scrapers_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "src/scrapers")
    )
    if scrapers_dir not in sys.path:
        sys.path.append(scrapers_dir)
    for filename in os.listdir(scrapers_dir):
        if filename.endswith(".py") and filename not in [
            "__init__.py",
            "base_scraper.py",
        ]:
            module_name = filename[:-3]
            try:
                module = importlib.import_module(f"src.scrapers.{module_name}")
                for attr in dir(module):
                    cls = getattr(module, attr)
                    if (
                        isinstance(cls, type)
                        and attr.endswith("Scraper")
                        and attr
                        not in [
                            "BaseScraper",
                            "GoogleMapsScraper",
                            "ResidentAdvisorScraper",
                        ]
                    ):
                        scrapers.append(cls())
            except Exception as e:
                print(f"Error loading module {module_name}: {e}")
    return scrapers


def build_search_queries(city, config):
    """Builds search queries tailored to the city.
    For Detroit-area cities, uses neighborhood-aware and scene-specific queries.
    For other cities, falls back to genre-based queries.
    """
    detroit_area = [
        "Detroit",
        "Hamtramck",
        "Ferndale",
        "Royal Oak",
        "Ann Arbor",
        "Grand Rapids",
    ]
    is_home_region = city in detroit_area
    queries = []
    target_genres = config.get("target_genres") or ["psytrance"]

    if is_home_region:
        # Detroit-specific search queries from config
        detroit_queries = config.get("detroit_search_queries") or []
        for q in detroit_queries:
            queries.append((q, "psytrance"))

        # Neighborhood-level deep search
        neighborhoods = config.get("detroit_neighborhoods") or []
        for hood in neighborhoods:
            queries.append((f"electronic music venue {hood}", "psytrance"))
            queries.append((f"underground club {hood}", "psytrance"))

        # Genre-specific queries for the Detroit scene
        for genre in target_genres:
            queries.append((f"{genre} event {city}", genre))
            queries.append((f"{genre} party {city}", genre))
    else:
        # Standard genre-based queries for expansion cities
        for genre in target_genres:
            queries.append((f"underground {genre} club", genre))
            queries.append((f"{genre} venue", genre))

    # Deduplicate
    seen = set()
    unique = []
    for q, g in queries:
        if q not in seen:
            seen.add(q)
            unique.append((q, g))
    return unique


def qualify_and_pitch(v_data, v_id, db, ai, geocoder, predictor, config, analytics):
    """Runs full qualification, trait extraction, geocoding, and pitch generation."""
    vibe_threshold = config.get("vibe_threshold") or 6
    enriched_text = v_data.get("raw_about_text", "")

    # RA profile enrichment
    if "ra.co/venues/" in v_data.get("website", ""):
        from src.scrapers.resident_advisor import ResidentAdvisorWebScraper

        ra_enricher = ResidentAdvisorWebScraper()
        ra_details = ra_enricher.enrich_venue(v_data["website"])
        if ra_details.get("website"):
            v_data["website"] = ra_details["website"]
        if ra_details.get("image_url"):
            v_data["image_url"] = ra_details["image_url"]
        if ra_details.get("description"):
            enriched_text += (
                f"\nResident Advisor Description: {ra_details['description']}"
            )
        if ra_details.get("socials"):
            for s in ra_details["socials"]:
                if "instagram.com" in s:
                    insta_handle = s.split("/")[-1].split("?")[0]
                    db.add_contact({"venue_id": v_id, "instagram_handle": insta_handle})

    # Website contact extraction
    if v_data.get("website") and "ra.co" not in v_data["website"]:
        contact_info = ContactExtractor.scrape_website(v_data["website"])
        if contact_info:
            if contact_info.get("about_text"):
                enriched_text = contact_info["about_text"]
            insta = ", ".join(contact_info.get("instagrams", []))
            db.add_contact(
                {
                    "venue_id": v_id,
                    "email": ", ".join(contact_info.get("emails", [])),
                    "instagram_handle": insta,
                }
            )
            social_context = ContactExtractor.get_social_context(insta)
            if social_context:
                enriched_text += f"\nSocial Media Context: {social_context}"

    # Qualification genre
    qualify_genre = v_data.get(
        "discovery_genre", (config.get("target_genres") or ["psytrance"])[0]
    )

    # Vision-Enriched Qualification
    image_url = v_data.get("image_url")
    if image_url:
        print(f"  Performing visual analysis for {v_data['name']}...")
        visual_result = ai.analyze_visual_vibe(image_url, genre=qualify_genre)
        visual_desc = visual_result.get("visual_description", "")
        db.update_venue_visuals(v_id, image_url, visual_desc)
        if visual_desc:
            enriched_text += f"\nVisual Aesthetic Analysis: {visual_desc}"

    # AI Vibe Check
    vibe_result = ai.vibe_check(
        v_data["name"],
        enriched_text,
        genre=qualify_genre,
        rating=v_data.get("google_rating"),
    )

    # Extract traits
    traits = ai.extract_venue_traits(enriched_text)
    db.update_venue_traits(v_id, traits)

    # Geocode
    lat, lon = geocoder.geocode_venue(v_data["name"], v_data["city"])
    if lat and lon:
        db.update_venue_location(v_id, lat, lon)

    # Generate pitch if qualified
    pitch = ""
    variant = "Professional"

    if vibe_result["vibe_score"] >= vibe_threshold:
        # Epsilon-Greedy Variant Selection
        variant_stats = analytics.get_variant_stats()
        variants = ["Professional", "Underground", "Technical"]
        epsilon = 0.2
        if random.random() < epsilon or not variant_stats:
            variant = random.choice(variants)
            print(f"  Exploration: Randomly assigned '{variant}' variant.")
        else:
            variant = max(
                variant_stats.keys(), key=lambda k: variant_stats[k]["conversion_rate"]
            )
            conv = variant_stats[variant]["conversion_rate"]
            print(f"  Exploitation: Best variant '{variant}' (Conv: {conv}%).")

        print(f"  Generating '{variant}' pitch for {v_data['name']}...")
        pitch = ai.generate_pitch(
            v_data["name"],
            vibe_result["justification"],
            epk_link=config.get("epk_link"),
            mix_link=config.get("mix_link"),
            traits=traits,
            media_library=config.get("media_library"),
            genre=qualify_genre,
            variant=variant,
        )
        status = "PENDING_REVIEW"
    else:
        status = "PENDING_QUALIFICATION"

    lead_data = {
        "venue_id": v_id,
        "vibe_score": vibe_result["vibe_score"],
        "qualification_justification": vibe_result["justification"],
        "generated_pitch": pitch,
        "pipeline_status": status,
        "qualified_genre": qualify_genre,
        "pitch_variant": variant,
    }
    db.add_lead(lead_data)

    # Cache success probability
    lead = db.get_lead_by_venue_id(v_id)
    if lead:
        predictor.predict_success_probability(lead["id"], use_cache=False)

    print(
        f"  [{v_data['name']}] Vibe: {vibe_result['vibe_score']}/10 | Status: {status} | Genre: {qualify_genre}"
    )


def main():
    load_dotenv()
    db = DatabaseManager()
    ai = AIEngine()
    config = ConfigManager()
    outreach = OutreachEngine()
    follow_up = FollowUpEngine()
    geocoder = GeocodingUtility()
    predictor = OutreachPredictor()
    analytics = AnalyticsEngine()
    scrapers = load_scrapers()

    artist_name = config.get("artist_name") or ""
    collective = config.get("collective_name") or ""
    home_city = config.get("home_city") or "Detroit"

    print(f"\n{'=' * 60}")
    print("  PSYTRANCE NIGHT OUTREACH AGENT")
    print(f"  Home Base: {home_city}")
    if artist_name:
        print(f"  Artist: {artist_name}")
    if collective:
        print(f"  Collective: {collective}")
    print(f"  Scrapers: {len(scrapers)} ({[s.__class__.__name__ for s in scrapers]})")
    print(f"{'=' * 60}\n")

    cities = config.get("cities") or [home_city]
    target_genres = config.get("target_genres") or ["psytrance"]

    for city in cities:
        if db.is_city_processed(city):
            print(f"Skipping {city} - Already processed in this cycle.")
            continue

        print(f"\n--- Processing {city} ---")

        # Build city-specific search queries
        search_queries = build_search_queries(city, config)
        print(f"  {len(search_queries)} search queries for {city}")

        raw_venues = []
        seen_venue_names = set()

        for query, genre in search_queries:
            print(f'\n  Hunting: "{query}" (genre: {genre})')
            db.log_system_event("DISCOVERY", "START", f"Hunting: '{query}' in {city}")

            for scraper in scrapers:
                try:
                    if hasattr(scraper, "search_venues"):
                        import inspect

                        sig = inspect.signature(scraper.search_venues)
                        if "query" in sig.parameters:
                            results = scraper.search_venues(city, query=query)
                        else:
                            results = scraper.search_venues(city)

                        for r in results:
                            r["discovery_genre"] = genre
                            venue_key = (r["name"].strip().lower(), city.lower())
                            if venue_key not in seen_venue_names:
                                seen_venue_names.add(venue_key)
                                raw_venues.append(r)
                except Exception as e:
                    print(f"  Error running {scraper.__class__.__name__}: {e}")

        print(f"\n  Discovered {len(raw_venues)} unique venues in {city}")

        for v_data in raw_venues:
            existing_id = db.venue_exists_by_name(v_data["name"], v_data["city"])
            if existing_id:
                v_id = existing_id
                existing_lead = db.get_lead_by_venue_id(v_id)
                if existing_lead:
                    print(f"  Skipping {v_data['name']} - Lead already exists.")
                    continue
            else:
                v_id = v_data["id"]
                db.add_venue(v_data)

            qualify_and_pitch(
                v_data, v_id, db, ai, geocoder, predictor, config, analytics
            )

        db.mark_city_processed(city)

    print(
        "\nScraping and qualification complete. Running outreach and follow-up cycles..."
    )
    outreach.run_outreach_cycle()
    follow_up.run_follow_up_cycle()

    print("\nPipeline run complete.")
    db.log_system_event("PIPELINE", "SUCCESS", "Full outreach cycle completed")


if __name__ == "__main__":
    main()
