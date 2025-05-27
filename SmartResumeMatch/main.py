import pandas as pd
import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar, Style, Button
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load spaCy model (download via: python -m spacy download en_core_web_sm)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    messagebox.showerror("spaCy Error", "Please run: python -m spacy download en_core_web_sm")
    raise

# === Keyword Extraction ===
def extract_keywords(text):
    doc = nlp(text)
    keywords = set()

    for ent in doc.ents:
        if ent.label_ in ['ORG', 'PRODUCT', 'PERSON', 'SKILL']:
            keywords.add(ent.text.lower())

    for token in doc:
        if token.pos_ in ['NOUN', 'PROPN', 'VERB'] and token.is_alpha and not token.is_stop and len(token) > 2:
            keywords.add(token.lemma_.lower())

    return ' '.join(keywords)

# === Skill Extractor ===
def extract_skills_from_text(text):
    doc = nlp(text)
    skills = []
    for token in doc:
        if token.pos_ in ['NOUN', 'PROPN', 'ADJ'] and token.is_alpha and not token.is_stop and len(token) > 2:
            skills.append(token.text.lower())
    return ', '.join(set(skills))

# === Skill Gap Analyzer ===
def skill_gap_analysis(resume_skills, job_skills):
    resume_set = set([s.strip().lower() for s in resume_skills.split(',')])
    job_set = set([s.strip().lower() for s in str(job_skills).split(',')])
    missing_skills = job_set - resume_set
    return ', '.join(sorted(missing_skills)) if missing_skills else 'None'

# === Salary Predictor ===
def predict_salary(match_score, base_salary):
    try:
        base_salary = float(str(base_salary).replace(',', '').replace('$', ''))
        predicted = base_salary * (match_score / 100)
        return f"${predicted:,.2f}"
    except:
        return "N/A"

# === Resume Loader ===
def load_resume():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if not file_path:
        return
    try:
        doc = fitz.open(file_path)
        resume_text = ""
        for page in doc:
            resume_text += page.get_text()
        doc.close()
        resume_keywords = extract_keywords(resume_text)
        process_matching(resume_keywords, resume_text)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read PDF: {e}")

# === Job Matching ===
def process_matching(resume_keywords, full_resume_text):
    try:
        jobs_df = pd.read_csv("job_postings.csv")  # Columns: Title, Description, Skills, Salary
        jobs_df.fillna('', inplace=True)
        jobs_df['Combined'] = jobs_df['Title'] + ' ' + jobs_df['Description'] + ' ' + jobs_df['Skills']
        jobs_df['Keywords'] = jobs_df['Combined'].apply(extract_keywords)

        tfidf = TfidfVectorizer()
        tfidf_matrix = tfidf.fit_transform([resume_keywords] + jobs_df['Keywords'].tolist())
        cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        jobs_df['Match Score'] = cosine_sim * 100

        top_matches = jobs_df.sort_values(by='Match Score', ascending=False).head(5)
        show_results(top_matches, full_resume_text)
    except Exception as e:
        messagebox.showerror("Processing Error", str(e))

# === Results Window ===
def show_results(matches, full_resume_text):
    resume_skills = extract_skills_from_text(full_resume_text)
    average_score = matches['Match Score'].mean()

    result_window = tk.Toplevel(root)
    result_window.title("Top Job Matches")
    result_window.geometry("750x550")

    canvas = tk.Canvas(result_window)
    scrollbar = tk.Scrollbar(result_window, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas)

    canvas.create_window((0, 0), window=scroll_frame, anchor='nw')
    canvas.configure(yscrollcommand=scrollbar.set)
    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # Resume Summary Panel
    tk.Label(scroll_frame, text=f"Resume Match Summary", font=('Arial', 14, 'bold'), fg="#006699").pack(anchor='w', pady=(5, 2))
    tk.Label(scroll_frame, text=f"Extracted Skills: {resume_skills}", wraplength=700, justify="left").pack(anchor='w')
    tk.Label(scroll_frame, text=f"Average Match Score: {average_score:.2f}%", fg="green").pack(anchor='w', pady=(0, 10))

    saved_rows = []

    for _, row in matches.iterrows():
        title = row['Title']
        match_score = row['Match Score']
        skills_required = row['Skills']
        gap = skill_gap_analysis(resume_skills, skills_required)
        salary_pred = predict_salary(match_score, row['Salary'])

        tk.Label(scroll_frame, text=f"{title} - {match_score:.2f}% match", font=('Arial', 12, 'bold')).pack(anchor='w')
        tk.Label(scroll_frame, text=f"Required Skills: {skills_required}", wraplength=700, justify='left').pack(anchor='w')
        tk.Label(scroll_frame, text=f"Missing Skills: {gap}", fg='red').pack(anchor='w')
        tk.Label(scroll_frame, text=f"Predicted Salary: {salary_pred}").pack(anchor='w')
        tk.Label(scroll_frame, text=f"Job Description: {row['Description'][:300]}...", wraplength=700).pack(anchor='w')

        pb = Progressbar(scroll_frame, length=500, mode='determinate')
        pb['value'] = match_score
        pb.pack(anchor='w', pady=(0, 10))

        saved_rows.append({
            'Title': title,
            'Match Score': f"{match_score:.2f}",
            'Missing Skills': gap,
            'Predicted Salary': salary_pred,
            'Description': row['Description']
        })

    # Export to CSV
    def export_to_csv():
        df = pd.DataFrame(saved_rows)
        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV file", "*.csv")])
        if save_path:
            df.to_csv(save_path, index=False)
            messagebox.showinfo("Exported", "Top job matches saved successfully!")

    Button(scroll_frame, text="Export Matches to CSV", command=export_to_csv).pack(pady=10)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

# === Dark/Light Theme Toggle ===
def toggle_theme():
    current_bg = root.cget("bg")
    if current_bg == "SystemButtonFace":
        root.configure(bg="#2E2E2E")
        frame.configure(bg="#2E2E2E")
        for widget in frame.winfo_children():
            widget.configure(bg="#2E2E2E", fg="white")
    else:
        root.configure(bg="SystemButtonFace")
        frame.configure(bg="SystemButtonFace")
        for widget in frame.winfo_children():
            widget.configure(bg="SystemButtonFace", fg="black")

# === GUI Setup ===
root = tk.Tk()
root.title("💼 Resume Analyzer & Job Matcher")
root.geometry("500x260")

style = Style()
style.configure("TButton", font=('Arial', 11))
style.configure("TLabel", font=('Arial', 12))

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(expand=True)

tk.Label(frame, text="📄 Upload Your Resume (PDF)", font=('Arial', 14, 'bold')).pack(pady=10)
tk.Button(frame, text="Browse Resume", command=load_resume).pack(pady=5)
tk.Button(frame, text="🌗 Toggle Theme", command=toggle_theme).pack(pady=5)

root.mainloop()
