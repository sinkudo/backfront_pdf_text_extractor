from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
from pdf_broken_encoding_reader.pdf_worker.pdf_reader import PDFReader  # Импортируем ваш метод

from functions import extract_text_from_ltpage, extract_text_per_page

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:3000"],
    # allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/extract-text")
async def extract_text(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(400, detail="Требуется PDF-файл")
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, "wb") as f:
                f.write(await file.read())
            reader = PDFReader()
            result = reader.get_correct_layout(Path(file_path))

            pages_list = result[0][1]
            good_pdf_path = str(result[1])

            texts_per_page = extract_text_per_page(pages_list)
            return_text = '\n'.join(texts_per_page)

            print(return_text)
            print(good_pdf_path)

            with open(good_pdf_path, "rb") as f:
                pdf_bytes = f.read()
            import base64
            return {"text": return_text, "pdf": base64.b64encode(pdf_bytes).decode("utf-8"), "filename": "corrected_" + file.filename}
            # return {"text": return_text}

    except Exception as e:
        raise HTTPException(500, detail=f"Ошибка обработки: {str(e)}")
