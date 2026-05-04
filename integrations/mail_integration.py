import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("SENDGRID_API_KEY")


def send_email(lead_data):
    status = lead_data["final_status"]

    if status.lower() in ["hot lead", "hot"]:
        status_color = "#16a34a"
        status_label = "Hot Lead"
    elif status.lower() in ["cold lead", "cold"]:
        status_color = "#dc2626"
        status_label = "Cold Lead"
    else:
        status_color = "#6b7280"
        status_label = "Pending"

    phone = lead_data["phone_number"]
    whatsapp_link = f"https://wa.me/972{phone[1:]}"

    content = f"""
    <div style="font-family: Arial, sans-serif; background:#f4f6f8; padding:24px;">
        <div style="max-width:560px; margin:auto; background:#ffffff; border-radius:14px; overflow:hidden; border:1px solid #e5e7eb;">

            <div style="background:#111827; color:white; padding:20px 24px;">
                <h2 style="margin:0; font-size:22px;">New Lead Received</h2>
                <p style="margin:6px 0 0 0; font-size:14px; color:#d1d5db;">
                    A new inquiry was submitted through your lead filter.
                </p>
            </div>

            <div style="padding:22px 24px;">

                <div style="margin-bottom:20px;">
                    <span style="
                        display:inline-block;
                        padding:7px 12px;
                        border-radius:999px;
                        background:{status_color}20;
                        color:{status_color};
                        font-size:13px;
                        font-weight:bold;">
                        {status_label}
                    </span>
                </div>

                <table style="width:100%; border-collapse:collapse; font-size:14px;">
                    <tr>
                        <td style="padding:10px 0; color:#6b7280;">Name</td>
                        <td style="padding:10px 0; text-align:right; font-weight:bold; color:#111827;">
                            {lead_data["name"]}
                        </td>
                    </tr>

                    <tr>
                        <td style="padding:10px 0; color:#6b7280; border-top:1px solid #f0f0f0;">Phone</td>
                        <td style="padding:10px 0; text-align:right; font-weight:bold; color:#111827; border-top:1px solid #f0f0f0;">
                            {phone}
                        </td>
                    </tr>

                    <tr>
                        <td style="padding:10px 0; color:#6b7280; border-top:1px solid #f0f0f0;">Goal</td>
                        <td style="padding:10px 0; text-align:right; font-weight:bold; color:#111827; border-top:1px solid #f0f0f0;">
                            {lead_data["goal_user"]}
                        </td>
                    </tr>

                    <tr>
                        <td style="padding:10px 0; color:#6b7280; border-top:1px solid #f0f0f0;">Timeline</td>
                        <td style="padding:10px 0; text-align:right; font-weight:bold; color:#111827; border-top:1px solid #f0f0f0;">
                            {lead_data["urgency_user"]}
                        </td>
                    </tr>

                    <tr>
                        <td style="padding:10px 0; color:#6b7280; border-top:1px solid #f0f0f0;">Score</td>
                        <td style="padding:10px 0; text-align:right; font-weight:bold; color:#111827; border-top:1px solid #f0f0f0;">
                            {lead_data["total_score"]}
                        </td>
                    </tr>
                </table>

                <div style="margin-top:24px;">
                    <a href="{whatsapp_link}"
                       style="
                       display:block;
                       text-align:center;
                       background:#25D366;
                       color:white;
                       text-decoration:none;
                       padding:14px 18px;
                       border-radius:10px;
                       font-size:15px;
                       font-weight:bold;">
                       Message on WhatsApp
                    </a>
                </div>

                <p style="margin:18px 0 0 0; font-size:12px; color:#9ca3af; text-align:center;">
                    Sent automatically by your lead qualification system.
                </p>

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







