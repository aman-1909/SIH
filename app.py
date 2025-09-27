import streamlit as st
import pandas as pd
import os

# Set up page
st.set_page_config(page_title="Internship Matching Engine", layout="wide")

# Load Data
@st.cache_data
def load_data():
    base_dir = os.path.dirname(__file__)
    candidates = pd.read_csv(os.path.join(base_dir, "candidates.csv"))
    internships = pd.read_csv(os.path.join(base_dir, "internships.csv"))
    return candidates, internships

candidates, internships = load_data()

st.title("🎯 AI-powered Internship Matching Engine")

# Sidebar for candidate selection
st.sidebar.header("Candidate Selection")
candidate_id = st.sidebar.selectbox("Choose a Candidate ID", candidates["id"].tolist())

# Get candidate details
candidate = candidates[candidates["id"] == candidate_id].iloc[0]
st.subheader(f"👤 Candidate Profile: {candidate['name']}")
st.write(f"**Skills:** {candidate['skills']}")
st.write(f"**Qualification:** {candidate['qualification']}")
st.write(f"**Preferred Location:** {candidate['location_preference']}")
st.write(f"**Sector Interest:** {candidate['sector_interest']}")

# Simple Matching Logic
def match_internships(candidate, internships):
    matches = []
    for _, row in internships.iterrows():
        score = 0

        # Skill match
        candidate_skills = set(candidate["skills"].lower().split(", "))
        internship_skills = set(row["required_skills"].lower().split(", "))
        skill_match = len(candidate_skills & internship_skills)
        score += skill_match

        # Qualification match
        if candidate["qualification"].lower() in row["qualification_required"].lower():
            score += 1

        # Location preference
        if candidate["location_preference"].lower() == row["location"].lower():
            score += 1

        # Sector interest
        if candidate["sector_interest"].lower() == row["sector"].lower():
            score += 1

        matches.append((row["title"], row["company"], score, row["location"], row["sector"]))

    # Sort by score (highest first)
    matches = sorted(matches, key=lambda x: x[2], reverse=True)
    return matches[:5]  # top 5 matches

matches = match_internships(candidate, internships)

st.subheader("📌 Top Internship Matches")
if matches:
    for title, company, score, location, sector in matches:
        st.markdown(f"""
        **{title}** at **{company}**  
        📍 Location: {location} | 🏢 Sector: {sector}  
        🔢 Match Score: {score}
        ---
        """)
else:
    st.warning("No suitable internships found for this candidate.")