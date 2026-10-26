"""La Fórmula: edita reels con gráficos animados encima, a partir de tus clips. Cuatro estilos (ajustes: estilo=):
«encima» (tú a pantalla entera y el gráfico arriba), «partida» (pantalla partida: el gráfico en un panel arriba y tú
abajo), «clip» (el clip de otro arriba y tú debajo escuchando; luego tú a pantalla entera) y «vlog» (un día de tu vida,
tu voz encima y una palabra cada vez). Todos se renderizan con HyperFrames.

  formula preparar NOMBRE   junta los clips, quita silencios y transcribe     → base.mp4, frases.txt
                            con --piezas, tres ganchos y dos cuerpos: hasta seis vídeos (piezas.py)
  formula vlog NOMBRE --clips CARPETA | --montar | --voz FICHERO   estilo vlog (vlog.py)
  formula clip NOMBRE URL   estilo clip: el vídeo de otro, transcrito; con --trozos, cortado → clip.mp4
  formula armar NOMBRE      guion.html + subtítulos                            → index.html (y lo valida)
  formula foto NOMBRE 3.2 8 fotogramas para mirarlos antes de renderizar (sin segundos: uno cada 0,5 s)
  formula captura NOMBRE URL FICHERO   la captura de una web para ponerla en pantalla → capturas/FICHERO.png
  formula musica NOMBRE TIPO   la canción de ese tipo que lleva más tiempo sin sonar  → musica.wav
  formula render NOMBRE     el vídeo final y su portada en videos/salida (--borrador: rápido, para ver el ritmo)
  formula portada NOMBRE    solo la portada: el gancho sobre un fotograma con los ojos abiertos
  formula pruebas NOMBRE --hashtags "…"   5 copias de prueba, una al día; grabado en piezas, cada una otro vídeo
                            (otro gancho y otro cuerpo)   → videos/salida/pruebas/

Ver .claude/skills/edicion/SKILL.md.
"""
import argparse, html, json, os, re, shutil, subprocess, sys
from html.parser import HTMLParser
from pathlib import Path

import config  # noqa: E402
import corte  # noqa: E402
import sonidos  # noqa: E402
import musica  # noqa: E402
import vlog as dia  # noqa: E402
import piezas  # noqa: E402
from config import AQUI, KIT, HF_DIR, TRABAJO, ENTRADA, SALIDA, FFMPEG, FFPROBE  # noqa: E402

HF = HF_DIR / "node_modules" / ".bin" / "hyperframes"
ICONOS = HF_DIR / "node_modules"
ENTORNO = {**os.environ, "PATH": f"{config.BIN}:{os.environ['PATH']}", "DO_NOT_TRACK": "1",
           "HYPERFRAMES_TELEMETRY": "0", "PRODUCER_BROWSER_GPU_MODE": "hardware"}
AJUSTES = {"velo": None, "sub-y": 932, "cara-y": 1080, "arriba": 250, "subs": "si", "sonido": 0.14,
            "sonidos": "remates",   # un sonido por idea, en su remate (sonidos.py); sonido=0 los quita; sonidos=todos, todo (cansa)
            "estilo": "encima", "costura": 1060, "encuadre": 68,   # partida y clip: dónde empiezas tú y qué trozo de ti
            "clip-y": 410}   # clip: dónde empieza el clip, debajo del título
ESTILOS = ("encima", "partida", "clip", "vlog")
INGLES = (r"\b(?:the|and|with|for|your|new|free|active|memory|focus|introducing|months?|models?|released?|"
          r"launch(?:es|ed)?|faster|cheaper|best|how|what|why)\b")   # si tu idioma es el español, en pantalla nada en inglés
# Lo que Instagram pinta encima del reel, en px del vídeo: (x0, y0, x1, y1). Además, un iPhone recorta unos 47 px
# por cada lado. Nada de texto ni gráfico ahí: lo tapan la cabecera, los botones y el nombre de la cuenta.
ZONAS_IG = {"la cabecera de Instagram": (0, 0, 1080, 240), "los botones de la derecha": (900, 1130, 1080, 1920),
            "el nombre y el pie": (0, 1680, 1080, 1920)}
LETRAS_SUB = 20      # un subtítulo más largo se parte: a 50 px, 20 letras son unos 600 px y no llegan a los botones
LETRAS_COSTURA = 16  # partida: una o dos palabras cada vez en la costura
ANCHO_BLOQUE = 968   # lo que mide un bloque de lado a lado (1080 menos los dos márgenes de kit/base.css)


def carpeta(nombre):
    return TRABAJO / nombre


def limpia(texto):
    return corte.limpia(texto)


def duracion_de(video):
    import av
    with av.open(str(video)) as c:
        return c.duration / 1e6


# ── preparar ────────────────────────────────────────────────────────────────

def luz_de_arriba(video, dur):
    """Brillo medio (0-255) del tercio de arriba, donde va el texto blanco."""
    from PIL import Image, ImageStat
    import io
    valores = []
    for k in (0.2, 0.5, 0.8):
        png = subprocess.run([FFMPEG, "-v", "error", "-ss", f"{dur * k:.2f}", "-i", str(video), "-frames:v", "1",
                              "-vf", "crop=iw:ih*0.3:0:0,scale=108:-1", "-f", "image2pipe", "-c:v", "png", "-"],
                             capture_output=True, check=True).stdout
        valores.append(ImageStat.Stat(Image.open(io.BytesIO(png)).convert("L")).mean[0])
    return sum(valores) / len(valores)


def frases_de(palabras, desfase=0.0):
    """Una frase por línea con el segundo de cada palabra. El #n de delante es el número de su primera palabra."""
    lineas, frase = [], []
    for i, p in enumerate(palabras):
        frase.append(p)
        if re.search(r"[.?!…]$", p["t"]) or i == len(palabras) - 1:
            lineas.append(f"#{frase[0]['n']:<4}[{frase[0]['a'] + desfase:6.2f}–{frase[-1]['b'] + desfase:6.2f}]  "
                          + " ".join(f"{q['t']}({q['a'] + desfase:.2f})" for q in frase))
            frase = []
    return "\n".join(lineas) + "\n"


def escribir_frases(palabras, dir_):
    """frases.txt: de aquí salen los tiempos del guion. palabras.txt: una por línea, con su número, para
    cortar por dentro de una frase con --fuera. En el estilo clip, los dos van ya con el clip delante:
    son los segundos del vídeo entero."""
    desfase = desfase_de(dir_)
    (dir_ / "frases.txt").write_text(frases_de(palabras, desfase), encoding="utf-8")
    (dir_ / "palabras.txt").write_text(
        "".join(f"{p['n']:<5}{p['a'] + desfase:7.2f}  {p['t']}\n" for p in palabras), encoding="utf-8")


def desfase_de(dir_):
    """Lo que dura el clip de otro que va delante (estilo clip, `formula clip`); 0 si no hay."""
    medidas = dir_ / "medidas.json"
    return json.loads(medidas.read_text()).get("clip", 0.0) if medidas.exists() else 0.0


def apuntar(dir_, **datos):
    """medidas.json sin perder lo que ya tenía (preparar y clip escriben cada uno lo suyo)."""
    medidas = dir_ / "medidas.json"
    viejo = json.loads(medidas.read_text()) if medidas.exists() else {}
    medidas.write_text(json.dumps({**viejo, **datos}))


