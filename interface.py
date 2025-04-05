import os
import streamlit as st
import httpx
import asyncio
import nest_asyncio
import pandas as pd
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage

###############################################################################
# 1) SETUP
###############################################################################
nest_asyncio.apply()
load_dotenv()
st.set_page_config(page_title="SFSU Course Recommender", layout="wide")


###############################################################################
# 2) LLM CLASS (UNCHANGED)
###############################################################################
class GroqLLM:
    def __init__(self, model="llama3-70b-8192", api_key=None):
        self.model = model
        self.api_key = api_key or os.getenv("GROQ_API_KEY")

    def _serialize_message(self, msg):
        if isinstance(msg, HumanMessage):
            return {"role": "user", "content": msg.content}
        elif isinstance(msg, SystemMessage):
            return {"role": "system", "content": msg.content}
        raise TypeError("Unsupported message type")

    def invoke(self, messages):
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {"model": self.model, "messages": [self._serialize_message(m) for m in messages]}
        try:
            response = httpx.post(url, headers=headers, json=payload, timeout=30.0)
            return response.json()["choices"][0]["message"]
        except Exception as e:
            return {"content": f"Error: {e}"}


llm = GroqLLM()

###############################################################################
# 3) THEME TOGGLE & CSS
###############################################################################
theme = st.sidebar.radio("Theme", ["Dark", "Light"], index=0)
dark = (theme == "Dark")

DARK_CSS = """
<style>
body {
    font-family: 'Inter', sans-serif;
    background-color: #0e0e0e !important;
    color: #f1f1f1 !important;
    padding-bottom: 5rem;
}
h1 {
    text-align: center;
    font-size: 2.6rem;
    margin-bottom: 0.2rem;
}
p.subtitle {
    text-align: center;
    color: #ccc;
    margin: 0 0 1.5rem 0;
}
.chat-box {
    max-width: 720px;
    margin: auto;
}
.chat-bubble {
    padding: 1rem;
    border-radius: 18px;
    margin: 0.5rem 0;
    word-wrap: break-word;
    animation: fadeIn 0.3s ease-in-out;
    font-size: 1.02rem;
    line-height: 1.5;
    white-space: pre-wrap;
}
.chat-bubble.user {
    background-color: #1a1a2a;
    border-left: 4px solid #bb6bff;
}
.chat-bubble.assistant {
    background-color: #111820;
    border-left: 4px solid #7ac1ff;
}
.course-card {
    background-color: #1a1a2a;
    border-radius: 10px;
    padding: 1rem;
    margin: 0.5rem 0;
    border-left: 4px solid #7ac1ff;
}
@keyframes fadeIn {
  0% {opacity: 0; transform: translateY(10px);}
  100% {opacity: 1; transform: translateY(0);}
}
</style>
"""

LIGHT_CSS = """
<style>
body {
    font-family: 'Inter', sans-serif;
    background-color: #f9f9f9 !important;
    color: #111 !important;
    padding-bottom: 5rem;
}
h1 {
    text-align: center;
    font-size: 2.6rem;
    margin-bottom: 0.2rem;
}
p.subtitle {
    text-align: center;
    color: #333;
    margin: 0 0 1.5rem 0;
}
.chat-box {
    max-width: 720px;
    margin: auto;
}
.chat-bubble {
    padding: 1rem;
    border-radius: 18px;
    margin: 0.5rem 0;
    word-wrap: break-word;
    animation: fadeIn 0.3s ease-in-out;
    font-size: 1.02rem;
    line-height: 1.5;
    white-space: pre-wrap;
}
.chat-bubble.user {
    background-color: #e0e0e0;
    border-left: 4px solid #bb6bff;
}
.chat-bubble.assistant {
    background-color: #e5f0ff;
    border-left: 4px solid #7ac1ff;
}
.course-card {
    background-color: #e5f0ff;
    border-radius: 10px;
    padding: 1rem;
    margin: 0.5rem 0;
    border-left: 4px solid #7ac1ff;
}
@keyframes fadeIn {
  0% {opacity: 0; transform: translateY(10px);}
  100% {opacity: 1; transform: translateY(0);}
}
</style>
"""

st.markdown(DARK_CSS if dark else LIGHT_CSS, unsafe_allow_html=True)

###############################################################################
# 4) TITLE & SUBTITLE
###############################################################################
st.markdown("<h1>🎓 SFSU Course Recommender</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Find the perfect courses for your degree program</p>", unsafe_allow_html=True)


