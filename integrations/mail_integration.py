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
        status_text  = "#10b981"
        status_label = "Hot Lead"
    elif status.lower() in ["cold lead", "cold"]:
        status_text  = "#ef4444"
        status_label = "Cold Lead"
    else:
        status_text  = "#94a3b8"
        status_label = "Pending"

    phone          = lead_data["phone_number"]
    lead_id        = lead_data["lead_id"]
    whatsapp_link  = f"https://wa.me/972{phone[1:]}"
    dashboard_link = f"{DASHBOARD_URL}?lead={lead_id}"
    score          = int(lead_data["total_score"])

    content = f"""
    <table width="100%" cellpadding="0" cellspacing="0" style="background:#f3f5f9;font-family:Arial,sans-serif;">
    <tr>
    <td align="center" style="padding:30px 10px;">

    <table width="520" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:16px;overflow:hidden;">

    <tr>
    <td style="background:#0b1220;padding:26px 24px;color:#ffffff;">
    <div style="font-size:22px;font-weight:800;">New lead received</div>
    <div style="font-size:13px;color:#94a3b8;margin-top:6px;">
    A new inquiry was submitted through your lead filter.
    </div>
    </td>
    </tr>

    <tr>
    <td style="padding:24px;">

    <div style="font-size:18px;font-weight:800;color:#0f172a;">
    {lead_data["name"]}
    </div>

    <div style="font-size:13px;color:#64748b;margin-top:4px;">
    {phone}
    </div>

    <div style="margin-top:10px;font-size:12px;font-weight:700;color:{status_text};">
    ● {status_label}
    </div>

    </td>
    </tr>

    <tr>
    <td style="padding:0 24px 18px 24px;">

    <div style="font-size:13px;color:#94a3b8;margin-bottom:6px;">Score</div>
    <div style="font-size:28px;font-weight:800;color:#0f172a;">
    {score}/10
    </div>

    </td>
    </tr>

    <tr>
    <td style="padding:0 24px 18px 24px;">

    <div style="font-size:13px;color:#94a3b8;margin-bottom:6px;">Timeline</div>
    <div style="font-size:15px;font-weight:600;color:#0f172a;">
    {lead_data["urgency_user"]}
    </div>

    </td>
    </tr>

    <tr>
    <td style="padding:0 24px 26px 24px;">

    <div style="font-size:13px;color:#94a3b8;margin-bottom:6px;">Goal</div>
    <div style="font-size:15px;font-weight:600;color:#0f172a;">
    {lead_data["goal_user"]}
    </div>

    </td>
    </tr>

    <tr>
    <td style="padding:0 24px 12px 24px;">

    <a href="{whatsapp_link}" 
    style="display:block;background:#16a34a;color:#ffffff;text-align:center;padding:14px;border-radius:10px;font-weight:800;text-decoration:none;">
    Message on WhatsApp
    </a>

    </td>
    </tr>

    <tr>
    <td style="padding:0 24px 24px 24px;">

    <a href="{dashboard_link}" 
    style="display:block;background:#ffffff;color:#0f172a;text-align:center;padding:13px;border-radius:10px;font-weight:800;text-decoration:none;border:1px solid #dbe3ee;">
    View in Dashboard →
    </a>

    </td>
    </tr>

    <tr>
    <td align="center" style="padding:18px;font-size:12px;color:#94a3b8;">
    Sent automatically
    </td>
    </tr>

    </table>

    </td>
    </tr>
    </table>
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