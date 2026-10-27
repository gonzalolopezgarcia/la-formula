---
name: guion
description: Escribe el guion de un reel hablado a cámara, con las reglas de los que funcionan. Tres modos según lo que digas - (1) INSPIRACIÓN («busca inspiración», o sin tema ni enlace) mira los reels recientes que mejor van de tus referentes y te propone tres; (2) TEMA («hazme el guion de X») comprueba si el tema puede funcionar, elige el molde y te da tomas numeradas con tres ganchos que se graban los tres y un segundo cuerpo (lo mismo dicho de otra forma), para sacar seis vídeos de una grabación; (3) COPIA (un enlace, «cópiame este reel») traduce ese reel frase a frase, entero y en orden. Úsala con «hazme el guion», «qué digo en el reel de X», «busca inspiración», «cópiame este reel», «escríbeme el vídeo de X». Deja listo el pie, lo que se manda por privado y los titulares para /edicion. No edita (/edicion) ni sube (/subida).
---

# Guion: lo que dices y cómo lo cuentas

Lo que hace que un reel funcione no es la edición: es de qué hablas y cómo lo cuentas. En las cuentas de
creadores de IA medidas, unos pocos reels suman casi todas las visualizaciones, y casi todos acaban en «comenta X
y te lo mando».

Antes de escribir, lee `marca/voz.md` (cómo hablas, tus expresiones, lo que nunca dirías), `marca/lecciones.md`
(lo que ya sabemos de tus vídeos publicados) y, en modo inspiración, `marca/referentes.md`. Los moldes al detalle:
`moldes.md`. Escribe en el idioma de `marca/marca.json`.

## Lo que le vas contando

Una o dos líneas por paso, con lo que has hecho de verdad. Por ejemplo:

- «Voy a mirar los últimos reels de tus 4 referentes para ver qué les está funcionando.» → «He mirado 112 reels: estos
  3 van por encima de 5 veces su mediana. Te propongo el 2, que encaja con lo que tú puedes enseñar.»
- «Antes de escribir, compruebo si el tema puede funcionar.» → «Tiene nombre, es gratis y se ve funcionando: tiene
  gancho. Lo haría como un `capacidad` de 45 s.»
- «He comprobado las 4 cifras del guion en su web oficial: todas cuadran, te dejo las fuentes.»
- «Te dejo 3 ganchos, cada uno engancha por algo distinto: el 1 por dinero, el 2 por sorpresa y el 3 por ti. Te
  recomiendo el 1.»
- Al acabar: «Grábalo con tus palabras, cada toma por separado, y pásame los clips a `videos/entrada/`: te lo edito yo.»

## Primero: qué guion pide

| Dice | Modo | Qué haces |
|---|---|---|
| «busca inspiración», o ni tema ni enlace | **Inspiración** | Lo que mejor va de sus referentes, tres propuestas, elige y lo escribes con sus palabras |
| Un tema: «hazme el guion de X» | **Tema** | El guion desde cero con los moldes |
| Un reel concreto: un enlace, «cópiame este» | **Copia** | Ningún guion tuyo: ese reel, frase a frase, traducido |

Lo deciden sus palabras: no preguntes cuál. Un tema más «busca inspiración» es Inspiración solo de ese tema.

## Inspiración

0. 🚨 **Sin referentes no se busca a ciegas.** La Fórmula llega sin sector ni cuentas: si `marca/referentes.md`
   está vacío, primero una pregunta, «¿De qué va tu contenido, o en qué cuentas te fijas?».
   - **Si te da cuentas**, van a `referentes.md` y sigues.
   - **Si te da su sector**, apúntalo en `marca/marca.json` → `sector` y búscalas tú: en su Chrome, el buscador de
     Instagram con dos o tres palabras de su sector, en su idioma y en inglés («inmobiliaria», «real estate
     agent»). Los reels que salen son los que mejor van: de sus cuentas, las que hablan a cámara como él; de
     cada una, su rejilla con `vistas-rejilla.js` (paso 2) y su mediana. Propón cinco en una tabla (cuenta,
     seguidores, mediana de vistas, qué hace bien) y, con su sí, a `referentes.md`.
   - Nunca cuentas de otro sector «por si acaso»: la inspiración vale si su público es como el suyo.
1. Avísale de que vas a usar su Chrome (Claude in Chrome); todo es de lectura. A ritmo de persona: una cuenta cada
   vez, en una pestaña, cinco como mucho por sesión (Meta marca lo automático: /subida). Lo que ya leíste esta semana
   no se vuelve a leer.