###############################################################################
# 5) LOAD MAJORS FROM DATA
###############################################################################
def load_majors():
    # This function loads all majors from the SFSU academic bulletin
    majors = [
        "Accountancy: Master's Degree",
        "Accounting: Bachelor's Concentration, Graduate Certificate",
        "African Studies: Minor",
        "Africana Studies: Bachelor's Degree, Minor",
        "American Indian Studies: Bachelor's Degree, Minor",
        "American Studies: Bachelor's Degree, Minor",
        "Animation: Minor",
        "Anthropology: Bachelor's Degree, Minor, Master's Degree",
        "Apparel Design & Merchandising, Design: Bachelor's Concentration",
        "Apparel Design and Merchandising, Merchandising: Bachelor's Concentration",
        "Applied Mathematics: Bachelor's Degree",
        "Arab & Muslim Ethnicities & Diasporas Studies: Minor",
        "Art: Bachelor's Degree, Minor, Master's Degree",
        "Art, Art History & Studio Art: Bachelor's Concentration",
        "Art, Studio Art: Bachelor's Degree, Minor",
        "Art History: Bachelor's Degree, Minor",
        "Asian American Studies: Bachelor's Degree, Minor, Master's Degree",
        "Astronomy: Bachelor's Concentration, Minor",
        "Astronomy & Astrophysics: Master's Degree",
        "Astrophysics: Bachelor's Concentration",
        "Athletic Coaching: Minor",
        "Augmentative & Alternative Communication: Graduate Certificate",
        "Autism Studies: Graduate Certificate",
        "Bilingual Spanish Journalism: Bachelor's Degree, Minor",
        "Biochemistry: Bachelor's Degree, Master's Concentration",
        "Biology, General: Bachelor's Degree, Minor",
        "Biology, Cell & Molecular: Bachelor's Concentration, Master's Concentration",
        "Biology, Ecology, Evolution, and Conservation Biology: Bachelor's Concentration",
        "Biology, Integrative Biology: Masters Concentration",
        "Biology, Marine Science: Bachelor's Concentration",
        "Biology, Microbiology: Bachelor's Concentration",
        "Biology, Physiology: Bachelor's Concentration",
        "Biology, Physiology & Behavioral Biology: Master's Concentration",
        "Biomedical Science, Biotechnology: Master's Concentration",
        "Biomedical Science, Stem Cell Science: Master's Concentration",
        "Biotechnology: Master's Concentration",
        "Biotechnology - Data Science and Machine Learning for: Certificate",
        "Broadcast & Electronic Communication Arts: Bachelor's Degree, Master's Degree, Master's of Fine Arts, Minor",
        "Business Administration: Minor, Master's Degree",
        "Business Administration, Accounting: Bachelor's Concentration",
        "Business Administration, Decision Sciences: Bachelor's Concentration",
        "Business Administration, Finance: Bachelor's Concentration, Graduate Certificate",
        "Business Administration, General Business: Bachelor's Concentration",
        "Business Administration, Information Systems: Bachelor's Concentration",
        "Business Administration, International Business: Bachelor's Concentration",
        "Business Administration, Management: Bachelor's Concentration",
        "Business Administration, Marketing: Bachelor's Concentration",
        "Business Analytics: Bachelor's Concentration, Master's Degree, Certificate",
        "Business Ethics & Compliance: Graduate Certificate",
        "Business Principles: Graduate Certificate",
        "California Studies: Minor",
        "Cell & Molecular Biology: Bachelor's Concentration, Master's Concentration",
        "Chemistry: Bachelor of Arts, Bachelor of Science, Minor, Master's Degree",
        "Child & Adolescent Development, Community, Health, and Social Services: Bachelor's Concentration",
        "Child & Adolescent Development, Early Care and Education: Bachelor's Concentration",
        "Child & Adolescent Development, Elementary Education Teaching Pre-Credential: Bachelor's Concentration",
        "Child Development Pre-K to 3rd Grade: Bachelor's Degree",
        "Chinese: Master's Degree",
        "Chinese, Flagship Chinese: Bachelor's Concentration",
        "Chinese Language: Bachelor's Concentration, Minor",
        "Chinese Literature & Linguistics: Bachelor's Concentration, Minor",
        "Cinema: Bachelor's Degree, Minor, Master's Degree",
        "Cinema Studies: Master's Degree",
        "Civil Engineering: Bachelor's Degree, Minor, Master's Degree",
        "Classics: Bachelor's Degree, Minor, Master's Degree",
        "Climate Change Causes, Impacts, and Solutions: Certificate",
        "Climate Justice Education - PK-12, Graduate Certificate",
        "Clinical Laboratory Science: Graduate Certificate",
        "Clinical Mental Health Counseling: Master's Degree",
        "Clinical Psychology: Master's Concentration",
        "Comic Studies: Minor",
        "Communication Studies: Bachelor's Degree, Minor, Master's Degree",
        "Comparative & World Literature: Bachelor's Degree, Minor, Master's Degree",
        "Composition: Master's Concentration",
        "Composition, Teaching of: Graduate Certificate",
        "Computational Linguistics: Undergraduate Certificate, Graduate Certificate",
        "Computer Engineering: Bachelor's Degree, Minor",
        "Computer Science: Bachelor's Degree, Minor, Master's Degree",
        "Computing Applications: Minor",
        "Conflict Resolution: Certificate",
        "Cooperative Education: Certificate",
        "Counseling: Minor, Master's Degree",
        "Creative Nonfiction Comics Making: Certificate",
        "Creative Writing: Bachelor's Degree, Minor, Master of Arts, Master of Fine Arts",
        "Criminal Justice Studies: Bachelor's Degree, CPaGE Bachelor's Degree Completion, Minor",
        "Critical Mixed Race Studies: Minor",
        "Critical Pacific Islands & Oceania Studies: Minor",
        "Critical Social Thought: Minor",
        "Curriculum and Instruction Master's Degree",
        "Cybersecurity for Managers: Certificate",
        "Cybersecurity, Enterprise: Graduate Certificate",
        "Dance: Bachelor's Degree, Minor",
        "Data Science and Machine Learning for Biotechnology: Certificate",
        "Data Science for Psychology: Certificate",
        "Data Science, Statistical: Master's Degree",
        "Data Science and Artificial Intelligence: Master's Degree",
        "Data Science for Biology and Chemistry: Graduate Certificate",
        "Decision Sciences: Bachelor's Concentration, Minor, Graduate Certificate",
        "Design: Master's Degree, Minor",
        "Disability Studies: Minor",
        "Early Childhood Development: Minor",
        "Early Childhood Education: Master's Degree",
        "Earth Sciences: Bachelor of Arts, Bachelor of Science, Minor",
        "Economics: Bachelor's Degree, Minor, Master's Degree",
        "Education: Doctoral Degree",
        "Education: Minor",
        "Education, Special Interest Area: Master's Concentration",
        "Educational Administration and Leadership: Master's Degree",
        "Educational Leadership: Doctoral Degree",
        "Electrical and Computer Engineering: Master's Degree",
        "Electrical Engineering: Bachelor's Degree, Minor",
        "Empowerment Self-Defense: Minor",
        "Engineering, Civil Engineering: Bachelor's Degree, Minor, Master's Degree",
        "Engineering, Computer Engineering: Bachelor's Degree, Minor",
        "Engineering, Electrical Engineering: Bachelor's Degree, Minor",
        "Engineering, Electrical and Computer Engineering: Master's Degree",
        "Engineering, Mechanical Engineering: Bachelor's Degree, Minor, Master's Degree"
    ]
    # This is a subset of the full list for demonstration
    return sorted(majors)


