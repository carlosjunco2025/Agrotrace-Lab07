import './App.css'

const fundos = [
  {
    id: 1,
    nombre_fundo: 'Fundo Santa Elena',
    propietario_dni_ruc: '20481234567',
    hectareas: '48.50',
    valido_exportacion: true,
    cupo_diario_lotes: 12,
  },
  {
    id: 2,
    nombre_fundo: 'Fundo Valle Verde',
    propietario_dni_ruc: '45872136',
    hectareas: '32.00',
    valido_exportacion: false,
    cupo_diario_lotes: 3,
  },
  {
    id: 3,
    nombre_fundo: 'Fundo Los Olivos',
    propietario_dni_ruc: '20567891234',
    hectareas: '65.75',
    valido_exportacion: true,
    cupo_diario_lotes: 0,
  },
]

const lotes = [
  {
    id: 1,
    codigo_lote: 'LOT-2026-001',
    toneladas_brutas: '12.50',
    porcentaje_descarte: '1.20',
    estado_evaluacion: 'PROCESADO',
    fundo: 1,
  },
  {
    id: 2,
    codigo_lote: 'LOT-2026-002',
    toneladas_brutas: '8.75',
    porcentaje_descarte: '2.40',
    estado_evaluacion: 'EN_PROCESO',
    fundo: 1,
  },
  {
    id: 3,
    codigo_lote: 'LOT-2026-003',
    toneladas_brutas: '15.00',
    porcentaje_descarte: '0.80',
    estado_evaluacion: 'PENDIENTE',
    fundo: 2,
  },
  {
    id: 4,
    codigo_lote: 'LOT-2026-004',
    toneladas_brutas: '6.25',
    porcentaje_descarte: '3.10',
    estado_evaluacion: 'EN_PROCESO',
    fundo: 3,
  },
]

function estadoVisible(estado) {
  return estado === 'PROCESADO'
    ? 'Aprobado'
    : estado === 'EN_PROCESO'
      ? 'Bajo Inspección'
      : 'En Revisión'
}

function claseEstado(estado) {
  return estado === 'PROCESADO'
    ? 'badge badge--approved'
    : estado === 'EN_PROCESO'
      ? 'badge badge--inspection'
      : 'badge badge--review'
}

