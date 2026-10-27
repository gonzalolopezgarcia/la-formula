---
name: pruebas
description: Hace 5 copias de prueba de un reel ya subido para subirlas como «Reels de prueba» de Instagram (solo las ven quienes no te siguen y no salen en tu perfil), una al día durante los cinco días siguientes. Si lo grabaste en piezas, cada copia es otro vídeo de verdad: con tres ganchos y dos cuerpos, otra combinación; con tres ganchos y un cuerpo, cada gancho con otro recorte del cuerpo (o, en una lista, los puntos en otro orden); si no, otro titular. Además cambia la velocidad, el color, el estilo de subtítulos y de gancho, y dos van en espejo (sin voltear lo que la cámara graba con letras). Úsala con «haz las pruebas», «las copias de prueba», «los trials de este reel», «déjalas para esta noche». Solo de vídeos tuyos ya aprobados y subidos. No sube el original (/subida).
---

# Pruebas: 5 copias para quien no te sigue, una al día

Un **Reel de prueba** de Instagram solo se enseña a quien no te sigue y nunca sale en tu perfil: cada copia es otra
oportunidad de que el vídeo encuentre su público, sin cansar a tus seguidores. Solo Instagram (ni TikTok ni Facebook).

## Lo que le vas contando

Una o dos líneas por paso. Por ejemplo:

- «Te voy a hacer 5 copias para Reels de prueba: solo las ve quien no te sigue y no salen en tu perfil. Como grabaste
  tres ganchos y dos cuerpos, cada una es otro vídeo: B1, C1, A2, B2 y C2.»
- O con un solo cuerpo: «Grabaste tres ganchos y un cuerpo: te saco dos cuerpos más de tus frases, uno rápido (1:21)
  y uno exprés (0:59), y cada copia es otro gancho con otro cuerpo: B1, C2, A3, B2 y C3.»
- «Las renderizo esta noche a las 23:00, que el ordenador está libre, y salen una al día desde mañana a las 11:00.»
- Al acabar: «Programadas las 5 como Reels de prueba, en manual, una al día. Cuando salga la última, miramos cuál ha
  ido mejor: ese gancho nos dice qué engancha a quien no te conoce.»

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

## Los trucos: que cada copia sea otro vídeo de verdad

Cinco copias casi iguales se quedan en 0. Lo que más cambia una copia, de más a menos: **otro gancho dicho**, **otro
cuerpo** (otras palabras, más corto o en otro orden), **otro titular arriba** y, encima de todo, el estilo (velocidad,
color, subtítulos, espejo). Usa todo lo que dé la grabación:

| Grabó | Las 5 copias | Cómo |
|---|---|---|
| 3 ganchos + 2 cuerpos | **B1, C1, A2, B2, C2**: las seis combinaciones menos el reel normal (A1) | `preparar --piezas` (/edicion) ya las deja hechas |
| 3 ganchos + 1 cuerpo | **B1, C2, A3, B2, C3**: cada gancho con otro recorte del cuerpo, ninguna pareja repetida | Dos cuerpos más hechos de sus frases (abajo) |
| 1 gancho + 1 cuerpo | **Otro titular** en cada copia y, mejor, con dos recortes del cuerpo (o, en una lista, otro orden): A2, A3, A1, A2, A3 | `ganchos-prueba.txt` (abajo); los recortes, con `--piezas "A=0,1=<donde empieza el cuerpo>"` y `--cuerpos` |

### 🚨 Un solo cuerpo: los otros dos salen de él

Con un cuerpo grabado no se repite el mismo cinco veces: se hacen dos más **cortando por frases enteras**, sin
grabar nada:

- **Rápido (~80 %)**: fuera los comentarios de paso, las repeticiones y lo que se ve sin que lo diga (un segundo
  dictado igual que el primero, «aquí está pensando»).
- **Exprés (~60 %)**: solo los pasos y el resultado. Que se entienda solo: si un paso nombra algo de una frase
  quitada, esa frase vuelve.
- **Una lista** («5 hábitos», «3 herramientas»): en vez de recortar, **otro orden de los puntos**, con estructura:
  el menos de nicho primero, el más de nicho al final y lo que va antes de otra cosa, antes. Solo los del medio se
  mueven. 🚨 Solo si ni la voz ni la pantalla los numeran («el primero», «1.» en el titular): si los numeran,
  recorta en vez de reordenar.

