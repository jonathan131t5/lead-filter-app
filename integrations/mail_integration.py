import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("SENDGRID_API_KEY")


def send_email(lead_data):
    status = lead_data['final_status']
    if status.lower() in ["hot lead", "hot"]:
        status_color = "#28a745"
    elif status.lower() in ["cold lead", "cold"]:
        status_color = "#dc3545"
    else:
        status_color = "#6c757d"

    content = f"""
    <div style="font-family: Arial, sans-serif; background:#f6f6f6; padding:20px;">
    
    <div style="max-width:520px; margin:auto; background:white; border-radius:10px; padding:20px; border:1px solid #eee;">
            
        <h2 style="margin:0 0 10px 0;">🔥 New Lead</h2>

        <p style="margin:0 0 15px 0; font-size:14px;">
            Status: <b style="color:{status_color};">{lead_data['final_status']}</b>
        </p>

        <div style="font-size:14px; line-height:1.6;">
            <p><b>Name:</b> {lead_data['name']}</p>
            <p><b>Phone:</b> {lead_data['phone_number']}</p>
            <p><b>Goal:</b> {lead_data['goal_user']}</p>
            <p><b>Timeline:</b> {lead_data['urgency_user']}</p>
            <p><b>Score:</b> {lead_data['total_score']}</p>
        </div>

        <hr style="margin:15px 0; border:none; border-top:1px solid #eee;">

        <div style="font-size:14px;">
            <p style="margin-bottom:5px;"><b>Summary:</b></p>
            <p style="margin:0; color:#333;">
                {lead_data['summary'].replace(chr(10), "<br>")}
            </p>
        </div>

        <div style="margin-top:20px;">
            <a href="https://wa.me/972{lead_data['phone_number'][1:]}" 
            style="display:inline-block;
            padding:12px 18px;
            background:#25D366;
            color:white;
            text-decoration:none;
            border-radius:6px;
            font-size:14px;
            font-weight:bold;">
            Message on WhatsApp
            </a>
        </div>

    </div>

</div>
"""  

    message = Mail(
        from_email="jona.wexler@gmail.com",
        to_emails="jona.wexler@gmail.com",
        subject="New Lead",
        html_content=content
    )

    sg = SendGridAPIClient(api_key)
    response = sg.send(message)

    return response.status_code







