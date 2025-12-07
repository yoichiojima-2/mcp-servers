import pytest
from pathlib import Path


@pytest.fixture(scope="session")
def sample_pdf(tmp_path_factory) -> Path:
    """Create a sample PDF for testing."""
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle

    pdf_path = tmp_path_factory.mktemp("data") / "sample.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=letter)

    # Page 1: Text content
    c.drawString(100, 750, "Test Document Title")
    c.drawString(100, 700, "Page 1: This is a test paragraph.")
    c.drawString(100, 680, "It contains multiple lines of text.")
    c.drawString(100, 660, "Used for testing PDF extraction.")
    c.showPage()

    # Page 2: More text
    c.drawString(100, 750, "Page 2: Second Page")
    c.drawString(100, 700, "Additional content on page two.")
    c.showPage()

    # Page 3: Another page
    c.drawString(100, 750, "Page 3: Final Page")
    c.drawString(100, 700, "The last page of the document.")
    c.showPage()

    c.save()
    return pdf_path


@pytest.fixture(scope="session")
def sample_pdf_with_table(tmp_path_factory) -> Path:
    """Create a sample PDF with a table for testing."""
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle, SimpleDocTemplate

    pdf_path = tmp_path_factory.mktemp("data") / "sample_table.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)

    # Create table data
    data = [
        ["Name", "Age", "City"],
        ["Alice", "30", "Tokyo"],
        ["Bob", "25", "Osaka"],
        ["Charlie", "35", "Kyoto"],
    ]

    table = Table(data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 14),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ]))

    doc.build([table])
    return pdf_path


@pytest.fixture
def output_dir(tmp_path) -> Path:
    """Create an output directory for test results."""
    out = tmp_path / "output"
    out.mkdir()
    return out