Se hacen en /edicion, al preparar: lee `piezas.txt` (cada palabra con su número), decide los tramos y pásalos:

```bash
herramientas/formula preparar <nombre> --piezas "A=0,B=13,C=27,1=47,cierre=561" \
  --cuerpos "2=47-155,165-305,360-456,476-560;3=47-80,148-155,165-198,256-305,360-456,476-526,541-560"
```

Cada cuerpo nuevo son los tramos del 1 que dice, **en el orden en que los pones** (para una lista, ponlos en el
nuevo orden). Cada número es una palabra de `piezas.txt`; uno solo («57») es la frase que empieza ahí. `preparar`
imprime cuánto dura cada uno y cómo empieza cada tramo: compruébalo antes de seguir. El guion de esos cuerpos sale
solo del de la pieza 1 (cada bloque con su frase; el de una frase quitada, fuera); **mira los fotogramas de una copia
de cada cuerpo** (`formula foto`) antes de hacerlas.

Si ya se preparó en piezas sin `--cuerpos`, pasa `preparar` otra vez igual pero con él (no transcribe de nuevo) y
vuelve a `armar`: el reel normal (A1) sale igual.

### Un gancho que vuelve: otro titular

En B1, C2, A3, B2, C3 los ganchos B y C salen dos veces. La segunda vez, **otro titular arriba** con otro ángulo de
lo mismo: escribe `ganchos-prueba.txt` con los cinco (el de cada copia, en su orden; abajo, cómo) y enséñaselos.
Sin el fichero, cada copia lleva el titular de su gancho.

## Un titular distinto por copia (sin piezas, o un gancho que vuelve)

Cambiar solo el estilo de la caja no prueba nada; cambiar la primera frase que se lee, sí. **No se graba nada más**:
solo cambia el titular en pantalla (el `gancho`) sobre el mismo vídeo.

- Escribe `videos/trabajo/<nombre>/ganchos-prueba.txt`: 5 líneas, una por copia (` / ` parte la línea): otros ángulos
  **sacados de lo que dice en el vídeo**: un dato o resultado, curiosidad, una promesa de «cómo». Máximo 2 líneas de
  unas 5 palabras, en la misma caja que el titular del vídeo (si va en mayúsculas, en mayúsculas).
  - **Grabado en piezas**: la línea de cada copia es el titular de su gancho (`pantalla` en `hablado.json`) y, si
    ese gancho ya salió en otra copia, otro ángulo de lo mismo: que no haya dos iguales.
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
- 🚨 **El espejo y las letras grabadas**: si la cámara graba algo con letras (su pantalla, un cartel, una camiseta),
  en espejo sale del revés. Mira los fotogramas: esos tramos van en `--pantallas "120-135,200-210"` (las palabras que
  dice mientras se ve, de `piezas.txt` o `frases.txt`) y ahí la copia no se voltea.
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
- 🚨 **Si no sale en ningún sitio, su cuenta aún no la tiene**: hace falta cuenta profesional (creador o empresa) y,
  con pocos seguidores, Meta puede no darla (una cuenta de ~140 seguidores la tenía bloqueada; con ~4.000, sí).
  Díselo, no renderices copias que no se van a poder subir, y que vuelva a mirar cuando crezca.
- Mismo cuidado que en /subida con Meta: subirlas a ritmo de persona, una detrás de otra, nunca varias pestañas a la
  vez.
- 🚨 **Siempre en manual**: que no se comparta sola con tus seguidores si funciona. Es la copia de un reel que ya está en
  tu perfil: lo verían dos veces.
- Si ese día ya sale algo tuyo a esa hora, la siguiente de `HORAS_DE_PRUEBA`, y se lo dices.
- Al acabar, dile cuáles quedaron programadas y cuándo, y apunta en `marca/subida.md` cómo se llama la opción.

## La primera semana

Mira el alcance y el Estado de la cuenta de Instagram. Si bajan, para: nadie sabe seguro si Instagram trata la copia
como un vídeo nuevo.

## Cuál ganó

Las pruebas no salen en tu rejilla: sus vistas, en la app (Panel profesional → tu contenido, o en cada prueba). Al día
siguiente de la última, una fila en `marca/lecciones.md` con las vistas de cada copia y su combinación. El gancho (o el
cuerpo) de la que más saca es lo que engancha a quien no te conoce: /guion empieza por ese tipo de gancho la próxima
vez. Con una prueba sola es una pista; si el mismo tipo gana tres veces, es una regla.
