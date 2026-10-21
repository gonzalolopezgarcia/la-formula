"""Estilo «vlog»: un día de tu vida. Mandas los clips del día; aquí se montan sin voz (un plano nuevo cada 1,2
a 1,8 s); grabas tu voz encima del corte; y aquí van los subtítulos (una palabra cada vez), la música y el título.

  formula vlog NOMBRE --clips CARPETA   una hoja por clip (un fotograma cada «cada» s)   → tomas/, tomas.json
  formula vlog NOMBRE --montar          los planos de montaje.json, uno tras otro      → corte.mp4, planos.txt
                                        y videos/salida/NOMBRE-para-la-voz.mp4, para grabar tu voz encima
  formula vlog NOMBRE --voz FICHERO     tu voz (audio o vídeo) sobre el corte           → base.mp4, voz.wav
Después, como siempre: formula musica NOMBRE vlog, formula armar, formula foto, formula render.

montaje.json: {"planos": [{"toma": 3, "desde": 2.0, "hasta": 3.5, "que": "llego a la oficina"}, …]}
«sonido»: true deja el sonido de ese plano (tú hablando a cámara); si no, el plano va mudo.
"""
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

import corte
from config import FFMPEG, SALIDA

FPS = 30
HOJA = 36   # fotogramas por hoja como mucho: un clip largo se mira cada más segundos
# En los vlogs que funcionan la canción va solo 2,5 dB por debajo de la voz: voz a −14 y canción a −16,5
# (musica.py, NIVEL), y el reel sale a ~−14, como los demás.
VOZ = "highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,loudnorm=I=-14:TP=-1.5:LRA=9"
ENCUADRE = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1,format=yuv420p"


def duracion(fichero):
    salida = subprocess.run([FFMPEG, "-hide_banner", "-i", str(fichero)], capture_output=True, text=True).stderr
    h, m, s = salida.split("Duration: ")[1].split(",")[0].split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def tiene_audio(fichero):
    salida = subprocess.run([FFMPEG, "-hide_banner", "-i", str(fichero)], capture_output=True, text=True).stderr
    return "Audio:" in salida


def tomas(dir_, origen):
    """Una hoja por clip: el fotograma k de la hoja es el segundo k × cada. Devuelve las líneas a enseñar."""
    clips = corte.ordenar([p for p in Path(origen).expanduser().iterdir() if p.suffix.lower() in corte.VIDEO_EXT])
    if not clips:
        sys.exit(f"No hay vídeos en {origen}")
    hojas = dir_ / "tomas"
    shutil.rmtree(hojas, ignore_errors=True)
    hojas.mkdir(parents=True)
    lista, lineas = [], []
    for n, clip in enumerate(clips, 1):
        dur = duracion(clip)
        cada = max(1.0, math.ceil(dur / HOJA))
        filas = math.ceil(dur / cada / 6)
        subprocess.run([FFMPEG, "-v", "error", "-y", "-i", str(clip), "-vf",
                        f"fps=1/{cada},scale=270:-2,tile=6x{filas}", "-frames:v", "1", str(hojas / f"{n:02d}.jpg")],
                       check=True)
        lista.append({"n": n, "clip": clip.name, "ruta": str(clip), "dur": round(dur, 2), "cada": cada})
        lineas.append(f"  {n:2d}  {clip.name:<22} {dur:5.1f} s  → tomas/{n:02d}.jpg (un fotograma cada {cada:g} s)")
    (dir_ / "tomas.json").write_text(json.dumps(lista, ensure_ascii=False, indent=1), encoding="utf-8")
    return lineas


def montar(dir_):
    """Cada plano de montaje.json a 1080x1920 y 30 fps, mudo salvo «sonido», y todos seguidos."""
    lista = {t["n"]: t for t in json.loads((dir_ / "tomas.json").read_text(encoding="utf-8"))}
    planos = json.loads((dir_ / "montaje.json").read_text(encoding="utf-8"))["planos"]
    trozos = dir_ / "trozos"
    shutil.rmtree(trozos, ignore_errors=True)
    trozos.mkdir()
    t, guia = 0.0, []
    for k, p in enumerate(planos):
        toma = lista[p["toma"]]
        largo = round(p["hasta"] - p["desde"], 3)
        if largo <= 0 or p["hasta"] > toma["dur"] + 0.05:
            sys.exit(f"Plano {k + 1}: {p['desde']}–{p['hasta']} no cabe en la toma {p['toma']} ({toma['dur']} s)")
        orden = [FFMPEG, "-v", "error", "-y", "-ss", str(p["desde"]), "-t", str(largo), "-i", toma["ruta"]]
        if p.get("sonido") and tiene_audio(toma["ruta"]):
            orden += ["-map", "0:v:0", "-map", "0:a:0"]
        else:   # mudo: un silencio del mismo largo, para que todos los trozos tengan audio y se peguen sin recodificar
            orden += ["-f", "lavfi", "-t", str(largo), "-i", "anullsrc=r=48000:cl=stereo", "-map", "0:v:0", "-map", "1:a:0"]
        orden += ["-vf", ENCUADRE, "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-r", str(FPS),
                  "-c:a", "aac", "-ar", "48000", "-ac", "2", "-shortest", str(trozos / f"{k:03d}.mp4")]
        subprocess.run(orden, check=True)
        guia.append(f"{t:5.1f}–{t + largo:5.1f}  toma {p['toma']:>2}  {p.get('que', '')}")
        t += largo
    (trozos / "lista.txt").write_text("".join(f"file '{f.name}'\n" for f in sorted(trozos.glob("*.mp4"))))
    corte = dir_ / "corte.mp4"
    subprocess.run([FFMPEG, "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(trozos / "lista.txt"),
                    "-c", "copy", "-movflags", "+faststart", str(corte)], check=True)
    shutil.rmtree(trozos)
    (dir_ / "planos.txt").write_text("\n".join(guia) + "\n", encoding="utf-8")
    SALIDA.mkdir(parents=True, exist_ok=True)
    para_voz = SALIDA / f"{dir_.name}-para-la-voz.mp4"
    shutil.copy(corte, para_voz)
    return corte, para_voz, t, guia


def con_voz(dir_, fichero, desde=0.0):
    """Tu voz, limpia y a −14, encima del corte (con el sonido de los planos que lo llevan, más bajo).
    Si la voz dura más que el corte, se avisa: o grabas más corto o se alarga el corte."""
    corte, voz, base = dir_ / "corte.mp4", dir_ / "voz.wav", dir_ / "base.mp4"
    subprocess.run([FFMPEG, "-v", "error", "-y", "-ss", str(desde), "-i", str(fichero), "-vn",
                    "-af", VOZ, "-ar", "48000", "-ac", "2", str(voz)], check=True)
    sobra = duracion(voz) - duracion(corte)
    subprocess.run([FFMPEG, "-v", "error", "-y", "-i", str(corte), "-i", str(voz), "-filter_complex",
                    "[0:a]volume=0.45[c];[c][1:a]amix=inputs=2:duration=first:normalize=0[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", str(base)], check=True)
    return base, voz, sobra
