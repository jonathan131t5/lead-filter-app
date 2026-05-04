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
<table width="100%" cellpadding="0" cellspacing="0" style="background:#eef2f7;font-family:Arial,sans-serif;padding:0;margin:0;">
<tr>
<td align="center" style="padding:34px 12px;">

<table width="540" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:18px;overflow:hidden;border:1px solid #e2e8f0;">

<tr>
<td style="padding:26px 26px 22px 26px;background:#0f172a;color:#ffffff;">
  <div style="font-size:12px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:#94a3b8;">
    FitLead
  </div>

  <div style="font-size:24px;font-weight:800;margin-top:10px;line-height:1.2;">
    New qualified lead
  </div>

  <div style="font-size:14px;color:#cbd5e1;margin-top:8px;line-height:1.5;">
    A new inquiry was filtered, scored, and summarized for follow-up.
  </div>
</td>
</tr>

<tr>
<td style="padding:24px 26px 10px 26px;">

<table width="100%" cellpadding="0" cellspacing="0">
<tr>
<td>
  <div style="font-size:20px;font-weight:800;color:#0f172a;">
    {lead_data["name"]}
  </div>

  <div style="font-size:14px;color:#64748b;margin-top:5px;">
    {phone}
  </div>
</td>

<td align="right">
  <div style="display:inline-block;background:#f8fafc;border:1px solid #e2e8f0;border-radius:999px;padding:7px 12px;font-size:12px;font-weight:800;color:{status_text};">
    ● {status_label}
  </div>
</td>
</tr>
</table>

</td>
</tr>

<tr>
<td style="padding:16px 26px 8px 26px;">

<table width="100%" cellpadding="0" cellspacing="0" style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:14px;">
<tr>
<td style="padding:18px;">
  <div style="font-size:13px;color:#64748b;font-weight:700;">
    Lead score
  </div>

  <div style="font-size:34px;font-weight:900;color:#0f172a;margin-top:6px;line-height:1;">
    {score}<span style="font-size:18px;color:#94a3b8;">/10</span>
  </div>
</td>
</tr>
</table>

</td>
</tr>

<tr>
<td style="padding:10px 26px 0 26px;">

<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:separate;border-spacing:0 10px;">

<tr>
<td style="background:#ffffff;border:1px solid #e2e8f0;border-radius:12px;padding:15px;">
  <div style="font-size:12px;color:#94a3b8;font-weight:800;text-transform:uppercase;letter-spacing:0.04em;">
    Timeline
  </div>
  <div style="font-size:15px;color:#0f172a;font-weight:700;margin-top:6px;line-height:1.45;">
    {lead_data["urgency_user"]}
  </div>
</td>
</tr>

<tr>
<td style="background:#ffffff;border:1px solid #e2e8f0;border-radius:12px;padding:15px;">
  <div style="font-size:12px;color:#94a3b8;font-weight:800;text-transform:uppercase;letter-spacing:0.04em;">
    Goal
  </div>
  <div style="font-size:15px;color:#0f172a;font-weight:700;margin-top:6px;line-height:1.45;">
    {lead_data["goal_user"]}
  </div>
</td>
</tr>

</table>

</td>
</tr>

<tr>
<td style="padding:18px 26px 10px 26px;">
  <a href="{whatsapp_link}"
  style="display:block;background:#16a34a;color:#ffffff;text-align:center;padding:15px;border-radius:12px;font-weight:900;text-decoration:none;font-size:15px;">
    Message on WhatsApp
  </a>
</td>
</tr>

<tr>
<td style="padding:0 26px 26px 26px;">
  <a href="{dashboard_link}"
  style="display:block;background:#ffffff;color:#0f172a;text-align:center;padding:14px;border-radius:12px;font-weight:900;text-decoration:none;font-size:15px;border:1px solid #cbd5e1;">
    View full lead →
  </a>
</td>
</tr>

<tr>
<td align="center" style="background:#f8fafc;padding:16px;font-size:12px;color:#94a3b8;border-top:1px solid #e2e8f0;">
  Sent automatically by FitLead
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