import sqlite3
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

import streamlit as st

try:
    from streamlit_autorefresh import st_autorefresh  # optional
except Exception:
    st_autorefresh = None

# ---- Flexible imports so the file works in slightly different project layouts ----
try:
    from service.service_layer import ServiceLayer
except ImportError:
    from service_layer import ServiceLayer  # type: ignore

try:
    from utils.validators import validate_phone_number, validate_str
except ImportError:
    from validators import validate_phone_number, validate_str  # type: ignore

DB_PATH = "lead_qualification.db"
AUTO_REFRESH_INTERVAL_MS = 8000


# =========================
# Database helpers
# =========================
def bootstrap_database() -> None:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS leads_data(
            lead_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone_number TEXT UNIQUE NOT NULL,
            final_status TEXT DEFAULT 'pending',
            summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            last_interaction_at TIMESTAMP
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS lead_conversation_states(
            lead_id INTEGER PRIMARY KEY,
            current_field TEXT DEFAULT 'goal',
            regular_attempt_number INTEGER DEFAULT 1,
            confuse_attempt_number INTEGER DEFAULT 1,
            question_state TEXT DEFAULT 'base',
            question_reason TEXT DEFAULT 'base',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            last_interaction_at TIMESTAMP
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS leads_scores(
            lead_id INTEGER PRIMARY KEY,
            goal_score INTEGER DEFAULT 0,
            budget_score INTEGER DEFAULT 0,
            urgency_score INTEGER DEFAULT 0,
            goal_status TEXT,
            budget_status TEXT,
            urgency_status TEXT,
            score_count INTEGER DEFAULT 0,
            total_score INTEGER DEFAULT 0
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS leads_fields_data(
            lead_id INTEGER PRIMARY KEY,
            goal_bot TEXT,
            goal_user TEXT,
            budget_bot TEXT,
            budget_user TEXT,
            urgency_bot TEXT,
            urgency_user TEXT,
            updated_at TIMESTAMP
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS leads_messages(
            message_id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER,
            role TEXT,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()
    conn.close()


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


@st.cache_resource
def get_service_layer() -> ServiceLayer:
    bootstrap_database()
    return ServiceLayer()


# =========================
# Dashboard queries
# =========================
def fetch_dashboard_leads() -> List[Dict[str, Any]]:
    query = """
        SELECT
            ld.lead_id,
            ld.name,
            ld.phone_number,
            ld.final_status,
            ld.summary,
            ld.created_at,
            ld.last_interaction_at,
            ls.total_score,
            ls.score_count,
            ls.goal_score,
            ls.budget_score,
            ls.urgency_score,
            ls.goal_status,
            ls.budget_status,
            ls.urgency_status,
            lfd.goal_user,
            lfd.budget_user,
            lfd.urgency_user
        FROM leads_data ld
        LEFT JOIN leads_scores ls ON ld.lead_id = ls.lead_id
        LEFT JOIN leads_fields_data lfd ON ld.lead_id = lfd.lead_id
        ORDER BY COALESCE(ld.last_interaction_at, ld.created_at) DESC, ld.lead_id DESC
    """
    with get_db() as conn:
        rows = conn.execute(query).fetchall()
    return [dict(row) for row in rows]


def fetch_lead_messages(lead_id: int) -> List[Dict[str, Any]]:
    query = """
        SELECT message_id, lead_id, role, content, created_at
        FROM leads_messages
        WHERE lead_id = ?
        ORDER BY message_id ASC
    """
    with get_db() as conn:
        rows = conn.execute(query, (lead_id,)).fetchall()
    return [dict(row) for row in rows]


def fetch_lead_state(lead_id: int) -> Optional[Dict[str, Any]]:
    query = """
        SELECT current_field, regular_attempt_number, confuse_attempt_number,
               question_state, question_reason, created_at, updated_at, last_interaction_at
        FROM lead_conversation_states
        WHERE lead_id = ?
    """
    with get_db() as conn:
        row = conn.execute(query, (lead_id,)).fetchone()
    return dict(row) if row else None


# =========================
# Helpers
# =========================
def safe_text(value: Any, empty: str = "—") -> str:
    if value is None:
        return empty
    txt = str(value).strip()
    return txt if txt else empty


def status_label(status: Optional[str]) -> str:
    if status == "Hot Lead":
        return "🔥 ליד חם"
    if status == "Cold Lead":
        return "🧊 ליד קר"
    return "⏳ בתהליך"


def status_class(status: Optional[str]) -> str:
    if status == "Hot Lead":
        return "hot"
    if status == "Cold Lead":
        return "cold"
    return "pending"


def score_display(value: Any) -> str:
    if value is None:
        return "—"
    return str(value)


def init_state() -> None:
    defaults = {
        "page": "chat",
        "chat_phase": "phone",   # phone -> name -> chat
        "phone_number": "",
        "lead_name": "",
        "lead_context": None,
        "chat_messages": [],
        "flow_finished": False,
        "selected_lead_id": None,
        "dashboard_search": "",
        "dashboard_filter": "הכל",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_chat_state() -> None:
    st.session_state.chat_phase = "phone"
    st.session_state.phone_number = ""
    st.session_state.lead_name = ""
    st.session_state.lead_context = None
    st.session_state.chat_messages = []
    st.session_state.flow_finished = False


def append_system_message(text: str, persist: bool = False) -> None:
    st.session_state.chat_messages.append({"role": "assistant", "content": text})
    if persist and st.session_state.get("lead_context"):
        lead_id = st.session_state["lead_context"]["lead_base_data"]["lead_id"]
        insert_message(lead_id, "assistant", text)


def append_user_message(text: str) -> None:
    st.session_state.chat_messages.append({"role": "user", "content": text})



def insert_message(lead_id: int, role: str, content: str) -> None:
    with get_db() as conn:
        conn.execute(
            "INSERT INTO leads_messages (lead_id, role, content) VALUES (?, ?, ?)",
            (lead_id, role, content),
        )
        conn.commit()

def ask_first_question(service_layer: ServiceLayer, context: Dict[str, Any]) -> None:
    output = service_layer.process_lead_message(
        lead_all_data=context,
        mode="output",
        ack_mode=0,
    )
    if output.get("status") == "output":
        append_system_message(output["question"], persist=True)
    elif output.get("status") == "DONE":
        append_system_message(output["closing_message"], persist=True)
        st.session_state.flow_finished = True


# =========================
# Styling
# =========================
def inject_css() -> None:
    st.markdown("""
    <style>
        :root {
            --bg: #f5f7fb;
            --surface: #ffffff;
            --surface-alt: #f8fafc;
            --border: #e5e7eb;
            --border-strong: #d8dee8;
            --text: #0f172a;
            --muted: #64748b;
            --blue: #2563eb;
            --blue-soft: #eff6ff;
            --green: #16a34a;
            --green-soft: #f0fdf4;
            --red: #dc2626;
            --red-soft: #fef2f2;
            --amber: #d97706;
            --amber-soft: #fffbeb;
            --shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
        }

        .stApp {
            background: var(--bg);
            color: var(--text);
        }

        [data-testid="stHeader"] {
            background: rgba(245, 247, 251, 0.88);
            border-bottom: 1px solid var(--border);
            backdrop-filter: blur(8px);
        }

        [data-testid="stSidebar"] {
            background: #ffffff;
            border-left: 1px solid var(--border);
        }

        .block-container {
            max-width: 1360px;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        .shell-card,
        .section-card,
        .lead-list-card,
        .tile,
        .lead-row {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 18px;
            box-shadow: var(--shadow);
        }

        .shell-card {
            padding: 1.4rem 1.5rem;
            margin-bottom: 1rem;
        }

        .hero-title {
            font-size: 2rem;
            font-weight: 800;
            line-height: 1.1;
            color: var(--text);
            margin-bottom: 0.35rem;
            letter-spacing: -0.02em;
        }

        .hero-sub {
            color: var(--muted);
            font-size: 1rem;
            line-height: 1.7;
        }

        .section-card,
        .lead-list-card {
            padding: 1rem 1.05rem;
            margin-bottom: 1rem;
        }

        .section-title {
            font-size: 1.04rem;
            font-weight: 800;
            color: var(--text);
            margin-bottom: 0.75rem;
        }

        .minor-text {
            color: var(--muted);
            font-size: 0.94rem;
            line-height: 1.65;
        }

        .tile {
            padding: 1rem 1.05rem;
            min-height: 110px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            margin-bottom: 0.85rem;
        }

        .tile-label {
            color: var(--muted);
            font-size: 0.92rem;
            font-weight: 600;
        }

        .tile-value {
            color: var(--text);
            font-size: 1.8rem;
            font-weight: 800;
            line-height: 1;
        }

        .lead-row {
            padding: 0.95rem;
            margin-bottom: 0.7rem;
            border: 1px solid var(--border);
        }

        .lead-row.selected {
            border-color: rgba(37, 99, 235, 0.45);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.08);
        }

        .lead-name {
            color: var(--text);
            font-size: 1rem;
            font-weight: 800;
            margin-bottom: 0.2rem;
        }

        .lead-sub {
            color: var(--muted);
            font-size: 0.92rem;
        }

        .badge {
            display: inline-flex;
            align-items: center;
            gap: .3rem;
            border-radius: 999px;
            padding: .34rem .7rem;
            font-size: .8rem;
            font-weight: 700;
            border: 1px solid transparent;
        }

        .badge.hot {
            background: var(--green-soft);
            color: var(--green);
            border-color: #bbf7d0;
        }

        .badge.cold {
            background: var(--red-soft);
            color: var(--red);
            border-color: #fecaca;
        }

        .badge.pending {
            background: var(--amber-soft);
            color: var(--amber);
            border-color: #fde68a;
        }

        .top-nav-wrap {
            display: flex;
            gap: .75rem;
            margin-bottom: 1rem;
        }

        .top-nav-button {
            width: 100%;
            padding: 0.92rem 1rem;
            border-radius: 14px;
            border: 1px solid var(--border);
            background: white;
            font-weight: 800;
            color: var(--text);
            transition: all .15s ease;
        }

        .top-nav-button.active {
            background: var(--blue);
            color: white;
            border-color: var(--blue);
            box-shadow: 0 10px 20px rgba(37, 99, 235, 0.18);
        }

        .chat-stage {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 1.15rem;
            box-shadow: var(--shadow);
            margin-bottom: 1rem;
        }

        .chat-head {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: .8rem;
            margin-bottom: .9rem;
            flex-wrap: wrap;
        }

        .chat-meta {
            display: flex;
            gap: .45rem;
            flex-wrap: wrap;
        }

        .chat-badge {
            background: var(--surface-alt);
            color: var(--text);
            border: 1px solid var(--border);
            border-radius: 999px;
            padding: .34rem .65rem;
            font-size: .82rem;
            font-weight: 700;
        }

        .empty-state {
            background: var(--surface-alt);
            border: 1px dashed var(--border-strong);
            border-radius: 16px;
            padding: 1rem;
            color: var(--muted);
        }

        .subtle-divider {
            height: 1px;
            background: var(--border);
            margin: 1rem 0;
        }

        .sidebar-brand {
            font-size: 1.3rem;
            font-weight: 900;
            color: var(--text);
            margin-bottom: .15rem;
        }

        .sidebar-sub {
            color: var(--muted);
            font-size: .92rem;
            margin-bottom: 1rem;
        }

        .sidebar-note {
            background: var(--surface-alt);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: .9rem;
            color: var(--muted);
            line-height: 1.7;
            font-size: .92rem;
            margin-top: 1rem;
        }

        .stChatMessage {
            background: white;
            border: 1px solid var(--border);
            border-radius: 16px;
        }

        [data-testid="stForm"] {
            border: none !important;
            padding: 0 !important;
            background: transparent !important;
        }

        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea {
            background: white !important;
            color: var(--text) !important;
            border: 1px solid var(--border-strong) !important;
            border-radius: 12px !important;
        }

        input::placeholder,
        textarea::placeholder {
            color: transparent !important;
        }

        div[data-testid="stTextInput"] input:focus,
        div[data-testid="stTextArea"] textarea:focus {
            border-color: rgba(37, 99, 235, 0.55) !important;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.10) !important;
        }

        .stButton > button,
        div[data-testid="stFormSubmitButton"] > button {
            border-radius: 12px !important;
            border: 1px solid var(--border-strong) !important;
            background: white !important;
            color: var(--text) !important;
            font-weight: 800 !important;
            min-height: 44px !important;
        }

        .stButton > button:hover,
        div[data-testid="stFormSubmitButton"] > button:hover {
            border-color: rgba(37, 99, 235, 0.45) !important;
            color: var(--blue) !important;
            background: var(--blue-soft) !important;
        }

        .primary-action button {
            background: var(--blue) !important;
            color: white !important;
            border-color: var(--blue) !important;
        }

        .primary-action button:hover {
            background: #1d4ed8 !important;
            color: white !important;
            border-color: #1d4ed8 !important;
        }

        div[data-baseweb="select"] > div {
            background: white !important;
            border-color: var(--border-strong) !important;
            border-radius: 12px !important;
        }

        label, .stMarkdown, .stCaption {
            color: var(--text) !important;
        }
    </style>
    """, unsafe_allow_html=True)


# =========================
# Navigation
# =========================
def render_sidebar() -> None:
    with st.sidebar:
        st.markdown('<div class="sidebar-brand">Lead Filter Engine</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-sub">Analyze • Score • Classify</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("צ׳אט משתמש", use_container_width=True):
                st.session_state.page = "chat"
                st.rerun()
        with col2:
            if st.button("דשבורד", use_container_width=True):
                st.session_state.page = "dashboard"
                st.rerun()


# =========================
# Chat page
# =========================
def render_chat_page(service_layer: ServiceLayer) -> None:
    st.markdown(
        """
        <div class="shell-card" dir="rtl">
            <div class="hero-title">התאמה חכמה לפני שמתחילים</div>
            <div class="hero-sub">
                כמה שאלות קצרות כדי להבין מה הכיוון שלך, לשמור את ההתקדמות,
                ולהמשיך בדיוק מאיפה שנעצרת.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    top_a, top_b = st.columns([5, 1])
    with top_b:
        if st.button("התחלה מחדש", use_container_width=True):
            reset_chat_state()
            st.rerun()

    if st.session_state.chat_phase == "phone":
        st.markdown('<div class="section-card" dir="rtl">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">הכנס מספר טלפון</div>', unsafe_allow_html=True)
        with st.form("phone_form"):
            phone_number = st.text_input("הכנס מספר טלפון", placeholder="", label_visibility="collapsed")
            submitted = st.form_submit_button("המשך", use_container_width=True)
            if submitted:
                try:
                    validate_phone_number(phone_number)
                    phone_number = phone_number.strip()
                    context = service_layer.prepare_lead_context(phone_number=phone_number)
                    st.session_state.phone_number = phone_number

                    if isinstance(context, dict) and context.get("status") == "new":
                        st.session_state.chat_phase = "name"
                        st.rerun()
                    else:
                        st.session_state.lead_context = context
                        st.session_state.lead_name = safe_text(context["lead_base_data"].get("name"), "")
                        st.session_state.chat_phase = "chat"
                        st.session_state.chat_messages = []
                        st.session_state.flow_finished = False
                        ask_first_question(service_layer, context)
                        st.rerun()
                except Exception as exc:
                    st.error(str(exc))
        st.markdown('</div>', unsafe_allow_html=True)
        return

    if st.session_state.chat_phase == "name":
        st.markdown('<div class="section-card" dir="rtl">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">מעולה, איך קוראים לך?</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="minor-text">כדי להמשיך, נוסיף שם ונמשיך הלאה.</div>',
            unsafe_allow_html=True,
        )
        with st.form("name_form"):
            lead_name = st.text_input("מעולה, איך קוראים לך?", placeholder="", label_visibility="collapsed")
            submitted = st.form_submit_button("להתחיל", use_container_width=True)
            if submitted:
                try:
                    validate_str(lead_name, "שם")
                    lead_name = lead_name.strip()
                    context = service_layer.prepare_lead_context(
                        phone_number=st.session_state.phone_number,
                        name=lead_name,
                        mode=2,
                    )
                    st.session_state.lead_name = lead_name
                    st.session_state.lead_context = context
                    st.session_state.chat_phase = "chat"
                    st.session_state.chat_messages = []
                    st.session_state.flow_finished = False
                    ask_first_question(service_layer, context)
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))
        st.markdown('</div>', unsafe_allow_html=True)
        return

    st.markdown('<div class="chat-stage">', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div dir="rtl" style="margin-bottom: .85rem; display:flex; gap:.45rem; flex-wrap:wrap;">
            <span class="chat-badge">{st.session_state.lead_name or 'משתמש'}</span>
            <span class="chat-badge">{st.session_state.phone_number}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for msg in st.session_state.chat_messages:
        with st.chat_message("assistant" if msg["role"] == "assistant" else "user"):
            st.markdown(f"<div dir='rtl'>{msg['content']}</div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.flow_finished:
        return

    prompt = st.chat_input("כתוב כאן את התשובה שלך")
    if prompt:
        try:
            append_user_message(prompt)
            service_layer.process_lead_message(
                lead_all_data=st.session_state.lead_context,
                content=prompt,
                mode="input",
            )

            refreshed_context = service_layer.prepare_lead_context(phone_number=st.session_state.phone_number)
            st.session_state.lead_context = refreshed_context

            next_output = service_layer.process_lead_message(
                lead_all_data=refreshed_context,
                mode="output",
                ack_mode=1,
            )

            if next_output.get("status") == "output":
                append_system_message(next_output["question"], persist=True)
            elif next_output.get("status") == "DONE":
                append_system_message(next_output["closing_message"], persist=True)
                st.session_state.flow_finished = True

            st.rerun()
        except Exception as exc:
            st.error(str(exc))


# =========================
# Dashboard page
# =========================
def render_dashboard_page() -> None:
    st.markdown(
        """
        <div class="shell-card" dir="rtl">
            <div class="hero-title">דשבורד בעל העסק</div>
            <div class="hero-sub">
                תמונה ברורה של כל הלידים: מי חם, מי בתהליך, מה נאמר בשיחה, ומה הסיכום הסופי.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    controls_left, controls_right = st.columns([1, 5])
    with controls_left:
        if st.button("רענן", use_container_width=True):
            st.rerun()
    with controls_right:
        if st_autorefresh is not None:
            st_autorefresh(interval=AUTO_REFRESH_INTERVAL_MS, key="dashboard_autorefresh")

    leads = fetch_dashboard_leads()

    total_leads = len(leads)
    hot_leads = sum(1 for lead in leads if lead.get("final_status") == "Hot Lead")
    cold_leads = sum(1 for lead in leads if lead.get("final_status") == "Cold Lead")
    pending_leads = total_leads - hot_leads - cold_leads

    cards = st.columns(4)
    data = [
        ("סה״כ לידים", total_leads),
        ("לידים חמים", hot_leads),
        ("לידים קרים", cold_leads),
        ("בתהליך", pending_leads),
    ]
    for col, (label, value) in zip(cards, data):
        with col:
            st.markdown(
                f"""
                <div class="tile">
                    <div class="tile-label">{label}</div>
                    <div class="tile-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    search_col, filter_col = st.columns([2.15, 1])
    with search_col:
        search_term = st.text_input(
            "חיפוש לפי שם או טלפון",
            value=st.session_state.dashboard_search,
            placeholder="למשל: יהונתן או 050...",
        )
        st.session_state.dashboard_search = search_term
    with filter_col:
        options = ["הכל", "Hot Lead", "Cold Lead", "pending"]
        current_index = options.index(st.session_state.dashboard_filter) if st.session_state.dashboard_filter in options else 0
        status_filter = st.selectbox("סינון לפי סטטוס", options, index=current_index)
        st.session_state.dashboard_filter = status_filter

    filtered: List[Dict[str, Any]] = []
    for lead in leads:
        haystack = f"{safe_text(lead.get('name'))} {safe_text(lead.get('phone_number'))}".lower()
        lead_status = lead.get("final_status") or "pending"
        if search_term and search_term.lower() not in haystack:
            continue
        if status_filter != "הכל" and lead_status != status_filter:
            continue
        filtered.append(lead)

    if not filtered:
        st.info("אין כרגע לידים להצגה.")
        return

    if st.session_state.selected_lead_id is None:
        st.session_state.selected_lead_id = filtered[0]["lead_id"]

    valid_ids = {lead["lead_id"] for lead in filtered}
    if st.session_state.selected_lead_id not in valid_ids:
        st.session_state.selected_lead_id = filtered[0]["lead_id"]

    left, right = st.columns([1.05, 1.95], gap="large")

    with left:
        st.markdown('<div class="lead-list-card" dir="rtl">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">רשימת לידים</div>', unsafe_allow_html=True)
        st.markdown('<div class="minor-text" style="margin-bottom: .8rem;">לחיצה על ליד טוענת את כל הפרטים שלו בצד.</div>', unsafe_allow_html=True)

        for lead in filtered:
            selected = lead["lead_id"] == st.session_state.selected_lead_id
            st.markdown(
                f"""
                <div class="lead-row {'selected' if selected else ''}" dir="rtl">
                    <div class="lead-name">{safe_text(lead.get('name'), 'ללא שם')}</div>
                    <div class="lead-sub">{safe_text(lead.get('phone_number'))}</div>
                    <div style="margin-top:.6rem; display:flex; justify-content:space-between; align-items:center; gap:.5rem; flex-wrap:wrap;">
                        <span class="badge {status_class(lead.get('final_status'))}">{status_label(lead.get('final_status'))}</span>
                        <span class="minor-text">ציון: {safe_text(lead.get('total_score'), '0')}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("בחר ליד" if not selected else "נבחר", key=f"lead_select_{lead['lead_id']}", use_container_width=True, disabled=selected):
                st.session_state.selected_lead_id = lead["lead_id"]
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    selected_lead = next((lead for lead in filtered if lead["lead_id"] == st.session_state.selected_lead_id), filtered[0])
    messages = fetch_lead_messages(selected_lead["lead_id"])
    lead_state = fetch_lead_state(selected_lead["lead_id"])

    with right:
        st.markdown('<div class="section-card" dir="rtl">', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div style="display:flex; align-items:center; justify-content:space-between; gap:1rem; flex-wrap:wrap;">
                <div>
                    <div class="section-title" style="margin-bottom:.25rem;">{safe_text(selected_lead.get('name'), 'ללא שם')}</div>
                    <div class="minor-text">טלפון: {safe_text(selected_lead.get('phone_number'))} · ליד #{selected_lead['lead_id']}</div>
                </div>
                <span class="badge {status_class(selected_lead.get('final_status'))}">{status_label(selected_lead.get('final_status'))}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

        metric_cols = st.columns(4)
        metric_data = [
            ("ציון סופי", selected_lead.get("total_score", 0)),
            ("מטרה", selected_lead.get("goal_score", 0)),
            ("תקציב", selected_lead.get("budget_score", 0)),
            ("דחיפות", selected_lead.get("urgency_score", 0)),
        ]
        for col, (label, value) in zip(metric_cols, metric_data):
            with col:
                st.markdown(
                    f"""
                    <div class="tile">
                        <div class="tile-label">{label}</div>
                        <div class="tile-value">{score_display(value)}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown('<div class="section-card" dir="rtl">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">סיכום ליד</div>', unsafe_allow_html=True)
        st.markdown(safe_text(selected_lead.get("summary"), "עדיין לא נוצר סיכום."))
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-card" dir="rtl">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">היסטוריית שיחה</div>', unsafe_allow_html=True)
        if not messages:
            st.markdown('<div class="empty-state" dir="rtl">אין עדיין הודעות שמורות לליד הזה.</div>', unsafe_allow_html=True)
        else:
            for msg in messages:
                with st.chat_message("assistant" if msg["role"] != "user" else "user"):
                    st.markdown(f"<div dir='rtl'>{msg['content']}</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# =========================
# Main
# =========================
def main() -> None:
    st.set_page_config(
        page_title="Lead Filter Engine",
        page_icon="🔥",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    init_state()
    inject_css()
    render_sidebar()


    service_layer = get_service_layer()

    if st.session_state.page == "chat":
        render_chat_page(service_layer)
    else:
        render_dashboard_page()


if __name__ == "__main__":
    main()