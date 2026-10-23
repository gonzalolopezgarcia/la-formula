---
name: empezar
description: La primera vez que se usa La Fórmula - instala las herramientas, comprueba que todo funciona y rellena tu marca (colores, letras, voz, referentes, horas) con una entrevista corta, una pregunta cada vez. Úsala con «empezar», «instálalo», «configúralo», «primera vez», «/empezar», o cuando marca/marca.json siga vacío.
---

# Empezar: instalar y hacer tuya La Fórmula

Cuatro agentes trabajan en cadena: **/guion** (qué dices), **/edicion** (tus clips con gráficos encima), **/subida**
(a Instagram, TikTok y Facebook a tu hora) y **/pruebas** (9 copias para quien no te sigue). Todo corre en tu
ordenador; lo único que pagas es tu plan de Claude.

Habla en el idioma de quien escribe y ve paso a paso: una pregunta cada vez y nada técnico sin explicarlo.

## Lo que le vas contando

Que vea desde el principio lo que va a hacer la IA por él. Por ejemplo:

- «Te instalo todo lo que hace falta dentro de esta carpeta, sin tocar nada de tu ordenador: el transcriptor, el
  editor y el render. Tardo unos minutos.»
- «Ahora te hago unas preguntas para que cada vídeo salga con tu estilo: tus colores, tus letras, cómo hablas. Una cada
  vez.»
- Al acabar: «Listo. A partir de ahora: me pides un guion, lo grabas, te lo edito, te lo subo a tu mejor hora y te hago
  las pruebas. Si algún paso lo quieres hacer tú, me lo dices y me lo salto.»

## 1. Las herramientas

```bash
herramientas/instalar.sh
```

- Necesita Node.js 20 o más (nodejs.org) y Python 3.12 (o uv, que se lo baja solo: docs.astral.sh/uv). Si falta algo,
  el script dice qué y dónde. Mejor en un Mac: fuera de macOS todo funciona salvo medir los ojos de la portada.
- Instala dentro de `herramientas/` (nada en el sistema): Whisper para transcribir en local, ffmpeg, HyperFrames (el
  render) con su Chrome sin ventana, iconos y letras. ~2,5 GB con el modelo de Whisper, que baja la primera vez que
  transcribe.
- Comprueba: `herramientas/formula --help`.

Para subir desde su Chrome hace falta **Claude in Chrome** (la extensión oficial de Anthropic) instalada y con sesión en
Instagram, Meta Business Suite y TikTok. Si no la tiene, explícale qué es y dónde se instala; sin ella, /subida le deja
todo listo y lo sube él.

## 2. Su marca, con una entrevista

Una pregunta cada vez, con un ejemplo de respuesta, y lo que conteste va a su fichero:

| Pregunta | Fichero |
|---|---|
| Su nombre o el de su marca, y sus cuentas de Instagram, TikTok y Facebook | `marca/marca.json` → `nombre`, `cuentas` |
| De qué va su contenido: su sector («inmobiliaria», «fitness», «IA para empresas») | `sector` |
| En qué idioma hace los vídeos y su zona horaria | `idioma`, `zona_horaria` |
| Su color de acento (el de la palabra clave y la cifra que importa) y el de las tarjetas. Si no sabe, ofrécele tres combinaciones con contraste y que elija | `colores.acento`, `colores.panel` |
| Sus letras, de las instaladas (Inter, Montserrat, Poppins para el texto; Bebas Neue o Anton para lo grande) | `letras` |
| A qué horas sube. Si no lo sabe, míralo con él en Estadísticas → «Momentos de más actividad» y propón 30 min antes de su pico; sin datos, 13:00 y 19:30 | `horas` |
| Qué pie lleva en TikTok y Facebook (por ejemplo «IG: sucuenta»), o el mismo | `pie_otras_redes` |
| Cómo habla, sus expresiones, lo que nunca diría y a quién le habla | `marca/voz.md` |
| Palabras que no quiere en sus guiones | `palabras_prohibidas` |
| Qué cuentas le inspiran y qué hacen bien. Si no tiene, no pasa nada: /guion se las busca por su sector la primera vez que pida inspiración | `marca/referentes.md` |
| Qué estilo de edición quiere por defecto y qué le gusta o no de los reels que ve | `marca/estilo.md` |

Si tiene un reel suyo que le guste, mira sus fotogramas y propón colores y letras parecidos.

## 3. Su música

Que añada unas cuantas canciones por tipo (las que suenan en los virales de su nicho y las que tiene guardadas en
Instagram), solo música que pueda usar:

```bash
herramientas/formula musica --anadir <fichero o enlace> --tipos utilidad,caso --titulo "…" --artista "…" --desde <segundo>
```

`--desde`: el segundo donde la canción suena mejor (donde la usan los virales). Los tipos, en `marca/musica.json`.

## 4. El primer vídeo

Propón uno corto (30 a 40 s) para probarlo todo: /guion para un tema que domine, que lo grabe en el móvil (de pie o
sentado, con pared lisa detrás y la cabeza a media pantalla: deja sitio arriba para los gráficos), pase los clips a
`videos/entrada/` y /edicion. Cada corrección que haga se apunta en `marca/estilo.md` o `marca/voz.md`: así cada
vídeo sale mejor que el anterior.
