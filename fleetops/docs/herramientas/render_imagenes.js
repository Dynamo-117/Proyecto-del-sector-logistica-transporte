// Genera las imagenes de "codigo aplicado" (codigo con resaltado, ruta y numero de linea)
// y de "ejecucion" (salida de consola con formato de terminal) para los documentos.
//
// Uso:  NODE_PATH=<carpeta con node_modules> node render_imagenes.js
// Requiere: puppeteer-core, highlight.js y Google Chrome instalado.
//   FLEETOPS_OUT  carpeta de salida de las imagenes        (por defecto ./img/)
//   FLEETOPS_EV   carpeta con las salidas .txt de consola   (por defecto ./ev/)
const fs = require("fs");
const path = require("path");
const hljs = require("highlight.js");
const puppeteer = require("puppeteer-core");

const CHROME = "C:/Program Files/Google/Chrome/Application/chrome.exe";
const ROOT = path.resolve(__dirname, "../../") + "/"; // .../fleetops/fleetops/
const OUT = process.env.FLEETOPS_OUT || "./img/";
const EV = process.env.FLEETOPS_EV || "./ev/";
const hljsDir = path.dirname(require.resolve("highlight.js/package.json"));
const TEMA = fs.readFileSync(path.join(hljsDir, "styles/github-dark.css"), "utf8");
const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
fs.mkdirSync(OUT, { recursive: true });

const N = "services/navigation-integration-service/";
const F = "services/fleet-management-service/";
const R = "services/route-optimization-service/";
const G = "services/api-gateway/";
const M = "services/predictive-maintenance-service/";

// [id, archivo, desde, hasta]  (desde/hasta: numero de linea 1-based o regex; hasta puede ser "EOF")
const CODIGO = [
  // ---- patrones de las semanas 3 a 5
  ["singleton_01", F + "app/core/config.py", /^class Settings/, /PATRON GOF: SINGLETON -- termina/],
  ["singleton_02", F + "app/core/config.py", /^def get_settings/, "EOF"],
  ["fm_01", R + "app/infrastructure/db/repositorio_creador.py", 1, "EOF"],
  ["fm_02", R + "app/infrastructure/db/nodo_repository.py", /^class NodoRepositorioCreador/, "EOF"],
  ["fm_03", R + "app/api/dependencies.py", /^def get_nodo_repo/, /VehiculoDisponibleRepositorioCreador\(\)\.obtener/],
  ["af_01", F + "app/infrastructure/db/repositorio_factory.py", 1, "EOF"],
  ["af_02", F + "app/api/dependencies.py", /^def get_repositorio_factory/, /^ConductorRepo = /],
  ["builder_01", N + "app/domain/ruta_builder.py", 1, "EOF"],
  ["builder_02", N + "app/infrastructure/external/ruta_director.py", 1, "EOF"],
  ["builder_03", N + "app/infrastructure/external/osrm_client.py", /datos = respuesta\.json\(\)/, /construir_desde_respuesta_osrm/],
  // ---- semana 9: Facade
  ["facade_01", G + "app/application/ports/subsistemas.py", 1, "EOF"],
  ["facade_02", G + "app/application/facade/resumen_operativo_facade.py", /^class ResumenOperativoFacade/, /llamadas_internas=llamadas/],
  ["facade_03", G + "app/application/facade/resumen_operativo_facade.py", /def _armar_flota/, /PATRON GOF: FACADE -- termina/],
  ["facade_04", G + "app/api/routes/resumen_routes.py", 1, "EOF"],
  ["facade_05", G + "app/api/dependencies.py", /^def get_resumen_facade/, "EOF"],
  // ---- semana 10: Flyweight
  ["flyweight_01", M + "app/domain/tipos_mantenimiento.py", /^@dataclass\(frozen=True\)/, /PATRON GOF: FLYWEIGHT \(Peso ligero\) -- termina/],
  ["flyweight_02", M + "app/domain/tipos_mantenimiento.py", /^_CATALOGO/, "EOF"],
  ["flyweight_03", M + "app/api/schemas/alerta_schemas.py", /^class AlertaResponse/, /resuelta_en=alerta\.resuelta_en/],
  // ---- semana 10: Proxy
  ["proxy_01", F + "app/infrastructure/messaging/publicador_proxy.py", /^class PublicadorReal/, /self\.descartados = 0/],
  ["proxy_02", F + "app/infrastructure/messaging/publicador_proxy.py", /async def publicar/, /PATRON GOF: PROXY -- termina/],
  ["proxy_03", F + "app/infrastructure/messaging/rabbitmq_publisher.py", /^class RabbitMQPublisher/, "EOF"],
  ["proxy_04", F + "app/main.py", /^async def lifespan/, /await publisher\.desconectar/],
  ["proxy_05", F + "app/api/routes/evento_routes.py", /^router = /, "EOF"],
];

function recortar(lineas, desde, hasta) {
  const buscar = (c, ini) => {
    if (typeof c === "number") return c - 1;
    for (let i = ini; i < lineas.length; i++) if (c.test(lineas[i])) return i;
    throw new Error("no se encontro " + c);
  };
  const a = buscar(desde, 0);
  const b = hasta === "EOF" ? lineas.length - 1 : buscar(hasta, a);
  return [a, b];
}

