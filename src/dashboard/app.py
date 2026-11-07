from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import sys
import os
import subprocess
import json
import signal

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

@app.context_processor
def inject_attention_count():
    count = db.get_attention_required_count()
    return dict(attention_count=count)

def get_full_dashboard_context(active_tab='pipeline', view='pending'):
    """
    Consolidated helper to load all necessary data across all high-value modules
    for the unified single-page dashboard architecture.
    """
    # 1. Pipeline & Lead Queues
    if view == 'pending':
        leads = db.get_pending_leads()
    elif view == 'qualification':
        leads = db.get_leads_by_status('PENDING_QUALIFICATION')
        for lead in leads:
            venue = db.get_venue(lead['venue_id'])
            if venue:
                lead['name'] = venue['name']
                lead['city'] = venue['city']
                lead['image_url'] = venue.get('image_url')
                lead['visual_description'] = venue.get('visual_description')
                if venue.get('extracted_traits'):
                    try:
                        lead['traits_dict'] = json.loads(venue['extracted_traits'])
                    except:
                        lead['traits_dict'] = {}
    elif view == 'history':
        leads = db.get_lead_history()
        for lead in leads:
            lead['replies'] = db.get_lead_replies(lead['id'])
    elif view == 'booked':
        leads = db.get_leads_by_status('BOOKED')
    elif view == 'dm_queue':
        query = """
            SELECT l.*, v.name, v.city, vc.instagram_handle
            FROM outreach_leads l
            JOIN venues v ON l.venue_id = v.id
            JOIN venue_contacts vc ON v.id = vc.venue_id
            WHERE l.pipeline_status IN ('SENT', 'REPLIED')
            AND vc.email IS NULL
            AND vc.instagram_handle IS NOT NULL
        """
        with db._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query)
            leads = [dict(row) for row in cursor.fetchall()]
    elif view == 'pending_follow_ups':
        query = "SELECT l.*, v.name, v.city FROM outreach_leads l JOIN venues v ON l.venue_id = v.id WHERE l.pipeline_status = 'PENDING_FOLLOW_UP'"
        with db._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query)
            leads = [dict(row) for row in cursor.fetchall()]
    else:
        leads = db.get_pending_leads()

    for lead in leads:
        lead['success_prob'] = lead.get('success_probability')
        if lead.get('extracted_traits') and 'traits_dict' not in lead:
            try:
                lead['traits_dict'] = json.loads(lead['extracted_traits'])
            except:
                lead['traits_dict'] = {}

    unmatched = db.get_unmatched_replies() if view == 'history' or active_tab in ['pipeline', 'analytics'] else []
    artists = db.list_artists()

    # 2. Map & Geographical Intelligence
    venues = db.get_venues_with_location()
    clusters = analytics.get_venue_clusters()

    # 3. Analytics & A/B Testing
    stats = analytics.get_summary_stats()
    approval_rate = analytics.get_approval_rate()
    variant_stats = analytics.get_variant_stats()
    funnel = analytics.get_conversion_funnel()
    health = analytics.get_scene_health()
    timeline = analytics.get_outreach_timeline()

    # 4. Settings & Media Library
    current_config = config_mgr.load_config()

    # 5. System Health & Git Protocols
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
    sync_logs = [log for log in db.get_latest_system_logs(limit=20) if log['component'] == 'SYNC']
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

    # 6. Scraper Sources
    scrapers_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/scrapers'))
    scraper_files = [f for f in os.listdir(scrapers_dir) if f.endswith('.py') and f not in ['__init__.py', 'base_scraper.py']]

    return {
        'active_tab': active_tab,
        'view': view,
        'leads': leads,
        'artists': artists,
        'unmatched': unmatched,
        'venues': venues,
        'clusters': clusters,
        'stats': stats,
        'approval_rate': approval_rate,
        'variant_stats': variant_stats,
        'funnel': funnel,
        'health': health,
        'timeline': timeline,
        'config': current_config,
        'version': version,
        'git_info': git_info,
        'sync_logs': sync_logs,
        'pipeline_history': pipeline_history,
        'sync_stats': sync_stats,
        'stale_branches': stale_branches,
        'audit_trail': audit_trail,
        'ai_usage': ai_usage,
        'performance_report': performance_report,
        'files': scraper_files
    }

