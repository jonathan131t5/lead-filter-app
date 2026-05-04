import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("SENDGRID_API_KEY")

DASHBOARD_URL = "https://lead-filter-app.onrender.com/dashboard"


def send_email(lead_data):
    status = lead_data["final_status"]

    if status.lower() in ["hot lead", "hot"]:
        status_dot   = "#10b981"
        status_bg    = "rgba(16,185,129,0.12)"
        status_border= "rgba(16,185,129,0.25)"
        status_text  = "#10b981"
        status_label = "Hot Lead"
    elif status.lower() in ["cold lead", "cold"]:
        status_dot   = "#ef4444"
        status_bg    = "rgba(239,68,68,0.12)"
        status_border= "rgba(239,68,68,0.25)"
        status_text  = "#ef4444"
        status_label = "Cold Lead"
    else:
        status_dot   = "#94a3b8"
        status_bg    = "rgba(148,163,184,0.12)"
        status_border= "rgba(148,163,184,0.25)"
        status_text  = "#94a3b8"
        status_label = "Pending"

    phone          = lead_data["phone_number"]
    lead_id        = lead_data["lead_id"]
    whatsapp_link  = f"https://wa.me/972{phone[1:]}"
    dashboard_link = f"{DASHBOARD_URL}?lead={lead_id}"
    initials       = "".join([w[0] for w in lead_data["name"].split()][:2]).upper()
    score          = int(lead_data["total_score"])
    score_pct      = min(score * 10, 100)

    content = f"""
<div style="font-family:-apple-system,'Segoe UI',Helvetica,sans-serif;background:#e8eaf0;padding:40px 20px;">
<div style="max-width:480px;margin:0 auto;">
<div style="background:#0f172a;border-radius:24px;overflow:hidden;">

  <div style="padding:32px 32px 28px;border-bottom:1px solid rgba(255,255,255,0.07);">
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px;">
      <div style="width:6px;height:6px;border-radius:50%;background:#22c55e;"></div>
      <span style="font-size:10px;font-weight:600;letter-spacing:0.12em;text-transform:uppercase;color:#475569;">Lead Qualification System</span>
    </div>
    <div style="font-size:24px;font-weight:700;color:#f8fafc;letter-spacing:-0.5px;margin-bottom:4px;">New lead received</div>
    <div style="font-size:13px;color:#475569;">A new inquiry was submitted through your lead filter.</div>
  </div>

  <div style="padding:24px 32px;border-bottom:1px solid rgba(255,255,255,0.06);">
    <div style="display:flex;align-items:center;justify-content:space-between;">
      <div style="display:flex;align-items:center;gap:12px;">
        <div style="width:44px;height:44px;border-radius:50%;background:linear-gradient(135deg,#7c3aed,#4f46e5);display:flex;align-items:center;justify-content:center;font-size:15px;font-weight:700;color:#fff;">{initials}</div>
        <div>
          <div style="font-size:16px;font-weight:700;color:#f1f5f9;">{lead_data["name"]}</div>
          <div style="font-size:12px;color:#64748b;margin-top:2px;font-family:monospace;">{phone}</div>
        </div>
      </div>
      <div style="background:{status_bg};border:1px solid {status_border};padding:6px 14px;border-radius:999px;display:flex;align-items:center;gap:6px;">
        <div style="width:6px;height:6px;border-radius:50%;background:{status_dot};"></div>
        <span style="font-size:12px;font-weight:600;color:{status_text};">{status_label}</span>
      </div>
    </div>
  </div>

  <div style="display:flex;border-bottom:1px solid rgba(255,255,255,0.06);">
    <div style="flex:1;padding:20px 32px;border-right:1px solid rgba(255,255,255,0.06);">
      <div style="font-size:10px;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;color:#475569;margin-bottom:8px;">Score</div>
      <div style="font-size:32px;font-weight:800;color:#10b981;line-height:1;">{score}</div>
      <div style="margin-top:10px;height:3px;background:rgba(255,255,255,0.07);border-radius:999px;overflow:hidden;">
        <div style="width:{score_pct}%;height:100%;background:#10b981;border-radius:999px;"></div>
      </div>
    </div>
    <div style="flex:1;padding:20px 32px;">
      <div style="font-size:10px;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;color:#475569;margin-bottom:8px;">Timeline</div>
      <div style="display:flex;align-items:center;gap:6px;">
        <div style="width:6px;height:6px;border-radius:50%;background:#f59e0b;flex-shrink:0;"></div>
        <span style="font-size:14px;font-weight:600;color:#f1f5f9;">{lead_data["urgency_user"]}</span>
      </div>
    </div>
  </div>

  <div style="padding:20px 32px;border-bottom:1px solid rgba(255,255,255,0.06);">
    <div style="font-size:10px;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;color:#475569;margin-bottom:8px;">Goal</div>
    <div style="font-size:15px;font-weight:600;color:#f1f5f9;">{lead_data["goal_user"]}</div>
  </div>

  <div style="padding:24px 32px;display:flex;flex-direction:column;gap:10px;">
    <a href="{dashboard_link}" style="display:block;text-align:center;background:#f8fafc;color:#0f172a;text-decoration:none;padding:16px;border-radius:14px;font-size:14px;font-weight:700;">
      View in Dashboard →
    </a>
    <a href="{whatsapp_link}" style="display:block;text-align:center;background:#16a34a;color:#fff;text-decoration:none;padding:16px;border-radius:14px;font-size:14px;font-weight:700;">
      Message on WhatsApp
    </a>
  </div>

  <div style="padding:16px 32px;border-top:1px solid rgba(255,255,255,0.05);">
    <div style="font-size:11px;color:#334155;text-align:center;">Sent automatically · Lead Qualification System</div>
  </div>

</div>
</div>
</div>
    """

    message = Mail(
        from_email="jona.wexler@gmail.com",
        to_emails="jona.wexler@gmail.com",
        subject=f"New Lead — {status_label} · {lead_data['name']}",
        html_content=content,
    )

    sg = SendGridAPIClient(api_key)
    response = sg.send(message)

    return response.status_code