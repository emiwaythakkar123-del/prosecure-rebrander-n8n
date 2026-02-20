from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response
from replace_logo import replace_logo
import io

app = FastAPI()

@app.post("/rebrand")
async def rebrand_pdf(file: UploadFile = File(...)):
    pdf_content = await file.read()
    # This calls your original replace_logo script
    output_bytes = replace_logo(pdf_input=pdf_content, logo_path="logo.png", position="right")
    return Response(content=output_bytes, media_type="application/pdf")