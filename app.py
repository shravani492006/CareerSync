# app.py
import streamlit as st
import io
import json
import random
from datetime import datetime, timedelta, date
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from supabase import Client, create_client

# Multi-file architectural module imports
from data.knowledge_base import (
    ALL_SKILLS,
    BADGES,
    DEFAULT_ROADMAP,
    INTERVIEW_QUESTIONS,
    ROADMAP_DB,
    ROLE_REQUIREMENTS,
)
from utils.helpers import (
    get_css_vars,
    pill,
    progress_bar,
    render_html,
    render_metric_tile,
    render_notif,
    render_pills,
)
from utils.reporting import export_report_pdf

# Import predictive calculations from the analytical engine
from utils.engine import (
    compute_ats_score,
    compute_behavioral_insights,
    compute_company_eligibility,
    compute_salary_prediction,
    compute_xp,
    estimate_time_to_ready,
    extract_skills_from_resume,
    generate_learning_plan,
    generate_smart_suggestions,
    generate_study_plan,
    get_level,
    get_skill_order,
    predict_placement,
    whatif_simulation,
)

st.set_page_config(
    page_title="CareerSync", layout="wide", initial_sidebar_state="expanded"
)

if "theme" not in st.session_state:
    st.session_state.theme = "dark"
if "interview_notes" not in st.session_state:
    st.session_state.interview_notes = {}

THEMES = {
    "dark": {
        "--bg": "#210635",
        "--surface": "rgba(66, 13, 75, 0.4)",
        "--border": "rgba(200, 168, 233, 0.2)",
        "--accent1": "#c8a8e9",
        "--accent2": "#e3aadd",
        "--accent3": "#6667ab",
        "--text": "#f4e7fb",
        "--muted": "#94a3b8",
        "--card-bg": "rgba(33, 6, 53, 0.5)",
        "--prog-bg": "#420d4b",
    },
    "light": {
        "--bg": "#f4e7fb",
        "--surface": "rgba(242, 221, 220, 0.6)",
        "--border": "rgba(246, 188, 186, 0.4)",
        "--accent1": "#6667ab",
        "--accent2": "#f6bcba",
        "--accent3": "#c3c7f4",
        "--text": "#210635",
        "--muted": "#64748b",
        "--card-bg": "rgba(255, 255, 255, 0.75)",
        "--prog-bg": "#f2dddc",
    },
}

st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@700&family=Syne:wght@600;700;800&display=swap');
:root {{ {get_css_vars(st.session_state.theme, THEMES)} }}
html, body, [class*="css"] {{ background-color: var(--bg) !important; color: var(--text) !important; font-family: 'Syne', sans-serif; }}
.stApp {{ background: var(--bg); }}

section[data-testid="stSidebar"] {{ background: var(--surface) !important; backdrop-filter: blur(20px); border-right: 1px solid var(--border); }}
h1, h2, h3, h4 {{ font-family: 'Syne', sans-serif !important; font-weight: 800; }}

/* Glassmorphism Structural Formatting Cards */
.glass-card {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
    transition: transform 0.2s, border-color 0.2s;
}}
.glass-card:hover {{ border-color: var(--accent1); transform: translateY(-1px); }}

.style-metric {{ text-align: center; }}
.metric-val {{ font-size: 2.6rem; font-weight: 800; font-family: 'Space Mono', monospace; color: var(--accent1); }}
.metric-label {{ font-size: .8rem; color: var(--muted); text-transform: uppercase; font-weight: 700; margin-top: .2rem; }}

