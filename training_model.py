from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy

# Function to preprocess text
def preprocess_text(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text.lower())
    tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
    return " ".join(tokens)

# Input: Resume and Job Description
resume_text = """
Aspiring software engineer with a solid foundation in software development and problem-solving. Proficient in
Java, Python, and SQL, with hands-on experience in building scalable projects and collaborating effectively in
team settings. Passionate about contributing to impactful solutions and advancing technical expertise in dynamic
environments. Skilled in React, Express.js, HTML, CSS, and MongoDB. Adept at implementing machine learning algorithms.
"""

job_desc_text = """
Bachelor's degree or equivalent practical experience. Experience in coding using either Java, C++, or Python.
Experience in SQL, Technical Design, Web Technologies, Troubleshooting, and Stakeholder Management.
Preferred qualifications include experience with ad tech products, project management, and excellent problem-solving skills.
"""

# Preprocess both texts
resume_cleaned = preprocess_text(resume_text)
job_desc_cleaned = preprocess_text(job_desc_text)

# Compute TF-IDF vectors
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform([resume_cleaned, job_desc_cleaned])

# Compute similarity
similarity_score = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]

# Percentage match
match_percentage = round(similarity_score * 100, 2)

# Identify missing skills or terms
resume_tokens = set(resume_cleaned.split())
job_desc_tokens = set(job_desc_cleaned.split())
missing_terms = job_desc_tokens - resume_tokens

# Output results
print(f"Resume Match Percentage: {match_percentage}%")
print(f"Areas for Improvement (Missing Skills/Terms): {', '.join(missing_terms)}")