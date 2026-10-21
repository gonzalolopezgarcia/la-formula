/* Saca la captura de una web para ponerla en el reel como prueba. Lo llama `formula captura`,
   con el Chrome sin ventana que ya trae HyperFrames: no toca tu Chrome ni tu sesión.

   La página se abre estrecha, como en un móvil, para que el texto salga grande, y a doble
   densidad. Recibe un JSON: { chrome, url, destino, ancho, alto, selector, recorte, entera,
   portada, oscuro, quita, espera, idioma }. */
const fs = require("fs");
const puppeteer = require("puppeteer-core");

const o = JSON.parse(process.argv[2]);
const AVISOS = '#onetrust-consent-sdk, .fc-consent-root, [id*="cookie" i], [class*="cookie" i], ' +
  '[id*="consent" i], [class*="consent" i], [aria-label*="cookie" i]';

(async () => {
  const navegador = await puppeteer.launch({ executablePath: o.chrome, headless: "shell" });
  try {
    const pagina = await navegador.newPage();
    await pagina.setUserAgent("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 " +
      "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36");
    await pagina.setViewport({ width: o.ancho, height: o.alto, deviceScaleFactor: 2 });
    if (o.oscuro) await pagina.emulateMediaFeatures([{ name: "prefers-color-scheme", value: "dark" }]);
    await pagina.goto(o.url, { waitUntil: "networkidle2", timeout: 45000 }).catch(function (e) {
      if (!/timeout/i.test(e.message)) throw e;   // una web que nunca deja de pedir cosas: vale con lo cargado
    });
    await new Promise(function (r) { setTimeout(r, o.espera * 1000); });
    const idioma = await pagina.evaluate(function () { return document.documentElement.lang || ""; });
    if (idioma && o.idioma && !new RegExp("^" + o.idioma, "i").test(idioma)) {   // en pantalla, todo en tu idioma
      console.log("⚠️  esta página está en «" + idioma + "», no en tu idioma (" + o.idioma + "): no vale para ponerla " +
        "en pantalla con texto. Busca un medio en tu idioma que lo cuente, o usa solo su imagen (--portada).");
    }

    if (o.portada) {   // la imagen con la que la propia web se anuncia (og:image)
      const imagen = await pagina.$eval('meta[property="og:image"], meta[name="twitter:image"]',
        function (m) { return new URL(m.content, location.href).href; });
      fs.writeFileSync(o.destino, await (await pagina.goto(imagen)).buffer());
      console.log("portada: " + imagen);
      return;
    }

    // fuera los avisos de cookies; y con un recorte, también lo que se queda pegado al hacer scroll
    await pagina.evaluate(function (avisos, pegado) {
      document.querySelectorAll(avisos).forEach(function (el) { el.remove(); });
      if (!pegado) return;
      document.querySelectorAll("body *").forEach(function (el) {
        var p = getComputedStyle(el).position;
        if (p === "fixed" || p === "sticky") el.style.display = "none";
      });
    }, o.quita ? AVISOS + ", " + o.quita : AVISOS, Boolean(o.selector || o.recorte || o.entera));

    const medida = await pagina.evaluate(function () {
      return document.documentElement.scrollWidth + " x " + document.documentElement.scrollHeight;
    });
    if (o.selector) {
      const trozo = await pagina.$(o.selector);
      if (!trozo) throw new Error("no hay nada en la página con el selector " + o.selector);
      await trozo.screenshot({ path: o.destino });
    } else if (o.recorte) {
      const r = o.recorte.split(",").map(Number);
      await pagina.screenshot({ path: o.destino, clip: { x: r[0], y: r[1], width: r[2], height: r[3] } });
    } else {
      await pagina.screenshot({ path: o.destino, fullPage: Boolean(o.entera) });
    }
    console.log("página: " + medida + " px (los de --recorte) · " + (await pagina.title()));
  } finally {
    await navegador.close();
  }
})().catch(function (e) { console.error("No se ha podido capturar: " + e.message); process.exit(1); });