2. La rejilla de cada cuenta de `marca/referentes.md` en `instagram.com/<cuenta>/reels/`, pegando
   `herramientas/vistas-rejilla.js` con la herramienta de JavaScript: el código y las visualizaciones de cada reel
   y su mediana.
3. **Candidatos**: reels recientes por encima de la mediana de su cuenta, de más a menos. Fuera las noticias
   caducadas, lo que no puede enseñar funcionando y los temas que ya tiene.
4. **Tres propuestas** en una tabla: número, cuenta y enlace, visualizaciones (y su mediana), de qué va, su gancho
   traducido y qué molde es. Contesta con un número.
5. **La elegida se escribe como un guion de Tema** con ese reel de modelo: su forma y su tipo de gancho, con sus
   palabras, sus datos y lo que puede enseñar. Nunca la frase del otro tal cual (si dice «cópialo», es Copia).

## Copia: el guion es ese reel, frase a frase

No se escribe guion: se traduce el suyo. Cada frase que dice, en su orden, entera y en su idioma. Nada se resume,
se junta, se quita ni se añade, y no se aplican las reglas de abajo: ese reel ya ha demostrado que funciona.

1. **Bájalo y transcríbelo**, cada uno en su carpeta:
   ```bash
   mkdir -p videos/estudio/<código> && herramientas/.venv/bin/yt-dlp -q -o "videos/estudio/<código>/v.%(ext)s" \
     --ffmpeg-location herramientas/.bin "https://www.instagram.com/reel/<código>/"
   herramientas/formula-estudiar videos/estudio
   ```
   Deja `transcript.txt` con cada frase y su segundo. Si Whisper parte las frases por la mitad, rehazlo con una
   frase por línea desde `palabras.json`; una de 30 palabras o más se puede partir en la coma donde cambia la
   idea, para grabarla en dos tomas. Luego mira sus fotogramas cada 0,5 s (`ffmpeg -i v.mp4 -vf
   "fps=2,scale=216:384,tile=6x4" hoja-%02d.jpg`): de ahí salen sus escenas y lo que se ve.
2. **`hablado.json` con `copia`**: un solo gancho (su primera frase traducida; en `pantalla`, su gancho de pantalla
   traducido) y **una toma por línea de su transcripción**, con `original` (la suya, tal cual) y `texto` (la
   traducción). El `titular` es su titular de pantalla traducido y la `pantalla`, su gráfico en ese segundo: así
   /edicion lo calca.
   **Sus escenas también**: `escena` en el gancho o la toma donde empieza cada una: el sitio, el plano (selfie con
   el 0,5×, plano abierto desde un trípode), lo que hace (andar, comprar algo, comérselo) y dónde cae el corte
   («corte en "La número uno"»). Al darle el guion, cada escena va como una línea encima de su toma: así lo graba igual.
3. Lo único que cambia sin preguntar: la palabra del «comenta X» pasa a ser la de lo que tú mandas, **una sola**
   aunque el original pida dos. Cada cambio va en `cambio` en esa toma, con el motivo. Una palabra suya que tu
   público no conoce («slop») va en tu idioma («genérico»), en todas partes. Si algo suyo no te vale (una cifra que no
   es tuya, «mi empresa», una herramienta que no tienes), no se toca: pregúntaselo al darle el guion y, con su sí,
   pasa a lo que sí tiene, con la misma idea («un MCP que busca virales» → «una skill que busca virales»).
4. El comprobador (paso 6) en modo copia falla si falta una frase suya, sobra una, van en otro orden o una
   traducción tiene menos del 70 % de sus palabras.

## Tema: el guion desde cero

### 🚨 Antes del guion: ¿puede funcionar el tema?

Un guion perfecto sobre un tema flojo no despega. Cinco preguntas; con dos «no», dile en una línea cómo darle la vuelta:

| | Sí | No |
|---|---|---|
| ¿Tiene nombre? | Una herramienta, una skill, un modelo | Un consejo o una opinión |
| ¿Lo que ganas cabe en la primera frase? | Dinero, clientes, tiempo o no parecer amateur | «Mejores resultados» |
| ¿Es nuevo o gratis? | Recién salido, de código abierto, lo regalan | Lo que ya ha visto todo el mundo |
| ¿Se ve funcionando? | Tu pantalla, el prompt y lo que devuelve | Tú hablando 50 s sin enseñar nada |
| ¿Hay algo que mandar que ahorra el trabajo? | «Un solo mensaje para pegar que lo instala todo» | «Más información» |

