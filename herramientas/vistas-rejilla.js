// Lee las visualizaciones de la rejilla de reels de un perfil de Instagram (el tuyo o el de un referente).
// Solo lee: no hace clic en nada ni escribe. Se pega con la herramienta de JavaScript de Claude in Chrome en
// https://www.instagram.com/<cuenta>/reels/ y devuelve una línea por reel: «<código> <vistas>», de más a menos.
// Guárdalo en vistas.txt para formula-estudiar o para medir tus vídeos contra tu mediana.
// La rejilla se va montando y desmontando al bajar: por eso se recoge mientras se baja.
(async () => {
  const vistos = {};
  const recoger = () => document.querySelectorAll('a[href*="/reel/"]').forEach((a) => {
    const codigo = a.getAttribute("href").split("/reel/")[1].split("/")[0];
    const texto = a.innerText.replace(/\n/g, " ").trim();
    if (texto) vistos[codigo] = texto;
  });
  let alto = -1;
  for (let vuelta = 0; vuelta < 40; vuelta++) {
    recoger();
    window.scrollTo(0, document.body.scrollHeight);
    await new Promise((r) => setTimeout(r, 1300));
    if (document.body.scrollHeight === alto && vuelta > 3) break;   // ya no carga más
    alto = document.body.scrollHeight;
  }
  recoger();
  const numero = (t) => {
    const m = t.match(/([\d.,]+)\s*(mil|k|m|mill)?/i);
    if (!m) return 0;
    const unidad = (m[2] || "").toLowerCase();
    const cifra = unidad ? parseFloat(m[1].replace(",", ".")) : parseFloat(m[1].replace(/\./g, "").replace(",", "."));
    return Math.round(cifra * (unidad === "mil" || unidad === "k" ? 1e3 : unidad.startsWith("m") ? 1e6 : 1));
  };
  const filas = Object.entries(vistos).map(([c, t]) => [c, numero(t), t]).sort((a, b) => b[1] - a[1]);
  const valores = filas.map((f) => f[1]).sort((a, b) => a - b);
  const mediana = valores.length ? valores[Math.floor(valores.length / 2)] : 0;
  return `${filas.length} reels · mediana ${mediana}\n` + filas.map((f) => `${f[0]} ${f[2]}`).join("\n");
})();