@app.route('/')
def index():
    tab = request.args.get('tab', 'pipeline')
    view = request.args.get('view', 'pending')
    ctx = get_full_dashboard_context(active_tab=tab, view=view)
    return render_template('index.html', **ctx)

@app.route('/venue/<string:venue_id>')
def venue_detail(venue_id):
    venue = db.get_venue(venue_id)
    if not venue: return "Venue not found", 404

    query = "SELECT * FROM outreach_leads WHERE venue_id = ?"
    with db._get_connection() as conn:
        conn.row_factory = sqlite3.Row
        leads = [dict(row) for row in conn.execute(query, (venue_id,)).fetchall()]

    for lead in leads:
        lead['replies'] = db.get_lead_replies(lead['id'])

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
    notes = db.get_venue_notes(venue_id)
    return render_template('venue_detail.html', venue=venue, leads=leads, contacts=contacts, warmth=warmth, notes=notes)

@app.route('/venue/<string:venue_id>/notes', methods=['GET', 'POST'])
def venue_notes_api(venue_id):
    """API endpoint to get or add private curator notes for a venue."""
    if request.method == 'POST':
        note = request.form.get('note') or (request.json.get('note') if request.is_json else None)
        author = request.form.get('author') or (request.json.get('author') if request.is_json else 'Curator')
        if not note:
            if request.is_json:
                return jsonify({"error": "Note text is required"}), 400
            return redirect(url_for('venue_detail', venue_id=venue_id))

        note_id = db.add_venue_note(venue_id, note, author=author)
        if request.is_json:
            return jsonify({"status": "success", "note_id": note_id, "note": note, "author": author})
        return redirect(url_for('venue_detail', venue_id=venue_id))

    notes = db.get_venue_notes(venue_id)
    return jsonify({"venue_id": venue_id, "notes": notes})

@app.route('/pending_qualification')
def pending_qualification():
    ctx = get_full_dashboard_context(active_tab='pipeline', view='qualification')
    return render_template('index.html', **ctx)

@app.route('/history')
def history():
    ctx = get_full_dashboard_context(active_tab='pipeline', view='history')
    return render_template('index.html', **ctx)

@app.route('/booked')
def booked_tracker():
    ctx = get_full_dashboard_context(active_tab='pipeline', view='booked')
    return render_template('index.html', **ctx)

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
    ctx = get_full_dashboard_context(active_tab='sources', view='pending')
    return render_template('index.html', **ctx)

@app.route('/analytics')
def show_analytics():
    ctx = get_full_dashboard_context(active_tab='analytics', view='pending')
    return render_template('index.html', **ctx)

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
    ctx = get_full_dashboard_context(active_tab='map', view='pending')
    return render_template('index.html', **ctx)

@app.route('/plan_tour/<int:cluster_index>')
def plan_tour(cluster_index):
    recommendation = planner.plan_optimized_tour(cluster_index)
    pitch = planner.generate_cluster_pitch(cluster_index)
    return jsonify({
        "recommendation": recommendation,
        "pitch": pitch
    })

@app.route('/plan_circuit')
def plan_circuit():
    recommendation = planner.plan_optimized_tour(cluster_index=None)
    route = planner.get_circuit_route() if hasattr(planner, 'get_circuit_route') else []
    return jsonify({
        "recommendation": recommendation,
        "route": route
    })

@app.route('/dispatch_circuit', methods=['POST'])
def dispatch_circuit():
    route = planner.get_circuit_route() if hasattr(planner, 'get_circuit_route') else []
    if not route:
        return jsonify({"error": "No circuit route available"}), 404

    pitch = request.json.get('pitch') if request.is_json else request.form.get('pitch')
    if not pitch:
        return jsonify({"error": "Pitch content required"}), 400

    venues_list = []
    for cluster in route:
        venues_list.extend(cluster['venues'])

    results = outreach_engine.dispatch_cluster_pitch(venues_list, pitch)
    return jsonify(results)

