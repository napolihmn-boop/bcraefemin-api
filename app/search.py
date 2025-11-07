import re


def _normalizar(texto: str) -> str:
    return texto.lower()


def _buscar_parrafos_relevantes(texto_total: str, pregunta: str, min_len: int = 80):
    q = _normalizar(pregunta)
    palabras = [p for p in re.split(r"\W+", q) if len(p) > 4]
    if not palabras:
        return []

    parrafos = [p.strip() for p in texto_total.split("\n") if len(p.strip()) >= min_len]
    relevantes = []

    for p in parrafos:
        pl = p.lower()
        score = sum(1 for w in palabras if w in pl)
        if score >= 2:
            relevantes.append((score, p))

    relevantes.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in relevantes[:5]]


# ---------- Lógica específica para porcentajes ---------- #

def _es_pregunta_porcentaje_caja_ahorro_pesos(pregunta: str) -> bool:
    q = _normalizar(pregunta)
    tiene_porcentaje = any(g in q for g in ["porcentaje", "%", "alicuota", "alícuota", "tasa", "exigencia"])
    tiene_caja_ahorro_pesos = ("caja" in q or "cajas" in q) and "ahorro" in q and "peso" in q
    return tiene_porcentaje and tiene_caja_ahorro_pesos


def _buscar_porcentaje_caja_ahorro_pesos(texto_total: str):
    """
    Intenta ubicar el porcentaje de exigencia para cajas de ahorro en pesos
    buscando líneas o fragmentos donde aparezca el concepto y un número con '%'.
    Está pensado para texto proveniente de tablas o cuadros del régimen.
    """

    # Trabajamos por líneas para respetar cómo suelen bajar las tablas
    lineas = [l.strip() for l in texto_total.split("\n") if l.strip()]

    candidatos = []
    for i, linea in enumerate(lineas):
        ln = linea.lower()

        # Buscamos menciones al concepto
        if ("caja" in ln or "cajas" in ln) and "ahorro" in ln and "peso" in ln:
            # Buscamos porcentaje en la misma línea
            m = re.search(r"(\d+(?:[.,]\d+)?)\s*%", linea)
            if m:
                candidatos.append((i, m.group(1)))
                continue

            # Si no está en la misma, miramos 1-2 líneas siguientes (típico en tablas PDF)
            for j in range(1, 3):
                if i + j < len(lineas):
                    m2 = re.search(r"(\d+(?:[.,]\d+)?)\s*%", lineas[i + j])
                    if m2:
                        candidatos.append((i + j, m2.group(1)))
                        break

    if not candidatos:
        return None

    # Si hay varios candidatos, tomamos el primero (podés refinar si hiciera falta)
    _, porcentaje = sorted(candidatos, key=lambda x: x[0])[0]
    return porcentaje.replace(",", ".")


def buscar_respuesta(texto_total: str, pregunta: str) -> str:
    """
    Devuelve un texto de respuesta basado exclusivamente en texto_total.
    - Caso específico: porcentaje de exigencia para cajas de ahorro en pesos.
    - Caso general: devuelve párrafos relevantes como base para que el GPT los sintetice.
    """
    if not texto_total.strip():
        return ""

    # 1) Caso específico: porcentaje cajas de ahorro en pesos
    if _es_pregunta_porcentaje_caja_ahorro_pesos(pregunta):
        porcentaje = _buscar_porcentaje_caja_ahorro_pesos(texto_total)

        if porcentaje:
            return (
                f"La normativa vigente establece una exigencia de efectivo mínimo para las "
                f"cajas de ahorro en pesos equivalente al {porcentaje}% sobre los saldos "
                f"alcanzados, conforme al cuadro de alícuotas del régimen de efectivo mínimo. "
                f"Este valor surge del texto normativo consolidado disponible."
            )
        else:
            return (
                "Con la información normativa disponible en el texto cargado no se pudo "
                "identificar de forma explícita un porcentaje de exigencia aplicable a las "
                "cajas de ahorro en pesos. La determinación debe verificarse directamente "
                "en el cuadro de alícuotas vigente del régimen de efectivo mínimo."
            )

    # 2) Caso general: búsqueda de párrafos relevantes
    parrafos = _buscar_parrafos_relevantes(texto_total, pregunta)

    if not parrafos:
        return ""

    return "\n\n".join(parrafos)
