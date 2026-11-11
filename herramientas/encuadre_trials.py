"""Zoom, encuadre y grano de cada copia de prueba (trial), con control de calidad.

Gonzalo López, 11-nov-2026: «que la calidad sea aceptable pero que nos encarguemos de meterle las variaciones
suficientes para que sean distintos… con un control de calidad… que por variar no salga una mierda. Sobre todo para
cuando las variaciones tienen de más en común».

Medido en un fotograma de su reel con una huella perceptiva (dHash, 256 puntos), qué cambia cada cosa:
  zoom 3-9 % anclado en la cara y la imagen corrida hasta 24 px   12-35 % de la huella
  espejo                                                          ~50 %
  color, grano                                                     ~1 %: solo cambian los píxeles del fichero
Por eso el reparto (`repartir`) da los encuadres más distintos a las piezas que más se parecen (mismo gancho, mismo
corte, mismo espejo), el reel incluido, que va sin zoom. Y antes de hacer cada copia, el control:
  nitidez  la de la cara (sin ella, el centro), con la imagen a un cuarto: la mediana de los fotogramas ≥ 88 % de la del
           original y el peor ≥ 80 %. Si no, el zoom baja un escalón y se mide otra vez. A un cuarto, el ruido fino del
           sensor o de una pantalla oscura no cuenta y sí la blandura que se ve: con 9 % salía 90-99 % (a la vista,
           igual); con 20 %, 80-85 % (a la vista, más blanda)
  grano    invisible: ≥ 40 dB frente a la misma imagen sin grano, y el fichero no más de un 25 % más pesado. Si no, un
           nivel menos (el 2 daba 41-44 dB y -6 a +5 %; el 3, 39-40 dB; el 4, 37 dB y el doble de peso)
  letras   en un vídeo con texto ya quemado: el zoom nunca deja una letra a menos de 12 px del borde
Solo Python y ffmpeg, sin numpy: el mismo fichero va en edit-social-gonzalo, en el kit, en la-formula y en la skill
pública reels-de-prueba. Se cambia en uno y se copia a los otros tres.
"""
import itertools
import re
import subprocess

ZOOMS = (1.03, 1.045, 1.06, 1.075, 1.09)
MUEVE = (-24, -12, 0, 12, 24)     # px que la cara se mueve en pantalla (+ a la izquierda)
GRANO = 2
NITIDEZ_MIN = 0.88     # la mediana de los fotogramas
NITIDEZ_PEOR = 0.80    # y el peor
GRANO_DB_MIN = 40.0
PESO_MAX = 1.25
MARGEN_LETRAS = 12


# ── el reparto ──────────────────────────────────────────────────────────────────────────────────────────────────────

def parecido(a, b):
    """Cuánto se parecen dos piezas en lo que el encuadre puede compensar: el mismo gancho pesa 2 (es lo primero que se
    ve), el mismo cuerpo o corte 1 y el mismo espejo 1."""
    return (2 * (a.get("gancho") == b.get("gancho")) + (a.get("cuerpo") == b.get("cuerpo"))
            + (bool(a.get("espejo")) == bool(b.get("espejo"))))


def _dist(e, f):
    return abs(e[0] - f[0]) / (ZOOMS[-1] - ZOOMS[0]) + abs(e[1] - f[1]) / (MUEVE[-1] - MUEVE[0])


