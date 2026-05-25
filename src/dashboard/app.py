from flask import Flask, render_template, request, redirect, url_for
import sys
import os

# Add the parent directory to sys.path to allow absolute imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.db_manager import DatabaseManager

app = Flask(__name__)
# Adjust path because we are running from project root or src/dashboard
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../database/outreach.db'))
db = DatabaseManager(db_path=db_path)

@app.route('/')
def index():
    leads = db.get_pending_leads()
    return render_template('index.html', leads=leads)

@app.route('/approve/<int:lead_id>', methods=['POST'])
def approve(lead_id):
    db.update_lead_status(lead_id, 'APPROVED')
    return redirect(url_for('index'))

@app.route('/reject/<int:lead_id>', methods=['POST'])
def reject(lead_id):
    db.update_lead_status(lead_id, 'REJECTED')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
