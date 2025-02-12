Resume and Job Description Matcher with Flask
This web application helps match resumes with job descriptions by analyzing both using natural language processing (NLP) techniques. Built with Flask for the backend, it allows users to upload their resumes and job descriptions to receive a match score along with suggestions for improving the resume. The system leverages powerful NLP models like spaCy and BERT to extract and compare keywords from resumes and job descriptions, providing valuable insights for both candidates and recruiters.

------>Features
  User Authentication: Users can sign up, log in, and manage their profiles.
  Resume Upload: Upload resumes in PDF or DOCX format.
  Job Description Input: Input job descriptions in text format for comparison.
  Text Extraction: Extracts text from resumes (PDF and DOCX formats) using PyMuPDF and python-docx.
  Semantic Matching: Uses BERT to compute semantic similarity between job descriptions and resumes.
  Keyword Extraction: Identifies key skills, tools, and other important keywords from both job descriptions and resumes using spaCy.
  Suggestions for Improvement: The app suggests missing keywords, categorized into technical skills, soft skills, and tools, to help users improve their resumes.
  
----->Technologies Used
  Flask: Web framework to handle backend logic and routing.
  spaCy: NLP library for text processing and keyword extraction.
  BERT (Sentence-Transformers): For semantic similarity comparison between job descriptions and resumes.
  sqlite3: For storing user data and managing user accounts.
  PyMuPDF (fitz): To extract text from PDF files.
  python-docx: To extract text from DOCX files.
  WTForms: To manage web forms for user sign up and login.
  Werkzeug: For file handling and secure file uploads.
  
------>How It Works
  Sign Up and Login: Users can register an account and log in to access the resume matching feature.
  Uploading Resumes: After logging in, users can upload a resume (PDF or DOCX format) and enter a job description.
  Text Extraction: The app extracts text from the uploaded resume and the job description.
  Keyword Matching: It extracts relevant keywords from both the resume and the job description using spaCy.
  Semantic Similarity: It calculates a match score by comparing the extracted keywords with BERT, considering both exact keyword matches and semantic similarity.
  Suggestions for Improvement: It also provides suggestions for missing skills or tools that should be added to the resume to make it more aligned with the job description.