def repartir(copias, reel=None, fijos=None):
    """[(zoom, mueve)] de cada copia.

    copias  [{"gancho", "cuerpo", "espejo"}], en orden; reel, lo mismo del original (va sin zoom: 1.0, 0)
    fijos   {i: (zoom, mueve)} de las copias ya hechas, que no se tocan (una copia vieja sin zoom: (1.0, 0))
    Entre las parejas que más se parecen (parecido ≥ 2, el reel incluido), la menor distancia de encuadre, lo más
    grande posible; a igualdad, la suma pesada por el parecido. Hasta 5 copias, cada una con un zoom y un desplazamiento
    que no lleva otra (todas las permutaciones de los que quedan libres); más de 5, de una en una sobre la rejilla."""
    reel = reel or {"gancho": None, "cuerpo": None, "espejo": False}
    fijos = {k: tuple(v) for k, v in (fijos or {}).items() if k < len(copias)}
    piezas = [reel, *copias]
    pares = [(i, j, parecido(piezas[i], piezas[j])) for i, j in itertools.combinations(range(len(piezas)), 2)]
    libres = [k for k in range(len(copias)) if k not in fijos]

    def nota(asig):
        enc = [(1.0, 0)] + [fijos.get(k) or asig.get(k) for k in range(len(copias))]
        hay = [(i, j, p) for i, j, p in pares if enc[i] is not None and enc[j] is not None]
        criticas = [_dist(enc[i], enc[j]) for i, j, p in hay if p >= 2]
        return (min(criticas) if criticas else 0.0, sum(p * _dist(enc[i], enc[j]) for i, j, p in hay))

    asig = {}
    if len(copias) <= len(ZOOMS):
        zs = [z for z in ZOOMS if z not in {v[0] for v in fijos.values()}]
        ms = [m for m in MUEVE if m not in {v[1] for v in fijos.values()}]
        while len(zs) < len(libres):
            zs.append(ZOOMS[len(zs) % len(ZOOMS)])
        while len(ms) < len(libres):
            ms.append(MUEVE[len(ms) % len(MUEVE)])
        mejor = None
        for pz in itertools.permutations(zs, len(libres)):
            for pm in itertools.permutations(ms, len(libres)):
                prueba = dict(zip(libres, zip(pz, pm)))
                n = nota(prueba)
                if mejor is None or n > mejor[0]:
                    mejor = (n, prueba)
        asig = mejor[1] if mejor else {}
    else:
        rejilla = list(itertools.product(ZOOMS, MUEVE))
        for k in libres:
            asig[k] = max(rejilla, key=lambda e: nota({**asig, k: e}))
    return [fijos.get(k) or asig[k] for k in range(len(copias))]


# ── los filtros ─────────────────────────────────────────────────────────────────────────────────────────────────────

def _ventana(z, m, ancho, alto, ancla_y):
    """(ancho y alto escalados, x e y del recorte, dónde queda el ancla en pantalla)."""
    W, H = max(ancho, round(ancho * z / 2) * 2), max(alto, round(alto * z / 2) * 2)
    ay = alto / 2 if ancla_y is None else ancla_y
    x = min(max(0, round(ancho / 2 * W / ancho - ancho / 2 + m)), W - ancho)
    y = min(max(0, round(ay * H / alto - ay)), H - alto)
    return W, H, x, y, (ancho / 2 * W / ancho - x, ay * H / alto - y)


def filtro(z, m, ancho=1080, alto=1920, ancla_y=None):
    """El zoom z anclado en (centro, ancla_y) —la cara; sin ella, el centro de la imagen— con la imagen corrida m px.
    "" si no cambia nada."""
    W, H, x, y, _ = _ventana(z, m, ancho, alto, ancla_y)
    if W == ancho and H == alto:
        return ""
    return f"scale={W}:{H}:flags=lanczos,crop={ancho}:{alto}:{x}:{y}"


def filtro_grano(nivel, semilla):
    """Grano que cambia en cada fotograma (allf=t), con su semilla: "" con nivel 0."""
    return f"noise=alls={nivel}:allf=t:all_seed={semilla}" if nivel else ""


def unir(*filtros):
    return ",".join(f for f in filtros if f)


# ── medir ───────────────────────────────────────────────────────────────────────────────────────────────────────────

def tamano(ff, video):
    """(ancho, alto) del vídeo tal como se ve, según ffmpeg."""
    r = subprocess.run([ff, "-hide_banner", "-i", str(video)], capture_output=True, text=True)
    m = re.search(r"Video:.*?\b(\d{2,5})x(\d{2,5})[\s,\[]", r.stderr)
    if not m:
        raise SystemExit(f"No sé el tamaño de {video}")
    w, h = int(m.group(1)), int(m.group(2))
    if re.search(r"rotate\s*:\s*-?(90|270)|rotation of -?90", r.stderr):
        w, h = h, w
    return w, h


def duracion(ff, video):
    r = subprocess.run([ff, "-hide_banner", "-i", str(video)], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r.stderr)
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3)) if m else 0.0


