---
name: pruebas
description: Hace 9 copias de prueba de un reel ya subido, cada una con otra velocidad, color, estilo de subtítulos y de gancho, para subirlas al día siguiente como «Reels de prueba» de Instagram (solo las ven quienes no te siguen y no salen en tu perfil). Úsala con «haz las pruebas», «las copias de prueba», «los trials de este reel», «déjalas para esta noche». Solo de vídeos tuyos ya aprobados y subidos. No sube el original (/subida).
---

# Pruebas: 9 copias para quien no te sigue

Un **Reel de prueba** de Instagram solo se enseña a quien no te sigue y nunca sale en tu perfil: cada copia es otra
oportunidad de que el vídeo encuentre su público, sin cansar a tus seguidores. Solo Instagram (ni TikTok ni Facebook).

## Lo que le vas contando

Una o dos líneas por paso. Por ejemplo:

- «Te voy a hacer 9 copias distintas del vídeo para Reels de prueba: solo las ve quien no te sigue y no salen en tu
  perfil. Cada una con otra velocidad, otro color y otro estilo de subtítulos, para que Instagram las trate como vídeos
  nuevos.»
- «Las renderizo esta noche a las 23:00, que el ordenador está libre, y mañana salen a las 08:00, 09:40, 11:15, 12:55,
  14:30, 16:10, 17:45, 19:25 y 21:00.»
- «Hechas las 9. He mirado la hoja: la 4 tapaba tu cara con el gancho y la he quitado; quedan 8.»
- Al acabar: «Programadas las 8 como Reels de prueba, en manual. Mañana te digo cuál ha ido mejor.»

## Cuándo

- **Solo de un vídeo tuyo ya aprobado y subido** con /subida. Nunca de un borrador ni del clip de otro.
- **Salen al día siguiente** del original: 9 repartidas por igual de 08:00 a 21:00, redondeadas a 5 minutos.
- 🚨 **Díselo antes de hacer nada**, con las horas: «Mañana, 9 pruebas a las 08:00, 09:40, 11:15, 12:55, 14:30, 16:10,
  17:45, 19:25 y 21:00. Las hago esta noche a las 23:00, que el ordenador está libre, y las dejo programadas».
- Si una cae a menos de 15 minutos de otra publicación suya de ese día, se mueve 15 minutos y se lo dices.
- Si mañana ya hay pruebas de otro vídeo, las de este se intercalan entre las otras.
- **Se renderizan cuando diga**: ya, o «esta noche» si el ordenador está ocupado (por defecto, a las 23:00). Cada copia
  rehace el vídeo entero: unos 3 minutos por cada 45 s con el ordenador libre.

## Hacerlas

```bash
herramientas/formula pruebas <nombre> --hashtags "#tema1 #tema2 #tema3 #tema4 #tema5"   # --dia AAAA-MM-DD si no es mañana
```

- Cada copia cambia: la velocidad (1,03× a 1,10×, la voz sin cambiar de tono), el color, el estilo de los subtítulos
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
