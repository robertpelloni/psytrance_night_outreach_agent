from flask import Flask, render_template, request, redirect, url_for, jsonify
import sys
import os

# Add the parent directory to sys.path to allow absolute imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.db_manager import DatabaseManager
from src.ai_engine import AIEngine
from src.mailer import Mailer

app = Flask(__name__)
# Adjust path because we are running from project root or src/dashboard
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../database/outreach.db'))
db = DatabaseManager(db_path=db_path)
ai = AIEngine()
mailer = Mailer()

@app.route('/')
def index():
    leads = db.get_pending_leads()
    return render_template('index.html', leads=leads, view='pending')

@app.route('/history')
def history():
    leads = db.get_lead_history()
    return render_template('index.html', leads=leads, view='history')

@app.route('/approve/<int:lead_id>', methods=['POST'])
def approve(lead_id):
    pitch = request.form.get('pitch')

    # 1. Update status in DB
    db.update_lead_status(lead_id, 'APPROVED', pitch=pitch)

    # 2. Find contact email
    lead = db.get_lead(lead_id)
    query = "SELECT email FROM venue_contacts WHERE venue_id = ?"
    with db._get_connection() as conn:
        cursor = conn.execute(query, (lead['venue_id'],))
        contact = cursor.fetchone()

    if contact and contact[0]:
        email = contact[0].split(',')[0].strip() # Get first email
        subject = "Proposal for Psytrance Night Residency"
        if mailer.send_email(email, subject, pitch):
            db.update_lead_status(lead_id, 'SENT')

    print(f"Lead {lead_id} approved. Pitch: {pitch[:50]}...")
    return redirect(url_for('index'))

@app.route('/reject/<int:lead_id>', methods=['POST'])
def reject(lead_id):
    db.update_lead_status(lead_id, 'REJECTED')
    return redirect(url_for('index'))

@app.route('/regenerate/<int:lead_id>', methods=['POST'])
def regenerate(lead_id):
    lead = db.get_lead(lead_id)
    if not lead:
        return jsonify({"error": "Lead not found"}), 404

    venue = db.get_venue(lead['venue_id'])
    if not venue:
        return jsonify({"error": "Venue not found"}), 404

    new_pitch = ai.generate_pitch(venue['name'], lead['qualification_justification'])
    return jsonify({"pitch": new_pitch})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
