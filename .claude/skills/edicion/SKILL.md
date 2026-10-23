---
name: edicion
description: Edita un reel a partir de tus clips hablando a cámara, con gráficos animados encima que prueban lo que dices, subtítulos, música y efectos de sonido, todo en tu ordenador y gratis. Cuatro estilos - «encima» (tú a pantalla entera y el gráfico arriba), «partida» (pantalla partida, el gráfico en un panel), «clip» (el clip de otro arriba y tú reaccionando) y «vlog» (un día de tu vida con tu voz encima). Úsala cuando digas «edítame el vídeo», «edita estos clips», «hazme el reel», «el vídeo de hoy», «edítalo estilo partida», «haz el vlog», o pases unos clips. Corta silencios y tomas repetidas, escribe el guion visual sobre lo que dijiste de verdad, lo revisa fotograma a fotograma y te enseña un borrador antes del final. No escribe el guion hablado (/guion) ni lo sube (/subida).
---

# Edición: tus clips, con gráficos que prueban lo que dices

Hablas a cámara sin cambios de plano. Todo lo demás es una capa encima: **cada idea que dices se convierte en un
titular corto y un gráfico que la prueba**, sincronizados palabra a palabra. Corre en tu ordenador y cuesta 0 €:
el corte y la voz los hace `herramientas/corte.py` (Whisper en local) y el render, HyperFrames.

Antes de nada, lee `marca/estilo.md` (lo que te gusta y lo que no, y tus correcciones) y `marca/marca.json`.
Las piezas del kit, con ejemplos: `piezas.md`. Los estilos «partida», «clip» y «vlog» al detalle: `estilos.md`.
Un guion de ejemplo con lo principal: `ejemplo/guion.html`.

## Lo que le vas contando

Una o dos líneas por paso, con los números de verdad. Por ejemplo:

- «Junto tus 12 clips y los transcribo en tu ordenador, sin mandar nada fuera.» → «Listo: 2:27 de brutos.»
- «Te he quitado los silencios, 3 tomas repetidas y 2 frases cortadas: de 2:27 a 1:18. Lo que has dicho está entero.»
- «Leyendo lo que dices: cierras bien la idea antes del "comenta". Te propongo el estilo de gráficos encima.»
- «He escrito 19 bloques, uno cada 3 s: tus seguidores girando de 879 a 3.787, tu gráfica, tus 4 reels con más vistas…»
- «La canción: Cinematic Pulse, por debajo de tu voz y nivelada para que se oiga igual en el móvil.»
- «27 efectos de sonido, uno en cada remate y ninguno al entrar un bloque, como los editores que funcionan.»
- «He revisado los 158 fotogramas del vídeo (uno cada medio segundo) y he arreglado 4 cosas antes de enseñártelo.»
- «Aquí tienes el borrador. Míralo con sonido y dime qué cambio.» → con su sí: «Renderizo la versión final y la
  portada, con el fotograma donde tienes los ojos más abiertos.»
- Al acabar: «Perfecto. Te sugiero subirlo hoy a las 19:30, media hora antes de tu pico: ¿lo programo?» (/subida)

## Primero: qué estilo

Pregúntalo si no lo dice ni está en `marca/estilo.md`. Una línea por estilo:

| Estilo | Cómo se ve | Para |
|---|---|---|
| `encima` | Tú a pantalla entera; el titular y el gráfico arriba, en cristal | Lo normal: un tutorial, un caso, una opinión |
| `partida` | El gráfico en un panel claro arriba; tú abajo; la palabra clave grande en la costura | Tutoriales con muchos pasos, cosas que necesitan sitio |
| `clip` | El clip de otro arriba (un CEO, un pódcast) traducido; tú abajo escuchando; luego tú a pantalla entera opinando | Reaccionar a lo que ha dicho alguien |
| `vlog` | Los clips de tu día cortados cada 1,2 a 1,8 s, tu voz encima, una palabra cada vez | Un día de tu vida |

## Los pasos

Cada vídeo vive en `videos/trabajo/<nombre>/` (nombre: `AAAA-MM-DD-tema`). El lanzador: `herramientas/formula`.

