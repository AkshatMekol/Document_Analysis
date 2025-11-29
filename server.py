from fastapi.middleware.cors import CORSMiddleware
import os
import asyncio
import requests
from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter
from fastapi import FastAPI, HTTPException
from helpers import extract_form_pages 
from s3_utils import list_s3_pdfs, fetch_pdf
from utils.mongo_utils import vector_collection, is_document_complete

app = FastAPI()

origins = [
    "http://localhost:8080",
    "http://192.168.1.5:8080",
    "https://tenderbharat.vercel.app",
    "http://localhost:3000",
    "https://www.bidindia.site",
    "https://www.bidindia.co.in",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def process_single_tender(tender_id: str):
    prefix = f"tender-documents/{tender_id}/"
    pdf_keys = await list_s3_pdfs(prefix)

    if not pdf_keys:
        print(f"⚠️ No PDFs found for tender ID {tender_id}")
        return

    for pdf_key in pdf_keys:
        pdf_name = os.path.basename(pdf_key)
        pdf_bytes = await fetch_pdf(pdf_key)

        extracted_pdf_bytes, num_pages = await extract_form_pages(pdf_bytes, pdf_name)

        output_path = f"fillable_forms_{pdf_name}"
        if num_pages > 0:
            reader = PdfReader(extracted_pdf_bytes)
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)

            with open(output_path, "wb") as f:
                writer.write(f)

            print(f"\n🎯 Combined FORM pages PDF saved as: {output_path}")
        else:
            print(f"\n⚠️ No FORM pages found in {pdf_name}")

        print(f"📊 Total FORM pages in {pdf_name}: {num_pages}")

@app.post("/process/{tender_id}")
async def route_process(tender_id: str):
    print(f"\n🌐 API CALL → /process/{tender_id}")
    try:
        return await process_single_tender(tender_id)
    except Exception as e:
        print(f"❌ API ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))
