from fastapi import FastAPI
from fastapi.responses import FileResponse
from typing import Dict, Any
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
import uuid

app = FastAPI()

resumes = []


def generate_resume_pdf(data: Dict[str, Any], filename: str):

    doc = SimpleDocTemplate(filename, pagesize=letter)

    styles = getSampleStyleSheet()

    elements = []

    # HEADER
    elements.append(
        Paragraph(
            f"<b>{data.get('name', '')}</b>",
            styles['Title']
        )
    )

    elements.append(
        Paragraph(
            f"""
            Email: {data.get('email', '')}<br/>
            Phone: {data.get('phone', '')}
            """,
            styles['Normal']
        )
    )

    elements.append(Spacer(1, 12))

    # ATS SCORE
    elements.append(
        Paragraph(
            "<b>ATS Analysis</b>",
            styles['Heading2']
        )
    )

    elements.append(
        Paragraph(
            f"ATS Score: {data.get('ats_score', 0)}/100",
            styles['Normal']
        )
    )

    elements.append(Spacer(1, 12))

    # SKILLS
    elements.append(
        Paragraph(
            "<b>Skills</b>",
            styles['Heading2']
        )
    )

    skills = data.get('skills', {})

    for category, values in skills.items():

        if isinstance(values, list):

            skill_text = ", ".join(
                [str(v) for v in values]
            )

            elements.append(
                Paragraph(
                    f"<b>{category}</b>: {skill_text}",
                    styles['Normal']
                )
            )

    elements.append(Spacer(1, 12))

    # EXPERIENCE
    elements.append(
        Paragraph(
            "<b>Experience</b>",
            styles['Heading2']
        )
    )

    for exp in data.get('experience', []):

        title = exp.get('title', '')
        company = exp.get('company', '')
        description = exp.get('description', '')

        elements.append(
            Paragraph(
                f"<b>{title}</b> - {company}",
                styles['Normal']
            )
        )

        elements.append(
            Paragraph(
                str(description),
                styles['Normal']
            )
        )

        elements.append(Spacer(1, 8))

    # EDUCATION
    elements.append(
        Paragraph(
            "<b>Education</b>",
            styles['Heading2']
        )
    )

    for edu in data.get('education', []):

        degree = edu.get('degree', '')
        institution = edu.get('institution', '')
        duration = f"{edu.get('start_date', '')} - {edu.get('end_date', '')}"
        grade = edu.get('grade', '')

        elements.append(
            Paragraph(
                f"""
                <b>{degree}</b><br/>
                {institution}<br/>
                {duration}<br/>
                Grade: {grade}
                """,
                styles['Normal']
            )
        )

        elements.append(Spacer(1, 8))

    # PROJECTS
    elements.append(
        Paragraph(
            "<b>Projects</b>",
            styles['Heading2']
        )
    )

    for project in data.get('projects', []):

        name = project.get('name', '')
        description = project.get('description', '')

        technologies = ", ".join(
            [str(t) for t in project.get('technologies', [])]
        )

        elements.append(
            Paragraph(
                f"<b>{name}</b>",
                styles['Normal']
            )
        )

        elements.append(
            Paragraph(
                str(description),
                styles['Normal']
            )
        )

        elements.append(
            Paragraph(
                f"Technologies: {technologies}",
                styles['Normal']
            )
        )

        elements.append(Spacer(1, 8))

    # MISSING SKILLS
    elements.append(
        Paragraph(
            "<b>Missing Skills</b>",
            styles['Heading2']
        )
    )

    missing_skills = ", ".join(
        [str(m) for m in data.get('missing_skills', [])]
    )

    elements.append(
        Paragraph(
            missing_skills,
            styles['Normal']
        )
    )

    # BUILD PDF
    doc.build(elements)


@app.post('/resume')
async def save_resume(resume: Dict[str, Any]):

    resumes.append(resume)

    pdf_name = f"resume_{uuid.uuid4().hex}.pdf"

    generate_resume_pdf(resume, pdf_name)

    return {
        "message": "Resume saved successfully",
        "pdf_file": pdf_name,
        "data": resume
    }


@app.get('/resumes')
async def get_resumes():
    return resumes


@app.get('/download/{filename}')
async def download_resume(filename: str):

    return FileResponse(
        path=filename,
        media_type='application/pdf',
        filename=filename
    )