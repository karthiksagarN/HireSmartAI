import React, { useState } from "react";
import {
  Button,
  Container,
  Typography,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from "@mui/material";
import axios from "axios";

const Home = () => {
  const [jobData, setJobData] = useState({
    job_id: "123", // You can generate this dynamically or leave it empty
    title: "",
    skills: "",
    experience: "",
    locations: "",
    employment_type: [],
    responsibilities: "",
    requirements_summary: "",
  });
  const [file, setFile] = useState(null);
  const [results, setResults] = useState([]);

  const handleFileUpload = (event) => {
    setFile(event.target.files[0]);
  };

  const handleSubmit = async () => {
    if (!file) {
      alert("Please upload a CSV file.");
      return;
    }

    // Convert the CSV file to Base64
    const reader = new FileReader();
    reader.onload = async () => {
      const csvBase64 = reader.result; // Extract Base64 data

      // Prepare the payload for the external API
      const payload = {
        data: [csvBase64, jobData],
      };

      try {
        // Send the request to the external API
        const response = await axios.post(
          "https://karthiksagar.us-east-1.modelbit.com/v1/process_profiles/latest",
          payload
        );

        // Log the API response
        console.log("API Response:", response.data);

        // Extract the `data` array from the response
        if (response.data && Array.isArray(response.data.data)) {
          setResults(response.data.data); // Set the `data` array to `results`
        } else {
          console.error("Unexpected API response format:", response.data);
          alert("Unexpected response format from the API.");
        }
      } catch (error) {
        console.error("Error:", error);
        alert("An error occurred while processing the request.");
      }
    };

    // Read the file as a Base64 string
    reader.readAsDataURL(file);
  };

  return (
    <Container>
      <Typography variant="h3" gutterBottom>
        Job Matching App
      </Typography>

      {/* Job Title */}
      <TextField
        label="Job Title"
        value={jobData.title}
        onChange={(e) => setJobData({ ...jobData, title: e.target.value })}
        fullWidth
        margin="normal"
      />

      {/* Required Skills */}
      <TextField
        label="Required Skills"
        value={jobData.skills}
        onChange={(e) => setJobData({ ...jobData, skills: e.target.value })}
        fullWidth
        margin="normal"
      />

      {/* Experience */}
      <TextField
        label="Experience Required"
        value={jobData.experience}
        onChange={(e) => setJobData({ ...jobData, experience: e.target.value })}
        fullWidth
        margin="normal"
      />

      {/* Location */}
      <TextField
        label="Location"
        value={jobData.locations}
        onChange={(e) => setJobData({ ...jobData, locations: e.target.value })}
        fullWidth
        margin="normal"
      />

      {/* Employment Type */}
      <FormControl fullWidth margin="normal">
        <InputLabel>Employment Type</InputLabel>
        <Select
          multiple
          value={jobData.employment_type}
          onChange={(e) => setJobData({ ...jobData, employment_type: e.target.value })}
        >
          <MenuItem value="Full-time">Full-time</MenuItem>
          <MenuItem value="Part-time">Part-time</MenuItem>
          <MenuItem value="Contract">Contract</MenuItem>
          <MenuItem value="Internship">Internship</MenuItem>
        </Select>
      </FormControl>

      {/* Responsibilities */}
      <TextField
        label="Responsibilities"
        value={jobData.responsibilities}
        onChange={(e) => setJobData({ ...jobData, responsibilities: e.target.value })}
        fullWidth
        margin="normal"
        multiline
        rows={4}
      />

      {/* Requirements Summary */}
      <TextField
        label="Requirements Summary"
        value={jobData.requirements_summary}
        onChange={(e) => setJobData({ ...jobData, requirements_summary: e.target.value })}
        fullWidth
        margin="normal"
        multiline
        rows={4}
      />

      {/* File Upload */}
      <input type="file" onChange={handleFileUpload} />

      {/* Submit Button */}
      <Button variant="contained" color="primary" onClick={handleSubmit}>
        Match Profiles
      </Button>

      {/* Display Results */}
      <div>
        {results.length > 0 ? (
          results.map((result, index) => (
            <div key={index}>
              <h3>{result.profile_id}</h3>
              <p>Match: {result.match_percentage}%</p>
              <p>Fit: {result.fit_category}</p>
            </div>
          ))
        ) : (
          <p>No results to display.</p>
        )}
      </div>
    </Container>
  );
};

export default Home;