Poner «comenta X» por sí solo no mueve nada: lo que funciona es lo que se manda.

### 🚨 Todo vídeo cierra la idea

**Cada guion lleva una toma `conclusion`**, la última antes de lo que mandas (o del «sígueme»): una frase que se
lleva quien mira. O lo que tiene que hacer, o la idea en limpio. **Contesta al gancho**: lo que el gancho abrió,
la conclusión lo cierra con palabras parecidas. Si al grabar no la dice, díselo antes de editar, con la frase.

### 🚨 Se graban los tres ganchos y un segundo cuerpo

Para las pruebas (/pruebas) hacen falta vídeos distintos de verdad, no el mismo con otro titular: cinco copias casi
iguales se quedan en 0 visualizaciones. Así que cada guion de Tema o de Inspiración se graba en piezas y /edicion saca
hasta seis vídeos (3 ganchos × 2 cuerpos): el gancho 1 con el cuerpo 1 es el reel normal y los otros cinco, sus
pruebas, una al día.

- **Los tres ganchos se graban**, cada uno con su frase 2 (`puente`). El 1 va en el reel normal: ninguno es de
  relleno.
- **El cuerpo 2 (`cuerpo2`)**: la misma información que el cuerpo 1, **con otras palabras y en otro orden**. Lleva
  las mismas `parte`, empieza por otra (el resultado, el ejemplo) y ninguna frase es igual que en el 1: el
  comprobador avisa. Dura parecido (±25 %) y no lleva `puente`, `conclusion`, `iman` ni `cta`: el cierre es uno para
  los dos cuerpos y se graba una vez, así que tiene que contestar a los tres ganchos.
- Si el tema no da para dos formas (un `regalo` de 20 s, una historia contada en su orden), sin `cuerpo2`: las
  pruebas combinan los tres ganchos con recortes de ese cuerpo (uno rápido y uno exprés, por frases enteras) o, en
  una lista, con los puntos en otro orden (/pruebas). Díselo. Para que se pueda recortar, cada frase se entiende
  sola: que ninguna diga «como te he dicho» ni dependa de una de relleno.
- En una `lista` las pruebas solo pueden cambiar el orden de los puntos si la voz no los numera: con «El número
  uno es…» (como en el molde) se recorta dentro de cada punto. Si no tiene `cuerpo2`, pregúntale cuál prefiere.
- **Cómo se graba: tres clips.** El 1, los tres ganchos seguidos (cada uno con su frase 2); el 2, el cuerpo 1 y el
  cierre; el 3, el cuerpo 2. Una pausa entre pieza y pieza.
- Una **Copia** se queda con su único gancho y sin `cuerpo2`: es su reel, frase a frase.

### 🚨 El gancho da una razón para pararse, no resume el reel

La prueba: **¿se pararía alguien que no sabe nada del tema?** Cada gancho lleva escrita su razón (`para`) y, de los
tres que le das, cada uno engancha por una distinta:

| `para` | Por qué te paras |
|---|---|
| `imposible` | Algo que no sabías que ya se puede, o que inquieta |
| `dinero` | Dinero ganado, ahorrado o quemado, con su cifra |
| `gratis` | Regalan algo que cuesta |
| `identidad` | Una frase sobre ti que no se espera |
| `perdida` | Te estás quedando atrás o lo haces mal |
| `drama` | Una pelea o un giro entre grandes |
| `secreto` | Algo que casi nadie cuenta |

- **Rotundo**: «nunca abro el chat», no «casi nunca»; «lo estás usando mal», no «te estás perdiendo cosas». Lo suyo
  (sus horas, sus costumbres) se dice a lo grande; lo que quien mira va a probar (qué hace la herramienta, un
  «gratis», un precio, dinero ganado) se comprueba.
- **Nunca es gancho**: un dato técnico (precio, tokens, «la versión nueva»), un deber («tienes que probar»,
  «deberías») ni el resumen de lo que viene («te cuento qué es»). Eso va dentro.
- **De dónde sale cada gancho, por orden**: los suyos que ya funcionaron (3 veces su mediana o más, en
  `marca/lecciones.md`), rehechos casi con las mismas palabras; la forma del gancho de un viral de sus referentes,
  con palabras nuevas; uno nuevo con el `para` que mejor encaje.
