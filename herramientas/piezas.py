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
"""
import json
import re
import subprocess

import corte
from config import FFMPEG, FFPROBE

PIEZAS = ("A", "B", "C", "1", "2", "cierre")   # el orden de piezas.txt
GANCHOS, CUERPOS = ("A", "B", "C"), ("1", "2")
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
    Tres ganchos y un cuerpo: B1, C1, A1, B1, C1; sin piezas, todas A1."""
    return (combos[1:] + combos * n)[:n]


def piezas_de(combo, etiquetas):
    return [combo[0], combo[1]] + (["cierre"] if "cierre" in etiquetas else [])


def guion_de(texto, combo, tramos):
    """El guion.html de una combinación: lo de sus piezas, con sus tiempos donde caen en ella.
    `tramos`: {pieza: [segundo en que empieza en piezas.txt, lo que dura]}."""
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
    return f"<!-- {combo}, sacado de guion-piezas.html: se cambia allí -->\n" + "".join(salida)


def carpeta_de(dir_, combo, combos):
    return dir_ if combo == combos[0] else dir_ / f"_combo-{combo}"


def escribir_guiones(dir_):
    medidas = json.loads((dir_ / "medidas.json").read_text())
    texto = (dir_ / "guion-piezas.html").read_text(encoding="utf-8")
    for combo in medidas["combos"]:
        guion = guion_de(texto, combo, medidas["piezas"])
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
    f.apuntar(dir_, piezas=tramos_guion, combos=combos)
    print(f"\nListo: {dur:.0f} s grabados → {', '.join(f'{e} {hechas[e][1]:.1f} s' for e in hechas)}")
    print(f"  {len(combos)} combinaciones: {', '.join(combos)} (la primera es el reel normal, en la carpeta)")
    print(f"  {dir_ / 'piezas.txt'}: los tiempos de guion-piezas.html")
