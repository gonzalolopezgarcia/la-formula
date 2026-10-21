---
name: subida
description: Programa un vídeo terminado en Instagram, TikTok y Facebook a la vez, a tu hora buena, desde tu propio Chrome (Claude in Chrome) - Meta Business Suite para Instagram y Facebook y TikTok Studio para TikTok, con la portada buena y el pie de cada red. Antes escribe lo que se manda a quien comenta, sobre lo que dijiste en el vídeo. Úsala con «súbelo», «prográmalo», «súbelo por la tarde», «súbelo ya», «sube este vídeo a mis redes». No edita (/edicion) ni hace las copias de prueba (/pruebas). Nunca publica sin tu sí a ese vídeo.
---

# Subida: el mismo vídeo en Instagram, TikTok y Facebook, a la vez

El último paso: /guion → /edicion → **/subida** → /pruebas. Todo desde tu Chrome con Claude in Chrome: no hace
falta ninguna API ni cuenta de desarrollador. Lee `marca/marca.json` (cuentas, horas, pie de las otras redes) y
`marca/subida.md` (lo que ya se aprendió de los botones de cada web).

🚨 **Publicar es tuyo**: se deja todo rellenado y se pulsa «Programar» o «Publicar» solo con su sí a ESE vídeo, a esa
hora. Nunca escribas su contraseña: si una web pide entrar, que entre él.

## 0. Lo que se manda, a la vez que su visto bueno

Si el vídeo acaba en «comenta X», el documento que recibe quien comenta se escribe aquí:

- **Sale de lo que dice en el vídeo** (`frases.txt` de su carpeta), no del guion: si en el vídeo cuenta cinco pasos,
  el documento construye esos cinco, con sus palabras y en su orden. Y de lo que te diga en el chat.
- El formato, el de /guion («Lo que mandas»): título, «Qué hay dentro» en cuatro puntos, lo que necesitas, los pasos,
  y lo siguiente.
- Dónde vive el enlace: un gist secreto de GitHub (`gh gist create`), una página de Notion pública o un PDF. Que
  abra bien en el móvil.
- 🚨 **Quien comenta recibe el enlace con una herramienta oficial**: las respuestas automáticas de Meta Business
  Suite (Bandeja de entrada → Automatizaciones: «cuando alguien comenta X, mándale este mensaje») o una herramienta
  homologada por Meta (ManyChat y similares). **Nunca contestes desde su Chrome**, ni a mano ni con JavaScript:
  Instagram lo detecta como comportamiento automático y puede bloquear la cuenta.
- Enséñale el documento y el mensaje junto con el resumen de la subida: su «súbelo» es el sí a todo.

## 1. Qué vídeo y a qué hora

- **El que se acaba de hacer** (`videos/salida/<nombre>.mp4`, su `.portada.png` y su `.pie.txt`) o el que diga.
- La hora real con `date`, en su zona (`marca/marca.json`).

| Dice | Hora |
|---|---|
| «por la mañana», «a mediodía» | `horas.mañana` de marca.json |
| «por la tarde», «por la noche» o nada | `horas.tarde` |
| una hora concreta | esa |
| «ya», «súbelo ya» | ahora |

- Si la de hoy ya ha pasado, la de mañana: díselo en la respuesta, no preguntes.
- **Nunca dos publicaciones a la vez** en la misma red: mira lo que ya tiene programado.
- TikTok solo deja programar entre 15 minutos y 10 días por delante.
- **Las horas se aprenden**: un poco antes del pico de su audiencia (Estadísticas de Instagram → Seguidores →
  Momentos de más actividad). Si un vídeo a una hora va mal dos veces, propón moverla; se cambia con su sí.

## 2. El pie de cada red

- **Instagram**: el del vídeo (`<nombre>.pie.txt`): una frase de qué va y la línea del «comenta X». Si no hay, escríbelo
  y enséñaselo antes.
