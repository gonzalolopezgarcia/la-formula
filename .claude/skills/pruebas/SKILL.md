---
name: pruebas
description: Hace 5 copias de prueba de un reel ya subido para subirlas como «Reels de prueba» de Instagram (solo las ven quienes no te siguen y no salen en tu perfil), una al día durante los cinco días siguientes. Si lo grabaste en piezas (tres ganchos y dos cuerpos), cada copia es otro vídeo de verdad (otro gancho y otro cuerpo); si no, otro titular. Además cambia la velocidad, el color, el estilo de subtítulos y de gancho, y la mitad van en espejo. Úsala con «haz las pruebas», «las copias de prueba», «los trials de este reel», «déjalas para esta noche». Solo de vídeos tuyos ya aprobados y subidos. No sube el original (/subida).
---

# Pruebas: 5 copias para quien no te sigue, una al día

Un **Reel de prueba** de Instagram solo se enseña a quien no te sigue y nunca sale en tu perfil: cada copia es otra
oportunidad de que el vídeo encuentre su público, sin cansar a tus seguidores. Solo Instagram (ni TikTok ni Facebook).

## Lo que le vas contando

Una o dos líneas por paso. Por ejemplo:

- «Te voy a hacer 5 copias para Reels de prueba: solo las ve quien no te sigue y no salen en tu perfil. Como grabaste
  tres ganchos y dos cuerpos, cada una es otro vídeo: B1, C1, A2, B2 y C2.»
- «Las renderizo esta noche a las 23:00, que el ordenador está libre, y salen una al día desde mañana a las 11:00.»
- Al acabar: «Programadas las 5 como Reels de prueba, en manual, una al día. Dentro de una semana te digo cuál ha ido mejor.»

## Cuándo

- **Solo de un vídeo tuyo ya aprobado y subido** con /subida. Nunca de un borrador ni del clip de otro.
- **Una al día, los cinco días siguientes** al original, a la primera hora de `HORAS_DE_PRUEBA` (11:00, 13:00, 16:00,
  19:00, 21:00) que tengas libre ese día: libre es que no salga nada tuyo 20 minutos antes ni después.
- **Por qué una al día**: varias copias del mismo vídeo el mismo día se quedan en 0 visualizaciones, y muchas a 0
  pueden costarte alcance. Medido sobre 52 pruebas: 9 copias al día del mismo vídeo bajaron la prueba típica de unas
  3.400 vistas a 190 en una semana. Por franja, la media mañana (11-13 h) fue la mejor y la tarde (~17:45) la peor.
- 🚨 **Díselo antes de hacer nada**, con los días y la hora.
- **Se renderizan cuando diga**: ya, o «esta noche» si el ordenador está ocupado (por defecto, a las 23:00). Cada copia
  rehace el vídeo entero: unos 3 minutos por cada 45 s con el ordenador libre.

## Grabado en piezas: cada copia, otro vídeo

Si lo grabaste con /guion en piezas (tres ganchos y un `cuerpo2`) y /edicion lo preparó con `--piezas`, las copias
son las otras combinaciones de gancho y cuerpo, por este orden: **B1, C1, A2, B2, C2** (A1 es el reel normal). Cada
una lleva el titular de su gancho, su cuerpo y su canción cortada a su largo. No hace falta `ganchos-prueba.txt`.

Con tres ganchos y un solo cuerpo salen B1, C1, A1, B1, C1: se repiten, y entonces sí conviene un titular distinto en
cada copia (abajo).

## Si no se grabó en piezas: un titular distinto por copia

Cambiar solo el estilo de la caja no prueba nada; cambiar la primera frase que se lee, sí. **No se graba nada más**:
solo cambia el titular en pantalla (el `gancho`) sobre el mismo vídeo.

- Escribe `videos/trabajo/<nombre>/ganchos-prueba.txt`: 5 líneas, una por copia (` / ` parte la línea): otros ángulos
  **sacados de lo que dice en el vídeo**: un dato o resultado, curiosidad, una promesa de «cómo». Máximo 2 líneas de
  unas 5 palabras, en la misma caja que el titular del vídeo (si va en mayúsculas, en mayúsculas).
- 🚨 Enséñale los 5 y espera su sí antes de renderizar.
- Si el vídeo solo tenía el titular en la portada (`solo-portada`), la herramienta pone el nuevo los primeros 2,6 s.
- **Un vídeo que abre con su propio gráfico arriba** (un bloque desde el segundo 0) no lleva titular: lo taparía. La
  herramienta lo dice y solo cambia el estilo; no hace falta el fichero.

## Hacerlas

```bash
herramientas/formula pruebas <nombre> --hashtags "#tema1 #tema2 #tema3 #tema4 #tema5"   # --dia AAAA-MM-DD: el día de la primera
```

- Cada copia cambia, además del gancho (o el titular): la velocidad (1,03× a 1,10×, la voz sin cambiar de tono), el
  color, el estilo de los subtítulos (contorno, caja negra, amarillo, caja blanca, mayúsculas) y del gancho, y lo baja
  0, 28 o 56 px (nunca más arriba: arriba tapa Instagram). **La 2.ª y la 4.ª van en espejo** (solo tu cámara: los
  gráficos y el texto, al derecho). Fichero nuevo, sin los datos del original.
- **Hashtags**: de 5 a 10 del tema del vídeo, nunca los de alcance (#viral, #fyp). Cada copia lleva 5, en otro orden,
  debajo de su pie. El pie empieza igual que el del original: así la respuesta automática del «comenta X» también
  contesta en las pruebas (compruébalo en la herramienta que use).
- Deja en `videos/salida/pruebas/` cada `<nombre>-prueba-N.mp4` con su portada y su pie, la hoja `<nombre>-pruebas.jpg`
  (el gancho y un subtítulo de cada una) y **`<nombre>-pruebas-horario.txt`, el día y la hora de cada una**.
- Si se corta, sigue por donde iba: `--desde N --n <las que faltan>`.
- **Para dejarlas haciéndose solas esta noche** (y que sigan aunque cierres Claude), en Mac:
  `screen -dmS pruebas zsh -c 'sleep $(( $(date -j -f "%H:%M" 23:00 +%s) - $(date +%s) )); caffeinate -i herramientas/formula pruebas <nombre> --hashtags "…"'`

🚨 **Mira la hoja antes de subirlas**: texto cortado o encima de la cara, esa copia se arregla en el guion y se rehace.

## Programarlas

Con /subida, **cada una en su día y a su hora del horario**, marcando **«Reel de prueba»**:

- En Meta Business Suite, al crear el reel, si sale la opción «Reel de prueba», actívala; si no, desde la app de
  Instagram al compartir el reel.
- 🚨 **Siempre en manual**: que no se comparta sola con tus seguidores si funciona. Es la copia de un reel que ya está en
  tu perfil: lo verían dos veces.
- Si ese día ya sale algo tuyo a esa hora, la siguiente de `HORAS_DE_PRUEBA`, y se lo dices.
- Al acabar, dile cuáles quedaron programadas y cuándo, y apunta en `marca/subida.md` cómo se llama la opción.

## La primera semana

Mira el alcance y el Estado de la cuenta de Instagram. Si bajan, para: nadie sabe seguro si Instagram trata la copia
como un vídeo nuevo.
