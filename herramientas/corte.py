"""El corte: junta tus clips, transcribe en local (Whisper), quita silencios, muletillas y tomas
repetidas, y deja el vídeo base sin texto con la voz a −14 LUFS. Lo usa formula.py (preparar, clip)."""
import json
import math
import re
import subprocess
from datetime import datetime

from config import FFMPEG, marca

VIDEO_EXT = {".mov", ".mp4", ".m4v"}
MULETILLAS = {"eh", "ehh", "ehm", "em", "emm", "mm", "mmm", "ah", "uh", "um", "hmm"}
PALABRAS_POR_LINEA = 4
HUECO_MAX = 0.35      # palabras más juntas que esto van en el mismo trozo (s)
MARGEN = 0.12         # aire alrededor de cada trozo antes de medir el audio (s)
SILENCIO_MAX = 0.12   # silencio más largo que se deja dentro de un trozo (s). 0,25 deja las comas
AIRE_ANTES = 0.04     # voz antes de la primera sílaba, para no comerse el ataque (s)
AIRE_DESPUES = 0.07   # cola después de la última, para no comerse la «s» final (s)
FUNDIDO = 0.012       # fundido en cada corte: sin él, cada corte suena a clic

# Tonos de color del vídeo (preparar --tono)
TONOS = {
    "sin tocar": "",
    "cálido": "eq=contrast=1.06:saturation=1.15:gamma=0.98,colorbalance=rs=0.03:bs=-0.03,",
    "frío": "eq=contrast=1.08:saturation=1.05,colorbalance=rs=-0.04:bs=0.05,",
    "cine": "eq=contrast=1.16:saturation=0.9:gamma=0.94,colorbalance=rm=0.04:bs=0.04:bh=-0.03,",
}


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


def fecha_grabacion(path):
    out = subprocess.run([FFMPEG, "-hide_banner", "-i", str(path)], capture_output=True, text=True).stderr
    m = re.search(r"creation_time\s*:\s*(\S+)", out)
    if m:
        try:
            return datetime.fromisoformat(m.group(1).replace("Z", "+00:00")).timestamp()
        except ValueError:
            pass
    return path.stat().st_mtime


def ordenar(clips):
    """Un número al principio del nombre manda («1 IMG_8581.MOV»); si no, la hora de grabación."""
    def clave(p):
        m = re.match(r"\s*(\d+)", p.name)
        return (0, int(m.group(1)), 0) if m else (1, 0, fecha_grabacion(p))
    return sorted(clips, key=clave)