@app.route('/dispatch_tour/<int:cluster_index>', methods=['POST'])
def dispatch_tour(cluster_index):
    clusters = analytics.get_venue_clusters()
    if cluster_index >= len(clusters):
        return jsonify({"error": "Cluster not found"}), 404

    cluster = clusters[cluster_index]
    pitch = request.json.get('pitch') if request.is_json else request.form.get('pitch')

    if not pitch:
        return jsonify({"error": "Pitch content required"}), 400

    results = outreach_engine.dispatch_cluster_pitch(cluster['venues'], pitch)
    return jsonify(results)

@app.route('/system')
def system_status():
    ctx = get_full_dashboard_context(active_tab='system', view='pending')
    return render_template('index.html', **ctx)

@app.route('/reset_cycles', methods=['POST'])
def reset_cycles():
    city = request.form.get('city')
    db.reset_city_cycle(city)
    return redirect(url_for('system_status'))

@app.route('/run_pipeline_now', methods=['POST'])
def run_pipeline_now():
    scheduler.add_job(scheduled_pipeline, id='manual_run', replace_existing=True)
    return jsonify({"status": "success", "message": "Pipeline run started in background."})

@app.route('/run_sync', methods=['POST'])
def run_sync():
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
            "vibe_threshold": float(request.form.get('vibe_threshold', 6.5)),
            "auto_approve_threshold": float(request.form.get('auto_approve_threshold', 9.0)),
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

    ctx = get_full_dashboard_context(active_tab='settings', view='pending')
    return render_template('index.html', **ctx)

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

@app.route('/add_venue_manually', methods=['POST'])
def add_venue_manually():
    import uuid
    import threading
    name = request.form.get('name')
    city = request.form.get('city')
    website = request.form.get('website', '')
    notes = request.form.get('notes', '')

    if not name or not city:
        return jsonify({"error": "Name and City are required"}), 400

    v_id = str(uuid.uuid4())
    v_data = {
        'id': v_id,
        'name': name,
        'city': city,
        'website': website,
        'raw_about_text': notes,
        'source': 'manual',
        'discovery_genre': (config_mgr.get("target_genres") or ["psytrance"])[0]
    }

    db.add_venue(v_data)

    def run_pipeline_for_manual_venue():
        from main import qualify_and_pitch
        from src.geocoding import GeocodingUtility
        from src.outreach_predictor import OutreachPredictor
        geocoder = GeocodingUtility()
        predictor = OutreachPredictor(db)
        qualify_and_pitch(v_data, v_id, db, ai, geocoder, predictor, config_mgr, analytics)

    t = threading.Thread(target=run_pipeline_for_manual_venue)
    t.start()

    return redirect(url_for('index'))

@app.route("/add_source", methods=["POST"])
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

    db.update_lead_status(lead_id, 'APPROVED', pitch=pitch)
    if artist_id:
        with db._get_connection() as conn:
            conn.execute("UPDATE outreach_leads SET artist_id = ? WHERE id = ?", (artist_id, lead_id))

    lead = db.get_lead(lead_id)
    primary_genre = (config_mgr.get("target_genres") or ["psytrance"])[0]

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

