# La Fórmula

Tu equipo de agentes de IA para hacer reels, en tu ordenador y con Claude:

| Agente | Qué hace |
|---|---|
| **/guion** | Te escribe el guion: desde un tema, inspirándose en lo que mejor les funciona a tus referentes, o copiando un vídeo (aunque esté en otro idioma). Ganchos que paran, frases cortas, cada cifra comprobada |
| **/edicion** | Edita tus clips: quita silencios y tomas repetidas, y pone encima gráficos animados que prueban lo que dices, subtítulos, música y efectos de sonido. Cuatro estilos: gráficos encima, pantalla partida, clip y reacción, y vlog |
| **/subida** | Lo programa en Instagram, TikTok y Facebook a la vez, a tu hora buena, desde tu propio Chrome |
| **/pruebas** | Al día siguiente, 9 copias distintas como «Reels de prueba»: solo las ve quien no te sigue |

Todo corre en tu ordenador: la transcripción (Whisper), el corte (ffmpeg) y el render (HyperFrames). Lo único que
pagas es tu plan de Claude.

No trae el estilo de nadie: cada cual pone el suyo en `marca/` (colores, letras, voz, referentes, música) y cada
corrección que haces se apunta ahí, así que cada vídeo sale más tuyo que el anterior.

## Lo que necesitas

- [Claude Code](https://claude.com/claude-code)
- Un Mac (recomendado) o Linux, con ~3 GB libres
- [Node.js](https://nodejs.org) 20 o más y Python 3.12 (o [uv](https://docs.astral.sh/uv/), que se lo baja solo)
- Para subir: Chrome con la extensión **Claude in Chrome** y sesión en Instagram, Meta Business Suite y TikTok

## Empezar

```bash
git clone https://github.com/gonzalolopezgarcia/la-formula
cd la-formula
claude
```

Y dentro de Claude: **/empezar**. Instala las herramientas y te hace unas preguntas para rellenar tu marca.

Después, la cadena:

1. **/guion** «hazme el guion de …» → te da las tomas numeradas. Grábalas con tus palabras.
2. Pasa los clips a `videos/entrada/` y **/edicion** → te enseña un borrador; corriges lo que quieras.
3. **/subida** «súbelo por la tarde» → Instagram, TikTok y Facebook a la vez.
4. **/pruebas** → las 9 copias de prueba para el día siguiente.

## Qué hay dentro

```
.claude/skills/     los agentes: empezar, guion, edicion, subida, pruebas
herramientas/       el código: formula (corte, gráficos, render, portada, música, copias), guion (comprobador)…
marca/              lo tuyo: marca.json, voz, referentes, estilo, música, lecciones
ejemplo/guion.html  un guion de edición con las piezas principales
videos/             tus clips y lo que sale (no se sube a git)
```

## Hecho con

[HyperFrames](https://github.com/heygen-com/hyperframes) (render de vídeo desde HTML),
[GSAP](https://gsap.com), [faster-whisper](https://github.com/SYSTRAN/faster-whisper),
[ffmpeg](https://ffmpeg.org), [yt-dlp](https://github.com/yt-dlp/yt-dlp),
[Simple Icons](https://simpleicons.org), [Lucide](https://lucide.dev) y las letras de
[Fontsource](https://fontsource.org) (licencia OFL).

## Licencia

MIT. Úsalo, cámbialo y hazlo tuyo.
