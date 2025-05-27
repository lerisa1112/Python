📄 About the Project:
SmartResumeMatch is an intelligent desktop application built using Python and Tkinter that allows users to upload their resume in PDF format and receive top job matches from a CSV database of job postings. The application uses Natural Language Processing (NLP) techniques to extract keywords and skills from the resume, calculate the cosine similarity between the resume and job descriptions, identify skill gaps, and even predict a salary range based on match percentage.

🔍 Key Features:

Upload resume in PDF format.
Automatically extract keywords and skills using spaCy NLP.
Match resume with job descriptions using TF-IDF + cosine similarity.
Display top 5 job matches with:
Required and missing skills.
Match score with progress bar.
Predicted salary.
Job description preview.
Export results to a CSV file.
Toggle between Dark and Light Themes.

🧰 Libraries Used:

tkinter	
fitz (PyMuPDF)	
pandas	
spacy	
sklearn	
messagebox	
filedialog	