@app.route('/bulk_action', methods=['POST'])
def bulk_action():
    """Perform batch approvals, rejections, or requalifications asynchronously."""
    import threading
    action = request.form.get('action')
    lead_ids = request.form.getlist('lead_ids[]')

    if not lead_ids and request.is_json:
        action = request.json.get('action')
        lead_ids = request.json.get('lead_ids', [])

    if not action or not lead_ids:
        if request.is_json:
            return jsonify({"error": "Missing action or lead IDs"}), 400
        return redirect(request.referrer or url_for('index'))

    lead_ids = [int(i) for i in lead_ids if str(i).isdigit()]

    def process_batch(ids, act):
        primary_genre = (config_mgr.get("target_genres") or ["psytrance"])[0]
        for lid in ids:
            try:
                if act == 'approve':
                    lead = db.get_lead(lid)
                    if not lead: continue
                    pitch = lead.get('generated_pitch')
                    if not pitch:
                        venue = db.get_venue(lead['venue_id'])
                        notes = db.get_venue_notes(lead['venue_id'])
                        pitch = ai.generate_pitch(
                            venue['name'],
                            lead['qualification_justification'],
                            epk_link=config_mgr.get("epk_link"),
                            mix_link=config_mgr.get("mix_link"),
                            traits=venue.get('extracted_traits'),
                            media_library=config_mgr.get("media_library"),
                            genre=primary_genre,
                            notes=notes
                        )
                    db.update_lead_status(lid, 'APPROVED', pitch=pitch)
                    query = "SELECT email FROM venue_contacts WHERE venue_id = ?"
                    with db._get_connection() as conn:
                        cursor = conn.execute(query, (lead['venue_id'],))
                        contact = cursor.fetchone()
                    if contact and contact[0]:
                        email = contact[0].split(',')[0].strip()
                        subject = f"Proposal for {primary_genre.capitalize()} Night Residency"
                        if mailer.send_email(email, subject, pitch):
                            db.update_lead_status(lid, 'SENT')
                elif act == 'reject':
                    db.update_lead_status(lid, 'REJECTED')
                elif act == 'requalify':
                    lead = db.get_lead(lid)
                    if not lead: continue
                    venue = db.get_venue(lead['venue_id'])
                    if not venue: continue
                    vibe_res = ai.vibe_check(
                        venue['name'],
                        venue.get('raw_about_text', ''),
                        genre=lead.get('qualified_genre', primary_genre),
                        rating=venue.get('google_rating')
                    )
                    vibe_thresh = float(config_mgr.get("vibe_threshold") or 6.5)
                    new_st = 'PENDING_REVIEW' if vibe_res['vibe_score'] >= vibe_thresh else 'PENDING_QUALIFICATION'
                    q = "UPDATE outreach_leads SET vibe_score = ?, qualification_justification = ?, pipeline_status = ? WHERE id = ?"
                    with db._get_connection() as conn:
                        conn.execute(q, (vibe_res['vibe_score'], vibe_res['justification'], new_st, lid))
            except Exception as e:
                db.log_system_event("DASHBOARD_BULK", "ERROR", f"Error processing lead {lid}: {e}")

    thread = threading.Thread(target=process_batch, args=(lead_ids, action))
    thread.daemon = True
    thread.start()

    if request.is_json:
        return jsonify({"status": "processing", "count": len(lead_ids), "action": action})
    return redirect(request.referrer or url_for('index'))

@app.route('/send_reply/<int:reply_id>', methods=['POST'])
def send_reply(reply_id):
    reply_content = request.form.get('reply_content')

    with db._get_connection() as conn:
        conn.row_factory = sqlite3.Row
        reply = conn.execute("SELECT * FROM lead_replies WHERE id = ?", (reply_id,)).fetchone()
        if not reply: return "Reply not found", 404

        lead = db.get_lead(reply['lead_id'])
        venue = db.get_venue(lead['venue_id'])

        cursor = conn.execute("SELECT email FROM venue_contacts WHERE venue_id = ?", (venue['id'],))
        contact = cursor.fetchone()

    if contact and contact[0]:
        email = contact[0].split(',')[0].strip()
        subject = f"Re: Proposal for Psytrance Night Residency - {venue['name']}"
        if mailer.send_email(email, subject, reply_content):
            db.log_system_event("OUTREACH", "SUCCESS", f"Sent manual reply to {email} for lead {lead['id']}")
            db.mark_reply_handled(reply_id)
            return redirect(url_for('history'))

    return "Error sending reply", 500

@app.route('/dismiss_reply/<int:reply_id>', methods=['POST'])
def dismiss_reply(reply_id):
    is_unmatched = request.args.get('unmatched', 'false').lower() == 'true'
    db.mark_reply_handled(reply_id, is_unmatched=is_unmatched)
    return jsonify({"status": "success"})

