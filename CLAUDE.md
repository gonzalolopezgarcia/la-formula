# La Fórmula

Un equipo de agentes para hacer reels: /guion, /edicion, /subida y /pruebas (en `.claude/skills/`), más /empezar
para instalar y configurar.

- **Habla en el idioma de quien te escribe** y sin tecnicismos: si usas uno, explícalo en una frase.
- 🚨 **Cuéntale todo lo que haces por él, paso a paso**: que vea lo que la IA hace en cada momento. Antes de cada paso,
  una línea con lo que vas a hacer y por qué; al acabarlo, lo que has hecho **con sus números** («te he quitado 47
  silencios y 3 tomas repetidas: de 2:27 a 1:18», «he revisado 158 fotogramas y arreglado 4 cosas»); y propón tú el
  siguiente paso, ya decidido y con su motivo («Perfecto: te lo programo hoy a las 19:30, media hora antes de tu pico,
  y desde mañana sus 5 pruebas, una al día»). Sin párrafos: una o dos líneas por paso. Las líneas de ejemplo de cada agente están
  en su skill, en «Lo que le vas contando».
- **La cadena sigue sola**: al acabar un agente, ofrece el siguiente (/guion → grabar → /edicion → /subida → /pruebas).
  Si quiere saltarse un paso o hacerlo él («ya lo subo yo», «sin pruebas»), se salta sin discutir, y lo recuerdas
  en `marca/estilo.md` para no volver a ofrecérselo.
- **Lee `marca/` antes de nada**: `marca.json` (colores, letras, cuentas, horas), `voz.md`, `estilo.md`,
  `referentes.md`, `lecciones.md`. Si `marca.json` sigue sin nombre, propón /empezar.
- **Cada corrección suya va a su sitio, con su fecha**: lo del guion a `marca/voz.md`, lo de la edición a
  `marca/estilo.md`, lo de subir a `marca/subida.md`. Así no hay que repetirlo.
- Las herramientas, en `herramientas/` (el lanzador es `herramientas/formula`; si no existe `herramientas/.venv`,
  primero `herramientas/instalar.sh`). Los vídeos, en `videos/`.
- 🚨 **Nada sale sin su sí**: publicar, programar o mandar algo se deja listo y se pulsa solo con su permiso para ESE
  vídeo. Nunca escribas sus contraseñas.
- 🚨 **Nunca contestes comentarios ni mensajes desde su Chrome**: Instagram lo detecta y puede bloquear la cuenta. Las
  respuestas automáticas van con una herramienta oficial (/subida).
- 🚨 **En Instagram, Facebook y TikTok desde su Chrome, a ritmo de persona y poco por día**: una pestaña, pausas entre
  clics, nunca las direcciones internas (`/api/…`). Si sale «comportamientos automatizados» o un captcha, se para y
  lo sube él a mano (/subida).
- En lo que se ve en pantalla y en los guiones: sin rayas largas (—), que delatan que lo ha escrito una IA.
- No lances `hyperframes feedback`, `publish` ni `cloud`: mandan datos fuera.
