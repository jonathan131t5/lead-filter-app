import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("SENDGRID_API_KEY")


def send_email(lead_data):
    status = lead_data["final_status"]

    if status.lower() in ["hot lead", "hot"]:
        status_color_bg = "#dcfce7"
        status_color_text = "#166534"
        status_dot = "#16a34a"
        status_label = "Hot Lead"
    elif status.lower() in ["cold lead", "cold"]:
        status_color_bg = "#fee2e2"
        status_color_text = "#991b1b"
        status_dot = "#dc2626"
        status_label = "Cold Lead"
    else:
        status_color_bg = "#f1f5f9"
        status_color_text = "#475569"
        status_dot = "#94a3b8"
        status_label = "Pending"

    phone = lead_data["phone_number"]
    whatsapp_link = f"https://wa.me/972{phone[1:]}"
    initials = "".join([w[0] for w in lead_data["name"].split()][:2]).upper()
    score_pct = min(int(lead_data["total_score"]) * 10, 100)

    content = f"""
    <div style="font-family:-apple-system,'Segoe UI',sans-serif; background:#f8fafc; padding:24px;">
      <div style="max-width:520px; margin:auto; background:#ffffff; border-radius:16px; overflow:hidden; border:1px solid #e2e8f0;">

        <div style="background:#0f172a; padding:28px 28px 24px;">
          <div style="display:flex; align-items:center; gap:8px; margin-bottom:10px;">
            <div style="width:7px; height:7px; border-radius:50%; background:#22c55e;"></div>
            <span style="font-size:11px; color:#64748b; letter-spacing:0.08em; text-transform:uppercase;">Lead Qualification System</span>
          </div>
          <h2 style="margin:0 0 6px; font-size:22px; font-weight:500; color:#f8fafc;">New lead received</h2>
          <p style="margin:0; font-size:13px; color:#64748b;">A new inquiry was submitted through your lead filter app.</p>
        </div>

        <div style="padding:20px 28px 0;">
          <span style="display:inline-flex; align-items:center; gap:6px; padding:5px 12px; border-radius:999px; background:{status_color_bg}; font-size:12px; font-weight:500; color:{status_color_text};">
            <span style="width:6px; height:6px; border-radius:50%; background:{status_dot}; display:inline-block;"></span>
            {status_label}
          </span>
        </div>

        <div style="padding:20px 28px;">

          <div style="display:flex; align-items:center; gap:14px; padding:14px 0; border-bottom:1px solid #f1f5f9;">
            <div style="width:36px; height:36px; border-radius:50%; background:#e0e7ff; display:flex; align-items:center; justify-content:center; font-size:13px; font-weight:500; color:#3730a3; flex-shrink:0;">{initials}</div>
            <div>
              <p style="margin:0 0 2px; font-size:11px; color:#94a3b8;">Name</p>
              <p style="margin:0; font-size:15px; font-weight:500; color:#0f172a;">{lead_data["name"]}</p>
            </div>
          </div>

          <div style="display:grid; grid-template-columns:1fr 1fr;">
            <div style="padding:14px 16px 14px 0; border-bottom:1px solid #f1f5f9; border-right:1px solid #f1f5f9;">
              <p style="margin:0 0 2px; font-size:11px; color:#94a3b8;">Phone</p>
              <p style="margin:0; font-size:14px; font-weight:500; color:#0f172a; font-family:monospace;">{phone}</p>
            </div>
            <div style="padding:14px 0 14px 16px; border-bottom:1px solid #f1f5f9;">
              <p style="margin:0 0 2px; font-size:11px; color:#94a3b8;">Score</p>
              <div style="display:flex; align-items:center; gap:8px;">
                <span style="font-size:22px; font-weight:500; color:#16a34a;">{lead_data["total_score"]}</span>
                <div style="flex:1; background:#f1f5f9; border-radius:999px; height:6px; overflow:hidden; max-width:60px;">
                  <div style="width:{score_pct}%; height:100%; background:#16a34a; border-radius:999px;"></div>
                </div>
              </div>
            </div>
          </div>

          <div style="padding:14px 0; border-bottom:1px solid #f1f5f9;">
            <p style="margin:0 0 2px; font-size:11px; color:#94a3b8;">Goal</p>
            <p style="margin:0; font-size:14px; font-weight:500; color:#0f172a;">{lead_data["goal_user"]}</p>
          </div>

          <div style="padding:14px 0;">
            <p style="margin:0 0 2px; font-size:11px; color:#94a3b8;">Timeline</p>
            <div style="display:flex; align-items:center; gap:6px;">
              <span style="width:7px; height:7px; border-radius:50%; background:#f59e0b; display:inline-block;"></span>
              <p style="margin:0; font-size:14px; font-weight:500; color:#0f172a;">{lead_data["urgency_user"]}</p>
            </div>
          </div>

        </div>

        <div style="padding:0 28px 28px;">
          <a href="{whatsapp_link}" style="display:flex; align-items:center; justify-content:center; gap:8px; background:#16a34a; color:white; text-decoration:none; padding:14px; border-radius:10px; font-size:14px; font-weight:500;">
            Message on WhatsApp
          </a>
        </div>

        <div style="padding:14px 28px; border-top:1px solid #f1f5f9; background:#f8fafc;">
          <p style="margin:0; font-size:11px; color:#94a3b8; text-align:center;">Sent automatically by your lead qualification system</p>
        </div>

      </div>
    </div>
    """

    message = Mail(
        from_email="jona.wexler@gmail.com",
        to_emails="jona.wexler@gmail.com",
        subject=f"New Lead - {status_label}",
        html_content=content,
    )

    sg = SendGridAPIClient(api_key)
    response = sg.send(message)

    return response.status_code







