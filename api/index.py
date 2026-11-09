"""API principal FastAPI para el servicio Serverless en Vercel."""

from typing import List, Dict, Any
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel

try:
    from parser import extraer_datos_pdf
    from excel_generator import generar_excel_bytes
except ImportError:
    from api.parser import extraer_datos_pdf
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
    """Modelo de datos para la solicitud de exportación a Excel."""
    rotaciones: List[Dict[str, Any]]
    fecha: str


@app.get("/api/health")
def health():
    """Ruta de verificación de estado del servicio."""
    return {"status": "ok"}


@app.post("/api/parse")
async def parse_pdf_endpoint(file: UploadFile = File(...)):
    """Endpoint para recibir el PDF y retornar los datos extraídos."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="El archivo debe ser un PDF válido."
        )
    contenido = await file.read()
    resultado = extraer_datos_pdf(contenido)
    return resultado


@app.post("/api/export-excel")
async def export_excel_endpoint(req: ExportRequest):
    """Endpoint para generar y descargar el archivo Excel procesado."""
    excel_bytes = generar_excel_bytes(req.rotaciones, req.fecha)
    nombre_limpio = req.fecha.replace("/", "-")
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="Itinerario_{nombre_limpio}.xlsx"'
        }
    )
