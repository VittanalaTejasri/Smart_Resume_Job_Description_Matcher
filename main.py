from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, RadioField, SubmitField
from wtforms.validators import DataRequired, EqualTo
import sqlite3
import os
import fitz  # PyMuPDF for PDFs
from docx import Document
from sentence_transformers import SentenceTransformer, util
import spacy
import re
from werkzeug.utils import secure_filename

# Flask app setup
app = Flask(__name__)
app.secret_key = "_privatekey_"
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load models and resources once
nlp = spacy.load("en_core_web_sm")
bert_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
regex_remove_punct = re.compile(r'[^\w\s]')

# Initialize Database
def init_db():
    con = sqlite3.connect('users_db.db')
    c = con.cursor()

    c.execute(""" 
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            gender TEXT
        )
    """)

    con.commit()
    con.close()

# Forms for SignUp, Login, Forgot Password
class SignUpForm(FlaskForm):
    name = StringField("Username", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password', message="Passwords must match")])
    gender = RadioField("Gender", choices=[('male', 'Male'), ('female', 'Female')], validators=[DataRequired()])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


# Extract text from PDF
def extract_text_from_pdf(file_path):
    """
    Extracts text from a PDF file.
    """
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

# Extract text from DOCX
def extract_text_from_docx(file_path):
    """
    Extracts text from a DOCX file.
    """
    doc = Document(file_path)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])

# Extract keywords with context
def extract_keywords_with_context(text):
    """
    Extracts keywords or phrases with context, preserving multi-word phrases like "problem solving".
    """
    # Preprocess the text
    segments = [segment.strip() for segment in text.split(',')]
    cleaned_segments = [regex_remove_punct.sub('', segment) for segment in segments]
    cleaned_text = ' '.join(cleaned_segments)

    # Process the text with spaCy
    doc = nlp(cleaned_text.lower())

    # Extract phrases (noun chunks) and keywords
    keywords = set()

    # Add noun chunks to the keywords set
    for chunk in doc.noun_chunks:
        keywords.add(chunk.text.strip())

    # Add individual tokens that are not stopwords
    for token in doc:
        if not token.is_stop and (token.is_alpha or any(char.isalnum() for char in token.text)):
            keywords.add(token.text.strip())

    return keywords
def compute_keyword_similarity(job_description, resume_text):
    job_keywords = extract_keywords_with_context(job_description)
    resume_keywords = extract_keywords_with_context(resume_text)
    
    job_embeddings = bert_model.encode(list(job_keywords), convert_to_tensor=True)
    resume_embeddings = bert_model.encode(list(resume_keywords), convert_to_tensor=True)
    similarity_matrix = util.pytorch_cos_sim(job_embeddings, resume_embeddings).cpu().numpy()
    
    best_match_scores = similarity_matrix.max(axis=1)
    keyword_overlap = len(job_keywords & resume_keywords) / len(job_keywords)

    semantic_score = sum(best_match_scores) / len(job_keywords) if job_keywords else 0
    final_score = (0.9 * semantic_score + 0.2 * keyword_overlap) * 100
    return min(final_score, 100)

