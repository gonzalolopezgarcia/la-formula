"""La canción de fondo de un reel, según el tipo de vídeo y rotando: la de ese tipo que lleva más tiempo
sin sonar. Tus canciones están en marca/musica/<id>.(m4a|mp3|wav) y su ficha en marca/musica.json (tipos,
desde qué segundo suena, de dónde la sacaste). marca/musica/sonadas.txt apunta cada vez que se pone una.

Tres cosas que se aprenden a base de vídeos:
- Debajo de tu voz (−15 LUFS) la canción va a −33 y aplanada (LRA 5): si no, la parte fuerte se sale del fondo.
- Se mide lo que suena por el altavoz de un móvil (por encima de 250 Hz): una canción casi toda de graves
  mide igual que las demás y no se oye nada en el móvil.
- Para elegir entre varias, una página con cada una «en tu reel» y «sola», todas igual de altas.
"""
import json
import math
import re
import shutil
import subprocess
import time
from pathlib import Path

from config import FFMPEG, MARCA_DIR

CATALOGO = MARCA_DIR / "musica.json"
CANCIONES = MARCA_DIR / "musica"
SONADAS = CANCIONES / "sonadas.txt"
PAGINA = Path(__file__).resolve().parent / "musica-opciones.html"
VOLUMEN = "loudnorm=I=-33:TP=-8:LRA=5"                   # debajo de tu voz (−15), aplanada
NIVEL = {"vlog": "loudnorm=I=-16.5:TP=-2:LRA=7",        # un groove casi a la par de la voz: 2,5 dB por debajo
         "reflexion": "loudnorm=I=-14:TP=-1.5:LRA=7"}   # sin voz: la música lo lleva todo
ESCUCHA = 35.0   # lo que se oye de cada una «en tu reel»: el principio del vídeo, con tu voz
MOVIL = "highpass=f=250,"


def catalogo():
    return json.loads(CATALOGO.read_text(encoding="utf-8"))


def fichero(c):
    hay = [f for f in CANCIONES.glob(f"{c['id']}.*") if f.suffix.lower() in (".m4a", ".mp3", ".wav", ".aac")]
    if not hay:
        raise SystemExit(f"Falta el audio de «{c['id']}» en {CANCIONES}")
    return hay[0]


def ultimas():
    """{id: (fecha, vídeo)} de la última vez que sonó cada una."""
    vistas = {}
    for linea in SONADAS.read_text(encoding="utf-8").splitlines() if SONADAS.exists() else []:
        fecha, id_, video = linea.split("\t")
        vistas[id_] = (fecha, video)
    return vistas


def lista():
    cat, vistas = catalogo(), ultimas()
    lineas = []
    for tipo, que in cat["tipos"].items():
        lineas.append(f"\n{tipo}: {que}")
        for c in (c for c in cat["canciones"] if tipo in c["tipos"]):
            fecha, video = vistas.get(c["id"], ("", ""))
            lineas.append(f"  {c['id']:34} {c['titulo']}, {c['artista']} · {f'{fecha} en {video}' if fecha else 'sin estrenar'}")
    return "\n".join(lineas)


def lufs(audio, hasta=None, movil=False):
    """La sonoridad integrada (LUFS); con movil, solo lo que suena por el altavoz de un móvil."""
    salida = subprocess.run([FFMPEG, "-hide_banner", "-nostats", *(["-t", f"{hasta}"] if hasta else []), "-i", str(audio),
                             "-af", f"{MOVIL if movil else ''}ebur128=framelog=quiet", "-f", "null", "-"],
                            capture_output=True, text=True).stderr
    return float(salida.rsplit("I:", 1)[1].split("LUFS")[0])


def igualar(audio, objetivo, hasta=None, movil=False):
    """Ganancia fija hasta que lo que se oye (sus primeros «hasta» s) dé «objetivo» LUFS. loudnorm de una pasada
    sobre un trozo corto falla hasta 3 dB: para comparar canciones, esto."""
    ganancia = objetivo - lufs(audio, hasta, movil)
    tmp = audio.with_name("_" + audio.name)
    subprocess.run([FFMPEG, "-v", "error", "-y", "-i", str(audio), "-af", f"volume={ganancia:.2f}dB,alimiter=limit=0.89", str(tmp)], check=True)
    tmp.replace(audio)


def objetivo_de(tipo):
    return float(NIVEL.get(tipo, VOLUMEN).split("I=")[1].split(":")[0])


