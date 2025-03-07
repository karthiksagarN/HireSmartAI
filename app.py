import os
import pandas as pd
import json
from groq import Groq
from dotenv import load_dotenv

# Load Groq API Key
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

# Function to get match percentage using Groq
def match_profile_with_groq(profile, job):
    prompt = f"""
    You are an AI that evaluates the compatibility between a candidate's profile and a job description.
    Your response must be strictly in JSON format with no extra text, explanations, or comments.

    **Candidate Profile:**
    {{
        "profile_id": "{profile.get("profile_id")}",
        "name": "{profile.get("name")}",
        "skills": {json.dumps(profile.get("skills", "").split(", "))},
        "interested_positions": {json.dumps(profile.get("interested_position_titles", "").split(", "))},
        "location": "{profile.get("location")}",
        "experience": "{profile.get("experience")}",
        "job_type": "{profile.get("job_type")}"
    }}

    **Job Description:**
    {{
        "job_id": "{job.get("job_id")}",
        "title": "{job.get("title")}",
        "required_skills": {json.dumps(job.get("skills", "").split(", "))},
        "experience_required": "{job.get("experience")}",
        "location": "{job.get("locations")}",
        "employment_type": {json.dumps(job.get("employment_type", []))},
        "responsibilities": "{job.get("responsibilities")}",
        "requirements_summary": "{job.get("requirements_summary")}"
    }}

    **Task:**  
    - Evaluate the match between the candidate's profile and job description.  
    - Determine a match percentage (0-100%).  
    - Categorize the fit as "Good Fit", "Moderate Fit", or "Not a Good Fit".  
    - Identify missing skills or requirements.

    **Response Format (STRICTLY RETURN ONLY THIS JSON, NO EXTRA TEXT):**
    {{
      "profile_id": "{profile.get("profile_id")}",
      "match_percentage": <match_value>,
      "fit_category": "<Good Fit | Moderate Fit | Not a Good Fit>",
      "missing_criteria": ["List of missing skills or requirements"]
    }}
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.7
    )

    return json.loads(response.choices[0].message.content)

# Function to process profiles from CSV and compare with job description
def process_profiles(csv_path, job_data):
    df = pd.read_csv(csv_path, encoding="ISO-8859-1")

    profile_matches = []  # Store all profile match results

    for _, row in df.iterrows():
        profile = row.to_dict()
        result = match_profile_with_groq(profile, job_data)
        profile_matches.append(result)

    return profile_matches


# Example Usage
if __name__ == "__main__":
    job_posting = {
        "job_id": "1455387012",
        "title": "SOFTWARE ENGINEER",
        "skills": "C#, VB.NET, Microsoft SQL Server, Progress Databases",
        "experience": "5-10",
        "locations": "Rochester, New York, United States",
        "employment_type": ["Full-time"],
        "responsibilities": "Provide development and customization of Epicor ERP Application.",
        "requirements_summary": "4+ years of Microsoft .Net programming experience required."
    }

    result = process_profiles("/Users/karthiksagar/TailorMyCV/profiles.csv", job_posting)
    print(json.dumps(result, indent=4))
