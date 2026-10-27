"""Un reel grabado en piezas: tres ganchos (A, B y C, cada uno con su frase 2), uno o dos cuerpos (1 y 2: lo mismo,
dicho con otras palabras y en otro orden) y un cierre para todos. De una grabación salen hasta seis vídeos
distintos: A1 es el reel normal y los demás, sus pruebas, una al día. Cinco copias del mismo vídeo con otro titular
no engañan a Instagram; seis vídeos de verdad, sí.

  formula preparar NOMBRE --piezas "A=0,B=31,C=58,1=90,cierre=301,2=340"
    cada número, la palabra de crudo.txt (lo que dijiste, sin quitar nada) en que empieza esa pieza.
    → la carpeta es A1 (base.mp4, palabras.json, frases.txt); cada otra combinación, en _combo-B1/…;
      piezas.txt, todas seguidas en el orden A, B, C, 1, 2, cierre, con los tiempos del guion.

El guion se escribe una vez, en guion-piezas.html, con los tiempos de piezas.txt y cada cosa que lleva
tiempo dentro de su pieza: <!-- pieza B --> … <!-- /pieza -->. construir saca de ahí el guion.html de cada
combinación (el de la carpeta, A1, también: no se toca a mano).

Con un solo cuerpo grabado, los otros salen de él, por frases enteras:
  formula preparar NOMBRE --piezas "…" --cuerpos "2=47-155,163-560;3=47-100,200-560"
    cada cuerpo nuevo, los tramos del cuerpo 1 que dice y en qué orden (el número de palabra de piezas.txt; uno
    solo, «57», es la frase que empieza ahí). Para recortarlo, deja fuera frases; para una lista, cambia el orden
    de los puntos. Su guion sale solo del de la pieza 1: cada bloque va con su tramo, y el de un tramo quitado, fuera.
"""
import json
import re
import subprocess

import corte
from config import FFMPEG, FFPROBE

PIEZAS = ("A", "B", "C", "1", "2", "3", "cierre")   # el orden de piezas.txt
GANCHOS, CUERPOS = ("A", "B", "C"), ("1", "2", "3")
FPS = 30
# Los «+0.5» son de su bloque: no se tocan. data-clase, data-clic, data-mueve y data-cascada llevan el segundo delante
# («9.2:on», «12.4,0.12»): sin moverlos, la lista no se marcaría ni el ratón pulsaría en las combinaciones
TIEMPO = re.compile(r'(data-(?:a|b|en|t|hasta|sale|clase|clic|mueve|cascada)=")(\d+(?:\.\d+)?)([":,])')
MARCA = re.compile(r"<!--\s*(/?)pieza\s*(\w*)\s*-->")


def leer(texto):
    """«A=0,B=31,1=90,cierre=301» → [(0, "A"), (31, "B"), …], en el orden en que las grabaste."""
    marcas = []
    for par in texto.split(","):
        etiqueta, _, n = par.strip().partition("=")
        if etiqueta not in PIEZAS or not n.isdigit():
            raise SystemExit(f'--piezas: «{par.strip()}». Va así: "A=0,B=31,C=58,1=90,cierre=301,2=340" '
                             f'(piezas: {", ".join(PIEZAS)}; el número, de crudo.txt)')
        marcas.append((int(n), etiqueta))
    etiquetas = [e for _, e in marcas]
    if len(set(etiquetas)) < len(etiquetas) or not {"A", "1"} <= set(etiquetas):
        raise SystemExit("--piezas: cada pieza una vez, y como poco el gancho A y el cuerpo 1")
    return sorted(marcas)


def leer_cuerpos(texto, grabadas):
    """«2=47-155,163-560;3=47-100» → {"2": [(47, 155), (163, 560)], …}. Un número solo es la frase que empieza ahí:
    se cierra en `tramos_de`, que tiene las palabras."""
    cuerpos = {}
    for parte in filter(None, (x.strip() for x in texto.split(";"))):
        etiqueta, _, tramos = parte.partition("=")
        if etiqueta not in CUERPOS[1:] or etiqueta in grabadas or etiqueta in cuerpos:
            raise SystemExit(f'--cuerpos: «{parte}». Cada cuerpo nuevo es el 2 o el 3, que no hayas grabado: '
                             '"2=47-155,163-560;3=47-100,200-560"')
        try:
            cuerpos[etiqueta] = [(int(a), int(b) if b else None) for a, _, b in (t.strip().partition("-")
                                                                                for t in tramos.split(","))]
        except ValueError:
            raise SystemExit(f'--cuerpos: «{parte}». Los tramos van «47-155» (esas palabras) o «57» (esa frase)')
    return cuerpos