def cortar(c, dur, destino, entra=0.0, tipo=None):
    """Desde el segundo en que suena mejor («desde»). Si desde ahí no llega al final del vídeo, empieza antes; si
    la canción es más corta que el vídeo, vuelve a empezar. Con «entra», empieza en ese segundo del vídeo (antes
    solo suena lo demás) y siempre desde «desde», para que el golpe caiga ahí; si no llega, repite de «desde» a
    «hasta» fundiendo cada vuelta. Devuelve el segundo desde el que suena."""
    lecho, cancion = dur - entra, str(fichero(c))
    final = (f"{NIVEL.get(tipo or c['tipos'][0], VOLUMEN)},afade=t=in:d={0.1 if entra else 1.5},afade=t=out:st={lecho - 2.5:.3f}:d=2.5"
             + (f",aresample=48000,adelay={int(entra * 1000)}:all=1,apad=whole_dur={dur:.3f}" if entra else ""))
    a, b, funde = c.get("desde", 0), c.get("hasta", c["largo"]), 1.5
    if entra and a + lecho > b:
        vueltas = math.ceil((lecho - funde) / (b - a - funde))
        filtro = "".join(f"[0:a]atrim={a}:{b},asetpts=N/SR/TB[t{i}];" for i in range(vueltas))
        previo = "t0"
        for i in range(1, vueltas):
            filtro += f"[{previo}][t{i}]acrossfade=d={funde}[x{i}];"
            previo = f"x{i}"
        subprocess.run([FFMPEG, "-v", "error", "-y", "-i", cancion, "-filter_complex",
                        f"{filtro}[{previo}]atrim=0:{lecho:.3f},{final}[m]", "-map", "[m]", "-ar", "48000", "-ac", "2",
                        str(destino)], check=True)
        return a
    desde = a if entra else min(a, max(0, c["largo"] - lecho - 1))
    vueltas = math.ceil((desde + lecho) / c["largo"])
    subprocess.run([FFMPEG, "-v", "error", "-y", "-stream_loop", str(vueltas - 1), "-i", cancion,
                    "-af", f"atrim={desde}:{desde + lecho:.3f},asetpts=N/SR/TB,{final}", "-ar", "48000", "-ac", "2",
                    str(destino)], check=True)
    return desde


def poner(dir_, tipo=None, cancion=None, entra=0.0):
    """musica.wav en la carpeta del vídeo. Sin tipo ni canción, la lista."""
    cat = catalogo()
    if not cat["canciones"]:
        raise SystemExit("Aún no tienes canciones: `formula musica --anadir <fichero o enlace> --tipos caso,utilidad`")
    if not (tipo or cancion):
        return print(lista())
    if cancion:
        c = next((c for c in cat["canciones"] if c["id"] == cancion), None)
        if not c:
            raise SystemExit(f"{cancion}: no está en marca/musica.json. Las que hay: formula musica {dir_.name}")
    elif tipo not in cat["tipos"]:
        raise SystemExit(f"tipo={tipo}: es {', '.join(cat['tipos'])}")
    else:
        vistas = ultimas()
        candidatas = [c for c in cat["canciones"] if tipo in c["tipos"]]
        if not candidatas:
            raise SystemExit(f"No tienes canciones de tipo «{tipo}» en marca/musica.json")
        c = min(candidatas, key=lambda c: vistas.get(c["id"], ("",))[0])
    medidas = json.loads((dir_ / "medidas.json").read_text())
    dur = medidas["duracion"] + medidas.get("clip", 0.0)
    musica = dir_ / "musica.wav"
    desde = cortar(c, dur, musica, entra, tipo)
    if (falta := objetivo_de(tipo or c["tipos"][0]) - 2 - lufs(musica, movil=True)) > 1:   # una de graves: que se oiga en el móvil
        igualar(musica, objetivo_de(tipo or c["tipos"][0]) - 2 - max(0, falta - 8), movil=True)
    SONADAS.parent.mkdir(parents=True, exist_ok=True)
    with SONADAS.open("a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M')}\t{c['id']}\t{dir_.name}\n")
    print(f"{c['titulo']}, {c['artista']} (desde el {desde:g} s) → musica.wav\nEn la línea de ajustes del guion: musica=musica.wav")