def cortes_sobre_la_voz(unido, tramos, palabras):
    """Cada corte se mira antes de enseñar el vídeo: si cae con la voz aún sonando (los 30 ms de cada lado a menos
    de 20 dB de la voz normal), se oye el tijeretazo. Con un aviso: se quita la frase entera o se mueve el corte."""
    import numpy as np
    pcm = subprocess.run([FFMPEG, "-v", "error", "-i", str(unido), "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
    n = len(x) // 160
    voz = np.percentile(20 * np.log10(np.sqrt((x[:n * 160].reshape(n, 160) ** 2).mean(1)) + 1e-9), 90)
    nivel = lambda t0, t1: 20 * np.log10(np.sqrt((x[int(t0 * 16000):int(t1 * 16000)] ** 2).mean()) + 1e-9) - voz
    avisos, montado = [], 0.0
    for (a1, b1), (a2, _) in zip(tramos, tramos[1:]):
        montado += b1 - a1
        cola, ataque = nivel(b1 - .03, b1), nivel(a2, a2 + .03)
        if max(cola, ataque) > -20:
            antes = [p["t"] for p in palabras if p["a"] < b1][-1:]
            despues = [p["t"] for p in palabras if p["b"] > a2][:1]
            avisos.append(f"corte sobre la voz en el {montado:.1f} s del montaje («{' '.join(antes)} | {' '.join(despues)}», "
                          f"{max(cola, ataque):.0f} dB): escúchalo o quita la frase entera")
    return avisos


def preparar(args):
    dir_ = carpeta(args.nombre)
    dir_.mkdir(parents=True, exist_ok=True)
    unido, crudo = dir_ / "unido.mov", dir_ / "crudo.json"

    if not (unido.exists() and crudo.exists()):   # lo lento se hace una vez; repetir preparar solo recorta
        origen = Path(args.clips).expanduser() if args.clips else ENTRADA
        clips = corte.ordenar([p for p in origen.iterdir() if p.suffix.lower() in corte.VIDEO_EXT])
        if not clips:
            sys.exit(f"No hay vídeos en {origen}")
        print("Orden:", *[f"  {i}) {c.name}" for i, c in enumerate(clips, 1)], sep="\n")
        print("1/4 Juntando clips…")
        corte.unir(clips, unido)
        print("2/4 Transcribiendo (Whisper, en tu ordenador)…")
        palabras = corte.transcribir(unido, args.pista)
        if not palabras:
            sys.exit("No se ha detectado voz.")
        crudo.write_text(json.dumps(palabras, ensure_ascii=False), encoding="utf-8")

    palabras = corte.juntar_cifras(json.loads(crudo.read_text(encoding="utf-8")))
    # crudo.txt: todo lo que dijiste, sin quitar nada, con el número de cada palabra (para --piezas)
    (dir_ / "crudo.txt").write_text(frases_de([{**p, "n": n} for n, p in enumerate(palabras)]), encoding="utf-8")
    # En piezas, las tomas repetidas se buscan dentro de cada una: el gancho B o el cuerpo 2 dicen lo mismo que el A
    # o el 1 con otras palabras, y si no quitar_repetidas se quedaría solo con el último
    trozos = piezas.trocear(palabras, piezas.leer(args.piezas)).values() if args.piezas else [palabras]
    palabras = []
    for trozo in trozos:
        trozo, repetidas = corte.quitar_repetidas(trozo)
        if repetidas:
            print(f"   {repetidas} palabras de tomas repetidas fuera (me quedo con la última)")
        trozo, quitadas = corte.quitar_fallos(trozo)
        for q in quitadas:   # «corta eso», arranques cortados y frases dichas otra vez: se leen, por si sobra alguno
            print(f"   fuera: «{q}»")
        palabras += trozo
    for n, p in enumerate(palabras):
        p["n"] = n
    fuera = set()   # tomas que sobran: «57» = la frase que empieza en la palabra 57; «83-91» = esas palabras
    for trozo in filter(None, (args.fuera or "").split(",")):
        a, _, b = trozo.partition("-")
        if not b:
            b = next((p["n"] for p in palabras[int(a):] if re.search(r"[.?!…]$", p["t"])), len(palabras) - 1)
        fuera.update(range(int(a), int(b) + 1))
    palabras = [p for p in palabras if p["n"] not in fuera]
    cambios = dict(par.split("=") for par in filter(None, (args.cambia or "").split(";")))
    for p in palabras:                                          # lo que Whisper oyó mal
        clave = limpia(p["t"])
        for mal, bien in cambios.items():
            if mal == f"#{p['n']}":                              # «#185=programación.»: solo esa, entera
                p["t"] = bien
            elif clave == limpia(mal):
                p["t"] = re.sub(r"[\wáéíóúñüÁÉÍÓÚÑÜ]+", bien, p["t"], count=1)
    if args.piezas:
        return piezas.montar(sys.modules[__name__], dir_, unido, palabras, args)

    print("3/4 Quitando silencios y muletillas…")
    dur = duracion_de(unido)
    tramos = corte.ajustar_a_la_voz(unido, corte.tramos_a_conservar(palabras, dur), silencio=args.silencio)
    for aviso in cortes_sobre_la_voz(unido, tramos, palabras):
        print(f"   ⚠ {aviso}")
    nuevas, dur_final = corte.recolocar(palabras, tramos)
    for nueva, vieja in zip(nuevas, [p for p in palabras if not corte.es_muletilla(p["t"])]):
        nueva["n"] = vieja["n"]

    print("4/4 Vídeo base, sin texto…")
    base = dir_ / "base.mp4"
    corte.montar(unido, tramos, base, tono=args.tono, crf=16, gop=30)
    dur_final = duracion_de(base)
    nuevas = [p for p in nuevas if p["a"] < dur_final]
    (dir_ / "palabras.json").write_text(json.dumps(nuevas, ensure_ascii=False), encoding="utf-8")
    luz = luz_de_arriba(base, dur_final)
    velo = round(max(0.0, min(0.6, (luz - 90) * 0.004)), 2)
    apuntar(dir_, duracion=dur_final, luz_arriba=round(luz), velo=velo)
    escribir_frases(nuevas, dir_)
    print(f"\nListo: {dur:.0f} s → {dur_final:.1f} s. Pared de arriba: {luz:.0f}/255 → velo {velo}")
    print(f"  {dir_ / 'frases.txt'}")


def clip(args):
    """Estilo clip: el vídeo de otro que va arriba (estilos.md). La primera vez lo
    baja y lo transcribe en su idioma (fuente.txt, para elegir) y saca fuente.jpg con una rejilla cada 100 px
    (para el recorte). Con --trozos: clip.mp4, solo esos trozos, sin las pausas largas y del tamaño del hueco."""
    dir_ = carpeta(args.nombre)
    dir_.mkdir(parents=True, exist_ok=True)
    fuente, crudo = dir_ / "fuente.mp4", dir_ / "fuente.json"
    if not fuente.exists():
        if re.match(r"https?://", args.fuente):   # de X sale también un 4K de 700 MB: con 1080 basta
            subprocess.run(["yt-dlp", "-q", "--no-warnings", "-f", "bv*[height<=1080]+ba/b[height<=1080]",
                            "--merge-output-format", "mp4", "-o", str(fuente), args.fuente], check=True)
        else:
            shutil.copy(Path(args.fuente).expanduser(), fuente)
    dur = duracion_de(fuente)
    if not crudo.exists():
        print("Transcribiendo el clip (Whisper, en tu ordenador)…")
        palabras = corte.transcribir(fuente, args.pista, idioma=None)
        crudo.write_text(json.dumps(palabras, ensure_ascii=False), encoding="utf-8")
        subprocess.run([FFMPEG, "-v", "error", "-y", "-ss", f"{dur / 2:.1f}", "-i", str(fuente), "-frames:v", "1",
                        "-vf", "drawgrid=w=100:h=100:t=1:c=red@0.5", str(dir_ / "fuente.jpg")], check=True)
    palabras = json.loads(crudo.read_text(encoding="utf-8"))
    for n, p in enumerate(palabras):
        p["n"] = n
    (dir_ / "fuente.txt").write_text(frases_de(palabras), encoding="utf-8")
    if not args.trozos:
        return print(f"  {dir_ / 'fuente.txt'}\n  {dir_ / 'fuente.jpg'}\nAhora: formula clip {args.nombre} {args.fuente} "
                     '--trozos "4.2-8.9,10.5-11.9" (segundos de fuente.txt)')

    # Cada trozo por separado: si no, dos trozos seguidos se juntan con lo que hay entre ellos
    alto = float(AJUSTES["costura"]) - float(AJUSTES["clip-y"])
    trozos = [tuple(map(float, t.split("-"))) for t in args.trozos.split(",")]
    tramos = []
    for a, b in trozos:
        dichas = [p for p in palabras if a <= p["a"] < b]
        # pausas de hasta 0,35 s dentro de un trozo: en un podcast, cada corte de 0,12 s se ve como un salto
        tramos += corte.ajustar_a_la_voz(fuente, corte.tramos_a_conservar(dichas, dur), silencio=0.35)
    dichas = [p for p in palabras if any(a <= p["a"] < b for a, b in trozos)]
    nuevas, _ = corte.recolocar(dichas, tramos)
    w, h = (int(v) for v in subprocess.run([FFPROBE, "-v", "error", "-select_streams", "v:0",
                                            "-show_entries", "stream=width,height", "-of", "csv=p=0", str(fuente)],
                                           capture_output=True, text=True, check=True).stdout.split(","))
    if args.recorte:   # «x,y,ancho,alto» en px de fuente.jpg: fuera los subtítulos quemados y los logos del programa
        x, y, rw, rh = (int(v) for v in args.recorte.split(","))
    else:              # el centro, del alto entero
        rh, rw = h, min(w, round(h * 1080 / alto))
        x, y = (w - rw) // 2, 0
    encuadrado = dir_ / "encuadrado.mp4"
    subprocess.run([FFMPEG, "-v", "error", "-y", "-i", str(fuente), "-vf",
                    f"crop={rw}:{rh}:{x}:{y},scale=1080:{round(alto)}:force_original_aspect_ratio=increase,"
                    f"crop=1080:{round(alto)},setsar=1", "-c:v", "libx264", "-preset", "veryfast", "-crf", "14",
                    "-c:a", "copy", str(encuadrado)], check=True)
    corte.montar(encuadrado, tramos, dir_ / "clip.mp4", tono="sin tocar", crf=16, gop=30)
    encuadrado.unlink()
    largo = duracion_de(dir_ / "clip.mp4")
    for n, p in enumerate(nuevas):
        p["n"] = n
    (dir_ / "clip.json").write_text(json.dumps(nuevas, ensure_ascii=False), encoding="utf-8")
    (dir_ / "clip.txt").write_text(frases_de(nuevas), encoding="utf-8")
    apuntar(dir_, clip=largo)
    if (dir_ / "palabras.json").exists():   # lo tuyo va detrás del clip: sus tiempos se mueven
        escribir_frases(json.loads((dir_ / "palabras.json").read_text(encoding="utf-8")), dir_)
    if args.reaccion:   # tu toma escuchando el clip, sin sonido y del largo del clip
        subprocess.run([FFMPEG, "-v", "error", "-y", "-ss", f"{args.desde:.2f}", "-t", f"{largo:.3f}",
                        "-i", str(Path(args.reaccion).expanduser()), "-an", "-vf",   # el tono de base.mp4: al subir no cambia de color
                        corte.TONOS[args.tono] + "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1",
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-g", "30", str(dir_ / "reaccion.mp4")],
                       check=True)
    elif not (dir_ / "reaccion.mp4").exists():
        print("⚠️  falta tu toma de reacción (--reaccion): abajo no hay nada mientras suena el clip")
    print(f"\nClip: {sum(b - a for a, b in trozos):.1f} s elegidos → {largo:.1f} s\n  {dir_ / 'clip.txt'}")


# ── armar ───────────────────────────────────────────────────────────────────

def svg_marca(slug):
    svg = (ICONOS / "simple-icons" / "icons" / f"{slug}.svg").read_text(encoding="utf-8")
    datos = json.loads((ICONOS / "simple-icons" / "data" / "simple-icons.json").read_text(encoding="utf-8"))
    color = next(d["hex"] for d in datos if d["slug"] == slug)
    svg = re.sub(r"<title>.*?</title>", "", svg)
    return svg.replace("<svg ", f'<svg fill="#{color}" ', 1), color


def svg_icono(nombre):
    svg = (ICONOS / "lucide-static" / "icons" / f"{nombre}.svg").read_text(encoding="utf-8")
    return re.sub(r"<!--.*?-->\s*", "", svg, flags=re.S).strip()


def poner_iconos(guion):
    """<i data-marca="claude"></i> → el logo en su color; <i data-icono="mail"></i> → icono de línea."""
    guion = re.sub(r'<i data-marca="([\w-]+)"></i>', lambda m: svg_marca(m.group(1))[0], guion)
    return re.sub(r'<i data-icono="([\w-]+)"></i>', lambda m: svg_icono(m.group(1)), guion)


def poner_tiempos(guion, dur):
    """data-a / data-b (segundo en que entra y en que sale) → lo que entiende HyperFrames."""
    bloques = []

    def cambiar(m):
        etiqueta = m.group(0)
        a = float(re.search(r'data-a="([\d.]+)"', etiqueta).group(1))
        b = min(float(re.search(r'data-b="([\d.]+)"', etiqueta).group(1)), dur)
        clase = re.search(r'class="([^"]*)"', etiqueta).group(1)
        bloques.append((a, b, clase))
        etiqueta = re.sub(r'\s*data-[ab]="[\d.]+"', "", etiqueta)
        etiqueta = etiqueta.replace(f'class="{clase}"', f'id="{clase.split()[0]}-{len(bloques)}" class="{clase} clip"', 1)
        return etiqueta[:-1] + f' data-start="{a:.3f}" data-duration="{b - a:.3f}" data-track-index="2">'

    return re.sub(r'<\w+[^>]*\bdata-a="[\d.]+"[^>]*>', cambiar, guion), bloques


def subtitulos(palabras, dur):
    bloques = []
    for bloque in corte.lineas(palabras):
        medio = len(bloque) // 2
        largo = len(" ".join(p["t"] for p in bloque)) > LETRAS_SUB and medio
        bloques += [bloque[:medio], bloque[medio:]] if largo else [bloque]
    salida = []
    for k, bloque in enumerate(bloques):
        a = bloque[0]["a"]
        b = bloques[k + 1][0]["a"] if k + 1 < len(bloques) else dur
        b = min(b, bloque[-1]["b"] + 0.6, dur)
        texto = re.sub(r"[.,;:]+$", "", " ".join(p["t"] for p in bloque))
        salida.append(f'<p id="sub-{k + 1}" class="sub clip" data-start="{a:.3f}" data-duration="{max(b - a, 0.1):.3f}" '
                      f'data-track-index="3">{html.escape(texto)}</p>')
    return "\n".join(salida)


def subtitulos_claves(palabras, dur, claves):
    """«subs=claves»: quietos, como los de CapCut: 2 a 4 palabras blancas con borde fino, debajo de la barbilla, que
    cambian de golpe; las claves (<!-- claves: … -->) y las cifras, en tu color de acento. Palabra a palabra con
    cajas que saltan llama demasiado la atención: el subtítulo acompaña, no compite con el gráfico."""
    bloques = []
    for bloque in corte.lineas(palabras):
        medio = len(bloque) // 2
        largo = len(" ".join(p["t"] for p in bloque)) > LETRAS_SUB and medio
        bloques += [bloque[:medio], bloque[medio:]] if largo else [bloque]
    salida = []
    for k, bloque in enumerate(bloques):
        a = bloque[0]["a"]
        b = min(bloques[k + 1][0]["a"] if k + 1 < len(bloques) else dur, bloque[-1]["b"] + 0.6, dur)
        trozos, n = [], 0
        while n < len(bloque):
            largo = next((len(c) for c in claves if [limpia(x["t"]) for x in bloque[n:n + len(c)]] == c), 0)
            if not largo and re.search(r"\d", bloque[n]["t"]):
                largo = 1
            texto = " ".join(html.escape(x["t"]) for x in bloque[n:n + (largo or 1)])
            trozos.append(f'<span class="acento">{texto}</span>' if largo else texto)
            n += largo or 1
        texto = re.sub(r"[.,;:]+(</span>)?$", r"\1", " ".join(trozos))
        salida.append(f'<p id="sub-{k + 1}" class="sub claves clip" data-start="{a:.3f}" data-duration="{max(b - a, 0.1):.3f}" '
                      f'data-track-index="3">{texto}</p>')
    return "\n".join(salida)


def palabra_a_palabra(palabras, dur):
    """Estilo vlog: una palabra cada vez, sola en el centro. Sin puntuación; las cifras, en tu acento.
    Se queda hasta la siguiente o medio segundo tras decirla."""
    salida = []
    for k, p in enumerate(palabras):
        b = min(palabras[k + 1]["a"] if k + 1 < len(palabras) else dur, p["b"] + 0.5, dur)
        texto = html.escape(re.sub(r"[.,;:¿?¡!…\"«»]+", "", p["t"]))
        if not texto:
            continue
        if re.search(r"\d", texto):
            texto = f'<span class="acento">{texto}</span>'
        salida.append(f'<p id="sub-{k + 1}" class="sub clip" data-start="{p["a"]:.3f}" '
                      f'data-duration="{max(b - p["a"], 0.08):.3f}" data-track-index="3">{texto}</p>')
    return "\n".join(salida)


def claves_de(guion):
    """<!-- claves: muy loca, IA, copiar --> → las palabras que salen en tu acento (y solas y grandes en «partida»)."""
    m = re.search(r"<!--\s*claves:(.*?)-->", guion, flags=re.S)
    return [[limpia(w) for w in c.split()] for c in m.group(1).split(",") if c.strip()] if m else []


def costuras(palabras, dur, claves):
    """Los subtítulos de «partida», en la costura: cada clave sola (cada vez que la dice) y lo demás
    de una o dos palabras, sin pasar de una pausa ni de un punto."""
    def clave_en(i):
        return next((len(c) for c in claves if [limpia(p["t"]) for p in palabras[i:i + len(c)]] == c), 0)
    trozos, i = [], 0
    while i < len(palabras):
        n = clave_en(i)
        if n:
            trozos.append((palabras[i:i + n], True))
            i += n
            continue
        trozo = [palabras[i]]
        i += 1
        while (i < len(palabras) and len(trozo) < 2 and not clave_en(i) and not re.search(r"[.,;:?!]$", trozo[-1]["t"])
               and palabras[i]["a"] - trozo[-1]["b"] < 0.25
               and len(" ".join(p["t"] for p in trozo + [palabras[i]])) <= LETRAS_COSTURA):
            trozo.append(palabras[i])
            i += 1
        trozos.append((trozo, False))
    salida = []
    for k, (trozo, clave) in enumerate(trozos):
        a = trozo[0]["a"]
        if a >= dur:   # un vídeo recortado (una prueba de los primeros segundos)
            break
        b = trozos[k + 1][0][0]["a"] if k + 1 < len(trozos) else dur
        b = min(b, trozo[-1]["b"] + 0.6, dur)
        texto = re.sub(r"[.,;:]+$", "", " ".join(p["t"] for p in trozo))
        salida.append(f'<p id="costura-{k + 1}" class="costura{" clave" if clave else ""} clip" data-start="{a:.3f}" '
                      f'data-duration="{max(b - a, 0.1):.3f}" data-track-index="3">{html.escape(texto)}</p>')
    return "\n".join(salida)


def sacar_dichos(guion):
    """Estilo clip: la traducción de lo que dice el clip, <p class="dice" data-a="0" data-b="2.4">Uno pensaría</p>
    por frase. Devuelve [(a, b, texto)] y el guion sin ellas."""
    dichos = []
    for m in re.finditer(r'<p\b[^>]*\bclass="dice"[^>]*>(.*?)</p>', guion, flags=re.S):
        a, b = (float(re.search(rf'data-{k}="([\d.]+)"', m.group(0)).group(1)) for k in "ab")
        dichos.append((a, b, html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip()))
    return dichos, re.sub(r'<p\b[^>]*\bclass="dice"[^>]*>.*?</p>\s*', "", guion, flags=re.S)


def traduccion(dichos, dur, claves):
    """Estilo clip: cada frase traducida entera mientras suena, como el subtítulo de una película, y sus claves
    en el acento. De una o dos palabras cada vez no da tiempo a leerla mientras el otro habla."""
    salida = []
    for k, (a, b, texto) in enumerate(dichos):
        w, i, partes = re.sub(r"[.,;:]+$", "", texto).split(), 0, []
        while i < len(w):
            n = next((len(c) for c in claves if [limpia(p) for p in w[i:i + len(c)]] == c), 0)
            partes.append(f'<span class="acento">{html.escape(" ".join(w[i:i + n]))}</span>' if n else html.escape(w[i]))
            i += n or 1
        b = min(dichos[k + 1][0] if k + 1 < len(dichos) else dur, b + 0.6, dur)
        salida.append(f'<p id="dice-{k + 1}" class="traduccion clip" data-start="{a:.3f}" '
                      f'data-duration="{max(b - a, 0.1):.3f}" data-track-index="3">{" ".join(partes)}</p>')
    return "\n".join(salida)


class _Capturas(HTMLParser):
    """Las capturas del guion ya armado: (fichero, alto máximo, sobre tu cara, segundos que se ve)."""

    def __init__(self):
        super().__init__()
        self.a = self.b = 0.0
        self.cara, self.lista = False, []

    def handle_starttag(self, etiqueta, attrs):
        at = {k: v or "" for k, v in attrs}
        clases = at.get("class", "").split()
        if "beat" in clases:
            self.a = float(at["data-start"])
            self.b, self.cara = self.a + float(at["data-duration"]), "cara" in clases
        if "captura" in clases:
            en = at.get("data-en", "+0").strip()
            entra = self.a + float(en[1:]) if en.startswith("+") else float(en)
            alto = re.search(r"--alto:\s*(\d+)", at.get("style", ""))
            self.lista.append((at.get("src", ""), int(alto.group(1)) if alto else 560, self.cara, self.b - entra))


def avisos_de_capturas(guion, dir_, aj):
    from PIL import Image
    lector, lista = _Capturas(), []
    lector.feed(guion)
    for src, alto, cara, segundos in lector.lista:
        if not src or re.match(r"(https?:)?//", src):
            lista.append(f"una captura es un fichero de capturas/, no una dirección ({src or 'sin src'}): al renderizar no hay red")
            continue
        if not (dir_ / src).exists():
            lista.append(f"falta la captura {src}")
            continue
        w, h = Image.open(dir_ / src).size
        escala = min(ANCHO_BLOQUE / w, alto / h, 1)
        if escala == 1 and w < 800:
            lista.append(f"{src} solo mide {w} px de ancho: saldrá pequeña. Se saca otra vez, más recortada")
        baja = float(aj["cara-y"]) + h * escala / 2
        if cara and baja > float(aj["sub-y"]) - 20:
            lista.append(f"{src}, sobre tu cara, baja hasta {baja:.0f} y los subtítulos están en {aj['sub-y']}: "
                         f'style="--alto:{2 * (float(aj["sub-y"]) - 30 - float(aj["cara-y"])):.0f}px"')
        if segundos > 5:
            lista.append(f"{src} se queda {segundos:.1f} s en pantalla: una captura aguanta de 0,6 a 3,5 s, lo que dura su frase")
        elif segundos < 0.5:
            lista.append(f"{src} se ve {segundos:.1f} s: no da tiempo ni a saber qué es")
    return lista


def avisos(guion, bloques, dur, dir_, aj):
    """Lo que se comprueba solo. Lo demás se mira en los fotogramas."""
    lista = [f"titular de {len(t)} letras, puede irse a dos líneas: «{t}»"
             for t in re.findall(r'class="titular[^"]*"[^>]*>([^<]+)<', guion) if len(t) > 32]
    beats = sorted((a, b, "cara" in clase.split()) for a, b, clase in bloques if "beat" in clase.split())
    for cara in (False, True):   # un bloque sobre tu cara es otra capa: puede convivir con el de arriba
        capa = [(a, b) for a, b, c in beats if c == cara]
        lista += [f"el bloque de {a:.1f} s acaba en {b:.1f} y el siguiente empieza en {a2:.1f}: se pisan"
                  for (a, b), (a2, _) in zip(capa, capa[1:]) if a2 < b - 0.01]
    cabecera = ZONAS_IG["la cabecera de Instagram"][3]
    altos = [("arriba", float(aj["arriba"]))] + [(m, float(m)) for m in re.findall(r'style="[^"]*(?<![-\w])top:\s*(\d+)px', guion)]
    lista += [f"algo empieza en {y:.0f} px ({de}): por encima de {cabecera} lo tapa la cabecera de Instagram"
              for de, y in altos if y < cabecera]
    pie = ZONAS_IG["el nombre y el pie"][1]
    partida_, desde = aj["estilo"] == "partida", aj["desde"]
    if aj["estilo"] not in ("encima", "vlog") and not claves_de(guion):
        lista.append(f"estilo {aj['estilo']} sin <!-- claves: … -->: ninguna palabra sale "
                     + ("en naranja en la traducción" if aj["estilo"] == "clip" else "grande en la costura"))
    if aj["estilo"] == "clip" and not desde:
        lista.append("estilo clip sin clip: falta `formula clip NOMBRE URL --trozos …`")
    if desde and not (dir_ / "reaccion.mp4").exists():
        lista.append("falta tu toma escuchando el clip (`formula clip … --reaccion FICHERO`): abajo no hay nada")
    if partida_:   # el panel vacío se ve roto, aunque sea una décima
        lista += [f"de {b:.2f} a {a2:.2f} s el panel se queda vacío: el bloque de {a:.1f} s, hasta {a2:.2f}"
                  for (a, b, _), (a2, _, _) in zip(beats, beats[1:]) if 0.01 < a2 - b]
    if not partida_ and float(aj["sub-y"]) + 130 > pie:
        lista.append(f"sub-y={aj['sub-y']}: un subtítulo de dos líneas baja de {pie} y se mezcla con el nombre de la cuenta")
    fin = max(beats[0][1], desde) if beats else 0   # mientras suena el clip, lo que se ve es el clip
    for a, b, _ in beats[1:]:
        if a - fin > 3:
            lista.append(f"de {fin:.1f} a {a:.1f} s no hay nada en pantalla ({a - fin:.1f} s)")
        fin = max(fin, b)
    lista += [f"el bloque de {a:.1f} s dura {b - a:.1f} s: no da tiempo a leerlo" for a, b, clase in bloques
              if "beat" in clase.split() and "entera" not in clase.split() and b - a < 1.2]   # «PASO 1» dura lo que el «uno»
    suyos = [a for a, _, _ in beats if a >= desde]
    if suyos and suyos[0] > desde + 3:
        lista.append(f"el primer bloque {'tras el clip ' if desde else ''}llega en el segundo {suyos[0]:.1f}: tarde")
    lista += avisos_de_capturas(guion, dir_, aj)
    # lo que no da tiempo a leer: más de 3,5 palabras por segundo sin contar el titular
    for a, d, dentro in re.findall(r'<section[^>]*\bclass="beat[^"]*"[^>]*data-start="([\d.]+)" data-duration="([\d.]+)"[^>]*>(.*?)</section>',
                                   guion, flags=re.S):
        texto = re.sub(r'<h2.*?</h2>|<svg.*?</svg>|<span class="pista".*?</span>|<[^>]+>', " ", dentro, flags=re.S)
        n = len(re.findall(r"\w+", texto))
        if n > 6 and n / float(d) > 3.5:
            lista.append(f"el bloque de {float(a):.1f} s lleva {n} palabras para {float(d):.1f} s, sin contar el titular: no da tiempo a leerlo")
    for m in re.finditer(r'<div[^>]*class="gancho[^"]*"[^>]*>(.*?)</div>', guion, flags=re.S):
        largas = [l.strip() for l in re.split(r"<br\s*/?>", m.group(1)) if len(re.sub(r"[^\w ]", "", l).strip()) > 14]
        if largas and "font-size" not in m.group(0) and "tres" not in m.group(0) and aj["estilo"] == "encima":
            lista.append(f"el gancho se va a tres líneas («{largas[0]}» pasa de 14 letras): "
                         'style="font-size:126px; white-space:nowrap" o menos palabras')
    rotulos = re.sub(r"<svg.*?</svg>|<[^>]+>", " ", re.sub(r"<!--.*?-->", "", guion, flags=re.S), flags=re.S)
    ingles = sorted(set(re.findall(INGLES, rotulos, flags=re.I)), key=str.lower) if config.marca()["idioma"] == "es" else []
    if ingles:
        lista.append(f"en pantalla, todo en español, y hay rótulos que parecen inglés: {', '.join(ingles)}")
    if not any("gancho" in clase.split() for _, _, clase in bloques):
        lista.append("no hay gancho: el primer fotograma es la portada del reel")
    # Ninguna cifra en pantalla sin respaldo: la has dicho o está en las fuentes del guion
    respaldo = "".join(re.sub(r"\([\d.]+\)", "", (dir_ / f).read_text(encoding="utf-8"))   # sin los segundos
                       for f in ("frases.txt", "clip.txt") if (dir_ / f).exists())
    if (dir_ / "hablado.json").exists():
        respaldo += " ".join(json.loads((dir_ / "hablado.json").read_text(encoding="utf-8")).get("fuentes", []))
    digitos = lambda s: re.sub(r"[.,\s]", "", s)
    visible = re.sub(r"<(style|script|svg)\b.*?</\1>|<!--.*?-->|<[^>]+>", " ", guion, flags=re.S)
    cifras = re.findall(r'data-(?:cuenta|rueda)="[\d.]+,([\d.]+)"', guion) + re.findall(r"\d[\d.,]*\d|\d", visible)
    sueltas = sorted({c for c in cifras if len(digitos(c)) >= 2 and digitos(c) not in digitos(respaldo)})
    if sueltas:
        lista.append(f"cifras en pantalla que ni dice ni están en las fuentes: {', '.join(sueltas)}. Se comprueban o fuera")
    return lista


def leer_ajustes(guion, velo=None):
    """La primera línea del guion: <!-- ajustes: estilo=partida sub-y=932 … -->, sobre AJUSTES."""
    aj = dict(AJUSTES, velo=velo)
    m = re.search(r"<!--\s*ajustes:(.*?)-->", guion, flags=re.S)
    if m:
        aj.update(par.split("=") for par in m.group(1).split())
    if aj["estilo"] not in ESTILOS:
        sys.exit(f"estilo={aj['estilo']}: es {' o '.join(ESTILOS)}")
    return aj


# Las letras que instala instalar.sh (fontsource) en kit/fonts: familia → fichero. Las variables, de 100 a 900
LETRAS = {"Inter": ("inter.woff2", True), "JetBrains Mono": ("jetbrains-mono.woff2", True), "Montserrat": ("montserrat.woff2", True),
          "Bebas Neue": ("bebas-neue.woff2", False), "Anton": ("anton.woff2", False), "Poppins": ("poppins.woff2", False),
          "Instrument Serif": ("instrument-serif.woff2", False)}


def letras():
    """@font-face de las letras instaladas: al renderizar no hay red, todo sale de kit/fonts."""
    reglas = []
    for familia, (fichero, variable) in LETRAS.items():
        if (KIT / "fonts" / fichero).exists():
            peso = "font-weight: 100 900; " if variable else ""
            reglas.append(f'@font-face {{ font-family: "{familia}"; src: url("kit/fonts/{fichero}") format("woff2"); {peso}font-display: block; }}')
    if (KIT / "fonts" / "instrument-serif-italic.woff2").exists():
        reglas.append('@font-face { font-family: "Instrument Serif"; src: url("kit/fonts/instrument-serif-italic.woff2") format("woff2"); '
                      'font-style: italic; font-display: block; }')
    return "\n".join(reglas) + "\n"


def variables_de_marca():
    """Tus colores y letras (marca/marca.json), encima de los valores por defecto del kit."""
    m = config.marca()
    c, l = m["colores"], m["letras"]
    for familia in l.values():
        if familia not in LETRAS:
            print(f"⚠️  la letra «{familia}» no está instalada: vale {', '.join(LETRAS)}")
    return (f':root {{ --acento: {c["acento"]}; --panel: {c["panel"]}; --papel: {c["papel"]}; --tinta: {c["tinta"]}; '
            f'--letra: "{l["texto"]}"; --letra-grande: "{l["grande"]}"; --mono: "{l["mono"]}"; --letra-titulo: "{l["titulo"]}"; }}\n')


def construir(nombre):
    """Escribe index.html a partir del guion. Lo llaman armar, foto y render: nunca va atrasado."""
    dir_ = carpeta(nombre)
    if (dir_ / "guion-piezas.html").exists():   # grabado en piezas: el guion.html de cada combinación sale de ahí
        piezas.escribir_guiones(dir_)
    guion = (dir_ / "guion.html").read_text(encoding="utf-8") if (dir_ / "guion.html").exists() else ""
    medidas = json.loads((dir_ / "medidas.json").read_text())
    aj = leer_ajustes(guion, medidas["velo"])
    partida_ = aj["estilo"] == "partida"
    # estilo clip: el clip de otro va delante y tú entras cuando acaba; todos los tiempos, del vídeo entero
    aj["desde"] = desde = medidas.get("clip", 0.0) if aj["estilo"] == "clip" else 0.0
    dur = medidas["duracion"] + desde
    dichos, guion = sacar_dichos(guion)
    suena = sonidos.eventos(guion, todos=aj["sonidos"] == "todos") if float(aj["sonido"]) > 0 else []
    if aj["sonidos"] not in ("remates", "todos"):   # o solo esos tipos: «sonidos=pop,golpe»
        suena = [e for e in suena if e[1] in aj["sonidos"].split(",")]
    if suena:
        sonidos.mezclar(suena, dur, dir_ / "sonidos.wav", float(aj["sonido"]))
    pista = (f'<audio id="sonidos" class="clip" src="sonidos.wav" data-start="0" data-duration="{dur:.3f}" '
             f'data-track-index="4" data-volume="1"></audio>') if suena else ""
    if aj.get("musica"):    # «musica=musica.wav»: ya cortada, con su volumen y sus fundidos (formula musica)
        pista += (f'<audio id="musica" class="clip" src="{aj["musica"]}" data-start="0" data-duration="{dur:.3f}" '
                  f'data-track-index="5" data-volume="1"></audio>')
    guion, bloques = poner_tiempos(poner_iconos(guion), dur)
    palabras = json.loads((dir_ / "palabras.json").read_text(encoding="utf-8"))

    shutil.copytree(KIT, dir_ / "kit", dirs_exist_ok=True)
    css = letras() + (KIT / "base.css").read_text(encoding="utf-8")
    if aj["estilo"] != "encima":
        css += "\n" + (KIT / f"{aj['estilo']}.css").read_text(encoding="utf-8")
    css += "\n" + variables_de_marca()
    subs = ""
    if aj["subs"] == "si" and partida_:
        subs = costuras(palabras, dur, claves_de(guion))
    elif aj["subs"] == "claves":
        subs = subtitulos_claves(palabras, dur, claves_de(guion))
    elif aj["subs"] == "si" and aj["estilo"] == "vlog":
        subs = palabra_a_palabra(palabras, dur)
    elif aj["subs"] == "si":
        subs = subtitulos([{**p, "a": p["a"] + desde, "b": p["b"] + desde} for p in palabras], dur)
        if dichos:   # estilo clip: la traducción del clip, frase a frase, encima de la costura
            subs = traduccion(dichos, desde, claves_de(guion)) + "\n" + subs
    videos = (f'<video id="base" class="clip" src="base.mp4" playsinline data-has-audio="true" data-start="{desde:.3f}" '
              f'data-duration="{medidas["duracion"]:.3f}" data-track-index="0"></video>')
    if desde:   # arriba el clip con su sonido; abajo tú escuchándolo, sin sonido
        videos = (f'<video id="clip" class="clip" src="clip.mp4" playsinline data-has-audio="true" data-start="0" '
                  f'data-duration="{desde:.3f}" data-track-index="1"></video>\n' + videos)
        if (dir_ / "reaccion.mp4").exists():
            videos = (f'<video id="reaccion" class="clip" src="reaccion.mp4" playsinline muted data-has-audio="false" '
                      f'data-start="0" data-duration="{desde:.3f}" data-track-index="0"></video>\n' + videos)
    js = (KIT / "motor.js").read_text(encoding="utf-8")
    pagina = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=1080, height=1920">
<title>{html.escape(nombre)}</title>
<style>
{css}
#root {{ --velo: {aj['velo']}; --sub-y: {aj['sub-y']}px; --cara-y: {aj['cara-y']}px; --arriba: {aj['arriba']}px;
  --costura: {aj['costura']}px; --encuadre: {aj['encuadre']}%; --clip-y: {aj['clip-y']}px; }}
</style>
</head>
<body>
<div id="root" data-composition-id="formula" data-start="0" data-width="1080" data-height="1920" data-duration="{dur:.3f}">
{videos}
{pista}
<div id="velo"></div>
{guion}
{subs}
</div>
<script src="kit/gsap.min.js"></script>
<script>
{js}
</script>
</body>
</html>
"""
    (dir_ / "index.html").write_text(pagina, encoding="utf-8")
    return dir_, guion, bloques, dur, suena, aj


def vlog(args):
    """Estilo vlog (vlog.py): las tomas del día, el corte sin voz y, con tu voz, la base para armar."""
    dir_ = carpeta(args.nombre)
    dir_.mkdir(parents=True, exist_ok=True)
    if args.clips:
        print("Tomas:", *dia.tomas(dir_, args.clips), sep="\n")
        print(f"\nMíralas y escribe {dir_ / 'montaje.json'}; luego: formula vlog {args.nombre} --montar")
    if args.montar:
        _, para_voz, dur, guia = dia.montar(dir_)
        print(*guia, sep="\n")
        print(f"\n{len(guia)} planos, {dur:.1f} s → {para_voz}\nGraba tu voz encima (CapCut o una nota de voz con el vídeo sonando) y: "
              f"formula vlog {args.nombre} --voz <fichero>")
    if args.voz:
        base, voz, sobra = dia.con_voz(dir_, Path(args.voz).expanduser(), args.desde)
        if sobra > 0.3:
            print(f"⚠️  la voz dura {sobra:.1f} s más que el corte: se corta ahí. O grabas más corto o se alargan los planos")
        print("Transcribiendo tu voz (Whisper, en tu ordenador)…")
        palabras = corte.transcribir(voz, args.pista)
        for n, p in enumerate(palabras):
            p["n"] = n
        dur = duracion_de(base)
        palabras = [p for p in palabras if p["a"] < dur]
        (dir_ / "palabras.json").write_text(json.dumps(palabras, ensure_ascii=False), encoding="utf-8")
        apuntar(dir_, duracion=dur, luz_arriba=round(luz_de_arriba(base, dur)), velo=0)
        escribir_frases(palabras, dir_)
        guion = dir_ / "guion.html"
        if not guion.exists():   # el título del principio es la portada: lo escribe Claude (estilos.md, «vlog»)
            guion.write_text(f'<!-- ajustes: estilo=vlog sub-y=930 sonido=0 -->\n<!-- Vlog «{args.nombre}». -->\n'
                             '<div class="gancho" data-a="0" data-b="2.6"><span class="dia">Día 1:</span> '
                             'la idea con su palabra en <i class="acento">cursiva</i></div>\n', encoding="utf-8")
        print(f"\nListo: {dur:.1f} s, {len(palabras)} palabras → {dir_ / 'frases.txt'}\n"
              f"Ahora: el título en guion.html, formula musica {args.nombre} vlog, formula armar, formula foto")


def armar(args):
    dir_, guion, bloques, dur, suena, aj = construir(args.nombre)
    print(f"{sum('beat' in c.split() for _, _, c in bloques)} bloques en {dur:.1f} s · {len(suena)} sonidos")
    for aviso in avisos(guion, bloques, dur, dir_, aj):
        print("⚠️ ", aviso)
    validar(dir_)


RUIDO = {"studio_missing_editable_id", "composition_file_too_large", "timeline_track_too_dense",
         "nested_structure_needs_subcomposition"}   # consejos para proyectos de varias escenas; aquí no aplican


def validar(dir_):
    """La puerta de HyperFrames (estructura, errores al cargar, texto que se sale, contraste)."""
    r = subprocess.run([str(HF), "check", str(dir_), "--json"], env=ENTORNO, capture_output=True, text=True)
    try:
        informe = json.loads(r.stdout[r.stdout.index("{"):r.stdout.rindex("}") + 1])
    except ValueError:
        sys.exit("HyperFrames no ha podido validar:\n" + (r.stdout + r.stderr)[-1500:])
    n = 0
    for parte in ("lint", "runtime", "layout", "contrast"):
        for h in informe[parte]["findings"]:
            if h["code"] in RUIDO or h["severity"] == "info":
                continue
            if h["code"] == "text_occluded" and "rueda" in h.get("selector", ""):   # las cifras de la rueda esperan escondidas
                continue
            n += 1
            donde = f" [{h['time']} s]" if "time" in h else ""
            print(f"{'❌' if h['severity'] == 'error' else '⚠️ '} {parte}{donde} {h['code']} "
                  f"{h.get('selector', '')}: {h['message'][:220]}")
    print("Validado sin avisos." if not n else f"{n} avisos de HyperFrames.")


# ── captura, foto, render, a-fotos ──────────────────────────────────────────

def captura(args):
    """La captura de una web (o la imagen con la que se anuncia) en capturas/FICHERO.png, lista
    para `<img class="captura">`. Sale de un Chrome sin ventana: el tuyo ni se toca."""
    from PIL import Image
    destino = carpeta(args.nombre) / "capturas" / f"{args.fichero}.png"
    destino.parent.mkdir(parents=True, exist_ok=True)
    chromes = sorted(Path.home().glob(".cache/*/chrome*/**/chrome-headless-shell"))
    if not chromes:
        sys.exit("No encuentro el Chrome de HyperFrames (~/.cache/hyperframes): vuelve a pasar herramientas/instalar.sh")
    pedido = {"chrome": str(chromes[-1]), "url": args.url, "destino": str(destino), "ancho": args.ancho,
              "alto": args.alto, "selector": args.selector, "recorte": args.recorte, "entera": args.entera,
              "portada": args.portada, "oscuro": args.oscuro, "quita": args.quita, "espera": args.espera,
              "idioma": config.marca()["idioma"]}
    subprocess.run(["node", str(AQUI / "captura.js"), json.dumps(pedido)],
                   env={**ENTORNO, "NODE_PATH": str(ICONOS)}, check=True)
    imagen = Image.open(destino)
    if imagen.format != "PNG":   # la portada de una web suele venir en JPG o WebP
        imagen.convert("RGB").save(destino, "PNG")
    with open(destino.parent / "fuentes.txt", "a", encoding="utf-8") as f:   # de qué página salió cada una
        f.write(f"{destino.name}  ←  {args.url}\n")
    print(f"  {destino}  ({imagen.width}x{imagen.height})")


def imagen(args):
    """La imagen de verdad de algo (una cara, un meme, un producto) buscada en la web: las N primeras en
    capturas/FICHERO-1.png… y una hoja numerada para elegir. En vez de un emoji o un icono, lo real.
    Google pide captcha al Chrome sin ventana; Bing no."""
    import io, urllib.parse, urllib.request
    from PIL import Image, ImageDraw
    navegador = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"}
    pide = lambda url: urllib.request.urlopen(urllib.request.Request(url, headers=navegador), timeout=20).read()
    pagina = pide("https://www.bing.com/images/search?first=1&q=" + urllib.parse.quote(args.busqueda)).decode("utf-8", "ignore")
    resultados = [json.loads(html.unescape(m)) for m in re.findall(r'class="iusc"[^>]*m="([^"]+)"', pagina)]
    destino = carpeta(args.nombre) / "capturas"
    destino.mkdir(parents=True, exist_ok=True)
    bajadas = []
    for r in resultados:
        if len(bajadas) == args.n:
            break
        try:   # un GIF se queda en su primer fotograma; las que no bajan, fuera
            img = Image.open(io.BytesIO(pide(r["murl"]))).convert("RGB")
        except Exception:
            continue
        if min(img.size) < 200:
            continue
        fichero = destino / f"{args.fichero}-{len(bajadas) + 1}.png"
        img.save(fichero, "PNG")
        bajadas.append((fichero, img))
        with open(destino / "fuentes.txt", "a", encoding="utf-8") as f:
            f.write(f"{fichero.name}  ←  {r['murl']}  ({r.get('purl', '')})\n")
    if not bajadas:
        sys.exit(f"Sin imágenes para «{args.busqueda}»: prueba otras palabras")
    hoja = Image.new("RGB", (360 * len(bajadas), 400), "white")
    for k, (fichero, img) in enumerate(bajadas):
        tamano = f"{img.width}x{img.height}"
        img.thumbnail((350, 350))
        hoja.paste(img, (360 * k + 5, 45))
        ImageDraw.Draw(hoja).text((360 * k + 10, 10), f"{k + 1}  {tamano}", fill="black")
        print(f"  {fichero}")
    hoja.save(destino / f"{args.fichero}-hoja.jpg", quality=85)
    print(f"Mira {destino / (args.fichero + '-hoja.jpg')} y usa la buena; las demás se borran.")


def foto(args):
    """Fotogramas sueltos, juntos en una hoja para leerlos de un vistazo. En rojo, lo que tapa Instagram."""
    from PIL import Image, ImageDraw
    dir_, dur = (lambda r: (r[0], r[3]))(construir(args.nombre))
    tiempos = args.tiempos or [f"{k * args.cada:.1f}" for k in range(int(dur / args.cada) + 1)]
    destino = dir_ / "fotos"
    shutil.rmtree(destino, ignore_errors=True)
    for viejo in dir_.glob("hoja*.jpg"):
        viejo.unlink()
    subprocess.run([str(HF), "snapshot", str(dir_), "--at", ",".join(tiempos), "--no-end",
                    "--describe", "false", "-o", str(destino)], env=ENTORNO, check=True, capture_output=True)
    fotos = sorted(destino.glob("*.png"), key=lambda f: int(re.search(r"\d+", f.name).group()))
    # Con --cada, hojas de 10 (5 × 2) para leerlas todas; si no, una fila
    por_hoja, cols = (10, 5) if not args.tiempos else (len(fotos), len(fotos))
    ancho = 1080 if len(fotos) == 1 else (360 if not args.tiempos else 540)
    alto = ancho * 16 // 9
    hojas = [fotos[k:k + por_hoja] for k in range(0, len(fotos), por_hoja)]
    for n, grupo in enumerate(hojas, 1):
        filas = -(-len(grupo) // cols)
        hoja = Image.new("RGB", (ancho * min(cols, len(grupo)), alto * filas))
        tinta = ImageDraw.Draw(hoja, "RGBA")
        for i, f in enumerate(grupo):
            x, y = (i % cols) * ancho, (i // cols) * alto
            hoja.paste(Image.open(f).convert("RGB").resize((ancho, alto), Image.LANCZOS), (x, y))
            if not args.limpia:
                for x0, y0, x1, y1 in ZONAS_IG.values():
                    tinta.rectangle([x + x0 * ancho // 1080, y + y0 * ancho // 1080, x + x1 * ancho // 1080 - 1,
                                     y + y1 * ancho // 1080 - 1], fill=(255, 0, 0, 70), outline=(255, 0, 0, 255))
        nombre = "hoja.jpg" if len(hojas) == 1 else f"hoja-{n:02d}.jpg"
        hoja.save(dir_ / nombre, quality=88)
        primero, ultimo = tiempos[fotos.index(grupo[0])], tiempos[fotos.index(grupo[-1])]
        print(dir_ / nombre, "←", f"{primero} a {ultimo} s")


def para_instagram(origen, destino):
    """El render final de HyperFrames sale a ~23 Mb/s y Meta corta en 25: se deja en 10, que es
    más de lo que Instagram enseña."""
    subprocess.run([FFMPEG, "-v", "error", "-y", "-i", str(origen), "-c:v", "libx264", "-preset", "medium",
                    "-b:v", "10M", "-maxrate", "12M", "-bufsize", "20M", "-pix_fmt", "yuv420p",
                    "-c:a", "copy", "-movflags", "+faststart", str(destino)], check=True)


OJOS_ABIERTOS = 0.22   # alto/ancho del ojo (ojos.swift). Mirando a cámara: ~0,28. Un parpadeo: menos de 0,2


def hay_swift():
    return sys.platform == "darwin" and shutil.which("swift") is not None


def ojos_abiertos(base, a, b):
    """[(segundo, apertura, giro)] de 0,1 en 0,1 s entre a y b. La apertura de un fotograma es la peor de él
    y sus dos vecinos: así no se elige el que está pegado a un parpadeo. Giro 0 = mirando a cámara."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run([FFMPEG, "-v", "error", "-ss", f"{a:.2f}", "-t", f"{max(b - a, 0.3):.2f}", "-i", str(base),
                        "-vf", "fps=10", f"{tmp}/%03d.png"], check=True)
        fotos = sorted(Path(tmp).glob("*.png"))
        sale = subprocess.run(["swift", str(Path(__file__).parent / "ojos.swift"), *map(str, fotos)],
                              capture_output=True, text=True, check=True).stdout
    filas = [l.split("\t") for l in sale.splitlines() if "\t" in l]
    crudo = [float(f[1]) for f in filas]
    return [(a + i / 10, min(crudo[max(i - 1, 0): i + 2]), float(f[2])) for i, f in enumerate(filas)]


