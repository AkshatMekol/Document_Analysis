import asyncio
import zipfile
from io import BytesIO
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from s3_utils import list_s3_pdfs, fetch_pdf  

app = FastAPI()

async def build_zip_stream_for_tender(tender_id: str):
    prefix = f"tender-documents/{tender_id}/"
    pdf_keys = await list_s3_pdfs(prefix)  # async

    if not pdf_keys:
        raise HTTPException(status_code=404, detail="No PDFs found for this tender")

    zip_buffer = BytesIO()

    async def fetch_and_add(key):
        file_bytes = await fetch_pdf(key)  
        relative_path = key[len(prefix):] if key.startswith(prefix) else key
        return relative_path, file_bytes

    results = await asyncio.gather(*(fetch_and_add(key) for key in pdf_keys))

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for relative_path, file_bytes in results:
            zipf.writestr(relative_path, file_bytes)

    zip_buffer.seek(0)
    return zip_buffer

@app.get("/download_documents/{tender_id}")
async def download_documents(tender_id: str):
    zip_stream = await build_zip_stream_for_tender(tender_id)
    filename = f"tender_{tender_id}.zip"

    return StreamingResponse(
        zip_stream,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
