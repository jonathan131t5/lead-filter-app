import streamlit as st
import sqlite3
from mvp import service_layer, validate_str

st.set_page_config(page_title="Lead Filter Engine", page_icon="💬", layout="wide")

# =========================
# Reset button
# =========================
if st.sidebar.button("🧹 איפוס מלא"):
    conn = sqlite3.connect("lead_qualification.db", check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM leads_messages")
    cursor.execute("DELETE FROM leads_fields_data")
    cursor.execute("DELETE FROM leads_scores")
    cursor.execute("DELETE FROM leads_info")

    conn.commit()
    conn.close()

    st.session_state.clear()
    st.rerun()

# =========================
# Style
# =========================
st.markdown("""
<style>
    .main {
        direction: rtl;
    }

    .stApp {
        background-color: #f7f9fc;
    }

    h1, h2, h3 {
        color: #1f3b73;
    }

    .custom-card {
        background: white;
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.08);
        margin-bottom: 14px;
        border: 1px solid #e6ebf2;
    }

    .summary-box {
        background: #fff8e8;
        border: 1px solid #ffe2a8;
        border-radius: 14px;
        padding: 14px;
        margin-top: 10px;
        margin-bottom: 10px;
    }

    .section-title {
        font-size: 20px;
        font-weight: 700;
        color: #1f3b73;
        margin-bottom: 10px;
    }

    .small-label {
        color: #5f6b7a;
        font-size: 14px;
        font-weight: 600;
    }

    .status-hot {
        color: #b54708;
        font-weight: 700;
    }

    .status-cold {
        color: #175cd3;
        font-weight: 700;
    }

    .status-pending {
        color: #667085;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# Session state
# =========================
if "phone_number" not in st.session_state:
    st.session_state.phone_number = None

if "lead_name" not in st.session_state:
    st.session_state.lead_name = None

if "new_lead" not in st.session_state:
    st.session_state.new_lead = False

if "welcome_message" not in st.session_state:
    st.session_state.welcome_message = False

if "first" not in st.session_state:
    st.session_state.first = False

if "ended" not in st.session_state:
    st.session_state.ended = False

if "messages" not in st.session_state:
    st.session_state.messages = []

if "need_name" not in st.session_state:
    st.session_state.need_name = False

if "ready_for_chat" not in st.session_state:
    st.session_state.ready_for_chat = False


# =========================
# Helpers
# =========================
def add_bot_message(text):
    st.session_state.messages.append({"role": "assistant", "content": text})


def add_user_message(text):
    st.session_state.messages.append({"role": "user", "content": text})


def get_db_connection():
    return sqlite3.connect("lead_qualification.db", check_same_thread=False)


def translate_status(status):
    if status == "Hot Lead":
        return "ליד חם 🔥"
    elif status == "Cold Lead":
        return "ליד קר ❄️"
    else:
        return "ממתין ⏳"


def status_class(status):
    if status == "Hot Lead":
        return "status-hot"
    elif status == "Cold Lead":
        return "status-cold"
    return "status-pending"


def run_message_flow(content, prepare_info):
    validate_str(content, "content")

    analyze_info = service_layer.get_lead_all_information(
        all_lead_info=prepare_info,
        mode="analyze"
    )

    ai_analyze_response = service_layer.build_analyze_input(
        lead_info=analyze_info,
        content=content
    )

    new_data_info = service_layer.process_analysis_result(
        lead_info=analyze_info,
        ai_analyze_response=ai_analyze_response,
        user_answer=content
    )

    final_status = service_layer.classify_lead(
        lead_info=analyze_info,
        ai_analyze_response=ai_analyze_response
    )

    if final_status is not None:
        if final_status["final_status"] == "Hot Lead":
            service_layer.process_lead_summary(
                lead_id=analyze_info["lead_id"],
                phone_number=st.session_state.phone_number
            )
        else:
            service_layer.data_access.upload_summary(
                lead_summary="הליד סווג כקר - לא נמצא פוטנציאל מתאים כרגע.",
                lead_id=analyze_info["lead_id"]
                )
    else:
        service_layer.data_access.upload_summary(
        lead_summary="לא הושלם סיווג.",
        lead_id=analyze_info["lead_id"]
    )

    
    lead_base_info = service_layer.get_lead_all_information(
        all_lead_info=prepare_info,
        mode="chat"
    )

    if new_data_info["status"] == "info provided":
        lead_base_info["current_field"] = new_data_info["updated_field"]
        lead_base_info["attempt_number"] = new_data_info["updated_attempt"]
        question_type = new_data_info["question_type"]
    else:
        lead_base_info["attempt_number"] = new_data_info["updated_attempt"]
        question_type = new_data_info["question_type"]

    status = service_layer.conversation_chat(
        lead_info=lead_base_info,
        content=content,
        question_type=question_type
    )

    if status["status"] == "all info provided include final status":
        final_text = (
            f"{lead_base_info['name']}, תודה רבה על הזמן ועל שיתוף הפעולה.\n\n"
            "קיבלנו בהצלחה את כל הפרטים שלך והם הועברו לצוות שלנו להמשך בדיקה וטיפול.\n"
            "נציג מטעמנו יחזור אליך בהקדם האפשרי עם המשך התהליך והפרטים הרלוונטיים.\n\n"
            "מאחלים לך המשך יום נעים ובריאות טובה."
        )
        add_bot_message(final_text)
        st.session_state.ended = True

    elif status["status"] == "ok":
        add_bot_message(status["response"])


def render_customer_page():
    st.title("צד לקוח")

    if not st.session_state.ready_for_chat:
        phone_input = st.text_input(
            "הכנס מספר טלפון",
            value=st.session_state.phone_number or ""
        )

        if st.session_state.need_name:
            name_input = st.text_input("הכנס שם")
        else:
            name_input = ""

        if st.button("התחל"):
            try:
                if not phone_input.strip():
                    st.error("יש להזין מספר טלפון")
                    st.stop()

                st.session_state.phone_number = phone_input.strip()

                prepare_info = service_layer.prepare_lead_context(
                    phone_number=st.session_state.phone_number
                )

                if prepare_info == "new account":
                    st.session_state.new_lead = True
                    st.session_state.need_name = True

                    if not name_input.strip():
                        st.warning("זה מספר חדש. הזן שם ואז לחץ שוב על 'התחל'.")
                        st.stop()

                    st.session_state.lead_name = name_input.strip()

                    prepare_info = service_layer.prepare_lead_context(
                        phone_number=st.session_state.phone_number,
                        lead_name=st.session_state.lead_name,
                        account_status="login"
                    )

                    st.session_state.need_name = False

                else:
                    st.session_state.new_lead = False
                    st.session_state.need_name = False
                    st.session_state.lead_name = prepare_info["lead_base_info"]["result"]["name"]

                if not st.session_state.welcome_message:
                    if st.session_state.new_lead:
                        add_bot_message(
                            f"{st.session_state.lead_name}, החשבון שלך נוצר בהצלחה. תודה שבחרת בנו."
                        )
                    else:
                        add_bot_message(
                            f"ברוך הבא {st.session_state.lead_name}, שמחים לראות אותך שוב."
                        )
                    st.session_state.welcome_message = True

                if not st.session_state.first:
                    greeting = f"היי מה שלומך {st.session_state.lead_name}"
                    add_bot_message(greeting)

                    run_message_flow("none", prepare_info)
                    st.session_state.first = True

                st.session_state.ready_for_chat = True
                st.rerun()

            except Exception as e:
                st.error(f"Error: {e}")

    for msg in st.session_state.messages:
        with st.chat_message("user" if msg["role"] == "user" else "assistant"):
            st.write(msg["content"])

    if st.session_state.ready_for_chat and not st.session_state.ended:
        user_text = st.chat_input("כתוב הודעה...")

        if user_text:
            try:
                add_user_message(user_text)

                prepare_info = service_layer.prepare_lead_context(
                    phone_number=st.session_state.phone_number
                )

                run_message_flow(user_text.strip(), prepare_info)
                st.rerun()

            except Exception as e:
                st.error(f"Error: {e}")

    if st.session_state.ended:
        st.info("השיחה הסתיימה.")


def render_business_page():
    st.title("צד בעל העסק")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            li.lead_id,
            li.name,
            li.phone_number,
            li.status,
            li.summary,
            li.created_at,
            ls.total_score,
            ls.goal_score,
            ls.budget_score,
            ls.urgency_score
        FROM leads_info li
        LEFT JOIN leads_scores ls ON li.lead_id = ls.lead_id
        ORDER BY li.lead_id DESC
    """)
    leads = cursor.fetchall()

    if not leads:
        st.info("אין עדיין לידים במערכת.")
        conn.close()
        return

    hot_count = sum(1 for lead in leads if lead[3] == "Hot Lead")
    cold_count = sum(1 for lead in leads if lead[3] == "Cold Lead")
    pending_count = sum(1 for lead in leads if lead[3] == "pending")

    col1, col2, col3 = st.columns(3)
    col1.metric("לידים חמים", hot_count)
    col2.metric("לידים קרים", cold_count)
    col3.metric("ממתינים", pending_count)

    st.divider()

    for lead in leads:
        lead_id = lead[0]
        name = lead[1] or "ללא שם"
        phone = lead[2] or "-"
        raw_status = lead[3] or "pending"
        status_display = translate_status(raw_status)
        status_style = status_class(raw_status)
        summary = lead[4] or "אין עדיין סיכום"
        created_at = lead[5] or "-"
        total_score = lead[6] if lead[6] is not None else 0
        goal_score = lead[7] if lead[7] is not None else 0
        budget_score = lead[8] if lead[8] is not None else 0
        urgency_score = lead[9] if lead[9] is not None else 0

        with st.expander(f"ליד #{lead_id} | {name} | {status_display} | ציון כולל: {total_score}"):
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)

            st.write(f"**שם:** {name}")
            st.write(f"**טלפון:** {phone}")
            st.markdown(f'**סטטוס:** <span class="{status_style}">{status_display}</span>', unsafe_allow_html=True)
            st.write(f"**נוצר בתאריך:** {created_at}")

            c1, c2, c3 = st.columns(3)
            c1.metric("מטרה", goal_score)
            c2.metric("תקציב", budget_score)
            c3.metric("דחיפות", urgency_score)

            st.markdown('<div class="summary-box">', unsafe_allow_html=True)
            st.markdown("**סיכום:**")
            st.markdown(summary.replace("\n", "  \n"))
            st.markdown('</div>', unsafe_allow_html=True)

            cursor.execute("""
                SELECT role, content, created_at
                FROM leads_messages
                WHERE lead_id = ?
                ORDER BY message_id ASC
            """, (lead_id,))
            messages = cursor.fetchall()

            st.markdown("**היסטוריית שיחה:**")
            if messages:
                for role, content, created in messages:
                    role_text = "לקוח" if role == "user" else "בוט"
                    st.write(f"**{role_text}:** {content}")
            else:
                st.write("אין הודעות עדיין.")

            st.markdown('</div>', unsafe_allow_html=True)

    conn.close()


# =========================
# Sidebar navigation
# =========================
page = st.sidebar.radio("בחר מסך", ["צד לקוח", "צד בעל העסק"])

if page == "צד לקוח":
    render_customer_page()
else:
    render_business_page()