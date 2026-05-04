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
<div style="margin:0;padding:0;background:#f3f5f9;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif;">
  <div style="padding:36px 16px;">
    <div style="max-width:560px;margin:0 auto;background:#ffffff;border:1px solid #e6eaf0;border-radius:22px;overflow:hidden;box-shadow:0 18px 45px rgba(15,23,42,0.10);">

      <div style="padding:30px 32px 24px;background:#0b1220;">
        <div style="font-size:11px;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;color:#22c55e;margin-bottom:18px;">
          Lead Qualification System
        </div>

        <div style="font-size:26px;line-height:1.2;font-weight:800;color:#ffffff;letter-spacing:-0.6px;margin-bottom:8px;">
          New lead received
        </div>

        <div style="font-size:14px;line-height:1.5;color:#94a3b8;">
          A new inquiry was submitted through your lead filter.
        </div>
      </div>

      <div style="padding:28px 32px 24px;background:#ffffff;">
        <div style="display:flex;align-items:center;justify-content:space-between;gap:16px;">
          <div style="display:flex;align-items:center;gap:14px;">
            <div style="width:52px;height:52px;border-radius:16px;background:linear-gradient(135deg,#7c3aed,#2563eb);color:#ffffff;font-size:17px;font-weight:800;display:flex;align-items:center;justify-content:center;">
              {initials}
            </div>

            <div>
              <div style="font-size:18px;font-weight:800;color:#0f172a;line-height:1.2;">
                {lead_data["name"]}
              </div>
              <div style="font-size:13px;color:#64748b;margin-top:5px;">
                {phone}
              </div>
            </div>
          </div>

          <div style="white-space:nowrap;background:{status_bg};border:1px solid {status_border};color:{status_text};font-size:12px;font-weight:800;padding:8px 13px;border-radius:999px;">
            ● {status_label}
          </div>
        </div>
      </div>

      <div style="padding:0 32px 28px;background:#ffffff;">
        <div style="border:1px solid #e8edf4;border-radius:18px;overflow:hidden;background:#fbfcfe;">
          
          <div style="display:flex;">
            <div style="width:42%;padding:22px 22px;border-right:1px solid #e8edf4;">
              <div style="font-size:11px;font-weight:800;letter-spacing:0.10em;text-transform:uppercase;color:#94a3b8;margin-bottom:12px;">
                Score
              </div>
              <div style="font-size:42px;line-height:1;font-weight:900;color:#0f172a;letter-spacing:-1px;">
                {score}<span style="font-size:17px;color:#94a3b8;font-weight:800;">/10</span>
              </div>
              <div style="height:5px;background:#e2e8f0;border-radius:999px;margin-top:16px;overflow:hidden;">
                <div style="width:{score_pct}%;height:5px;background:#10b981;border-radius:999px;"></div>
              </div>
            </div>

            <div style="width:58%;padding:22px 22px;">
              <div style="font-size:11px;font-weight:800;letter-spacing:0.10em;text-transform:uppercase;color:#94a3b8;margin-bottom:12px;">
                Timeline
              </div>
              <div style="font-size:15px;line-height:1.5;font-weight:750;color:#0f172a;">
                <span style="color:#f59e0b;">●</span>
                {lead_data["urgency_user"]}
              </div>
            </div>
          </div>

          <div style="border-top:1px solid #e8edf4;padding:22px;">
            <div style="font-size:11px;font-weight:800;letter-spacing:0.10em;text-transform:uppercase;color:#94a3b8;margin-bottom:10px;">
              Goal
            </div>
            <div style="font-size:16px;line-height:1.55;font-weight:750;color:#0f172a;">
              {lead_data["goal_user"]}
            </div>
          </div>

        </div>
      </div>

      <div style="padding:0 32px 32px;background:#ffffff;">
        <a href="{whatsapp_link}" style="display:block;background:#16a34a;color:#ffffff;text-decoration:none;text-align:center;padding:16px 18px;border-radius:14px;font-size:15px;font-weight:850;margin-bottom:12px;">
          Message on WhatsApp
        </a>

        <a href="{dashboard_link}" style="display:block;background:#ffffff;color:#0f172a;text-decoration:none;text-align:center;padding:15px 18px;border-radius:14px;font-size:14px;font-weight:800;border:1px solid #dbe3ee;">
          View in Dashboard →
        </a>
      </div>

      <div style="padding:18px 32px;background:#f8fafc;border-top:1px solid #e8edf4;text-align:center;">
        <div style="font-size:12px;color:#94a3b8;">
          Sent automatically · Lead Qualification System
        </div>
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