/* Motor de animación de La Fórmula. Lee los atributos del guion (guion.html) y monta UNA línea de tiempo
   de GSAP, parada y registrada para HyperFrames. Todo síncrono y sin callbacks: cada fotograma sale solo del
   tiempo que pide el render, así el vídeo sale igual cada vez.

   Tiempos: segundos del vídeo ya recortado (los de frases.txt). «+0.3» = 0,3 s después de empezar el bloque.

   data-en="12.4"            el elemento entra en ese segundo (desenfocado → nítido)
   data-como="pop|izq|fundido|baja|sacude"   otra forma de entrar (por defecto, sube). «baja»: cae desde arriba
                             con un rebote, como una notificación; «sacude»: entra temblando, como un error
   data-como="gira|barre|estira"   las que se salen de lo normal (una o dos por vídeo, en el giro de la idea):
                             «gira» se voltea como un panel; «barre» se destapa en círculo desde la esquina;
                             «estira» se abre como una ventana, primero una raya y luego se despliega
   data-clic="14.5"          un ratón llega y lo pulsa en ese segundo; se le añade la clase «pulsado»
   class="captura"           una imagen real: entra y sale de golpe, en un fotograma, salvo que lleve data-como
   data-cascada="12.4,0.12"  los hijos entran uno tras otro desde ese segundo
   data-cuenta="0,1700"      el número cuenta de 0 a 1700 (data-dur="0.9", data-dec="1")
   data-rueda="879,3787"     cuentakilómetros: cada cifra gira en su rueda, con punto de miles y coma decimal
                             («3.787», «502,8»). data-dec="1", data-dur="1.4". Para cifras reales que cambian
   data-barra="0.85"         la barra se llena hasta el 85 % («1,0.03»: llena que se vacía)
   data-traza                la línea SVG se dibuja (data-t = cuándo empieza; data-dur, o data-hasta="19.6" = la
                             palabra en que llega: así se pinta mientras hablas)
   data-cabeza="a"           con data-traza: un punto va en la punta. Dos tramos con la misma letra = una sola línea
   data-mueve="9.4:y=-150,scale=0.8"   en ese segundo se mueve algo que ya está en pantalla (data-mueve-dur,
                             data-mueve-curva="none"). «rotation=-30>0» fija también de dónde parte.
                             No en algo que lleve transform en el CSS
   data-escribe              el texto se teclea letra a letra (0,1 s por letra)
   data-clase="13.2:on"      en ese segundo se le añade la clase
   data-atenua="14.0"        en ese segundo baja al 35 %
   data-sale="15.1"          se va antes de que acabe el bloque
   <h2 class="titular relevo" data-en="8.0">  segundo titular en el mismo sitio (al primero, data-sale="7.9")
   data-queda                en el bloque: no se va al acabar (el del cierre)
   <div data-ritmo="lento"></div>   vídeo personal: todo entra y sale más despacio
   <section class="beat solo"> / <section class="beat entera">   pantalla partida: solo el gráfico / solo tú
*/
(function () {
  var tl = gsap.timeline({ paused: true });
  // Vídeo personal (<div data-ritmo="lento"></div> en el guion): todo entra y sale más despacio y cada
  var LENTO = !!document.querySelector('[data-ritmo="lento"]'), K = LENTO ? 2.2 : 1;
  var NITIDO = "blur(0px)";
  var ENTRADAS = {
    sube: { opacity: 0, filter: "blur(14px)", y: 12 },
    izq: { opacity: 0, filter: "blur(14px)", x: -18 },
    pop: { opacity: 0, filter: "blur(6px)", scale: 0.6 },
    fundido: { opacity: 0, filter: "blur(10px)" },
    baja: { opacity: 0, filter: "blur(0px)", y: -190 },
    sacude: { opacity: 0, filter: "blur(0px)", x: -46 },
    gira: { opacity: 0, filter: "blur(0px)", rotationX: -75, transformPerspective: 1400, transformOrigin: "50% 0%" },
    barre: { opacity: 1, filter: "blur(0px)", clipPath: "circle(0% at 100% 0%)" },
  };

  function todos(raiz, sel) { return Array.prototype.slice.call(raiz.querySelectorAll(sel)); }
  function deGolpe(el) { return el.classList.contains("captura") && !el.dataset.como; }
  function tiempo(valor, inicio) {
    var v = String(valor).trim();
    return v.charAt(0) === "+" ? inicio + parseFloat(v.slice(1)) : parseFloat(v);
  }
  function entra(el, t, como) {
    var forma = como || el.dataset.como || "sube";
    if (deGolpe(el)) {   // una captura no se anima: aparece en la palabra, como en sus virales
      el.style.opacity = "0";
      tl.set(el, { opacity: 1 }, t);
      return;
    }
    if (forma === "estira") {   // una ventana que se abre: primero una raya, luego se despliega
      tl.fromTo(el, { opacity: 0, filter: NITIDO, scaleX: 0.25, scaleY: 0.03 }, { opacity: 1, scaleX: 1, duration: 0.22 * K, ease: "power2.out" }, t);
      tl.to(el, { scaleY: 1, duration: 0.32 * K, ease: "power3.out" }, t + 0.22 * K);
      return;
    }
    var hasta = { opacity: 1, filter: NITIDO, x: 0, y: 0, scale: 1, duration: 0.4 * K, ease: "power2.out" };
    if (forma === "pop") { hasta.ease = LENTO ? "back.out(1.4)" : "back.out(1.7)"; hasta.duration = 0.36 * K; }
    if (forma === "baja") { hasta.ease = "back.out(1.2)"; hasta.duration = 0.55 * K; }
    if (forma === "sacude") { hasta.ease = "elastic.out(1.1, 0.22)"; hasta.duration = 0.9 * K; }
    if (forma === "gira") { hasta.rotationX = 0; hasta.ease = "back.out(1.4)"; hasta.duration = 0.6 * K; }
    if (forma === "barre") { hasta.clipPath = "circle(150% at 100% 0%)"; hasta.ease = "power2.inOut"; hasta.duration = 0.6 * K; }
    tl.fromTo(el, ENTRADAS[forma], hasta, t);
  }
  function envolver(el, clase) {
    var caja = document.createElement("div");
    caja.className = clase;
    while (el.firstChild) caja.appendChild(el.firstChild);
    el.appendChild(caja);
    return caja;
  }
  function partir(el, clase, porLetra) {
    if (!porLetra && el.querySelector(".acento")) {   // remotion: el titular con su palabra clave en el acento
      var conAcento = [];
      Array.prototype.forEach.call(el.childNodes, function (nodo) {
        var acento = nodo.nodeType === 1 && nodo.classList.contains("acento");
        nodo.textContent.trim().split(/\s+/).forEach(function (t) { if (t) conAcento.push({ t: t, acento: acento }); });
      });
      el.textContent = "";
      return conAcento.map(function (trozo, i) {
        var s = document.createElement("span");
        s.className = clase + (trozo.acento ? " acento" : "");
        s.textContent = i === conAcento.length - 1 ? trozo.t : trozo.t + " ";
        el.appendChild(s);
        return s;
      });
    }
    var trozos = porLetra ? el.textContent.split("") : el.textContent.trim().split(/\s+/);
    el.textContent = "";
    return trozos.map(function (trozo, i) {
      var s = document.createElement("span");
      s.className = clase;
      s.textContent = porLetra || i === trozos.length - 1 ? trozo : trozo + " ";
      el.appendChild(s);
      return s;
    });
  }

  // Cuentakilómetros: una columna por cifra con su tira de dígitos; todas giran a la vez y con la misma curva,
  // así las de la derecha dan más vueltas, como un contador de verdad. Una cifra que no estaba (879 → 3.787)
  // nace en blanco y se ensancha. Las tiras largas se recortan a 10-19 pasos sin cambiar la cifra final.
  function rueda(el, t0) {
    var p = el.dataset.rueda.split(","), dec = parseInt(el.dataset.dec || "0", 10), f = Math.pow(10, dec);
    var A = Math.round(parseFloat(p[0]) * f), B = Math.round(parseFloat(p[1]) * f);
    var dur = parseFloat(el.dataset.dur || "1.4"), curva = "power3.inOut";
    var cifras = Math.max(String(Math.max(A, B)).length, dec + 1);
    el.textContent = "";
    el.classList.add("rueda");
    for (var pos = cifras - 1; pos >= 0; pos--) {
      var col = document.createElement("span"), tira = document.createElement("span");
      col.className = "rd-c"; tira.className = "rd-tira";
      var a = Math.floor(A / Math.pow(10, pos)), b = Math.floor(B / Math.pow(10, pos));
      var estaA = a > 0 || pos <= dec, estaB = b > 0 || pos <= dec;
      var pasos = b - a, signo = pasos < 0 ? -1 : 1, n = Math.abs(pasos);
      if (n > 19) n = 10 + (((n - 10) % 10) + 10) % 10;   // a 30 fps, más de ~12 cifras por segundo parpadea
      for (var i = 0; i <= n; i++) {
        var d = document.createElement("span");
        var digito = (((a + signo * i) % 10) + 10) % 10;
        d.textContent = (i === 0 && !estaA) || (i === n && !estaB) ? " " : String(digito);
        tira.appendChild(d);
      }
      col.appendChild(tira);
      el.appendChild(col);
      if (n) tl.fromTo(tira, { yPercent: 0 }, { yPercent: -100 * n / (n + 1), duration: dur, ease: curva }, t0);
      if (!estaA && estaB) tl.fromTo(col, { width: 0 }, { width: "0.62em", duration: dur * 0.4, ease: "power2.out" }, t0);
      if (estaA && !estaB) tl.to(col, { width: 0, duration: dur * 0.4, ease: "power2.in" }, t0 + dur * 0.6);
      var sep = pos === dec && dec > 0 ? "," : pos > dec && (pos - dec) % 3 === 0 ? "." : "";
      if (sep) {
        var s = document.createElement("span");
        s.className = "rd-sep"; s.textContent = sep;
        el.appendChild(s);
        var conA = sep === "," || Math.floor(A / Math.pow(10, pos)) > 0, conB = sep === "," || Math.floor(B / Math.pow(10, pos)) > 0;
        if (!conA && conB) tl.fromTo(s, { width: 0, opacity: 0 }, { width: "0.26em", opacity: 1, duration: dur * 0.4, ease: "power2.out" }, t0);
        if (conA && !conB) tl.to(s, { width: 0, opacity: 0, duration: dur * 0.4 }, t0 + dur * 0.6);
      }
    }
  }

  function detalles(raiz, inicio) {
    todos(raiz, "[data-cascada]").forEach(function (el) {
      var p = el.dataset.cascada.split(",");
      var t0 = tiempo(p[0], inicio), paso = parseFloat(p[1] || "0.1");
      Array.prototype.forEach.call(el.children, function (hijo, i) { entra(hijo, t0 + i * paso, el.dataset.como); });
    });
    todos(raiz, "[data-en]:not(.titular)").forEach(function (el) { entra(el, tiempo(el.dataset.en, inicio)); });

    function cuando(el) {   // el segundo en que arranca un detalle: el suyo o el de quien lo contiene
      var dueno = el.closest("[data-en]");
      return el.dataset.t ? tiempo(el.dataset.t, inicio) : dueno ? tiempo(dueno.dataset.en, inicio) : inicio;
    }
    todos(raiz, "[data-cuenta]").forEach(function (el) {
      var p = el.dataset.cuenta.split(","), dec = parseInt(el.dataset.dec || "0", 10);
      tl.fromTo(el, { textContent: parseFloat(p[0]) },
        { textContent: parseFloat(p[1]), snap: { textContent: Math.pow(10, -dec) },
          duration: parseFloat(el.dataset.dur || "0.9"), ease: "power2.out" }, cuando(el) + 0.05);
    });
    todos(raiz, "[data-rueda]").forEach(function (el) { rueda(el, cuando(el) + 0.05); });
    todos(raiz, "[data-mueve]").forEach(function (el) {
      var p = el.dataset.mueve.split(":"), hacia = { duration: parseFloat(el.dataset.mueveDur || "0.5") * K, ease: el.dataset.mueveCurva || "power3.inOut" };
      var desde = null;
      p[1].split(",").forEach(function (par) {
        var kv = par.split("="), v = kv[1].split(">"), k = kv[0].trim();
        if (v.length > 1) { desde = desde || {}; desde[k] = parseFloat(v[0]); }
        hacia[k] = parseFloat(v[v.length - 1]);
      });
      if (desde) tl.fromTo(el, desde, hacia, tiempo(p[0], inicio));
      else tl.to(el, hacia, tiempo(p[0], inicio));
    });
    todos(raiz, "[data-barra]").forEach(function (el) {
      var v = el.dataset.barra.split(",");
      tl.fromTo(el, { scaleX: v.length > 1 ? parseFloat(v[0]) : 0, transformOrigin: "left center" },
        { scaleX: parseFloat(v[v.length - 1]), duration: parseFloat(el.dataset.dur || "0.7"), ease: "power2.out" },
        cuando(el) + 0.1);
    });
    var cabezas = {};
    todos(raiz, "[data-traza]").forEach(function (el) {
      el.setAttribute("pathLength", "100");
      // data-hasta: la línea llega a su final en ESA palabra, así se pinta mientras habla
      var t0 = cuando(el), llega = el.dataset.hasta;
      var dur = llega ? tiempo(llega, inicio) - t0 : parseFloat(el.dataset.dur || "0.45");
      var curva = llega ? "power1.inOut" : "power2.inOut";
      tl.fromTo(el, { attr: { "stroke-dashoffset": 101 } }, { attr: { "stroke-dashoffset": 0 }, duration: dur, ease: curva }, t0);
      if (el.dataset.cabeza === undefined) return;
      // la cabeza: un punto que va en la punta. Es una copia de la misma línea con un solo trazo de
      // longitud cero y punta redonda, movida con el mismo tween: no puede ir desacompasada.
      // Los tramos con el mismo data-cabeza se la pasan: la línea que se para y sigue es una sola.
      var c = el.cloneNode(false), clave = el.dataset.cabeza;
      c.removeAttribute("data-traza");
      c.setAttribute("class", "cabeza");
      c.style.opacity = "0";
      el.parentNode.appendChild(c);
      if (cabezas[clave]) tl.set(cabezas[clave], { opacity: 0 }, t0);
      cabezas[clave] = c;
      tl.set(c, { opacity: 1 }, t0);
      tl.fromTo(c, { attr: { "stroke-dashoffset": 0 } }, { attr: { "stroke-dashoffset": -99.9 }, duration: dur, ease: curva }, t0);
    });
    todos(raiz, "[data-escribe]").forEach(function (el) {
      var t0 = cuando(el);
      partir(el, "letra", true).forEach(function (letra, i) {
        letra.style.display = "none";
        tl.set(letra, { display: "inline-block" }, t0 + i * 0.1);
      });
    });
    todos(raiz, "[data-clase]").forEach(function (el) {
      var p = el.dataset.clase.split(":");
      tl.set(el, { className: el.className + " " + p[1] }, tiempo(p[0], inicio));
    });
    todos(raiz, "[data-clic]").forEach(function (el) {   // el ratón llega medio segundo antes, pulsa y se va
      var t = tiempo(el.dataset.clic, inicio), raton = document.createElement("i");
      raton.className = "raton";
      raton.innerHTML = '<svg viewBox="0 0 24 24"><path d="M5 2.5l14 10.6-6.4.9 3.8 7.4-2.9 1.4-3.7-7.5-4.8 4.6z"/></svg>';
      el.appendChild(raton);
      tl.fromTo(raton, { opacity: 0, x: 150, y: 170 }, { opacity: 1, x: 0, y: 0, duration: 0.45, ease: "power2.out" }, t - 0.5);
      tl.to([raton, el], { scale: 0.9, duration: 0.07, yoyo: true, repeat: 1, ease: "power1.inOut" }, t);
      tl.set(el, { className: el.className + " pulsado" }, t);
      tl.to(raton, { opacity: 0, duration: 0.25 }, t + 0.7);
    });
    todos(raiz, "[data-atenua]").forEach(function (el) {
      tl.to(el, { opacity: 0.35, duration: 0.3, ease: "power1.out" }, tiempo(el.dataset.atenua, inicio));
    });
    todos(raiz, "[data-sale]").forEach(function (el) {
      if (deGolpe(el)) tl.set(el, { opacity: 0 }, tiempo(el.dataset.sale, inicio));
      else tl.to(el, { opacity: 0, filter: "blur(10px)", duration: 0.22, ease: "power1.in" }, tiempo(el.dataset.sale, inicio));
    });
  }

  function salida(cuerpo, fin) {
    tl.to(cuerpo, { opacity: 0, filter: "blur(10px)", duration: 0.2 * K, ease: "power1.in" }, fin - 0.2 * K);
  }

  var lienzo = document.getElementById("root");
  // estilo clip: cuando acaba el clip de otro, él sube desde la costura hasta llenar la pantalla
  // (con transform: top y height saltan de píxel en píxel y HyperFrames no los deja)
  var elClip = document.getElementById("clip");
  if (elClip) {
    var costura = parseFloat(getComputedStyle(lienzo).getPropertyValue("--costura"));
    tl.fromTo("#base", { y: costura, borderRadius: "30px 30px 0px 0px" },
      { y: 0, borderRadius: "0px 0px 0px 0px", duration: 0.45, ease: "power3.out" }, parseFloat(elClip.dataset.duration));
  }
  todos(document, ".beat").forEach(function (beat) {
    var a = parseFloat(beat.dataset.start), b = a + parseFloat(beat.dataset.duration);
    // estilo remotion: mientras dura, el plano cambia (kit/remotion.css): solo el gráfico o solo él
    var plano = beat.classList.contains("entera") ? "entera" : beat.classList.contains("solo") ? "solo" : "";
    if (plano) { tl.set(lienzo, { className: plano }, a); tl.set(lienzo, { className: "" }, b); }
    todos(beat, ".titular").forEach(function (titular) {   // con data-en, releva al anterior sin cambiar el gráfico
      tl.fromTo(partir(titular, "w"), { opacity: 0, filter: "blur(12px)", x: -10 },
        { opacity: 1, filter: NITIDO, x: 0, duration: 0.34 * K, ease: "power2.out", stagger: 0.05 * K },
        titular.dataset.en ? tiempo(titular.dataset.en, a) : a);
    });
    var cuerpo = envolver(beat, "cuerpo");
    if (LENTO) tl.fromTo(cuerpo, { scale: 0.97, transformOrigin: "left top" }, { scale: 1.03, duration: b - a, ease: "none" }, a);
    detalles(cuerpo, a);
    var soloCapturas = todos(cuerpo, ".captura").length && todos(cuerpo, ".titular, [data-en], [data-cascada]").every(deGolpe);
    if (!beat.hasAttribute("data-queda") && !soloCapturas) salida(cuerpo, b);   // el último bloque aguanta; las capturas se van de golpe
  });

  todos(document, ".enfasis").forEach(function (enf) {
    var a = parseFloat(enf.dataset.start), b = a + parseFloat(enf.dataset.duration);
    todos(enf, "span").forEach(function (palabra) {
      var raya = document.createElement("i");
      palabra.appendChild(raya);
      var t = tiempo(palabra.dataset.en || "+0", a);
      tl.fromTo(raya, { scaleX: 0, transformOrigin: "left center" }, { scaleX: 1, duration: 0.3, ease: "power2.out" }, t + 0.12);
    });
    var cuerpo = envolver(enf, "cuerpo");
    detalles(cuerpo, a);
    salida(cuerpo, b);
  });

  todos(document, ".gancho").forEach(function (g) {   // está desde el fotograma 0: es la portada
    salida(envolver(g, "cuerpo"), parseFloat(g.dataset.start) + parseFloat(g.dataset.duration));
  });

  window.__timelines = window.__timelines || {};
  window.__timelines["formula"] = tl;
})();
