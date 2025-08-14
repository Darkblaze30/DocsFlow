from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.utils.database import get_db
from app.utils.pdf_processor import extract_tables
from app.utils.file_utils import save_pdf
import json

router = APIRouter()

def get_current_user():
    return {"id": 1, "department": "Finanzas"}  # Simulado

@router.post("/upload")
def upload_document(file: UploadFile = File(...), user=Depends(get_current_user)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")

    filename, file_path = save_pdf(file)
    tables = extract_tables(file_path)

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO documents (filename, uploaded_by, department, upload_date)
        VALUES (%s, %s, %s, NOW())
    """, (filename, user["id"], user["department"]))
    document_id = cursor.lastrowid

    for t in tables:
        cursor.execute("""
            INSERT INTO extracted_tables (document_id, page_number, description, table_data)
            VALUES (%s, %s, %s, %s)
        """, (document_id, t["page"], t["description"], json.dumps(t["data"])))

    db.commit()
    cursor.close()
    db.close()

    return {"message": "Documento procesado", "document_id": document_id, "tables": len(tables)}

@router.get("/tables/{document_id}")
def get_tables_by_document(document_id: int):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, page_number,description, table_data 
        FROM extracted_tables
        WHERE document_id = %s
    """, (document_id,))
    results = cursor.fetchall()

    cursor.close()
    db.close()

    if not results:
        raise HTTPException(status_code=404, detail="No se encontraron tablas para este documento")

    # Decodificar JSON
    for r in results:
        r["table_data"] = json.loads(r["table_data"])

    return {"document_id": document_id, "tables": results}