def mejor_portada(medidas):
    """El fotograma de la portada: ojos abiertos y de frente; entre esos, el más abierto. Si no hay
    ninguno así, el más abierto (y se avisa)."""
    return max(medidas, key=lambda m: (m[1] >= OJOS_ABIERTOS and m[2] == 0, m[1]))


def hacer_portada(nombre, en=None):
    """La portada: SOLO el gancho sobre un fotograma tuyo con los ojos abiertos, sin nada en la cara. El primer
    fotograma del vídeo suele salir a medio parpadeo o con un gráfico en la frente: en el perfil se ve fatal."""
    dir_ = carpeta(nombre)
    guion = (dir_ / "guion.html").read_text(encoding="utf-8")
    gancho = re.search(r'<div[^>]*class="gancho[^"]*"[^>]*>.*?</div>', guion, flags=re.S)
    if not gancho:
        sys.exit("No hay gancho en el guion: sin gancho no hay portada.")
    a, b = (float(re.search(rf'data-{k}="([\d.]+)"', gancho.group(0)).group(1)) for k in "ab")
    estilo = leer_ajustes(guion)["estilo"]
    if en is None and not hay_swift():   # sin macOS no hay medidor de ojos: el medio del gancho, y se mira a mano
        en = (a + b) / 2
        print(f"⚠️  sin macOS no se miden los ojos: portada en el {en:.1f} s. Mírala y, si sale con los ojos cerrados, "
              f"`formula portada {nombre} --en SEGUNDO`")
    if en is None:   # en el estilo clip, mientras está el gancho tú eres la toma de abajo, escuchando
        medidas = ojos_abiertos(dir_ / ("reaccion.mp4" if estilo == "clip" else "base.mp4"), a, b - 0.2)
        en, apertura, giro = mejor_portada(medidas)
        print(f"   portada en {en:.1f} s (ojos {apertura:.2f}, giro {giro:.2f}; de {min(m[1] for m in medidas):.2f} a "
              f"{max(m[1] for m in medidas):.2f} en el gancho)")
        if apertura < OJOS_ABIERTOS or giro:
            print(f"⚠️  en todo el gancho no hay un fotograma con los ojos abiertos (mínimo {OJOS_ABIERTOS}) y de frente: "
                  f"se mira a mano y se elige con `formula portada {nombre} --en SEGUNDO`")
    ajustes = re.search(r"<!--\s*ajustes:.*?-->", guion, flags=re.S)
    solo = f"{nombre}/_portada"   # un vídeo aparte con el gancho y nada más
    shutil.rmtree(carpeta(solo), ignore_errors=True)
    carpeta(solo).mkdir()
    for f in ("medidas.json", "palabras.json"):
        shutil.copy(dir_ / f, carpeta(solo) / f)
    for f in ("base.mp4", "clip.mp4", "reaccion.mp4", "capturas"):   # capturas: el logo del gancho
        if (dir_ / f).exists():
            (carpeta(solo) / f).symlink_to(dir_ / f)
    # sin subtítulos y con los estilos propios del guion (la letra del gancho), para que salga igual que en el vídeo
    ajustes = ajustes.group(0).replace("-->", " subs=no -->") if ajustes else "<!-- ajustes: subs=no -->"
    estilos = "\n".join(re.findall(r"<style>.*?</style>", guion, flags=re.S))
    # en partida y clip el gancho es un título pequeño: la portada lleva también lo que empieza con él
    # (la animación, quién habla en el clip), quieto (data-queda) y no a medio irse. Sin ella sale el panel vacío
    debajo = [m.group(0).replace("<section", "<section data-queda", 1)
              for m in re.finditer(r'<section[^>]*\bclass="beat[^"]*"[^>]*>.*?</section>', guion, flags=re.S)
              if estilo != "encima" and float(re.search(r'data-a="([\d.]+)"', m.group(0)).group(1)) == a]
    (carpeta(solo) / "guion.html").write_text("\n".join([ajustes, estilos, gancho.group(0), *debajo]), encoding="utf-8")
    construir(solo)
    subprocess.run([str(HF), "snapshot", str(carpeta(solo)), "--at", f"{en:.2f}", "--no-end", "--describe", "false",
                    "-o", str(carpeta(solo) / "fotos")], env=ENTORNO, check=True, capture_output=True)
    destino = SALIDA / f"{nombre}.portada.png"
    shutil.copy(next((carpeta(solo) / "fotos").glob("frame-*.png")), destino)
    shutil.rmtree(carpeta(solo))
    print(f"  {destino}")
    return destino


