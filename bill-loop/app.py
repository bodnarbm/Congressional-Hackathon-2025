import re
import tempfile
from xml.sax.saxutils import escape

import markitdown
import mistune
from fastapi import FastAPI, File, Request, Response, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
views = Jinja2Templates(directory="views")

def convert_text_to_uslm(text: str) -> str:
    """
    A best-effort parser to convert raw text of a bill into a simplified USLM XML format.
    This parser looks for common structural patterns in legislative text.
    """
    lines = text.split('\n')
    xml_output = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_output.append('<bill xmlns="http://schemas.gpo.gov/xml/uslm" bill-stage="Introduced-in-House">')

    # Simplified metadata extraction
    # A real implementation would parse the header of the bill more robustly
    xml_output.append('<meta><dc:title>A Bill</dc:title></meta>')
    xml_output.append('<form><distribution-code>I</distribution-code></form>')

    xml_output.append('<legis-body>')

    # State machine variables
    open_tags = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Regex for sections: e.g., "Section 1." or "Sec. 2."
        section_match = re.match(r'^(?:Section|Sec\.)\s+([\w\d]+)\.\s*(.*)', line, re.IGNORECASE)
        if section_match:
            while open_tags:
                xml_output.append(f'</{open_tags.pop()}>')

            sec_num = section_match.group(1)
            heading = escape(section_match.group(2))

            xml_output.append(f'<section id="sec{sec_num}">')
            open_tags.append('section')
            xml_output.append(f'<num>Sec. {sec_num}.</num>')
            if heading:
                xml_output.append(f'<heading>{heading}</heading>')
            continue

        # Regex for subsections: e.g., "(a) Heading"
        subsection_match = re.match(r'^\(([a-z])\)\s*(.*)', line)
        if subsection_match:
            if 'subsection' in open_tags:
                xml_output.append('</subsection>')
                open_tags.remove('subsection')

            sub_num = subsection_match.group(1)
            heading = escape(subsection_match.group(2))

            xml_output.append(f'<subsection id="sec{open_tags[-1].replace("section-", "")}.{sub_num}">')
            open_tags.append('subsection')
            xml_output.append(f'<num>({sub_num})</num>')
            if heading:
                xml_output.append(f'<heading>{heading}</heading>')
            continue

        # Default case for content
        if open_tags: # Only add content if we are inside a structural element
             # Simple paragraph wrapping
            if not open_tags or open_tags[-1] != 'paragraph':
                 xml_output.append('<paragraph>')
                 open_tags.append('paragraph')

            xml_output.append(f'<content>{escape(line)}</content>')

            if open_tags and open_tags[-1] == 'paragraph':
                xml_output.append('</paragraph>')
                open_tags.remove('paragraph')


    # Close any remaining open tags
    while open_tags:
        xml_output.append(f'</{open_tags.pop()}>')

    xml_output.append('</legis-body>')
    xml_output.append('</bill>')

    return '\n'.join(xml_output)


@app.get("/health")
async def health():
    return JSONResponse(status_code=200, content={"status": "ok"})


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return views.TemplateResponse(
        "index.html",
        {"title": "Congressional Bill Converter", "request": request},
    )

# serve form.js from static directory
@app.get("/script.js", response_class=HTMLResponse)
async def form_js(response: Response, request: Request):
    response.headers["Content-Type"] = "application/javascript"
    return views.TemplateResponse("script.js", { "request": request })


@app.post("/convert")
async def pdf_to_markdown(file: UploadFile = File(...), request: Request = None):
    # Save uploaded PDF to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = tmp.name

    mdown = markitdown.MarkItDown()
    # Convert PDF to Markdown using markitdown
    try:
        markdown = mdown.convert(tmp_path)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

    return views.TemplateResponse(
        "index.html",
        {"title": "Congressional Bill Converter", "request": request,
         "markdown": markdown.text_content, "html": mistune.markdown(markdown.text_content) },
    )

@app.post("/api/v1/to_uslm")
async def pdf_to_uslm(file: UploadFile = File(...)):
    """
    Converts a PDF of a bill into a structured USLM XML format.
    This endpoint uses a custom parser to identify legislative structures in the text.
    """
    # Save uploaded PDF to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = tmp.name

    mdown = markitdown.MarkItDown()
    # Convert PDF to text using markitdown
    try:
        markdown_content = mdown.convert(tmp_path)
        text_content = markdown_content.text_content
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

    # Use the custom parser to convert text to USLM
    uslm_xml = convert_text_to_uslm(text_content)

    return Response(content=uslm_xml, media_type="application/xml")
