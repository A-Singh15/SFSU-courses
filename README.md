# 🎓 SFSU Course Recommender

## Overview

The **SFSU Course Recommender** is an interactive AI-powered application designed to help students at San Francisco State University discover relevant courses tailored to their major, academic level, and interests. Leveraging the Groq LLaMA3 model, a clean Streamlit interface, and dynamic prompt generation, this tool provides personalized course suggestions with detailed descriptions and relevance to a student's academic journey.

This app is ideal for students looking for course planning guidance, elective exploration, and academic discovery based on real-time preferences.

---

## Architecture

The system includes the following components:

1. **User Input Interface**:
   - Built using Streamlit.
   - Allows users to select their major, academic year, completed courses, and interests.

2. **LLM Integration (Groq LLaMA3)**:
   - Queries are converted into structured prompts.
   - Groq’s LLaMA3 model generates relevant course recommendations.

3. **Dynamic Course Matching**:
   - Users can search by department prefix and optionally include a course number.
   - The model returns 3–5 recommended courses with key information.

4. **Theme Toggle and Styling**:
   - Users can toggle between Dark and Light themes for a personalized UI experience.
   - Custom CSS provides a modern, animated interface with accessible formatting.

5. **State Management**:
   - Session state stores chat history and selections across user interactions.

---

## Sample Workflow

1. Select your major and academic year.
2. Optionally enter completed courses and interests.
3. Choose a department prefix and/or course number.
4. Click **“Get Course Recommendations.”**
5. View detailed results including course title, units, description, relevance, and prerequisites.

---

## Installation

### Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/sfsu-course-recommender.git
   cd sfsu-course-recommender
