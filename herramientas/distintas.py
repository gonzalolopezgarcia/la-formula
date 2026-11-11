"""¿Son las copias de prueba (trials) lo bastante distintas para que Instagram no las trate como el mismo vídeo?

La regla de mínimos (Gonzalo López, 11-nov-2026): entre el reel y sus copias (5 copias + el reel = 6 vídeos), NO
puede haber dos que compartan ninguna de estas cuatro cosas:
  cancion      otra canción de fondo en cada uno
  subtitulos   otro estilo de subtítulos en cada uno (contorno, caja negra, amarillo, caja blanca, mayúsculas…)
  contenido    otro contenido: otro gancho con otro cuerpo, u otro recorte del cuerpo (frases fuera, otro orden)
  titular      otro titular arriba (otra frase, no la misma con una palabra cambiada)
Y encima, lo más distinto posible: velocidad (si se da, tampoco se repite), color, encuadre, espejo.

Instagram reconoce un vídeo por lo que se ve y se oye: el color, la velocidad o el espejo solos no lo esconden.
Si no se cumple, se avisa y solo se sigue si la persona, después de leer el aviso, dice que sí.

Cada vídeo es un dict con cancion, subtitulos, contenido, titular y (opcional) velocidad. En una copia, None = como
el reel. «contenido» puede ser una tupla (gancho, cuerpo). Un vídeo sin subtítulos (un UGC mudo con su app):
subtitulos="sin subtítulos" en el reel y en sus copias, y esa palanca no se le pide (NO_APLICA).
"""
import re
import unicodedata

PALANCAS = ("cancion", "subtitulos", "contenido", "titular")
NOMBRE = {"cancion": "la canción", "subtitulos": "el estilo de subtítulos", "contenido": "el contenido (gancho y cuerpo)",
          "titular": "el titular", "velocidad": "la velocidad"}
NO_APLICA = {"subtitulos": "sin subtítulos"}

ARREGLOS = (
    "Canción: otra en cada copia, nunca la del reel ni la de otra copia.",
    "Subtítulos: otro estilo en cada copia (contorno, caja negra, amarillo, caja blanca, mayúsculas…).",
    "Contenido: cada copia otro gancho con otro cuerpo; si se acaban, otro recorte del cuerpo (frases fuera, otro orden).",
    "Titular: otra frase arriba en cada copia, la misma idea dicha de otra forma.",
    "Menos copias: mejor 3 que cumplan que 5 que se repitan.",
)


def _texto(t):
    t = re.sub(r"<[^>]+>", " ", str(t))   # un titular con <span class="acento">
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def mismo(palanca, a, b):
    """Dos valores de una palanca, ¿son lo mismo? Dos titulares que comparten 3 de cada 4 palabras, también."""
    if a is None or b is None:
        return a is None and b is None
    if palanca != "titular":
        return str(a) == str(b)
    x, y = set(_texto(a).split()), set(_texto(b).split())
    return x == y or (bool(x | y) and len(x & y) / len(x | y) >= 0.75)


def _nombre(k):
    return "el reel" if k == 0 else f"la copia {k}"


def revisar(copias, original):
    """Una línea por cada palanca repetida entre dos de los vídeos (el reel y sus copias). Vacía: cumplen."""
    videos = [original] + [{p: c.get(p) if c.get(p) is not None else original.get(p)
                            for p in (*PALANCAS, "velocidad")} for c in copias]
    avisos = []
    for p in (*PALANCAS, "velocidad"):
        if p == "velocidad" and any(c.get("velocidad") is None for c in copias):
            continue   # sin velocidades no se mira
        repes = []
        for i in range(len(videos)):
            for j in range(i + 1, len(videos)):
                a, b = videos[i].get(p), videos[j].get(p)
                if p in NO_APLICA and a == NO_APLICA[p] and b == NO_APLICA[p]:
                    continue
                if mismo(p, a, b):
                    repes.append(f"{_nombre(i)} y {_nombre(j)}")
        if repes:
            avisos.append(f"{NOMBRE[p]} se repite: {', '.join(repes[:5])}{'…' if len(repes) > 5 else ''}"
                          + (f" ({len(repes)} parejas)" if len(repes) > 5 else ""))
    return avisos


def aviso(avisos, seguir="--aun-asi", arreglos=ARREGLOS):
    """El texto que se le enseña a la persona, entero, antes de hacer nada."""
    return ("\n⚠ ESTAS COPIAS NO SON LO BASTANTE DISTINTAS\n"
            "Entre el reel y sus copias no puede repetirse la canción, el estilo de subtítulos, el contenido ni el\n"
            "titular. Instagram reconoce un vídeo por lo que se ve y se oye: el color, la velocidad o el espejo solos no\n"
            "lo esconden. Copias casi iguales se quedan en 0 visualizaciones y, si se repite, Instagram puede dejar de\n"
            "recomendar la cuenta.\n\n"
            + "\n".join("  · " + a for a in avisos)
            + "\n\nCómo arreglarlo:\n"
            + "\n".join(f"  {k}. {a}" for k, a in enumerate(arreglos, 1))
            + f"\n\nSi aun así quiere hacerlas, se vuelve a lanzar con {seguir}, solo después de que la persona haya\n"
              "leído este aviso y diga que sí.\n")
