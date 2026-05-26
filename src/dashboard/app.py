from flask import Flask, render_template, request, redirect, url_for, jsonify
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

@app.route('/')
def index():
    leads = db.get_pending_leads()
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
    return render_template('analytics.html', stats=stats, approval_rate=approval_rate)

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

    return render_template('system.html', stats=stats, version=version, git_info=git_info, sync_logs=sync_logs)

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
    query = "SELECT email FROM venue_contacts WHERE venue_id = ?"
    with db._get_connection() as conn:
        cursor = conn.execute(query, (lead['venue_id'],))
        contact = cursor.fetchone()
    if contact and contact[0]:
        email = contact[0].split(',')[0].strip()
        subject = "Proposal for Psytrance Night Residency"
        if mailer.send_email(email, subject, pitch):
            db.update_lead_status(lead_id, 'SENT')
    return redirect(url_for('index'))

@app.route('/reject/<int:lead_id>', methods=['POST'])
def reject(lead_id):
    db.update_lead_status(lead_id, 'REJECTED')
    return redirect(url_for('index'))

@app.route('/regenerate/<int:lead_id>', methods=['POST'])
def regenerate(lead_id):
    lead = db.get_lead(lead_id)
    if not lead: return jsonify({"error": "Lead not found"}), 404
    venue = db.get_venue(lead['venue_id'])
    if not venue: return jsonify({"error": "Venue not found"}), 404

    new_pitch = ai.generate_pitch(
        venue['name'],
        lead['qualification_justification'],
        epk_link=config_mgr.get("epk_link"),
        mix_link=config_mgr.get("mix_link")
    )
    return jsonify({"pitch": new_pitch})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