def portada(args):
    hacer_portada(args.nombre, args.en)


def revisar_final(video):
    """Lo que se mira en el MP4 de verdad: volumen, primer fotograma, imagen congelada y silencio al final.
    Avisa; lo demás se mira en los fotogramas."""
    r = subprocess.run([FFMPEG, "-hide_banner", "-nostats", "-i", str(video),
                        "-af", "ebur128=peak=true,silencedetect=n=-45dB:d=1",
                        "-vf", "blackdetect=d=0.05:pix_th=0.08,freezedetect=n=0.002:d=2.5", "-f", "null", "-"],
                       capture_output=True, text=True)
    log, dur, mal = r.stderr, duracion_de(video), []
    volumen = re.findall(r"I:\s+(-?[\d.]+) LUFS", log)
    pico = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", log)
    if volumen and not -16.5 <= float(volumen[-1]) <= -12:
        mal.append(f"volumen {volumen[-1]} LUFS (va a -14)")
    if pico and float(pico[-1]) > -0.5:
        mal.append(f"pico de {pico[-1]} dB: puede saturar")
    if re.search(r"black_start:0(\.0+)?\b", log):
        mal.append("el primer fotograma sale negro")
    for a in re.findall(r"freeze_start: ([\d.]+)", log):
        mal.append(f"imagen congelada desde {float(a):.1f} s")
    silencios = re.findall(r"silence_start: ([\d.]+)", log)
    if silencios and float(silencios[-1]) < dur - 0.2 and "silence_end" not in log.split(f"silence_start: {silencios[-1]}")[-1]:
        mal.append(f"silencio desde {float(silencios[-1]):.1f} s hasta el final ({dur:.1f} s)")
    print("  revisión: " + ("bien" if not mal else "⚠️  " + "; ".join(mal)), flush=True)
    return mal


