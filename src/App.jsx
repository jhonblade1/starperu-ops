import React, { useState } from 'react';
import FileUploader from './components/FileUploader';
import FlightTable from './components/FlightTable';
import { FileSpreadsheet, AlertCircle } from 'lucide-react';
import { saveAs } from 'file-saver';

// En desarrollo local apunta a FastAPI (puerto 8000), en producción usa ruta relativa
const API_BASE = import.meta.env.DEV ? 'http://127.0.0.1:8000' : '';

export default function App() {
  const [rotaciones, setRotaciones] = useState([]);
  const [fecha, setFecha] = useState('');
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState('');

  const handleFile = async (file) => {
    setCargando(true);
    setError('');
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`${API_BASE}/api/process`, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.error || `Error del servidor (${res.status})`);
      }

      const data = await res.json();
      setRotaciones(data.rotaciones || []);
      setFecha(data.fecha || '');
    } catch (err) {
      console.error(err);
      setError(`No se pudo procesar el PDF: ${err.message}`);
    } finally {
      setCargando(false);
    }
  };

  const handleExport = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/export`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rotaciones, fecha }),
      });

      if (!res.ok) {
        throw new Error(`Error al exportar (${res.status})`);
      }

      const blob = await res.blob();
      const cleanDate = (fecha || 'reporte').replace(/\//g, '-');
      saveAs(blob, `Itinerario_${cleanDate}.xlsx`);
    } catch (err) {
      console.error(err);
      alert(`Error al generar el archivo: ${err.message}`);
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 p-6 flex flex-col items-center">
      <div className="max-w-3xl w-full">
        <header className="mb-6 text-center">
          <h1 className="text-3xl font-bold text-slate-800">Operaciones StarPerú — LIM</h1>
          <p className="text-slate-500 text-sm mt-1">
            Procesador automatizado de itinerarios a Excel
          </p>
        </header>

        {fecha && (
          <div className="mb-4 flex items-center justify-between bg-white px-4 py-2.5 rounded-lg border border-slate-200">
            <span className="text-sm text-slate-600 font-medium">Fecha detectada:</span>
            <input
              type="text"
              value={fecha}
              onChange={(e) => setFecha(e.target.value)}
              className="text-center font-bold text-slate-800 border-b border-slate-300 focus:outline-none focus:border-blue-500 px-2 py-0.5"
            />
          </div>
        )}

        <FileUploader cargando={cargando} onFileSelected={handleFile} />

        {error && (
          <div className="mt-4 p-4 bg-red-50 text-red-700 rounded-lg flex items-center gap-3 border border-red-200 text-sm">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {rotaciones.length > 0 && (
          <div className="mt-6 flex justify-end">
            <button
              onClick={handleExport}
              className="bg-emerald-600 hover:bg-emerald-700 text-white px-5 py-2.5 rounded-lg font-semibold flex items-center gap-2 shadow-sm transition cursor-pointer"
            >
              <FileSpreadsheet className="w-5 h-5" />
              Descargar Excel Oficial
            </button>
          </div>
        )}

        <FlightTable rotaciones={rotaciones} />
      </div>
    </div>
  );
}