def opciones(dir_, ids, tipo="utilidad"):
    """Una página con varias canciones, cada una «en tu reel» (el principio del vídeo con tu voz y los sonidos,
    la canción a su volumen de verdad) y «sola». Todas igual de altas por el altavoz de un móvil."""
    from config import FFMPEG as F
    cat = {c["id"]: c for c in catalogo()["canciones"]}
    if falta := [i for i in ids if i not in cat]:
        raise SystemExit(f"{', '.join(falta)}: no está en marca/musica.json")
    medidas = json.loads((dir_ / "medidas.json").read_text())
    dur = medidas["duracion"] + medidas.get("clip", 0.0)
    sal = dir_ / "musica-opciones"
    sal.mkdir(exist_ok=True)
    voz, estereo = sal / "voz.wav", "aresample=48000,aformat=channel_layouts=stereo"
    entradas, filtro = ["-i", str(dir_ / "base.mp4")], f"[0:a]{estereo}[v]"
    if medidas.get("clip"):
        entradas = ["-i", str(dir_ / "clip.mp4")] + entradas
        filtro = f"[0:a]{estereo}[a];[1:a]{estereo}[b];[a][b]concat=n=2:v=0:a=1[v]"
    subprocess.run([F, "-v", "error", "-y", *entradas, "-filter_complex", filtro, "-map", "[v]", "-t", f"{ESCUCHA}", str(voz)], check=True)
    sonidos = dir_ / "sonidos.wav"
    for c in (cat[i] for i in ids):
        cancion = sal / f"{c['id']}.wav"
        cortar(c, dur, cancion, tipo=tipo)
        igualar(cancion, objetivo_de(tipo) - 2, ESCUCHA, movil=True)
        capas = [voz, cancion] + ([sonidos] if sonidos.exists() else [])
        subprocess.run([F, "-v", "error", "-y", *[x for f in capas for x in ("-i", str(f))], "-filter_complex",
                        f"[1:a]afade=t=out:st={ESCUCHA - 2}:d=2[m];"
                        + "".join(f"[{k}:a]{estereo},atrim=0:{ESCUCHA}[s{k}];" for k in range(2, len(capas)))
                        + "[0:a][m]" + "".join(f"[s{k}]" for k in range(2, len(capas)))
                        + f"amix=inputs={len(capas)}:normalize=0:duration=first[x]",
                        "-map", "[x]", "-c:a", "aac", "-b:a", "160k", str(sal / f"{c['id']}.m4a")], check=True)
        cancion.unlink()
        desde = min(c.get("desde", 0), max(0, c["largo"] - 31))
        sola = sal / f"{c['id']}.sola.wav"
        subprocess.run([F, "-v", "error", "-y", "-ss", f"{desde}", "-t", "30", "-i", str(fichero(c)),
                        "-af", "afade=t=in:d=0.5,afade=t=out:st=28:d=2", str(sola)], check=True)
        igualar(sola, -18.0, movil=True)
        subprocess.run([F, "-v", "error", "-y", "-i", str(sola), "-c:a", "aac", "-b:a", "160k", str(sal / f"{c['id']}.sola.m4a")], check=True)
        sola.unlink()
    voz.unlink()
    datos = [{"id": c["id"], "titulo": c["titulo"], "artista": c["artista"], "etq": c.get("de_donde", [])} for c in (cat[i] for i in ids)]
    pagina = sal / "index.html"
    pagina.write_text(PAGINA.read_text(encoding="utf-8").replace("/*OPCIONES*/[]", json.dumps(datos, ensure_ascii=False)), encoding="utf-8")
    print(f"{pagina}\nCon la que elijas: formula musica {dir_.name} {tipo} --cancion <id>")
    return pagina


def anadir(fuente, tipos, titulo=None, artista=None, desde=0.0):
    """Añade una canción a tu catálogo: un fichero tuyo o un enlace (lo baja yt-dlp). Solo música que puedas usar."""
    CANCIONES.mkdir(parents=True, exist_ok=True)
    cat = catalogo()
    base = re.sub(r"[^a-z0-9]+", "-", (titulo or Path(fuente).stem).lower()).strip("-")[:40] or "cancion"
    id_, n = base, 2
    while any(c["id"] == id_ for c in cat["canciones"]):
        id_, n = f"{base}-{n}", n + 1
    if re.match(r"https?://", fuente):
        subprocess.run(["yt-dlp", "-q", "--no-warnings", "-x", "--audio-format", "m4a", "--ffmpeg-location", str(Path(FFMPEG).parent),
                        "-o", str(CANCIONES / f"{id_}.%(ext)s"), fuente], check=True)
    else:
        origen = Path(fuente).expanduser()
        shutil.copy(origen, CANCIONES / f"{id_}{origen.suffix.lower()}")
    audio = next(CANCIONES.glob(f"{id_}.*"))
    info = subprocess.run([FFMPEG, "-hide_banner", "-i", str(audio)], capture_output=True, text=True).stderr
    h, m, s = info.split("Duration: ")[1].split(",")[0].split(":")
    cat["canciones"].append({"id": id_, "tipos": tipos, "titulo": titulo or id_, "artista": artista or "", "desde": desde,
                             "largo": round(int(h) * 3600 + int(m) * 60 + float(s), 1), "de_donde": [fuente]})
    CATALOGO.write_text(json.dumps(cat, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Añadida «{id_}» ({', '.join(tipos)}) → {audio}")
