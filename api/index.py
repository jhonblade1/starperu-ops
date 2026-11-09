# pylint: disable=wrong-import-order,wrong-import-position,import-error
"""API principal FastAPI para el servicio Serverless en Vercel."""

import sys
from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel

# Configuración de ruta para ejecución local y Serverless
DIRECTORIO_ACTUAL = Path(__file__).resolve().parent
if str(DIRECTORIO_ACTUAL) not in sys.path:
    sys.path.insert(0, str(DIRECTORIO_ACTUAL))

try:
    from pdf_parser import extraer_datos_pdf
    from excel_generator import generar_excel_bytes
except ImportError:
    from api.pdf_parser import extraer_datos_pdf
    from api.excel_generator import generar_excel_bytes

app = FastAPI(title="StarPeru Ops API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ExportRequest(BaseModel):
    """Modelo de datos para la exportación a Excel."""
    rotaciones: List[Dict[str, Any]]
    fecha: str


@app.get("/")
@app.get("/api")
@app.get("/api/health")
def health():
    """Verificación de estado de la API."""
    return {"status": "ok"}


@app.post("/parse")
@app.post("/api/parse")
async def parse_pdf_endpoint(file: UploadFile = File(...)):
    """Extrae las rotaciones desde el PDF subido."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="El archivo debe ser un PDF válido."
        )
    contenido = await file.read()
    return extraer_datos_pdf(contenido)


@app.post("/export-excel")
@app.post("/api/export-excel")
async def export_excel_endpoint(req: ExportRequest):
    """Genera y descarga el archivo Excel oficial."""
    excel_bytes = generar_excel_bytes(req.rotaciones, req.fecha)
    nombre_archivo = f"Itinerario_{req.fecha.replace('/', '-')}.xlsx"
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{nombre_archivo}"'}
    )