def render(args):
    dir_ = construir(args.nombre)[0]
    SALIDA.mkdir(parents=True, exist_ok=True)
    final = SALIDA / f"{args.nombre}{'-borrador' if args.borrador else ''}.mp4"
    crudo = final if args.borrador else dir_ / "render.mp4"
    subprocess.run([str(HF), "render", str(dir_), "-o", str(crudo), "--fps", "30",
                    "--quality", "draft" if args.borrador else "delivery"], env=ENTORNO, check=True)
    if not args.borrador:
        para_instagram(crudo, final)
        crudo.unlink()
        revisar_final(final)
        hacer_portada(args.nombre)
    print(f"\n  {final}  ({duracion_de(final):.1f} s)")
    if args.borrador:
        abrir(final)


# Pruebas: copias que Instagram enseña solo a quien no te sigue (Reels de prueba). Cada una cambia lo que se
# cambiaría a mano en una app: velocidad (la voz no cambia de tono), color, estilo de subtítulos y de gancho, y un
# poco la altura. 8, 7, 5, 4 y 3 opciones: dentro de un mismo vídeo no se repite una combinación. Se baja, nunca se
# sube: arriba está lo que tapa Instagram.
VELOCIDADES = [1.03, 1.04, 1.06, 1.07, 1.08, 1.09, 1.10, 1.05]
COLORES = {
    "cálido": "colorbalance=rs=.05:gs=.01:bs=-.05",
    "frío": "colorbalance=rs=-.04:bs=.05",
    "contraste": "eq=contrast=1.08:saturation=1.12",
    "suave": "eq=contrast=.95:saturation=.92:brightness=.02",
    "vivo": "eq=saturation=1.2",
    "oscuro": "eq=contrast=1.05:brightness=-.03:saturation=.9",
    "dorado": "colorbalance=rm=.04:gm=.02:bm=-.05,eq=saturation=1.05",
}
CAJA_SUB = "-webkit-text-stroke:0; text-shadow:none; padding:6px 16px; border-radius:12px; width:fit-content; max-width:640px; left:0; right:0; margin-left:auto; margin-right:auto;"
SUBS_TRIAL = {
    "contorno": "",
    "caja negra": "background:rgba(0,0,0,.78); " + CAJA_SUB,
    "amarillo": "color:#FFE14D;",
    "caja blanca": "background:#fff; color:#111; " + CAJA_SUB,
    "mayúsculas": "text-transform:uppercase; font-weight:800; font-size:40px; letter-spacing:.01em;",
}
GANCHOS_TRIAL = {
    "letra": "",
    "caja blanca": "background:#fff; color:#111; -webkit-text-stroke:0; text-shadow:none; padding:14px 8px 6px; border-radius:20px;",
    "caja negra": "background:rgba(0,0,0,.82); -webkit-text-stroke:0; padding:14px 8px 6px; border-radius:20px;",
    "pequeño": "font-size:96px !important;",
}
BAJA_TRIAL = [0, 28, 56]
# En «partida» los subtítulos son tinta sobre papel: el amarillo o el contorno negro no se leen. La clave no se toca.
CAJA_COSTURA = "border-radius:16px; width:fit-content; margin:0 auto; padding:0 24px;"
SUBS_TRIAL_REMOTION = {
    "costura": "",
    "caja blanca": "background:#fff; " + CAJA_COSTURA,
    "mayúsculas": "text-transform:uppercase; font-weight:800; letter-spacing:.01em;",
    "caja tinta": "background:var(--tinta); color:#fff; " + CAJA_COSTURA,
    "grande": "font-size:50px;",
}
GANCHOS_TRIAL_REMOTION = {
    "letra": "",
    "caja blanca": "background:#fff; padding:18px 10px 12px; border-radius:20px;",
    "tinta": "color:var(--tinta);",
    "pequeño": "font-size:70px !important;",
}
# En clip el gancho es el título blanco sobre negro encima del clip: sin «tinta» y sin bajarlo, que pisaría el clip
GANCHOS_TRIAL_CLIP = {
    "letra": "",
    "caja blanca": "background:#fff; color:#111; padding:18px 10px 12px; border-radius:20px;",
    "mayúsculas": "text-transform:uppercase; font-size:54px !important;",
    "pequeño": "font-size:50px !important;",
}


