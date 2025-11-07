import os
import re
from pypdf import PdfReader

DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "docs")


def _extraer_texto_pdf(path: str) -> str:
    reader = PdfReader(path)
    partes = []
    for page in reader.pages:
        txt = page.extract_text() or ""
        partes.append(txt)
    texto = "\n".join(partes)

    # Normalización básica
    texto = texto.replace("\r", "\n")
    # Unificar espacios
    texto = re.sub(r"[ \t]+", " ", texto)
    # Normalizar saltos múltiples
    texto = re.sub(r"\n{2,}", "\n", texto)

    return texto


def cargar_documentos() -> str:
    """
    Carga y concatena el texto de todos los PDFs en /docs.
    Devuelve un único string normalizado que se usará como base de búsqueda.
    """
    textos = []
    if not os.path.isdir(DOCS_DIR):
        return ""

    for nombre in os.listdir(DOCS_DIR):
        if nombre.lower().endswith(".pdf"):
            path = os.path.join(DOCS_DIR, nombre)
            try:
                contenido = _extraer_texto_pdf(path)
                if contenido.strip():
                    textos.append(contenido)
            except Exception as e:
                # En producción podrías loguear esto si querés
                continue

    texto_total = "\n".join(textos)

    # Normalización adicional global
    texto_total = re.sub(r"[ \t]+", " ", texto_total)
    texto_total = re.sub(r"\n{2,}", "\n", texto_total)

    return texto_total
