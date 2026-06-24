# utils/reporting.py
import io
from datetime import datetime
from data.knowledge_base import ROADMAP_DB, DEFAULT_ROADMAP, BADGES
from utils.engine import compute_salary_prediction

def export_report_pdf(profile, result):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.colors import HexColor
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=60, bottomMargin=40)
        styles = getSampleStyleSheet()
        story  = []

        title_style = ParagraphStyle("title", parent=styles["Title"], fontSize=22, textColor=HexColor("#c8a8e9"), spaceAfter=6)
        head_style  = ParagraphStyle("head",  parent=styles["Heading2"], fontSize=14, textColor=HexColor("#6667ab"), spaceAfter=4)
        body_style  = ParagraphStyle("body",  parent=styles["Normal"], fontSize=10, textColor=HexColor("#210635"), spaceAfter=3)
        sub_style   = ParagraphStyle("sub",   parent=styles["Normal"], fontSize=9,  textColor=HexColor("#64748b"), spaceAfter=2)

        story.append(Paragraph("CareerSync — Career Intelligence Report", title_style))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%d %b %Y %H:%M')}  |  Role: {profile['role']}", sub_style))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor("#c8a8e9")))
        story.append(Spacer(1, 12))

        story.append(Paragraph("Profile Summary", head_style))
        profile_data = [
            ["Metric", "Value"],
            ["CGPA", str(profile["cgpa"])],
            ["Projects", str(profile["projects"])],
            ["Internships", str(profile["internships"])],
            ["Certifications", str(profile["certs"])],
            ["Target Role", profile["role"]],
            ["Placement Probability", f"{result['probability']}%"],
        ]
        t = Table(profile_data, colWidths=[3 * inch, 3.5 * inch])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#c8a8e9")),
            ("TEXTCOLOR",  (0, 0), (-1, 0), HexColor("#210635")),
            ("GRID",       (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
        ]))
        story.append(t)

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception:
        return None