def unir(clips, destino):
    """Todos a 1080x1920, 30 fps y audio 48 kHz, pegados en orden."""
    entradas, filtros = [], []
    for i, c in enumerate(clips):
        entradas += ["-i", str(c)]
        filtros.append(f"[{i}:v]scale=1080:1920:force_original_aspect_ratio=decrease,"
                       f"pad=1080:1920:(ow-iw)/2:(oh-ih)/2,fps=30,setsar=1[v{i}];"
                       f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo[a{i}]")
    pares = "".join(f"[v{i}][a{i}]" for i in range(len(clips)))
    grafo = ";".join(filtros) + f";{pares}concat=n={len(clips)}:v=1:a=1[v][a]"
    run([FFMPEG, "-y", *entradas, "-filter_complex", grafo, "-map", "[v]", "-map", "[a]",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-c:a", "pcm_s16le", str(destino)])


def juntar_cifras(palabras):
    """Whisper parte las cifras con punto o coma: «3» «.000.» → «3.000.». Se juntan en una palabra."""
    salida = []
    for p in palabras:
        if salida and re.fullmatch(r"\d+", salida[-1]["t"]) and re.match(r"[.,]\d", p["t"]):
            salida[-1] = {**salida[-1], "t": salida[-1]["t"] + p["t"], "b": p["b"]}
        else:
            salida.append(p)
    return salida


def transcribir(video, pista=None, idioma="marca"):
    """Palabra a palabra, con su segundo. `pista`: los nombres propios que dices («Claude, Notion»), para que
    los escriba bien. idioma=None: que lo adivine (el clip de otro). La primera vez baja el modelo (~1,5 GB)."""
    from faster_whisper import WhisperModel
    modelo = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")
    idioma = marca()["idioma"] if idioma == "marca" else idioma
    segmentos, _ = modelo.transcribe(str(video), language=idioma, word_timestamps=True, vad_filter=True,
                                     initial_prompt=pista)
    palabras = [{"t": w.word.strip(), "a": w.start, "b": w.end} for s in segmentos for w in s.words or []]
    return juntar_cifras([p for p in palabras if p["t"]])


def limpia(texto):
    return re.sub(r"[^\wáéíóúñü]", "", texto.lower())


def es_muletilla(texto):
    return limpia(texto) in MULETILLAS


def tramos_a_conservar(palabras, duracion):
    """Trozos con voz, sin muletillas y sin silencios largos."""
    tramos, tras_muletilla = [], False
    for p in palabras:
        if es_muletilla(p["t"]):
            tras_muletilla = True
            if tramos:
                tramos[-1][1] = min(tramos[-1][1], p["a"])
            continue
        a, b = max(0.0, p["a"] - MARGEN), min(duracion, p["b"] + MARGEN)
        if tras_muletilla and tramos:
            a = max(a, tramos[-1][1])
        if tramos and not tras_muletilla and a - tramos[-1][1] <= HUECO_MAX:
            tramos[-1][1] = max(tramos[-1][1], b)
        else:
            tramos.append([a, b])
        tras_muletilla = False
    return [tr for tr in tramos if tr[1] - tr[0] > 0.05]


def ajustar_a_la_voz(video, tramos, silencio=SILENCIO_MAX):
    """Recorta cada trozo al audio que de verdad suena (los tiempos de Whisper llegan y se van tarde):
    fuera el silencio al empezar y al acabar, y parte el trozo en cada pausa de más de `silencio`."""
    import numpy as np
    sr, paso = 16000, 160  # ventanas de 10 ms
    pcm = subprocess.run([FFMPEG, "-v", "error", "-i", str(video), "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
    n = len(x) // paso
    db = 20 * np.log10(np.sqrt((x[:n * paso].reshape(n, paso) ** 2).mean(1)) + 1e-9)
    # Voz = hasta 18 dB por debajo de tu voz normal en este vídeo. Más abajo: respiraciones y eco de la sala
    suena = db > np.percentile(db, 90) - 18
    # La cola de una palabra que se apaga suena por debajo de ese umbral y se perdía: se mide con uno 12 dB más
    # suave, siempre 8 dB por encima del ruido de la sala (en la calle no alarga nada)
    suave = db > max(np.percentile(db, 90) - 30, np.percentile(db, 20) + 8)

    # Si en el borde de una palabra aún suena (Whisper la da por acabada antes), el trozo sigue hasta que se
    # apaga: 0,3 s como mucho y sin pisar al de al lado. Si no, se come la última sílaba
    ampliados = []
    for k, (a, b) in enumerate(tramos):
        j0 = i0 = int(a * 100)
        j1 = i1 = min(n, int(b * 100) + 1)
        tope = min(n, i1 + 30, int(tramos[k + 1][0] * 100) if k + 1 < len(tramos) else n)
        while i1 < tope and suena[i1 - 1] and suena[i1]:
            i1 += 1
        suelo = max(0, i0 - 30, math.ceil(ampliados[-1][1] * 100) if ampliados else 0)
        while i0 > suelo and suena[i0] and suena[i0 - 1]:
            i0 -= 1
        ampliados.append([max(suelo / 100, i0 / 100 - AIRE_ANTES) if i0 < j0 else a,
                          min(tope / 100, i1 / 100 + AIRE_DESPUES) if i1 > j1 else b])
    tramos = ampliados

    salida = []
    for a, b in tramos:
        i0, i1 = int(a * 100), min(n, int(b * 100) + 1)
        idx = np.flatnonzero(suena[i0:i1]) + i0
        if not len(idx):
            continue
        ini = fin = idx[0]
        for k in idx[1:]:
            if (k - fin) / 100 > silencio:
                salida.append([ini / 100, (fin + 1) / 100])
                ini = k
            fin = k
        salida.append([ini / 100, (fin + 1) / 100])
    for k, seg in enumerate(salida):   # cada trozo acaba cuando la palabra deja de sonar de verdad: 0,4 s como mucho
        e = int(round(seg[1] * 100))
        tope = min(n, e + 40, int(salida[k + 1][0] * 100) if k + 1 < len(salida) else n)
        while e < tope and suave[e]:
            e += 1
        seg[1] = e / 100
    final = []
    for (a, b), (wa, wb) in zip(salida, [next(t for t in tramos if t[0] - 0.01 <= s[0] <= t[1]) for s in salida]):
        a, b = max(wa, a - AIRE_ANTES), b if b > wb else min(wb, b + AIRE_DESPUES)   # la cola suave no se recorta
        if final and a - final[-1][1] < 0.1:  # quitar menos de 0,1 s solo da un salto de imagen
            final[-1][1] = b
        else:
            final.append([a, b])
    return [t for t in final if t[1] - t[0] > 0.08]


def quitar_repetidas(palabras, minimo=8):
    """Si repites una toma, se queda la última. Una toma repetida es un trozo largo que vuelve a empezar
    igual, con un hueco de más o menos lo mismo: así no se confunde con una frase que dices dos veces."""
    # Lo que Whisper se inventa en el silencio del final (copias de la última frase): no duran,
    # media frase con palabras de menos de 0,05 s. Se tiran antes de buscar repetidas
    frase, dichas = [], []
    for k, p in enumerate(palabras):
        frase.append(p)
        if re.search(r"[.?!…]$", p["t"]) or k == len(palabras) - 1:
            if len(frase) < 3 or sum(q["b"] - q["a"] < 0.05 for q in frase) * 2 < len(frase):
                dichas += frase
            frase = []
    inventadas, palabras = len(palabras) - len(dichas), dichas
    claves = [limpia(p["t"]) for p in palabras]
    fuera, i = set(), 0
    while i < len(claves) - minimo:
        for j in range(i + minimo, len(claves) - minimo + 1):
            if claves[j:j + minimo] != claves[i:i + minimo]:
                continue
            largo = minimo
            while j + largo < len(claves) and claves[i + largo] == claves[j + largo]:
                largo += 1
            if j - i <= largo * 2.5:
                fuera.update(range(i, j))
                i = j - 1
            break
        i += 1
    k = len(claves) - 1
    while k > 0 and claves[k] == claves[k - 1]:   # «Gracias. Gracias. Gracias.» al final
        fuera.add(k)
        k -= 1
    return [p for k, p in enumerate(palabras) if k not in fuera], len(fuera) + inventadas


# Lo que dices al grabar para tirar la toma de antes. Solo frases que nadie dice en un reel
NOTAS = [("corta", "eso"), ("corta", "corta"), ("editor", "corta")]
PAUSA_TOMA = 0.6     # una pausa así separa una toma de la siguiente (s)
PARECIDO = 0.72      # dos tomas así de parecidas son la misma frase dicha otra vez
VENTANA_TOMA = 45.0  # y solo si la segunda llega antes de tantos segundos


def quitar_fallos(palabras):
    """Lo que hace un editor a mano, después de quitar_repetidas:
    1. «Corta eso»: fuera la toma de antes y la propia nota.
    2. «Se llama Hy… se llama HyperFrames»: el arranque cortado fuera, se queda el que sigue.
    3. Una frase dicha otra vez con otras palabras: se queda la última.
    Devuelve las palabras que quedan y el texto de cada trozo quitado, para leerlo."""
    from difflib import SequenceMatcher
    fin_de_frase = lambda p: re.search(r"[.?!…]$", p["t"])
    corte = lambda k: k == 0 or palabras[k]["a"] - palabras[k - 1]["b"] >= PAUSA_TOMA or fin_de_frase(palabras[k - 1])
    claves = [limpia(p["t"]) for p in palabras]
    fuera, quitadas = set(), []

    def quitar(rango):
        rango = [k for k in rango if k not in fuera]
        if rango:
            fuera.update(rango)
            quitadas.append(" ".join(palabras[k]["t"] for k in rango))

    for i in range(len(claves)):
        nota = next((n for n in NOTAS if tuple(claves[i:i + len(n)]) == n), None)
        if nota:
            k = i - 1 if corte(i) else i
            while k > 0 and not corte(k):
                k -= 1
            quitar(range(max(k, 0), i + len(nota)))

    i = 0
    while i < len(claves):
        for m in (4, 3, 2):
            j = next((i + m + h for h in range(2) if claves[i:i + m] == claves[i + m + h:i + 2 * m + h]
                      and len(claves[i:i + m]) == m and (h == 0 or len(claves[i + m]) <= 3)), None)
            if j is not None:
                quitar(range(i, j))
                i = j
                break
        else:
            i += 1

    frases, ini = [], 0
    for k in range(1, len(palabras) + 1):
        if k == len(palabras) or corte(k):
            frases.append([n for n in range(ini, k) if n not in fuera])
            ini = k
    frases = [f for f in frases if f]
    for x, a in enumerate(frases):
        if len(a) < 4:
            continue
        for b in frases[x + 1:]:
            if palabras[b[0]]["a"] - palabras[a[-1]]["b"] > VENTANA_TOMA:
                break
            ta, tb = [claves[k] for k in a], [claves[k] for k in b]
            if len(tb) >= 0.8 * len(ta) and SequenceMatcher(None, ta, tb[:len(ta) + 2]).ratio() >= PARECIDO:
                quitar(a)
                break
    return [p for k, p in enumerate(palabras) if k not in fuera], quitadas


def recolocar(palabras, tramos):
    """Pasa los tiempos de cada palabra a la línea de tiempo ya recortada."""
    salida, desplaz, j, inicio_nuevo = [], 0.0, 0, []
    for a, b in tramos:
        inicio_nuevo.append(desplaz)
        desplaz += b - a
    for p in palabras:
        if es_muletilla(p["t"]):
            continue
        while j < len(tramos) - 1 and p["a"] > tramos[j][1]:
            j += 1
        a, b = tramos[j]
        salida.append({"t": p["t"], "a": inicio_nuevo[j] + max(p["a"], a) - a, "b": inicio_nuevo[j] + min(p["b"], b) - a})
    return salida, desplaz


def lineas(palabras):
    """Bloques de hasta 4 palabras; corta antes en un punto o una coma."""
    bloque, bloques = [], []
    for p in palabras:
        bloque.append(p)
        if len(bloque) == PALABRAS_POR_LINEA or re.search(r"[.,;:?!]$", p["t"]):
            bloques.append(bloque)
            bloque = []
    if bloque:
        bloques.append(bloque)
    return bloques


def audio_limpio(fuente, tramos, destino):
    """Pega los trozos de voz con un fundido mínimo y la sube a −14 LUFS con ganancia fija y un limitador
    para los picos. Sin reductor de ruido: el audio del móvil ya viene limpio y el filtro lo deja metálico."""
    partes = [f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,"
              f"afade=t=in:d={FUNDIDO},afade=t=out:st={b - a - FUNDIDO:.3f}:d={FUNDIDO}[a{i}]"
              for i, (a, b) in enumerate(tramos)]
    pegar = "".join(f"[a{i}]" for i in range(len(tramos))) + f"concat=n={len(tramos)}:v=0:a=1,highpass=f=70"
    medir = destino.with_suffix(".medir.txt")
    medir.write_text(";".join(partes) + f";{pegar},loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json[out]")
    info = subprocess.run([FFMPEG, "-hide_banner", "-i", str(fuente), "-filter_complex_script", str(medir),
                           "-map", "[out]", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = json.loads(info[info.rindex("{"):info.rindex("}") + 1])
    ln = f"volume={-14 - float(m['input_i']):.2f}dB,alimiter=limit=0.84:attack=5:release=50:level=false"
    medir.write_text(";".join(partes) + f";{pegar},{ln},aresample=48000[out]")
    run([FFMPEG, "-y", "-i", str(fuente), "-filter_complex_script", str(medir), "-map", "[out]", "-c:a", "pcm_s16le", str(destino)])
    medir.unlink()


def montar(fuente, tramos, destino, tono="cálido", crf=16, gop=30):
    """El vídeo base: solo los trozos con voz, sin texto, con un fotograma clave cada `gop` (HyperFrames salta
    por el vídeo al renderizar y lo necesita)."""
    audio = destino.with_suffix(".wav")
    audio_limpio(fuente, tramos, audio)
    sel = "+".join(f"between(t,{a:.3f},{b:.3f})" for a, b in tramos)
    vf = f"select='{sel}',setpts=N/FRAME_RATE/TB,{TONOS[tono]}".rstrip(",")
    # el vídeo del móvil puede traer una marca de giro: se anula al leerlo, si no sale tumbado
    run([FFMPEG, "-y", "-display_rotation", "0", "-i", str(fuente), "-i", str(audio), "-vf", vf,
         "-map", "0:v", "-map", "1:a", "-r", "30", "-shortest", "-c:v", "libx264", "-preset", "medium",
         "-crf", str(crf), "-pix_fmt", "yuv420p", "-g", str(gop), "-keyint_min", str(gop),
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(destino)])
    audio.unlink()
