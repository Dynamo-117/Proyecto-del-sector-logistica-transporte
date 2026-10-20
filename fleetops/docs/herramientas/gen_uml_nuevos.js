// Genera los diagramas UML (SVG -> PNG) de Facade, Flyweight y Proxy.
// Uso:  NODE_PATH=<carpeta con node_modules> FLEETOPS_OUT=<carpeta> node gen_uml_nuevos.js
const fs = require("fs");
const puppeteer = require("puppeteer-core");
const OUT = process.env.FLEETOPS_OUT || "./img/";
fs.mkdirSync(OUT, { recursive: true });

const FT = "Segoe UI, Arial, sans-serif";
const FC = "Consolas, 'Cascadia Mono', monospace";
const INK = "#1a1a1a", LINE = "#333333", DEP = "#555555", LABEL = "#7a4a00";
const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

function box(x, y, w, { title, stereo, body = [], h, abstract = false }) {
  const lines = Array.isArray(title) ? title : [title];
  const headerH = 16 + (stereo ? 22 : 0) + lines.length * 24 + 8;
  const bodyH = body.reduce((a, l) => a + (l === "---" ? 14 : 22), 0);
  const H = h || headerH + (body.length ? bodyH + 22 : 6);
  let s = `<rect x="${x}" y="${y}" width="${w}" height="${H}" rx="6" fill="#fff" stroke="${LINE}" stroke-width="1.7"/>`;
  let ty = y + 26;
  if (stereo) { s += `<text x="${x + w / 2}" y="${ty}" text-anchor="middle" font-family="${FT}" font-style="italic" font-size="14" fill="#555">${esc(stereo)}</text>`; ty += 22; }
  for (const t of lines) {
    s += `<text x="${x + w / 2}" y="${ty}" text-anchor="middle" font-family="${FT}" font-weight="700" font-style="${abstract ? "italic" : "normal"}" font-size="19" fill="${INK}">${esc(t)}</text>`;
    ty += 24;
  }
  const sepY = y + headerH - 6;
  if (body.length) s += `<line x1="${x}" y1="${sepY}" x2="${x + w}" y2="${sepY}" stroke="${LINE}" stroke-width="1.3"/>`;
  let by = sepY + 24;
  for (const l of body) {
    if (l === "---") { s += `<line x1="${x}" y1="${by - 14}" x2="${x + w}" y2="${by - 14}" stroke="${LINE}" stroke-width="1"/>`; by += 14; continue; }
    s += `<text x="${x + 16}" y="${by}" font-family="${FC}" font-size="14.5" fill="${INK}">${esc(l)}</text>`;
    by += 22;
  }
  return { svg: s, h: H, x, y, w, cx: x + w / 2, cy: y + H / 2, bottom: y + H, right: x + w };
}

