# Los estilos «partida», «clip» y «vlog»

Todo lo de SKILL.md vale igual (pasos, capturas, portada, sonidos, música); aquí, lo que cambia.

## «partida»: pantalla partida

`<!-- ajustes: estilo=partida -->` y debajo `<!-- claves: … -->`.

| | encima | partida |
|---|---|---|
| Tú | A pantalla entera | De la `costura` (1060) para abajo, esquinas de arriba redondeadas. `encuadre=68` mueve qué trozo de ti se ve (0 arriba, 100 abajo) |
| El gráfico | Cristal (`panel`) sobre tu pared | Tinta (`tinta`) sobre papel claro (`papel`), con tu acento (marca.json) |
| Gancho | Dos líneas grandes | 🚨 Un título corto arriba, en frase normal con la clave en `.acento`, y la animación debajo, en un `.beat` que empieza a la vez (`style="padding-top:110px"`) |
| Titulares | Arriba a la izquierda, 56 px | Centrados, 62 px; el gráfico, centrado debajo |
| Subtítulos | 2 a 4 palabras en el centro | En la costura, una o dos palabras; cada clave sola, grande y en tu acento |
| Ritmo | Un bloque cada 2 a 3,5 s | Igual, pero dentro algo se mueve cada ~0,5 s (lo que se teclea, los pasos que se marcan, la cifra) |

- 🚨 **El panel nunca se queda vacío**: cada bloque acaba (`data-b`) donde empieza el siguiente. Una décima de papel
  vacío se ve roto; `armar` avisa.
- **Las claves**: ~1 de cada 3 subtítulos, lo que se recordaría sin sonido: el nombre de la herramienta, la cifra,
  el verbo del paso, el remate.
- **Los otros dos planos**, para romper la rutina:
  - `<section class="beat entera">` con `<div class="paso" data-en="…" data-como="pop">Paso 1</div>`: solo tú, a
    pantalla entera, en **cada paso que enumeras**, del número a la primera palabra con gráfico (0,6 a 1 s). Si avisas
    de algo («aquí falla casi todo el mundo»), la frase va en `<div class="nota">` debajo.
  - `<section class="beat solo">`: solo el gráfico, a pantalla entera, para un esquema que necesita sitio. Una vez por vídeo.
- **Sus piezas** (`kit/partida.css`): `.hoja` (tarjeta con icono y rótulo, `.buena` con el borde de acento),
  `.con-sello > .sello` (la pegatina inclinada en la esquina), `.movil` (`data-clase="…:marcada"` lo enciende),
  `.terminal` (se teclea con `data-escribe` y cada `.linea` pasa de girando a hecha con `data-clase="…:hecha"`) y
  `.ventana` (la app: `.cabecera`, `.rotulo` y `.escrito`; la palabra que dices, con `data-clase="…:resalta"`).
- 🚨 **El cierre dice qué comentar sin duda**: la caja grande (`.comentar.grande`) con la palabra tecleándose a
  64 px y el titular «Comenta **X**». Una pegatina «Comenta X» sola no se entiende.
- **La portada**: el título y, debajo, la animación que empieza con él, ya completa. Si su remate llega más tarde,
  `formula portada <nombre> --en <un segundo con todo dentro y los ojos abiertos>`.

## «clip»: el clip de otro arriba

Para reaccionar a lo que ha dicho alguien (un CEO, un pódcast).

| | Mientras suena el clip | Cuando acaba |
|---|---|---|
| Arriba | El título (250 a 410): frase normal, 60 px, la clave en `.acento` | Tus bloques, como en «encima» |
| El clip | De `clip-y` (410) a la `costura` (1060), sin los subtítulos quemados ni los logos del programa. Con su sonido | Se va |
| La costura | La traducción, frase entera mientras suena, como el subtítulo de una película; las claves en tu acento | Nada: tus subtítulos van en el centro |
| Tú | Abajo, escuchando, sin sonido (`reaccion.mp4`) | Subes de la costura a pantalla entera (0,45 s) y hablas |

1. **El clip**: `herramientas/formula clip <nombre> <url> --pista "Nombre, Empresa"`. Lo baja (como mucho a 1080),
   lo transcribe en su idioma (`fuente.txt`) y saca `fuente.jpg`, un fotograma con una rejilla cada 100 px para medir
   el recorte.
