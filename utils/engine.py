# utils/engine.py
import re
import numpy as np
import streamlit as st
from data.knowledge_base import ROLE_REQUIREMENTS, ROADMAP_DB, DEFAULT_ROADMAP, SALARY_MAP, COMPANY_DB, SKILL_DEPENDENCIES, ALL_SKILLS, CHAT_KNOWLEDGE

def parse_salary_low(salary_str: str) -> float:
    cleaned = salary_str.replace(",", "")
    match = re.search(r"(\d+(?:\.\d+)?)", cleaned)
    return float(match.group(1)) if match else 0.0

def parse_salary_range(salary_str: str):
    cleaned = salary_str.replace(" LPA", "").replace("LPA", "").replace("+", "").strip()
    for sep in ["–", "—", "-"]:
        if sep in cleaned:
            parts = cleaned.split(sep)
            try:
                return float(parts[0].strip()), float(parts[1].strip())
            except (ValueError, IndexError):
                pass
    match = re.search(r"(\d+(?:\.\d+)?)", cleaned)
    if match:
        val = float(match.group(1))
        return val, val * 1.3
    return 0.0, 0.0

def compute_skill_match(user_skills: list, role: str) -> dict:
    req = ROLE_REQUIREMENTS[role]
    all_req = req["core"] + req["tech"] + req["plus"]
    user_lower = [s.lower() for s in user_skills]
    matched = [s for s in all_req if s.lower() in user_lower]
    missing = [s for s in req["core"] + req["tech"] if s.lower() not in user_lower]
    weak    = [s for s in req["plus"] if s.lower() not in user_lower]
    skill_score = (
        sum(3 for s in req["core"] if s.lower() in user_lower) +
        sum(2 for s in req["tech"] if s.lower() in user_lower) +
        sum(1 for s in req["plus"] if s.lower() in user_lower)
    )
    max_score = 3 * len(req["core"]) + 2 * len(req["tech"]) + 1 * len(req["plus"])
    return {
        "matched": matched,
        "missing": missing,
        "weak":    weak,
        "skill_pct": skill_score / max_score if max_score else 0,
    }

@st.cache_data
def predict_placement(cgpa, projects, internships, certs, coding_rating, skills, role):
    req  = ROLE_REQUIREMENTS[role]
    w    = req["weights"]
    sm   = compute_skill_match(skills, role)
    cgpa_norm   = min(cgpa / 10, 1.0)
    proj_norm   = min(projects / 5, 1.0)
    intern_norm = min(internships / 3, 1.0)
    cert_norm   = min(certs / 5, 1.0)
    code_norm   = min(coding_rating / 2500, 1.0)
    skill_norm  = sm["skill_pct"]
    raw = (
        w["cgpa"]          * cgpa_norm   +
        w["projects"]      * (proj_norm * 0.6 + cert_norm * 0.4) +
        w["skills"]        * skill_norm  +
        w["internship"]    * intern_norm +
        w["coding_rating"] * code_norm
    )
    if cgpa < req["min_cgpa"]:
        raw *= 0.85
    prob = round(min(max(raw * 100, 5), 97), 1)
    academic_score = round((cgpa_norm * 0.5 + intern_norm * 0.3 + cert_norm * 0.2) * 100)
    skill_score    = round(skill_norm * 100)
    activity_score = round((proj_norm * 0.5 + code_norm * 0.3 + cert_norm * 0.2) * 100)
    readiness      = round((academic_score * 0.35 + skill_score * 0.45 + activity_score * 0.20))
    return {
        "probability":     prob,
        "academic_score":  academic_score,
        "skill_score":     skill_score,
        "activity_score":  activity_score,
        "readiness":       readiness,
        "skill_match":     sm,
    }

def estimate_time_to_ready(missing_skills, current_prob):
    if current_prob >= 80:
        return 0.5
    days = sum(
        int(ROADMAP_DB.get(s, DEFAULT_ROADMAP)["time"].split()[0])
        for s in missing_skills
    )
    return round(days / 30, 1)

def whatif_simulation(base_prob, new_skills, skills, cgpa, projects, internships, certs, coding_rating, role):
    combined = list(set(skills + new_skills))
    result   = predict_placement(cgpa, projects, internships, certs, coding_rating, combined, role)
    return result["probability"]

def generate_learning_plan(missing_skills):
    plan = []
    day  = 1
    for skill in missing_skills[:8]:
        info = ROADMAP_DB.get(skill, DEFAULT_ROADMAP)
        days = int(info["time"].split()[0])
        plan.append({
            "day_start": day, "day_end": day + days - 1,
            "skill": skill, "resources": info["resources"], "priority": info["priority"],
        })
        day += days
    return plan

def chat_response(user_msg, gap_skills, role, prob):
    msg_l = user_msg.lower().strip()
    for key, resp in CHAT_KNOWLEDGE.items():
        if any(w in msg_l for w in key.split()):
            return resp
    if any(w in msg_l for w in ["missing", "learn", "next", "focus", "gap"]):
        if gap_skills:
            top = gap_skills[:3]
            return f"For the {role} target track, your top priority skill gaps are: {', '.join(top)}. Focus on these first."
        return "Excellent profile metrics! Your parameters completely align with standard requirements."
    if any(w in msg_l for w in ["probability", "chance", "likely", "percent"]):
        tier = "strong" if prob >= 70 else "moderate" if prob >= 50 else "needs refinement"
        return f"Your current baseline profile probability tracks at {prob}% (Classification: {tier})."
    return f"To maximize your trajectory for the {role} career matrix, resolve your highest core skill gaps systematically."