function open(x2, y2, ang, col = DEP) {
  const L = 13, a1 = ang + Math.PI * 0.85, a2 = ang - Math.PI * 0.85;
  return `<line x1="${x2}" y1="${y2}" x2="${x2 + L * Math.cos(a1)}" y2="${y2 + L * Math.sin(a1)}" stroke="${col}" stroke-width="1.7"/><line x1="${x2}" y1="${y2}" x2="${x2 + L * Math.cos(a2)}" y2="${y2 + L * Math.sin(a2)}" stroke="${col}" stroke-width="1.7"/>`;
}
function dep(x1, y1, x2, y2, label, pos = "above") {
  let s = `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${DEP}" stroke-width="1.7" stroke-dasharray="7,5"/>` + open(x2, y2, Math.atan2(y2 - y1, x2 - x1));
  if (label) {
    const mx = (x1 + x2) / 2, my = (y1 + y2) / 2;
    s += pos === "right"
      ? `<text x="${mx + 10}" y="${my + 5}" font-family="${FT}" font-style="italic" font-size="14" fill="${LABEL}">${esc(label)}</text>`
      : `<text x="${mx}" y="${my - 10}" text-anchor="middle" font-family="${FT}" font-style="italic" font-size="14" fill="${LABEL}">${esc(label)}</text>`;
  }
  return s;
}
function tree(parentCx, parentBottom, spineY, childTop, centers, dashed = false) {
  const tri = 20, half = 12, da = dashed ? ' stroke-dasharray="7,5"' : "";
  let s = `<polygon points="${parentCx},${parentBottom} ${parentCx - half},${parentBottom + tri} ${parentCx + half},${parentBottom + tri}" fill="#fff" stroke="${LINE}" stroke-width="1.7"/>`;
  s += `<line x1="${parentCx}" y1="${parentBottom + tri}" x2="${parentCx}" y2="${spineY}" stroke="${LINE}" stroke-width="1.7"${da}/>`;
  const mn = Math.min(...centers, parentCx), mx = Math.max(...centers, parentCx);
  if (mx > mn) s += `<line x1="${mn}" y1="${spineY}" x2="${mx}" y2="${spineY}" stroke="${LINE}" stroke-width="1.7"${da}/>`;
  for (const c of centers) s += `<line x1="${c}" y1="${spineY}" x2="${c}" y2="${childTop}" stroke="${LINE}" stroke-width="1.7"${da}/>`;
  return s;
}
// linea horizontal con rombo hueco/relleno en (x1,y) y punta abierta en (x2,y)
function diamondH(x1, x2, y, filled, label, lx, ly) {
  const d = 24;
  let s = `<line x1="${x1 + d}" y1="${y}" x2="${x2}" y2="${y}" stroke="${LINE}" stroke-width="1.7"/>`;
  s += `<polygon points="${x1},${y} ${x1 + 12},${y - 8} ${x1 + d},${y} ${x1 + 12},${y + 8}" fill="${filled ? LINE : "#fff"}" stroke="${LINE}" stroke-width="1.7"/>`;
  s += open(x2, y, 0, LINE);
  if (label) s += `<text x="${lx}" y="${ly}" text-anchor="middle" font-family="${FT}" font-style="italic" font-size="14" fill="${LABEL}">${esc(label)}</text>`;
  return s;
}
function note(x, y, w, lines) {
  const h = 22 * lines.length + 22, f = 16;
  let s = `<polygon points="${x},${y} ${x + w - f},${y} ${x + w},${y + f} ${x + w},${y + h} ${x},${y + h}" fill="#fff8dc" stroke="#9a8a4a" stroke-width="1.4"/><polyline points="${x + w - f},${y} ${x + w - f},${y + f} ${x + w},${y + f}" fill="none" stroke="#9a8a4a" stroke-width="1.2"/>`;
  lines.forEach((l, i) => { s += `<text x="${x + 14}" y="${y + 28 + i * 22}" font-family="${FT}" font-size="14" fill="#4a3f10">${esc(l)}</text>`; });
  return { svg: s, h };
}
const wrap = (w, h, b) => `<svg viewBox="0 0 ${w} ${h}" width="${w}" height="${h}" xmlns="http://www.w3.org/2000/svg" font-family="${FT}"><rect width="${w}" height="${h}" fill="#fff"/>${b}</svg>`;

// -------------------------------------------------------------------- FACADE
function facade() {
  const W = 1650, H = 660; let b = "";
  const cliente = box(40, 200, 330, { title: "resumen_routes.py", stereo: "«Cliente»", body: ["GET /resumen", "+ resumen_operativo(request)"] });
  const fachada = box(520, 140, 540, {
    title: "ResumenOperativoFacade", stereo: "«Fachada»",
    body: ["- _flota : FlotaApi", "- _rutas : RutasApi", "- _mantenimiento : MantenimientoApi", "- _tracking : TrackingApi", "---", "+ obtener(headers) : ResumenOperativo", "- _armar_flota() / _armar_rutas()", "- _armar_mantenimiento() / _armar_tracking()"],
  });
  const subs = [
    ["FlotaApi", ["+ listar_vehiculos()", "+ listar_conductores()"], "fleet-management"],
    ["RutasApi", ["+ listar_rutas_activas()"], "route-optimization"],
    ["MantenimientoApi", ["+ contar_alertas_activas(vehiculo_id)"], "predictive-maintenance"],
    ["TrackingApi", ["+ estado_movimiento(vehiculo_id)"], "vehicle-tracking"],
  ].reduce((acc, [t, body, srv]) => { const y = acc.length ? acc[acc.length - 1].bottom + 28 : 30; acc.push(box(1230, y, 390, { title: t, stereo: `«Subsistema (Protocol)» ${srv}`, body })); return acc; }, []);
  const resultado = box(520, 480, 540, { title: "ResumenOperativo", stereo: "«Resultado (dominio)»", body: ["flota, rutas, mantenimiento, tracking", "llamadas_internas : int"] });
  b += cliente.svg + fachada.svg + resultado.svg + subs.map((s) => s.svg).join("");
  b += dep(cliente.right, 270, fachada.x, 270, "1 llamada");
  subs.forEach((s) => (b += dep(fachada.right, 300, s.x, s.y + 56, "")));
  b += dep(fachada.cx, fachada.bottom, fachada.cx, resultado.y, "devuelve", "right");
  b += note(40, 440, 400, ["La fachada usa los 4 subsistemas: detras hay", "4 microservicios y una consulta por vehiculo.", "El cliente no los conoce, la fachada los coordina."]).svg;
  return wrap(W, H, b);
}