function App() {
  const totalToneladas = lotes.reduce(
    (total, lote) => total + Number(lote.toneladas_brutas),
    0,
  )
  const lotesEnRevision = lotes.filter(
    (lote) => lote.estado_evaluacion !== 'PROCESADO',
  ).length

  return (
    <main className="agrotrace-container">
      <header className="page-header">
        <div>
          <p className="eyebrow">Plataforma de trazabilidad agrícola</p>
          <h1>AgroTrace</h1>
          <p className="page-intro">
            Control de fundos productores y lotes recepcionados.
          </p>
        </div>
        <span className="demo-label">Vista demostrativa · Datos de ejemplo</span>
      </header>

      <section className="summary-grid" aria-label="Resumen de recepción">
        <article className="summary-card">
          <span className="summary-label">Fundos registrados</span>
          <strong>{fundos.length}</strong>
          <span className="summary-footnote">unidades productoras</span>
        </article>
        <article className="summary-card">
          <span className="summary-label">Lotes recepcionados</span>
          <strong>{lotes.length}</strong>
          <span className="summary-footnote">registros en el periodo</span>
        </article>
        <article className="summary-card">
          <span className="summary-label">Peso bruto total</span>
          <strong>{totalToneladas.toFixed(2)} t</strong>
          <span className="summary-footnote">suma de todos los lotes</span>
        </article>
        <article className="summary-card summary-card--attention">
          <span className="summary-label">Requieren atención</span>
          <strong>{lotesEnRevision}</strong>
          <span className="summary-footnote">pendientes o en inspección</span>
        </article>
      </section>

      {lotesEnRevision > 0 && (
        <aside className="global-alert" role="status">
          <span className="alert-icon" aria-hidden="true">!</span>
          <p>
            Hay <strong>{lotesEnRevision}</strong> lotes pendientes o bajo
            inspección que requieren seguimiento.
          </p>
        </aside>
      )}

      <section className="section-heading">
        <div>
          <p className="eyebrow">Relación productor → recepción</p>
          <h2>Fundos productores</h2>
        </div>
        <span className="record-count">{fundos.length} fundos</span>
      </section>

      {fundos.length === 0 ? (
        <div className="empty-state">
          <span aria-hidden="true">⌂</span>
          <p>No hay fundos productores registrados.</p>
        </div>
      ) : (
        <div className="fundos-grid">
          {fundos.map((fundo) => {
            const lotesDelFundo = lotes.filter(
              (lote) => lote.fundo === fundo.id,
            )
            const pesoTotalFundo = lotesDelFundo.reduce(
              (total, lote) => total + Number(lote.toneladas_brutas),
              0,
            )
            const requiereAtencion =
              fundo.cupo_diario_lotes <= 2 ||
              lotesDelFundo.some(
                (lote) =>
                  Number(lote.toneladas_brutas) < 7 ||
                  lote.estado_evaluacion !== 'PROCESADO',
              )

            return (
              <article className="fundo-card" key={fundo.id}>
                <div className="fundo-card-header">
                  <div className="fundo-avatar" aria-hidden="true">
                    {fundo.nombre_fundo.charAt(6)}
                  </div>
                  <div className="fundo-title">
                    <h3>{fundo.nombre_fundo}</h3>
                    <span>RUC / DNI: {fundo.propietario_dni_ruc}</span>
                  </div>
                  <span
                    className={
                      fundo.valido_exportacion
                        ? 'badge badge--approved'
                        : 'badge badge--review'
                    }
                  >
                    {fundo.valido_exportacion
                      ? 'Apto exportación'
                      : 'En revisión'}
                  </span>
                </div>

                <div className="fundo-metrics">
                  <div>
                    <span>Superficie</span>
                    <strong>{Number(fundo.hectareas).toFixed(2)} ha</strong>
                  </div>
                  <div>
                    <span>Cupo disponible</span>
                    <strong>{fundo.cupo_diario_lotes} lotes</strong>
                  </div>
                  <div>
                    <span>Peso acumulado</span>
                    <strong>{pesoTotalFundo.toFixed(2)} t</strong>
                  </div>
                  <div>
                    <span>Lotes asociados</span>
                    <strong>{lotesDelFundo.length}</strong>
                  </div>
                </div>
                <div
                  className="quota-track"
                  aria-label={`Cupo disponible: ${fundo.cupo_diario_lotes} lotes`}
                >
                  <span
                    className="quota-fill"
                    style={{
                      width: `${Math.min(
                        (fundo.cupo_diario_lotes / 12) * 100,
                        100,
                      )}%`,
                    }}
                  />
                </div>

                {requiereAtencion && (
                  <div className="registro-alerta">
                    <span aria-hidden="true">!</span>
                    <p>
                      Atención requerida: revise el cupo, el peso o los lotes
                      pendientes de este fundo.
                    </p>
                  </div>
                )}

                <div className="lotes-section">
                  <div className="lotes-heading">
                    <h4>Lotes recepcionados</h4>
                    <span>{lotesDelFundo.length} registros</span>
                  </div>
                  {lotesDelFundo.length === 0 ? (
                    <p className="empty-lotes">
                      Este fundo todavía no tiene lotes recepcionados.
                    </p>
                  ) : (
                    <ul className="lotes-list">
                      {lotesDelFundo.map((lote) => (
                        <li className="lote-row" key={lote.id}>
                          <div className="lote-description">
                            <strong>{lote.codigo_lote}</strong>
                            <span>
                              Descarte: {Number(lote.porcentaje_descarte).toFixed(2)}%
                            </span>
                          </div>
                          <span className="lote-weight">
                            {Number(lote.toneladas_brutas).toFixed(2)} t
                          </span>
                          <span className={claseEstado(lote.estado_evaluacion)}>
                            {estadoVisible(lote.estado_evaluacion)}
                          </span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </article>
            )
          })}
        </div>
      )}

      {lotes.length === 0 && (
        <p className="empty-global">
          No hay lotes recepcionados para mostrar.
        </p>
      )}

      <footer className="page-footer">
        <span>AgroTrace · Desarrollo de Aplicaciones Empresariales</span>
        <span>Los datos mostrados son mock y no provienen de la API.</span>
      </footer>
    </main>
  )
}

export default App
