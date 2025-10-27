## How to Run

## Run Locally (for development)

**Create and activate a venv**
for frontend and HTML service
```bash
python3 -m venv venv
source venv/bin/activate
pip install flask fastapi uvicorn httpx
```

**Terminal 1 - Frontend:**
```bash
cd frontend
python -m http.server 8000
# Visit http://localhost:8000
```

**Terminal 2 - API Gateway:**
```bash
cd api_gateway
python3 main.py 
```

**Terminal 3 - MD Parser:**
```bash
cd md_parser
npm i 
node server.js
```

**Terminal 4 - HTML Templater Service:**
```bash
cd html_templater
python3 main.py
```


**Terminal 5 - PDF Renderor Service:**
```bash
cd pdf_renderer
python3 main.py
```

## Architecture Overview

```
User Browser (Port 80)
    ↓
    → uploads .ipynb file
    ↓
API Gateway (Port 3000, Node.js)
    ↓
    → forwards to Service 3
    ↓
IPYNB→HTML Service (Port 5000, Python)
    ↓
    → returns HTML
    ↓
HTML→PDF Service (Port 8080, Go)
    ↓
    → returns PDF
    ↓
API Gateway → User (PDF download)
```