###############################################################################
# 6) DEPARTMENT PREFIXES
###############################################################################
def load_department_prefixes():
    # Common department prefixes at SFSU
    prefixes = [
        "ACCT", "AFRS", "AIS", "AMST", "ANTH", "ARAB", "ART", "ASTR", "BIOL",
        "BECA", "BUS", "CHEM", "CAD", "CHIN", "CINE", "CLAS", "CFS", "COMM",
        "CSC", "COUN", "CJ", "DANC", "DS", "ECON", "ENGR", "EED", "ENG",
        "ERTH", "ENVS", "ETHS", "FIN", "HIST", "HTM", "HUM", "IBUS", "INFO",
        "IR", "ISYS", "ITAL", "JAPN", "JS", "KIN", "LTNS", "LS", "MATH",
        "MGMT", "MKTG", "MUS", "NURS", "PHIL", "PHYS", "PLSI", "PSY", "RRS",
        "SCI", "SED", "SOC", "SPAN", "SPED", "SW", "TH A", "WGS"
    ]
    return sorted(prefixes)


###############################################################################
# 7) SESSION STATE INITIALIZATION
###############################################################################
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "selected_major" not in st.session_state:
    st.session_state.selected_major = None
if "course_prefix" not in st.session_state:
    st.session_state.course_prefix = ""
if "course_number" not in st.session_state:
    st.session_state.course_number = ""
if "recommendations" not in st.session_state:
    st.session_state.recommendations = []