@app.route('/compare_venues', methods=['POST'])
def compare_venues():
    """Retrieve side-by-side comparative metadata for specified venue IDs."""
    venue_ids = request.json.get('venue_ids', []) if request.is_json else request.form.getlist('venue_ids[]')
    if not venue_ids:
        return jsonify({"error": "No venue IDs provided"}), 400

    results = []
    for vid in venue_ids[:5]:
        v = db.get_venue(vid)
        if not v:
            continue
        traits = {}
        if v.get('extracted_traits'):
            try:
                traits = json.loads(v['extracted_traits'])
            except:
                traits = {}
        lead = db.get_lead_by_venue_id(vid)
        results.append({
            "id": v['id'],
            "name": v['name'],
            "city": v['city'],
            "website": v.get('website'),
            "google_rating": v.get('google_rating'),
            "venue_type": v.get('venue_type') or 'Club / Event Space',
            "capacity": v.get('capacity') or 'N/A',
            "neighborhood": v.get('neighborhood') or 'N/A',
            "vibe_score": lead.get('vibe_score') if lead else None,
            "pipeline_status": lead.get('pipeline_status') if lead else 'UNCONTACTED',
            "success_probability": lead.get('success_probability') if lead else None,
            "traits": traits
        })

    return jsonify({"venues": results})

@app.route('/preview_digest', methods=['GET'])
def preview_digest():
    """Generates an HTML preview of the pipeline activity digest."""
    from src.digest_generator import DigestGenerator
    days = request.args.get('days', default=7, type=int)
    generator = DigestGenerator(db_path=db.db_path)
    metrics = generator.collect_metrics(days=days)
    return generator.render_html_digest(metrics)

@app.route('/send_digest', methods=['POST'])
def send_digest():
    """Triggers dispatch of the pipeline activity digest via email."""
    from src.digest_generator import DigestGenerator
    data = request.get_json(silent=True) or {}
    recipient = data.get('recipient_email')
    days = int(data.get('days', 7))

    generator = DigestGenerator(db_path=db.db_path, mailer=mailer)
    result = generator.dispatch_digest(recipient_email=recipient, days=days)
    return jsonify(result)

@app.route('/requalify/<int:lead_id>', methods=['POST'])
def requalify(lead_id):
    lead = db.get_lead(lead_id)
    if not lead: return jsonify({"error": "Lead not found"}), 404
    venue = db.get_venue(lead['venue_id'])
    if not venue: return jsonify({"error": "Venue not found"}), 404

    primary_genre = (config_mgr.get("target_genres") or ["psytrance"])[0]

    vibe_result = ai.vibe_check(
        venue['name'],
        venue.get('raw_about_text', ''),
        genre=lead.get('qualified_genre', primary_genre),
        rating=venue.get('google_rating')
    )

    vibe_threshold = float(config_mgr.get("vibe_threshold") or 6.5)
    new_status = 'PENDING_REVIEW' if float(vibe_result.get('vibe_score', 0)) >= vibe_threshold else 'PENDING_QUALIFICATION'

    pitch = lead['generated_pitch']
    if new_status == 'PENDING_REVIEW' and not pitch:
        traits = venue.get('extracted_traits', '{}')
        notes = db.get_venue_notes(venue['id'])
        pitch = ai.generate_pitch(
            venue['name'],
            vibe_result['justification'],
            epk_link=config_mgr.get("epk_link"),
            mix_link=config_mgr.get("mix_link"),
            traits=traits,
            media_library=config_mgr.get("media_library"),
            genre=lead.get('qualified_genre', primary_genre),
            notes=notes
        )

    query = "UPDATE outreach_leads SET vibe_score = ?, qualification_justification = ?, pipeline_status = ?, generated_pitch = ? WHERE id = ?"
    with db._get_connection() as conn:
        conn.execute(query, (vibe_result['vibe_score'], vibe_result['justification'], new_status, pitch, lead_id))

    return jsonify({"status": "success", "new_score": vibe_result['vibe_score'], "new_status": new_status})

