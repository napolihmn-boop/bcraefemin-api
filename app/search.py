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


# ---------- Detección consultas específicas ---------- #

def _es_pregunta_porcentaje_caja_ahorro_pesos(pregunta: str) -> bool:
    q = _normalizar(pregunta)
    tiene_trigger = any(t in q for t in ["porcentaje", "%", "alicuota", "alícuota", "tasa", "exigencia"])
    tiene_concepto = ("caja" in q or "cajas" in q) and "ahorro" in q and "peso" in q
    return tiene_trigger and tiene_concepto


def _buscar_porcentaje_caja_ahorro_pesos(texto_total: str) -> str | None:
    """
    Identifica la alícuota para depósitos en caja de ahorro en pesos (1.3.2.1. En pesos.)
    usando el formato típico:

    1.3.2.1. En pesos.                         45       20

    Se toma el primer número de esa línea como alícuota aplicable al Grupo A / G-SIB.
    No se inventan valores: si no se encuentra el patrón, se devuelve None.
    """

    lineas = [l.strip() for l in texto_total.split("\n") if l.strip()]

    for linea in lineas:
        ln = linea.lower()
        if "1.3.2.1." in ln and "en pesos" in ln:
            # Buscar todos los números en la misma línea
            nums = re.findall(r"\d+(?:[.,]\d+)?", linea)
            if nums:
                # Primer número = Grupo A / G-SIB
                return nums[0].replace(",", ".")
            # Si no hay números en la misma línea, no forzamos desde otra
            return None

    return None


# ---------- Lógica principal ---------- #

def buscar_respuesta(texto_total: str, pregunta: str) -> str:
    """
    Devuelve un texto normativo basado exclusivamente en texto_total.
    - Caso específico: porcentaje de exigencia para cajas de ahorro en pesos.
    - Caso general: devuelve párrafos relevantes como base para la respuesta.
    """
    if not texto_total.strip():
        return ""

    # 1) Caso específico: porcentaje cajas de ahorro en pesos
    if _es_pregunta_porcentaje_caja_ahorro_pesos(pregunta):
        porcentaje = _buscar_porcentaje_caja_ahorro_pesos(texto_total)

        if porcentaje:
            return (
                "La normativa vigente establece una exigencia de efectivo mínimo para los "
                "depósitos en caja de ahorros en pesos comprendidos en el punto 1.3.2.1 "
                f"equivalente al {porcentaje}% sobre los saldos alcanzados del Grupo A/G-SIB, "
                "conforme al cuadro de alícuotas previsto en el texto ordenado de efectivo mínimo."
            )
        else:
            return (
                "Con la información normativa disponible en el texto cargado no se pudo "
                "identificar de forma explícita una alícuota aplicable a las cajas de ahorro "
                "en pesos. La determinación debe verificarse directamente en el cuadro de "
                "alícuotas vigente del régimen de efectivo mínimo."
            )

    # 2) Caso general: búsqueda de párrafos relevantes
    parrafos = _buscar_parrafos_relevantes(texto_total, pregunta)

    if not parrafos:
        return (
            "Con la información normativa disponible no es posible brindar una respuesta "
            "explícita a esta consulta. La determinación debe efectuarse directamente sobre "
            "el texto vigente."
        )

    return "\n\n".join(parrafos)
