from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import sys
import os
import subprocess

# Add the parent directory to sys.path to allow absolute imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.db_manager import DatabaseManager
from src.ai_engine import AIEngine
from src.mailer import Mailer
from src.scraper_generator import ScraperGenerator
from src.analytics import AnalyticsEngine
from src.sentiment_analyzer import SentimentAnalyzer
from src.config_manager import ConfigManager
from src.reliability_monitor import ReliabilityMonitor
from src.tour_planner import TourPlanner
from src.outreach_predictor import OutreachPredictor
from src.outreach_engine import OutreachEngine
from src.inbox_monitor import InboxMonitor
from apscheduler.schedulers.background import BackgroundScheduler
from main import main as run_pipeline

app = Flask(__name__)
# Adjust path because we are running from project root or src/dashboard
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../database/outreach.db'))
db = DatabaseManager(db_path=db_path)
ai = AIEngine()
mailer = Mailer()
generator = ScraperGenerator()
analytics = AnalyticsEngine(db_path=db_path)
sentiment_analyzer = SentimentAnalyzer(db_path=db_path)
config_mgr = ConfigManager()
reliability = ReliabilityMonitor(db_path=db_path)
planner = TourPlanner(db_path=db_path)
predictor = OutreachPredictor(db_path=db_path)
outreach_engine = OutreachEngine(db_path=db_path)
inbox_monitor = InboxMonitor(db_path=db_path)

# Initialize Scheduler
scheduler = BackgroundScheduler()

def scheduled_pipeline():
    """Wrapper to run the pipeline on a schedule."""
    print("Scheduler: Starting automated pipeline run...")
    try:
        # Pass empty list to avoid reading sys.argv which contains Flask args
        run_pipeline([])
        print("Scheduler: Automated pipeline run completed.")
    except Exception as e:
        print(f"Scheduler: Pipeline run failed: {e}")

# Note: We'll start the scheduler in the __main__ block
# to avoid issues during module import/tests

import json

@app.context_processor
def inject_attention_count():
    count = db.get_attention_required_count()
    return dict(attention_count=count)

@app.route('/')
def index():
    leads = db.get_pending_leads()
    artists = db.list_artists()
    for lead in leads:
        # success_probability is now fetched from the database in get_pending_leads
        lead['success_prob'] = lead.get('success_probability')

        if lead.get('extracted_traits'):
            try:
                lead['traits_dict'] = json.loads(lead['extracted_traits'])
            except:
                lead['traits_dict'] = {}
    return render_template('index.html', leads=leads, artists=artists, view='pending')

@app.route('/venue/<string:venue_id>')
def venue_detail(venue_id):
    venue = db.get_venue(venue_id)
    if not venue: return "Venue not found", 404

    # Get all leads for this venue (usually just one, but schema allows more conceptually)
    query = "SELECT * FROM outreach_leads WHERE venue_id = ?"
    with db._get_connection() as conn:
        conn.row_factory = sqlite3.Row
        leads = [dict(row) for row in conn.execute(query, (venue_id,)).fetchall()]

    # Get all replies for these leads
    for lead in leads:
        lead['replies'] = db.get_lead_replies(lead['id'])

    # Get contacts
    query = "SELECT * FROM venue_contacts WHERE venue_id = ?"
    with db._get_connection() as conn:
        conn.row_factory = sqlite3.Row
        contacts = [dict(row) for row in conn.execute(query, (venue_id,)).fetchall()]

    if venue.get('extracted_traits'):
        try:
            venue['traits_dict'] = json.loads(venue['extracted_traits'])
        except:
            venue['traits_dict'] = {}
    else:
        venue['traits_dict'] = {}

    warmth = analytics.get_venue_warmth(venue_id)
    return render_template('venue_detail.html', venue=venue, leads=leads, contacts=contacts, warmth=warmth)

@app.route('/pending_qualification')
def pending_qualification():
    leads = db.get_leads_by_status('PENDING_QUALIFICATION')
    for lead in leads:
        venue = db.get_venue(lead['venue_id'])
        lead['name'] = venue['name']
        lead['city'] = venue['city']
        lead['image_url'] = venue.get('image_url')
        lead['visual_description'] = venue.get('visual_description')
        if venue.get('extracted_traits'):
            try:
                lead['traits_dict'] = json.loads(venue['extracted_traits'])
            except:
                lead['traits_dict'] = {}
    return render_template('index.html', leads=leads, view='qualification')

