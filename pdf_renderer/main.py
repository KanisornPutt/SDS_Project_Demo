from flask import Flask, request, Response
import subprocess, tempfile

app = Flask(__name__)

@app.post("/render")
def render():
    data = request.get_json()
    html = data.get("html", "")
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
        tmp.write(html.encode("utf-8"))
        tmp.flush()
        pdf_bytes = subprocess.check_output(["wkhtmltopdf", "-", "-"], input=html.encode("utf-8"))
    return Response(pdf_bytes, content_type="application/pdf")

if __name__ == "__main__":
    app.run(port=8083)
