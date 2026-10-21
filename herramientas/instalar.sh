#!/usr/bin/env bash
# Instala lo que usa La Fórmula, todo dentro de herramientas/ (nada en el sistema): Python con Whisper para
# transcribir en local, ffmpeg, HyperFrames (el render), su Chrome sin ventana, los iconos y las letras.
# Mac o Linux. Se puede pasar otra vez sin miedo: solo pone lo que falta. Ocupa ~2,5 GB con el modelo de Whisper.
set -euo pipefail
cd "$(dirname "$0")"
falta() { echo "❌ Falta $1. $2"; exit 1; }

command -v node >/dev/null || falta "Node.js (20 o más)" "Instálalo desde https://nodejs.org y vuelve a pasar esto."
[ "$(node -p 'process.versions.node.split(".")[0]')" -ge 20 ] || falta "Node.js 20 o más" "Tienes $(node -v)."

echo "1/5 Python y Whisper…"
if command -v uv >/dev/null; then
  [ -x .venv/bin/python ] || uv venv --python 3.12 .venv
  uv pip install --quiet --python .venv/bin/python -r requirements.txt
else
  py=$(command -v python3.12 || command -v python3.13 || true)
  [ -n "$py" ] || falta "Python 3.12" "Lo más fácil: instala uv (https://docs.astral.sh/uv/) y vuelve a pasar esto; uv se baja Python solo."
  [ -x .venv/bin/python ] || "$py" -m venv .venv
  .venv/bin/pip install --quiet -r requirements.txt
fi

echo "2/5 HyperFrames, iconos y letras (npm)…"
mkdir -p .hf
cp package.json .hf/package.json
(cd .hf && npm install --silent --no-audit --no-fund)

echo "3/5 ffmpeg y ffprobe…"
mkdir -p .bin
ln -sf "$(.venv/bin/python -c 'import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())')" .bin/ffmpeg
ln -sf "$(cd .hf && node -p 'require("@ffprobe-installer/ffprobe").path')" .bin/ffprobe

echo "4/5 El kit: GSAP y las letras…"
cp .hf/node_modules/gsap/dist/gsap.min.js kit/gsap.min.js
mkdir -p kit/fonts
f=.hf/node_modules
cp $f/@fontsource-variable/inter/files/inter-latin-wght-normal.woff2 kit/fonts/inter.woff2
cp $f/@fontsource-variable/jetbrains-mono/files/jetbrains-mono-latin-wght-normal.woff2 kit/fonts/jetbrains-mono.woff2
cp $f/@fontsource-variable/montserrat/files/montserrat-latin-wght-normal.woff2 kit/fonts/montserrat.woff2
cp $f/@fontsource/bebas-neue/files/bebas-neue-latin-400-normal.woff2 kit/fonts/bebas-neue.woff2
cp $f/@fontsource/anton/files/anton-latin-400-normal.woff2 kit/fonts/anton.woff2
cp $f/@fontsource/poppins/files/poppins-latin-600-normal.woff2 kit/fonts/poppins.woff2
cp $f/@fontsource/instrument-serif/files/instrument-serif-latin-400-normal.woff2 kit/fonts/instrument-serif.woff2
cp $f/@fontsource/instrument-serif/files/instrument-serif-latin-400-italic.woff2 kit/fonts/instrument-serif-italic.woff2

echo "5/5 El Chrome sin ventana de HyperFrames (sin telemetría)…"
export PATH="$PWD/.bin:$PATH"
.hf/node_modules/.bin/hyperframes telemetry disable >/dev/null 2>&1 || true
.hf/node_modules/.bin/hyperframes browser ensure

chmod +x formula formula-guion formula-estudiar
mkdir -p ../videos/entrada ../videos/trabajo ../videos/salida ../marca/musica
echo
echo "✅ Listo. Prueba: herramientas/formula --help"
echo "   La primera transcripción baja el modelo de Whisper (~1,5 GB): tarda un poco, solo esa vez."
[ "$(uname)" = Darwin ] || echo "   Fuera de macOS la portada no mide los ojos: elige el segundo con «formula portada NOMBRE --en S»."