@app.route('/history')
def history():
    leads = db.get_lead_history()
    # Attach replies to each lead for the history view
    for lead in leads:
        lead['replies'] = db.get_lead_replies(lead['id'])
    unmatched = db.get_unmatched_replies()
    return render_template('index.html', leads=leads, unmatched=unmatched, view='history')

@app.route('/booked')
def booked_tracker():
    leads = db.get_leads_by_status('BOOKED')
    return render_template('index.html', leads=leads, view='booked')

@app.route('/mark_booked/<int:lead_id>', methods=['POST'])
def mark_booked(lead_id):
    db.update_lead_status(lead_id, 'BOOKED')
    return redirect(request.referrer or url_for('history'))

@app.route('/mark_lost/<int:lead_id>', methods=['POST'])
def mark_lost(lead_id):
    db.update_lead_status(lead_id, 'LOST')
    return redirect(request.referrer or url_for('history'))

@app.route('/sources')
def sources():
    scrapers_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/scrapers'))
    files = [f for f in os.listdir(scrapers_dir) if f.endswith('.py') and f not in ['__init__.py', 'base_scraper.py']]
    return render_template('sources.html', files=files)

@app.route('/analytics')
def show_analytics():
    stats = analytics.get_summary_stats()
    approval_rate = analytics.get_approval_rate()
    variant_stats = analytics.get_variant_stats()
    funnel = analytics.get_conversion_funnel()
    health = analytics.get_scene_health()
    timeline = analytics.get_outreach_timeline()
    return render_template('analytics.html', stats=stats, approval_rate=approval_rate, variant_stats=variant_stats, funnel=funnel, health=health, timeline=timeline)

@app.route('/export_leads')
def export_leads():
    from flask import Response
    csv_data = analytics.export_leads_csv()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=outreach_leads.csv"}
    )

@app.route('/map')
def show_map():
    venues = db.get_venues_with_location()
    clusters = analytics.get_venue_clusters()
    return render_template('map.html', venues=venues, clusters=clusters)

@app.route('/plan_tour/<int:cluster_index>')
def plan_tour(cluster_index):
    recommendation = planner.plan_optimized_tour(cluster_index)
    pitch = planner.generate_cluster_pitch(cluster_index)
    return jsonify({
        "recommendation": recommendation,
        "pitch": pitch
    })

@app.route('/dispatch_tour/<int:cluster_index>', methods=['POST'])
def dispatch_tour(cluster_index):
    clusters = analytics.get_venue_clusters()
    if cluster_index >= len(clusters):
        return jsonify({"error": "Cluster not found"}), 404

    cluster = clusters[cluster_index]
    pitch = request.json.get('pitch')

    if not pitch:
        return jsonify({"error": "Pitch content required"}), 400

    results = outreach_engine.dispatch_cluster_pitch(cluster['venues'], pitch)
    return jsonify(results)

@app.route('/system')
def system_status():
    stats = analytics.get_summary_stats()
    version = "unknown"
    version_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../VERSION.md'))
    if os.path.exists(version_path):
        with open(version_path, 'r') as f:
            version = f.read().strip()

    git_info = {
        "branch": subprocess.getoutput("git rev-parse --abbrev-ref HEAD"),
        "commit": subprocess.getoutput("git rev-parse --short HEAD"),
        "branches": subprocess.getoutput("git branch --format='%(refname:short)'").splitlines()
    }

    # Fetch last 10 sync logs
    sync_logs = [log for log in db.get_latest_system_logs(limit=20) if log['component'] == 'SYNC']

    daily_budget = cfg.get('openai_daily_budget_tokens')
    used_today = db.get_ai_usage_today()

    pipeline_history = db.get_pipeline_history()

    sync_stats = reliability.get_sync_health_stats()
    stale_branches = reliability.get_stale_branches()
    audit_trail = db.get_version_audit_trail()
    ai_usage = db.get_ai_usage_stats(days=7)

    performance_report = None
    perf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../PERFORMANCE.md'))
    if os.path.exists(perf_path):
        with open(perf_path, 'r') as f:
            performance_report = f.read()

    return render_template('system.html', stats=stats, version=version, git_info=git_info, sync_logs=sync_logs, pipeline_history=pipeline_history, sync_stats=sync_stats, stale_branches=stale_branches, audit_trail=audit_trail, ai_usage=ai_usage, performance_report=performance_report)

