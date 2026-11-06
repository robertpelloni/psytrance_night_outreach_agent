import sqlite3
import os
import json
from datetime import datetime, timedelta
from src.mailer import Mailer

class DigestGenerator:
    """
    Aggregates periodic pipeline activity, response metrics, and token usage,
    and formats/dispatches email summaries for collective managers.
    """
    def __init__(self, db_path=None, config_path='database/config.json', mailer=None):
        self.db_path = db_path or os.getenv("DB_PATH") or 'database/outreach.db'
        self.config_path = config_path
        self.mailer = mailer or Mailer()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _get_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def collect_metrics(self, days=7):
        """
        Gathers outreach and pipeline metrics for the past `days`.
        """
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        metrics = {
            "period_days": days,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "cutoff": cutoff,
            "new_venues_discovered": 0,
            "leads_qualified": 0,
            "pitches_sent": 0,
            "replies_received": 0,
            "replies_by_sentiment": {},
            "total_booked": 0,
            "tokens_consumed": 0,
            "attention_required": 0,
            "unmatched_replies": 0,
            "recent_replies": []
        }

        with self._get_connection() as conn:
            # 1. Venues & leads
            try:
                # Count venues
                res = conn.execute("SELECT count(*) FROM venues").fetchone()
                metrics["total_venues"] = res[0] if res else 0

                # Count qualified leads generated in period
                res = conn.execute(
                    "SELECT count(*) FROM outreach_leads WHERE created_at >= ?", (cutoff,)
                ).fetchone()
                metrics["leads_qualified"] = res[0] if res else 0

                # Count pitches sent in period
                res = conn.execute(
                    "SELECT count(*) FROM outreach_leads WHERE pipeline_status IN ('SENT', 'BOOKED', 'LOST') AND last_outreach_at >= ?",
                    (cutoff,)
                ).fetchone()
                metrics["pitches_sent"] = res[0] if res else 0

                # Total booked
                res = conn.execute(
                    "SELECT count(*) FROM outreach_leads WHERE pipeline_status = 'BOOKED'"
                ).fetchone()
                metrics["total_booked"] = res[0] if res else 0
            except sqlite3.OperationalError:
                pass

            # 2. Inbound replies
            try:
                res = conn.execute(
                    "SELECT count(*) FROM lead_replies WHERE received_at >= ?", (cutoff,)
                ).fetchone()
                metrics["replies_received"] = res[0] if res else 0

                sentiment_rows = conn.execute(
                    "SELECT sentiment, count(*) as count FROM lead_replies WHERE received_at >= ? GROUP BY sentiment",
                    (cutoff,)
                ).fetchall()
                for row in sentiment_rows:
                    metrics["replies_by_sentiment"][row["sentiment"] or "UNKNOWN"] = row["count"]

                recent = conn.execute(
                    """
                    SELECT r.id, r.sentiment, r.content, r.received_at, v.name as venue_name
                    FROM lead_replies r
                    LEFT JOIN outreach_leads l ON r.lead_id = l.id
                    LEFT JOIN venues v ON l.venue_id = v.id
                    WHERE r.received_at >= ?
                    ORDER BY r.received_at DESC LIMIT 5
                    """,
                    (cutoff,)
                ).fetchall()
                metrics["recent_replies"] = [dict(r) for r in recent]
            except sqlite3.OperationalError:
                pass

            # 3. AI Token consumption
            try:
                res = conn.execute(
                    "SELECT sum(total_tokens) FROM ai_usage WHERE timestamp >= ?", (cutoff,)
                ).fetchone()
                metrics["tokens_consumed"] = res[0] if res and res[0] else 0
            except sqlite3.OperationalError:
                pass

            # 4. Attention items
            try:
                att_res = conn.execute(
                    "SELECT count(*) FROM lead_replies WHERE requires_attention = 1"
                ).fetchone()
                metrics["attention_required"] = att_res[0] if att_res else 0

                unm_res = conn.execute("SELECT count(*) FROM unmatched_replies").fetchone()
                metrics["unmatched_replies"] = unm_res[0] if unm_res else 0
            except sqlite3.OperationalError:
                pass

        return metrics

    def render_text_digest(self, metrics):
        """Formats the metrics into a clean plain text report."""
        period_str = f"Past {metrics.get('period_days', 7)} Days"
        sentiment_summary = ", ".join(
            f"{k}: {v}" for k, v in metrics.get("replies_by_sentiment", {}).items()
        ) or "None"

        text = [
            f"=== Psytrance Night Outreach Pipeline Digest ({period_str}) ===",
            f"Report Generated: {metrics.get('generated_at')}",
            "",
            "📊 Activity Overview:",
            f" • New Leads Qualified: {metrics.get('leads_qualified', 0)}",
            f" • Pitches Dispatched: {metrics.get('pitches_sent', 0)}",
            f" • Replies Received: {metrics.get('replies_received', 0)}",
            f" • Reply Breakdown: {sentiment_summary}",
            f" • Total Booked Venues: {metrics.get('total_booked', 0)}",
            f" • AI Tokens Consumed: {metrics.get('tokens_consumed', 0):,}",
            "",
            "⚠️ Attention Required:",
            f" • Unhandled Replies: {metrics.get('attention_required', 0)}",
            f" • Unmatched Messages: {metrics.get('unmatched_replies', 0)}",
            ""
        ]

        if metrics.get("recent_replies"):
            text.append("💬 Recent Inbound Messages:")
            for r in metrics["recent_replies"]:
                snippet = (r.get("content") or "").replace("\n", " ")[:80]
                text.append(f" • [{r.get('sentiment')}] {r.get('venue_name', 'Unknown')}: \"{snippet}...\"")
            text.append("")

        text.append("Access the command dashboard for full HITL approval and reply dispatch.")
        return "\n".join(text)

    def render_html_digest(self, metrics):
        """Formats the metrics into a styled HTML email."""
        period_str = f"Past {metrics.get('period_days', 7)} Days"
        sentiments = metrics.get("replies_by_sentiment", {})
        sentiment_badges = "".join(
            f"<span style='background:#343a40;color:#f8f9fa;padding:4px 8px;border-radius:4px;margin-right:6px;font-size:12px;'><strong>{k}:</strong> {v}</span>"
            for k, v in sentiments.items()
        ) or "<span style='color:#6c757d;'>No replies received</span>"

        replies_html = ""
        if metrics.get("recent_replies"):
            rows = ""
            for r in metrics["recent_replies"]:
                snippet = (r.get("content") or "").replace("\n", " ")[:100]
                rows += f"""
                <tr style='border-bottom:1px solid #dee2e6;'>
                    <td style='padding:8px;font-weight:bold;'>{r.get('venue_name', 'Unknown')}</td>
                    <td style='padding:8px;'><span style='background:#0d6efd;color:white;padding:2px 6px;border-radius:3px;font-size:11px;'>{r.get('sentiment')}</span></td>
                    <td style='padding:8px;color:#495057;'>{snippet}...</td>
                </tr>
                """
            replies_html = f"""
            <h3 style='color:#212529;margin-top:24px;'>💬 Recent Inbound Replies</h3>
            <table style='width:100%;border-collapse:collapse;font-size:13px;text-align:left;'>
                <thead>
                    <tr style='background:#e9ecef;'>
                        <th style='padding:8px;'>Venue</th>
                        <th style='padding:8px;'>Sentiment</th>
                        <th style='padding:8px;'>Excerpt</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
            """

        html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Pipeline Digest</title>
