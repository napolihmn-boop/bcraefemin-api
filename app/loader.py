import os
from pypdf import PdfReader

DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "docs")

def cargar_documentos():
    textos = []
    for nombre in os.listdir(DOCS_DIR):
        if nombre.lower().endswith(".pdf"):
            path = os.path.join(DOCS_DIR, nombre)
            reader = PdfReader(path)
            contenido = ""
            for page in reader.pages:
                contenido += page.extract_text() or ""
            textos.append(contenido)
    # Un solo gran texto consolidado con todo lo vigente que cargaste
    return "\n".join(textos)