import streamlit as st
from streamlit_extras.stylable_container import stylable_container
import sqlite3
from datetime import datetime
import os
import sqlite3
import streamlit.components.v1 as components
print("RUNNING FROM:", os.getcwd())
print("DB PATH:", os.path.abspath("lead_qualification.db"))
# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LeadSync",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)
 
# ─── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Heebo', sans-serif !important;
    direction: rtl;
}

html, body, [class*="css"] {
    background-color: #f7f8fc;
    color: #1a1a2e;
}
 
/* Sidebar */
[data-testid="stSidebar"] {
    background: #ffffff;
    border-left: 1px solid #e8eaf0;
    border-right: none;
}
 
[data-testid="stSidebar"] .block-container {
    padding: 2rem 1.2rem;
}
 
/* Hide default streamlit elements */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
 
/* Main content */
.block-container {
    padding: 2.5rem 2rem 2rem 2rem;
    max-width: 900px;
}
 
/* Page title */
.page-title {
    font-size: 2rem;
    font-weight: 800;
    color: #1a1a2e;
    margin-bottom: 0.2rem;
    letter-spacing: -0.5px;
}
 
.page-subtitle {
    font-size: 0.9rem;
    color: #8892a4;
    margin-bottom: 2rem;
    font-weight: 400;
}
 
/* Metric cards */
.metrics-row {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;
}
 
