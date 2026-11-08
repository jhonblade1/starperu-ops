from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any

from api.parser import extraer_datos_pdf
from api.excel_generator import generar_excel_bytes

# Esta es la variable que Uvicorn estaba buscando
app = FastAPI()

# Configuración de CORS para permitir la conexión desde React (localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/process")
async def process_pdf(file: UploadFile = File(...)):
    try:
        contenido = await file.read()
        resultado = extraer_datos_pdf(contenido)
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class ExportRequest(BaseModel):
    rotaciones: List[Dict[str, Any]]
    fecha: str


@app.post("/api/export")
async def export_excel(req: ExportRequest):
    try:
        excel_bytes = generar_excel_bytes(req.rotaciones, req.fecha)
        return Response(
            content=excel_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=itinerario.xlsx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