1. **Los clips**: en `videos/entrada/` o en la carpeta que diga. Con un número delante manda el orden
   («1 IMG_8581.MOV»); si no, la hora de grabación. Si dice que uno va primero, cópialos a otra carpeta con su número.
   - **El B-roll** (un sitio, un objeto, algo que nombra) no se le pide: búscalo entre sus clips y sus fotos de ese
     día. 🚨 **Si no existe `~/Library/CloudStorage/GoogleDrive-*`, sugiérele en una línea conectar su Drive**:
     «si guardas tu B-roll en Google Drive, instala Google Drive para escritorio y lo cojo de ahí». Una vez por
     vídeo, y sigue sin él. Con Drive para escritorio su carpeta es una carpeta más del ordenador; el conector de
     Drive del chat solo encuentra ficheros, no puede traerte un vídeo.
2. **Preparar** (~30 s por cada 25 s de clips):
   ```bash
   herramientas/formula preparar <nombre> --clips <carpeta> --pista "Claude, Notion"
   ```
   `--pista`: los nombres propios que dice, para que Whisper los escriba bien. Deja `base.mp4` (cortado, sin
   texto), `frases.txt` (cada palabra con su segundo: de aquí salen todos los tiempos) y `palabras.txt`.
3. **Lee `frases.txt` entero**:
   - **¿Cierra la idea?** Antes del «comenta X» o del «sígueme» tiene que decir una conclusión o algo que hacer
     que conteste al gancho. Si no lo dice, **díselo antes de montar**, con la frase propuesta para grabarla
     aparte. No la tapes con un titular.
   - **Fuera cada fallo y cada toma repetida**: la frase cortada a medias, el «se llama Hy… se llama
     HyperFrames», la toma dicha otra vez con otras palabras. Se queda la última completa. El script ya quita
     las repetidas casi idénticas; el resto, con `--fuera "57"` (la frase #57) o `--fuera "83-91"` (esas palabras).
   - Palabras mal oídas: `--cambia "Cloud=Claude"` o, una sola, `--cambia "#185=programación."`.
   - Volver a pasar `preparar` con esas opciones tarda segundos (no transcribe otra vez).
   - **Una frase con un dato dudoso se le señala y decide él**: nunca se quita sola.
   - **Si ha soltado el rollo** (sin guion, o un minuto o más por encima de lo que durará el reel): apunta las
     frases que no sirven a la idea principal del gancho, con su número de `frases.txt`, en la tabla del borrador,
     y quítalas con `--fuera` solo con su sí.
   - Si avisa de un **corte sobre la voz**, quita la frase entera o mueve el corte: se oye el tijeretazo.
4. **Mira el encuadre**: guion vacío (`<!-- ajustes: sub-y=932 -->`) y `herramientas/formula foto <nombre> 3`.
   Apunta dónde empieza su pelo: el hueco de cada bloque va de 250 px hasta ahí. Si la pared de detrás es
   clara, el `velo` (0 a 0,6) oscurece la franja de arriba; `preparar` lo calcula midiendo.
5. **Las capturas**, si nombra algo real («Capturas: la prueba», abajo). Antes del guion: un bloque no puede
   prometer una imagen que luego no se consigue.
6. **Escribe `guion.html`** con las reglas de abajo y las piezas de `piezas.md`. **Y la canción**:
   `herramientas/formula musica <nombre> <tipo>` y `musica=musica.wav` en la línea de ajustes («La música»).
7. **Monta y mira**:
   ```bash
   herramientas/formula armar <nombre>        # index.html, sonidos, avisos y la validación de HyperFrames
   herramientas/formula foto <nombre> 3.9 6.7  # un fotograma por bloque, hacia el final de cada uno
   herramientas/formula foto <nombre>          # todo el vídeo, uno cada 0,5 s, en hojas de 10
   ```
   🚨 **Antes del borrador, todos los fotogramas**: lee cada hoja y arregla lo que se vea mal (texto cortado o
   sobre la cara, un titular que no cambia en 3 s, un logo que no entró, un subtítulo mal oído, algo que entra
   tan tarde que no da tiempo a leerlo). Repite hasta que ninguna hoja tenga nada. Lo que tapa Instagram sale
   en rojo: nada de texto ahí (`--limpia` lo quita para enseñarlo).
8. **Borrador** (~20 s de render por cada 20 s de vídeo): `herramientas/formula render <nombre> --borrador`. Se abre
   solo. Saca fotogramas de dos o tres entradas para comprobar que el movimiento cae en la palabra.
9. **Enséñaselo**: la ruta del borrador y una tabla de bloques (segundo, titular, gráfico). Los sonidos y la
   canción solo los puede juzgar él: pídele que lo vea con sonido. Cada corrección suya va al guion **y a
   `marca/estilo.md`** con su fecha: así el siguiente vídeo ya sale bien.
10. **Con su visto bueno**: `herramientas/formula render <nombre>` (calidad final, a 10 Mb/s, lo que acepta
    Instagram, y su portada `<nombre>.portada.png`). 🚨 **Abre la portada y mírala**: ojos abiertos, nada en la cara
    y el gancho entero. Luego `/subida`.

## Las reglas de estilo

Medidas en reels editados que funcionan (59 s, 23 titulares):

- **Un bloque cada 2 a 3,5 s.** Más de 3 s sin nada arriba: falta un bloque (`armar` avisa).
- **El titular resume, no transcribe.** De 2 a 5 palabras, en frase normal, sin punto final. Dice «te cobra por
  lo que entra y lo que sale es gratis»; el titular dice «Lo que sale es gratis». Nunca el subtítulo repetido.
- **El gráfico prueba el titular** y cada cosa entra **cuando dice la palabra**: el logo cuando nombra la
  empresa, cada fila cuando la enumera, la cifra contando mientras la dice. `data-en` = el segundo de esa palabra
  en `frases.txt`, o una décima antes.
- **Todo se mueve una vez y se queda quieto**: las cifras cuentan, las barras se llenan, las líneas se dibujan.
  Nada parpadea ni se repite.
- **Tu color de acento** (marca.json) en la palabra clave del titular, la cifra que importa y lo que se marca.
  El resto, blanco sobre el cristal, y los colores de los logos y capturas reales.
- **Etiquetas pequeñas en mono y mayúsculas** («MÁS RÁPIDO», «COSTE TOTAL»). Cada cifra lleva la suya.
- **El gancho**: los primeros 2 s, solo texto, sin logo ni emoji. Es la portada: tiene que entenderse sin sonido
  y decir qué es, sin dramas. Dos líneas grandes, o en tres tamaños (`.gancho.tres`: línea pequeña, frase y LA
  palabra gigante en tu acento).
- 🚨 **Las primeras animaciones son las que más importan**: lo que se mueve en los primeros 5 s refuerza el dolor
  o lo que promete el gancho con algo que se ve pasar (el contador que gira, el reloj que corre), no con frases.
- 🚨 **Una animación corta casi no lleva texto**: se entiende de un vistazo, con un dibujo que se mueve y como
  mucho una o dos palabras clave. Si hay que pararse a leerla, está mal.
- 🚨 **Cada bloque se lee en lo que dura**: `armar` avisa por encima de 3,5 palabras por segundo sin contar el
  titular. Y lo que entra con `pop` tarda 0,36 s en verse nítido: como muy tarde 0,5 s antes de que acabe su bloque.
- 🚨 **Lo grande, grande**: el texto dentro de una tarjeta a 38-44 px, las tarjetas de margen a margen, y el
  bloque llega hasta 40 px por encima de su pelo. Si sobra sitio debajo de un gráfico, el gráfico es pequeño.
- **Las líneas se pintan mientras habla**: `data-t` = la palabra donde empieza, `data-hasta` = donde llega,
  `data-cabeza` (un punto en la punta) y debajo el carril tenue con todo el recorrido. Cada punto salta cuando la
  línea llega. Compruébalo a mitad de cada tramo, no solo al final.
- **La frase de abajo** (`.enfasis`): una o dos veces por vídeo, solo en el remate de una idea («Rápido. Barato.»).
- **El cierre**: el titular con la llamada a la acción y la caja de comentario que se teclea sola.
- **Algo fuera de lo normal, una o dos veces** y en el giro de la idea: la tarjeta que se voltea (`gira`), la
  ventana que se abre (`estira`), el barrido circular (`barre`), el ratón que pulsa (`data-clic`), la lista que se
  marca. Si todo es especial, nada lo es.
- **Lo que no hay**: zooms, B-roll, transiciones, emojis.
- En tu idioma, sin rayas largas (—) y con cada cifra comprobada antes de dibujarla.

## Que no se note que lo ha editado una IA

Lo que delata una edición hecha con IA, y lo que hacemos en su lugar (en todos los estilos):

| Lo cutre | Lo que hacemos |
|---|---|
| Texto animado: subtítulos en píldoras, letras mezcladas, chispitas, botes | Subtítulos quietos y sencillos, de 2 a 4 palabras. Lo cutre solo como chiste, en las palabras que lo nombran (abajo) |
| Un emoji o un icono de línea en lugar de una idea (🤖, 💰, una bombilla) | **Una imagen de verdad**: el logo, la cara, el meme, el producto. De su fuente (`captura`) o con `herramientas/formula imagen <nombre> "<búsqueda>" <fichero>`, que baja las 6 primeras de una búsqueda de imágenes y deja una hoja numerada para elegir. `data-icono` solo dentro de una app redibujada que lo enseñe |
| Tiempos muertos | Cada pausa de más de 0,12 s se va (`preparar` ya lo hace) |
| Frases que no sirven al gancho | Si ha soltado el rollo, se le proponen para quitar (paso 3) |
| Un aviso hortera: degradado, estrellas, «¡¡VAMOOOS!! 🔥», cosas que laten | **Un aviso es la pantalla de una app de verdad** (la notificación del móvil, el chat de Claude, los comentarios de Instagram, Google, Fotos, los conectores de Claude) en tu cristal, arriba. Entra con el movimiento de esa app (la notificación cae) o en un fotograma; solo se mueve lo de dentro, como en la app: el texto que se escribe mientras lo dice, el botón que se pone verde, la barra que se llena |
| Imágenes de banco | Las suyas: sus fotos y capturas de ese día y sus clips |

**Trucos que funcionan**, cuando encajen (y en una copia, todos los del original):

- **Enseña lo malo mientras lo nombra.** En «cutre» y en «anima demasiado el texto», los propios subtítulos se
  vuelven cutres; en «avisos sin animar», el hortera y el limpio uno al lado del otro. Una o dos veces por reel.
- **La prueba son sus números**: dos reels suyos lado a lado con sus vistas de verdad, «CUTRE» en rojo sobre el
  que no funcionó y «VIRAL» en verde sobre el que sí. Ese es el gancho; no necesita titular.
- **El «comenta X» vive en la pantalla**: la cabecera de cada tarjeta del chat dice «Comenta X y te paso mi
  setup», y cada «comenta X» lleva los comentarios de Instagram con la palabra escribiéndose, publicada y el
  corazón poniéndose rojo.
- **La vida real debajo**: un sitio nuevo por punto, cortando en «La número X», y una historia pequeña (compra
  algo y se lo come hasta el final); lo que dice otra persona, en letra pequeña amarilla a su lado; la gente que
  pasa, con la cara borrosa.

## Los efectos de sonido: uno por idea, en su remate

`armar` pone **un sonido por idea** (un bloque, o lo que va desde que cambia el titular) **en su remate, nunca al
entrar el bloque ni al cambiar el titular**. Medido en un reel de 49 s que funciona: 21 de sus 35 cambios en
pantalla van en silencio y unos 20 efectos caen cada uno en el momento en que la idea aterriza.

| Sonido | Dónde va | Nivel bajo la voz |
|---|---|---|
| `pop` (campana brillante) | El resultado: lo que se sella (`.sello`) | −9 dB, el más alto |
| `golpe` (golpe grave) | Abre un paso (un titular que empieza «1.», «Paso 2») o llega un mensaje (`data-como="baja"`, `.noti`, `.aviso`) | −11,5 |
| `ding` | Aparece un nombre, un logo o una palabra grande (`.icono`, `.captura`, `.palabra`, `data-como="pop"`), o aterriza una cifra (al final de `data-rueda` / `data-cuenta`) | −13 |
| `hecho` (dos notas) | Algo se marca o se pulsa (`data-clase`, `data-clic`), si no hay nada que pese más en esa idea | −14 |
| `entra` (silbido) | Solo los giros grandes (`gira`, `barre`, `estira`), uno cada 15 s como mucho: dos o tres por vídeo | −15 |

- En cada idea gana el que más pesa (`entra` > `pop` > `golpe` > `ding` > `hecho`) y, si empatan, el último: el
  remate llega al final. Dos sonidos a menos de 0,8 s: se queda el que pesa más.
- **A mano**: `data-son="ding"` en un elemento lo hace sonar ahí y calla el resto de esa idea; `data-son="no"` lo
  calla. En un `section`, `data-son` le da sonido de entrada. El tecleo solo suena con `data-son="tecla"`.
- En la línea de ajustes: `sonido=0.14` es el nivel medido (`sonido=0` los quita), `sonidos=todos` vuelve a un
  sonido por cada cosa que se mueve (cansa) y `sonidos=pop,golpe` deja solo esos.
- No los puedes oír: mides dónde están y a qué nivel. Si dice «más bajo» o «ese no», cambia el nivel o el tipo en
  `herramientas/sonidos.py` y apúntalo en `marca/estilo.md`.

## La música

Cada reel lleva una canción, de las suyas: `marca/musica.json` (su ficha) y `marca/musica/` (los audios).

```bash
herramientas/formula musica <nombre> utilidad          # la de ese tipo que lleva más tiempo sin sonar → musica.wav
herramientas/formula musica <nombre> utilidad --cancion <id>   # esa
herramientas/formula musica <nombre> utilidad --opciones "id1,id2,id3"   # una página para elegir
herramientas/formula musica --anadir <fichero o enlace> --tipos caso,utilidad --titulo "…" --artista "…" --desde 14
```

- Va a −33 LUFS debajo de su voz (−15) y aplanada: la parte fuerte de la canción no se sale del fondo.
- Se nivela por lo que suena en el altavoz de un móvil: una canción casi toda de graves mide igual que las demás
  y en el móvil no se oye. En la página de opciones todas suenan igual de altas: que las escuche en el móvil.
- Si rechaza dos seguidas, no le pongas una tercera a ciegas: la página con seis o siete.
- Solo música que pueda usar. Va pegada al vídeo, no de la biblioteca de Instagram.
- Sin canciones aún: que añada unas cuantas por tipo (las que suenan en los virales de su nicho y las que tiene
  guardadas).

## Capturas: la prueba en pantalla

Cuando nombra algo real (una noticia, una herramienta, sus números), su imagen lo prueba.

- 🚨 **Se entiende de un vistazo: es una imagen, nunca texto.** Un logo, la foto de quien nombra, la pantalla del
  producto, una gráfica. Un titular de prensa, un tuit o un párrafo no: si la prueba es texto, se dibuja en dos o
  tres palabras.
- **Sus propios números, mejor la captura real**: da credibilidad. Si su móvil está en otro idioma, o la cifra
  tiene que moverse (seguidores de antes a ahora), se redibuja la tarjeta tal cual con sus números de verdad y un
  cuentakilómetros (`data-rueda`). Dile cuál es real y cuál redibujada.
- **Entra en la palabra que la nombra y se va cuando acaba la frase**: de 0,6 a 3,5 s. Entra y sale de golpe, en
  un fotograma, sin marco ni sombra.
- **Lo más importante, en el gancho**, debajo de las dos líneas, aunque le tape media cara.
- **Solo lo que existe y de su fuente**: la web oficial, el medio que lo cuenta, su pantalla. Nunca una imagen de
  banco ni generada.
- **Datos personales tapados** en cualquier captura suya. Y la cara de otro creador, borrosa (lo justo para que
  no se le reconozca; lo que importa de su vídeo, el título o el gráfico, se deja nítido).
- Sacarlas, con un Chrome sin ventana (el suyo ni se toca):
  ```bash
  herramientas/formula captura <nombre> <url> anuncio --portada      # la imagen con la que la web se anuncia
  herramientas/formula captura <nombre> <url> titular --recorte "0,160,640,215"
  herramientas/formula captura <nombre> <url> tabla --selector "table"
  herramientas/formula imagen <nombre> "meme de alguien asintiendo" meme   # una imagen real buscada en la web
  ```
  🚨 Abre y mira cada captura antes de usarla. Si la web no deja (muro de pago, bloqueo), otra fuente o pídesela.

## Lo que tapa Instagram

| Zona (px del vídeo) | Qué pone Instagram | Qué hacemos |
|---|---|---|
| 0 a 240, todo el ancho | La hora, «Reels», la flecha, la cámara | El titular y el gancho empiezan en 250 |
| De 1130 abajo, desde x=900 | Me gusta, comentar, compartir | Subtítulos de 640 px (220 a 860) |
| De 1680 abajo | El nombre de la cuenta y el pie | Nada de texto |
| 47 px a cada lado | El iPhone recorta | El margen (56) ya lo cubre |

## Los subtítulos

- **Por defecto** (`subs=si`, `sub-y=932`): 2 a 4 palabras en el centro exacto de la pantalla, con borde.
- **Quietos bajo la barbilla** (`subs=claves sub-y=1250`): blancos con borde fino, cambian de golpe, y las palabras
  de `<!-- claves: … -->` y las cifras en tu acento. Como los de CapCut.
- 🚨 **No los animes palabra a palabra** con cajas que saltan: llaman más la atención que el gráfico.
- En «partida» van en la costura, una o dos palabras, y la clave sola, grande y en tu acento.

## La portada

`render` la hace solo (`formula portada <nombre>` la repite): mide en cada décima del gancho lo abiertos que
están sus ojos (macOS) y se queda con el más abierto y de frente, con solo el gancho encima. Fuera de macOS
elige el medio del gancho: mírala y, si sale con los ojos cerrados, `--en SEGUNDO`. 🚨 Ábrela siempre antes de subir.

## Si copia un reel concreto: calca la edición, bloque a bloque

Si el guion salió de copiar un reel (`/guion`, modo copia), la edición es la de ese reel con sus palabras:
mismos bloques, mismos gráficos, mismo tamaño, mismas animaciones y mismos momentos de sonido. Hoja de
fotogramas cada 0,5 s del original (`ffmpeg -i v.mp4 -vf "fps=2,scale=216:384,tile=6x4" hoja-%02d.jpg`), un
bloque nuestro por cada uno suyo y, antes del borrador, un fotograma suyo y uno nuestro del mismo bloque, juntos.
Los colores, las letras y las piezas son los suyos (marca.json): se copia el qué y el cuándo, nunca el aspecto.

- **Sus escenas también**: el guion trae `escena` en la toma donde empieza cada una (el sitio, el plano, lo que
  hace). Antes de `preparar`, comprueba que sus clips cubren cada escena en ese orden; si falta una, díselo antes
  de montar, como una frase que falta.
- **Su canción**, a su nivel bajo la voz: búscala, añádela con `musica --anadir` y apunta de qué reel sale.

## Si contesta un mensaje: llega como notificación

Si el vídeo responde a un mensaje que le mandaron, empieza con la notificación cayendo arriba (`.noti`,
`data-como="baja"`, `data-son="mensaje"`), el nombre de quien escribe borroso, y debajo el gancho y luego una
animación por cada cosa que pide. El gancho, sobre lo que le importa a quien pregunta.

## Vídeo personal (su historia, una decisión)

`<div data-ritmo="lento"></div>` en el guion: todo entra y sale más despacio y cada bloque crece un poco
mientras dura. Menos bloques y más largos, solo el sonido de los remates y bajo (`sonido=0.08`), y una canción
de tipo `historia`. Su voz manda.

## Trampas del kit

- `<i data-icono="x"></i>` y `<i data-marca="x"></i>` solo se cambian por el icono tal cual, sin `class` ni
  `style`: para darle color o tamaño, envuélvelo (`<span class="ico"><i data-icono="moon"></i></span>`).
- Dentro de un `h2.titular` solo sobrevive `<span class="acento">`.
- 🚨 **Una clase tuya no puede llamarse como una del kit** (`.caja`, `.tira`, `.c`, `.lista`…): rompe la pieza sin
  dar error. Ponles nombres propios (`.mi-tarjeta`). Y una regla `.algo span {…}` alcanza las cifras de un
  cuentakilómetros que esté dentro: usa `.algo > span`.
- Una etiqueta `.mono` suelta sobre una pared con mucho detalle no se lee: dentro de un `.vidrio`.
- Lo que no está en el kit se escribe en HTML dentro del bloque con su `data-en`, con su `<style>` arriba del
  guion. Si lo usas en un segundo vídeo, pásalo a `herramientas/kit/base.css`.

## Lo que rompe el render de HyperFrames si se olvida

- Una sola línea de tiempo de GSAP, parada y montada de golpe: nada de `onUpdate`, `setTimeout`, `Math.random()`
  ni `Date.now()`. Cada fotograma sale solo de su segundo (`herramientas/kit/motor.js` ya lo cumple).
- No animes con GSAP algo que ya tenga `transform` en el CSS, ni toques `display` o `visibility` de un bloque con
  `data-a` (anima lo de dentro).
- Las letras salen de `kit/fonts`: al renderizar no hay red.
- 🚨 No lances `hyperframes feedback`, `publish` ni `cloud`: mandan datos fuera. La telemetría va apagada.
- Para verlo y tocarlo a mano en su editor: `herramientas/.hf/node_modules/.bin/hyperframes preview` en la
  carpeta del vídeo.
