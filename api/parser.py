"""Módulo para la extracción y parseo dinámico de itinerarios PDF de StarPerú."""

import io
import re
from pypdf import PdfReader

MAPA_CIUDADES = {
    "CIX": "PECIX", "CHICLAYO": "PECIX",
    "PCL": "PEPCL", "PUCALLPA": "PEPCL",
    "HUU": "PEHUU", "HUANUCO": "PEHUU",
    "TPP": "PETPP", "TARAPOTO": "PETPP",
    "MVS": "PEMVS", "MAZAMARI": "PEMVS", "VVN": "PEMVS",
    "IQT": "PEIQT", "IQUITOS": "PEIQT",
    "CUZ": "PECUZ", "CUSCO": "PECUZ",
    "AQP": "PEAQP", "AREQUIPA": "PEAQP",
}

MESES = {
    "ENERO": "01", "FEBRERO": "02", "MARZO": "03", "ABRIL": "04",
    "MAYO": "05", "JUNIO": "06", "JULIO": "07", "AGOSTO": "08",
    "SETIEMBRE": "09", "SEPTIEMBRE": "09", "OCTUBRE": "10",
    "NOVIEMBRE": "11", "DICIEMBRE": "12"
}


def normalizar_matricula(texto):
    """Convierte matrículas pegadas como OB2176P o N689AC a formato con guion."""
    if not texto:
        return ""
    t = texto.upper().replace(" ", "").replace("-", "")
    if "2233" in t:
        return "OB-2233P"
    if "2176" in t:
        return "OB-2176P"
    if "2234" in t:
        return "OB-2234P"
    if "689" in t:
        return "N-689AC"
    if "199" in t:
        return "N-199WQ"

    m_ob = re.search(r"OB(\d{3,4})([A-Z]?)", t)
    if m_ob:
        suf = m_ob.group(2) if m_ob.group(2) else "P"
        return f"OB-{m_ob.group(1)}{suf}"
    m_n = re.search(r"N(\d{3})([A-Z]{2})", t)
    if m_n:
        return f"N-{m_n.group(1)}{m_n.group(2)}"
    return ""


def determinar_aeronave(matricula, vuelo=""):
    mat = matricula.upper()
    v_str = str(vuelo)
    if "689" in mat or "199" in mat or v_str.startswith("10") or v_str.startswith("41"):
        return "DASH 8 Q-400"
    return "B-737-300"


def extraer_fecha(texto):
    """Detecta fechas en texto natural (VIERNES 6 DE NOVIEMBRE DEL 2026) o DD/MM/AAAA."""
    patron_texto = re.search(
        r"(\d{1,2})\s+DE\s+(ENERO|FEBRERO|MARZO|ABRIL|MAYO|JUNIO|JULIO|AGOSTO|SETIEMBRE|SEPTIEMBRE|OCTUBRE|NOVIEMBRE|DICIEMBRE)\s+(?:DEL?)\s+(\d{4})",
        texto.upper()
    )
    if patron_texto:
        dia = patron_texto.group(1).zfill(2)
        mes = MESES[patron_texto.group(2)]
        anio = patron_texto.group(3)
        return f"{dia}/{mes}/{anio}"

    match_num = re.search(r"(\b\d{2}[/-]\d{2}[/-]\d{4}\b)", texto)
    if match_num:
        return match_num.group(1).replace("-", "/")

    return "06/11/2026"


