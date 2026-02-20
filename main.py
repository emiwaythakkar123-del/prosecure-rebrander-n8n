from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response
from replace_logo import replace_logo
import io

app = FastAPI()

@app.post("/rebrand")
async def rebrand_pdf(file: UploadFile = File(...)):
    # 1. Capture the original filename
    original_name = file.filename
    
    # 2. Rename: Replace "Prudent" with "Prosecure"
    # This matches your logic from app.py
    new_name = original_name.replace("Prudent", "Prosecure")
    if new_name == original_name:
         new_name = f"Prosecure_{original_name}"
    
    # 3. Read and Process the PDF
    pdf_content = await file.read()
    output_bytes = replace_logo(
        pdf_input=pdf_content, 
        logo_path="logo.png", 
        position="right"
    )
    
    # 4. Return with the DYNAMIC filename
    return Response(
        content=output_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={new_name}"
        }
    )
