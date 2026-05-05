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
        badge_bg     = "#f0fdf4"
        badge_border = "#86efac"
        badge_color  = "#15803d"
        dot_color    = "#16a34a"
        status_label = "Hot Lead"
    elif status.lower() in ["cold lead", "cold"]:
        badge_bg     = "#eff6ff"
        badge_border = "#93c5fd"
        badge_color  = "#1d4ed8"
        dot_color    = "#3b82f6"
        status_label = "Cold Lead"
    else:
        badge_bg     = "#fafafa"
        badge_border = "#d4d4d8"
        badge_color  = "#52525b"
        dot_color    = "#a1a1aa"
        status_label = "Pending"

    phone          = lead_data["phone_number"]
    lead_id        = lead_data["lead_id"]
    whatsapp_link  = f"https://wa.me/972{phone[1:]}"
    dashboard_link = f"{DASHBOARD_URL}?lead={lead_id}"
    name           = lead_data["name"]

    content = f"""<!DOCTYPE html>
<html lang="he" dir="rtl" xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<title>ליד חדש</title>
<style type="text/css">
  body,table,td,a{{-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;}}
  table,td{{mso-table-lspace:0pt;mso-table-rspace:0pt;}}
  body{{margin:0!important;padding:0!important;background-color:#f4f4f5;}}

  @media only screen and (max-width:599px){{
    .email-card{{width:100%!important;border-radius:0!important;}}
    .pad{{padding:22px 20px!important;}}
    .head{{padding:24px 20px 20px!important;}}
    .cta{{padding:0 20px 28px!important;}}
    .foot{{padding:14px 20px 20px!important;}}
    .i1,.i2{{display:block!important;width:100%!important;}}
    .isp{{display:none!important;}}
    .headline{{font-size:20px!important;}}
    .btn{{font-size:15px!important;}}
  }}
</style>
</head>
<body style="margin:0;padding:0;background-color:#f4f4f5;">

<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#f4f4f5;">
<tr><td align="center" style="padding:40px 16px;">

  <table role="presentation" class="email-card" cellpadding="0" cellspacing="0" border="0"
    style="width:580px;max-width:580px;background:#ffffff;border-radius:16px;
           border:1px solid #e4e4e7;border-collapse:separate;">

    <!-- top accent -->
    <tr>
      <td style="height:3px;background:#16a34a;border-radius:16px 16px 0 0;
                 font-size:0;line-height:0;">&nbsp;</td>
    </tr>

    <!-- header -->
    <tr>
      <td class="head" style="padding:32px 36px 26px;border-bottom:1px solid #f4f4f5;">
        <p style="margin:0 0 10px;font-size:11px;font-weight:600;letter-spacing:0.1em;
                  text-transform:uppercase;color:#a1a1aa;
                  font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;">
          ליד חדש
        </p>
        <p class="headline" style="margin:0 0 6px;font-size:22px;font-weight:800;color:#09090b;
                  line-height:1.25;
                  font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;">
          {name} השאיר פנייה
        </p>
        <p style="margin:0;font-size:14px;color:#71717a;line-height:1.55;
                  font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;">
          פנייה חדשה נכנסה ועברה סיכום אוטומטי עבורך.
        </p>
      </td>
    </tr>

    <!-- contact + badge -->
    <tr>
      <td class="pad" style="padding:24px 36px 0;">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
          <tr>
            <td valign="middle">
              <p style="margin:0 0 3px;font-size:17px;font-weight:700;color:#09090b;
                        font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;">
                {name}
              </p>
              <p style="margin:0;font-size:13px;color:#71717a;direction:ltr;text-align:right;
                        font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;">
                {phone}
              </p>
            </td>
            <td align="left" valign="middle">
              <table role="presentation" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td style="background:{badge_bg};border:1px solid {badge_border};
                             border-radius:999px;padding:6px 12px;">
                    <table role="presentation" cellpadding="0" cellspacing="0" border="0">
                      <tr>
                        <td width="7" height="7"
                          style="width:7px;height:7px;border-radius:4px;
                                 background-color:{dot_color};font-size:0;line-height:0;">
                        </td>
                        <td style="padding-right:6px;">
                          <span style="font-size:12px;font-weight:600;color:{badge_color};
                                       font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;
                                       white-space:nowrap;">
                            {status_label}
                          </span>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </td>
    </tr>

    <!-- divider -->
    <tr>
      <td style="padding:20px 36px 0;">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
          <tr><td style="height:1px;background:#f4f4f5;font-size:0;line-height:0;">&nbsp;</td></tr>
        </table>
      </td>
    </tr>

    <!-- info cells -->
    <tr>
      <td class="pad" style="padding:20px 36px 0;">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
          <tr>
            <td class="i1" valign="top"
              style="width:48%;background:#fafafa;border:1px solid #ebebeb;
                     border-radius:10px;padding:14px 16px;">
              <p style="margin:0 0 6px;font-size:10px;font-weight:600;letter-spacing:0.08em;
                        text-transform:uppercase;color:#a1a1aa;
                        font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;">
                מתי רוצה להתחיל
              </p>
              <p style="margin:0;font-size:14px;font-weight:600;color:#09090b;line-height:1.4;
                        font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;">
                {lead_data["urgency_user"]}
              </p>
            </td>
            <td class="isp" style="width:4%;font-size:0;">&nbsp;</td>
            <td class="i2" valign="top"
              style="width:48%;background:#fafafa;border:1px solid #ebebeb;
                     border-radius:10px;padding:14px 16px;">
              <p style="margin:0 0 6px;font-size:10px;font-weight:600;letter-spacing:0.08em;
                        text-transform:uppercase;color:#a1a1aa;
                        font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;">
                מה מחפש
              </p>
              <p style="margin:0;font-size:14px;font-weight:600;color:#09090b;line-height:1.4;
                        font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;">
                {lead_data["goal_user"]}
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>

    <!-- CTAs -->
    <tr>
      <td class="cta" style="padding:24px 36px 32px;">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
          <tr>
            <td style="padding-bottom:10px;">
              <!--[if mso]><v:roundrect xmlns:v="urn:schemas-microsoft-com:vml"
                href="{whatsapp_link}"
                style="height:48px;v-text-anchor:middle;width:508px;"
                arcsize="21%" stroke="f" fillcolor="#16a34a">
                <w:anchorlock/><center style="color:#fff;font-size:15px;font-weight:700;
                font-family:Arial,sans-serif;">שלח הודעה ב-WhatsApp</center>
              </v:roundrect><![endif]-->
              <!--[if !mso]><!-->
              <a href="{whatsapp_link}" class="btn"
                style="display:block;background:#16a34a;color:#ffffff;text-align:center;
                       padding:14px 20px;border-radius:10px;font-weight:700;font-size:15px;
                       text-decoration:none;
                       font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;">
                שלח הודעה ב-WhatsApp
              </a>
              <!--<![endif]-->
            </td>
          </tr>
          <tr>
            <td>
              <!--[if mso]><v:roundrect xmlns:v="urn:schemas-microsoft-com:vml"
                href="{dashboard_link}"
                style="height:46px;v-text-anchor:middle;width:508px;"
                arcsize="21%" strokecolor="#e4e4e7" fillcolor="#ffffff">
                <w:anchorlock/><center style="color:#3f3f46;font-size:14px;font-weight:500;
                font-family:Arial,sans-serif;">פרטי הליד המלאים</center>
              </v:roundrect><![endif]-->
              <!--[if !mso]><!-->
              <a href="{dashboard_link}" class="btn"
                style="display:block;background:#ffffff;color:#3f3f46;text-align:center;
                       padding:13px 20px;border-radius:10px;font-weight:500;font-size:14px;
                       text-decoration:none;border:1px solid #e4e4e7;
                       font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;">
                פרטי הליד המלאים ←
              </a>
              <!--<![endif]-->
            </td>
          </tr>
        </table>
      </td>
    </tr>

    <!-- footer -->
    <tr>
      <td class="foot"
        style="padding:16px 36px 24px;border-top:1px solid #f4f4f5;
               text-align:center;font-size:12px;color:#a1a1aa;line-height:1.6;
               font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;">
        המייל נשלח אוטומטית לאחר שליד מילא את הטופס.
      </td>
    </tr>

  </table>

</td></tr>
</table>
</body>
</html>"""

    message = Mail(
        from_email="jona.wexler@gmail.com",
        to_emails="jona.wexler@gmail.com",
        subject=f"ליד חדש — {status_label} · {name}",
        html_content=content,
    )

    sg = SendGridAPIClient(api_key)
    response = sg.send(message)

    return response.status_code