</head>
<body style='font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;line-height:1.5;color:#212529;background-color:#f4f6f9;margin:0;padding:20px;'>
  <div style='max-width:650px;margin:0 auto;background:#ffffff;border-radius:8px;overflow:hidden;border:1px solid #dee2e6;'>
    <div style='background:linear-gradient(135deg, #1f2937, #111827);color:#ffffff;padding:20px 24px;'>
      <h2 style='margin:0 0 6px 0;font-size:22px;'>🌌 Psytrance Outreach Pipeline Digest</h2>
      <div style='font-size:13px;color:#9ca3af;'>Reporting Period: <strong>{period_str}</strong> &bull; Generated: {metrics.get('generated_at')}</div>
    </div>

    <div style='padding:24px;'>
      <div style='display:flex;gap:12px;margin-bottom:20px;flex-wrap:wrap;'>
        <div style='flex:1;min-width:120px;background:#f8f9fa;border:1px solid #e9ecef;border-radius:6px;padding:12px;text-align:center;'>
          <div style='font-size:11px;color:#6c757d;text-transform:uppercase;font-weight:600;'>Leads Qualified</div>
          <div style='font-size:22px;font-weight:bold;color:#0d6efd;'>{metrics.get('leads_qualified', 0)}</div>
        </div>
        <div style='flex:1;min-width:120px;background:#f8f9fa;border:1px solid #e9ecef;border-radius:6px;padding:12px;text-align:center;'>
          <div style='font-size:11px;color:#6c757d;text-transform:uppercase;font-weight:600;'>Pitches Sent</div>
          <div style='font-size:22px;font-weight:bold;color:#198754;'>{metrics.get('pitches_sent', 0)}</div>
        </div>
        <div style='flex:1;min-width:120px;background:#f8f9fa;border:1px solid #e9ecef;border-radius:6px;padding:12px;text-align:center;'>
          <div style='font-size:11px;color:#6c757d;text-transform:uppercase;font-weight:600;'>Replies</div>
          <div style='font-size:22px;font-weight:bold;color:#ffc107;'>{metrics.get('replies_received', 0)}</div>
        </div>
        <div style='flex:1;min-width:120px;background:#f8f9fa;border:1px solid #e9ecef;border-radius:6px;padding:12px;text-align:center;'>
          <div style='font-size:11px;color:#6c757d;text-transform:uppercase;font-weight:600;'>Booked</div>
          <div style='font-size:22px;font-weight:bold;color:#20c997;'>{metrics.get('total_booked', 0)}</div>
        </div>
      </div>

      <h3 style='color:#212529;margin-top:20px;font-size:16px;'>📊 Reply Sentiment Breakdown</h3>
      <div style='margin-bottom:16px;'>{sentiment_badges}</div>

      <div style='background:#f8f9fa;border-left:4px solid #fd7e14;padding:12px 16px;margin:20px 0;border-radius:0 4px 4px 0;'>
        <div style='font-weight:bold;font-size:14px;color:#212529;'>AI Operations & Attention Summary</div>
        <div style='font-size:13px;color:#495057;margin-top:4px;'>
          Tokens Consumed: <strong>{metrics.get('tokens_consumed', 0):,}</strong> &bull;
          Unhandled Replies: <strong>{metrics.get('attention_required', 0)}</strong> &bull;
          Unmatched Leads: <strong>{metrics.get('unmatched_replies', 0)}</strong>
        </div>
      </div>

      {replies_html}

      <div style='margin-top:28px;text-align:center;padding-top:16px;border-top:1px solid #dee2e6;'>
        <p style='font-size:13px;color:#6c757d;margin:0 0 12px 0;'>Review queued leads, AI counter-proposals, and multi-city circuits in your command center.</p>
      </div>
    </div>
  </div>
</body>
</html>
"""
        return html

    def dispatch_digest(self, recipient_email=None, days=7):
        """
        Gathers metrics, renders plain text and HTML reports, and dispatches via mailer.
        """
        metrics = self.collect_metrics(days=days)
        subject = f"Pipeline Digest ({days}-Day Summary) - {metrics['generated_at']}"
        body = self.render_text_digest(metrics)
        html_body = self.render_html_digest(metrics)

        target = recipient_email or os.getenv("DIGEST_RECIPIENT_EMAIL") or os.getenv("SENDER_EMAIL")
        if not target:
            target = "collective@psytrance.local"

        success = self.mailer.send_email(to_email=target, subject=subject, body=body)
        return {
            "success": success,
            "recipient": target,
            "subject": subject,
            "metrics": metrics
        }
