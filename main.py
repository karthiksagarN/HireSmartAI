import os
import pandas as pd
import json
import io
from groq import Groq
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import List
import base64

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


app = FastAPI()

class JobDescription(BaseModel):
    job_id: str
    title: str
    skills: str
    experience: str
    locations: str
    employment_type: List[str]
    responsibilities: str
    requirements_summary: str


def match_profile_with_groq(profile, job):
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
        "job_id": "{job.job_id}",
        "title": "{job.title}",
        "required_skills": {json.dumps(job.skills.split(", "))},
        "experience_required": "{job.experience}",
        "location": "{job.locations}",
        "employment_type": {json.dumps(job.employment_type)},
        "responsibilities": "{job.responsibilities}",
        "requirements_summary": "{job.requirements_summary}"
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


def process_profiles(df, job_data):
    profile_matches = []

    for _, row in df.iterrows():
        profile = row.to_dict()
        result = match_profile_with_groq(profile, job_data)
        profile_matches.append(result)

    return profile_matches

@app.post("/match-profiles")
async def match_profiles(job: JobDescription, file: UploadFile = File(...)):
    try:
        # Read the uploaded CSV file
        contents = await file.read()
        csv_base64 = base64.b64encode(contents).decode("utf-8")

        # Process profiles and match with job
        results = process_profiles(csv_base64, job)  # Call process_profiles, not match_profile_with_groq
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
