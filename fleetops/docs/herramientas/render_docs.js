// Genera los documentos Word de patrones a partir de contenido_patrones.js:
//   - un .docx por patron nuevo (facade, flyweight, proxy)
//   - UML_Patrones.docx y Evidencias_Patrones.docx (todos los patrones)
//   - fleetops_fragmento.json: XML de las semanas 9 y 10 para insertar en FLEETOPS.docx
//     (lo usa insertar_fleetops.py)
//
// Uso: NODE_PATH=<carpeta con node_modules> node render_docs.js <carpeta de salida>
// Requiere: docx (npm). Las imagenes se buscan en docs/evidencias/semanas_9_10, semanas_7_8 y docs/evidencias.
const fs = require("fs");
const path = require("path");
const D = require("docx");
const { PREVIOS, NUEVOS78, NUEVOS910 } = require("./contenido_patrones.js");

const OUT = path.resolve(process.argv[2] || "./salida_docs");
fs.mkdirSync(OUT, { recursive: true });
const EVID = path.resolve(__dirname, "../evidencias") + path.sep;
const DIRS = [EVID + "semanas_9_10" + path.sep, EVID + "semanas_7_8" + path.sep, EVID];
const ALIAS = {
  "console_singleton.png": "01_singleton_consola.png",
  "console_factory_method.png": "02_factory_method_consola.png",
  "console_pytest_fm.png": "03_factory_method_pruebas.png",
  "fe_fm_nodos.png": "04_factory_method_frontend_nodos.png",
  "fe_fm_rutas.png": "05_factory_method_frontend_rutas_activas.png",
  "console_abstract_factory.png": "06_abstract_factory_consola.png",
  "console_pytest_af.png": "07_abstract_factory_pruebas.png",
  "fe_af_login.png": "08_abstract_factory_frontend_login.png",
  "fe_af_vehiculos.png": "09_abstract_factory_frontend_vehiculos.png",
  "fe_af_conductores.png": "10_abstract_factory_frontend_conductores.png",
  "console_pytest_builder.png": "12_builder_pruebas.png",
};
function imgPath(name) {
  const dirs = process.env.FLEETOPS_IMG ? [process.env.FLEETOPS_IMG + path.sep, ...DIRS] : DIRS;
  for (const d of dirs) if (fs.existsSync(d + name)) return d + name;
  const a = ALIAS[name];
  if (a) for (const d of dirs) if (fs.existsSync(d + a)) return d + a;
  throw new Error("imagen no encontrada: " + name);
}
const dimsCache = {};
function dims(name) {
  const p = imgPath(name);
  if (!dimsCache[p]) {
    const b = fs.readFileSync(p);
    dimsCache[p] = { p, w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
  }
  return dimsCache[p];
}
// tamano en EMU: ancho solicitado (pulgadas), limitado en alto
function tam(name, anchoIn, maxAnchoIn, maxAltoIn) {
  const d = dims(name);
  let w = Math.min(anchoIn || maxAnchoIn, maxAnchoIn);
  let h = (w * d.h) / d.w;
  if (h > maxAltoIn) { w = (maxAltoIn * d.w) / d.h; h = maxAltoIn; }
  return { w: Math.round(w * 914400), h: Math.round(h * 914400), path: d.p };
}

const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const ESTR = { Creacional: "creacional", Estructural: "estructural" };

// ------------------------------------------------------------------ bloques (representacion intermedia)
function bloquesCodigo(p) {
  const b = [];
  for (const c of p.codigo) { b.push({ k: "sub", t: c.t }, { k: "img", n: c.img, w: c.ancho }, { k: "cap", t: c.pie }); }
  return b;
}
function bloquesEjecucion(p) {
  const b = [];
  for (const e of p.ejecucion) {
    if (e.t) b.push({ k: "sub", t: e.t });
    if (e.pasos) b.push({ k: "pk", t: "Pasos: " + e.pasos });
    if (e.cmd) b.push({ k: "pk", t: "Comando:" }, { k: "cmd", lines: e.cmd.split("\n") });
    b.push({ k: "img", n: e.img, w: e.ancho }, { k: "cap", t: e.pie });
  }
  return b;
}

// ------------------------------------------------------------------ renderizador docx-js
const FUENTE = { size: 22 };
const run = (t, o = {}) => new D.TextRun({ text: t, size: 22, ...o });
const H2 = (t) => new D.Paragraph({ heading: D.HeadingLevel.HEADING_2, keepNext: true, spacing: { before: 220, after: 100 }, children: [new D.TextRun({ text: t, bold: true, color: "2E75B6", size: 24 })] });
const H1 = (t, pb = true) => new D.Paragraph({ heading: D.HeadingLevel.HEADING_1, keepNext: true, pageBreakBefore: pb, border: { bottom: { style: D.BorderStyle.SINGLE, size: 6, color: "1F4E5F", space: 4 } }, spacing: { before: 280, after: 140 }, children: [new D.TextRun({ text: t, bold: true, color: "1F4E5F", size: 30 })] });
const P = (t, keep = false) => new D.Paragraph({ keepNext: keep, spacing: { after: 130, line: 290 }, children: [run(t)] });
const BUL = (t) => new D.Paragraph({ style: "ListParagraph", numbering: { reference: "bul", level: 0 }, spacing: { after: 80, line: 270 }, children: [run(t)] });

function tabla(cols, head, filas, tamFuente = 19) {
  const borde = { style: D.BorderStyle.SINGLE, size: 4, color: "BFBFBF" };
  const bordes = { top: borde, bottom: borde, left: borde, right: borde };
  const mar = { top: 60, bottom: 60, left: 100, right: 100 };
  const celda = (t, i, h) => new D.TableCell({
    width: { size: cols[i], type: D.WidthType.DXA }, borders: bordes, margins: mar,
    shading: h ? { fill: "1F4E5F", type: D.ShadingType.CLEAR, color: "auto" } : undefined,
    children: [new D.Paragraph({ children: [new D.TextRun({ text: t, size: tamFuente, bold: h, color: h ? "FFFFFF" : undefined })] })],
  });
  return new D.Table({
    width: { size: cols.reduce((a, b) => a + b, 0), type: D.WidthType.DXA }, columnWidths: cols,
    rows: [
      new D.TableRow({ tableHeader: true, children: head.map((t, i) => celda(t, i, true)) }),
      ...filas.map((f) => new D.TableRow({ cantSplit: true, children: f.map((t, i) => celda(t, i, false)) })),
    ],
  });
}

function render(bloques, maxAncho, maxAlto) {
  const out = [];
  for (const b of bloques) {
    if (b.k === "sub") out.push(new D.Paragraph({ keepNext: true, spacing: { before: 160, after: 70 }, children: [run(b.t, { bold: true })] }));
    else if (b.k === "pk") out.push(P(b.t, true));
    else if (b.k === "cmd") {
      out.push(new D.Paragraph({
        keepNext: true, keepLines: true, shading: { type: D.ShadingType.CLEAR, fill: "F2F2F2", color: "auto" },
        spacing: { after: 140, line: 250 }, indent: { left: 200, right: 100 },
        children: b.lines.map((l, i) => new D.TextRun({ text: l, font: "Consolas", size: 19, break: i ? 1 : 0 })),
      }));
    } else if (b.k === "img") {
      const t = tam(b.n, b.w, maxAncho, maxAlto);
      out.push(new D.Paragraph({
        keepNext: true, alignment: D.AlignmentType.CENTER, spacing: { before: 60, after: 100 },
        children: [new D.ImageRun({ type: "png", data: fs.readFileSync(t.path), transformation: { width: Math.round(t.w / 9525), height: Math.round(t.h / 9525) }, altText: { title: b.n, description: b.n, name: b.n } })],
      }));
    } else if (b.k === "cap") out.push(new D.Paragraph({ alignment: D.AlignmentType.CENTER, spacing: { after: 200 }, children: [new D.TextRun({ text: b.t, italics: true, color: "666666", size: 19 })] }));
  }
  return out;
}

function documento(hijos, landscape = false) {
  return new D.Document({
    creator: "FleetOps",
    numbering: { config: [{ reference: "bul", levels: [{ level: 0, format: D.LevelFormat.BULLET, text: "●", alignment: D.AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] }] },
    sections: [{
      properties: {
        page: {
          size: { width: 12240, height: 15840, orientation: landscape ? D.PageOrientation.LANDSCAPE : D.PageOrientation.PORTRAIT },
          margin: landscape ? { top: 864, right: 1080, bottom: 864, left: 1080 } : { top: 1080, right: 1080, bottom: 1080, left: 1080 },
        },
      },
      children: hijos,
    }],
  });
}
const titulo = (t, sub) => [
  new D.Paragraph({ alignment: D.AlignmentType.CENTER, spacing: { after: 40 }, children: [new D.TextRun({ text: t, bold: true, color: "1F4E5F", size: 40 })] }),
  new D.Paragraph({ alignment: D.AlignmentType.CENTER, spacing: { after: 260 }, children: [new D.TextRun({ text: sub, italics: true, color: "666666", size: 22 })] }),
];
const guardar = async (doc, nombre) => fs.writeFileSync(path.join(OUT, nombre), await D.Packer.toBuffer(doc));

// ------------------------------------------------------------------ documento de un patron
function docPatron(p) {
  const h = [...titulo(p.nombre, `Semana ${p.semana} · Patrón ${ESTR[p.categoria]} · ${p.servicio}`)];
  h.push(H2("1. Qué es"), ...p.queEs.map((t) => P(t)));
  h.push(H2("2. Por qué aquí"), ...p.porQue.map((t) => P(t)));
  h.push(H2("3. Diagrama UML"), ...render([{ k: "img", n: p.umlImg, w: 7.0 }, { k: "cap", t: p.umlPie }], 7.0, 4.6));
  h.push(...p.participantesTexto.map(BUL), new D.Paragraph({ spacing: { after: 120 }, children: [] }));
  h.push(tabla([2200, 3500, 4380], ["Rol GoF", "Clase", "Archivo"], p.participantes));
  h.push(H2("4. Código aplicado"), P("Código real del proyecto, con su ruta y número de línea. Los comentarios «PATRON GOF» marcan dónde inicia y termina cada participante."));
  h.push(...render(bloquesCodigo(p), 7.0, 8.2));
  h.push(H2("5. Ejecución y prueba de que funciona"), ...render(bloquesEjecucion(p), 7.0, 8.2));
  h.push(H2("6. De qué manera aporta al proyecto"), ...p.aporte.map(BUL));
  h.push(H2("7. Dónde está aplicado"), ...p.donde.map(BUL));
  return documento(h);
}

// ------------------------------------------------------------------ UML_Patrones.docx
const TODOS = [...PREVIOS, ...NUEVOS78, ...NUEVOS910];
function docUML() {
  const h = [...titulo("Diagramas UML de los patrones de diseño", "FleetOps — Fase 3 — patrones GoF aplicados hasta el momento")];
  h.push(P("Este documento reúne el diagrama UML de cada patrón GoF aplicado en FleetOps. Cada diagrama muestra los participantes reales del patrón (con los nombres exactos de las clases del código) y va acompañado de una tabla que indica en qué archivo vive cada participante."));
  h.push(H2("Patrones aplicados"));
  h.push(tabla([645, 2968, 2581, 1291, 6195], ["#", "Patrón", "Categoría GoF", "Semana", "Servicio donde se aplicó"], TODOS.map((p, i) => [String(i + 1), p.nombre, p.categoria, String(p.semana), p.servicio])));
  h.push(new D.Paragraph({ spacing: { after: 120 }, children: [] }), H2("Notación utilizada"));
  [
    "Rectángulo de tres compartimentos: nombre de la clase (con su estereotipo entre « »), atributos y métodos. Las clases abstractas van en cursiva.",
    "Flecha continua con triángulo hueco: generalización (herencia) — apunta a la clase padre.",
    "Flecha punteada con triángulo hueco: realización — la clase implementa la interfaz a la que apunta.",
    "Flecha punteada con punta abierta: dependencia («usa», «crea», «delega en»).",
    "Línea con rombo hueco: agregación (el rombo está en el lado que contiene al otro). Rombo relleno: composición.",
    "Nota con esquina doblada: aclaración sobre el diseño. Visibilidad: + público, − privado, # protegido.",
  ].forEach((t) => h.push(BUL(t)));
  TODOS.forEach((p, i) => {
    h.push(H1(`${i + 1}. ${p.nombre}`), P(p.resumenUml));
    h.push(...render([{ k: "img", n: p.umlImg, w: 9.4 }, { k: "cap", t: `Figura ${i + 1}. ${p.umlPie}` }], 9.4, 3.6));
    h.push(tabla([3016, 5757, 4907], ["Rol GoF", "Clase", "Archivo"], p.participantes));
  });
  return documento(h, true);
}

// ------------------------------------------------------------------ Evidencias_Patrones.docx
const RESUMEN_EV = {
  singleton: ["demo_singleton.py", "—", "No aplica (sin manifestación visual)"],
  fm: ["demo_factory_method", "7", "Pantalla Rutas"],
  af: ["demo_abstract_factory", "5", "Login, Vehículos, Conductores"],
  builder: ["demo_builder (OSRM real)", "11", "Navegación"],
  adapter: ["demo_adapter (OSRM y Valhalla reales)", "10", "Navegación (selector de proveedor)"],
  bridge: ["demo_bridge", "17", "Panel «Reportes» (Vehículos y Conductores)"],
  composite: ["demo_composite", "17", "Rutas: plan de ruta con paradas"],
  decorator: ["demo_decorator (OSRM real)", "11", "Navegación (tiempo de respuesta)"],
  facade: ["demo_facade", "20", "Resumen (una sola llamada) y servicio caído"],
  flyweight: ["demo_flyweight (memoria medida)", "10", "Mantenimiento (alertas con su tipo)"],
  proxy: ["demo_proxy (broker simulado)", "12", "Vehículos (estado de la mensajería)"],
};
const CARPETA = { singleton: "raíz del repositorio" };
function comandoDemo(p) {
  if (p.id === "singleton") return "python scripts/demo_singleton.py";
  const demo = { fm: "demo_factory_method", af: "demo_abstract_factory" }[p.id] || "demo_" + p.id;
  return `.\\.venv\\Scripts\\python.exe -m scripts.${demo}`;
}
function docEvidencias() {
  const h = [...titulo("Evidencias de aplicación de los patrones", "Código aplicado y resultados de su ejecución (consola y frontend) — FleetOps")];
  h.push(P("Este documento reúne, para cada patrón, las evidencias que pide el profesor: capturas del código aplicado y capturas de su ejecución (salidas de consola, pruebas automatizadas y pantallas del frontend). Está organizado por patrón y cada bloque es independiente: puede copiarse y pegarse tal cual en el documento general."));
  h.push(H2("Cómo se generó cada evidencia"));
  [
    "Código aplicado: imágenes del código real del proyecto con su ruta y número de línea.",
    "Consola: scripts de demostración incluidos en el repositorio (uno por patrón); las imágenes muestran la salida real de esos comandos.",
    "Pruebas: salida real de pytest -v de las pruebas propias de cada patrón (todas en verde).",
    "Frontend: capturas reales de la aplicación (http://localhost:5173) con el usuario admin@fleetops.com, con el sistema completo levantado.",
  ].forEach((t) => h.push(BUL(t)));
  h.push(H2("Resumen de evidencias por patrón"));
  h.push(tabla([1664, 2055, 2740, 881, 2740], ["Patrón", "Servicio", "Consola", "Pruebas", "Frontend"],
    TODOS.map((p) => [p.nombre, p.id === "singleton" ? "los 6 servicios" : p.servicio.replace("-service", ""), ...RESUMEN_EV[p.id]])));
  TODOS.forEach((p, i) => {
    h.push(H1(`${i + 1}. ${p.nombre}`), H2("Qué se demuestra"), P(p.demuestra));
    h.push(H2("Evidencia A — Código aplicado"), ...render(bloquesCodigo(p), 7.0, 8.2));
    h.push(H2("Evidencia B — Ejecución y prueba de que funciona"), ...render(bloquesEjecucion(p), 7.0, 8.2));
    h.push(H2("Texto sugerido para el informe"), P(p.informe));
  });
  h.push(H1(`${TODOS.length + 1}. Anexo — Cómo repetir las evidencias`));
  h.push(P("Requisitos: haber seguido el Manual de usuario (instalación) y tener el sistema levantado para las capturas del frontend. Las evidencias de consola y de pruebas no necesitan que los servicios estén corriendo (las de Builder, Adapter y Decorator necesitan internet)."));
  h.push(tabla([2200, 3400, 4480], ["Patrón", "Carpeta", "Comando de demostración"],
    TODOS.map((p) => [p.nombre, CARPETA[p.id] || "services\\" + p.servicio, comandoDemo(p)])));
  return documento(h);
}

// ------------------------------------------------------------------ fragmento XML para FLEETOPS.docx
const RF = '<w:rFonts w:asciiTheme="majorHAnsi" w:hAnsiTheme="majorHAnsi" w:cstheme="majorHAnsi"/>';
const COL = '<w:color w:val="000000" w:themeColor="text1"/>';
const imgs = [];
let docPr = 20500;
function xmlP(ppr, rpr, t) { return `<w:p><w:pPr>${ppr}</w:pPr><w:r><w:rPr>${rpr}</w:rPr><w:t xml:space="preserve">${esc(t)}</w:t></w:r></w:p>`; }
function xmlImg(b) {
  const t = tam(b.n, b.w, 6.5, 8.0);
  const id = ++docPr;
  const rid = "rIdFO" + String(imgs.length + 1).padStart(3, "0");
  imgs.push({ rid, src: t.path, media: `fleetops_s910_${String(imgs.length + 1).padStart(3, "0")}.png` });
  return `<w:p><w:pPr><w:keepNext/><w:spacing w:before="60" w:after="60"/><w:jc w:val="center"/></w:pPr><w:r><w:rPr><w:noProof/></w:rPr><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="${t.w}" cy="${t.h}"/><wp:effectExtent l="0" t="0" r="0" b="0"/><wp:docPr id="${id}" name="Imagen ${id}" descr="${esc(b.n)}"/><wp:cNvGraphicFramePr><a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" noChangeAspect="1"/></wp:cNvGraphicFramePr><a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:nvPicPr><pic:cNvPr id="0" name=""/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill><a:blip r:embed="${rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="${t.w}" cy="${t.h}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>`;
}
const xH2 = (t) => xmlP('<w:pStyle w:val="Ttulo2"/><w:keepNext/><w:spacing w:before="320" w:after="140"/>', RF + COL, t);
const xP = (t, keep) => xmlP(`${keep ? "<w:keepNext/>" : ""}<w:spacing w:after="140" w:line="300" w:lineRule="auto"/>`, RF + COL + '<w:sz w:val="22"/>', t);
const xBul = (t) => xmlP('<w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="7"/></w:numPr><w:spacing w:after="90" w:line="280" w:lineRule="auto"/>', RF + COL + '<w:sz w:val="22"/><w:szCs w:val="22"/>', t);
function xBloques(bl) {
  return bl.map((b) => {
    if (b.k === "sub") return xmlP('<w:keepNext/><w:spacing w:before="200" w:after="80"/>', RF + '<w:b/><w:bCs/>' + COL + '<w:sz w:val="23"/><w:szCs w:val="23"/>', b.t);
    if (b.k === "pk") return xP(b.t, true);
    if (b.k === "cmd") {
      return b.lines.map((l, i) => xmlP(`<w:keepNext/><w:keepLines/><w:shd w:val="clear" w:color="auto" w:fill="F2F2F2"/><w:spacing w:after="${i === b.lines.length - 1 ? 140 : 0}" w:line="245" w:lineRule="auto"/><w:ind w:left="200" w:right="100"/><w:jc w:val="left"/>`,
        '<w:rFonts w:ascii="Consolas" w:eastAsia="Consolas" w:hAnsi="Consolas" w:cs="Consolas"/>' + COL + '<w:sz w:val="18"/><w:szCs w:val="18"/>', l)).join("");
    }
    if (b.k === "img") return xmlImg(b);
    return xmlP('<w:spacing w:after="200"/><w:jc w:val="center"/>', RF + '<w:i/><w:iCs/><w:color w:val="666666"/><w:sz w:val="19"/><w:szCs w:val="19"/>', b.t);
  }).join("");
}
function xPatron(p, primero) {
  const t1 = `<w:p><w:pPr><w:pStyle w:val="Ttulo1"/>${primero ? "" : "<w:pageBreakBefore/>"}<w:spacing w:before="200" w:after="200"/><w:rPr><w:rFonts w:cstheme="majorHAnsi"/><w:b/><w:bCs/><w:color w:val="auto"/></w:rPr></w:pPr><w:r><w:rPr><w:rFonts w:cstheme="majorHAnsi"/><w:b/><w:bCs/><w:color w:val="auto"/></w:rPr><w:t>${esc(p.nombre)}</w:t></w:r></w:p>`;
  return t1 + xH2("1. Qué es") + p.queEs.map((t) => xP(t)).join("")
    + xH2("2. Por qué aquí") + p.porQue.map((t) => xP(t)).join("")
    + xH2("3. Diagrama UML") + xBloques([{ k: "img", n: p.umlImg, w: 6.5 }, { k: "cap", t: p.umlPie }]) + p.participantesTexto.map(xBul).join("")
    + xH2("4. Código aplicado") + xBloques(bloquesCodigo(p))
    + xH2("5. Ejecución") + xBloques(bloquesEjecucion(p))
    + xH2("6. De qué manera aporta al proyecto") + p.aporte.map(xBul).join("");
}
function xSemana(n, titulo, pats) {
  const cab = `<w:p><w:pPr><w:pageBreakBefore/><w:jc w:val="center"/></w:pPr><w:r><w:rPr>${RF}<w:b/><w:bCs/><w:i/><w:iCs/><w:szCs w:val="24"/></w:rPr><w:t>SEMANA ${n}</w:t></w:r></w:p><w:p><w:pPr><w:jc w:val="left"/></w:pPr><w:r><w:rPr>${RF}<w:b/><w:bCs/><w:i/><w:iCs/><w:szCs w:val="24"/></w:rPr><w:t>${esc(titulo)}</w:t></w:r></w:p>`;
  return cab + pats.map((p, i) => xPatron(p, i === 0)).join("");
}

(async () => {
  const [facade, flyweight, proxy] = NUEVOS910;
  for (const p of NUEVOS910) await guardar(docPatron(p), p.id + ".docx");
  await guardar(docUML(), "UML_Patrones.docx");
  await guardar(docEvidencias(), "Evidencias_Patrones.docx");
  const xml = xSemana(9, "APLICACIÓN PATRÓN FACADE", [facade]) + xSemana(10, "APLICACIÓN PATRONES FLYWEIGHT Y PROXY", [flyweight, proxy]);
  fs.writeFileSync(path.join(OUT, "fleetops_fragmento.json"), JSON.stringify({ xml, imgs }));
  console.log("OK", fs.readdirSync(OUT).join(", "), "imagenes en FLEETOPS:", imgs.length);
})().catch((e) => { console.error(e); process.exit(1); });
