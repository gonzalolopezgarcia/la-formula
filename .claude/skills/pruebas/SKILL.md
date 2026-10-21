---
name: pruebas
description: Hace 9 copias de prueba de un reel ya subido, cada una con otra velocidad, color, estilo de subtítulos y de gancho, para subirlas al día siguiente como «Reels de prueba» de Instagram (solo las ven quienes no te siguen y no salen en tu perfil). Úsala con «haz las pruebas», «las copias de prueba», «los trials de este reel», «déjalas para esta noche». Solo de vídeos tuyos ya aprobados y subidos. No sube el original (/subida).
---

# Pruebas: 9 copias para quien no te sigue

Un **Reel de prueba** de Instagram solo se enseña a quien no te sigue y nunca sale en tu perfil: cada copia es otra
oportunidad de que el vídeo encuentre su público, sin cansar a tus seguidores. Solo Instagram (ni TikTok ni Facebook).

## Cuándo

- **Solo de un vídeo tuyo ya aprobado y subido** con /subida. Nunca de un borrador ni del clip de otro.
- **Salen al día siguiente** del original, repartidas de 08:00 a 21:00.
- **Se renderizan cuando digas**: ya, o «esta noche» si el ordenador está ocupado. Cada copia rehace el vídeo entero:
  unos 3 minutos por cada 45 s con el ordenador libre.

## Hacerlas

```bash
herramientas/formula pruebas <nombre> --hashtags "#tema1 #tema2 #tema3 #tema4 #tema5"
```

- Cada copia cambia: la velocidad (1,03× a 1,10×, la voz sin cambiar de tono), el color, el estilo de los subtítulos
  (contorno, caja negra, amarillo, caja blanca, mayúsculas) y del gancho, y lo baja 0, 28 o 56 px (nunca más arriba:
  arriba tapa Instagram). Fichero nuevo, sin los datos del original. En un mismo vídeo no se repite combinación.
- **Hashtags**: de 5 a 10 del tema del vídeo, nunca los de alcance (#viral, #fyp). Cada copia lleva 5, en otro orden,
  debajo de su pie.
- Deja en `videos/salida/pruebas/` cada `<nombre>-prueba-N.mp4` con su portada y su pie, y la hoja
  `<nombre>-pruebas.jpg` (el gancho y un subtítulo de cada una).
- Si se corta, sigue por donde iba: `--desde N --n <las que faltan>`.
- **Para dejarlas haciéndose solas** (y que sigan aunque cierres Claude):
  `screen -dmS pruebas caffeinate -i herramientas/formula pruebas <nombre> --hashtags "…"` (en Mac; en Linux sin
  `caffeinate`).

🚨 **Mira la hoja antes de subirlas**: texto cortado o encima de la cara, esa copia fuera.

## Subirlas

Con /subida, una a una y repartidas de 08:00 a 21:00 del día siguiente, marcando **«Reel de prueba»**:

- En Meta Business Suite, al crear el reel, si sale la opción «Reel de prueba», actívala.
- Si no sale, desde la app de Instagram: al compartir el reel, «Reel de prueba».
- 🚨 **Siempre en manual**: que no se comparta solo con tus seguidores si funciona. Es la copia de un reel que ya está
  en tu perfil: lo verían dos veces.
- Apunta en `marca/subida.md` cómo se llama la opción la primera vez.

## La primera semana

Mira el alcance y el Estado de la cuenta de Instagram. Si bajan, para: nadie sabe seguro si Instagram trata la copia
como un vídeo nuevo.
