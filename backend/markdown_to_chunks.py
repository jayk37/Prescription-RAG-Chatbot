# markdown_to_chunks.py
import pymupdf4llm
from pdf_to_markdown import extract_markdown_sections

def markdown_to_chunks(markdown_text):
    standard_us_content_template = "*Sections"
    if standard_us_content_template in markdown_text:
        md_text = markdown_text.split(standard_us_content_template)[1]
    else:
        md_text = markdown_text

    pdfheaderdict = extract_markdown_sections(md_text)
    print("HEADER LIST:", pdfheaderdict)
    return pdfheaderdict  # Return the header dictionary
