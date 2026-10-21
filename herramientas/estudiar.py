"""Transcribe reels bajados (de tus referentes o el que vas a copiar) y saca las medidas de cada guion.

Uso: herramientas/formula-estudiar <carpeta>
<carpeta> lleva una subcarpeta por reel con su v.mp4 (lo baja yt-dlp, ver /guion) y, si quieres comparar,
vistas.txt («<código> <vistas>» por línea, como sale de herramientas/vistas-rejilla.js).
Deja transcript.txt y palabras.json en cada una e imprime la tabla. Local, 0 €.
"""
import json
import re
import statistics
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import FFMPEG  # noqa: E402

raiz = Path(sys.argv[1]).expanduser()


def vistas_de(texto: str) -> int:
    texto = texto.strip().lower().replace("vistas", "").strip()
    cifra, _, unidad = texto.partition(" ")
    escala = {"mil": 1e3, "k": 1e3, "m": 1e6, "mill.": 1e6}.get(unidad, 1)
    if cifra[-1:] in ("k", "m"):
        escala, cifra = (1e3 if cifra[-1] == "k" else 1e6), cifra[:-1]
    return round(float(cifra.replace(".", "").replace(",", ".") if escala == 1 else cifra.replace(",", ".")) * escala)


vistas = {}
if (raiz / "vistas.txt").exists():
    for linea in (raiz / "vistas.txt").read_text().splitlines():
        if linea.strip():
            codigo, _, resto = linea.strip().partition(" ")
            vistas[codigo] = vistas_de(resto)
mediana = statistics.median(vistas.values()) if vistas else 0

pendientes = [c for c in sorted(raiz.iterdir()) if c.is_dir() and not (c / "transcript.txt").exists() and list(c.glob("v.*"))]
if pendientes:
    from faster_whisper import WhisperModel

    modelo = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")
    for carpeta in pendientes:
        wav = carpeta / "audio.wav"
        subprocess.run([FFMPEG, "-v", "error", "-y", "-i", str(next(carpeta.glob("v.*"))), "-vn", "-ac", "1", "-ar", "16000", str(wav)], check=True)
        segmentos, info = modelo.transcribe(str(wav), word_timestamps=True, vad_filter=True)   # el idioma, lo adivina
        palabras, lineas = [], []
        for s in segmentos:
            lineas.append(f"[{s.start:5.1f}-{s.end:5.1f}] {s.text.strip()}")
            palabras += [{"s": round(w.start, 2), "e": round(w.end, 2), "w": w.word.strip()} for w in s.words]
        (carpeta / "transcript.txt").write_text("\n".join(lineas) + "\n")
        (carpeta / "palabras.json").write_text(json.dumps({"dur": round(info.duration, 1), "idioma": info.language, "palabras": palabras}))
        wav.unlink()
        print("transcrito", carpeta.name, flush=True)


def segundo_de(palabras: list, patron: str, desde: float = 0.0):
    for i, p in enumerate(palabras):
        if p["s"] >= desde and re.match(patron, " ".join(q["w"] for q in palabras[i: i + 3]).lower()):
            return p["s"]
    return None


if vistas:
    print(f"\n{len(vistas)} reels · mediana {mediana:.0f} vistas · {sum(v >= 10 * mediana for v in vistas.values())} por encima de 10 veces")
print("\ncódigo         vistas    ×   dur   pal  p/s  frases  1ª frase    imán   «comenta»")
for carpeta in sorted((c for c in raiz.iterdir() if (c / "palabras.json").exists()), key=lambda c: -vistas.get(c.name, 0)):
    j = json.loads((carpeta / "palabras.json").read_text())
    p, dur = j["palabras"], j["dur"]
    if not p:
        continue
    frases = [f for f in re.split(r"(?<=[.!?])\s+", " ".join(x["w"] for x in p)) if f.strip()]
    n1 = len(frases[0].split())
    iman = segundo_de(p, r"i made a|i'll save you|if you want|he hecho|te he preparado|te dejo")
    cta = segundo_de(p, r"comment|comenta", dur * 0.5)
    v = vistas.get(carpeta.name, 0)
    print(f"{carpeta.name:13} {v:7} {v / (mediana or 1):4.0f} {dur:5.1f} {len(p):5} {len(p) / max(p[-1]['e'] - p[0]['s'], 1):4.1f} {len(frases):6}"
          f"   {n1:2} pal {p[min(n1, len(p)) - 1]['e']:4.1f} s   {iman if iman is not None else '-':>5}   {cta if cta is not None else '-':>6}")
