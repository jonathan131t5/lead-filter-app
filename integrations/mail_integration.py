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
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background:#f3f5f9;margin:0;padding:0;font-family:Arial,'Segoe UI',sans-serif;">
  <tr>
    <td align="center" style="padding:36px 14px;">

      <table role="presentation" width="560" cellspacing="0" cellpadding="0" border="0" style="width:560px;max-width:560px;background:#ffffff;border:1px solid #e5eaf1;border-radius:18px;overflow:hidden;">
        
        <tr>
          <td style="background:#0b1220;padding:30px 32px 26px;">
            <div style="font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#22c55e;margin-bottom:18px;">
              Lead Qualification System
            </div>
            <div style="font-size:26px;line-height:32px;font-weight:800;color:#ffffff;margin-bottom:8px;">
              New lead received
            </div>
            <div style="font-size:14px;line-height:21px;color:#94a3b8;">
              A new inquiry was submitted through your lead filter.
            </div>
          </td>
        </tr>

        <tr>
          <td style="padding:28px 32px 22px;background:#ffffff;">
            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
              <tr>
                <td width="58" valign="middle">
                  <table role="presentation" width="52" height="52" cellspacing="0" cellpadding="0" border="0">
                    <tr>
                      <td align="center" valign="middle" style="width:52px;height:52px;background:#5b5cf6;border-radius:14px;color:#ffffff;font-size:17px;font-weight:800;">
                        {initials}
                      </td>
                    </tr>
                  </table>
                </td>

                <td valign="middle" style="padding-left:12px;">
                  <div style="font-size:18px;line-height:22px;font-weight:800;color:#0f172a;">
                    {lead_data["name"]}
                  </div>
                  <div style="font-size:13px;line-height:18px;color:#64748b;margin-top:4px;">
                    {phone}
                  </div>
                </td>

                <td align="right" valign="middle" width="130">
                  <span style="display:inline-block;background:{status_bg};border:1px solid {status_border};color:{status_text};font-size:12px;font-weight:800;padding:8px 13px;border-radius:999px;white-space:nowrap;">
                    ● {status_label}
                  </span>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <tr>
          <td style="padding:0 32px 26px;background:#ffffff;">
            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="border:1px solid #e5eaf1;border-radius:16px;background:#fbfcfe;overflow:hidden;">
              <tr>
                <td width="42%" valign="top" style="padding:22px;border-right:1px solid #e5eaf1;">
                  <div style="font-size:11px;font-weight:800;letter-spacing:1px;text-transform:uppercase;color:#94a3b8;margin-bottom:10px;">
                    Score
                  </div>
                  <div style="font-size:42px;line-height:44px;font-weight:900;color:#0f172a;">
                    {score}<span style="font-size:17px;color:#94a3b8;font-weight:800;">/10</span>
                  </div>
                  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-top:14px;">
                    <tr>
                      <td style="height:5px;background:#e2e8f0;border-radius:999px;">
                        <div style="height:5px;width:{score_pct}%;background:#10b981;border-radius:999px;"></div>
                      </td>
                    </tr>
                  </table>
                </td>

                <td width="58%" valign="top" style="padding:22px;">
                  <div style="font-size:11px;font-weight:800;letter-spacing:1px;text-transform:uppercase;color:#94a3b8;margin-bottom:14px;">
                    Timeline
                  </div>
                  <div style="font-size:15px;line-height:22px;font-weight:700;color:#0f172a;">
                    <span style="color:#f59e0b;">●</span>&nbsp;{lead_data["urgency_user"]}
                  </div>
                </td>
              </tr>

              <tr>
                <td colspan="2" style="border-top:1px solid #e5eaf1;padding:22px;">
                  <div style="font-size:11px;font-weight:800;letter-spacing:1px;text-transform:uppercase;color:#94a3b8;margin-bottom:10px;">
                    Goal
                  </div>
                  <div style="font-size:16px;line-height:24px;font-weight:700;color:#0f172a;">
                    {lead_data["goal_user"]}
                  </div>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <tr>
          <td style="padding:0 32px 32px;background:#ffffff;">
            <a href="{whatsapp_link}" style="display:block;background:#16a34a;color:#ffffff;text-decoration:none;text-align:center;padding:16px 18px;border-radius:13px;font-size:15px;font-weight:800;">
              Message on WhatsApp
            </a>

            <div style="height:12px;line-height:12px;font-size:12px;">&nbsp;</div>

            <a href="{dashboard_link}" style="display:block;background:#ffffff;color:#0f172a;text-decoration:none;text-align:center;padding:15px 18px;border-radius:13px;font-size:14px;font-weight:800;border:1px solid #dbe3ee;">
              View in Dashboard →
            </a>
          </td>
        </tr>

        <tr>
          <td align="center" style="padding:18px 32px;background:#f8fafc;border-top:1px solid #e5eaf1;font-size:12px;color:#94a3b8;">
            Sent automatically · Lead Qualification System
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