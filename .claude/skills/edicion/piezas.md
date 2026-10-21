# Las piezas del kit

El guion (`guion.html`) es un HTML con un elemento por bloque. `data-a` y `data-b` son el segundo en que entra y
sale; dentro, `data-en` es el segundo en que entra cada cosa (`+0.3` = relativo al bloque). Todos los segundos,
los de `frases.txt`. Un ejemplo con lo principal: `ejemplo/guion.html`.

```html
<!-- ajustes: sub-y=932 musica=musica.wav -->
<!-- claves: fórmula, 3.000 -->
<div class="gancho" data-a="0" data-b="1.9">Cuatro modelos<br>de Claude</div>

<section class="beat" data-a="2.0" data-b="4.9">
  <h2 class="titular">El rápido y <span class="acento">barato</span></h2>
  <div class="fila">
    <div class="icono" data-en="2.2" data-como="pop"><i data-marca="claude"></i></div>
    <span class="palabra" data-en="2.6">Haiku</span>
    <span class="chip" data-en="3.4">Para volumen</span>
  </div>
</section>
```

## La línea de ajustes (la primera del guion)

| Ajuste | Qué hace | Por defecto |
|---|---|---|
| `estilo=` | `encima`, `partida`, `clip` o `vlog` | `encima` |
| `sub-y=` | Altura de los subtítulos (px). 932 = centro exacto | 932 |
| `subs=` | `si`, `claves` (quietos bajo la barbilla, claves en tu acento) o `no` | `si` |
| `velo=` | De 0 a 0,6: oscurece la franja de arriba si la pared es clara | lo mide `preparar` |
| `arriba=` | Dónde empieza el titular (nunca menos de 250: arriba tapa Instagram) | 250 |
| `musica=` | `musica.wav` (la deja `formula musica`) | sin música |
| `sonido=` / `sonidos=` | Volumen de los efectos / cuáles (ver SKILL.md) | 0.14 / remates |
| `costura=`, `encuadre=` | «partida» y «clip»: dónde empiezas tú y qué trozo de ti se ve | 1060 / 68 |

`<!-- claves: … -->`: las palabras que salen en tu acento en los subtítulos (y solas y grandes en «partida»).

## Piezas

| Pieza | Clase | Para qué |
|---|---|---|
| Gancho | `div.gancho` (`data-a="0"`), o `.gancho.tres` con `.k` (línea mono), `.m` (frase), `.g` (LA palabra, gigante en tu acento), `.c` (pie) | La portada: los primeros 2 s, solo texto |
| Titular | `h2.titular` | El primero de cada bloque. `.relevo` + `data-en` cambia el titular sin cambiar el gráfico (al anterior, `data-sale`) |
| Logo | `.icono` (`.med`, `.peq`, `.oscuro`) con `<i data-marca="claude">` | Marcas de `simple-icons`: claude, openai, notion, instagram, tiktok, whatsapp, github… |
| Icono de línea | `<i data-icono="mail">` | Cualquiera de `lucide` (envuélvelo en `<span class="ico">` para darle tamaño o color) |
| Palabra grande | `.palabra` (`.med`) | El nombre de lo que hablas, junto a su logo |
| Etiqueta | `.mono` (`.peq`, `.tenue`), `.chip` (`.claro`) | Etiquetas de datos |
| Cifra | `.cifra` con `<span data-cuenta="0,100">` | Una cifra que cuenta; `<small>` para la unidad |
| Cuentakilómetros | `<span data-rueda="879,3787" data-t="4.4" data-dur="1.2">879</span>` (`data-dec="1"` para «502,8») | Cada cifra gira en su rueda, con punto de miles y coma decimal. Para cifras reales que cambian delante de ti: seguidores antes → ahora, visualizaciones |
| Barras | `.medida` con `.barra > i[data-barra="0.9"]`; `data-barra="1,0.03"` se vacía | Comparar dos cosas; algo que se acaba |
| Tarjeta | `.vidrio` con `.renglon`, `.opcion` (`data-clase="9.2:elegida"`), `.sello` | Una tabla de precios, una lista donde se elige una |
| Lista que se marca | `.vidrio.lista` con `.item` (`.n`, `.ok`) y `data-clase="T:on"`; debajo `.barra.fina` | Enumeras de 3 a 5 cosas |
| Sello | `.sello` con `data-como="pop"` | El resultado, inclinado: «HECHO», «+2.908». Ahí suena la campana |
| Cajas | `.con-etiqueta > .caja` + `svg.tacha` con `data-traza` | «Esto sí, esto no» |
| Muchos ejemplos | `.rejilla > .pildora` (+ `.etq`), `data-cascada="17.4,0.14"` | Muchos casos a la vez |
| Dibujo | `svg.dibujo` con `path[data-traza]` (`data-t`, `data-hasta`, `data-cabeza`), `.carril`, `.hito` + `.tinta` | Ramas, líneas de tiempo, un camino con un obstáculo |
| Mover | `data-mueve="11.3:x=930"` (`data-mueve-dur`, `data-mueve-curva="none"`, `rotation=-30>0`) | Algo que ya está en pantalla se mueve: un cabezal, una línea que escanea, la escena que crece |
| Ratón | `data-clic="T"` en una `.opcion` o `.chip` | Un ratón llega y la pulsa: se pone en tu acento |
| Captura | `img.captura`, sola en el bloque o bajo el titular; `style="--alto:420px"` si llega al pelo. `.beat.cara` la pone sobre tu cara; `style="top:680px"`, bajo el gancho | La prueba de lo que dices (SKILL.md, «Capturas») |
| Frase de abajo | `div.enfasis` con un `span data-en` por palabra | El remate de una idea, subrayado palabra a palabra |
| Cierre | `.comentar` con `data-escribe` y `.aviso` | La caja de comentario que se teclea sola y el mensaje que llega |
| Cierre «sígueme» | `.vidrio.perfil` con `.texto` (tu cuenta) y `.boton` > `.seguir` (`data-sale`) + `.siguiendo` (`data-como="pop"`) | El botón Seguir que pasa a Siguiendo |
| Notificación | `.noti` con `.app`, `.tapado` (el nombre, borroso), `.cuando` y `.msg`; `data-como="baja"` y `data-son="mensaje"` | Llega un mensaje |
| IA que miente | `.robot` (`.antena`, `.cara`, `.ojos` con `data-clase="…:miran"`, `.nariz > i[data-barra="0.1,1"]`, `.dice`) y un `.sello` «MIENTE» | Se inventa algo: le crece la nariz |
| Algo que se acaba | `.bateria` (`.carga > i[data-barra="1,0"]`, `.polo`, `.aviso-ico`), `data-como="sacude"`, `data-clase="…:vacia"` | Créditos, tokens, batería |

Maquetación: `.fila` (`.arriba`, `.junto`), `.col` (`.centro`), `.crece`, `.derecha`.

## Cómo entra cada cosa (`data-como`)

`sube` (por defecto), `pop`, `izq`, `fundido`, `baja` (cae desde arriba con rebote: una notificación), `sacude`
(entra temblando: un error). Y las de fuera de lo normal, una o dos por vídeo: `gira` (se voltea como un panel),
`barre` (se destapa en círculo desde la esquina), `estira` (una ventana que se abre).

Otros atributos: `data-escribe` (se teclea, 0,1 s por letra), `data-clase="T:clase"`, `data-atenua="T"` (baja al
35 %), `data-sale="T"` (se va antes), `data-queda` (en el bloque del cierre: no se va), `data-son` (ver SKILL.md).
