from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

from datetime import datetime


class ReportGenerator:

    def __init__(self):

        pdfmetrics.registerFont(
            UnicodeCIDFont('STSong-Light')
        )

    def exportPdf(self, reportText):

        now = datetime.now().strftime("%Y%m%d_%H%M%S")

        filePath = f"outputs/reports/report_{now}.pdf"

        doc = SimpleDocTemplate(filePath)

        styles = getSampleStyleSheet()

        style = styles['BodyText']

        style.fontName = 'STSong-Light'
        style.fontSize = 14
        style.leading = 24

        story = []

        title = Paragraph(
            "FishAI 智能分析报告",
            style
        )

        story.append(title)

        story.append(Spacer(1, 20))

        content = reportText.replace("\n", "<br/>")

        story.append(
            Paragraph(content, style)
        )

        doc.build(story)

        return filePath