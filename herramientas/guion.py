"""Comprueba un guion hablado (hablado.json) contra las reglas de los reels que funcionan: el gancho, el puente,
la longitud de cada molde, las fuentes de cada cifra, el cierre y la palabra del «comenta X».

Uso: herramientas/formula-guion <carpeta>/hablado.json
Imprime los avisos y sale con 1 si hay alguno. El formato del JSON está en .claude/skills/guion/SKILL.md.
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

PPS = 4.4  # palabras por segundo hablando a cámara con los silencios quitados (se mide con tu primer vídeo)

# molde: (segundos mínimos, segundos máximos, palabras máximas del gancho dicho, lleva imán)
MOLDES = {
    "capacidad": (38, 55, 17, True),
    "lista": (36, 58, 17, True),
    "caso": (50, 80, 26, True),
    "regalo": (14, 25, 14, False),
    "sistema": (40, 68, 12, False),
    "comparacion": (40, 55, 26, True),
    "personal": (30, 55, 22, False),  # tu historia o una decisión: cierra con «sígueme», sin «comenta X»
    # tu opinión tras el clip de otro (estilo clip de /edicion). Los segundos son solo los tuyos: el clip, de 10 a 18 s,
    # va delante. El gancho «dicho» es tu primera frase al entrar; el de «pantalla», el título sobre el clip
    "reaccion": (25, 45, 14, False),   # cierra con «sígueme»; «comenta X» solo si hay algo que mandar
}
PARTES = ["puente", "que-es", "hueco", "paso", "punto", "resultado", "por-que", "prueba", "conclusion", "iman", "cta"]
MAL_ARRANQUE = ("¿", "hola", "hoy ", "buenas", "en este v", "os ", "te voy a", "bueno", "vale", "hace tiempo")
# Por qué se para alguien a mirar. Cada gancho declara el suyo, y los tres que se le dan, uno distinto.
MOTIVOS = {
    "imposible": "algo que no sabías que ya se puede",
    "dinero": "dinero ganado, ahorrado o quemado",
    "gratis": "regalan algo que cuesta",
    "identidad": "una frase sobre ti que no se espera",
    "perdida": "te estás quedando atrás",
    "drama": "una pelea o un giro entre grandes",
    "secreto": "algo que casi nadie cuenta",
}
# Lo que no para a nadie: un dato técnico, una tarea para el que mira o el resumen de lo que viene.
SOSO = r"\bcuesta\b|\bprecio|\btokens?\b|\bíndice\b|\bbenchmark|\bversión\b|\bque probar\b|\btienes que\b|\bdeberías\b|\b(?:te|os) cuento\b|\bhablemos\b|\bvamos a ver\b"
# El gancho va rotundo: «nunca», no «casi nunca». Lo tibio no para a nadie
TIBIO = r"\bcasi\b|\bun poco\b|\bpuede que\b|\bquizás?\b|\bbastante\b|\ba veces\b|\bmás o menos\b|\bsuele\b"
# Lo que delata que lo ha escrito una IA. Tus expresiones de siempre no van aquí: van en marca/voz.md
DE_IA = (r"\bno es (?:solo |solamente )?[^.,;]{1,40}, (?:es|sino)\b|\by eso lo cambia todo\b|\bla clave (?:está|es)\b|"
         r"\ben definitiva\b|\bsin más dilación\b|\bseamos (?:sinceros|honestos)\b|\bdéjame (?:que te )?expli|"
         r"\bun antes y un después\b|\brevolucionari|\bliteralmente\b|\bimagina (?:que|por un momento)\b|"
         r"\by lo mejor de todo\b|\bpero aquí viene lo bueno\b|\bte lo explico\b")
sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import TRABAJO as CARPETAS, marca  # noqa: E402
FRASE_MAX = 20  # en los reels que funcionan, de 10 a 15 de media; hablando sin guion salen de 26 a 42
PUNTO_MAX = 44  # un punto de lista dura de 5 a 10 s


def palabras(texto: str) -> int:
    return len(texto.split())


def frases(texto: str) -> list[str]:
    return [f for f in re.split(r"(?<=[.!?…:])\s+", texto.strip()) if f]


def segundos(n: int) -> float:
    return n / PPS


def transcripcion(ruta: str) -> list[str]:
    """Las frases de `transcript.txt` (formula-estudiar): «[  3.2-  4.3] This tool is called…»."""
    texto = Path(ruta).expanduser().read_text()
    return [m.group(1).strip() for m in re.finditer(r"^\[\s*[\d.]+-\s*[\d.]+\]\s*(.+)$", texto, re.M)]


def avisos_copia(g: dict) -> list[str]:
    """Copia de un reel concreto: cada frase suya, traducida entera y en su sitio. Nada más."""
    ruta = g["copia"].get("transcripcion", "")
    if not ruta or not Path(ruta).expanduser().exists():
        return ["copia: falta copia.transcripcion (el transcript.txt del reel original)"]
    suyas = transcripcion(ruta)
    ganchos, tomas = g.get("ganchos", []), g.get("tomas", [])
    a: list[str] = []
    if len(ganchos) != 1:
        a.append(f"copia: va un solo gancho, el suyo traducido (hay {len(ganchos)})")
    piezas = ganchos[:1] + tomas
    norm = lambda s: re.sub(r"\W+", " ", s.lower()).strip()
    originales = [p.get("original", "").strip() for p in piezas]
    for i, o in enumerate(originales, 1):
        if not o:
            a.append(f"copia: la frase {i} no lleva «original» (la suya que traduce)")
    puestas = [norm(o) for o in originales if o]
    for f in suyas:
        if norm(f) not in puestas:
            a.append(f"copia: falta su frase «{f[:70]}»: va traducida, en su sitio")
    for o in originales:
        if o and norm(o) not in map(norm, suyas):
            a.append(f"copia: «{o[:70]}» no está en su transcripción: el original va tal cual")
    orden = [norm(f) for f in suyas]
    if [x for x in puestas if x in orden] != [x for x in orden if x in puestas]:
        a.append("copia: las frases no van en su orden")
    for i, (p, o) in enumerate(zip(piezas, originales), 1):
        dicho = p.get("dicho", p.get("texto", ""))
        if o and palabras(dicho) < 0.7 * palabras(o):
            a.append(f"copia: frase {i}, {palabras(dicho)} palabras y la suya {palabras(o)}: ¿resumida? Va entera")
        if o and palabras(dicho) > 1.6 * palabras(o) + 3:
            a.append(f"copia: frase {i}, {palabras(dicho)} palabras y la suya {palabras(o)}: ¿añadido algo?")
    palabra = g.get("cta", {}).get("palabra", "")
    if palabra and not any(palabra.lower() in t.get("texto", "").lower() for t in tomas[-2:]):
        a.append(f"el cierre tiene que decir «{palabra}», donde él dice la suya")
    if palabra and palabra.lower() not in g.get("pie", "").lower():
        a.append(f"el pie no dice «comenta {palabra}»")
    fichero = g.get("cta", {}).get("fichero")
    if palabra and not fichero:   # el fichero se escribe al aprobar el vídeo (/subida, «Lo que mandas»)
        a.append("falta cta.fichero: dónde irá lo que se manda")
    todo = " ".join(p.get("dicho", p.get("texto", "")) + " " + p.get("pantalla", "") + " " + p.get("titular", "") for p in piezas)
    if "—" in todo or "–" in todo:
        a.append("hay una raya larga: fuera")
    return a


def avisos(g: dict) -> list[str]:
    if g.get("copia"):
        return avisos_copia(g)
    a: list[str] = []
    molde = g.get("molde")
    if molde not in MOLDES:
        return [f"molde «{molde}»: tiene que ser uno de {', '.join(MOLDES)}"]
    minimo, maximo, gancho_max, con_iman = MOLDES[molde]

    ganchos = g.get("ganchos", [])
    if len(ganchos) < 3:
        a.append(f"hay {len(ganchos)} ganchos: se le dan tres para elegir")
    for i, h in enumerate(ganchos, 1):
        dicho, pantalla = h.get("dicho", ""), h.get("pantalla", "")
        if palabras(dicho) > gancho_max:
            a.append(f"gancho {i}: {palabras(dicho)} palabras dichas; en «{molde}» caben {gancho_max} ({segundos(gancho_max):.1f} s)")
        if h.get("para") not in MOTIVOS:
            a.append(f"gancho {i}: falta su motivo para pararse («para»): {', '.join(MOTIVOS)}")
        soso = re.search(SOSO, dicho.lower())
        if soso:
            a.append(f"gancho {i}: «{soso.group(0).strip()}» es un dato técnico o un deber. El gancho da una razón para pararse; eso va dentro")
        tibio = re.search(TIBIO, dicho.lower())
        if tibio:
            a.append(f"gancho {i}: «{tibio.group(0)}» lo deja tibio. Va rotundo, aunque no sea exacto: «nunca», no «casi nunca»")
        # La frase 2 sale de lo que dice la 1: cada gancho trae la suya
        if molde != "lista" and len(ganchos) > 1 and not h.get("puente"):
            a.append(f"gancho {i}: sin su «puente». La frase 2 sale de lo que dice este gancho: cada uno trae la suya")
        elif h.get("puente") and palabras(h["puente"]) > 10:
            a.append(f"gancho {i}: su puente tiene {palabras(h['puente'])} palabras; son de 5 a 9")
        if dicho.lower().startswith(MAL_ARRANQUE):
            a.append(f"gancho {i}: empieza por «{dicho.split()[0]}». Arranca con lo que importa: la marca, «Estas son…», «Uso…»")
        if pantalla.count("|") != 1:
            a.append(f"gancho {i}: lo de pantalla va en dos líneas separadas por «|»")
        if palabras(pantalla.replace("|", " ")) > 8:
            a.append(f"gancho {i}: {palabras(pantalla.replace('|', ' '))} palabras en pantalla; son de 3 a 6, sin emoji")
        if pantalla.replace("|", " ").strip().lower().rstrip(" .") == dicho.strip().lower().rstrip(" ."):
            a.append(f"gancho {i}: la pantalla repite lo que dice. La pantalla promete y la voz cuenta el hecho")

    motivos = [h.get("para") for h in ganchos if h.get("para") in MOTIVOS]
    if len(motivos) >= 2 and len(set(motivos)) < len(motivos):
        a.append("dos ganchos con el mismo motivo: cada uno engancha por algo distinto")

    tomas = g.get("tomas", [])
    partes = [t.get("parte") for t in tomas]
    for i, t in enumerate(tomas, 1):
        if t.get("parte") not in PARTES:
            a.append(f"toma {i}: parte «{t.get('parte')}»; vale {', '.join(PARTES)}")
        for f in frases(t.get("texto", "")):
            if palabras(f) > FRASE_MAX:
                a.append(f"toma {i}: una frase de {palabras(f)} palabras («{' '.join(f.split()[:6])}…»). Pártela: una idea, {FRASE_MAX} como mucho")
        titular = t.get("titular", "")
        if not titular:
            a.append(f"toma {i}: sin titular para el edit (de 2 a 5 palabras)")
        elif palabras(titular) > 5:
            a.append(f"toma {i}: el titular «{titular}» tiene {palabras(titular)} palabras; son de 2 a 5")
        elif titular.lower().rstrip(".") in t.get("texto", "").lower():
            a.append(f"toma {i}: el titular «{titular}» repite lo que dice; resume, no transcribe")
    if molde != "lista" and partes[:1] != ["puente"]:
        a.append("la segunda frase es el puente («Así se monta», «Te enseño cómo»): de 5 a 9 palabras")
    if partes[:1] == ["puente"] and ganchos and ganchos[0].get("puente") and tomas[0]["texto"] != ganchos[0]["puente"]:
        a.append("la frase 2 no es el puente del gancho 1: va la suya")
    if partes[:1] == ["puente"] and palabras(tomas[0]["texto"]) > 10:
        a.append(f"el puente tiene {palabras(tomas[0]['texto'])} palabras; son de 5 a 9")
    if molde == "lista":
        puntos = [t for t in tomas if t.get("parte") == "punto"]
        if not 3 <= len(puntos) <= 6:
            a.append(f"una lista lleva de 3 a 6 puntos, hay {len(puntos)}")
        for i, t in enumerate(puntos, 1):
            if palabras(t["texto"]) > PUNTO_MAX:
                a.append(f"punto {i}: {palabras(t['texto'])} palabras ({segundos(palabras(t['texto'])):.0f} s); cada punto dura de 5 a 10 s")

    cta = g.get("cta", {})
    palabra = cta.get("palabra", "")
    if molde == "personal" or (molde == "reaccion" and not palabra):
        if partes[-1:] != ["cta"] or "sígueme" not in tomas[-1]["texto"].lower():
            a.append(f"la última toma es el «sígueme»: {'la historia' if molde == 'personal' else 'esta opinión'} no manda nada")
    elif partes[-1:] != ["cta"]:
        a.append("la última toma es el «comenta X»")
    elif not palabra or palabra.lower() not in tomas[-1]["texto"].lower() or "comenta" not in tomas[-1]["texto"].lower():
        a.append(f"la última toma tiene que decir «comenta {palabra or 'X'}»")
    elif palabras(tomas[-1]["texto"]) > 14:
        a.append(f"el «comenta X» tiene {palabras(tomas[-1]['texto'])} palabras; son los últimos 2 s")
    # Todo vídeo cierra la idea: una conclusión o algo que hacer, justo antes de lo que mandas o del «sígueme»
    if "conclusion" not in partes:
        a.append("falta la toma «conclusion»: la idea o el accionable que se lleva el que mira, justo antes de lo que mandas o del «sígueme»")
    elif len(partes) - 1 - partes[::-1].index("conclusion") != len(partes) - (3 if "iman" in partes else 2):
        a.append("la «conclusion» va justo antes del imán (o del «sígueme» si no se manda nada)")
    if con_iman and "iman" not in partes:
        a.append("falta la toma «iman»: qué has hecho para mandar, con lo que lleva dentro")
    if con_iman and "iman" in partes and partes.index("iman") != len(partes) - 2:
        a.append("el imán va justo antes del «comenta X»")
    fichero = cta.get("fichero")
    if palabra and not fichero:
        a.append("falta cta.fichero: dónde irá lo que se manda")
    pie = g.get("pie", "")
    if palabra and palabra.lower() not in pie.lower():
        a.append(f"el pie no dice «comenta {palabra}»")

    todo = " ".join([h.get("dicho", "") + " " + h.get("pantalla", "") for h in ganchos] + [t.get("texto", "") + " " + t.get("titular", "") for t in tomas] + [pie])
    if "—" in todo or "–" in todo:
        a.append("hay una raya larga: fuera")
    dicho = " ".join(t.get("texto", "") for t in tomas) + " " + " ".join(h.get("dicho", "") for h in ganchos)
    if re.search(r"\d|gratis|gratuit", dicho) and not g.get("fuentes"):
        a.append("hay cifras o un «gratis» y ninguna fuente apuntada: se comprueba antes de escribirlo")
    # Cada cifra dicha, en una fuente; y «gratis» solo si eso mismo funciona sin pagar
    fuentes = " ".join(g.get("fuentes", [])).lower()
    if g.get("fuentes"):
        for n in sorted(set(re.findall(r"\d+(?:[.,]\d+)*", dicho))):
            if n not in fuentes and n.replace(".", "") not in fuentes.replace(".", ""):
                a.append(f"la cifra «{n}» no está en ninguna fuente: se comprueba y se apunta, o fuera")
        if re.search(r"gratis|gratuit", dicho.lower()) and not re.search(r"gratis|gratuit|free|0 ?€|0 ?\$", fuentes):
            a.append("dice «gratis» y ninguna fuente lo dice: solo si eso mismo funciona sin plan de pago ni clave")
    for prohibida in marca().get("palabras_prohibidas", []):
        if prohibida.lower() in todo.lower():
            a.append(f"«{prohibida}» está en tus palabras prohibidas (marca/marca.json)")
    for i, h in enumerate(ganchos, 1):
        if m := re.search(DE_IA, h.get("dicho", "").lower()):
            a.append(f"gancho {i}: «{m.group(0)}» suena a IA. Dilo directo")
    for i, t in enumerate(tomas, 1):
        if m := re.search(DE_IA, t.get("texto", "").lower()):
            a.append(f"toma {i}: «{m.group(0)}» suena a IA. Dilo directo")
    # La palabra del «comenta X» no se repite nunca: los reels viejos siguen recibiendo comentarios y la respuesta
    # automática mandaría el fichero que no es
    if palabra:
        mia = Path(g.get("_ruta", "")).resolve().parent
        for otro in CARPETAS.glob("*/hablado.json"):
            if otro.resolve().parent == mia:
                continue
            try:
                usada = json.loads(otro.read_text()).get("cta", {}).get("palabra", "")
            except (json.JSONDecodeError, OSError):
                continue
            # Sin tildes y una dentro de otra: EDICIÓN y edicion, o MODELO y MODELOS, se confunden igual
            sin = lambda s: "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")
            if usada and (sin(usada) in sin(palabra) or sin(palabra) in sin(usada)):
                a.append(f"«comenta {palabra}» choca con «{usada}», usada en {otro.parent.name}: otra palabra")

    total = palabras(ganchos[0]["dicho"]) + sum(palabras(t.get("texto", "")) for t in tomas) if ganchos else 0
    s = segundos(total)
    if s > maximo:
        a.append(f"dura {s:.0f} s ({total} palabras); un «{molde}» que funciona no pasa de {maximo}")
    if s < minimo:
        a.append(f"dura {s:.0f} s ({total} palabras); a un «{molde}» le faltan cosas por debajo de {minimo}")
    return a


def comprobar(ruta: Path) -> tuple[dict, list[str]]:
    g = json.loads(ruta.read_text())
    g["_ruta"] = str(ruta)   # para no repetir la palabra del «comenta X» de otro reel
    lista = avisos(g)
    g.pop("_ruta")
    if g.get("molde") in MOLDES and g.get("ganchos"):
        total = palabras(g["ganchos"][0]["dicho"]) + sum(palabras(t.get("texto", "")) for t in g.get("tomas", []))
        print(f"{g.get('nombre')} · {g['molde']} · {total} palabras · {segundos(total):.0f} s con el gancho 1")
    for i, p in enumerate(g.get("ganchos", [])[:1] + g.get("tomas", []), 1):
        if g.get("copia") and p.get("cambio"):
            print(f"  cambiado a propósito, frase {i}: {p['cambio']} (se dice al dar el guion)")
    print("Sin avisos." if not lista else f"{len(lista)} avisos:")
    for x in lista:
        print("  ·", x)
    return g, lista


def main() -> None:
    _, lista = comprobar(Path(sys.argv[1]).expanduser())
    sys.exit(1 if lista else 0)


if __name__ == "__main__":
    main()