- **Los cuatro fallos**, gancho a gancho: **llega tarde** (palabras antes de lo que importa), **se enreda** (hay que
  oírlo dos veces: dos ideas, una palabra abstracta), **no va de ti** (quien mira no se ve dentro) y **sin intriga**
  (se entiende y aun así se pasa: no abre un «¿cómo?»).
- **Una palabra que no conoce todo el mundo** (MCP, «ingeniería inversa») no va en el gancho: primero lo que ganas
  y el nombre, en la frase 2. Claude, ChatGPT o Excel sí: los conoce cualquiera.
- **Concreto**: una cosa con nombre, una cifra o algo que se ve. «Una app» no engancha; «Photoshop», sí.

### Los pasos

1. **Elige el molde** (`moldes.md`): capacidad, lista, caso, regalo, sistema, comparación, personal o reacción.
2. **Comprueba los datos antes de escribirlos.** Cada cifra, cada «gratis», cada «es de Anthropic» y cada precio,
   en su fuente ese mismo día, apuntado en `fuentes`. Lo que no se puede comprobar, fuera. Un prompt que se dice en
   el vídeo se ha probado antes. Nunca una cifra de dinero que no ha ganado.
3. **Nada en primera persona** («yo le dije», «a mí me tardó») sin preguntarle si lo ha probado. Sin prueba, el
   ejemplo va como «Por ejemplo, dile…».
4. **Escribe `hablado.json`** en `videos/trabajo/<AAAA-MM-DD-tema>/`, la misma carpeta donde luego edita /edicion.
5. **Léelo entero como alguien que no sabe nada del tema**: cada frase sale de la anterior; si la herramienta hace
   algo abstracto, una comparación del día a día. Cada palabra técnica, con lo que es en una frase normal.
6. **Pasa el comprobador** y arregla todo lo que diga (si dejas un aviso a propósito, dile cuál y por qué):
   ```bash
   herramientas/formula-guion videos/trabajo/<carpeta>/hablado.json
   ```
7. **Dáselo para grabar**: en el chat, los tres ganchos (cada uno con su frase 2, el 1 marcado: va en el reel
   normal), luego las tomas numeradas y «Cuerpo 2» al final, todo para grabar en tres clips. Que lo grabe con sus palabras: luego se edita sobre lo que dijo de verdad (`frases.txt`).
8. **Cuando mande los vídeos**: /edicion. Cruza `frases.txt` con `hablado.json`: qué tomas dijo, cuáles se saltó y
   qué añadió. Lo que añadió con una cifra o un «gratis» se comprueba antes de ponerlo en pantalla. Si no cerró la
   idea, díselo antes de editar.
9. **A los 7 días de publicarlo**, una fila en `marca/lecciones.md`: las visualizaciones (de su rejilla, con
   `herramientas/vistas-rejilla.js`) contra su mediana. Si lo dobla o se queda por debajo de 0,6 veces, tres
   líneas: qué pasó en los 3 primeros segundos, por qué creemos que pasó («probable», «posible»: un reel es un dato,
   no una prueba) y qué se repite o se cambia.

## Las reglas, medidas en reels que funcionan

