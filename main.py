from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response
from replace_logo import replace_logo  # This imports your logic from your other file
import io

app = FastAPI()

@app.post("/rebrand")
async def rebrand_pdf(file: UploadFile = File(...)):
    # 1. Read the incoming PDF file from n8n or Swagger
    pdf_content = await file.read()
    
    # 2. Process it using your existing function
    # Note: logo.png must be in the same folder on GitHub
    output_bytes = replace_logo(
        pdf_input=pdf_content, 
        logo_path="logo.png", 
        position="right"
    )
    
    # 3. Return it as a proper downloadable PDF
    return Response(
        content=output_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=Branded_Report.pdf"
        }
    )
