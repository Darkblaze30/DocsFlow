from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query, Security
from app.utils.db_operations import get_db
from app.utils.pdf_processor import extract_tables
from app.utils.file_utils import save_pdf
from app.controllers.userControllers import get_current_user
import json
import os

router = APIRouter(tags=['Documents'])

@router.post("/upload", summary="Subir documento PDF")
def upload_document(file: UploadFile = File(...), user=Security(get_current_user)):
    """
    Sube un archivo PDF, lo guarda en el servidor y extrae las tablas contenidas.

    🔐 Requiere autenticación con JWT (Authorization: Bearer <token>)

    - Solo se permiten archivos PDF.
    - El documento se asocia al usuario y su departamento.
    - Las tablas extraídas se almacenan en la base de datos.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")

    filename, file_path = save_pdf(file)
    tables = extract_tables(file_path)

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO documents (filename, uploaded_by, department, upload_date)
        VALUES (%s, %s, %s, NOW())
    """, (filename, user["id"], user["department_id"]))
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

@router.get("/", summary="Listar documentos disponibles")
def list_documents(user=Security(get_current_user)):
    """
    Lista los documentos disponibles según el rol del usuario.

    🔐 Requiere autenticación con JWT

    - Admin: ve todos los documentos.
    - Usuario: ve solo los documentos de su departamento.
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)

    rol = user["rol"]
    department_id = user["department_id"]

    if rol == "admin":
        cursor.execute("""
            SELECT id, filename, department, upload_date
            FROM documents
            ORDER BY upload_date DESC
        """)
    else:
        cursor.execute("""
            SELECT id, filename, department, upload_date
            FROM documents
            WHERE department = %s
            ORDER BY upload_date DESC
        """, (department_id,))

    documents = cursor.fetchall()
    cursor.close()
    db.close()

    return {"documents": documents}

@router.get("/{id}", summary="Obtener detalles de un documento")
def get_document(id: int, user=Security(get_current_user)):
    """
    Obtiene los detalles de un documento por su ID.

    🔐 Requiere autenticación con JWT

    - Admin: puede ver cualquier documento.
    - Usuario: solo puede ver documentos de su departamento.
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)

    rol = user["rol"]
    department_id = user["department_id"]

    if rol == "admin":
        cursor.execute("""
            SELECT id, filename, department, upload_date
            FROM documents
            WHERE id = %s
        """, (id,))
    else:
        cursor.execute("""
            SELECT id, filename, department, upload_date
            FROM documents
            WHERE id = %s AND department = %s
        """, (id, department_id))

    document = cursor.fetchone()
    cursor.close()
    db.close()

    if not document:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    return {"document": document}

@router.get("/tables/{document_id}", summary="Obtener tablas extraídas de un documento")
def get_tables_by_document(document_id: int, user=Security(get_current_user)):
    """
    Obtiene las tablas extraídas de un documento específico.

    🔐 Requiere autenticación con JWT

    - Admin: puede acceder a cualquier documento.
    - Usuario: solo puede acceder a documentos de su departamento.
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)

    rol = user["rol"]
    department_id = user["department_id"]

    if rol == "admin":
        cursor.execute("""
            SELECT id FROM documents WHERE id = %s
        """, (document_id,))
    else:
        cursor.execute("""
            SELECT id FROM documents
            WHERE id = %s AND department = %s
        """, (document_id, department_id))

    doc = cursor.fetchone()
    if not doc:
        cursor.close()
        db.close()
        raise HTTPException(status_code=403, detail="No tienes acceso a este documento")

    cursor.execute("""
        SELECT id, page_number, description, table_data
        FROM extracted_tables
        WHERE document_id = %s
    """, (document_id,))
    results = cursor.fetchall()

    cursor.close()
    db.close()

    if not results:
        raise HTTPException(status_code=404, detail="No se encontraron tablas para este documento")

    for r in results:
        r["table_data"] = json.loads(r["table_data"])

    return {"document_id": document_id, "tables": results}

@router.get("/search", summary="Buscar tablas por descripción")
def search_tables(query: str, user=Security(get_current_user)):
    """
    Busca tablas por descripción textual.

    🔐 Requiere autenticación con JWT

    - La búsqueda es insensible a mayúsculas/minúsculas.
    - Se normalizan números (ej. '400.000' ≈ '400000').
    - Admin: busca en todos los documentos.
    - Usuario: busca solo en documentos de su departamento.
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)

    rol = user["rol"]
    department_id = user["department_id"]

    normalized_query = query.replace(".", "").replace(",", "").lower()

    if rol == "admin":
        cursor.execute("""
            SELECT t.id, t.page_number, t.description, t.table_data
            FROM extracted_tables t
            JOIN documents d ON t.document_id = d.id
            WHERE REPLACE(LOWER(t.description), '.', '') LIKE %s
        """, (f"%{normalized_query}%",))
    else:
        cursor.execute("""
            SELECT t.id, t.page_number, t.description, t.table_data
            FROM extracted_tables t
            JOIN documents d ON t.document_id = d.id
            WHERE d.department = %s AND REPLACE(LOWER(t.description), '.', '') LIKE %s
        """, (department_id, f"%{normalized_query}%"))

    results = cursor.fetchall()
    cursor.close()
    db.close()

    if not results:
        raise HTTPException(status_code=404, detail="No se encontraron coincidencias")

    for r in results:
        r["table_data"] = json.loads(r["table_data"])

    return {"query": query, "results": results}

@router.delete("/{id}", summary="Eliminar documento (solo admin)")
def delete_document(id: int, user=Security(get_current_user)):
    """
    Elimina un documento y sus tablas asociadas.

    🔐 Requiere autenticación con JWT

    - Solo el administrador puede realizar esta acción.
    - Elimina el registro en la base de datos y el archivo físico.
    """
    if user["rol"] != "admin":
        raise HTTPException(status_code=403, detail="Acceso denegado: solo el administrador puede eliminar documentos")

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT filename FROM documents WHERE id = %s", (id,))
    result = cursor.fetchone()
    if not result:
        cursor.close()
        db.close()
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    filename = result[0]

    cursor.execute("DELETE FROM extracted_tables WHERE document_id = %s", (id,))
    cursor.execute("DELETE FROM documents WHERE id = %s", (id,))
    db.commit()

    cursor.close()
    db.close()

    file_path = os.path.join("uploaded_pdfs", filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    return {"message": "Documento eliminado correctamente"}