| | Regla |
|---|---|
| Gancho dicho | Una razón para pararse, en 17 palabras como mucho (26 en `caso` y `comparacion`, 14 en `regalo`, 12 en `sistema`), con lo que importa delante: un nombre que conoce todo el mundo, la cifra, «Uso…», «Ayer dejé que…» |
| Lo que nunca abre | Un saludo, una pregunta, «hoy os traigo», «en este vídeo» |
| Gancho en pantalla | Dos líneas, de 3 a 6 palabras, sin emoji. Promete; no repite lo que dice la voz |
| Tres ganchos | Cada uno con un `para` distinto y **su propio puente**. Se graban los tres: uno por prueba |
| Segunda frase | Un puente de 5 a 9 palabras que mantiene la intriga o promete el cómo: «Así se monta». Sale de lo que dice su gancho |
| Frases | Una idea cada una y 20 palabras como mucho (hablando sin guion salen de 26 a 42: pártelas) |
| Ritmo | ~4,4 palabras por segundo ya editado: 200 palabras son 45 s |
| Prompts | Dichos enteros y como una orden: «dile: sácame todas las…» |
| Resultados | Cada uno con su cifra o su tiempo, real |
| Cabo suelto | A mitad, si hay enlace o comando: «te lo mando al final». Entre el 25 y el 40 % del reel |
| Cierre que vuelve al gancho | Lo que mandas o el cierre repite las palabras o la imagen del gancho |
| Del lado de quien mira | Ninguna frase le llama vago, le culpa ni le asusta sin decir cómo salir |
| Lo que mandas | Qué es, qué lleva y que ahorra trabajo, justo antes del cierre |
| Cierre | «Sígueme, comenta X y te lo envío por privado», 14 palabras como mucho. X es una sola palabra, del tema |
| Pie | Una frase de qué va el reel y, debajo, la línea del «comenta X» |
| Intriga | Tras el gancho no se adivina el resto; lo que se abre se cierra antes del «comenta X» |
| Suena a ti | Tapa tu nombre: si cualquiera podría decirlo, busca la frase que solo dirías tú y ponla delante |
| Frases de IA | Fuera «No es X, es Y», «y eso lo cambia todo», «la clave está en», «en definitiva»… (el comprobador avisa) |
| Cifras | Cada cifra dicha, en `fuentes`; «gratis» solo si eso mismo funciona sin plan de pago ni clave |
| Palabra del «comenta X» | Nunca una ya usada ni una parecida: los reels viejos siguen recibiendo comentarios. Fácil de teclear en el móvil y que nadie comente por su cuenta («top», «genial») |
| Tus palabras prohibidas | Las de `marca/marca.json`: el comprobador las vigila |

🚨 **Lo que más hay que vigilar: las frases largas.** Hablando sin guion salen de 20 a 42 palabras, unidas con «ya
sea», «por lo que», «y como es lógico». Pártelas: sujeto, verbo, punto.

## Lo que mandas (el imán)

Se escribe al aprobar el vídeo (/subida), **sobre lo que dijo de verdad** (`frases.txt`), no sobre el guion. Aquí
solo apunta en `cta.manda` qué es. El formato: **un solo problema, resuelto entero**:

- el título y debajo una frase que le dice a quien comenta que está en el sitio correcto;
- «Qué hay dentro»: cuatro puntos, cada uno algo que va a poder hacer;
- lo que necesita y los pasos numerados, con lo que se copia en bloques de copiar;
- al final, el siguiente problema con el que se va a encontrar y un paso honesto («sígueme, que el siguiente es…»).
- Si lo que mandas es un prompt que construye algo, que el Claude de quien lo pegue pregunte una cosa cada vez y
  espere la respuesta: así se adapta a su caso.

## El fichero

`hablado.json`. El gancho elegido es la frase 1; las `tomas` son el resto, en orden.

```json
{
  "nombre": "2026-10-20-tema",
  "tema": "Lo que cuenta, en una línea",
  "molde": "capacidad | lista | caso | regalo | sistema | comparacion | personal | reaccion",
  "cta": { "palabra": "UNA", "manda": "qué es y qué lleva dentro", "fichero": "videos/trabajo/…/una.md" },
  "ganchos": [ { "para": "imposible", "dicho": "La frase que dices", "pantalla": "DOS LÍNEAS|EN PANTALLA", "puente": "Tu frase 2, que sale de esta" } ],
  "tomas": [ { "parte": "puente", "texto": "Lo que dices", "titular": "De 2 a 5 palabras", "pantalla": "qué se ve o qué captura hace falta" } ],
  "cuerpo2": [ { "parte": "resultado", "texto": "Lo mismo que el cuerpo 1, con otras palabras y en otro orden", "titular": "…", "pantalla": "…" } ],
  "fuentes": [ "De dónde sale cada cifra y cada «gratis», con su fecha" ],
  "pie": "Una frase.\n\nSígueme y comenta UNA y te envío … por privado."
}
```

Las `parte`: `puente`, `que-es`, `hueco` (lo que le pasa hoy a casi todo el mundo), `paso`, `punto` (los de una
lista), `resultado`, `por-que`, `prueba`, `conclusion`, `iman` (lo que mandas) y `cta`. El `titular` resume, no
transcribe: es lo que /edicion pone arriba. `cuerpo2` es opcional: las tomas entre el puente y el cierre, dichas de
otra forma («Se graban los tres ganchos y un segundo cuerpo»).

## Tus correcciones

Cada vez que corrija un guion («ese gancho no», «esto no se entiende»), apúntalo en `marca/voz.md` con su fecha y
qué se hace desde entonces. Es lo que hace que el siguiente guion salga a la primera.
