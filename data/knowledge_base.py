# data/knowledge_base.py

ROLE_REQUIREMENTS = {
    "Software Developer": {
        "core":    ["DSA", "OOP", "OS", "DBMS", "Computer Networks", "Git"],
        "tech":    ["Python", "Java", "C++", "SQL", "REST APIs", "Linux"],
        "plus":    ["System Design", "Docker", "Cloud (AWS/GCP)", "CI/CD"],
        "weights": {"cgpa": 0.20, "projects": 0.20, "skills": 0.30, "internship": 0.15, "coding_rating": 0.15},
        "color":   "#c8a8e9",
        "min_cgpa": 6.5,
    },
    "Data Analyst": {
        "core":    ["SQL", "Statistics", "Excel", "Data Visualization", "Python"],
        "tech":    ["Pandas", "Tableau/PowerBI", "NumPy", "Matplotlib", "R"],
        "plus":    ["Machine Learning basics", "BigQuery", "Spark", "Storytelling"],
        "weights": {"cgpa": 0.25, "projects": 0.20, "skills": 0.35, "internship": 0.10, "coding_rating": 0.10},
        "color":   "#f6bcba",
        "min_cgpa": 6.0,
    },
    "AI/ML Engineer": {
        "core":    ["Python", "Mathematics", "Statistics", "ML Algorithms", "Deep Learning"],
        "tech":    ["TensorFlow/PyTorch", "Scikit-learn", "Pandas", "NumPy", "SQL"],
        "plus":    ["NLP", "Computer Vision", "MLOps", "Hugging Face", "LLMs"],
        "weights": {"cgpa": 0.20, "projects": 0.25, "skills": 0.30, "internship": 0.10, "coding_rating": 0.15},
        "color":   "#e3aadd",
        "min_cgpa": 7.0,
    },
    "Web Developer": {
        "core":    ["HTML", "CSS", "JavaScript", "React/Vue", "REST APIs", "Git"],
        "tech":    ["Node.js", "SQL/NoSQL", "TypeScript", "Responsive Design"],
        "plus":    ["Next.js", "Docker", "Testing", "Performance Optimization"],
        "weights": {"cgpa": 0.15, "projects": 0.30, "skills": 0.35, "internship": 0.12, "coding_rating": 0.08},
        "color":   "#c3c7f4",
        "min_cgpa": 5.5,
    },
    "DevOps Engineer": {
        "core":    ["Linux", "Docker", "Kubernetes", "CI/CD", "Git", "Bash Scripting"],
        "tech":    ["AWS/GCP/Azure", "Terraform", "Jenkins", "Ansible", "Monitoring"],
        "plus":    ["Security", "Networking", "Python automation", "Helm"],
        "weights": {"cgpa": 0.15, "projects": 0.20, "skills": 0.35, "internship": 0.20, "coding_rating": 0.10},
        "color":   "#6667ab",
        "min_cgpa": 6.0,
    },
}

ALL_SKILLS = sorted(set(
    s for r in ROLE_REQUIREMENTS.values()
    for cat in ["core", "tech", "plus"] for s in r[cat]
))

ROADMAP_DB = {
    "DSA":               {"time": "45 days",  "resources": ["LeetCode", "Striver Sheet", "GeeksforGeeks"], "priority": "Critical"},
    "Python":            {"time": "14 days",  "resources": ["Python Docs", "Real Python"], "priority": "Critical"},
    "SQL":               {"time": "10 days",  "resources": ["SQLZoo", "LeetCode SQL"], "priority": "Critical"},
    "Machine Learning basics": {"time": "30 days", "resources": ["Andrew Ng Course", "Kaggle Learn"], "priority": "Important"},
    "Deep Learning":     {"time": "30 days",  "resources": ["Fast.ai", "PyTorch Tutorials"], "priority": "Important"},
    "System Design":     {"time": "21 days",  "resources": ["System Design Primer", "Grokking Architecture"], "priority": "Important"},
    "Docker":            {"time": "7 days",   "resources": ["Docker Docs", "TechWorld with Nana"], "priority": "Good-to-have"},
    "Git":               {"time": "3 days",   "resources": ["Pro Git Book", "GitHub Learning Lab"], "priority": "Critical"},
    "React/Vue":         {"time": "21 days",  "resources": ["React Docs", "The Odin Project"], "priority": "Important"},
    "Statistics":        {"time": "14 days",  "resources": ["Khan Academy", "StatQuest"], "priority": "Important"},
    "Tableau/PowerBI":   {"time": "10 days",  "resources": ["Tableau Public", "Microsoft Learn"], "priority": "Good-to-have"},
    "Linux":             {"time": "7 days",   "resources": ["Linux Journey", "Command Line Book"], "priority": "Important"},
    "Kubernetes":        {"time": "14 days",  "resources": ["Kubernetes Docs", "KodeKloud"], "priority": "Important"},
    "DBMS":              {"time": "10 days",  "resources": ["NPTEL DBMS", "CMU 15-445"], "priority": "Critical"},
    "Computer Networks": {"time": "10 days",  "resources": ["Tanenbaum Book", "NPTEL Networking"], "priority": "Important"},
    "OS":                {"time": "14 days",  "resources": ["Three Easy Pieces", "NPTEL OS"], "priority": "Critical"},
    "NLP":               {"time": "21 days",  "resources": ["Hugging Face Course", "Stanford CS224N"], "priority": "Good-to-have"},
    "TensorFlow/PyTorch":{"time": "14 days",  "resources": ["TensorFlow Basics", "PyTorch Docs"], "priority": "Important"},
    "AWS/GCP/Azure":     {"time": "14 days",  "resources": ["AWS Free Tier", "Google Qwiklabs"], "priority": "Important"},
}

