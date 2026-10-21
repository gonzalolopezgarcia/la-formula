// Ayudas para programar un vídeo en TikTok Studio desde tu Chrome (Claude in Chrome), con TikTok en español.
// Se pega entero con la herramienta de JavaScript justo después de abrir
//   https://www.tiktok.com/tiktokstudio/upload?from=webapp
// (se pierde en cada navegación). Antes, fija el pie que debe llevar: window.__pie = "IG: tucuenta";
// Ver .claude/skills/subida/SKILL.md, «TikTok paso a paso».
//
// Por qué así:
// - La subida de ficheros desde Claude va por trozos de menos de 10 MB: el vídeo se parte en el disco
//   (split -b 9000000), se sube cada trozo a este input y __assemble los junta en el de TikTok.
// - La rueda de la hora falla si se hace clic en una posición: __time hace un clic sintético en la opción.
// - __go solo pulsa «Programar» si fecha, hora y pie son exactamente los que tocan.

window.__trozos = [];
(() => {
  const inp = document.createElement("input");
  inp.type = "file"; inp.multiple = true; inp.id = "formula-trozos";
  inp.setAttribute("aria-label", "formula trozos del video");
  inp.style.cssText = "position:fixed;top:4px;left:300px;z-index:99999;width:200px;height:24px;background:#fff";
  inp.addEventListener("change", () => { for (const f of inp.files) window.__trozos.push(f); });
  document.body.appendChild(inp);
})();

// Junta los trozos subidos (por nombre) y los mete en el input de TikTok. Devuelve [trozos, bytes]
window.__assemble = (nombre) => {
  const partes = [...window.__trozos].sort((a, b) => a.name.localeCompare(b.name));
  const file = new File(partes, nombre, { type: "video/mp4" });
  const tk = [...document.querySelectorAll("input[type=file]")].find((i) => i.id !== "formula-trozos");
  const dt = new DataTransfer(); dt.items.add(file); tk.files = dt.files;
  tk.dispatchEvent(new Event("change", { bubbles: true }));
  window.__trozos = [];
  return [partes.length, file.size];
};
// Junta, comprueba que el tamaño es el del original y espera a «Cargado»
window.__up = async (nombre, bytes) => {
  const r = window.__assemble(nombre);
  if (r[1] !== bytes) throw new Error("tamaño " + r);
  for (let i = 0; i < 40; i++) { await new Promise((s) => setTimeout(s, 1000)); if (/Cargado/.test(document.body.innerText)) return "cargado"; }
  return "aún cargando: espera y vuelve a mirar";
};