def tramos_de(cuerpo, suyas, largo, video1):
    """Los segundos del cuerpo 1 (su vídeo, _piezas/1.mp4) de cada tramo pedido. Cada corte cae en el fotograma más
    callado del hueco entre dos palabras: tras quitar los silencios el hueco es de décimas, y a mitad se oiría el
    tijeretazo o se comería el final de una palabra."""
    import numpy as np
    pcm = subprocess.run([FFMPEG, "-v", "error", "-i", str(video1), "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
    ruido = lambda t: float((x[max(0, int((t - .015) * 16000)):int((t + .015) * 16000)] ** 2).mean() or 0)

    def corte_entre(antes, despues):   # Whisper llega a equivocarse en 0,25 s: se busca por dentro de las dos palabras
        lo, hi = max(antes["a"] + 0.03, antes["b"] - 0.12), min(despues["b"] - 0.03, despues["a"] + 0.25)
        candidatos = [k / FPS for k in range(int(lo * FPS), int(hi * FPS) + 2) if lo <= k / FPS <= hi]
        return min(candidatos, key=ruido) if candidatos else round((antes["b"] + despues["a"]) / 2 * FPS) / FPS

    tramos = []
    for a, b in cuerpo:
        # las muletillas ya no están: el tramo va de la primera palabra que queda a la última
        i = next((k for k, p in enumerate(suyas) if p["n"] >= a), None)
        if b is None and i is not None:   # la frase que empieza en `a`, hasta su punto
            b = next((p["n"] for p in suyas[i:] if re.search(r"[.?!…]$", p["t"])), suyas[-1]["n"])
        j = max((k for k, p in enumerate(suyas) if p["n"] <= (b or -1)), default=None)
        if i is None or j is None or j < i or not suyas[0]["n"] <= a <= suyas[-1]["n"]:
            raise SystemExit(f"--cuerpos: el tramo {a}-{b} no es del cuerpo 1 (sus palabras: de la "
                             f"{suyas[0]['n']} a la {suyas[-1]['n']}, en piezas.txt)")
        ini = 0.0 if i == 0 else corte_entre(suyas[i - 1], suyas[i])
        fin = largo if j == len(suyas) - 1 else corte_entre(suyas[j], suyas[j + 1])
        tramos.append((ini, fin))
    for (a1, b1), (a2, b2) in zip(sorted(tramos), sorted(tramos)[1:]):
        if a2 < b1 - 0.01:
            raise SystemExit("--cuerpos: dos tramos se pisan; cada frase, una vez")
    return tramos


def cuerpo_nuevo(video1, tramos, suyas, destino):
    """El cuerpo hecho de esos tramos del 1, en su orden, con 10 ms de fundido en cada borde para que no chasque.
    Devuelve sus palabras y su mapa: [(segundo del 1 en que empieza el tramo, en que acaba, en que empieza aquí)]."""
    mapa, palabras, t = [], [], 0.0
    for a, b in tramos:
        mapa.append((a, b, round(t, 3)))
        # Whisper pone el arranque de una palabra hasta 50 ms antes del corte: es del tramo que empieza
        palabras += [{**p, "a": p["a"] - a + t, "b": min(p["b"], b) - a + t} for p in suyas if a - 0.06 <= p["a"] < b - 0.06]
        t += b - a
    filtro = "".join(f"[0:v]trim={a:.4f}:{b:.4f},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={a:.4f}:{b:.4f},asetpts=PTS-STARTPTS,"
                     f"afade=t=in:d=0.01,afade=t=out:st={max(0.0, b - a - 0.01):.4f}:d=0.01[a{i}];"
                     for i, (a, b) in enumerate(tramos))
    filtro += "".join(f"[v{i}][a{i}]" for i in range(len(tramos))) + f"concat=n={len(tramos)}:v=1:a=1[v][a]"
    subprocess.run([FFMPEG, "-v", "error", "-y", "-i", str(video1), "-filter_complex", filtro, "-map", "[v]", "-map", "[a]",
                    "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", "-g", "30",
                    "-keyint_min", "30", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(destino)], check=True)
    return palabras, mapa


def trocear(palabras, marcas):
    """Las palabras de crudo de cada pieza: llega hasta donde empieza la siguiente que grabaste. Lo de antes de la
    primera (probar el sonido) no es de ninguna."""
    fines = [n for n, _ in marcas[1:]] + [len(palabras)]
    return {e: [{**p, "pieza": e} for p in palabras[ini:fin]] for (ini, e), fin in zip(marcas, fines)}


def combinaciones(etiquetas):
    """A1 primero (el reel normal) y detrás cada gancho con cada cuerpo: A1, B1, C1, A2, B2, C2."""
    return [g + c for c in CUERPOS if c in etiquetas for g in GANCHOS if g in etiquetas]


def orden_pruebas(combos, n):
    """La combinación de cada prueba: las que no son el reel normal y, si faltan, otra vuelta entera.
    Tres ganchos y tres cuerpos (dos de ellos, recortes del 1), en diagonal para que ninguna repita gancho y cuerpo:
    B1, C2, A3, B2, C3. Tres ganchos y dos cuerpos: B1, C1, A2, B2, C2. Con uno: B1, C1, A1, B1, C1; sin piezas, A1."""
    ganchos = [g for g in GANCHOS if any(c[0] == g for c in combos)]
    cuerpos = [c for c in CUERPOS if any(x[1:] == c for x in combos)]
    if len(ganchos) == 3 and len(cuerpos) == 3:
        diagonal = [ganchos[(k + 1) % 3] + cuerpos[(k + k // 3) % 3] for k in range(9)]
        diagonal = [c for c in diagonal if c != combos[0]]
        return (diagonal * n)[:n]
    return (combos[1:] + combos * n)[:n]


def piezas_de(combo, etiquetas):
    return [combo[0], combo[1]] + (["cierre"] if "cierre" in etiquetas else [])


SECCION = re.compile(r"<section\b.*?</section>", re.S)


def recolocar(trozo, mapa, desde, inicio):
    """La pieza 1 del guion llevada a un cuerpo hecho de sus tramos (`mapa`, de cuerpo_nuevo): cada bloque va con el
    tramo que más pisa y lo de dentro no se sale de él; el bloque de un tramo quitado (menos de 0,4 s dentro), fuera.
    `desde`: dónde empieza la pieza 1 en piezas.txt; `inicio`: dónde empieza el cuerpo nuevo en la combinación."""
    def nuevo(t, tramo):
        a, b, n = tramo
        return inicio + n + min(max(t - desde, a), b) - a

    def bloque(seccion):
        etiqueta = seccion[:seccion.index(">")]
        a = float(re.search(r'data-a="([\d.]+)"', etiqueta)[1]) - desde
        fin = re.search(r'data-b="([\d.]+)"', etiqueta)
        b = float(fin[1]) - desde if fin else a + 0.5
        dentro, tramo = max((min(b, z) - max(a, x), (x, z, n)) for x, z, n in mapa)
        if dentro < 0.4:
            return ""
        return TIEMPO.sub(lambda t: f"{t[1]}{nuevo(float(t[2]), tramo):.2f}{t[3]}", seccion)

    def suelto(t):   # lo que lleva tiempo fuera de un bloque: con el tramo en que cae, o el siguiente
        s = float(t[2]) - desde
        tramo = next((x for x in mapa if x[0] <= s < x[1]), None) or min(mapa, key=lambda x: abs(x[0] - s))
        return f"{t[1]}{nuevo(float(t[2]), tramo):.2f}{t[3]}"

    partes, unidades = SECCION.split(trozo), []
    for i, m in enumerate(SECCION.finditer(trozo)):
        hecho = bloque(m[0])
        cuando = float(re.search(r'data-a="([\d.]+)"', hecho)[1]) if hecho else -1.0
        unidades.append((cuando, i, TIEMPO.sub(suelto, partes[i]) + hecho))
    # En otro orden (una lista), cada bloque, con el comentario que lleva delante, va donde cae ahora
    return "".join(u for *_, u in sorted(unidades)) + TIEMPO.sub(suelto, partes[-1])


def guion_de(texto, combo, tramos, derivados=None):
    """El guion.html de una combinación: lo de sus piezas, con sus tiempos donde caen en ella.
    `tramos`: {pieza: [segundo en que empieza en piezas.txt, lo que dura]}. `derivados`: los cuerpos hechos de
    tramos del 1 (--cuerpos), con su mapa: su guion es el de la pieza 1, recolocado."""
    derivado = (derivados or {}).get(combo[1:])
    inicio, t = {}, 0.0
    for e in piezas_de(combo, tramos):
        inicio[e], t = t, t + tramos[e][1]
    trozos, pieza, desde = [], None, 0
    for m in MARCA.finditer(texto):
        trozos.append((pieza, texto[desde:m.start()]))
        pieza, desde = (None if m[1] else m[2]), m.end()
        if pieza is not None and pieza not in PIEZAS:
            raise SystemExit(f"guion-piezas.html: «{m[0]}»; las piezas son {', '.join(PIEZAS)}")
    trozos.append((pieza, texto[desde:]))
    salida = []
    for pieza, trozo in trozos:
        if pieza is None:
            if fuera := TIEMPO.search(trozo):
                raise SystemExit(f"guion-piezas.html: «{fuera[0]}» está fuera de una pieza. Lo que lleva tiempo va "
                                 "dentro de <!-- pieza X --> … <!-- /pieza -->")
            salida.append(trozo)
        elif pieza in inicio:
            mover = inicio[pieza] - tramos[pieza][0]
            salida.append(TIEMPO.sub(lambda m: f"{m[1]}{max(0.0, float(m[2]) + mover):.2f}{m[3]}", trozo))
        elif pieza == "1" and derivado:
            salida.append(recolocar(trozo, derivado, tramos["1"][0], inicio[combo[1:]]))
    return f"<!-- {combo}, sacado de guion-piezas.html: se cambia allí -->\n" + "".join(salida)


def carpeta_de(dir_, combo, combos):
    return dir_ if combo == combos[0] else dir_ / f"_combo-{combo}"


def escribir_guiones(dir_):
    medidas = json.loads((dir_ / "medidas.json").read_text())
    texto = (dir_ / "guion-piezas.html").read_text(encoding="utf-8")
    for combo in medidas["combos"]:
        guion = guion_de(texto, combo, medidas["piezas"], medidas.get("derivados"))
        (carpeta_de(dir_, combo, medidas["combos"]) / "guion.html").write_text(guion, encoding="utf-8")


def largo_imagen(video):
    return float(subprocess.run([FFPROBE, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=duration",
                                 "-of", "csv=p=0", str(video)], capture_output=True, text=True, check=True).stdout)


def juntar(videos, destino):
    """Las piezas en fila, en un vídeo como los de corte.montar. La voz de cada pieza, cortada al largo de su imagen:
    dura unos milisegundos más y, pieza tras pieza, se iría quedando atrás de la boca."""
    entradas = [x for v in videos for x in ("-i", str(v))]
    filtro = "".join(f"[{i}:a]atrim=0:{largo_imagen(v):.3f},asetpts=PTS-STARTPTS[a{i}];" for i, v in enumerate(videos))
    filtro += "".join(f"[{i}:v][a{i}]" for i in range(len(videos))) + f"concat=n={len(videos)}:v=1:a=1[v][a]"
    subprocess.run([FFMPEG, "-v", "error", "-y", *entradas, "-filter_complex", filtro, "-map", "[v]", "-map", "[a]",
                    "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p",
                    "-g", "30", "-keyint_min", "30", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                    str(destino)], check=True)


def montar(f, dir_, unido, palabras, args):
    """El final de `formula preparar` con --piezas. Cada pieza se corta sola (_piezas/X.mp4) y cada combinación
    son sus piezas en fila. `f` es formula.py, por sus ayudas (cortes_sobre_la_voz, escribir_frases…)."""
    dur, hechas, tramos_guion, todas, t = f.duracion_de(unido), {}, {}, [], 0.0
    (dir_ / "_piezas").mkdir(exist_ok=True)
    print("3/4 Quitando silencios y muletillas, pieza a pieza…")
    for e in [e for e in PIEZAS if any(p["pieza"] == e for p in palabras)]:
        suyas = [p for p in palabras if p["pieza"] == e]
        tramos = corte.ajustar_a_la_voz(unido, corte.tramos_a_conservar(suyas, dur), silencio=args.silencio)
        for aviso in f.cortes_sobre_la_voz(unido, tramos, suyas):
            print(f"   ⚠ pieza {e}: {aviso}")
        nuevas, _ = corte.recolocar(suyas, tramos)
        for nueva, vieja in zip(nuevas, [p for p in suyas if not corte.es_muletilla(p["t"])]):
            nueva["n"] = vieja["n"]
        video = dir_ / "_piezas" / f"{e}.mp4"
        corte.montar(unido, tramos, video, tono=args.tono, crf=16, gop=30)
        largo = largo_imagen(video)
        hechas[e] = (video, largo, [p for p in nuevas if p["a"] < largo])
        tramos_guion[e] = [round(t, 3), round(largo, 3)]
        todas.append(f"== pieza {e}: {t:.2f}–{t + largo:.2f} s ==\n"
                     + f.frases_de([{**p, "a": p["a"] + t, "b": p["b"] + t} for p in hechas[e][2]]))
        t += largo
    (dir_ / "piezas.txt").write_text("\n".join(todas), encoding="utf-8")
    derivados = {}
    for e, pedidos in leer_cuerpos(getattr(args, "cuerpos", None) or "", hechas).items():
        if "1" not in hechas:
            raise SystemExit("--cuerpos: hace falta el cuerpo 1")
        video1, largo1, suyas1 = hechas["1"]
        video = dir_ / "_piezas" / f"{e}.mp4"
        palabras_e, mapa = cuerpo_nuevo(video1, tramos_de(pedidos, suyas1, largo1, video1), suyas1, video)
        largo = largo_imagen(video)
        hechas[e], derivados[e] = (video, largo, palabras_e), mapa
        tramos_guion[e] = [tramos_guion["1"][0], round(largo, 3)]
        print(f"   cuerpo {e}, del 1: {largo:.1f} s de {largo1:.1f} ({largo / largo1:.0%}), "
              + " · ".join(f"«{' '.join(p['t'] for p in palabras_e if n <= p['a'] < n + 1.2)}…»" for _, _, n in mapa))

    print("4/4 Un vídeo base por combinación, sin texto…")
    combos = combinaciones(hechas)
    for combo in combos:
        destino = carpeta_de(dir_, combo, combos)
        destino.mkdir(exist_ok=True)
        juntar([hechas[e][0] for e in piezas_de(combo, hechas)], destino / "base.mp4")
        suyas, t = [], 0.0
        for e in piezas_de(combo, hechas):
            suyas += [{**p, "a": p["a"] + t, "b": p["b"] + t} for p in hechas[e][2]]
            t += hechas[e][1]
        (destino / "palabras.json").write_text(json.dumps(suyas, ensure_ascii=False), encoding="utf-8")
        f.apuntar(destino, duracion=f.duracion_de(destino / "base.mp4"), combo=combo)
        f.escribir_frases(suyas, destino)
    luz = f.luz_de_arriba(dir_ / "base.mp4", f.duracion_de(dir_ / "base.mp4"))
    velo = round(max(0.0, min(0.6, (luz - 90) * 0.004)), 2)
    for combo in combos:
        f.apuntar(carpeta_de(dir_, combo, combos), luz_arriba=round(luz), velo=velo)
    f.apuntar(dir_, piezas=tramos_guion, combos=combos, derivados=derivados)
    print(f"\nListo: {dur:.0f} s grabados → {', '.join(f'{e} {hechas[e][1]:.1f} s' for e in hechas)}")
    print(f"  {len(combos)} combinaciones: {', '.join(combos)} (la primera es el reel normal, en la carpeta)")
    print(f"  {dir_ / 'piezas.txt'}: los tiempos de guion-piezas.html")