// ----------------------------------------------------------------- FLYWEIGHT
function flyweight() {
  const W = 1650, H = 640; let b = "";
  const fabrica = box(560, 40, 560, {
    title: "FabricaTiposMantenimiento", stereo: "«Fabrica de pesos ligeros»",
    body: ["- _pool : dict[TipoAlerta, TipoMantenimiento]", "---", "+ obtener(tipo) : TipoMantenimiento", "+ cantidad_creada : int"],
  });
  const peso = box(1260, 30, 360, {
    title: "TipoMantenimiento", stereo: "«Peso ligero (estado intrinseco)»",
    body: ["{frozen: inmutable}", "tipo : TipoAlerta", "nombre : str", "descripcion : str", "recomendacion : str", "prioridad : str", "intervalo_km : float", "intervalo_horas : float"],
  });
  const alerta = box(40, 330, 400, {
    title: "Alerta", stereo: "«Contexto (estado extrinseco)»",
    body: ["vehiculo_id : UUID", "tipo : TipoAlerta", "kilometraje_km : float", "horas_motor : float", "generada_en : datetime"],
  });
  const cliente = box(40, 60, 360, { title: "AlertaResponse", stereo: "«Cliente»", body: ["+ desde_alerta(alerta)"] });
  b += fabrica.svg + peso.svg + alerta.svg + cliente.svg;
  b += diamondH(fabrica.right, peso.x, 130, false, "pool: uno por tipo", (fabrica.right + peso.x) / 2 + 12, 112);
  b += dep(cliente.right, 112, fabrica.x, 112, "obtener(tipo)");
  b += dep(cliente.cx, cliente.bottom, alerta.cx, alerta.y, "lee", "right");
  b += `<path d="M ${alerta.right} 420 H ${fabrica.cx} V ${fabrica.bottom + 6}" fill="none" stroke="${DEP}" stroke-width="1.7" stroke-dasharray="7,5"/>`;
  b += open(fabrica.cx, fabrica.bottom + 6, -Math.PI / 2);
  b += `<text x="${fabrica.cx + 12}" y="360" font-family="${FT}" font-style="italic" font-size="14" fill="${LABEL}">su tipo se pide a la fabrica</text>`;
  b += note(900, 400, 720, ["100 000 alertas  ->  solo 2 objetos TipoMantenimiento.", "Lo comun se comparte (intrinseco); lo propio de cada alerta", "(vehiculo, km, horas, fecha) se queda en la Alerta (extrinseco)."]).svg;
  return wrap(W, H, b);
}

// --------------------------------------------------------------------- PROXY
function proxy() {
  const W = 1650, H = 700; let b = "";
  const iface = box(520, 40, 520, { title: "EventPublisher", stereo: "«Interfaz del servicio (Protocol)»", body: ["+ publicar(routing_key, payload)"] });
  const cliente = box(1230, 48, 390, { title: "CrearVehiculo / ...", stereo: "«Cliente (casos de uso)»", body: ["+ ejecutar(...)"] });
  const proxyB = box(60, 300, 640, {
    title: "PublicadorEventosProxy", stereo: "«Proxy»",
    body: ["- _real : PublicadorReal", "- _pendientes : deque  (acotado)", "+ publicados / descartados : int", "---", "+ publicar(routing_key, payload)", "+ entregar_pendientes(forzar) : int", "- _asegurar_conexion(forzar) : bool", "+ esta_conectado : bool"],
  });
  const real = box(1000, 300, 600, {
    title: "RabbitMQPublisher", stereo: "«Sujeto Real» (broker remoto)",
    body: ["+ conectar() / desconectar()", "+ esta_conectado : bool", "+ publicar(routing_key, payload)"],
  });
  b += iface.svg + cliente.svg + proxyB.svg + real.svg;
  b += dep(cliente.x, 100, iface.right, 100, "usa");
  b += tree(iface.cx, iface.bottom, 255, 300, [proxyB.cx, real.cx], true);
  b += diamondH(proxyB.right, real.x, 400, false, "controla el acceso (_real)", (proxyB.right + real.x) / 2, 382);
  b += note(60, proxyB.bottom + 28, 800, ["El proxy se hace pasar por el publicador: los casos de uso no lo notan.", "Conexion tolerante, buzon de pendientes y entrega en orden al volver el broker."]).svg;
  return wrap(W, H, b);
}

(async () => {
  const diagramas = { facade, flyweight, proxy };
  for (const [n, f] of Object.entries(diagramas)) fs.writeFileSync(`${OUT}uml_${n}.svg`, f());
  const browser = await puppeteer.launch({ executablePath: "C:/Program Files/Google/Chrome/Application/chrome.exe", headless: "new" });
  const page = await browser.newPage();
  for (const n of Object.keys(diagramas)) {
    const svg = fs.readFileSync(`${OUT}uml_${n}.svg`, "utf8");
    const m = svg.match(/viewBox="0 0 (\d+) (\d+)"/);
    await page.setViewport({ width: +m[1], height: +m[2], deviceScaleFactor: 1.5 });
    await page.setContent(`<html><body style="margin:0;background:#fff">${svg}</body></html>`);
    await page.screenshot({ path: `${OUT}uml_${n}.png`, clip: { x: 0, y: 0, width: +m[1], height: +m[2] } });
  }
  await browser.close();
  console.log("OK");
})();