// Píxeles de la página → coordenadas de captura (comprueba: ancho de la captura / window.innerWidth)
window.__S = 1;
window.__c = (r) => [Math.round((r.x + r.width / 2) * window.__S), Math.round((r.y + r.height / 2) * window.__S)];
// Hora y fecha como están en los campos visibles
window.__vis = () => [...document.querySelectorAll("input")].filter((e) => e.getClientRects().length && /^(\d\d:\d\d|\d{4}-\d\d-\d\d)$/.test(e.value.trim())).map((e) => e.value.trim());
window.__place = (el, y) => {
  let sc = el.parentElement;
  while (sc && !(sc.scrollHeight > sc.clientHeight + 5 && /(auto|scroll)/.test(getComputedStyle(sc).overflowY))) sc = sc.parentElement;
  sc = sc || document.scrollingElement;
  const r = el.getBoundingClientRect(); sc.scrollTop += (r.y + r.height / 2) - y; return sc;
};
window.__fieldRect = (re) => {
  const e = [...document.querySelectorAll("input")].find((e) => e.getClientRects().length && re.test(e.value.trim()));
  if (!e) return null; window.__place(e, 434); return window.__c(e.getBoundingClientRect());
};
// Cierra los avisos «Entendido» y deja la descripción a la vista: devuelve dónde hacer clic en ella
window.__prep = async () => {
  for (let k = 0; k < 3; k++) { for (const b of [...document.querySelectorAll("button")].filter((b) => b.textContent.trim() === "Entendido")) b.click(); await new Promise((s) => setTimeout(s, 1200)); }
  const ed = document.querySelector("[contenteditable=true]"); window.__place(ed, 380);
  await new Promise((s) => setTimeout(s, 300));
  const r = ed.getBoundingClientRect();
  return [(document.body.innerText.match(/Cargado[^\n]*|Cargando[^\n]*/) ?? [""])[0], Math.round((r.x + 80) * window.__S), Math.round((r.y + Math.min(r.height / 2, 20)) * window.__S)];
};
// Marca «Programación», acepta «Permitir» y devuelve dónde está el campo de la fecha
window.__sched = async () => {
  const lab = [...document.querySelectorAll("label,span")].find((e) => e.textContent.trim() === "Programación");
  lab.click(); await new Promise((s) => setTimeout(s, 800));
  const perm = [...document.querySelectorAll("button")].find((b) => b.textContent.trim() === "Permitir");
  if (perm) { perm.click(); await new Promise((s) => setTimeout(s, 800)); }
  return window.__fieldRect(/^\d{4}-\d\d-\d\d$/);
};
// Con el calendario abierto: mes en español con mayúscula ('Octubre') y día. Devuelve dónde hacer clic
window.__dayRect = async (mes, dia) => {
  for (let i = 0; i < 3; i++) {
    const mt = [...document.querySelectorAll(".month-title")].find((e) => e.getClientRects().length);
    if (!mt) return "sin calendario";
    if (mt.textContent.trim() === mes) break;
    const flechas = [...mt.closest(".title-wrapper").parentElement.querySelectorAll(".arrow")];
    flechas[flechas.length - 1].click(); await new Promise((s) => setTimeout(s, 500));
  }
  const d = [...document.querySelectorAll(".day.valid")].find((e) => e.getClientRects().length && e.textContent.trim() === String(dia));
  return d ? window.__c(d.getBoundingClientRect()) : "sin ese día";
};
// La hora sin depender de dónde cae la rueda. Con el selector abierto: await __time('19','30'), DESPUÉS una captura
// de pantalla (sin ella la pestaña oculta no pinta y el valor no entra), Escape y un clic fuera.
window.__pick = (lado, valor) => {
  const s = [...document.querySelectorAll(".tiktok-timepicker-option-text.tiktok-timepicker-" + lado)].find((e) => e.textContent.trim() === valor);
  if (!s) throw new Error("no hay opción " + valor);
  for (const el of [s, s.parentElement]) for (const t of ["pointerdown", "mousedown", "pointerup", "mouseup", "click"]) el.dispatchEvent(new MouseEvent(t, { bubbles: true, cancelable: true, view: window }));
};
window.__time = async (h, m = "00") => {
  await new Promise((s) => setTimeout(s, 1500)); window.__pick("left", h);
  await new Promise((s) => setTimeout(s, 800)); window.__pick("right", m);
  await new Promise((s) => setTimeout(s, 800)); return "ok";
};
// Solo pulsa «Programar» si hora, fecha y pie son los esperados: await __go('19:30,2026-10-24')
window.__go = async (esperado) => {
  const v = window.__vis().join();
  if (v !== esperado) return "NO, está " + v;
  if (window.__pie && document.querySelector("[contenteditable=true]").innerText.trim() !== window.__pie) return "NO, el pie no es " + window.__pie;
  const b = [...document.querySelectorAll("button")].find((b) => b.textContent.trim() === "Programar");
  b.click(); await new Promise((s) => setTimeout(s, 6000));
  return location.pathname + " | " + (document.body.innerText.match(/\d+ (sep|oct|nov|dic|ene|feb|mar|abr|may|jun|jul|ago), \d\d:\d\d/g) ?? []).slice(0, 5).join(", ");
};
"ayudas listas";
