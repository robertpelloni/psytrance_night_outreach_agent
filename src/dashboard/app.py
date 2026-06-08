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

import json

@app.route('/')
def index():
    leads = db.get_pending_leads()
    for lead in leads:
        # success_probability is now fetched from the database in get_pending_leads
        lead['success_prob'] = lead.get('success_probability')

        if lead.get('extracted_traits'):
            try:
                lead['traits_dict'] = json.loads(lead['extracted_traits'])
            except:
                lead['traits_dict'] = {}
    return render_template('index.html', leads=leads, view='pending')

@app.route('/history')
def history():
    leads = db.get_lead_history()
    # Attach replies to each lead for the history view
    for lead in leads:
        lead['replies'] = db.get_lead_replies(lead['id'])
    return render_template('index.html', leads=leads, view='history')

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
    return render_template('analytics.html', stats=stats, approval_rate=approval_rate, variant_stats=variant_stats)

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

    sync_stats = reliability.get_sync_health_stats()
    stale_branches = reliability.get_stale_branches()
    audit_trail = db.get_version_audit_trail()

    return render_template('system.html', stats=stats, version=version, git_info=git_info, sync_logs=sync_logs, sync_stats=sync_stats, stale_branches=stale_branches, audit_trail=audit_trail)

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
        new_config = {
            "cities": [c.strip() for f in request.form.getlist('cities') for c in f.split(',')],
            "target_genres": [g.strip() for f in request.form.getlist('genres') for g in f.split(',')],
            "epk_link": request.form.get('epk_link'),
            "mix_link": request.form.get('mix_link'),
            "vibe_threshold": int(request.form.get('vibe_threshold', 7))
        }
        config_mgr.save_config(new_config)
        return redirect(url_for('settings'))

    current_config = config_mgr.load_config()
    return render_template('settings.html', config=current_config)

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
    db.update_lead_status(lead_id, 'APPROVED', pitch=pitch)
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
            return redirect(url_for('history'))

    return "Error sending reply", 500

@app.route('/regenerate/<int:lead_id>', methods=['POST'])
def regenerate(lead_id):
    lead = db.get_lead(lead_id)
    if not lead: return jsonify({"error": "Lead not found"}), 404
    venue = db.get_venue(lead['venue_id'])
    if not venue: return jsonify({"error": "Venue not found"}), 404

    primary_genre = (config_mgr.get("target_genres") or ["psytrance"])[0]
    new_pitch = ai.generate_pitch(
        venue['name'],
        lead['qualification_justification'],
        epk_link=config_mgr.get("epk_link"),
        mix_link=config_mgr.get("mix_link"),
        traits=venue.get('extracted_traits'),
        media_library=config_mgr.get("media_library"),
        genre=primary_genre
    )
    return jsonify({"pitch": new_pitch})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
