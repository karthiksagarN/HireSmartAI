import json
import pandas as pd
import base64
from groq import Groq
from dotenv import load_dotenv
import os
import io

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def match_profile_with_groq(profile, job):
    """
    Evaluate the compatibility between a candidate's profile and a job description using Groq API.
    """
    # Initialize Groq client
    client = Groq(api_key=GROQ_API_KEY)
    
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

def process_profiles(csv_base64, job_data):
    """
    Process profiles from a CSV file and compare them with the job description.
    """
    # Decode the Base64 string
    csv_decoded = base64.b64decode(csv_base64.split(",")[1]).decode("utf-8")

    # Read the CSV into a Pandas DataFrame
    df = pd.read_csv(io.StringIO(csv_decoded))

    profile_matches = []  # Store all profile match results

    for _, row in df.iterrows():
        profile = row.to_dict()
        result = match_profile_with_groq(profile, job_data)
        profile_matches.append(result)

    return profile_matches