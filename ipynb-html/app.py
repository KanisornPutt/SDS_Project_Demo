import logging
from html import escape as html_escape

from flask import Flask, jsonify, request
import nbformat
from nbconvert import HTMLExporter
try:
    from mistune import HTMLRenderer, create_markdown
except ImportError:
    HTMLRenderer = None
    create_markdown = None


MAX_NOTEBOOK_SIZE = 5 * 1024 * 1024  # 5 MB ceiling for uploads

if not logging.getLogger().hasHandlers():
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)
app = Flask(__name__)
if create_markdown and HTMLRenderer:
    try:
        MARKDOWN_RENDERER = create_markdown(renderer=HTMLRenderer(escape=True))
    except Exception:
        logger.exception("Failed initializing mistune markdown renderer")
        MARKDOWN_RENDERER = None
else:
    MARKDOWN_RENDERER = None


@app.route('/convert', methods=['POST'])
def convert_ipynb_to_html():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part named "file" in request'}), 400

    upload = request.files['file']
    filename = upload.filename or 'notebook.ipynb'

    try:
        notebook_bytes = upload.read()
    except Exception:
        logger.exception("Failed reading upload %s", filename)
        return jsonify({'error': 'Failed to read uploaded file'}), 400

    if not notebook_bytes:
        return jsonify({'error': 'Uploaded file is empty'}), 400

    if len(notebook_bytes) > MAX_NOTEBOOK_SIZE:
        return jsonify({'error': 'Notebook file is too large'}), 413

    try:
        notebook_content = notebook_bytes.decode('utf-8')
    except UnicodeDecodeError:
        notebook_content = notebook_bytes.decode('utf-8', errors='replace')
        logger.warning("Input %s contained non UTF-8 bytes; replaced invalid sequences", filename)

    try:
        notebook = nbformat.reads(notebook_content, as_version=4)
    except Exception:
        logger.exception("Failed parsing notebook %s", filename)
        return jsonify({'error': 'Unable to parse notebook file'}), 400

    html_exporter = HTMLExporter()
    html_exporter.exclude_input_prompt = False
    html_exporter.exclude_output_prompt = False

    try:
        body, _ = html_exporter.from_notebook_node(notebook)
        logger.info("Converted %s to HTML via nbconvert", filename)
        return body, 200, {'Content-Type': 'text/html; charset=utf-8'}
    except AttributeError:
        logger.warning("nbconvert fallback triggered for %s", filename)
        body = create_simple_html(notebook, title=filename)
        return body, 200, {'Content-Type': 'text/html; charset=utf-8'}
    except Exception:
        logger.exception("nbconvert conversion failed for %s", filename)
        return jsonify({'error': 'Notebook conversion failed'}), 500


def create_simple_html(notebook, title='Notebook Preview'):
    """Fallback: create a basic HTML representation of the notebook."""
    html_parts = [
        "<!DOCTYPE html>",
        "<html lang=\"en\">",
        "<head>",
        "<meta charset=\"utf-8\" />",
        f"<title>{escape_html(title)}</title>",
        "<style>",
        "body { font-family: Arial, sans-serif; max-width: 900px; margin: 24px auto; padding: 0 16px; background: #f5f5f5; }",
        "h1 { text-align: center; }",
        ".cell { background: #ffffff; margin: 16px 0; padding: 16px; border-radius: 6px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }",
        ".code-cell { border-left: 4px solid #4c6ef5; }",
        ".markdown-cell { border-left: 4px solid #2f9e44; }",
        "pre { background: #1e1e1e; color: #f5f5f5; padding: 12px; border-radius: 4px; overflow-x: auto; }",
        ".markdown-body { line-height: 1.6; }",
        ".markdown-body pre { background: #f1f3f5; color: #212529; }",
        ".markdown-body code { background: #f1f3f5; color: #212529; padding: 2px 4px; border-radius: 3px; }",
        ".output { margin-top: 12px; padding: 12px; background: #fafafa; border: 1px solid #e5e5e5; border-radius: 4px; }",
        "</style>",
        "</head>",
        "<body>",
        f"<h1>{escape_html(title)}</h1>",
    ]

    for cell in notebook.cells:
        if cell.cell_type == 'code':
            html_parts.append('<section class="cell code-cell">')
            html_parts.append("<h3>Code</h3>")
            html_parts.append(f"<pre><code>{escape_html(cell.source)}</code></pre>")

            outputs = getattr(cell, 'outputs', []) or []
            rendered_outputs = []
            for output in outputs:
                text = extract_output_text(output)
                if text:
                    rendered_outputs.append(f"<pre>{escape_html(text)}</pre>")

            if rendered_outputs:
                html_parts.append('<div class="output">')
                html_parts.extend(rendered_outputs)
                html_parts.append('</div>')

            html_parts.append('</section>')
        elif cell.cell_type == 'markdown':
            html_parts.append('<section class="cell markdown-cell">')
            html_parts.append("<h3>Markdown</h3>")
            html_parts.append(render_markdown_html(cell.source))
            html_parts.append('</section>')
        else:
            html_parts.append('<section class="cell">')
            html_parts.append(f"<h3>{escape_html(cell.cell_type.title())}</h3>")
            html_parts.append(f"<pre>{escape_html(str(cell))}</pre>")
            html_parts.append('</section>')

    html_parts.extend(["</body>", "</html>"])
    return "\n".join(html_parts)


def extract_output_text(output):
    """Return a textual representation from a notebook output entry."""
    text = getattr(output, 'text', None)
    if text:
        return text

    data = getattr(output, 'data', None)
    if isinstance(data, dict):
        for key in ('text/plain', 'text/markdown', 'text/html'):
            value = data.get(key)
            if value:
                if isinstance(value, list):
                    return "".join(value)
                return value

    return ""


def escape_html(text):
    """Escape HTML characters safely."""
    return html_escape(text or "", quote=True)


def render_markdown_html(source):
    """Render markdown content using mistune when available."""
    if not source:
        return '<div class="markdown-body"></div>'

    if MARKDOWN_RENDERER is None:
        return f"<pre>{escape_html(source)}</pre>"

    try:
        rendered = MARKDOWN_RENDERER(source)
    except Exception:
        logger.exception("Mistune failed rendering markdown content")
        return f"<pre>{escape_html(source)}</pre>"

    return f'<div class="markdown-body">{rendered}</div>'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