###############################################################################
# 8) SIDEBAR FOR MAJOR SELECTION
###############################################################################
with st.sidebar:
    st.header("Your Academic Profile")

    # Major selection
    majors = load_majors()
    selected_major = st.selectbox("Select your major:", majors)
    st.session_state.selected_major = selected_major

    # Academic year
    year = st.selectbox("Academic Year:", ["Freshman", "Sophomore", "Junior", "Senior", "Graduate"])

    # Completed courses
    completed_courses = st.text_area("Courses you've already completed (e.g., MATH 226, ENGR 101):")

    # Interests
    interests = st.text_area("Your academic interests:")

###############################################################################
# 9) COURSE SEARCH SECTION
###############################################################################
st.subheader("Search for Courses")
col1, col2 = st.columns(2)

with col1:
    # Department prefix dropdown
    prefixes = load_department_prefixes()
    course_prefix = st.selectbox("Select department code:", prefixes, index=0)
    st.session_state.course_prefix = course_prefix

with col2:
    # Course number input
    course_number = st.text_input("Enter course number (optional):", value=st.session_state.course_number)
    st.session_state.course_number = course_number


###############################################################################
# 10) COURSE RECOMMENDATION FUNCTION
###############################################################################
def get_course_recommendations(major, prefix, number=None, completed=None, interests=None):
    """
    Use Groq LLM to generate course recommendations based on major and course prefix/number
    """
    # Create a prompt for the LLM
    prompt = f"""
    As an academic advisor at San Francisco State University, recommend courses for a student with the following profile:

    Major: {major}
    Department Code: {prefix}
    Course Number (if specified): {number}
    Academic Level: {year}
    Completed Courses: {completed if completed else 'None specified'}
    Academic Interests: {interests if interests else 'None specified'}

    Please recommend 3-5 specific courses from the {prefix} department that would be appropriate for this student's major and academic level.
    For each course, provide:
    1. Course code (e.g., {prefix} 101)
    2. Course title
    3. Number of units
    4. Brief description
    5. How it relates to their major
    6. Any prerequisites

    Format your response as a structured list of courses without any introductory text.
    """

    # Call the LLM
    response_data = llm.invoke([HumanMessage(content=prompt)])
    recommendations_text = response_data.get("content", "Unable to generate recommendations.")

    # Parse the recommendations (in a real application, you'd parse this more robustly)
    # For now, we'll return a list of dictionaries with the course information
    courses = []

    # Simple parsing logic - this would be more sophisticated in a real application
    course_blocks = recommendations_text.split("\n\n")
    for block in course_blocks:
        if not block.strip():
            continue

        lines = block.strip().split("\n")
        if not lines:
            continue

        # Extract course code and title from the first line
        first_line = lines[0]
        if ":" in first_line:
            code_title = first_line.split(":", 1)
            code = code_title[0].strip()
            title = code_title[1].strip() if len(code_title) > 1 else ""
        else:
            code = first_line
            title = ""

        # Extract other information
        units = "3-4"  # Default
        description = ""
        relevance = ""
        prerequisites = "None"

        for line in lines[1:]:
            if "unit" in line.lower():
                units = line.split(":")[1].strip() if ":" in line else line
            elif "description" in line.lower():
                description = line.split(":")[1].strip() if ":" in line else line
            elif "relate" in line.lower() or "major" in line.lower():
                relevance = line.split(":")[1].strip() if ":" in line else line
            elif "prerequisite" in line.lower():
                prerequisites = line.split(":")[1].strip() if ":" in line else line

        courses.append({
            "code": code,
            "title": title,
            "units": units,
            "description": description,
            "relevance": relevance,
            "prerequisites": prerequisites,
        })

    return courses


###############################################################################
# 11) DISPLAY RECOMMENDATIONS
###############################################################################
if st.button("Get Course Recommendations"):
    with st.spinner("Fetching personalized course recommendations..."):
        courses = get_course_recommendations(
            major=st.session_state.selected_major,
            prefix=st.session_state.course_prefix,
            number=st.session_state.course_number,
            completed=completed_courses,
            interests=interests
        )
        st.session_state.recommendations = courses

# Display recommendations
if st.session_state.recommendations:
    st.markdown("### 📘 Recommended Courses")
    for course in st.session_state.recommendations:
        st.markdown(f"""
        <div class='course-card'>
            <strong>{course['code']}: {course['title']}</strong><br>
            <em>Units:</em> {course['units']}<br>
            <em>Description:</em> {course['description']}<br>
            <em>Relevance to Major:</em> {course['relevance']}<br>
            <em>Prerequisites:</em> {course['prerequisites']}
        </div>
        """, unsafe_allow_html=True)