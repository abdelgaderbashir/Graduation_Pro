from reportlab.lib.pagesizes import letter  # Import letter size to use its format
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
import statistics

# Define the tabloid size
tabloid = (11 * 72, 17 * 72)

class GenerateReport:
    def __init__(self):
        self.data = []

    def append_report(self, protocol, service, score, status, comment):
        self.data.append({
            'Protocol': protocol,
            'Service': service,
            'CVSS Score': score,
            'status': status,
            'comment': comment
        })

    def calculate_max_scores(self):
        result = {}
        for entry in self.data:
            protocol = entry['Protocol']
            if protocol not in result:
                result[protocol] = {'services': [], 'scores': []}
            result[protocol]['services'].append(entry)
            result[protocol]['scores'].append(entry['CVSS Score'])

        for protocol in result:
            max_score = max(result[protocol]['scores'])
            result[protocol]['max_score'] = max_score
            result[protocol]['rank'] = self.determine_rank(max_score)

        return result

    @staticmethod
    def determine_rank(score):
        if score == 0:
            return 'Not Found', colors.green
        elif 1 <= score <= 3.9:
            return 'Low', colors.blue
        elif 4 <= score <= 6.9:
            return 'Medium', colors.orange
        elif 7 <= score <= 8.9:
            return 'High', colors.red
        elif 9 <= score <= 10:
            return 'Critical', colors.darkred

    @staticmethod
    def get_score_color(score):
        if score == 0:
            return colors.green
        elif 1 <= score <= 3.9:
            return colors.blue
        elif 4 <= score <= 6.9:
            return colors.orange
        elif 7 <= score <= 8.9:
            return colors.red
        elif 9 <= score <= 10:
            return colors.darkred

    @staticmethod
    def generate_table_data(result):
        table_data = {}
        for protocol, data in result.items():
            services = []
            for service in data['services']:
                rank_text, rank_color = GenerateReport.determine_rank(service['CVSS Score'])
                services.append([
                    service['Service'],
                    service['status'],
                    service['comment'],
                    service['CVSS Score'],
                    rank_text
                ])
            table_data[protocol] = {
                'services': services,
                'max_score': data['max_score'],
                'rank': data['rank']
            }
        return table_data

class PDFGenerator:
    @staticmethod
    def generate_full_report(table_data, headers, filename="full_report.pdf"):
        doc = SimpleDocTemplate(filename, pagesize=tabloid)  # Updated to custom tabloid size
        styles = getSampleStyleSheet()
        elements = []

        for protocol, data in table_data.items():
            # Protocol title
            elements.append(Paragraph(protocol, styles['Title']))
            elements.append(Spacer(1, 12))

            # Table data
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Header color
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Border
                ('LEFTPADDING', (0, 0), (-1, -1), 10),  # Adjust left padding
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),  # Adjust right padding
                ('TOPPADDING', (0, 0), (-1, -1), 10),  # Adjust top padding
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),  # Adjust bottom padding
            ])

            table_data_with_colors = [headers]
            for service in data['services']:
                color = GenerateReport.get_score_color(service[3])
                r, g, b = color.red, color.green, color.blue
                row = [
                    service[0],
                    service[1],
                    service[2],
                    Paragraph(f'<para align="center"><font color="rgb({int(r*255)},{int(g*255)},{int(b*255)})">{service[3]}</font></para>', styles['BodyText']),
                    Paragraph(f'<para align="center"><font color="rgb({int(r*255)},{int(g*255)},{int(b*255)})">{service[4]}</font></para>', styles['BodyText'])
                ]
                table_data_with_colors.append(row)

            table = Table(table_data_with_colors, colWidths=[220, 150, 280, 70, 70])
            table.setStyle(table_style)
            elements.append(table)
            elements.append(Spacer(1, 12))

            # Maximum score and rank
            max_score = data['max_score']
            rank_text, rank_color = data['rank']
            r, g, b = rank_color.red, rank_color.green, rank_color.blue
            max_rank = Paragraph(
                f'Maximum Score: <font color="rgb({int(GenerateReport.get_score_color(max_score).red*255)},{int(GenerateReport.get_score_color(max_score).green*255)},{int(GenerateReport.get_score_color(max_score).blue*255)})">{max_score}</font> | Rank: <font color="rgb({int(r*255)},{int(g*255)},{int(b*255)})">{rank_text}</font>',
                styles['Normal']
            )
            elements.append(max_rank)
            elements.append(Spacer(1, 10))  # Space between protocols

        doc.build(elements)

# Example usage
if __name__ == "__main__":
    report = GenerateReport()

    # Adding multiple services under different protocols with CVSS scores
    report.append_report("FTP", "Anonymous Login", 1, "Allowed", "You can leave it")
    report.append_report("FTP", "downloading files", 5.3, "Slow download speed", "Optimize server")
    report.append_report("FTP", "file listing", 3.8, "Acceptable speed", "Monitor performance")
    report.append_report("FTP", "file deletion", 4.5, "Moderate speed", "Improve server response")
    report.append_report("FTP", "file insertion", 0, "Moderate speed", "Improve server response")

    report.append_report("SSH", "secure access", 5.6, "Comment", "Recommendation")
    report.append_report("SSH", "x", 9.8, "Comment", "Recommendation")
    report.append_report("SSH", "y", 7.2, "Comment", "Recommendation")
    report.append_report("SSH", "h", 0, "not available", "Recommendation")

    report.append_report("RDP", "remote desktop", 8.5, "Comment", "Recommendation")

    result = report.calculate_max_scores()

    # Generate table data
    table_data = GenerateReport.generate_table_data(result)

    # Define table headers
    headers = ["Service", "status", "comment", "CVSS Score", "Rank"]

    # Generate a single PDF report with all protocols
    PDFGenerator.generate_full_report(table_data, headers)