@app.route('/regenerate/<int:lead_id>', methods=['POST'])
def regenerate(lead_id):
    lead = db.get_lead(lead_id)
    if not lead: return jsonify({"error": "Lead not found"}), 404
    venue = db.get_venue(lead['venue_id'])
    if not venue: return jsonify({"error": "Venue not found"}), 404

    artist_id = request.json.get('artist_id') if request.is_json else request.form.get('artist_id')

    primary_genre = (config_mgr.get("target_genres") or ["psytrance"])[0]
    notes = db.get_venue_notes(venue['id'])
    new_pitch = ai.generate_pitch(
        venue['name'],
        lead['qualification_justification'],
        epk_link=config_mgr.get("epk_link"),
        mix_link=config_mgr.get("mix_link"),
        traits=venue.get('extracted_traits'),
        media_library=config_mgr.get("media_library"),
        genre=primary_genre,
        artist_id=artist_id,
        notes=notes
    )
    return jsonify({"pitch": new_pitch})

@app.route('/calculate_ab_significance')
def calculate_ab_significance():
    stats = analytics.get_variant_stats()

    if len(stats) < 2:
        return jsonify({"error": "Need at least two variants with data to calculate significance."})

    sorted_variants = sorted(stats.items(), key=lambda item: item[1]['conversion_rate'], reverse=True)
    var_a = sorted_variants[0]
    var_b = sorted_variants[1]

    success_a = var_a[1]['interested']
    total_a = var_a[1]['sent']
    success_b = var_b[1]['interested']
    total_b = var_b[1]['sent']

    if total_a == 0 or total_b == 0:
        return jsonify({"error": "Insufficient pitch data sent to calculate significance."})

    p1 = success_a / total_a
    p2 = success_b / total_b
    p_pool = (success_a + success_b) / (total_a + total_b)

    if p_pool == 0 or p_pool == 1:
        return jsonify({
            "is_significant": False,
            "p_value": 1.0,
            "chi2": 0.0,
            "variant_a": var_a[0],
            "variant_b": var_b[0]
        })

    chi2 = ((p1 - p2)**2) / (p_pool * (1 - p_pool) * ((1/total_a) + (1/total_b)))
    is_significant = chi2 > 3.84

    p_value = 1.0
    if chi2 > 6.63: p_value = 0.01
    elif chi2 > 3.84: p_value = 0.05
    elif chi2 > 2.71: p_value = 0.10
    else: p_value = 0.50

    return jsonify({
        "is_significant": is_significant,
        "chi2": chi2,
        "p_value": p_value,
        "variant_a": var_a[0],
        "variant_b": var_b[0]
    })

@app.route('/dm_queue')
def dm_queue():
    ctx = get_full_dashboard_context(active_tab='pipeline', view='dm_queue')
    return render_template('index.html', **ctx)

@app.route('/pending_follow_ups')
def pending_follow_ups():
    ctx = get_full_dashboard_context(active_tab='pipeline', view='pending_follow_ups')
    return render_template('index.html', **ctx)

@app.route('/approve_follow_up/<int:lead_id>', methods=['POST'])
def approve_follow_up(lead_id):
    db.update_lead_status(lead_id, 'FOLLOW_UP_APPROVED')
    return redirect(url_for('pending_follow_ups'))

@app.route('/shutdown', methods=['POST'])
def shutdown_server():
    """Graceful shutdown endpoint utilized by tray companion or operator."""
    print("Initiating graceful application shutdown...")
    if scheduler.running:
        scheduler.shutdown(wait=False)

    # Only kill process if not running under pytest / test client
    if not app.config.get('TESTING'):
        def term_proc():
            import time
            time.sleep(0.5)
            os.kill(os.getpid(), signal.SIGTERM)

        import threading
        threading.Thread(target=term_proc, daemon=True).start()
    return jsonify({"status": "success", "message": "Server shutting down."})

if __name__ == '__main__':
    scheduler.add_job(scheduled_pipeline, 'interval', weeks=1, id='weekly_pipeline')
    scheduler.start()
    app.run(debug=True, port=5000)