2. **Qué trozos**: desde lo que pone el contexto hasta **la frase clave, y ahí se corta**: de 10 a 18 s. Fuera el
   saludo y los rodeos. Lo que viene después de la frase clave lo cubres tú en tu opinión.
3. **El recorte**, mirando `fuente.jpg`: por encima de sus subtítulos quemados, sin los logos del programa y con la
   cara grande.
   ```bash
   herramientas/formula clip <nombre> x --trozos "4.2-8.95,10.5-11.9,12.0-17.95" --recorte "430,70,1100,662" \
     --reaccion "videos/entrada/0 IMG_….MOV" --desde 1.5
   ```
   Deja `clip.mp4` (sin pausas de más de 0,35 s: en un pódcast, cortar cada 0,12 s se ve a saltos) y `clip.txt`. Desde
   entonces `frases.txt` lleva el clip delante: todos los segundos del guion son del vídeo entero.
4. 🚨 **Tu toma escuchando** (`--reaccion`, y `--desde` el segundo en que empiezas a mirar): una toma mirando el clip
   en el portátil, sin hablar, con alguna reacción, de lo que dure el clip. Nunca una toma tuya hablando: se te
   vería mover la boca.
5. **Tu opinión**: tus clips y `formula preparar` como siempre. 🚨 Tiene que acabar atando el clip a lo que piensas:
   qué significa para quien mira y qué hacer con ello.
6. **El guion**: `<!-- ajustes: estilo=clip sub-y=932 -->`, sus `<!-- claves: … -->` y:
   - el título: `<div class="gancho" data-a="0" data-b="<fin del clip>">El CEO de X sobre<br>trabajar con <span class="acento">IA</span></div>`;
   - quién habla, los 3 o 4 primeros segundos: `<section class="beat quien">` con su `.ficha` (logo, nombre y cargo);
   - 🚨 la traducción: un `<p class="dice" data-a="…" data-b="…">` por frase de `clip.txt`, natural y no palabra por
     palabra;
   - luego, bloques de «encima» con todas sus reglas, el primero 0,3 s después de que acabe el clip.

- El clip suena en su idioma, con la traducción; nunca doblado.
- De dónde sale: quién habla, en la ficha; el programa o la cuenta, en el pie («Clip: …»).

## «vlog»: un día de tu vida

Tres pasos, con tu voz en medio:

1. **Tus clips → el corte, sin voz.** `herramientas/formula vlog <nombre> --clips <carpeta>` hace una hoja por clip
   (`tomas/NN.jpg`: el fotograma k es el segundo k × `cada`). Lee cada hoja y escribe `montaje.json`:
   - **La historia en el orden del día**, de 35 a 60 s.
   - **Un plano nuevo cada 1,2 a 1,8 s.** Solo un selfie hablando a cámara dura más, con `"sonido": true`.
   - **Cada plano es la imagen literal de una frase**: «inglés» → la app de inglés en el portátil.
   - Mezcla ángulos: selfie (0,5×, en el coche o andando), primera persona (los pies andando, las manos en el
     teclado, el café), el móvil en la mesa grabándote, pantallas, gente, sitios, el gimnasio, y **un último plano
     que cierra el día** (habitación a oscuras, portátil cerrado).
   `herramientas/formula vlog <nombre> --montar` → `videos/salida/<nombre>-para-la-voz.mp4`. Dale ese fichero **y una
   frase de voz propuesta por plano** (corta, en primera persona, lo que enseña el plano) para que la grabe encima
   con sus palabras (CapCut, o una nota de voz con el vídeo sonando).
2. **Tu voz → la base.** `herramientas/formula vlog <nombre> --voz <fichero>` (`--desde S` si empieza antes del corte).
3. **Lo demás, como siempre**: el título en `guion.html` (es la portada), `formula musica <nombre> vlog` (y
   `musica=musica.wav`), `armar`, `foto`, `render`.

| | Cómo |
|---|---|
| Subtítulos | Una palabra cada vez, pequeña (46 px), blanca, sin contorno, sola en el centro (`sub-y=930`); las cifras, en tu acento |
| Título (la portada) | `<div class="gancho"><span class="dia">Día N:</span> la idea con su <i class="acento">palabra</i></div>`, los primeros 2,6 s |
| Música | Tipo `vlog`: un groove casi a la par de la voz (2,5 dB por debajo) |
| No | Titulares, gráficos ni efectos (`sonido=0`): lo cuentan los planos |
