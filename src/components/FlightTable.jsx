import React from 'react';
import { ArrowUpRight, ArrowDownLeft } from 'lucide-react';

export default function FlightTable({ rotaciones }) {
  if (!rotaciones || !rotaciones.length) return null;

  return (
    <div className="mt-6 bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
      <div className="px-5 py-3.5 bg-slate-50 border-b border-slate-200 font-semibold text-slate-700">
        Vuelos Reconocidos y Emparejados ({rotaciones.length} rotaciones)
      </div>
      <div className="divide-y divide-slate-100 max-h-96 overflow-y-auto">
        {rotaciones.map((par, idx) => (
          <div key={idx} className="p-4 hover:bg-slate-50 transition flex items-center justify-between text-sm">
            {/* Salida */}
            <div className="flex items-center gap-3">
              <div className="p-2 bg-amber-50 text-amber-700 rounded-lg">
                <ArrowUpRight className="w-4 h-4" />
              </div>
              <div>
                <div className="font-bold text-slate-800">
                  Vuelo {par.salida.vuelo} <span className="text-slate-400 font-normal">→ {par.salida.ciudad}</span>
                </div>
                <div className="text-xs text-slate-500">
                  {par.salida.matricula} ({par.salida.aeronave}) | ETD: <span className="font-semibold">{par.salida.etd}</span>
                </div>
              </div>
            </div>

            {/* Llegada */}
            <div className="flex items-center gap-3 text-right">
              <div>
                <div className="font-bold text-slate-800">
                  <span className="text-slate-400 font-normal">{par.llegada.ciudad} → </span> Vuelo {par.llegada.vuelo}
                </div>
                <div className="text-xs text-slate-500">
                  ETA: <span className="font-semibold text-emerald-600">{par.llegada.eta}</span>
                </div>
              </div>
              <div className="p-2 bg-emerald-50 text-emerald-700 rounded-lg">
                <ArrowDownLeft className="w-4 h-4" />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}