# Una prueba al día, a la primera de estas horas que tengas libre. Medido sobre 52 pruebas: 9 copias al día del mismo
# vídeo bajaron la prueba típica de unas 3.400 vistas a 190 en una semana (algunas a 0), y por franja la media mañana
# (11-13 h) fue la mejor y la tarde (~17:45) la peor. Mantén las mismas horas unas dos semanas, mide y mueve la peor.
HORAS_DE_PRUEBA = ["11:00", "13:00", "16:00", "19:00", "21:00"]


def dias_de_prueba(n, dia=None):
    """Una prueba al día, n días seguidos desde `dia` (por defecto, mañana), a la primera de HORAS_DE_PRUEBA. Varias
    copias del mismo vídeo el mismo día se quedan en 0 visualizaciones, y eso puede costarte alcance."""
    import datetime as dt
    from zoneinfo import ZoneInfo
    ahora = dt.datetime.now(ZoneInfo(config.marca()["zona_horaria"]))
    primero = dt.date.fromisoformat(dia) if dia else (ahora + dt.timedelta(days=1)).date()
    return [((primero + dt.timedelta(days=k)).isoformat(), HORAS_DE_PRUEBA[0]) for k in range(n)]


# El gancho a la vista del vídeo (el de solo-portada no sale en el vídeo). Cada copia lleva otro titular, que tú
# apruebas antes, sin grabar nada más; si el vídeo no tiene gancho a la vista, se le pone los primeros 2,6 s
GANCHO_A_LA_VISTA = re.compile(r'(<div class="gancho(?![^"]*solo-portada)[^"]*"[^>]*>).*?(</div>)', re.S)
# Un vídeo que abre con su gráfico arriba no lleva titular encima: lo taparía. Solo cambia el estilo
ABRE_CON_GRAFICO = re.compile(r'<section class="beat"[^>]*data-a="0(\.0+)?"')


