import streamlit as st
import pandas as pd

st.title("PM Internship Matcher Prototype")

st.markdown("""
This app matches candidates with internships based on skills, location, sector interest, and affirmative action.
""")

# Upload Candidate CSV
candidates_file = st.file_uploader("Upload Candidates CSV", type="csv")
# Upload Internship CSV
internships_file = st.file_uploader("Upload Internships CSV", type="csv")

def calculate_score(candidate, internship):
    score = 0
    # Skill match
    skills_c = set(candidate['Skills'].split(','))
    skills_i = set(internship['RequiredSkills'].split(','))
    score += len(skills_c & skills_i)  # common skills
    # Location match
    if candidate['Location'] == internship['Location']:
        score += 1
    # Sector match
    if candidate['SectorInterest'] == internship['Sector']:
        score += 1
    # Affirmative action
    if candidate['Category'] in ['SC','ST','OBC']:
        score += 1
    return score

if candidates_file and internships_file:
    candidates = pd.read_csv(candidates_file)
    internships = pd.read_csv(internships_file)

    # Match candidates
    matches = []
    for _, internship in internships.iterrows():
        scores = []
        for _, candidate in candidates.iterrows():
            score = calculate_score(candidate, internship)
            scores.append((candidate['CandidateID'], score))
        scores.sort(key=lambda x: x[1], reverse=True)
        top_candidates = scores[:internship['Capacity']]
        for candidate_id, sc in top_candidates:
            matches.append({
                'InternshipID': internship['InternshipID'],
                'CandidateID': candidate_id,
                'Score': sc
            })

    matches_df = pd.DataFrame(matches)

    st.success("Matching Completed!")

    # Select Internship to view top candidates
    internship_list = internships['InternshipID'].tolist()
    selected_internship = st.selectbox("Select Internship to View Top Candidates", internship_list)

    if selected_internship:
        top_candidates = matches_df[matches_df['InternshipID'] == selected_internship]
        top_candidates = top_candidates.merge(candidates, on='CandidateID')
        st.dataframe(top_candidates[['CandidateID','Skills','Location','SectorInterest','Category','Score']])

    # Option to download matches
    st.download_button(
        label="Download All Matches as CSV",
        data=matches_df.to_csv(index=False),
        file_name='matches.csv',
        mime='text/csv'
    )