DEFAULT_ROADMAP = {"time": "7 days", "resources": ["Documentation", "Video Tutorials"], "priority": "Good-to-have"}

CHAT_KNOWLEDGE = {
    "what should i learn next": "Prioritize your Critical items listed in your gap analysis roadmap first. Focus on the core foundational tools.",
    "how to improve cgpa": "While historic values are fixed, adding prominent micro-credentials and software deployments completely balances a profile gap.",
    "how many projects": "Aim to compile 2 to 3 heavily customized software architectures deployed with public operational links.",
    "internship tips": "Leverage specialized aggregators like LinkedIn or Internshala. Even introductory baseline freelance builds provide structural validation vectors.",
}

COMPANY_DB = {
    "Service-Based": [
        {"name": "TCS",        "min_cgpa": 6.0, "min_prob": 30, "skills_needed": ["DSA", "SQL", "Python"], "package": "3.5-7 LPA"},
        {"name": "Infosys",    "min_cgpa": 6.0, "min_prob": 30, "skills_needed": ["DSA", "OOP", "SQL"],    "package": "3.6-6.5 LPA"},
        {"name": "Wipro",      "min_cgpa": 6.0, "min_prob": 28, "skills_needed": ["Python", "SQL", "Git"], "package": "3.5-6 LPA"},
    ],
    "Product-Based (Mid)": [
        {"name": "Zoho",       "min_cgpa": 7.0, "min_prob": 55, "skills_needed": ["DSA", "OOP", "Python"], "package": "6-14 LPA"},
        {"name": "Freshworks", "min_cgpa": 7.0, "min_prob": 55, "skills_needed": ["DSA", "System Design", "OOP"], "package": "8-18 LPA"},
        {"name": "Paytm",      "min_cgpa": 6.5, "min_prob": 50, "skills_needed": ["DSA", "Python", "SQL"],  "package": "6-15 LPA"},
    ],
    "FAANG / Dream": [
        {"name": "Google",     "min_cgpa": 8.0, "min_prob": 80, "skills_needed": ["DSA", "System Design", "OS", "Computer Networks"], "package": "40-80 LPA"},
        {"name": "Microsoft",  "min_cgpa": 8.0, "min_prob": 78, "skills_needed": ["DSA", "System Design", "OOP", "OS"], "package": "35-65 LPA"},
        {"name": "Amazon",     "min_cgpa": 7.5, "min_prob": 72, "skills_needed": ["DSA", "System Design", "OOP", "Cloud (AWS/GCP)"], "package": "30-55 LPA"},
    ],
}

SKILL_DEPENDENCIES = {
    "System Design":     ["DSA", "OS", "Computer Networks", "DBMS"],
    "Deep Learning":     ["Python", "Statistics", "Machine Learning basics"],
    "Machine Learning basics": ["Python", "Statistics", "SQL"],
    "NLP":               ["Python", "Deep Learning", "Statistics"],
    "TensorFlow/PyTorch":["Python", "Machine Learning basics", "Deep Learning"],
}

SALARY_MAP = {
    "Software Developer": {"base": 6, "mid": 15, "top": 40},
    "Data Analyst":       {"base": 5, "mid": 12, "top": 25},
    "AI/ML Engineer":     {"base": 8, "mid": 20, "top": 50},
    "Web Developer":      {"base": 4, "mid": 10, "top": 20},
    "DevOps Engineer":    {"base": 7, "mid": 18, "top": 35},
}

INTERVIEW_QUESTIONS = {
    "Software Developer": {
        "Technical": ["Explain the difference between a stack and a queue.", "What is Big-O notation? Give examples.", "Explain OOP principles with examples."],
        "Behavioral": ["Tell me about a challenging project you built.", "How do you handle code reviews?"],
        "Coding": ["Reverse a linked list.", "Find the longest common subsequence."]
    },
    "Data Analyst": {
        "Technical": ["What is the difference between INNER JOIN and OUTER JOIN?", "Explain window functions in SQL."],
        "Behavioral": ["Describe a data analysis project you are proud of."],
        "Coding": ["Write a SQL query to find the top 5 customers by revenue."]
    },
    "AI/ML Engineer": {
        "Technical": ["Explain bias-variance tradeoff.", "What is gradient descent? Explain types."],
        "Behavioral": ["Describe an ML project you built end-to-end."],
        "Coding": ["Implement linear regression from scratch."]
    },
    "Web Developer": {
        "Technical": ["Explain the difference between let, const, and var.", "What is event bubbling in JavaScript."],
        "Behavioral": ["Describe a web app you built from scratch."],
        "Coding": ["Build a debounce function in JavaScript."]
    },
    "DevOps Engineer": {
        "Technical": ["Explain the difference between Docker and a VM.", "What is Kubernetes and why use it?"],
        "Behavioral": ["Describe an incident you handled in production."],
        "Coding": ["Write a Dockerfile for a Python Flask app."]
    }
}

BADGES = {
    "Project Builder":    {"desc": "Built 3+ projects",    "condition": lambda p: p.get("projects", 0) >= 3},
    "DSA Master":         {"desc": "Knows DSA skill",       "condition": lambda p: "DSA" in p.get("skills", [])},
    "Cloud Certified":    {"desc": "Has cloud skills",      "condition": lambda p: any("Cloud" in s or "AWS" in s for s in p.get("skills", []))},
    "Intern Veteran":     {"desc": "2+ internships",        "condition": lambda p: p.get("internships", 0) >= 2},
    "Cert Collector":     {"desc": "3+ certifications",     "condition": lambda p: p.get("certs", 0) >= 3},
    "Placement Ready":    {"desc": "Probability 75%+",      "condition": lambda p: p.get("probability", 0) >= 75},
}