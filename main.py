from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_resume():
    if 'job_description' in request.form and 'resume' in request.files:
        job_description = request.form['job_description']
        resume = request.files['resume']
      
        return f"Job Description: {job_description}, File: {resume.filename}"
    return "Error: Missing job description or resume file."

if __name__ == "__main__":
    app.run(debug=True)