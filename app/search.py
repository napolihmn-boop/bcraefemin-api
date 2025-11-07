import re

def _normalizar(texto: str) -> str:
    return texto.lower()

def _buscar_parrafos_relevantes(texto_total: str, pregunta: str, min_len: int = 60):
    """
    Busca párrafos del texto donde aparezcan las palabras clave de la pregunta.
    Si la pregunta menciona tasas o porcentajes, prioriza líneas con números o '%'.
    """
    q = _normalizar(pregunta)
    palabras = [p for p in re.split(r"\W+", q) if len(p) > 3]
    if not palabras:
        return []

    # Convertir texto a líneas para análisis granular
    lineas = [l.strip() for l in texto_total.split("\n") if len(l.strip()) >= min_len]
    relevantes = []

    busca_tasa = any(t in q for t in ["porcentaje", "%", "tasa", "alicuota", "alícuota", "exigencia"])

    for linea in lineas:
        ln = linea.lower()
        score = sum(1 for w in palabras if w in ln)
        # Damos más peso si hay números cuando la pregunta habla de tasas
        if busca_tasa and re.search(r"\d+(?:[.,]\d+)?", linea):
            score += 1
        if score >= 2:
            relevantes.append((score, linea))

    # Ordenar por relevancia y devolver los mejores fragmentos
    relevantes.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in relevantes[:8]]

def buscar_respuesta(texto_total: str, pregunta: str) -> str:
    """
    Devuelve fragmentos relevantes del texto normativo cargado, sin interpretar.
    El GPT usará estos fragmentos para construir la respuesta final.
    """
    if not texto_total.strip():
        return ""

    parrafos = _buscar_parrafos_relevantes(texto_total, pregunta)

    if not parrafos:
        return (
            "No se identificaron fragmentos específicos del texto normativo que respondan "
            "directamente a esta consulta. Puede requerirse una revisión manual del texto vigente."
        )

    # Devolver los fragmentos juntos, sin alterarlos
    return "\n\n".join(parrafos)
