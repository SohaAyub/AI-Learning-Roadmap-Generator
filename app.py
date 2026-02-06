import os
import gradio as gr
from groq import Groq
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import textwrap

# Initialize Groq client using environment variable
api_key = os.environ.get("AI_ROADMAP_KEY")

if api_key:
    client = Groq(api_key=api_key)
else:
    client = None


# ---------------- ROADMAP GENERATION ----------------
def generate_roadmap(domain, level, time_period):
    if not domain or not level or not time_period:
        return "Please fill in all fields."

    if client is None:
        return "Groq API key is missing. Please configure it in the Space settings."

    try:
        prompt = f"""
You are an expert learning mentor.

Create a detailed learning roadmap for:
Domain: {domain}
Skill Level: {level}
Time Duration: {time_period}

The roadmap should include:
- Weekly or phase-wise breakdown
- Topics to learn
- Tools and technologies
- Practice tasks or mini projects
- Learning tips

Use simple English and bullet points.
"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=900
        )

        return response.choices[0].message.content

    except Exception:
        return "Unable to generate roadmap at the moment. Please try again later."


# ---------------- PDF GENERATION ----------------
def generate_pdf(roadmap_text):
    if not roadmap_text:
        return None

    try:
        file_path = "AI_Learning_Roadmap.pdf"
        pdf = canvas.Canvas(file_path, pagesize=A4)
        width, height = A4

        pdf.setFont("Helvetica", 10)
        x = 40
        y = height - 50
        line_height = 14

        for line in roadmap_text.split("\n"):
            wrapped_lines = textwrap.wrap(line, 90) or [""]
            for wrapped_line in wrapped_lines:
                if y < 50:
                    pdf.showPage()
                    pdf.setFont("Helvetica", 10)
                    y = height - 50
                pdf.drawString(x, y, wrapped_line)
                y -= line_height

        pdf.save()
        return file_path

    except Exception:
        return None


# ---------------- GRADIO UI ----------------
with gr.Blocks() as app:
    gr.Markdown("## AI Learning Roadmap Generator")
    gr.Markdown("Generate a personalized learning roadmap and download it as a PDF.")

    domain = gr.Textbox(label="Learning Domain", placeholder="Example: Data Science")
    level = gr.Dropdown(
        ["Beginner", "Intermediate", "Advanced"],
        label="Skill Level"
    )
    time_period = gr.Textbox(label="Time to Learn", placeholder="Example: 3 months")

    generate_button = gr.Button("Generate Roadmap")
    roadmap_output = gr.Textbox(label="Generated Roadmap", lines=20)

    download_button = gr.Button("Download Roadmap as PDF")
    pdf_file = gr.File(label="Download PDF")

    generate_button.click(
        fn=generate_roadmap,
        inputs=[domain, level, time_period],
        outputs=roadmap_output
    )

    download_button.click(
        fn=generate_pdf,
        inputs=roadmap_output,
        outputs=pdf_file
    )

app.launch()