.metric-card {
    flex: 1;
    background: #ffffff;
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    border: 1px solid #e8eaf0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
 
.metric-label {
    font-size: 0.78rem;
    color: #8892a4;
    font-weight: 500;
    margin-bottom: 0.3rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
 
.metric-value {
    font-size: 2rem;
    font-weight: 800;
    color: #1a1a2e;
    line-height: 1;
}
 
.metric-value.hot { color: #e85d3f; }
.metric-value.cold { color: #4a90d9; }
.metric-value.pending { color: #f0a500; }
 
/* Lead card */
.lead-card {
    background: #ffffff;
    border-radius: 14px;
    border: 1px solid #e8eaf0;
    margin-bottom: 0.8rem;
    overflow: hidden;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    transition: box-shadow 0.2s ease;
}
 
.lead-card:hover {
    box-shadow: 0 4px 16px rgba(0,0,0,0.08);
}
 
.lead-card-header {
    padding: 1rem 1.3rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    cursor: pointer;
}
 
.lead-name-section {
    display: flex;
    align-items: center;
    gap: 0.7rem;
}
 
.lead-avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.85rem;
    flex-shrink: 0;
}
 
.avatar-hot { background: #fde8e3; color: #e85d3f; }
.avatar-cold { background: #e3edf8; color: #4a90d9; }
.avatar-pending { background: #fef3d8; color: #f0a500; }
 
.lead-name {
    font-weight: 600;
    font-size: 0.95rem;
    color: #1a1a2e;
}
 
.lead-meta {
    font-size: 0.78rem;
    color: #8892a4;
    margin-top: 1px;
}
 
.lead-right-info {
    display: flex;
    align-items: center;
    gap: 1rem;
    text-align: left;
}
 
.score-badge {
    font-size: 0.85rem;
    font-weight: 700;
    color: #1a1a2e;
}
 
.score-label {
    font-size: 0.7rem;
    color: #8892a4;
    font-weight: 400;
}
 
.status-tag {
    font-size: 0.72rem;
    font-weight: 600;
    padding: 0.3rem 0.7rem;
    border-radius: 20px;
    white-space: nowrap;
}
 
.tag-hot { background: #fde8e3; color: #c94c2e; }
.tag-cold { background: #e3edf8; color: #2e6db3; }
.tag-pending { background: #fef3d8; color: #c07f00; }
 
/* Lead detail section */
.lead-detail {
    padding: 1.2rem 1.3rem;
    border-top: 1px solid #f0f2f7;
    background: #fafbfe;
}
 
.detail-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-bottom: 1rem;
}
 
.detail-item {
    background: #ffffff;
    border-radius: 10px;
    padding: 0.8rem 1rem;
    border: 1px solid #e8eaf0;
    text-align: center;
}
 
.detail-item-label {
    font-size: 0.72rem;
    color: #8892a4;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 0.3rem;
}
 
.detail-item-value {
    font-size: 1.4rem;
    font-weight: 800;
    color: #1a1a2e;
}
 
.summary-box {
    background: #fffbf0;
    border: 1px solid #fae8b0;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 1rem;
    font-size: 0.88rem;
    color: #4a3c00;
    line-height: 1.7;
    white-space: pre-wrap;
}
 
.contact-row {
    display: flex;
    gap: 0.8rem;
    margin-top: 0.5rem;
}
 
.contact-pill {
    background: #f0f2f7;
    border-radius: 20px;
    padding: 0.35rem 0.9rem;
    font-size: 0.8rem;
    color: #4a4f6a;
    font-weight: 500;
}
 
/* Chat page */
.chat-container {
    display: flex;
    flex-direction: column;
    gap: 0.8rem;
    padding: 1rem 0;
    min-height: 300px;
}
 
.chat-bubble {
    max-width: 75%;
    padding: 0.8rem 1.1rem;
    border-radius: 16px;
    font-size: 0.9rem;
    line-height: 1.6;
}
 
.bubble-bot {
    background: #ffffff;
    border: 1px solid #e8eaf0;
    border-radius: 16px 16px 16px 4px;
    color: #1a1a2e;
    display: flex;
    gap: 0.7rem;
    align-items: flex-start;
    max-width: 80%;
    padding: 0.9rem 1.1rem;
}
 
.bubble-bot-icon {
    width: 28px;
    height: 28px;
    background: #ff8c42;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.85rem;
    flex-shrink: 0;
    margin-top: 1px;
}
 
.bubble-user {
    background: #1a1a2e;
    color: #ffffff;
    border-radius: 16px 16px 4px 16px;
    margin-right: auto;
    margin-left: 0;
    align-self: flex-end;
}
 
/* Input area */
.input-area {
    position: sticky;
    bottom: 0;
    background: #f7f8fc;
    padding: 1rem 0 0.5rem 0;
}
 
/* Sidebar nav */
.nav-label {
    font-size: 0.7rem;
    font-weight: 700;
    color: #b0b8cc;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 1.5rem 0 0.5rem 0;
}
 
.sidebar-title {
    font-size: 1.1rem;
    font-weight: 800;
    color: #1a1a2e;
    margin-bottom: 0.2rem;
}
 
.sidebar-subtitle {
    font-size: 0.75rem;
    color: #8892a4;
    margin-bottom: 1.5rem;
}
 
/* Phone input label */
.phone-prompt {
    font-size: 1rem;
    color: #4a4f6a;
    margin-bottom: 0.8rem;
    line-height: 1.6;
}
 
/* Buttons */
.stButton > button {
    border-radius: 10px !important;
    font-family: 'Heebo', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    border: 1.5px solid #1a1a2e !important;
    color: #1a1a2e !important;
    background: transparent !important;
    padding: 0.45rem 1.2rem !important;
    transition: all 0.15s ease !important;
}
 
.stButton > button:hover {
    background: #1a1a2e !important;
    color: #ffffff !important;
}
 
/* Text input */
.stTextInput > div > div > input {
    border-radius: 10px !important;
    border: 1.5px solid #e0e3ed !important;
    font-family: 'Heebo', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 0.7rem 1rem !important;
    background: #ffffff !important;
    direction: rtl;
}
 
.stTextInput > div > div > input:focus {
    border-color: #1a1a2e !important;
    box-shadow: 0 0 0 2px rgba(26,26,46,0.08) !important;
}
 
.stTextInput label {
    display: none !important;
}
 
/* History section */
.history-header {
    font-size: 0.75rem;
    font-weight: 700;
    color: #b0b8cc;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 1.2rem 0 0.6rem 0;
}
 
.history-item {
    padding: 0.55rem 0.7rem;
    border-radius: 8px;
    font-size: 0.85rem;
    color: #4a4f6a;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.15rem;
}
 
.history-item:hover {
    background: #f0f2f7;
}
 
.history-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    flex-shrink: 0;
}
 
.dot-hot { background: #e85d3f; }
.dot-cold { background: #4a90d9; }
.dot-pending { background: #f0a500; }
 
hr.divider {
    border: none;
    border-top: 1px solid #e8eaf0;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)
 
 
# ─── DB Helper ─────────────────────────────────────────────────────────────────
def get_db():
    db_path = os.path.abspath("lead_qualification.db")
    print("DB PATH:", db_path)
    conn = sqlite3.connect(db_path, timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn
 
 
def fetch_leads():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                l.lead_id, l.name, l.phone_number, l.final_status, l.created_at, l.summary,
                s.total_score, s.budget_score, s.goal_score, s.urgency_score,
                s.budget_status, s.goal_status, s.urgency_status
            FROM leads_data l
            LEFT JOIN leads_scores s ON l.lead_id = s.lead_id
            ORDER BY l.created_at DESC
        """)
        rows = cur.fetchall()
        conn.close()
        return rows
    except Exception:
        return []
 
 
def fetch_messages(lead_id):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT role, content FROM leads_messages
            WHERE lead_id = ? ORDER BY message_id ASC
        """, (lead_id,))
        msgs = cur.fetchall()
        conn.close()
        return msgs
    except Exception:
        return []
 
 
# ─── Session State ─────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "customer"
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "phone_entered" not in st.session_state:
    st.session_state.phone_entered = False
if "name_entered" not in st.session_state:
    st.session_state.name_entered = False
if "phone_number" not in st.session_state:
    st.session_state.phone_number = ""
if "lead_name" not in st.session_state:
    st.session_state.lead_name = ""
if "chat_done" not in st.session_state:
    st.session_state.chat_done = False
if "service" not in st.session_state:
    try:
        from service.service_layer import ServiceLayer
        st.session_state.service = ServiceLayer()
        st.session_state.service.leads_data.create_leads_data_table()
        st.session_state.service.leads_states.create_lead_conversation_states()
        st.session_state.service.leads_scores.create_leads_scores_table()
        st.session_state.service.leads_fields.create_leads_fields_data()
        st.session_state.service.messages.create_leads_messages_table()
    except Exception as e:
        st.session_state.service = None
        st.session_state.service_error = str(e)
if "lead_context" not in st.session_state:
    st.session_state.lead_context = None
if "ack_mode" not in st.session_state:
    st.session_state.ack_mode = 0

if "waiting_for_user" not in st.session_state:
    st.session_state.waiting_for_user = False
 
 
# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">🎯 LeadSync</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-subtitle">מערכת סינון לידים חכמה</div>', unsafe_allow_html=True)
 
    st.markdown('<div class="nav-label">בחר מסך</div>', unsafe_allow_html=True)
 
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👤 צד לקוח", use_container_width=True):
            st.session_state.page = "customer"
            st.rerun()
    with col2:
        if st.button("💼 בעל עסק", use_container_width=True):
            st.session_state.page = "business"
            st.rerun()
 
    # Show recent leads in sidebar for business view
    if st.session_state.page == "business":
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown('<div class="history-header">לידים אחרונים</div>', unsafe_allow_html=True)
        leads = fetch_leads()
        for lead in leads[:6]:
            name = lead[1] or "לא ידוע"
            status = lead[3] or "pending"
            dot_class = "dot-hot" if status == "Hot Lead" else ("dot-cold" if status == "Cold Lead" else "dot-pending")
            st.markdown(f"""
                <div class="history-item">
                    <div class="history-dot {dot_class}"></div>
                    <span>{name}</span>
                </div>
            """, unsafe_allow_html=True)
 
 
# ─── Customer Page ─────────────────────────────────────────────────────────────
if st.session_state.page == "customer":
    st.markdown('<div class="page-title">צד לקוח</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">שיחה אוטומטית לסינון והתאמה</div>', unsafe_allow_html=True)
 
    svc = st.session_state.get("service")
 
    # ── Reset button ──
    col_r, col_space = st.columns([1, 4])
    with col_r:
        if st.button("🔄 ריענון"):
            for key in ["chat_messages", "phone_entered", "name_entered", "phone_number",
                        "lead_name", "chat_done", "lead_context", "ack_mode"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
 
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
 
    # ── Phone input ──
    if not st.session_state.phone_entered:
        st.markdown('<div class="phone-prompt">שנייה לפני שמתחילים, כדי לשמור לך את ההתקדמות ולהמשיך איתך —<br><strong>מה המספר שלך?</strong></div>', unsafe_allow_html=True)
        phone_input = st.text_input("phone", placeholder="05X-XXXXXXX", label_visibility="collapsed")
        if st.button("התחל"):
            if phone_input.strip():
                st.session_state.phone_number = phone_input.strip()
                if svc:
                    try:
                        ctx = svc.prepare_lead_context(phone_number=st.session_state.phone_number)
                        if "status" in ctx and ctx["status"] == "new":
                            st.session_state.phone_entered = True
                            st.session_state.name_entered = False
                        else:
                            st.session_state.lead_context = ctx
                            st.session_state.phone_entered = True
                            st.session_state.name_entered = True
                        st.rerun()
                    except Exception as e:
                        st.error(f"שגיאה: {e}")
                else:
                    st.session_state.phone_entered = True
                    st.rerun()
        st.stop()
 
    # ── Name input (only for new leads) ──
    if not st.session_state.name_entered:
        st.markdown('<div class="phone-prompt">מעולה, <strong>איך קוראים לך?</strong></div>', unsafe_allow_html=True)
        name_input = st.text_input("name", placeholder="שם פרטי", label_visibility="collapsed")
        if st.button("המשך"):
            if name_input.strip():
                st.session_state.lead_name = name_input.strip()
                if svc:
                    try:
                        ctx = svc.prepare_lead_context(
                            phone_number=st.session_state.phone_number,
                            name=st.session_state.lead_name,
                            mode=2
                        )
                        st.session_state.lead_context = ctx
                        st.session_state.name_entered = True
                        st.rerun()
                    except Exception as e:
                        st.error(f"שגיאה: {e}")
                else:
                    st.session_state.name_entered = True
                    st.rerun()
        st.stop()
 
    # ── Chat flow ──
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
 
    for msg in st.session_state.chat_messages:
        role = msg["role"]
        content = msg["content"]
        if role == "bot":
            st.markdown(f"""
                <div class="bubble-bot">
                    <div class="bubble-bot-icon">🤖</div>
                    <div>{content}</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style="display:flex; justify-content:flex-end;">
                    <div class="chat-bubble bubble-user">{content}</div>
                </div>
            """, unsafe_allow_html=True)
 
    st.markdown('<div id="chat-bottom"></div></div>', unsafe_allow_html=True)

 
    if not st.session_state.chat_done:
        if svc and st.session_state.lead_context and not st.session_state.waiting_for_user:
            try:
                result = svc.process_lead_message(
                    lead_all_data=st.session_state.lead_context,
                    mode="output",
                    ack_mode=st.session_state.ack_mode
                )
                if result and result.get("status") == "DONE":
                    closing = result.get("closing_message", "תודה, נחזור אליך בקרוב!")
                    st.session_state.chat_messages.append({"role": "bot", "content": closing})
                    st.session_state.chat_done = True
                    st.rerun()
                elif result and result.get("status") == "output":
                    question = result.get("question", "")
                    if not st.session_state.chat_messages or st.session_state.chat_messages[-1].get("content") != question:
                        st.session_state.chat_messages.append({"role": "bot", "content": question})
                        st.session_state.waiting_for_user = True
                        st.rerun()
            except Exception as e:
                st.error(f"שגיאה: {e}")
 
    if not st.session_state.chat_done:
        with st.form(key="chat_form", clear_on_submit=True):
            user_input = st.text_input(
                "כתוב הודעה...",
                placeholder="כתוב הודעה...",
                key="user_msg",
                label_visibility="collapsed"
            )
            submitted = st.form_submit_button("שלח ↑")

        if submitted:
            if user_input.strip() and svc and st.session_state.lead_context:
                st.session_state.chat_messages.append({"role": "user", "content": user_input.strip()})
                try:
                    svc.process_lead_message(
                        lead_all_data=st.session_state.lead_context,
                        content=user_input.strip(),
                        mode="input"
                    )

                    st.session_state.lead_context = svc.prepare_lead_context(
                        phone_number=st.session_state.phone_number
                    )

                    st.session_state.ack_mode = 1
                    st.session_state.waiting_for_user = False

                except Exception as e:
                    st.error(f"שגיאה: {e}")

                st.rerun()
    
 
# ─── Business Page ─────────────────────────────────────────────────────────────
elif st.session_state.page == "business":
    leads = fetch_leads()
 
    hot = sum(1 for l in leads if l[3] == "Hot Lead")
    cold = sum(1 for l in leads if l[3] == "Cold Lead")
    pending = sum(1 for l in leads if l[3] not in ("Hot Lead", "Cold Lead"))
 
    st.markdown('<div class="page-title">צד בעל העסק</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">סקירת לידים וסינון אוטומטי</div>', unsafe_allow_html=True)
 
    # Metrics
    st.markdown(f"""
        <div class="metrics-row">
            <div class="metric-card">
                <div class="metric-label">לידים חמים</div>
                <div class="metric-value hot">{hot}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">לידים קרים</div>
                <div class="metric-value cold">{cold}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">ממתינים</div>
                <div class="metric-value pending">{pending}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
 
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
 
    if not leads:
        st.info("אין לידים עדיין במערכת.")
    else:
        for lead in leads:
            lead_id = lead["lead_id"]
            name = lead["name"] or "לא ידוע"
            phone = lead["phone_number"] or ""
            status = lead["final_status"] or "pending"
            created_at = lead["created_at"] or ""
            summary = lead["summary"] or ""

            total_score = lead["total_score"] or 0
            budget_score = lead["budget_score"] or 0
            goal_score = lead["goal_score"] or 0
            urgency_score = lead["urgency_score"] or 0
 
            if status == "Hot Lead":
                tag_class = "tag-hot"
                avatar_class = "avatar-hot"
                status_label = "ליד חם 🔥"
                status_display = "ליד חם 🔥"
            elif status == "Cold Lead":
                tag_class = "tag-cold"
                avatar_class = "avatar-cold"
                status_label = "ליד קר 🧊"
                status_display = "ליד קר 🧊"
            else:
                tag_class = "tag-pending"
                avatar_class = "avatar-pending"
                status_label = "ממתין ⏳"
                status_display = "ממתין ⏳"
 
            initial = name[0] if name else "?"
 
            with st.expander(f"ליד #{lead_id} | {name} | {status_display} | ציון כללי: {total_score}"):
                st.markdown(f"""
                    <div style="display:flex; gap:2rem; align-items:flex-start; flex-wrap:wrap;">
                        <div>
                            <div style="font-size:0.75rem; color:#8892a4; margin-bottom:2px;">שם</div>
                            <div style="font-weight:600; font-size:1rem;">{name}</div>
                        </div>
                        <div>
                            <div style="font-size:0.75rem; color:#8892a4; margin-bottom:2px;">טלפון</div>
                            <div style="font-weight:600; font-size:1rem;">{phone}</div>
                        </div>
                        <div>
                            <div style="font-size:0.75rem; color:#8892a4; margin-bottom:2px;">סטטוס</div>
                            <div style="font-weight:700; font-size:1rem;" class="{tag_class}">{status_display}</div>
                        </div>
                        <div>
                            <div style="font-size:0.75rem; color:#8892a4; margin-bottom:2px;">נוצר בתאריך</div>
                            <div style="font-size:0.88rem; color:#4a4f6a;">{created_at}</div>
                        </div>
                    </div>
                    <hr class="divider">
                    <div class="detail-grid">
                        <div class="detail-item">
                            <div class="detail-item-label">מטרה</div>
                            <div class="detail-item-value">{goal_score}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-item-label">תקציב</div>
                            <div class="detail-item-value">{budget_score}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-item-label">דחיפות</div>
                            <div class="detail-item-value">{urgency_score}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
 
                if summary:
                    st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)
 
                # Chat history
                messages = fetch_messages(lead_id)
                if messages:
                    st.markdown('<div class="history-header">היסטוריית שיחה</div>', unsafe_allow_html=True)
                    for msg in messages:
                        role = msg["role"]
                        content = msg["content"]

                        if role in ("assistant", "bot"):
                            # הודעת בוט
                            st.markdown(f"""
                                <div style="display:flex; justify-content:flex-start;">
                                    <div style="
                                        max-width:75%;
                                        background:#ffffff;
                                        border:1px solid #e8eaf0;
                                        padding:0.7rem 1rem;
                                        border-radius:16px 16px 16px 4px;
                                        font-size:0.88rem;
                                        margin-bottom:0.4rem;
                                    ">
                                        {content}
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)

                        else:
                            # הודעת משתמש
                            st.markdown(f"""
                                <div style="display:flex; justify-content:flex-end;">
                                    <div style="
                                        max-width:75%;
                                        background:#1a1a2e;
                                        color:#ffffff;
                                        padding:0.7rem 1rem;
                                        border-radius:16px 16px 4px 16px;
                                        font-size:0.88rem;
                                        margin-bottom:0.4rem;
                                    ">
                                        {content}
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
 