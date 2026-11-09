"""Módulo para la generación del archivo Excel de operaciones StarPerú."""

import io
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side


def generar_excel_bytes(rotaciones, fecha):
    """Genera y retorna en bytes el libro Excel con formato de itinerario operativo."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Itinerario"

    fecha_val = fecha if (fecha and fecha.strip()) else "06/11/2026"

    # Encabezados oficiales A-N (sin PEA)
    headers = [
        "FECHA", "AEROLIN", "MATRICULA", "AERONAVE", "VUELO_L", "CIUDAD_L", "ETA",
        "AEROLIN", "MATRICULA_S", "AERONAVE_S", "VUELO_S", "CIUDAD_S", "ETD", "T_VUELO"
    ]
    ws.append(headers)

    fill_verde_header = PatternFill(
        start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
    fill_amarillo = PatternFill(
        start_color="FFFF00", end_color="FFFF00", fill_type="solid")
    font_header = Font(name="Calibri", size=11, bold=True)
    font_data = Font(name="Calibri", size=11, bold=False)
    align_center = Alignment(horizontal="center", vertical="center")

    thin_border = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )

    for col in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col)
        cell.font = font_header
        cell.alignment = align_center
        cell.fill = fill_verde_header
        cell.border = thin_border
    ws.row_dimensions[1].height = 22

    fila_actual = 2
    for r in rotaciones:
        sal = r.get("salida", {})
        lleg = r.get("llegada", {})

        # 1. FILA DE SALIDA: Columnas H a M amarillas (cols 8 a 13)
        fila_salida = [
            fecha_val,
            "", "", "", "", "", "",
            sal.get("aerolin", "2I"),
            sal.get("matricula", ""),
            sal.get("aeronave", "B-737-300"),
            sal.get("vuelo", ""),
            sal.get("ciudad", ""),
            sal.get("etd", ""),
            ""
        ]
        ws.append(fila_salida)

        for col_idx in range(1, 15):
            cell = ws.cell(row=fila_actual, column=col_idx)
            cell.font = font_data
            cell.alignment = align_center
            cell.border = thin_border
            if col_idx in [8, 9, 10, 11, 12, 13]:
                cell.fill = fill_amarillo

        ws.row_dimensions[fila_actual].height = 20
        fila_actual += 1

        # 2. FILA DE LLEGADA: Columnas B a G amarillas (cols 2 a 7)
        fila_llegada = [
            fecha_val,
            lleg.get("aerolin", "2I"),
            lleg.get("matricula", ""),
            lleg.get("aeronave", "B-737-300"),
            lleg.get("vuelo", ""),
            lleg.get("ciudad", ""),
            lleg.get("eta", ""),
            "", "", "", "", "", "",
            ""
        ]
        ws.append(fila_llegada)

        for col_idx in range(1, 15):
            cell = ws.cell(row=fila_actual, column=col_idx)
            cell.font = font_data
            cell.alignment = align_center
            cell.border = thin_border
            if col_idx in [2, 3, 4, 5, 6, 7]:
                cell.fill = fill_amarillo

        ws.row_dimensions[fila_actual].height = 20
        fila_actual += 1

    anchos = {
        "A": 14, "B": 11, "C": 16, "D": 16, "E": 11, "F": 12, "G": 11,
        "H": 11, "I": 16, "J": 16, "K": 11, "L": 12, "M": 11, "N": 12
    }
    for col_letter, ancho in anchos.items():
        ws.column_dimensions[col_letter].width = ancho

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()
