import pymupdf4llm

def to_markdown(pdf_path):
    md_text = pymupdf4llm.to_markdown(pdf_path) 
    return md_text

def extract_markdown_sections(markdown_content):
    """Extracts headers and their corresponding content from a Markdown string.

    Args:
        markdown_content (str): The Markdown content as a string.

    Returns:
        dict: A dictionary where keys are headers and values are lists of content lines.
    """

    sections = {}
    current_section = None
    lines = markdown_content.splitlines()

    for line in lines:
        if ((line.startswith("**") and line.endswith("**"))
            or line.startswith("#")
            or line.startswith("##")):
            # Found a new header
            header = line.strip("**")
            header = header.strip("#")
            current_section = header
            sections[header] = []

        elif current_section:
            # Add content to the current section
            sections[current_section].append(line)

    return sections