def extract_skills_from_resume(text: str) -> list:
    found = []
    for skill in ALL_SKILLS:
        if re.search(re.escape(skill), text, re.IGNORECASE):
            found.append(skill)
    return list(set(found))

def recommend_top_roles(cgpa, projects, internships, certs, coding_rating, skills):
    scores = {}
    for role in ROLE_REQUIREMENTS:
        result = predict_placement(cgpa, projects, internships, certs, coding_rating, skills, role)
        scores[role] = result["probability"]
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]

def compute_ats_score(user_skills, role, cgpa, projects, internships):
    req = ROLE_REQUIREMENTS[role]
    sm  = compute_skill_match(user_skills, role)
    score = 0
    feedback = []

    skill_pts = round(sm["skill_pct"] * 40)
    score += skill_pts
    if skill_pts < 20:
        feedback.append(("Alert", f"Only {len(sm['matched'])} out of {len(req['core']+req['tech'])} target keywords mapped. Supplement your technology profile."))
    else:
        feedback.append(("Success", "Target keyword saturation parameters verified."))

    score += 15 if cgpa >= 8.0 else 12 if cgpa >= 7.0 else 8
    score += min(projects * 6, 20)
    score += min(internships * 7, 15)
    return min(score, 100), feedback

def compute_salary_prediction(role, prob, cgpa):
    s = SALARY_MAP.get(role, {"base": 5, "mid": 12, "top": 30})
    if prob >= 80:
        low, high, tier = s["mid"], s["top"], "Top Tier"
    elif prob >= 55:
        low, high, tier = round(s["base"] * 1.3, 1), s["mid"], "Mid Tier"
    else:
        low, high, tier = s["base"], round(s["base"] * 1.5, 1), "Entry Level"
    return low, high, tier

def compute_company_eligibility(prob, cgpa, user_skills):
    results = {}
    for category, companies in COMPANY_DB.items():
        cat_results = []
        for co in companies:
            user_has = sum(1 for s in co["skills_needed"] if s in user_skills)
            skill_ok = user_has >= len(co["skills_needed"]) // 2
            if prob >= co["min_prob"] and cgpa >= co["min_cgpa"] and skill_ok:
                eligibility = "Safe"
            elif prob >= co["min_prob"] * 0.75 and cgpa >= co["min_cgpa"] * 0.9:
                eligibility = "Moderate"
            else:
                eligibility = "Dream"
            cat_results.append({
                **co, "eligibility": eligibility,
                "skills_have": user_has, "skills_total": len(co["skills_needed"]),
            })
        results[category] = cat_results
    return results

def get_skill_order(missing_skills):
    ordered = []
    remaining = list(missing_skills)
    max_iters = len(remaining) * 2
    iteration = 0
    while remaining and iteration < max_iters:
        iteration += 1
        for skill in list(remaining):
            deps = SKILL_DEPENDENCIES.get(skill, [])
            deps_met = all(d not in missing_skills or d in ordered for d in deps)
            if deps_met:
                ordered.append(skill)
                remaining.remove(skill)
    ordered.extend(remaining)
    return ordered

def compute_xp(profile):
    xp = 0
    xp += profile.get("cgpa", 0) * 100
    xp += profile.get("projects", 0) * 200
    xp += profile.get("internships", 0) * 300
    xp += len(profile.get("skills", [])) * 50
    xp += profile.get("probability", 0) * 10
    return int(xp)

def get_level(xp):
    if xp < 500:   return 1, "Academic Starter", 500
    if xp < 1500:  return 2, "Profile Builder",  1500
    if xp < 3000:  return 3, "Technical Competitor", 3000
    return 4, "Industry Ready", 15000

def generate_study_plan(missing_skills, hours_per_day):
    plan = []
    for skill in missing_skills[:6]:
        info = ROADMAP_DB.get(skill, DEFAULT_ROADMAP)
        total_days = int(info["time"].split()[0])
        adjusted_days = max(1, round(total_days * (4 / max(hours_per_day, 1))))
        plan.append({
            "skill": skill, "original_days": total_days, "adjusted_days": adjusted_days,
            "hours_total": total_days * 4, "priority": info["priority"], "resources": info["resources"],
        })
    return plan

def compute_behavioral_insights(profile):
    insights = []
    prob   = profile.get("probability", 0)
    skills = profile.get("skills", [])
    cgpa   = profile.get("cgpa", 0)

    if cgpa >= 8.5 and prob < 60:
        insights.append({"type": "warn", "msg": "High CGPA but low probability — your technical skills need attention."})
    if profile.get("projects", 0) == 0 and prob > 40:
        insights.append({"type": "warn", "msg": "You have decent skills but zero projects. Build proof of work immediately."})
    if profile.get("coding_rating", 0) < 400 and "DSA" not in skills:
        insights.append({"type": "warn", "msg": "No DSA detected. This will limit technical evaluation passing rates."})
    if prob >= 80:
        insights.append({"type": "success", "msg": "Excellent profile! Focus on high-tier targeting."})
    if not insights:
        insights.append({"type": "info", "msg": "Profile healthy. Keep mapping skills systematically."})
    return insights

def generate_smart_suggestions(missing_skills, prob, role, projects, internships):
    suggestions = []
    if prob < 50 and missing_skills:
        suggestions.append(f"Target Priority: Dedicate timeline resources to master {missing_skills[0]} first.")
    if projects < 2:
        suggestions.append("Portfolio Build: Introduce another engineering project repository onto your workspace profile.")
    if prob >= 75:
        suggestions.append("Execution Vector: Profile is highly competitive. Begin structuring technical assessment trials.")
    return suggestions