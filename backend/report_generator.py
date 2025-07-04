# report_generator.py
from fpdf import FPDF
from datetime import datetime
import os

class MedicalReportPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Medical Diagnosis Report', ln=True, align='C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

def generate_medical_report(session_id, patient_name, symptoms, diagnosis, treatment, remarks):
    pdf = MedicalReportPDF()
    pdf.add_page()

    pdf.set_font('Arial', '', 12)
    date = datetime.now().strftime("%d-%m-%Y %H:%M")

    pdf.cell(0, 10, f"Patient Name: {patient_name}", ln=True)
    pdf.cell(0, 10, f"Session ID: {session_id}", ln=True)
    pdf.cell(0, 10, f"Date: {date}", ln=True)
    pdf.ln(10)

    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "Symptoms:", ln=True)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, ", ".join(symptoms))

    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "Diagnosis:", ln=True)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, diagnosis)

    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "Treatment:", ln=True)
    p
