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
        status_bg     = "#ecfdf5"
        status_text   = "#065f46"
        status_dot    = "#10b981"
        status_label  = "Hot Lead"
    elif status.lower() in ["cold lead", "cold"]:
        status_bg     = "#fef2f2"
        status_text   = "#991b1b"
        status_dot    = "#ef4444"
        status_label  = "Cold Lead"
    else:
        status_bg     = "#f8fafc"
        status_text   = "#475569"
        status_dot    = "#94a3b8"
        status_label  = "Pending"

    phone          = lead_data["phone_number"]
    lead_id        = lead_data["lead_id"]
    whatsapp_link  = f"https://wa.me/972{phone[1:]}"
    dashboard_link = f"{DASHBOARD_URL}?lead={lead_id}"
    initials       = "".join([w[0] for w in lead_data["name"].split()][:2]).upper()
    score          = int(lead_data["total_score"])
    score_pct      = min(score * 10, 100)

    content = f"""
<div style="font-family:-apple-system,'Segoe UI',Helvetica,sans-serif;background:#f1f5f9;padding:40px 20px;min-height:100vh;">
<div style="max-width:500px;margin:0 auto;">

  <div style="margin-bottom:6px;">
    <span style="font-size:11px;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:#94a3b8;">Lead Qualification System</span>
  </div>
  <h1 style="margin:0 0 28px;font-size:26px;font-weight:700;color:#0f172a;letter-spacing:-0.5px;">New lead received</h1>

  <div style="background:#ffffff;border-radius:20px;overflow:hidden;border:1px solid #e2e8f0;">

    <div style="padding:14px 24px;background:#f8fafc;border-bottom:1px solid #e2e8f0;display:flex;align-items:center;gap:8px;">
      <div style="width:8px;height:8px;border-radius:50%;background:{status_dot};flex-shrink:0;"></div>
      <span style="font-size:13px;font-weight:600;color:{status_text};">{status_label}</span>
    </div>

    <div style="padding:20px 24px;border-bottom:1px solid #f1f5f9;display:flex;align-items:center;gap:14px;">
      <div style="width:42px;height:42px;border-radius:50%;background:#ede9fe;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:700;color:#5b21b6;flex-shrink:0;">{initials}</div>
      <div>
        <div style="font-size:11px;color:#94a3b8;margin-bottom:3px;font-weight:500;">Name</div>
        <div style="font-size:17px;font-weight:700;color:#0f172a;">{lead_data["name"]}</div>
      </div>
    </div>

    <div style="display:flex;border-bottom:1px solid #f1f5f9;">
      <div style="flex:1;padding:18px 24px;border-right:1px solid #f1f5f9;">
        <div style="font-size:11px;color:#94a3b8;margin-bottom:4px;font-weight:500;">Phone</div>
        <div style="font-size:15px;font-weight:600;color:#0f172a;font-family:monospace;">{phone}</div>
      </div>
      <div style="flex:1;padding:18px 24px;">
        <div style="font-size:11px;color:#94a3b8;margin-bottom:4px;font-weight:500;">Score</div>
        <div style="display:flex;align-items:center;gap:10px;">
          <span style="font-size:22px;font-weight:800;color:#10b981;">{score}</span>
          <div style="flex:1;height:5px;background:#f1f5f9;border-radius:999px;overflow:hidden;max-width:56px;">
            <div style="width:{score_pct}%;height:100%;background:#10b981;border-radius:999px;"></div>
          </div>
        </div>
      </div>
    </div>

    <div style="padding:18px 24px;border-bottom:1px solid #f1f5f9;">
      <div style="font-size:11px;color:#94a3b8;margin-bottom:4px;font-weight:500;">Goal</div>
      <div style="font-size:15px;font-weight:600;color:#0f172a;">{lead_data["goal_user"]}</div>
    </div>

    <div style="padding:18px 24px;border-bottom:1px solid #f1f5f9;">
      <div style="font-size:11px;color:#94a3b8;margin-bottom:4px;font-weight:500;">Timeline</div>
      <div style="display:flex;align-items:center;gap:7px;">
        <div style="width:7px;height:7px;border-radius:50%;background:#f59e0b;flex-shrink:0;"></div>
        <div style="font-size:15px;font-weight:600;color:#0f172a;">{lead_data["urgency_user"]}</div>
      </div>
    </div>

    <div style="padding:20px 24px;display:flex;flex-direction:column;gap:10px;">
      <a href="{dashboard_link}"
         style="display:block;text-align:center;background:#0f172a;color:#ffffff;text-decoration:none;padding:15px;border-radius:12px;font-size:14px;font-weight:600;letter-spacing:0.01em;">
        View in Dashboard
      </a>
      <a href="{whatsapp_link}"
         style="display:block;text-align:center;background:#22c55e;color:#ffffff;text-decoration:none;padding:15px;border-radius:12px;font-size:14px;font-weight:600;letter-spacing:0.01em;">
        Message on WhatsApp
      </a>
    </div>

  </div>

  <p style="margin:20px 0 0;font-size:12px;color:#94a3b8;text-align:center;">
    Sent automatically &middot; Lead Qualification System
  </p>

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





