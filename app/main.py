from fastapi import FastAPI
from pydantic import BaseModel
from .loader import cargar_documentos
from .search import buscar_respuesta

app = FastAPI(title="API Normativa BCRA")

# Carga todos los PDFs de /docs al iniciar
TEXTO_NORMATIVO = cargar_documentos()

class Consulta(BaseModel):
    pregunta: str

@app.post("/consultar_normativa_bcra")
def consultar_normativa_bcra(consulta: Consulta):
    respuesta = buscar_respuesta(TEXTO_NORMATIVO, consulta.pregunta)

    if not respuesta:
        return {
            "respuesta": "El texto normativo vigente disponible no contiene un desarrollo explícito para esta consulta."
        }

    # Devolvemos solo texto basado en los documentos, sin mencionar archivos ni comunicaciones
    return {"respuesta": respuesta}