@app.route('/reset_cycles', methods=['POST'])
def reset_cycles():
    city = request.form.get('city')
    db.reset_city_cycle(city)
    return redirect(url_for('system_status'))

@app.route('/run_pipeline_now', methods=['POST'])
def run_pipeline_now():
    # Trigger a run immediately via the scheduler or directly
    scheduler.add_job(scheduled_pipeline, id='manual_run', replace_existing=True)
    return jsonify({"status": "success", "message": "Pipeline run started in background."})

@app.route('/run_sync', methods=['POST'])
def run_sync():
    # Trigger the sync protocol
    # Note: Using absolute path to sync_repo.py in root
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../sync_repo.py'))
    result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)

    status = 'success' if result.returncode == 0 else 'error'
    return jsonify({
        "status": status,
        "output": result.stdout + result.stderr
    })

@app.route('/match_unmatched/<int:reply_id>', methods=['POST'])
def match_unmatched(reply_id):
    lead_id = request.form.get('lead_id')
    if lead_id:
        with db._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            unmatched = conn.execute("SELECT * FROM unmatched_replies WHERE id = ?", (reply_id,)).fetchone()
            if unmatched:
                sentiment_analyzer.process_new_reply(lead_id, f"Subject: {unmatched['subject']}\n\n{unmatched['content']}")
                db.delete_unmatched_reply(reply_id)
    return redirect(url_for('history'))

@app.route('/delete_unmatched/<int:reply_id>', methods=['POST'])
def delete_unmatched(reply_id):
    db.delete_unmatched_reply(reply_id)
    return redirect(url_for('history'))

