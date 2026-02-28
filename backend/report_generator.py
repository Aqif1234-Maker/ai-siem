from database import get_connection
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import Table
from reportlab.lib.pagesizes import letter

def generate_pdf_report():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT source_ip, event_type, threat_level FROM logs WHERE threat_level = 'Critical'")
    rows = cursor.fetchall()

    doc = SimpleDocTemplate("incident_report.pdf", pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    elements.append(Paragraph("AI-SIEM Incident Report", styles['Heading1']))
    elements.append(Spacer(1, 20))

    data = [["Source IP", "Event Type", "Threat Level"]] + rows

    table = Table(data)
    table.setStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ])

    elements.append(table)
    doc.build(elements)

    conn.close()