def tiempos_de(ff, video, n=8):
    """Los fotogramas que se miden: 0,5 y 1,5 s (donde suele estar el titular) y n repartidos por el vídeo."""
    d = duracion(ff, video)
    return sorted({round(t, 2) for t in [0.5, 1.5] + [d * (k + 0.5) / n for k in range(n)] if 0.2 < t < d - 0.2})


def _gris(ff, video, t, vf, ancho, alto, escala=2):
    """Un fotograma en gris (bytes), con vf, a 1/escala: a la mitad, para buscar letras; a un cuarto, para la nitidez."""
    w, h = ancho // escala, alto // escala
    cadena = unir(vf, f"scale={w}:{h}:flags=lanczos", "format=gray")
    r = subprocess.run([ff, "-v", "error", "-ss", f"{t:.3f}", "-i", str(video), "-frames:v", "1", "-vf", cadena,
                        "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True)
    return r.stdout if len(r.stdout) == w * h else None


def _laplaciano(px, w, h, cx, cy, r):
    """Varianza del laplaciano en el cuadrado de lado 2r centrado en (cx, cy): la nitidez de esa zona."""
    x0, x1 = max(1, int(cx - r)), min(w - 1, int(cx + r))
    y0, y1 = max(1, int(cy - r)), min(h - 1, int(cy + r))
    n = s = s2 = 0
    for y in range(y0, y1):
        f = y * w
        for x in range(x0, x1):
            i = f + x
            v = 4 * px[i] - px[i - 1] - px[i + 1] - px[i - w] - px[i + w]
            n += 1
            s += v
            s2 += v * v
    return (s2 / n - (s / n) ** 2) if n else 0.0


def nitidez(ff, video, z, m, tiempos, ancho, alto, ancla_y=None, vf_antes="", _cache=None):
    """(mediana, peor) de (nitidez con el zoom) / (nitidez sin él) en los fotogramas de `tiempos`, con la imagen a un
    cuarto, en la cara (un cuadrado del 30 % del ancho) o, sin ella, en el centro (56 %); el cuadrado crece con el zoom y
    se mueve con la imagen, así se compara lo mismo."""
    zf = filtro(z, m, ancho, alto, ancla_y)
    if not zf:
        return 1.0, 1.0
    W, H, x, y, (axs, ays) = _ventana(z, m, ancho, alto, ancla_y)
    ay = alto / 2 if ancla_y is None else ancla_y
    r = (0.15 if ancla_y is not None else 0.28) * ancho / 4
    w4, h4 = ancho // 4, alto // 4
    cache = _cache if _cache is not None else {}
    razones = []
    for t in tiempos:
        if t not in cache:
            px = _gris(ff, video, t, vf_antes, ancho, alto, 4)
            cache[t] = _laplaciano(px, w4, h4, ancho / 8, ay / 4, r) if px else 0.0
        antes = cache[t]
        if antes < 2:   # un fotograma liso (negro, un fundido): no dice nada
            continue
        px = _gris(ff, video, t, unir(vf_antes, zf), ancho, alto, 4)
        if px:
            razones.append(_laplaciano(px, w4, h4, axs / 4, ays / 4, r * W / ancho) / antes)
    if not razones:
        return 1.0, 1.0
    razones.sort()
    return razones[len(razones) // 2], razones[0]


def _es_letra(px, i, w):
    """Un píxel muy claro (≥ 225) con uno muy oscuro (≤ 40) a 1-2 px: el borde de un subtítulo, o una letra sobre su caja."""
    return px[i] >= 225 and min(px[i - 2], px[i - 1], px[i + 1], px[i + 2], px[i - w], px[i + w]) <= 40


def letras(ff, video, tiempos, ancho, alto, vf_antes="", franja=140):
    """La caja (x0, y0, x1, y1), en px del vídeo, del texto quemado que hay a menos de `franja` px de algún borde (lo
    único que un zoom de hasta el 9 % con 24 px de desplazamiento puede cortar). Cuenta como texto una fila con al menos
    6 píxeles de letra (4 en las franjas de los lados, donde solo entra un trozo). None si no hay."""
    w, h, b = ancho // 2, alto // 2, franja // 2
    caja = None
    for t in tiempos:
        px = _gris(ff, video, t, vf_antes, ancho, alto)
        if not px:
            continue
        for y in range(2, h - 2):
            f = y * w
            if y < b or y >= h - b:
                xs, minimo = [x for x in range(2, w - 2) if _es_letra(px, f + x, w)], 6
            else:
                xs, minimo = [x for x in (*range(2, b), *range(w - b, w - 2)) if _es_letra(px, f + x, w)], 4
            if len(xs) >= minimo:
                c = (min(xs), y, max(xs), y)
                caja = c if caja is None else (min(caja[0], c[0]), min(caja[1], c[1]), max(caja[2], c[2]), max(caja[3], c[3]))
    return None if caja is None else tuple(v * 2 for v in caja)


def corta_letras(z, m, ancho, alto, caja, ancla_y=None, margen=MARGEN_LETRAS):
    """¿Ese zoom deja alguna letra de `caja` fuera o a menos de `margen` px del borde?"""
    if not caja:
        return False
    W, H, x, y, _ = _ventana(z, m, ancho, alto, ancla_y)
    k = W / ancho
    x0, x1 = x / k, (x + ancho) / k
    y0, y1 = y / k, (y + alto) / k
    return caja[0] < x0 + margen or caja[2] > x1 - margen or caja[1] < y0 + margen or caja[3] > y1 - margen


def elegir_zoom(ff, video, z, m, ancho, alto, ancla_y=None, tiempos=None, con_letras=False, vf_antes=""):
    """El zoom que pasa el control, empezando por z y bajando por ZOOMS hasta 1,0 (sin zoom). Devuelve
    (zoom, mueve, nitidez mediana, motivo de la bajada o "")."""
    tiempos = tiempos or tiempos_de(ff, video)
    caja = letras(ff, video, tiempos, ancho, alto, vf_antes) if con_letras else None
    cache, motivo = {}, ""
    for cand in [z] + [c for c in sorted(ZOOMS, reverse=True) if c < z]:
        if corta_letras(cand, m, ancho, alto, caja, ancla_y):
            motivo = motivo or f"con {cand:.3f} cortaba letras junto al borde"
            continue
        n, peor = nitidez(ff, video, cand, m, tiempos, ancho, alto, ancla_y, vf_antes, cache)
        if n >= NITIDEZ_MIN and peor >= NITIDEZ_PEOR:
            return cand, m, n, motivo
        motivo = motivo or f"con {cand:.3f} la imagen quedaba al {n:.0%} de nitidez (el peor fotograma, {peor:.0%})"
    return 1.0, 0, 1.0, motivo or "sin zoom"


def _psnr(ff, video, t, vf, nivel, semilla):
    g = f"[0:v]{vf or 'null'},split[a][b];[a]{filtro_grano(nivel, semilla)}[n];[n][b]psnr"
    r = subprocess.run([ff, "-hide_banner", "-nostats", "-ss", f"{t:.3f}", "-t", "1", "-i", str(video),
                        "-filter_complex", g, "-f", "null", "-"], capture_output=True, text=True)
    m = re.search(r"average:([\d.]+|inf)", r.stderr)
    return 99.0 if not m or m.group(1) == "inf" else float(m.group(1))


def _peso(ff, video, t, vf, nivel, semilla):
    """Bytes de 2 s codificados como una copia (x264, crf 18), con ese grano."""
    r = subprocess.run([ff, "-v", "error", "-ss", f"{t:.3f}", "-t", "2", "-i", str(video), "-an",
                        "-vf", unir(vf, filtro_grano(nivel, semilla)) or "null", "-c:v", "libx264", "-preset", "veryfast",
                        "-crf", "18", "-f", "mp4", "-movflags", "frag_keyframe+empty_moov", "-"], capture_output=True)
    return len(r.stdout)


def elegir_grano(ff, video, semilla, t=None, vf="", nivel=GRANO):
    """El grano que pasa el control (invisible y sin engordar el fichero), de `nivel` hacia abajo. (nivel, dB)."""
    t = duracion(ff, video) / 2 if t is None else t
    sin = None
    for n in range(nivel, 0, -1):
        db = _psnr(ff, video, t, vf, n, semilla)
        if db < GRANO_DB_MIN:
            continue
        sin = sin or _peso(ff, video, t, vf, 0, semilla)
        if not sin or _peso(ff, video, t, vf, n, semilla) <= sin * PESO_MAX:
            return n, db
    return 0, None