@app.route('/fetch_replies', methods=['POST'])
def fetch_replies():
    try:
        count = inbox_monitor.fetch_new_replies()
        return jsonify({
            "status": "success",
            "count": count,
            "message": f"Processed {count} new replies."
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/simulate_reply/<int:lead_id>', methods=['POST'])
def simulate_reply(lead_id):
    content = request.form.get('content')
    if content:
        sentiment = sentiment_analyzer.process_new_reply(lead_id, content)
        return redirect(url_for('history'))
    return "Missing content", 400

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        # Parse media library
        media_library = []
        names = request.form.getlist('media_name[]')
        urls = request.form.getlist('media_url[]')
        tags_list = request.form.getlist('media_tags[]')
        for i in range(len(names)):
            if names[i] and urls[i]:
                media_library.append({
                    "name": names[i],
                    "url": urls[i],
                    "tags": [t.strip() for t in tags_list[i].split(',')] if tags_list[i] else []
                })

        new_config = {
            "cities": [c.strip() for f in request.form.getlist('cities') for c in f.split(',')],
            "target_genres": [g.strip() for f in request.form.getlist('genres') for g in f.split(',')],
            "epk_link": request.form.get('epk_link'),
            "mix_link": request.form.get('mix_link'),
            "artist_name": request.form.get('artist_name'),
            "collective_name": request.form.get('collective_name'),
            "home_city": request.form.get('home_city', 'Detroit'),
            "vibe_threshold": int(request.form.get('vibe_threshold', 6)),
            "auto_approve_threshold": int(request.form.get('auto_approve_threshold', 9)),
            "daily_outreach_limit": int(request.form.get('daily_outreach_limit', 10)),
            "outreach_delay_min": int(request.form.get('outreach_delay_min', 5)),
            "follow_up_days": int(request.form.get('follow_up_days', 7)),
            "max_follow_ups": int(request.form.get('max_follow_ups', 2)),
            "rate_card": request.form.get('rate_card'),
            "availability_ranges": request.form.get('availability_ranges'),
            "imap_server": request.form.get('imap_server'),
            "imap_user": request.form.get('imap_user'),
            "imap_password": request.form.get('imap_password'),
            "imap_port": int(request.form.get('imap_port', 993)),
            "detroit_search_queries": [q.strip() for f in request.form.getlist('detroit_queries') for q in f.split('\n') if q.strip()],
            "detroit_neighborhoods": [n.strip() for f in request.form.getlist('detroit_hoods') for n in f.split('\n') if n.strip()],
            "media_library": media_library
        }
        config_mgr.save_config(new_config)
        return redirect(url_for('settings'))

    current_config = config_mgr.load_config()
    artists = db.list_artists()
    return render_template('settings.html', config=current_config, artists=artists)

@app.route('/artists/add', methods=['POST'])
def add_artist():
    artist_data = {
        "name": request.form.get('name'),
        "bio": request.form.get('bio'),
        "genres": request.form.get('genres'),
        "epk_link": request.form.get('epk_link'),
        "mix_link": request.form.get('mix_link'),
        "rate_card": request.form.get('rate_card')
    }
    if artist_data['name']:
        db.add_artist(artist_data)
    return redirect(url_for('settings'))

@app.route('/artists/delete/<int:artist_id>', methods=['POST'])
def delete_artist(artist_id):
    db.delete_artist(artist_id)
    return redirect(url_for('settings'))

@app.route('/add_source', methods=['POST'])
def add_source():
    url = request.form.get('url')
    name = request.form.get('name')
    if url and name:
        generator.generate_scraper(url, name)
        return redirect(url_for('sources'))
    return "Missing URL or Name", 400

@app.route('/approve/<int:lead_id>', methods=['POST'])
def approve(lead_id):
    pitch = request.form.get('pitch')
    artist_id = request.form.get('artist_id')

    # Update lead status and optionally artist_id
    db.update_lead_status(lead_id, 'APPROVED', pitch=pitch)
    if artist_id:
        with db._get_connection() as conn:
            conn.execute("UPDATE outreach_leads SET artist_id = ? WHERE id = ?", (artist_id, lead_id))

    lead = db.get_lead(lead_id)

    primary_genre = (cfg.get("target_genres") or ["psytrance"])[0]

    query = "SELECT email FROM venue_contacts WHERE venue_id = ?"
    with db._get_connection() as conn:
        cursor = conn.execute(query, (lead['venue_id'],))
        contact = cursor.fetchone()
    if contact and contact[0]:
        email = contact[0].split(',')[0].strip()
        subject = f"Proposal for {primary_genre.capitalize()} Night Residency"
        if mailer.send_email(email, subject, pitch):
            db.update_lead_status(lead_id, 'SENT')
    return redirect(url_for('index'))

@app.route('/reject/<int:lead_id>', methods=['POST'])
def reject(lead_id):
    db.update_lead_status(lead_id, 'REJECTED')
    return redirect(url_for('index'))

@app.route('/send_reply/<int:reply_id>', methods=['POST'])
def send_reply(reply_id):
    reply_content = request.form.get('reply_content')

    # Fetch lead info via reply_id
    with db._get_connection() as conn:
        conn.row_factory = sqlite3.Row
        reply = conn.execute("SELECT * FROM lead_replies WHERE id = ?", (reply_id,)).fetchone()
        if not reply: return "Reply not found", 404

        lead = db.get_lead(reply['lead_id'])
        venue = db.get_venue(lead['venue_id'])

        # Fetch email
        cursor = conn.execute("SELECT email FROM venue_contacts WHERE venue_id = ?", (venue['id'],))
        contact = cursor.fetchone()

    if contact and contact[0]:
        email = contact[0].split(',')[0].strip()
        subject = f"Re: Proposal for Psytrance Night Residency - {venue['name']}"
        if mailer.send_email(email, subject, reply_content):
            # Update reply as 'SENT' or similar if we had a status,
            # for now we'll just log success
            db.log_system_event("OUTREACH", "SUCCESS", f"Sent manual reply to {email} for lead {lead['id']}")
            db.mark_reply_handled(reply_id) # dismiss notification on send
            return redirect(url_for('history'))

    return "Error sending reply", 500

@app.route('/dismiss_reply/<int:reply_id>', methods=['POST'])
def dismiss_reply(reply_id):
    is_unmatched = request.args.get('unmatched', 'false').lower() == 'true'
    db.mark_reply_handled(reply_id, is_unmatched=is_unmatched)
    return jsonify({"status": "success"})

@app.route('/requalify/<int:lead_id>', methods=['POST'])
def requalify(lead_id):
    lead = db.get_lead(lead_id)
    if not lead: return jsonify({"error": "Lead not found"}), 404
    venue = db.get_venue(lead['venue_id'])
    if not venue: return jsonify({"error": "Venue not found"}), 404

    primary_genre = (cfg.get("target_genres") or ["psytrance"])[0]

    # Re-run vibe check
    vibe_result = ai.vibe_check(
        venue['name'],
        venue.get('raw_about_text', ''),
        genre=lead.get('qualified_genre', primary_genre),
        rating=venue.get('google_rating')
    )

    # Update status if threshold met
    vibe_threshold = cfg.get("vibe_threshold") or 6
    new_status = 'PENDING_REVIEW' if vibe_result['vibe_score'] >= vibe_threshold else 'PENDING_QUALIFICATION'

    # Generate pitch if newly qualified
    pitch = lead['generated_pitch']
    if new_status == 'PENDING_REVIEW' and not pitch:
        traits = venue.get('extracted_traits', '{}')
        pitch = ai.generate_pitch(
            venue['name'],
            vibe_result['justification'],
            epk_link=cfg.get("epk_link"),
            mix_link=cfg.get("mix_link"),
            traits=traits,
            media_library=cfg.get("media_library"),
            genre=lead.get('qualified_genre', primary_genre)
        )

    # Update lead
    query = "UPDATE outreach_leads SET vibe_score = ?, qualification_justification = ?, pipeline_status = ?, generated_pitch = ? WHERE id = ?"
    with db._get_connection() as conn:
        conn.execute(query, (vibe_result['vibe_score'], vibe_result['justification'], new_status, pitch, lead_id))

    return jsonify({"status": "success", "new_score": vibe_result['vibe_score'], "new_status": new_status})

@app.route('/generate_dm/<int:lead_id>', methods=['POST'])
def generate_dm(lead_id):
    lead = db.get_lead(lead_id)
    if not lead: return jsonify({"error": "Lead not found"}), 404
    venue = db.get_venue(lead['venue_id'])
    if not venue: return jsonify({"error": "Venue not found"}), 404

    artist_id = request.json.get('artist_id') if request.is_json else request.form.get('artist_id')
    primary_genre = (cfg.get("target_genres") or ["psytrance"])[0]

    dm_pitch = ai.generate_dm_pitch(
        venue['name'],
        lead['qualification_justification'],
        epk_link=cfg.get("epk_link"),
        mix_link=cfg.get("mix_link"),
        genre=primary_genre,
        artist_id=artist_id
    )
    return jsonify({"dm": dm_pitch})

@app.route('/log_dm_sent/<int:lead_id>', methods=['POST'])
def log_dm_sent(lead_id):
    try:
        db.log_dm_sent(lead_id)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ingest_dm/<int:lead_id>', methods=['POST'])
def ingest_dm(lead_id):
    content = request.json.get('content') if request.is_json else request.form.get('content')
    if not content: return jsonify({"error": "No content provided"}), 400

    from src.sentiment_analyzer import SentimentAnalyzer
    analyzer = SentimentAnalyzer(ai.client)
    sentiment = analyzer.analyze_sentiment(content)

    lead = db.get_lead(lead_id)
    venue = db.get_venue(lead['venue_id'])
    artist_id = lead.get('artist_id')

    draft = ai.generate_reply_draft(
        venue['name'],
        content,
        lead['generated_pitch'],
        genre=lead['qualified_genre'],
        artist_id=artist_id
    )

    try:
        db.add_reply(lead_id, content, sentiment, draft, source_channel='DM')
        db.update_lead_negotiation_from_dm(lead_id, sentiment)
        return jsonify({"success": True, "sentiment": sentiment})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/regenerate/<int:lead_id>', methods=['POST'])
def regenerate(lead_id):
    lead = db.get_lead(lead_id)
    if not lead: return jsonify({"error": "Lead not found"}), 404
    venue = db.get_venue(lead['venue_id'])
    if not venue: return jsonify({"error": "Venue not found"}), 404

    artist_id = request.json.get('artist_id') if request.is_json else request.form.get('artist_id')

    primary_genre = (cfg.get("target_genres") or ["psytrance"])[0]
    new_pitch = ai.generate_pitch(
        venue['name'],
        lead['qualification_justification'],
        epk_link=cfg.get("epk_link"),
        mix_link=cfg.get("mix_link"),
        traits=venue.get('extracted_traits'),
        media_library=cfg.get("media_library"),
        genre=primary_genre,
        artist_id=artist_id
    )
    return jsonify({"pitch": new_pitch})

if __name__ == '__main__':
    # Add a weekly job for the pipeline
    # For now, let's just make it configurable via code or later via UI
    scheduler.add_job(scheduled_pipeline, 'interval', weeks=1, id='weekly_pipeline')
    scheduler.start()

    app.run(debug=True, port=5000)
