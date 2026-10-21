"""Dónde está cada cosa y qué dice tu marca (marca/marca.json). Todo vive dentro del repo:
tus clips en videos/entrada, cada vídeo en videos/trabajo/<nombre> y lo terminado en videos/salida."""
import json
from pathlib import Path

AQUI = Path(__file__).resolve().parent          # herramientas/
RAIZ = AQUI.parent                              # el repo
MARCA_DIR = RAIZ / "marca"
VIDEOS = RAIZ / "videos"
ENTRADA, TRABAJO, SALIDA = VIDEOS / "entrada", VIDEOS / "trabajo", VIDEOS / "salida"
HF_DIR = AQUI / ".hf"                           # HyperFrames y lo que usa (npm), lo pone instalar.sh
BIN = AQUI / ".bin"                             # ffmpeg y ffprobe, lo pone instalar.sh
FFMPEG, FFPROBE = str(BIN / "ffmpeg"), str(BIN / "ffprobe")
KIT = AQUI / "kit"

POR_DEFECTO = {
    "nombre": "",
    "idioma": "es",
    "zona_horaria": "Europe/Madrid",
    "cuentas": {"instagram": "", "tiktok": "", "facebook": ""},
    "colores": {"acento": "#FFD400", "panel": "#111111", "papel": "#F4F1EA", "tinta": "#111111"},
    "letras": {"texto": "Inter", "grande": "Bebas Neue", "mono": "JetBrains Mono", "titulo": "Instrument Serif"},
    "horas": {"mañana": "13:00", "tarde": "19:00"},
    "pie_otras_redes": "",
    "palabras_prohibidas": [],
}


def marca():
    """marca.json sobre los valores por defecto (un campo que falta no rompe nada)."""
    fichero = MARCA_DIR / "marca.json"
    propia = json.loads(fichero.read_text(encoding="utf-8")) if fichero.exists() else {}
    junta = {**POR_DEFECTO, **{k: v for k, v in propia.items() if not k.startswith("_")}}
    for k in ("cuentas", "colores", "letras", "horas"):   # los «_ayuda» son notas para ti: fuera
        junta[k] = {**POR_DEFECTO[k], **{c: v for c, v in propia.get(k, {}).items() if not c.startswith("_")}}
    return junta