def admite_titular(guion):
    return bool(GANCHO_A_LA_VISTA.search(guion)) or not ABRE_CON_GRAFICO.search(guion)


def con_gancho(guion, texto):
    if texto is None:
        return guion
    texto = texto.replace(" / ", "<br>")
    if GANCHO_A_LA_VISTA.search(guion):
        return GANCHO_A_LA_VISTA.sub(lambda m: m.group(1) + texto + m.group(2), guion, count=1)
    return guion + f'\n<div class="gancho" data-a="0" data-b="2.6">{texto}</div>\n'


def pruebas(args):
    """Las copias de prueba de un reel ya terminado y aprobado (ver .claude/skills/pruebas/SKILL.md)."""
    dir_ = carpeta(args.nombre)
    original, pie = SALIDA / f"{args.nombre}.mp4", SALIDA / f"{args.nombre}.pie.txt"
    if not original.exists() or not pie.exists():
        sys.exit(f"Falta {original.name} o su pie ({pie.name}): las copias salen del vídeo final ya aprobado.")
    tags = args.hashtags.split()
    if not 5 <= len(tags) <= 10 or not all(re.fullmatch(r"#[\w]+", t) for t in tags):
        sys.exit('--hashtags: de 5 a 10, del tema del vídeo y sin los de alcance (#viral, #fyp): "#claudeai #ia …"')
    texto = pie.read_text(encoding="utf-8").strip()
    # Grabado en piezas (piezas.py): cada copia es otra combinación de gancho y cuerpo, con el titular de su gancho
    if (dir_ / "guion-piezas.html").exists():
        piezas.escribir_guiones(dir_)
    medidas = json.loads((dir_ / "medidas.json").read_text())
    combos = medidas.get("combos", ["A1"])
    orden = piezas.orden_pruebas(combos, args.desde + args.n)
    guion = (dir_ / "guion.html").read_text(encoding="utf-8")
    titulares = [None] * (args.desde + args.n)
    fichero_ganchos = dir_ / "ganchos-prueba.txt"
    if len(combos) > 1 and not fichero_ganchos.exists():
        print(f"  grabado en piezas: las copias son {', '.join(orden[args.desde:])}, cada una con su gancho", flush=True)
    elif admite_titular(guion):
        if not fichero_ganchos.exists():
            sys.exit(f"Falta {fichero_ganchos}: un titular por copia, una línea cada uno («/» parte la línea), "
                     "aprobados antes (ver .claude/skills/pruebas/SKILL.md)")
        titulares = [l.strip() for l in fichero_ganchos.read_text(encoding="utf-8").splitlines() if l.strip()]
        if len(titulares) < args.desde + args.n:
            sys.exit(f"{fichero_ganchos.name} trae {len(titulares)} titulares y hacen falta {args.desde + args.n}")
    else:
        print("  abre con su gráfico arriba: sin titular nuevo, cada copia cambia solo el estilo", flush=True)
    estilo = leer_ajustes(guion)["estilo"]
    partida_ = estilo == "partida"
    subs_, ganchos_ = {"partida": (SUBS_TRIAL_REMOTION, GANCHOS_TRIAL_REMOTION),
                       "clip": (SUBS_TRIAL, GANCHOS_TRIAL_CLIP)}.get(estilo, (SUBS_TRIAL, GANCHOS_TRIAL))
    destino = SALIDA / "pruebas"
    destino.mkdir(exist_ok=True)
    hechas = []
    for i in range(args.desde, args.desde + args.n):
        # +1: la combinación 0 sería la del original (la primera copia solo cambiaría el color)
        sub_, gancho = list(subs_)[(i + 1) % 5], list(ganchos_)[(i + 1) % 4]
        color, vel, baja = list(COLORES)[i % 7], VELOCIDADES[i % 8], BAJA_TRIAL[i % 3]
        copia, combo = f"{args.nombre}/_prueba-{i}", orden[i]
        origen, cual = piezas.carpeta_de(dir_, combo, combos), f" ({combo})" if len(combos) > 1 else ""
        shutil.rmtree(carpeta(copia), ignore_errors=True)
        carpeta(copia).mkdir()
        for f in dir_.iterdir():   # lo que el guion pueda nombrar (base, capturas, música), enlazado y no copiado
            if f.name not in ("guion.html", "guion-piezas.html", "index.html", "sonidos.wav", "kit", "render.mp4") and not f.name.startswith("_"):
                (carpeta(copia) / f.name).symlink_to(origen / f.name if f.name in ("base.mp4", "palabras.json", "medidas.json") else f)
        if origen != dir_ and medidas.get("musica"):   # la canción, cortada al largo de esta combinación
            (carpeta(copia) / "musica.wav").unlink(missing_ok=True)
            musica.recortar(carpeta(copia), medidas["musica"])
        espejo = i % 2 == 1   # las impares, con tu cámara en espejo: otro vídeo más para Instagram
        for f in ("base.mp4", "reaccion.mp4") if espejo else ():   # solo tu cámara: el clip de otro, los gráficos y el texto, al derecho
            if (enlace := carpeta(copia) / f).exists():
                fuente = enlace.resolve()
                enlace.unlink()
                subprocess.run([FFMPEG, "-v", "error", "-y", "-i", str(fuente), "-vf", "hflip", "-c:v", "libx264",
                                "-preset", "veryfast", "-crf", "16", "-g", "30", "-keyint_min", "30", "-pix_fmt", "yuv420p",
                                "-c:a", "copy", str(enlace)], check=True)
        sub_css = f"#root .costura:not(.clave) {{ {subs_[sub_]} }}" if partida_ else f"#root .sub {{ {subs_[sub_]} margin-top:{baja}px; }}"
        retoque = (f"<style>\n{sub_css}\n#root .gancho {{ {ganchos_[gancho]} margin-top:{0 if estilo == 'clip' else baja}px; }}"
                   "\n</style>\n")
        (carpeta(copia) / "guion.html").write_text(con_gancho((origen / "guion.html").read_text(encoding="utf-8"), titulares[i])
                                                   + "\n" + retoque, encoding="utf-8")
        construir(copia)
        crudo = carpeta(copia) / "render.mp4"
        subprocess.run([str(HF), "render", str(carpeta(copia)), "-o", str(crudo), "--fps", "30", "--quality", "delivery"],
                       env=ENTORNO, check=True, capture_output=True)
        largo = duracion_de(crudo)
        final = destino / f"{args.nombre}-prueba-{i}.mp4"
        # Fichero nuevo y sin los datos del original; 10 Mb/s como para_instagram
        subprocess.run([FFMPEG, "-v", "error", "-y", "-i", str(crudo), "-vf", f"setpts=PTS/{vel},{COLORES[color]}",
                        "-af", f"atempo={vel}", "-c:v", "libx264", "-preset", "medium", "-b:v", "10M", "-maxrate", "12M",
                        "-bufsize", "20M", "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                        "-map_metadata", "-1", "-movflags", "+faststart", str(final)], check=True)
        shutil.copy(SALIDA / f"{args.nombre}.portada.png", destino / f"{args.nombre}-prueba-{i}.portada.png")
        k = i % len(tags)
        (destino / f"{args.nombre}-prueba-{i}.pie.txt").write_text(
            f"{texto}\n\n{' '.join((tags[k:] + tags[:k])[:5])}\n", encoding="utf-8")
        if abs(duracion_de(final) - largo / vel) > 0.3:   # dura lo que toca a su velocidad
            sys.exit(f"{final.name} dura {duracion_de(final):.1f} s y a {vel}× tendría que durar {largo / vel:.1f}")
        shutil.rmtree(carpeta(copia))
        hechas.append(final)
        print(f"  {final.name}{cual}: «{titulares[i] or 'su gancho'}», {vel}×, {color}, subtítulos «{sub_}», gancho «{gancho}», "
              f"{baja} px más abajo{', en espejo' if espejo else ''}", flush=True)
    # La hoja para mirarlas: el gancho (1 s) y un subtítulo (la mitad) de cada una, en dos filas
    hoja = destino / f"{args.nombre}-pruebas.jpg"
    entradas = []
    for t in (1.0, None):
        for f in hechas:
            entradas += ["-ss", f"{t if t else duracion_de(f) / 2:.2f}", "-i", str(f)]
    n = len(hechas)
    escala = "".join(f"[{j}:v]scale=270:480[v{j}];" for j in range(2 * n))
    filas = "".join(f"[v{j}]" for j in range(n)) + f"hstack=inputs={n}[a];" if n > 1 else "[v0]null[a];"
    filas += "".join(f"[v{j}]" for j in range(n, 2 * n)) + (f"hstack=inputs={n}[b];" if n > 1 else "null[b];")
    subprocess.run([FFMPEG, "-v", "error", "-y", *entradas, "-filter_complex", escala + filas + "[a][b]vstack",
                    "-frames:v", "1", "-q:v", "3", str(hoja)], check=True)
    cuando = dias_de_prueba(args.desde + args.n, args.dia)
    horario = destino / f"{args.nombre}-pruebas-horario.txt"
    lineas = [f"{args.nombre}-prueba-{i}.mp4  {cuando[i][0]} {cuando[i][1]}" + (f"  ({orden[i]})" if len(combos) > 1 else "")
              for i in range(args.desde, args.desde + args.n)]
    horario.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"\n  {n} copias en {destino}\n  hoja: {hoja}\n\nCuándo sale cada una (Reel de prueba, en manual; una al día):")
    print("\n".join("  " + l for l in lineas))
    print(f"  → {horario}")


def abrir(video):
    """Te lo pone delante y sonando. Cierra antes el borrador anterior: QuickTime se queda con el viejo abierto y
    parece que no ha cambiado nada."""
    if sys.platform != "darwin":
        subprocess.run(["xdg-open", str(video)], capture_output=True)
        return
    guion = f'''
tell application "QuickTime Player"
  try
    close (every document whose name is "{video.name}") saving no
  end try
  delay 0.5
  set d to open POSIX file "{video}"
  activate
  play d
end tell
tell application "System Events" to set frontmost of process "QuickTime Player" to true'''
    subprocess.run(["osascript", "-e", guion], capture_output=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="orden", required=True)
    p = sub.add_parser("preparar")
    p.add_argument("nombre")
    p.add_argument("--clips", help=f"carpeta con los clips (por defecto {ENTRADA})")
    p.add_argument("--pista", help='nombres propios que dices: "Claude, Notion, ChatGPT"')
    p.add_argument("--fuera", help='tomas que sobran: "57" quita la frase #57 de frases.txt; "83-91", esas palabras')
    p.add_argument("--silencio", type=float, default=corte.SILENCIO_MAX,
                   help="pausa más larga que se deja dentro de una frase (s); 0.25 deja las comas, 0.12 lo aprieta todo")
    p.add_argument("--cambia", help='palabras mal oídas: "Cloud=Claude;Notión=Notion". Una sola, por su número: "#185=programación."')
    p.add_argument("--tono", default="cálido", choices=list(corte.TONOS))
    p.add_argument("--piezas", help='grabado en piezas (piezas.py): "A=0,B=31,C=58,1=90,cierre=301,2=340", '
                   "la palabra de crudo.txt en que empieza cada una")
    p.set_defaults(f=preparar)
    p = sub.add_parser("vlog")
    p.add_argument("nombre")
    p.add_argument("--clips", help="la carpeta con los clips del día: una hoja por clip (tomas/)")
    p.add_argument("--montar", action="store_true", help="monta montaje.json → corte.mp4 y salida/NOMBRE-para-la-voz.mp4")
    p.add_argument("--voz", help="tu voz grabada sobre el corte: un audio o el vídeo exportado con la voz")
    p.add_argument("--desde", type=float, default=0.0, help="segundo del fichero de la voz en que empieza el corte")
    p.add_argument("--pista", help='nombres propios que dices')
    p.set_defaults(f=vlog)
    p = sub.add_parser("clip")
    p.add_argument("nombre")
    p.add_argument("fuente", help="la dirección del vídeo (X, YouTube, Instagram) o un fichero")
    p.add_argument("--trozos", help='segundos de fuente.txt que se quedan: "4.2-8.9,10.5-11.9"; sin él, solo transcribe')
    p.add_argument("--recorte", help='"x,y,ancho,alto" en px de fuente.jpg: sin subtítulos quemados ni logos del programa')
    p.add_argument("--reaccion", help="tu toma escuchando el clip, sin hablar: va abajo, sin sonido")
    p.add_argument("--desde", type=float, default=0.0, help="segundo de esa toma en que empiezas a escuchar")
    p.add_argument("--pista", help='nombres propios que se dicen en el clip')
    p.add_argument("--tono", default="cálido", choices=list(corte.TONOS), help="el de tu preparar, para la reacción")
    p.set_defaults(f=clip)
    p = sub.add_parser("captura")
    p.add_argument("nombre")
    p.add_argument("url")
    p.add_argument("fichero", help="nombre sin extensión: anuncio → capturas/anuncio.png")
    p.add_argument("--portada", action="store_true", help="la imagen con la que la web se anuncia (og:image), no una captura")
    p.add_argument("--selector", help='solo ese trozo de la página: "h1", "table", "article header"')
    p.add_argument("--recorte", help='"x,y,ancho,alto" en px de la página (los que imprime la captura anterior)')
    p.add_argument("--entera", action="store_true", help="la página de arriba abajo, para buscar el recorte")
    p.add_argument("--ancho", type=int, default=640, help="ancho de la ventana: estrecha, el texto sale grande (640)")
    p.add_argument("--alto", type=int, default=420)
    p.add_argument("--oscuro", action="store_true", help="en modo oscuro, si la web lo tiene")
    p.add_argument("--quita", help='selectores que estorban, además de los avisos de cookies: ".modal, #banner"')
    p.add_argument("--espera", type=float, default=1.0, help="segundos tras cargar, para lo que se pinta tarde")
    p.set_defaults(f=captura)
    p = sub.add_parser("imagen")
    p.add_argument("nombre")
    p.add_argument("busqueda", help='lo que buscarías en Google Imágenes: "meme de alguien asintiendo"')
    p.add_argument("fichero", help="nombre sin extensión: meme → capturas/meme-1.png…")
    p.add_argument("--n", type=int, default=6, help="cuántas bajar para elegir")
    p.set_defaults(f=imagen)
    p = sub.add_parser("musica")
    p.add_argument("nombre", nargs="?")
    p.add_argument("tipo", nargs="?", help="uno de los tipos de marca/musica.json; sin él, la lista")
    p.add_argument("--cancion", help="esa, sin rotar: el id de marca/musica.json")
    p.add_argument("--opciones", help='"id1,id2,…": una página para elegir, cada una en tu reel y sola')
    p.add_argument("--entra", type=float, default=0.0, help="segundo del vídeo en que empieza: antes, solo lo demás")
    p.add_argument("--anadir", help="añade a tu catálogo un fichero de audio o un enlace")
    p.add_argument("--tipos", help='con --anadir: "caso,utilidad"')
    p.add_argument("--titulo")
    p.add_argument("--artista")
    p.add_argument("--desde", type=float, default=0.0, help="con --anadir: el segundo donde la canción suena mejor")

    def _musica(a):
        if a.anadir:
            return musica.anadir(a.anadir, (a.tipos or "utilidad").split(","), a.titulo, a.artista, a.desde)
        if not a.nombre:
            return print(musica.lista())
        if a.opciones:
            return musica.opciones(carpeta(a.nombre), a.opciones.split(","), a.tipo or "utilidad")
        return musica.poner(carpeta(a.nombre), a.tipo, a.cancion, a.entra)
    p.set_defaults(f=_musica)
    p = sub.add_parser("pruebas")
    p.add_argument("nombre")
    p.add_argument("--hashtags", required=True, help="de 5 a 10, del tema: cada copia lleva 5, en otro orden")
    p.add_argument("--n", type=int, default=5, help="cuántas copias (5, una al día: 3 ganchos × 2 cuerpos, menos el normal)")
    p.add_argument("--desde", type=int, default=0, help="la primera combinación: para seguir una tanda cortada")
    p.add_argument("--dia", help="el día de la primera, AAAA-MM-DD (por defecto, mañana); las demás, un día cada una")
    p.set_defaults(f=pruebas)
    for nombre, f in (("armar", armar), ("render", render), ("foto", foto), ("portada", portada)):
        p = sub.add_parser(nombre)
        p.add_argument("nombre")
        p.set_defaults(f=f)
        if nombre == "render":
            p.add_argument("--borrador", action="store_true", help="rápido y feo, para ver el ritmo")
        if nombre == "portada":
            p.add_argument("--en", type=float, help="el segundo, si la que elige sola no vale")
        if nombre == "foto":
            p.add_argument("tiempos", nargs="*", help="segundos: 3.2 8 14.5")
            p.add_argument("--cada", type=float, default=0.5, help="sin tiempos: un fotograma cada tantos segundos, en hojas de 10")
            p.add_argument("--limpia", action="store_true", help="sin las zonas de Instagram en rojo")
    args = ap.parse_args()
    args.f(args)


if __name__ == "__main__":
    main()
