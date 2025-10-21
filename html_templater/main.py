from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head><title>Doc Render</title></head>
<body style="font-family:sans-serif;">
  {{ content|safe }}
</body>
</html>"""

@app.post("/template")
def template():
    data = request.get_json()
    html_fragment = data.get("html", "")
    full_html = render_template_string(HTML_TEMPLATE, content=html_fragment)
    return jsonify({"html": full_html})

if __name__ == "__main__":
    app.run(port=8082)
