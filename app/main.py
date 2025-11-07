from fastapi import FastAPI
from pydantic import BaseModel
from .loader import cargar_documentos
from .search import buscar_respuesta

app = FastAPI(title="API Normativa BCRA")

# Cargamos el texto normativo al iniciar
TEXTO_NORMATIVO = cargar_documentos()


class Consulta(BaseModel):
    pregunta: str


@app.post("/consultar_normativa_bcra")
def consultar_normativa_bcra(consulta: Consulta):
    """
    Endpoint utilizado por el GPT.
    Devuelve siempre texto basado EXCLUSIVAMENTE en TEXTO_NORMATIVO.
    """
    if not consulta.pregunta or not consulta.pregunta.strip():
        return {
            "respuesta": "La consulta enviada no contiene un requerimiento normativo válido."
        }

    respuesta = buscar_respuesta(TEXTO_NORMATIVO, consulta.pregunta)

    if not respuesta or not respuesta.strip():
        return {
            "respuesta": (
                "Con la información normativa disponible no es posible brindar una "
                "respuesta explícita a esta consulta. La determinación debe efectuarse "
                "directamente sobre el texto vigente."
            )
        }

    return {"respuesta": respuesta}