def categorize_suggestions(job_description, resume_text):
    job_keywords = extract_keywords_with_context(job_description)
    resume_keywords = extract_keywords_with_context(resume_text)
    missing_keywords = set(map(str.lower, job_keywords)) - set(map(str.lower, resume_keywords))
    #print(job_keywords)
   # print(resume_keywords)
    #print(job_keywords-resume_keywords)
    technical_skills_set = {
            'python', 'java', 'javascript', 'react', 'angular', 'typescript', 'html', 'css',
            'sql', 'nosql', 'c++', 'c#', 'ruby', 'php', 'kotlin', 'swift','scala','julia',
            'machine learning', 'data science', 'ai', 'deep learning', 'nlp','pandas','expressjs'
            'cloud computing', 'aws', 'azure', 'google cloud', 'html5', 'css3','nodejs','reactjs',
            'kubernetes', 'linux', 'bash', 'devops', 'ci/cd', 'big data', 'hadoop', 'node.js', 'express.js',
            'spark', 'tensorflow', 'pytorch', 'd3.js', 'flask', 'django', 'fastapi', 'react.js','expressjs'
        }

    soft_skills_set = {
            'collaboration', 'teamwork', 'communication', 'problemsolving', 'leadership',
            'adaptability', 'time management', 'critical thinking', 'creativity','analytics','analytical'
            'conflict resolution', 'decision-making', 'mentoring', 'work-ethic',
            'emotional intelligence', 'negotiation', 'presentation-skills'
        }

    tools_set = {
            'git', 'github', 'bitbucket', 'jira', 'confluence', 'powerbi', 'tableau',
            'docker', 'kubernetes', 'jenkins', 'ansible', 'terraform', 'figma',
            'adobe xd', 'postman', 'swagger', 'visual studio code', 'intellij',
            'eclipse', 'pycharm', 'r', 'matlab', 'excel', 'splunk', 'elastic stack',
            'datadog', 'grafana', 'prometheus', 'powerbi','MsWord','MsExcel','word'
        }

    technical_skills = [keyword for keyword in missing_keywords if keyword in technical_skills_set]
    soft_skills = [keyword for keyword in missing_keywords if keyword in soft_skills_set]
    tools = [keyword for keyword in missing_keywords if keyword in tools_set]
    other_keywords = [
        keyword for keyword in missing_keywords
        if keyword not in technical_skills_set and keyword not in soft_skills_set and keyword not in tools_set
        ]

    return {
            'technical_skills': technical_skills,
            'soft_skills': soft_skills,
            'tools': tools,
            'other_keywords': other_keywords
        }

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()

    if form.validate_on_submit():
        username = form.name.data
        email = form.email.data
        password = form.password.data
        confirm_password = form.confirm_password.data
        gender = form.gender.data

        if password != confirm_password:
            flash("Passwords do not match. Please try again.", "error")
            return render_template('SignUp_Page.html', form=form)

        try:
            con = sqlite3.connect('users_db.db')
            c = con.cursor()
            c.execute("INSERT INTO users(username, email, password, gender) VALUES (?, ?, ?, ?)",
                      (username, email, password, gender))
            con.commit()
            flash("Signup successful! Please log in.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Email already exists. Please use a different email.", "error")
        finally:
            con.close()

    return render_template('SignUp_Page.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        con = sqlite3.connect('users_db.db')
        c = con.cursor()
        c.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = c.fetchone()
        con.close()

        if user and user[3] == password:  # Check if password matches
            
            return redirect(url_for('upload_resume'))
        else:
            flash("Invalid email or password. Please try again.", "error")

    return render_template('Login_Page.html', form=form)



@app.route('/upload', methods=['GET', 'POST'])
def upload_resume():
    if request.method == 'POST':
        if 'job_description' in request.form and 'resume' in request.files:
            job_description = request.form['job_description']
            resume = request.files['resume']

            if resume.filename == '':
                flash("No file uploaded. Please select a file.", "error")
                return redirect(url_for('upload_resume'))

            file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(resume.filename))
            resume.save(file_path)

            # Extract resume text
            if resume.filename.endswith('.pdf'):
                resume_text = extract_text_from_pdf(file_path)
            elif resume.filename.endswith('.docx'):
                resume_text = extract_text_from_docx(file_path)
            else:
                flash("Unsupported file format. Please upload a .pdf or .docx file.", "error")
                os.remove(file_path)
                return redirect(url_for('upload_resume'))

            similarity_score = compute_keyword_similarity(job_description, resume_text)
            suggestions = categorize_suggestions(job_description, resume_text)
            os.remove(file_path)

            return render_template('result.html',
                                   similarity_score=similarity_score,
                                   suggestions=suggestions)

        flash("Missing job description or resume file.", "error")
    return render_template('index.html')

if __name__ == "__main__":
    init_db()
    app.run(debug=True)