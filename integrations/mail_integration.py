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
<table width="100%" cellpadding="0" cellspacing="0" style="margin:0;padding:0;background:#f3f6fb;font-family:Arial,Helvetica,sans-serif;">
<tr>
<td align="center" style="padding:36px 12px;">

<table width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:100%;background:#ffffff;border-radius:22px;overflow:hidden;border:1px solid #dbe3ef;box-shadow:0 14px 40px rgba(15,23,42,0.08);">

<tr>
<td style="padding:30px 32px;background:#111827;">
  <div style="font-size:13px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;color:#9ca3af;">
    New lead
  </div>

  <div style="font-size:28px;font-weight:900;color:#ffffff;margin-top:10px;line-height:1.15;">
    {lead_data["name"]} is ready for follow-up
  </div>

  <div style="font-size:15px;color:#cbd5e1;margin-top:10px;line-height:1.5;">
    A new inquiry came in and was summarized for you.
  </div>
</td>
</tr>

<tr>
<td style="padding:28px 32px 0 32px;">

<table width="100%" cellpadding="0" cellspacing="0">
<tr>
<td valign="top">
  <div style="font-size:13px;color:#64748b;font-weight:700;margin-bottom:6px;">
    Contact
  </div>

  <div style="font-size:22px;font-weight:900;color:#0f172a;line-height:1.2;">
    {lead_data["name"]}
  </div>

  <div style="font-size:15px;color:#475569;margin-top:6px;">
    {phone}
  </div>
</td>

<td align="right" valign="top">
  <div style="display:inline-block;background:#ecfdf5;border:1px solid #bbf7d0;border-radius:999px;padding:8px 13px;font-size:13px;font-weight:900;color:{status_text};">
    ● {status_label}
  </div>
</td>
</tr>
</table>

</td>
</tr>

<tr>
<td style="padding:24px 32px 0 32px;">

<table width="100%" cellpadding="0" cellspacing="0" style="background:#f8fafc;border:1px solid #dbe3ef;border-radius:18px;">
<tr>
<td style="padding:24px;">
  <div style="font-size:13px;color:#64748b;font-weight:800;text-transform:uppercase;letter-spacing:0.04em;">
    Lead score
  </div>

  <div style="margin-top:10px;">
    <span style="font-size:46px;font-weight:900;color:#0f172a;line-height:1;">{score}</span>
    <span style="font-size:20px;font-weight:800;color:#94a3b8;">/10</span>
  </div>

  <div style="font-size:14px;color:#64748b;margin-top:8px;line-height:1.45;">
    Use this to decide how quickly to follow up.
  </div>
</td>
</tr>
</table>

</td>
</tr>

<tr>
<td style="padding:22px 32px 0 32px;">

<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:separate;border-spacing:0 12px;">

<tr>
<td style="background:#ffffff;border:1px solid #dbe3ef;border-radius:16px;padding:18px 20px;">
  <div style="font-size:12px;color:#94a3b8;font-weight:900;text-transform:uppercase;letter-spacing:0.06em;">
    Wants to start
  </div>

  <div style="font-size:16px;color:#0f172a;font-weight:800;margin-top:7px;line-height:1.45;">
    {lead_data["urgency_user"]}
  </div>
</td>
</tr>

<tr>
<td style="background:#ffffff;border:1px solid #dbe3ef;border-radius:16px;padding:18px 20px;">
  <div style="font-size:12px;color:#94a3b8;font-weight:900;text-transform:uppercase;letter-spacing:0.06em;">
    Looking for
  </div>

  <div style="font-size:16px;color:#0f172a;font-weight:800;margin-top:7px;line-height:1.45;">
    {lead_data["goal_user"]}
  </div>
</td>
</tr>

</table>

</td>
</tr>

<tr>
<td style="padding:22px 32px 0 32px;">

<table width="100%" cellpadding="0" cellspacing="0">
<tr>
<td style="padding-bottom:12px;">
  <a href="{whatsapp_link}"
     style="display:block;background:#16a34a;color:#ffffff;text-align:center;padding:16px 18px;border-radius:14px;font-weight:900;text-decoration:none;font-size:16px;">
    Message on WhatsApp
  </a>
</td>
</tr>

<tr>
<td>
  <a href="{dashboard_link}"
     style="display:block;background:#ffffff;color:#111827;text-align:center;padding:15px 18px;border-radius:14px;font-weight:900;text-decoration:none;font-size:15px;border:1px solid #cbd5e1;">
    Open lead details →
  </a>
</td>
</tr>
</table>

</td>
</tr>

<tr>
<td style="padding:26px 32px 30px 32px;">
  <div style="border-top:1px solid #e5e7eb;padding-top:18px;font-size:12px;color:#94a3b8;line-height:1.5;text-align:center;">
    This email was sent automatically after a new lead completed the form.
  </div>
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