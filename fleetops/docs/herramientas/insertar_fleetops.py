"""Inserta las semanas 9 y 10 (Facade, Flyweight y Proxy) en FLEETOPS.docx, antes del
MANUAL DE USUARIO, y actualiza el manual (guia de uso, tabla de demos, tabla de pruebas).

Uso: python insertar_fleetops.py <FLEETOPS.docx de entrada> <fleetops_fragmento.json> <FLEETOPS.docx de salida>
El fragmento lo genera render_docs.js.
"""
import json
import re
import shutil
import sys
import zipfile

entrada, fragmento, salida = sys.argv[1:4]
frag = json.load(open(fragmento, encoding="utf8"))

RF = '<w:rFonts w:asciiTheme="majorHAnsi" w:hAnsiTheme="majorHAnsi" w:cstheme="majorHAnsi"/>'
COL = '<w:color w:val="000000" w:themeColor="text1"/>'


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def run(t, negrita=False):
    return (f'<w:r><w:rPr>{RF}{"<w:b/><w:bCs/>" if negrita else ""}{COL}<w:sz w:val="22"/><w:szCs w:val="22"/></w:rPr>'
            f'<w:t xml:space="preserve">{esc(t)}</w:t></w:r>')


def vineta(titulo, texto):
    return ('<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="7"/></w:numPr>'
            '<w:spacing w:after="90" w:line="280" w:lineRule="auto"/></w:pPr>' + run(titulo, True) + run(texto) + "</w:p>")


def subtitulo(t):
    return ('<w:p><w:pPr><w:keepNext/><w:spacing w:before="200" w:after="80"/></w:pPr><w:r><w:rPr>' + RF
            + '<w:b/><w:bCs/>' + COL + '<w:sz w:val="23"/><w:szCs w:val="23"/></w:rPr><w:t>' + esc(t) + "</w:t></w:r></w:p>")


def celda(ancho, texto, codigo=False):
    if codigo:
        rpr = ('<w:rFonts w:ascii="Consolas" w:eastAsia="Consolas" w:hAnsi="Consolas" w:cs="Consolas"/>'
               '<w:color w:val="7A2E00"/><w:sz w:val="17"/><w:szCs w:val="17"/>')
    else:
        rpr = RF + COL + '<w:sz w:val="19"/><w:szCs w:val="19"/>'
    return (f'<w:tc><w:tcPr><w:tcW w:w="{ancho}" w:type="dxa"/></w:tcPr><w:p><w:pPr><w:spacing w:after="0" w:line="260" w:lineRule="auto"/>'
            f'<w:jc w:val="left"/></w:pPr><w:r><w:rPr>{rpr}</w:rPr><w:t xml:space="preserve">{esc(texto)}</w:t></w:r></w:p></w:tc>')


def fila_demo(patron, carpeta, demo):
    return ('<w:tr><w:trPr><w:cantSplit/></w:trPr>' + celda(2300, patron) + celda(3400, carpeta)
            + celda(3660, ".\\.venv\\Scripts\\python.exe -m scripts." + demo, True) + "</w:tr>")


z = zipfile.ZipFile(entrada)
partes = {n: z.read(n) for n in z.namelist()}
x = partes["word/document.xml"].decode("utf8")

if "SEMANA 9" in x:
    sys.exit("FLEETOPS.docx ya contiene la semana 9; no se inserta dos veces")

# 1) semanas 9 y 10 antes del manual
i = x.index(">MANUAL DE USUARIO<")
ini = max(x.rfind("<w:p ", 0, i), x.rfind("<w:p>", 0, i))
x = x[:ini] + frag["xml"] + x[ini:]

# 2) guia rapida: pantalla nueva y funciones de las semanas 9 y 10
assert x.count("el menú da acceso a las 7 pantallas") == 1
x = x.replace("el menú da acceso a las 7 pantallas", "el menú da acceso a las 8 pantallas")
i = x.index(">Probar los roles<")
ini = max(x.rfind("<w:p ", 0, i), x.rfind("<w:p>", 0, i))
nuevo = (subtitulo("Funciones agregadas en las semanas 9 y 10")
         + vineta("Resumen (Facade)", ": es la primera pantalla del menú. Con una sola llamada muestra la flota (vehículos por estado y conductores), las rutas activas, las alertas de mantenimiento y los vehículos en movimiento; abajo indica cuántas consultas internas hizo. Si detiene un servicio (por ejemplo route-optimization) y pulsa «Actualizar», solo esa sección queda marcada como no disponible.")
         + vineta("Mantenimiento → Alertas (Flyweight)", ": cada alerta ahora muestra el nombre de su tipo, la prioridad, el intervalo (cada X km) y la recomendación para el taller. Esa información sale de un objeto compartido por todas las alertas del mismo tipo.")
         + vineta("Vehículos → estado de la mensajería (Proxy)", ": sobre la tabla aparece si RabbitMQ está conectado y cuántos eventos esperan. Si RabbitMQ no está disponible, el sistema sigue funcionando (puede crear vehículos); los eventos quedan pendientes y se entregan en orden al pulsar «Reintentar entrega» o automáticamente cuando el broker vuelve."))
x = x[:ini] + nuevo + x[ini:]

# 3) tabla de demostraciones: 3 filas nuevas
i = x.index("Cada patrón aplicado tiene un script")
t1 = x.index("</w:tbl>", i)
filas = (fila_demo("Facade", "services\\api-gateway", "demo_facade")
         + fila_demo("Flyweight", "services\\predictive-maintenance-service", "demo_flyweight")
         + fila_demo("Proxy", "services\\fleet-management-service", "demo_proxy"))
x = x[:t1] + filas + x[t1:]

# 4) tabla de pruebas esperadas
i = x.index("Pruebas esperadas")
t1 = x.index("</w:tbl>", i)
tabla = x[i:t1]
for viejo, nuevo_t in (("70 passed", "82 passed"), ("24 passed", "34 passed"), ("30 passed", "50 passed"), ("243 passed", "285 passed")):
    assert tabla.count(f">{viejo}<") == 1, viejo
    tabla = tabla.replace(f">{viejo}<", f">{nuevo_t}<")
x = x[:i] + tabla + x[t1:]

partes["word/document.xml"] = x.encode("utf8")

# 5) imagenes: archivos, relaciones y tipo de contenido
rels = partes["word/_rels/document.xml.rels"].decode("utf8")
nuevas = ""
for im in frag["imgs"]:
    partes["word/media/" + im["media"]] = open(im["src"], "rb").read()
    nuevas += (f'<Relationship Id="{im["rid"]}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" '
               f'Target="media/{im["media"]}"/>')
partes["word/_rels/document.xml.rels"] = rels.replace("</Relationships>", nuevas + "</Relationships>").encode("utf8")
ct = partes["[Content_Types].xml"].decode("utf8")
if 'Extension="png"' not in ct:
    ct = ct.replace("<Default ", '<Default Extension="png" ContentType="image/png"/><Default ', 1)
partes["[Content_Types].xml"] = ct.encode("utf8")

with zipfile.ZipFile(salida, "w", zipfile.ZIP_DEFLATED) as out:
    # [Content_Types].xml primero, como pide el formato
    for n in ["[Content_Types].xml"] + [n for n in partes if n != "[Content_Types].xml"]:
        out.writestr(n, partes[n])
print("OK", salida, len(frag["imgs"]), "imagenes")
