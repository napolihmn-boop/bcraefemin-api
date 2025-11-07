import re

def buscar_respuesta(texto_total: str, pregunta: str) -> str:
    # Pasamos la pregunta a minúsculas
    q = pregunta.lower()
    # Tomamos palabras "relevantes" (más de 4 letras)
    palabras = [p for p in re.split(r"\W+", q) if len(p) > 4]

    if not palabras:
        return ""

    # Separar en párrafos (líneas largas)
    parrafos = [p.strip() for p in texto_total.split("\n") if len(p.strip()) > 80]

    relevantes = []
    for p in parrafos:
        # Score: cuántas palabras clave aparecen en el párrafo
        score = sum(1 for w in palabras if w in p.lower())
        if score >= 2:
            relevantes.append((score, p))

    if not relevantes:
        return ""

    # Ordenamos por relevancia y tomamos hasta 5 párrafos
    relevantes.sort(key=lambda x: x[0], reverse=True)
    seleccion = [p for _, p in relevantes[:5]]

    return "\n\n".join(seleccion)