- **TikTok y Facebook**: `pie_otras_redes` de marca.json si lo tiene (por ejemplo «IG: tucuenta»); si no, el mismo de
  Instagram.

## 3. El orden: Instagram → la respuesta automática → TikTok → Facebook → pruebas

Instagram primero: la automatización del «comenta X» va atada a la publicación, y los primeros comentarios son los
que más gente ve. Luego TikTok y Facebook a la misma hora, y al día siguiente las copias de prueba (/pruebas).

## 4. Instagram y Facebook: Meta Business Suite

Avísale de que vas a usar su Chrome. En `https://business.facebook.com` con su cuenta:

1. «Crear reel» (o Planificador → Crear → Reel). Marca **Instagram y Facebook** a la vez si quiere los dos.
2. **El vídeo, del disco**. La herramienta de subir ficheros acepta hasta 10 MB por llamada: si pesa más, pártelo
   (`split -b 9000000 <video.mp4> trozos/<nombre>.mp4.part_`), pega `herramientas/tiktok.js` (sirve igual: añade un
   campo para los trozos), sube cada trozo y júntalos con `__assemble('<nombre>.mp4')`. Comprueba que el tamaño es
   el del original.
3. **La portada**: «Portada» → subir `<nombre>.portada.png`. Nunca el fotograma que elige solo: suele salir a medio
   parpadeo.
4. **El pie**: el de Instagram; en Facebook, el de las otras redes si es distinto.
5. **Programar**: fecha y hora. Haz una captura y enséñasela con la fecha, la hora y las redes marcadas. Con su sí,
   «Programar».
6. La primera vez, apunta en `marca/subida.md` cómo se llama cada botón y dónde está: la web cambia y la próxima vez
   va directo.

## 5. TikTok: TikTok Studio

1. Abre `https://www.tiktok.com/tiktokstudio/upload?from=webapp`, espera 4 s, fija el pie que debe llevar
   (`window.__pie = "…"`) y pega `herramientas/tiktok.js` con la herramienta de JavaScript.
2. Busca el campo «formula trozos del video» (`find`) y sube cada trozo (o el mp4 si pesa menos de 10 MB), **una
   llamada por fichero**. Luego `await __up('<nombre>.mp4', <bytes del original>)`: comprueba el tamaño y espera a
   «Cargado».
3. 🚨 **La portada** (`<nombre>.portada.png`) con «Editar portada», antes de programar: un vídeo programado ya no se
   puede editar.
4. **El pie**: captura antes del primer clic (si no, el clic se pierde), clic en la descripción, seleccionar todo,
   borrar y teclear el pie.
5. **Fecha y hora**: `await __sched()` devuelve dónde está la fecha; clic ahí, `await __dayRect('Octubre', 24)` y clic
   donde diga. Un clic fuera, `__fieldRect(/^\d\d:\d\d$/)` y clic para abrir la hora, `await __time('19','30')`,
   **una captura** (sin ella la pestaña oculta no pinta y la hora no entra), Escape y un clic fuera.
6. Enséñale la captura. Con su sí, `await __go('19:30,2026-10-24')`: solo pulsa «Programar» si hora, fecha y pie son
   los que tocan; si devuelve `NO …`, repite el paso 5.
7. La primera vez TikTok pregunta por las «revisiones automáticas de contenido»: es un ajuste de su cuenta, que lo
   decida él.

Con TikTok en otro idioma, los textos que buscan las ayudas («Programación», «Programar», «Cargado») cambian:
adáptalos y apúntalo en `marca/subida.md`.

## 6. Comprobar y cerrar

- En el calendario de Meta Business Suite y en `tiktok.com/tiktokstudio/content`: el vídeo, con su fecha y hora.
- Cierra las pestañas que abriste.
- Contesta en dos líneas: qué vídeo, a qué hora y en qué redes; y, si pide «comenta X», que en TikTok esos
  comentarios los contesta él.
- Si es un vídeo normal suyo (no un clip de otro), ofrécele las copias de prueba de mañana: /pruebas.
