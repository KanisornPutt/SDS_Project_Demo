from flask import Flask, request, jsonify
import nbformat
from nbconvert import HTMLExporter
import json

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_ipynb_to_html():
    try:
        file = request.files['file']
        notebook_content = file.read().decode('utf-8')
        
        # Parse notebook
        notebook = nbformat.reads(notebook_content, as_version=4)
        
        # Convert to HTML with basic configuration
        html_exporter = HTMLExporter()
        html_exporter.exclude_input_prompt = False
        html_exporter.exclude_output_prompt = False
        
        # Use basic template to avoid parser issues
        try:
            (body, resources) = html_exporter.from_notebook_node(notebook)
        except AttributeError:
            # Fallback: create simple HTML manually if nbconvert fails
            body = create_simple_html(notebook)
        
        print(f"✅ Converted {file.filename} to HTML")
        return body, 200, {'Content-Type': 'text/html; charset=utf-8'}
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

def create_simple_html(notebook):
    """Fallback: Create basic HTML from notebook"""
    html = """
    
    
    
        
        
            body { font-family: sans-serif; max-width: 900px; margin: 20px auto; padding: 20px; }
            .cell { margin: 20px 0; padding: 10px; border-left: 3px solid #ddd; }
            .code-cell { background: #f5f5f5; }
            pre { background: #f8f8f8; padding: 10px; overflow-x: auto; }
            code { font-family: monospace; }
            .output { margin-top: 10px; padding: 10px; background: white; border: 1px solid #ddd; }
        
    
    
    """
    
    for cell in notebook.cells:
        if cell.cell_type == 'code':
            html += ''
            html += '' + escape_html(cell.source) + ''
            
            if hasattr(cell, 'outputs') and cell.outputs:
                html += ''
                for output in cell.outputs:
                    if hasattr(output, 'text'):
                        html += '' + escape_html(output.text) + ''
                    elif hasattr(output, 'data') and 'text/plain' in output.data:
                        html += '' + escape_html(output.data['text/plain']) + ''
                html += ''
            html += ''
            
        elif cell.cell_type == 'markdown':
            html += ''
            html += '' + escape_html(cell.source) + ''
            html += ''
    
    html += ''
    return html

def escape_html(text):
    """Escape HTML characters"""
    return (text.replace('&', '&')
                .replace('', '>')
                .replace('"', '"'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)