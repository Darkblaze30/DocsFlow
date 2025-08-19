import pdfplumber

def extract_tables(file_path):
    tables = []
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text_lines = page.extract_text().split("\n")
            page_tables = page.extract_tables()

            for table in page_tables:
                # Buscar título: línea anterior a la primera fila de la tabla
                first_row = table[0]
                title = None
                for line in text_lines:
                    if all(cell in line for cell in first_row[:2]): 
                        idx = text_lines.index(line)
                        if idx > 0:
                            title = text_lines[idx - 1]
                        break

                tables.append({
                    "page": i + 1,
                    "description": title or "Tabla sin título",
                    "data": table
                })
    return tables