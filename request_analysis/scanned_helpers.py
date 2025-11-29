import io
import gc
import pdfplumber
from PIL import Image
from io import BytesIO
from utils.llm_utils import query_groq, query_deepseek
from config import GROQ_OCR_PROMPT, DEEPSEEK_TRANSLATE_PROMPT

def is_scanned_page(page):
    text = page.extract_text() or ""
    return len(text.strip()) < 10
    
def render_page_to_image(page) -> bytes:
    image = page.to_image(resolution=200).original.convert("RGB")
    resized = image.resize((image.width // 2, image.height // 2))
    buffer = io.BytesIO()
    resized.save(buffer, format="JPEG", quality=40)
    return buffer.getvalue()

def process_scanned_page_worker(args):
    page_num, pdf_bytes = args
    try:
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            page = pdf.pages[page_num]
            print(f"\n[SCANNED PAGE] Processing Page {page_num+1}")

            image_bytes = render_page_to_image(page)

            try:
                raw_content = query_groq(image_bytes, GROQ_OCR_PROMPT)
                print(f"\n📷 [SCANNED PAGE] Page {page_num+1}, raw content length: {len(raw_content)}")
            except Exception as e_groq:
                raw_content = f"<!-- Groq error: {e_groq} -->"

            if not isinstance(raw_content, str) or raw_content is None:
                raw_content = ""

            del image_bytes
            gc.collect()
            return {"page": page_num+1, "raw_content": raw_content}

    except Exception as e:
        return {"page": page_num+1, "raw_content": f"<!-- Error: {e} -->"}

def deepseek_translate_worker(args):
    page_num, raw_text = args
    try:
        prompt = f"{DEEPSEEK_TRANSLATE_PROMPT}\n\nText to translate:\n{raw_text}"
        translated_text = query_deepseek(prompt)
        return {"page": page_num, "translated_text": translated_text}
    except Exception as e:
        return {"page": page_num, "translated_text": f"<!-- DeepSeek error: {e} -->"}
