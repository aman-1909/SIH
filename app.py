import streamlit as st
import pandas as pd

# ---------------------------
# Page Config & Theme
# ---------------------------
st.set_page_config(
    page_title="Internship Matching Engine",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for card-like styling
st.markdown("""
<style>
    .match-card {
        background-color: #f9f9f9;
        padding: 20px;
        margin-bottom: 15px;
        border-radius: 15px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    .score-bar {
        height: 20px;
        border-radius: 10px;
        background: #e0e0e0;
        overflow: hidden;
        margin-top: 5px;
    }
    .score-fill {
        height: 100%;
        background: linear-gradient(90deg, #06b6d4, #3b82f6);
        text-align: center;
        color: white;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Load Data
# ---------------------------
@st.cache_data
def load_data():
    candidates = pd.read_csv("candidates.csv")
    internships = pd.read_csv("internships.csv")
    return candidates, internships

candidates, internships = load_data()

st.title("🎯 Smart Internship Matching Engine")
st.write("AI-powered matching system that connects **students** with the most suitable **internships** based on skills, preferences & inclusivity.")

# ---------------------------
# Sidebar Inputs
# ---------------------------
st.sidebar.header("⚙️ Candidate Input Options")
input_mode = st.sidebar.radio("Choose input mode:", ["Select Candidate ID", "Enter Details Manually"])

if input_mode == "Select Candidate ID":
    candidate_id = st.sidebar.selectbox("Select Candidate ID", candidates["CandidateID"].unique())
    candidate = candidates[candidates["CandidateID"] == candidate_id].iloc[0]

    st.sidebar.subheader("🧑 Candidate Profile")
    st.sidebar.write(f"**Skills:** {candidate['Skills']}")
    st.sidebar.write(f"**Location:** {candidate['Location']}")
    st.sidebar.write(f"**Sector Interest:** {candidate['SectorInterest']}")
    st.sidebar.write(f"**Category:** {candidate['Category']}")
    st.sidebar.write(f"**Past Participation:** {candidate['PastParticipation']}")

    cand_skills = str(candidate["Skills"]).lower().split(",")
    cand_location = candidate["Location"]
    cand_sector = candidate["SectorInterest"]
    cand_category = candidate["Category"]
    cand_past = candidate["PastParticipation"]

else:
    st.sidebar.subheader("📝 Enter Your Profile")
    cand_skills = st.sidebar.text_input("Enter your skills (comma separated)", "Python, Excel").lower().split(",")
    cand_location = st.sidebar.text_input("Preferred Location", "Patna")
    cand_sector = st.sidebar.text_input("Sector of Interest", "IT")
    cand_category = st.sidebar.selectbox("Category", ["GEN", "OBC", "SC", "ST"])
    cand_past = st.sidebar.selectbox("Past Participation in Internship?", [0, 1])

# ---------------------------
# Matching Logic
# ---------------------------
def calculate_match(skills, location, sector, category, past, internships):
    scores = []
    for _, row in internships.iterrows():
        score = 0

        # Skill match
        req_skills = str(row["RequiredSkills"]).lower().split(",")
        common_skills = len(set(skills) & set(req_skills))
        score += common_skills * 50

        # Location match
        if location.lower() == row["Location"].lower():
            score += 20

        # Sector interest match
        if sector.lower() == row["Sector"].lower():
            score += 20

        # Affirmative action boost
        if category in ["SC", "ST", "OBC"]:
            score += 10

        # Penalize past participants
        if past == 1:
            score -= 10

        scores.append((row["InternshipID"], row["Sector"], row["Location"], row["RequiredSkills"], score))

    match_df = pd.DataFrame(scores, columns=["InternshipID", "Sector", "Location", "RequiredSkills", "Score"])
    return match_df.sort_values(by="Score", ascending=False)

matches = calculate_match(cand_skills, cand_location, cand_sector, cand_category, cand_past, internships)

# ---------------------------
# Display Results
# ---------------------------
st.subheader("🏆 Top 3 Internship Matches")

top3 = matches.head(3)

for _, row in top3.iterrows():
    st.markdown(
        f"""
        <div class="match-card">
            <h4>🎓 Internship ID: {row['InternshipID']}</h4>
            <p><b>Sector:</b> {row['Sector']} | <b>Location:</b> {row['Location']}</p>
            <p><b>Required Skills:</b> {row['RequiredSkills']}</p>
            <div class="score-bar">
                <div class="score-fill" style="width:{row['Score']}%">
                    {row['Score']}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True
    )

st.subheader("📊 Full Match Results")
st.dataframe(matches)

# Download option
csv = matches.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Download All Matches as CSV",
    data=csv,
    file_name="internship_matches.csv",
    mime="text/csv",
)