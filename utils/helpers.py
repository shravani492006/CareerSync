# utils/helpers.py
import streamlit as st

def get_css_vars(theme_name, themes_dict):
    t = themes_dict[theme_name]
    return "\n".join(f"    {k}: {v};" for k, v in t.items())

def render_html(html_str: str) -> None:
    st.markdown(html_str, unsafe_allow_html=True)

def pill(text: str, kind: str = "default") -> str:
    return f'<span class="pill pill-{kind}">{text}</span>'

def progress_bar(pct: float, color: str = "var(--accent1)") -> str:
    pct = max(0.0, min(float(pct), 100.0))
    return (
        f'<div class="prog-wrap">'
        f'<div class="prog-fill" style="width:{pct:.1f}%;background:{color};"></div>'
        f'</div>'
    )

def render_pills(items: list, kind: str = "default") -> None:
    if not items:
        render_html('<span style="color: var(--muted)">None Set</span>')
        return
    render_html(" ".join(pill(s, kind) for s in items))

def render_notif(message: str, kind: str = "info") -> None:
    render_html(f'<div class="glass-notif notif-{kind}">{message}</div>')

def render_metric_tile(value: str, label: str) -> None:
    render_html(f"""
    <div class="glass-card style-metric">
        <div class="metric-val">{value}</div>
        <div class="metric-label">{label}</div>
    </div>""")