function htmlCodigo(ruta, a, lineas) {
  const resaltado = hljs.highlight(lineas.join("\n"), { language: "python" }).value.split("\n");
  const filas = resaltado.map((l, i) => `<tr><td class="n">${a + 1 + i}</td><td class="c">${l || " "}</td></tr>`).join("");
  return `<html><head><meta charset="utf-8"><style>${TEMA}
    body{margin:0;background:#fff}
    .v{width:1100px;background:#0d1117;border:1px solid #30363d;border-radius:8px;overflow:hidden;font-family:Consolas,'Cascadia Mono',monospace}
    .b{background:#161b22;color:#c9d1d9;font:13px 'Segoe UI',sans-serif;padding:9px 16px;border-bottom:1px solid #30363d}
    .b span{color:#8b949e;float:right}
    table{border-collapse:collapse;width:100%}
    td{padding:0;font-size:15px;line-height:1.5;vertical-align:top}
    .n{color:#6e7681;text-align:right;padding:0 14px;width:1%;white-space:nowrap}
    .c{color:#e6edf3;white-space:pre;padding-right:16px}
    tbody tr:first-child td{padding-top:8px} tbody tr:last-child td{padding-bottom:10px}
  </style></head><body><div class="v" id="v"><div class="b">${esc(ruta)}<span>lineas ${a + 1}-${a + lineas.length}</span></div>
  <table><tbody>${filas}</tbody></table></div></body></html>`;
}

const SVC = (s) => "...\\fleetops\\services\\" + s;
// [id (archivo .txt en FLEETOPS_EV), carpeta, comando]
const TERMINALES = [
  ["builder", SVC("navigation-integration-service"), "python -m scripts.demo_builder"],
  ["facade", SVC("api-gateway"), "python -m scripts.demo_facade"],
  ["pytest_facade", SVC("api-gateway"), "python -m pytest tests/unit/test_resumen_facade.py tests/unit/test_subsistemas_http.py tests/integration/test_resumen_api.py -v"],
  ["flyweight", SVC("predictive-maintenance-service"), "python -m scripts.demo_flyweight"],
  ["pytest_flyweight", SVC("predictive-maintenance-service"), "python -m pytest tests/unit/test_tipos_flyweight.py tests/integration/test_alerta_tipo_info_api.py -v"],
  ["proxy", SVC("fleet-management-service"), "python -m scripts.demo_proxy"],
  ["pytest_proxy", SVC("fleet-management-service"), "python -m pytest tests/unit/test_publicador_proxy.py tests/integration/test_evento_api.py -v"],
];

function colorear(l) {
  l = esc(l);
  l = l.replace(/PASSED/g, '<span class="ok">PASSED</span>').replace(/(\d+ passed[^=]*)/g, '<span class="ok">$1</span>');
  l = l.replace(/^(RESULTADO:.*)$/, '<span class="ok">$1</span>').replace(/^(PATRON .*)$/, '<span class="t">$1</span>');
  l = l.replace(/\[(warning|info) *\]/g, '<span class="w">[$1]</span>').replace(/(TypeError|ValueError|FALLA|NO DISPONIBLE)/g, '<span class="w">$1</span>');
  return l;
}

(async () => {
  const browser = await puppeteer.launch({ executablePath: CHROME, headless: "new" });
  const page = await browser.newPage();
  await page.setViewport({ width: 1180, height: 800, deviceScaleFactor: 1.5 });

  for (const [id, archivo, desde, hasta] of CODIGO) {
    const lineas = fs.readFileSync(ROOT + archivo, "utf8").replace(/\r/g, "").split("\n");
    if (lineas[lineas.length - 1] === "") lineas.pop();
    const [a, b] = recortar(lineas, desde, hasta);
    await page.setContent(htmlCodigo("fleetops/" + archivo, a, lineas.slice(a, b + 1)));
    await (await page.$("#v")).screenshot({ path: `${OUT}code_${id}.png` });
  }

  await page.setViewport({ width: 1280, height: 800, deviceScaleFactor: 1.25 });
  for (const [id, carpeta, comando] of TERMINALES) {
    const salida = fs.readFileSync(`${EV}${id}.txt`, "utf8").replace(/\r/g, "").trimEnd();
    const cuerpo = salida.split("\n").map(colorear).join("\n");
    await page.setContent(`<html><head><meta charset="utf-8"><style>
      body{margin:0;background:#fff;font-family:Consolas,'Cascadia Mono',monospace}
      .v{width:1180px;background:#0c0c0c;border:1px solid #444}
      .b{background:#2b2b2b;color:#ddd;font:13px 'Segoe UI',sans-serif;padding:8px 14px;border-bottom:1px solid #444}
      pre{margin:0;padding:14px 18px;color:#ccc;font-size:14px;line-height:1.35;white-space:pre-wrap;word-break:break-word}
      .ok{color:#4ec46a}.w{color:#e5c07b}.t{color:#61afef;font-weight:bold}.p{color:#f5f5f5}
    </style></head><body><div class="v" id="v"><div class="b">Terminal — PowerShell</div>
    <pre><span class="p">PS ${esc(carpeta)}&gt;</span> <span class="p">${esc(comando)}</span>\n${cuerpo}\n\n<span class="p">PS ${esc(carpeta)}&gt;</span> </pre></div></body></html>`);
    await (await page.$("#v")).screenshot({ path: `${OUT}console_${id}.png` });
  }
  await browser.close();
  console.log("OK", CODIGO.length, TERMINALES.length);
})().catch((e) => { console.error(e); process.exit(1); });
