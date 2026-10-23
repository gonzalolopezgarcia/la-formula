---
name: pruebas
description: Hace 4 copias de prueba de un reel ya subido, cada una con otro titular, otra velocidad, color, estilo de subtítulos y de gancho, para subirlas al día siguiente como «Reels de prueba» de Instagram (solo las ven quienes no te siguen y no salen en tu perfil). Úsala con «haz las pruebas», «las copias de prueba», «los trials de este reel», «déjalas para esta noche». Solo de vídeos tuyos ya aprobados y subidos. No sube el original (/subida).
---

# Pruebas: 4 copias para quien no te sigue

Un **Reel de prueba** de Instagram solo se enseña a quien no te sigue y nunca sale en tu perfil: cada copia es otra
oportunidad de que el vídeo encuentre su público, sin cansar a tus seguidores. Solo Instagram (ni TikTok ni Facebook).

## Lo que le vas contando

Una o dos líneas por paso. Por ejemplo:

- «Te voy a hacer 4 copias distintas del vídeo para Reels de prueba: solo las ve quien no te sigue y no salen en tu
  perfil. Cada una abre con otro titular, y además cambia la velocidad, el color y el estilo de los subtítulos.»
- «Estos son los 4 titulares, sacados de lo que dices en el vídeo. ¿Te valen?» (y esperas su sí)
- «Las renderizo esta noche a las 23:00, que el ordenador está libre, y mañana salen a las 11:00, 13:00, 16:00 y 21:00.»
- Al acabar: «Programadas las 4 como Reels de prueba, en manual. Mañana te digo qué titular ha ido mejor.»

## Cuándo

- **Solo de un vídeo tuyo ya aprobado y subido** con /subida. Nunca de un borrador ni del clip de otro.
- **Salen al día siguiente** del original: 4, a las **11:00, 13:00, 16:00 y 21:00**.
- **Por qué 4 y esas horas**: medido sobre 52 pruebas, 9 copias al día del mismo vídeo bajaron la prueba típica de unas
  3.400 vistas a 190 en una semana, con algunas a 0: Instagram deja de enseñar tantas casi iguales. Por franja, la
  media mañana (11-13 h) fue la mejor y la tarde (~17:45) la peor. Mantén las mismas horas unas dos semanas, vuelve a
  medir (vistas de cada prueba frente a la mediana de su día) y mueve la peor. Las horas están en `HORAS_DE_PRUEBA`.
- 🚨 **Díselo antes de hacer nada**, con las horas: «Mañana, 4 pruebas a las 11:00, 13:00, 16:00 y 21:00. Las hago esta
  noche a las 23:00, que el ordenador está libre, y las dejo programadas».
- Si una cae a menos de 15 minutos de otra publicación suya de ese día, se mueve 15 minutos y se lo dices.
- Si mañana ya hay pruebas de otro vídeo, las de este se intercalan entre las otras.
- **Se renderizan cuando diga**: ya, o «esta noche» si el ordenador está ocupado (por defecto, a las 23:00). Cada copia
  rehace el vídeo entero: unos 3 minutos por cada 45 s con el ordenador libre.

## Primero, un titular distinto por copia

Cambiar solo el estilo de la caja no prueba nada; cambiar la primera frase que se lee, sí. **No se graba nada más**:
solo cambia el titular en pantalla (el `gancho`) sobre el mismo vídeo.

- Escribe `videos/<nombre>/ganchos-prueba.txt`: 4 líneas, una por copia (` / ` parte la línea). La 1, el titular del
  propio vídeo (la referencia); la 2 a la 4, otros tres ángulos **sacados de lo que dice en el vídeo**: un dato o
  resultado, curiosidad, una promesa de «cómo». Máximo 2 líneas de unas 5 palabras, en la misma caja que el titular
  del vídeo (si va en mayúsculas, en mayúsculas).
- 🚨 Enséñale los 4 y espera su sí antes de renderizar.
- Si el vídeo solo tenía el titular en la portada (`solo-portada`), la herramienta pone el nuevo los primeros 2,6 s.
- **Un vídeo que abre con su propio gráfico arriba** (un bloque desde el segundo 0) no lleva titular: lo taparía. La
  herramienta lo dice y solo cambia el estilo; no hace falta el fichero.

## Hacerlas

```bash
herramientas/formula pruebas <nombre> --hashtags "#tema1 #tema2 #tema3 #tema4 #tema5"   # --dia AAAA-MM-DD si no es mañana
```

- Cada copia cambia, además del titular: la velocidad (1,03× a 1,10×, la voz sin cambiar de tono), el color, el estilo de los subtítulos
  (contorno, caja negra, amarillo, caja blanca, mayúsculas) y del gancho, y lo baja 0, 28 o 56 px (nunca más arriba:
  arriba tapa Instagram). Fichero nuevo, sin los datos del original. En un mismo vídeo no se repite combinación.
- **Hashtags**: de 5 a 10 del tema del vídeo, nunca los de alcance (#viral, #fyp). Cada copia lleva 5, en otro orden,
  debajo de su pie. El pie empieza igual que el del original: así la respuesta automática del «comenta X» también
  contesta en las pruebas (compruébalo en la herramienta que use).
- Deja en `videos/salida/pruebas/` cada `<nombre>-prueba-N.mp4` con su portada y su pie, la hoja `<nombre>-pruebas.jpg`
  (el gancho y un subtítulo de cada una) y **`<nombre>-pruebas-horario.txt`, la hora de cada una**.
- Si se corta, sigue por donde iba: `--desde N --n <las que faltan>`.
- **Para dejarlas haciéndose solas esta noche** (y que sigan aunque cierres Claude), en Mac:
  `screen -dmS pruebas zsh -c 'sleep $(( $(date -j -f "%H:%M" 23:00 +%s) - $(date +%s) )); caffeinate -i herramientas/formula pruebas <nombre> --hashtags "…"'`

🚨 **Mira la hoja antes de subirlas**: texto cortado o encima de la cara, esa copia fuera.

## Programarlas

Con /subida, **cada una a su hora del horario**, marcando **«Reel de prueba»**:

- En Meta Business Suite, al crear el reel, si sale la opción «Reel de prueba», actívala; si no, desde la app de
  Instagram al compartir el reel.
- 🚨 **Siempre en manual**: que no se comparta sola con tus seguidores si funciona. Es la copia de un reel que ya está en
  tu perfil: lo verían dos veces.
- Al acabar, dile cuáles quedaron programadas y a qué hora, y apunta en `marca/subida.md` cómo se llama la opción.

## La primera semana

Mira el alcance y el Estado de la cuenta de Instagram. Si bajan, para: nadie sabe seguro si Instagram trata la copia
como un vídeo nuevo.
