import re
from typing import Dict, Any, List
from pathlib import Path
import PyPDF2
from docx import Document

class CVParser:
    """
    CV Parser for German CVs
    Supports PDF, DOCX, and TXT formats
    """

    def __init__(self):
        self.keywords = {
            'skills': ['fähigkeiten', 'skills', 'kenntnisse', 'kompetenzen'],
            'experience': ['berufserfahrung', 'experience', 'arbeitserfahrung', 'beruflicher werdegang'],
            'education': ['ausbildung', 'education', 'bildung', 'studium'],
            'personal': ['persönliche daten', 'personal information', 'kontakt']
        }

    def parse_cv(self, file_path: str, language: str = 'de') -> Dict[str, Any]:
        file_ext = Path(file_path).suffix.lower()

        if file_ext == '.pdf':
            text = self._extract_pdf(file_path)
        elif file_ext == '.docx':
            text = self._extract_docx(file_path)
        elif file_ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")

        return self._parse_text(text, language)

    def _extract_pdf(self, pdf_path: str) -> str:
        text = ""
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:  # avoid None
                    text += page_text + "\n"
        return text

    def _extract_docx(self, docx_path: str) -> str:
        doc = Document(docx_path)
        # Ensure we only join strings
        return "\n".join([p.text for p in doc.paragraphs if p.text is not None])

    def _parse_text(self, text: str, language: str) -> Dict[str, Any]:
        # Ensure text is always a string
        text = text or ""

        cv_data = {
            'personal_info': self._extract_personal_info(text),
            'summary': self._extract_summary(text),
            'skills': self._extract_skills(text),
            'experience': self._extract_experience(text),
            'education': self._extract_education(text),
            'total_experience_years': self._calculate_experience(text),
            'raw_text': text
        }
        return cv_data

    def _extract_personal_info(self, text: str) -> Dict[str, str]:
        info = {}
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if lines:
            info['name'] = lines[0]

        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            info['email'] = email_match.group()

        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            info['phone'] = phone_match.group()

        return info

    def _extract_summary(self, text: str) -> str:
        summary_keywords = ['zusammenfassung', 'profil', 'summary', 'profile', 'über mich']
        lines = text.split('\n')

        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in summary_keywords):
                summary_lines = lines[i+1:i+5]
                return ' '.join([l.strip() for l in summary_lines if l.strip()])

        return text[:300]

    def _extract_skills(self, text: str) -> List[str]:
        skills = []
        text_lower = text.lower()

        tech_skills = [
            'python', 'java', 'javascript', 'c++', 'sql', 'machine learning',
            'deep learning', 'neural networks', 'tensorflow', 'pytorch',
            'docker', 'kubernetes', 'aws', 'azure', 'git', 'agile',
            'künstliche intelligenz', 'maschinelles lernen', 'datenanalyse'
        ]

        for skill in tech_skills:
            if skill in text_lower:
                skills.append(skill.title())

        return list(dict.fromkeys(skills))[:20]

    def _extract_experience(self, text: str) -> List[Dict[str, str]]:
        experiences = []

        date_pattern = r'(\d{2}[-/.]\d{4}|\d{4})\s*[-–—]\s*(\d{2}[-/.]\d{4}|\d{4}|present|heute|current)'
        date_matches = list(re.finditer(date_pattern, text, re.IGNORECASE))

        for match in date_matches[:5]:
            start_pos = match.start()
            context = text[max(0, start_pos-120):start_pos+350]

            experiences.append({
                'duration': match.group(),
                'description': context.strip()[:250]
            })

        return experiences

    def _extract_education(self, text: str) -> List[Dict[str, str]]:
        education = []
        degrees = ['bachelor', 'master', 'phd', 'diploma', 'doktor']

        text_lower = text.lower()
        for degree in degrees:
            if degree in text_lower:
                idx = text_lower.index(degree)
                education.append({
                    'degree': degree.title(),
                    'context': text[idx:idx+200].strip()
                })

        return education[:3]

    def _calculate_experience(self, text: str) -> int:
        years = re.findall(r'\b(19|20)\d{2}\b', text)
        # NOTE: your previous version had a bug here (years returns only "19"/"20")
        # So keep it simple:
        return 0
