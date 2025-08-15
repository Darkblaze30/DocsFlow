from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
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

@router.get("/")
def list_documents(user=Depends(get_current_user)):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, filename, department, upload_date
        FROM documents
        WHERE uploaded_by = %s
        ORDER BY upload_date DESC
    """, (user["id"],))
    documents = cursor.fetchall()

    cursor.close()
    db.close()

    return {"documents": documents}

@router.get("/{id}")
def get_document(id: int, user=Depends(get_current_user)):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, filename, department, upload_date
        FROM documents
        WHERE id = %s AND uploaded_by = %s
    """, (id, user["id"]))
    document = cursor.fetchone()

    cursor.close()
    db.close()

    if not document:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    return {"document": document}

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

@router.get("/search/")
def search_tables(q: str = Query(..., min_length=1)):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT document_id, page_number, description, table_data
        FROM extracted_tables
    """)
    results = cursor.fetchall()

    cursor.close()
    db.close()

    matches = []
    for r in results:
        table = json.loads(r["table_data"])
        found = any(
            q.lower() in str(cell).lower()
            for row in table
            for cell in row if cell
        )
        if found:
            matches.append({
                "document_id": r["document_id"],
                "page_number": r["page_number"],
                "description": r["description"],
                "table_data": table
            })

    return {
        "query": q,
        "total_matches": len(matches),
        "results": matches
    }


@router.delete("/{id}")
def delete_document(id: int, user=Depends(get_current_user)):
    db = get_db()
    cursor = db.cursor()

    # Verificar propiedad
    cursor.execute("SELECT filename FROM documents WHERE id = %s AND uploaded_by = %s", (id, user["id"]))
    result = cursor.fetchone()
    if not result:
        raise HTTPException(status_code=404, detail="Documento no encontrado o no autorizado")

    filename = result[0]

    # Eliminar tablas asociadas
    cursor.execute("DELETE FROM extracted_tables WHERE document_id = %s", (id,))
    # Eliminar documento
    cursor.execute("DELETE FROM documents WHERE id = %s", (id,))
    db.commit()

    cursor.close()
    db.close()

    # Eliminar archivo físico
    import os
    file_path = os.path.join("uploaded_pdfs", filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    return {"message": "Documento eliminado correctamente"}