import React from 'react';
import { FileUp, Loader2 } from 'lucide-react';

export default function FileUploader({ onFileSelected, cargando }) {
  const handleChange = (e) => {
    const file = e.target.files[0];
    if (file) onFileSelected(file);
  };

  return (
    <div className="border-2 border-dashed border-slate-300 rounded-xl p-8 text-center hover:bg-slate-50 transition cursor-pointer relative bg-white">
      <input
        type="file"
        accept=".pdf,application/pdf"
        onChange={handleChange}
        disabled={cargando}
        className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
      />
      {cargando ? (
        <div className="flex flex-col items-center gap-3 text-blue-600">
          <Loader2 className="animate-spin w-10 h-10" />
          <span className="font-medium text-slate-600">Procesando programación de vuelos...</span>
        </div>
      ) : (
        <div className="flex flex-col items-center gap-3 text-slate-500">
          <FileUp className="w-12 h-12 text-slate-400" />
          <span className="font-semibold text-lg text-slate-700">Arrastra o selecciona el PDF de vuelos</span>
          <span className="text-xs text-slate-400">Formato oficial de StarPerú</span>
        </div>
      )}
    </div>
  );
}