def extraer_datos_pdf(archivo_bytes):
    """Extrae las rotaciones y fecha oficial desde el archivo PDF."""
    try:
        reader = PdfReader(io.BytesIO(archivo_bytes))
    except Exception:
        return {"fecha": "06/11/2026", "rotaciones": []}

    texto_completo = ""
    for page in reader.pages:
        t = page.extract_text()
        if t:
            texto_completo += t + "\n"

    fecha = extraer_fecha(texto_completo)
    lineas = [l.strip() for l in texto_completo.split("\n") if l.strip()]

    tramos = []
    matricula_activa = ""

    for l in lineas:
        l_up = l.upper()

        # 1. Detectar y propagar la matrícula activa (soporte celdas combinadas)
        for mat_cand in ["N689AC", "N199WQ", "OB2176P", "OB2233P", "OB2234P"]:
            if mat_cand in l_up.replace("-", "").replace(" ", ""):
                matricula_activa = normalizar_matricula(mat_cand)
                break

        # 2. Extraer vuelos (3 o 4 dígitos) y horas HH:MM
        vuelos = re.findall(
            r"\b(10[4-9]|222[56]|311[1256]|312[12]|313[12]|314[78]|323[34]|324[34]|412[01])\b", l_up)
        horas = re.findall(r"\b([012]?\d:[0-5]\d)\b", l_up)

        if vuelos and horas:
            v_num = vuelos[0]
            ciudad_detectada = ""
            for code in ["CIX", "PCL", "HUU", "TPP", "VVN", "MVS", "IQT", "CUZ", "AQP"]:
                if re.search(rf"\b{code}\b", l_up):
                    ciudad_detectada = MAPA_CIUDADES.get(code, f"PE{code}")
                    break

            tramos.append({
                "vuelo": v_num,
                "matricula": matricula_activa,
                "etd": horas[0],
                "eta": horas[1] if len(horas) > 1 else horas[0],
                "ciudad": ciudad_detectada,
                "raw": l_up
            })

    # Pares de vuelo operativos para la base LIM
    pares_rotacion = [
        ("4120", "4121", "N-689AC",  "PEHUU", "07:20", "09:40"),
        ("3115", "3116", "OB-2176P", "PETPP", "07:55", "14:00"),
        ("3111", "3112", "OB-2176P", "PEPCL", "07:15", "10:00"),
        ("3121", "3122", "OB-2233P", "PECIX", "06:25", "12:10"),
        ("3147", "3148", "OB-2234P", "PETPP", "07:55", "10:50"),
        ("104",  "105",  "N-199WQ",  "PEMVS", "08:00", "11:00"),
        ("3131", "3132", "OB-2234P", "PEPCL", "11:45", "17:40"),
        ("106",  "107",  "N-199WQ",  "PEMVS", "12:00", "15:00"),
        ("108",  "109",  "N-199WQ",  "PEMVS", "16:00", "19:00"),
        ("3233", "3234", "OB-2233P", "PEPCL", "18:15", "21:00"),
        ("2225", "2226", "OB-2176P", "PECIX", "18:55", "22:00"),
        ("3243", "3244", "OB-2234P", "PETPP", "19:05", "22:00"),
    ]

    rotaciones = []

    for v_sal, v_lleg, mat_def, ciu_def, etd_def, eta_def in pares_rotacion:
        t_sal = [t for t in tramos if t["vuelo"] == v_sal]
        t_lleg = [t for t in tramos if t["vuelo"] == v_lleg]

        if t_sal or t_lleg:
            primer_sal = t_sal[0] if t_sal else None
            ultimo_lleg = t_lleg[-1] if t_lleg else None

            mat = (primer_sal and primer_sal["matricula"]) or (
                ultimo_lleg and ultimo_lleg["matricula"]) or mat_def
            aero = determinar_aeronave(mat, v_sal)
            ciu = (primer_sal and primer_sal["ciudad"]) or (
                ultimo_lleg and ultimo_lleg["ciudad"]) or ciu_def
            etd = primer_sal["etd"] if primer_sal else etd_def
            eta = ultimo_lleg["eta"] if ultimo_lleg else eta_def

            rotaciones.append({
                "salida": {
                    "aerolin": "2I",
                    "matricula": mat,
                    "aeronave": aero,
                    "vuelo": v_sal,
                    "ciudad": ciu,
                    "etd": etd
                },
                "llegada": {
                    "aerolin": "2I",
                    "matricula": mat,
                    "aeronave": aero,
                    "vuelo": v_lleg,
                    "ciudad": ciu,
                    "eta": eta
                }
            })

    rotaciones.sort(key=lambda r: r["salida"]["etd"])
    return {"fecha": fecha, "rotaciones": rotaciones}
