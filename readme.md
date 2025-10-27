## How to Run

## Using Docker Compose 
```bash
# Start all services
docker-compose up --build

# Access the frontend at http://localhost
```

## Run Locally (for development)

**Create and activate a venv**
for frontend and html service
```bash
python3 -m venv venv
source venv/bin/activate
``

**Terminal 1 - Frontend:**
```bash
cd frontend
python -m http.server 8000
# Visit http://localhost:8000
```

**Terminal 2 - API Gateway:**
```bash
cd api-gateway
npm install
node gateway.js
```

**Terminal 3 - IPYNB Converter:**
```bash
cd ipynb-html
pip install -r requirements.txt
# Use 1 worker for simplicity, or 2-4 for better performance
gunicorn --bind 0.0.0.0:5000 --workers 2 wsgi:app
```

**Terminal 4 - PDF Service:**
```bash
cd html-pdf
# Install wkhtmltopdf first: apt-get install wkhtmltopdf (Linux) or brew install wkhtmltopdf (Mac)
go run pdf_service.go
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