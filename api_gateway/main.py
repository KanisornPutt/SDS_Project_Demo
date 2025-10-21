from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import httpx
import json

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/render")
async def render(request: Request):
    markdown = await request.body()
    
    async with httpx.AsyncClient() as client:
        # Step 1: Markdown → HTML fragment
        r1 = await client.post(
            "http://localhost:8081/parse",
            content=markdown.decode('utf-8'),
            headers={"Content-Type": "text/plain"}
        )
        fragment = r1.json()["html"]
        
        # Step 2: HTML fragment → Full HTML
        r2 = await client.post("http://localhost:8082/template", json={"html": fragment})
        full_html = r2.json()["html"]
        
        # Step 3: Full HTML → PDF
        r3 = await client.post("http://localhost:8083/render", json={"html": full_html})
        pdf_bytes = r3.content
        
        return Response(pdf_bytes, media_type="application/pdf")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8080)