.pill {{ display: inline-block; padding: .3rem .75rem; border-radius: 8px; font-size: .75rem; font-weight: 700; margin: .2rem; border: 1px solid var(--border); background: var(--surface); color: var(--text); }}
.pill-green  {{ color: #34d399; background: rgba(52, 211, 153, 0.1); }}
.pill-red    {{ color: #f87171; background: rgba(248, 113, 113, 0.1); }}
.pill-yellow {{ color: #fbbf24; background: rgba(251, 191, 36, 0.1); }}

.prog-wrap {{ background: var(--prog-bg); border-radius: 999px; height: 10px; overflow: hidden; margin: .5rem 0; }}
.prog-fill  {{ height: 100%; border-radius: 999px; transition: width .6s ease; }}

.glass-notif {{ padding: 1rem; border-radius: 12px; margin-bottom: .6rem; border-left: 4px solid var(--accent1); background: var(--card-bg); font-size: .9rem; }}
.notif-warn {{ border-left-color: var(--accent2); }}
.notif-success {{ border-left-color: #10b981; }}

.xp-bar-wrap {{ background: var(--prog-bg); border-radius: 999px; height: 14px; overflow: hidden; margin: .4rem 0; }}
.xp-bar-fill {{ height: 100%; border-radius: 999px; background: linear-gradient(90deg, var(--accent3), var(--accent1)); }}
.badge {{ display: inline-flex; padding: .4rem .9rem; border-radius: 10px; font-size: .8rem; font-weight: 700; border: 1px solid var(--border); background: var(--surface); margin: .25rem; }}

div[data-baseweb="tab-list"] {{ background: var(--card-bg) !important; border-radius: 12px; padding: 6px; border: 1px solid var(--border); }}
div[data-baseweb="tab"] {{ border-radius: 8px !important; font-weight: 700 !important; color: var(--muted) !important; }}
div[data-baseweb="tab"][aria-selected="true"] {{ background: var(--surface) !important; color: var(--text) !important; }}
button[kind="primary"] {{ background: linear-gradient(135deg, var(--accent1), var(--accent3)) !important; color: #fff !important; border-radius: 8px !important; font-weight: 700 !important; border: none !important; }}
</style>
""",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# 🔌 SECURED SUPABASE CLOUD CONNECTION INITIALIZATION
# ─────────────────────────────────────────────────────────────────────────────
# Safely parsing credentials directly from Streamlit's secrets tracking module
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]


@st.cache_resource
def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)


supabase = get_supabase_client()

if "user" not in st.session_state:
    st.session_state.user = None
if "result" not in st.session_state:
    st.session_state.result = None
if "profile" not in st.session_state:
    st.session_state.profile = {}
if "streak_data" not in st.session_state:
    st.session_state.streak_data = {
        "last_date": None,
        "current_streak": 0,
        "max_streak": 0,
    }
if "xp_total" not in st.session_state:
    st.session_state.xp_total = 0
if "displayed_interview_questions" not in st.session_state:
    st.session_state.displayed_interview_questions = None

# Render Cloud Gateway authorization locks if no user session token is present
if st.session_state.user is None:
    st.markdown(
        "<h2 style='text-align:center;'>Welcome to CareerSync</h2>",
        unsafe_allow_html=True,
    )

    auth_tab1, auth_tab2 = st.tabs(["Sign In", "Create Account"])

    with auth_tab1:
        email = st.text_input("Student Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Sign In to Workspace", type="primary"):
            try:
                res = supabase.auth.sign_in_with_password(
                    {"email": email, "password": password}
                )
                st.session_state.user = res.user
                st.success("Authentication verified! Launching console...")
                st.rerun()
            except Exception as e:
                st.error(f"Authentication rejected: {e}")

    with auth_tab2:
        reg_email = st.text_input("Student Email", key="reg_email")
        reg_password = st.text_input("Create Password", type="password", key="reg_pass")
        if st.button("Register Account", type="primary"):
            try:
                res = supabase.auth.sign_up(
                    {"email": reg_email, "password": reg_password}
                )
                st.info(
                    "Verification transmission deployed! Confirm via incoming link, then authenticate."
                )
            except Exception as e:
                st.error(f"Registration failure bounds triggered: {e}")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# 📊 APP DASHBOARD CORE LAYOUT EXECUTION
# ─────────────────────────────────────────────────────────────────────────────
user_id = st.session_state.user.id

with st.sidebar:
    st.markdown("## CareerSync")
    st.caption(f"Authenticated: {st.session_state.user.email}")

    if st.button("Sign Out of Workspace", use_container_width=True):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.session_state.result = None
        st.rerun()

    st.markdown("---")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        if st.button("Dark View", use_container_width=True):
            st.session_state.theme = "dark"
    with col_t2:
        if st.button("Light View", use_container_width=True):
            st.session_state.theme = "light"

    st.markdown("---")
    st.markdown("### Profile Backup System")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.button("Save Profile", use_container_width=True) and st.session_state.profile:
            profile_json = json.dumps(st.session_state.profile, indent=2)
            st.download_button(
                "Export JSON",
                profile_json,
                file_name="careersync_profile.json",
                mime="application/json",
                use_container_width=True,
            )
    with col_s2:
        uploaded_profile = st.file_uploader(
            "Import JSON", type=["json"], label_visibility="collapsed"
        )
        if uploaded_profile:
            try:
                loaded = json.load(uploaded_profile)
                st.session_state.profile = loaded
                if "probability" in loaded:
                    st.success("Config imported successfully.")
            except Exception as e:
                st.error(f"Config read error: {e}")

    st.markdown("---")
    st.markdown("### Automated Resume Intake")
    resume_file = st.file_uploader(
        "Drop Resume (PDF/TXT)", type=["pdf", "txt"], label_visibility="collapsed"
    )
    auto_skills = []
    if resume_file:
        try:
            if resume_file.type == "application/pdf":
                import PyPDF2

                reader = PyPDF2.PdfReader(io.BytesIO(resume_file.read()))
                text = " ".join(p.extract_text() or "" for p in reader.pages)
            else:
                text = resume_file.read().decode("utf-8", errors="ignore")
            auto_skills = extract_skills_from_resume(text)
            if auto_skills:
                st.success(f"Fetched {len(auto_skills)} profile skills automatically.")
        except Exception as e:
            st.error(f"Parsing crash: {e}")

    st.markdown("---")
    st.markdown("### Personalized Profile Parameters")
    cgpa = st.slider("CGPA Tracker", 0.0, 10.0, 8.4, 0.1)
    projects = st.number_input("Projects Logged", 0, 20, 3)
    internships = st.number_input("Internships Completed", 0, 10, 1)
    certs = st.number_input("Certifications", 0, 20, 3)
    coding_rating = st.slider("Competitive Coding Rating", 0, 2500, 1450, 50)

    st.markdown("### Skill Registry")
    assigned_defaults = (
        auto_skills if auto_skills else ["Python", "Java", "SQL", "Git"]
    )
    user_skills = st.multiselect(
        "Assign Active Tokens",
        options=ALL_SKILLS,
        default=[s for s in assigned_defaults if s in ALL_SKILLS],
        label_visibility="collapsed",
    )

    st.markdown("### Target Evaluation Objective")
    role = st.selectbox(
        "Career Track Focus",
        list(ROLE_REQUIREMENTS.keys()),
        index=0,
        label_visibility="collapsed",
    )
    st.markdown("---")

    if (
        st.button("Synchronize Profiler", use_container_width=True, type="primary")
        or st.session_state.result is None
    ):
        actual_skills = (
            user_skills if user_skills else ["Python", "Java", "SQL", "Git"]
        )
        result = predict_placement(
            cgpa, projects, internships, certs, coding_rating, actual_skills, role
        )
        sm = result["skill_match"]
        st.session_state.result = result
        st.session_state.profile = {
            "cgpa": cgpa,
            "projects": projects,
            "internships": internships,
            "certs": certs,
            "coding_rating": coding_rating,
            "skills": actual_skills,
            "role": role,
            "months": estimate_time_to_ready(sm["missing"], result["probability"]),
            "plan": generate_learning_plan(sm["missing"]),
            "missing": sm["missing"],
            "weak": sm["weak"],
            "matched": sm["matched"],
            "probability": result["probability"],
        }
        st.session_state.xp_total = compute_xp(st.session_state.profile)
        sd = st.session_state.streak_data
        today = str(date.today())
        if sd["last_date"] != today:
            sd["current_streak"] = (
                sd["current_streak"] + 1
                if sd["last_date"] == str(date.today() - timedelta(days=1))
                else 1
            )
            sd["last_date"] = today
            sd["max_streak"] = max(sd["max_streak"], sd["current_streak"])
        st.session_state.displayed_interview_questions = None

R = st.session_state.result
P = st.session_state.profile
role, prob = P["role"], R["probability"]

insights = compute_behavioral_insights(P)
with st.expander("System Profile Bulletins", expanded=False):
    for ins in insights:
        render_notif(ins["msg"], ins["type"])

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    render_metric_tile(f"{prob}%", "Placement Probability")
with c2:
    render_metric_tile(f"{R['readiness']}/100", "Readiness Evaluation")
with c3:
    render_metric_tile(f"{R['skill_score']}%", "Keyword Congruence")
with c4:
    render_metric_tile(f"{R['academic_score']}%", "Academic Standing")
with c5:
    render_metric_tile(f"{P['months']} mo", "Delta Learning Window")

xp = st.session_state.xp_total
lvl, lvl_name, lvl_max = get_level(xp)
lvl_prev = {1: 0, 2: 0, 3: 500, 4: 1500}.get(lvl, 0)
xp_progress = min((xp - lvl_prev) / max(lvl_max - lvl_prev, 1) * 100, 100)
streak = st.session_state.streak_data["current_streak"]

col_xp, col_str = st.columns([3, 1])
with col_xp:
    render_html(
        f'<div class="glass-card" style="padding: 1rem;"><div style="display:flex;align-items:center;gap:1rem;"><span style="font-family:\'Space Mono\';color:var(--accent1);font-weight:700">LV.{lvl}</span><div style="flex:1"><div style="display:flex;justify-content:space-between;font-size:.78rem;font-weight:700;"><span>{lvl_name}</span><span>{xp:,} / {lvl_max:,} XP</span></div><div class="xp-bar-wrap"><div class="xp-bar-fill" style="width:{xp_progress:.1f}%"></div></div></div></div></div>'
    )
with col_str:
    render_html(
        f'<div class="glass-card style-metric" style="padding:.7rem 1rem;"><div style="font-size:1.6rem;font-family:\'Space Mono\';font-weight:700;color:var(--accent2);">🔥 {streak}</div><div class="metric-label" style="font-size:0.65rem;margin-top:0;">Evaluation Activity Streak</div></div>'
    )

# Clean, Consolidated 6-Tab Interface Layer
tabs = st.tabs(
    [
        "📊 Overview Dashboard",
        "🧠 Skill Analytics",
        "🗺️ Career Roadmap",
        "🏢 Company Matching",
        "📝 Application Optimization",
        "🎤 Interview Checkpoints",
    ]
)

# TAB 1 - OVERVIEW DASHBOARD
with tabs[0]:
    cl, cr = st.columns([1.2, 1])
    with cl:
        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=prob,
                number={"suffix": "%", "font": {"color": "var(--text)", "family": "Space Mono"}},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": "var(--muted)"},
                    "bar": {"color": "var(--accent1)"},
                    "bgcolor": "rgba(0,0,0,0)",
                },
            )
        )
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=240, margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

        roles_all = list(ROLE_REQUIREMENTS.keys())
        probs_all = [
            predict_placement(
                P["cgpa"],
                P["projects"],
                P["internships"],
                P["certs"],
                P["coding_rating"],
                P["skills"],
                r,
            )["probability"]
            for r in roles_all
        ]
        fig_bar = go.Figure(
            go.Bar(
                x=probs_all,
                y=roles_all,
                orientation="h",
                marker_color=[ROLE_REQUIREMENTS[r]["color"] for r in roles_all],
            )
        )
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=220,
            xaxis={"gridcolor": "var(--border)", "color": "var(--muted)"},
            yaxis={"color": "var(--text)"},
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    with cr:
        st.markdown("#### Market Valuation & Tasks")
        low, high, tier = compute_salary_prediction(role, prob, P["cgpa"])
        st.info(f"Projected Valuation Scope: ₹{low} – ₹{high} LPA (Tier: {tier})")

        for s in generate_smart_suggestions(
            P["missing"], prob, role, P["projects"], P["internships"]
        ):
            render_notif(s, "info")
        pdf_bytes = export_report_pdf(P, R)
        if pdf_bytes:
            st.download_button(
                "Export Config Summary PDF",
                pdf_bytes,
                file_name="careersync_report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

# TAB 2 - SKILL ANALYTICS
with tabs[1]:
    c_a, c_b, c_c = st.columns(3)
    with c_a:
        render_html('<div class="glass-card"><b>Verified Match Credentials</b><br><br>')
        render_pills(P["matched"], "green")
        render_html("</div>")
    with c_b:
        render_html('<div class="glass-card"><b>Core Target Deficiencies</b><br><br>')
        render_pills(P["missing"], "red")
        render_html("</div>")
    with c_c:
        render_html(
            '<div class="glass-card"><b>Secondary Trajectory Additions</b><br><br>'
        )
        render_pills(P["weak"], "yellow")
        render_html("</div>")

    st.markdown("#### Interactive Optimization Testing")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        remaining = [s for s in ALL_SKILLS if s not in P["skills"]]
        test_skills = st.multiselect(
            "Simulate adding sample qualifications to your profile:", remaining
        )
        if test_skills:
            n_p = whatif_simulation(
                prob,
                test_skills,
                P["skills"],
                P["cgpa"],
                P["projects"],
                P["internships"],
                P["certs"],
                P["coding_rating"],
                role,
            )
            st.metric(
                "Adjusted Placement Forecast",
                f"{n_p}%",
                f"+{round(n_p - prob, 1)}% positive tracking shift",
            )
    with col_s2:
        if P["missing"]:
            skills_to_test = P["missing"][:5]
            gains = [
                round(
                    whatif_simulation(
                        prob,
                        [sk],
                        P["skills"],
                        P["cgpa"],
                        P["projects"],
                        P["internships"],
                        P["certs"],
                        P["coding_rating"],
                        role,
                    )
                    - prob,
                    1,
                )
                for sk in skills_to_test
            ]
            fig_roi = go.Figure(
                go.Bar(
                    x=gains,
                    y=skills_to_test,
                    orientation="h",
                    marker_color="var(--accent2)",
                )
            )
            fig_roi.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=180,
                xaxis={"color": "var(--muted)"},
                yaxis={"color": "var(--text)"},
                margin=dict(t=5, b=5),
            )
            st.plotly_chart(fig_roi, use_container_width=True)

# TAB 3 - CAREER ROADMAP
with tabs[2]:
    col_r1, col_r2 = st.columns([1.2, 1])
    with col_r1:
        st.markdown("#### Curated Preparation Milestones")
        if P["missing"]:
            for i, step in enumerate(P["plan"][:5]):
                info = ROADMAP_DB.get(step["skill"], DEFAULT_ROADMAP)
                render_html(
                    f'<div class="glass-card"><b>Phase {i+1}: {step["skill"]}</b> ({info["time"]})<br><small style="color:var(--muted)">Resource: {", ".join(info["resources"])}</small></div>'
                )
        else:
            st.success("All operational technology indicators mapped cleanly.")
    with col_r2:
        st.markdown("#### Checklist Verification Console")
        if P["missing"]:
            for skill in P["missing"][:4]:
                st.checkbox(
                    f"Deploy structural project repo using {skill}", key=f"chk_{skill}"
                )
            hours = st.slider("Daily Hours Allocation", 1, 10, 3)
            df_c = pd.DataFrame(
                generate_study_plan(get_skill_order(P["missing"]), hours)
            )
            st.dataframe(df_c, use_container_width=True, hide_index=True)

# TAB 4 - COMPANY MATCHING
with tabs[3]:
    eligibility = compute_company_eligibility(prob, P["cgpa"], P["skills"])
    for cat, cos in eligibility.items():
        st.markdown(f"#### {cat}")
        for co in cos:
            status_low = co["eligibility"].lower()
            render_html(
                f'<div class="glass-card" style="display:flex; justify-content:space-between; margin-bottom:.5rem;"><div><b>{co["name"]}</b> <span style="color:var(--muted); font-size:0.8rem;">({co["package"]})</span></div><div class="eligibility-{status_low}">{co["eligibility"]}</div></div>'
            )

# TAB 5 - APPLICATION OPTIMIZATION
with tabs[4]:
    col_a1, col_a2 = st.columns([1.2, 1])
    with col_a1:
        score, feedback = compute_ats_score(
            P["skills"], role, P["cgpa"], P["projects"], P["internships"]
        )
        st.metric("ATS Verification Level Match", f"{score}/100")

        if score < 60:
            st.warning(
                "⚠️ Critical Optimization Required: Your resume structure is light on core keywords. Shift skills to the top 1/3 section of your page layouts."
            )
        elif score < 85:
            st.info(
                "💡 Pro Tip: Boost impact metrics. Standardize your project bulletins using quantitative action metrics (e.g., 'Reduced processing latency by 20%')."
            )
        else:
            st.success(
                "🏆 Excellent Formatting: Structural alignment falls inside optimal hiring bounds."
            )

        for f in feedback:
            render_notif(f[1], "info")
    with col_a2:
        st.markdown("#### Earned Milestone Achievements")
        for b, inf in BADGES.items():
            if inf["condition"](P):
                render_html(f'<span class="badge" style="border-color:var(--accent1);">{b}</span>')

        st.markdown("<br>#### System Cohort Distributions", unsafe_allow_html=True)
        fig_hist = go.Figure(
            go.Histogram(
                x=np.random.normal(7.3, 0.7, 200).clip(4, 10),
                marker_color="var(--accent3)",
                opacity=0.7,
            )
        )
        fig_hist.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=150,
            xaxis={"color": "var(--muted)"},
            yaxis={"showgrid": False},
            margin=dict(t=5, b=5),
        )
        st.plotly_chart(fig_hist, use_container_width=True)

# TAB 6 - INTERVIEW CHECKPOINTS
with tabs[5]:
    q_type = st.selectbox(
        "Checkpoint Focus Arena", ["Technical", "Behavioral", "Coding"]
    )
    q_list = INTERVIEW_QUESTIONS.get(role, INTERVIEW_QUESTIONS["Software Developer"])[
        q_type
    ]
    n_show = st.number_input(
        "Display Allocation Upper Bounds",
        1,
        len(q_list),
        min(4, len(q_list)) if len(q_list) >= 4 else len(q_list),
    )

    if (
        st.session_state.displayed_interview_questions is None
        or st.session_state.displayed_interview_questions.get("category") != q_type
        or st.session_state.displayed_interview_questions.get("count") != int(n_show)
    ):
        st.session_state.displayed_interview_questions = {
            "category": q_type,
            "count": int(n_show),
            "questions": q_list[: int(n_show)],
        }

    displayed_qs = st.session_state.displayed_interview_questions["questions"]

    st.markdown("#### Active Interactive Prep Fields")
    for q in displayed_qs:
        st.info(q)
        existing_note = st.session_state.interview_notes.get(q, "")
        user_notes = st.text_input(
            f"Outline response architecture (STAR framework) for: '{q[:30]}...'",
            value=existing_note,
            key=f"note_{q}",
        )
        if user_notes:
            st.session_state.interview_notes[q] = user_notes

    if st.session_state.interview_notes:
        st.markdown("---")
        prep_data = [
            {"Question Prompt": q, "My Structured Notes": n}
            for q, n in st.session_state.interview_notes.items()
        ]
        df_prep = pd.DataFrame(prep_data)
        csv_buffer = io.StringIO()
        df_prep.to_csv(csv_buffer, index=False)
        st.download_button(
            label="📥 Export Preparation History CSV",
            data=csv_buffer.getvalue(),
            file_name="careersync_interview_prep.csv",
            mime="text/csv",
            use_container_width=True,
        )

    if st.button("Generate Trial Random Challenge Prompt"):
        st.warning(random.choice(q_list))