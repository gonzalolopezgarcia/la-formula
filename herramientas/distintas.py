"""¿Son las copias de prueba (trials) lo bastante distintas para que Instagram no las trate como el mismo vídeo?

Instagram reconoce un vídeo por lo que se ve y se oye. Lo que de verdad lo hace otro vídeo, los «cambios grandes»:
  gancho   otra toma de los primeros segundos (otro comienzo grabado)
  cuerpo   otro corte del cuerpo: frases quitadas o en otro orden
  titular  otro titular en pantalla (otra frase, no la misma con una palabra cambiada)
  cancion  otra canción de fondo
El color, la velocidad (3-10 %), el zoom, el grano, el espejo, el estilo de los subtítulos o un fichero nuevo se
suman encima, pero no cuentan: sin cambios grandes, el vídeo sigue siendo el mismo.

La regla (Gonzalo López, 11-nov-2026): cada copia, al menos 3 cambios grandes frente al original y al menos 2
frente a cada una de las otras copias. Mejor 3 copias distintas que 5 parecidas. Si no llega, se avisa y solo se
sigue si la persona, después de leer el aviso, dice que sí.

Cada copia es un dict con gancho, cuerpo, titular y cancion; None = como el original. El original, igual.
"""
import re
import unicodedata

PALANCAS = ("gancho", "cuerpo", "titular", "cancion")
NOMBRE = {"gancho": "otro gancho grabado", "cuerpo": "otro corte del cuerpo", "titular": "otro titular",
          "cancion": "otra canción"}
MINIMO_ORIGINAL = 3
MINIMO_ENTRE_COPIAS = 2

ARREGLOS = (
    "Graba 2 o 3 comienzos más (los primeros 3-5 segundos dichos de otra forma): cada copia empieza con uno.",
    "Quita en cada copia una frase distinta del cuerpo (una que no haga falta para entenderlo), o cambia el orden.",
    "Pon otra canción de fondo en cada copia, nunca la del original.",
    "Escribe otro titular para cada copia: la misma idea, dicha de otra forma.",
    "Haz menos copias: mejor 3 distintas que 5 parecidas.",
)


def _texto(t):
    t = re.sub(r"<[^>]+>", " ", str(t))   # un titular con <span class="acento">
    t = unicodedata.normalize("NFKD", str(t)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def mismo(palanca, a, b):
    """Dos valores de una palanca, ¿son lo mismo? Dos titulares que comparten 3 de cada 4 palabras, también."""
    if a is None or b is None:
        return a is None and b is None
    if palanca != "titular":
        return str(a) == str(b)
    x, y = set(_texto(a).split()), set(_texto(b).split())
    return x == y or (bool(x | y) and len(x & y) / len(x | y) >= 0.75)


def cambios(copia, original):
    """Los cambios grandes de una copia frente al original."""
    return [p for p in PALANCAS if copia.get(p) is not None and not mismo(p, copia[p], original.get(p))]


def _lista(palancas):
    return ", ".join(NOMBRE[p] for p in palancas) or "nada grande"


def revisar(copias, original):
    """Una línea por copia (o pareja de copias) que no llega. Vacía: todas son lo bastante distintas."""
    avisos = []
    for i, c in enumerate(copias):
        hechos = cambios(c, original)
        if len(hechos) < MINIMO_ORIGINAL:
            faltan = [NOMBRE[p] for p in PALANCAS if p not in hechos]
            avisos.append(f"copia {i + 1}: frente al original solo cambia {_lista(hechos)} ({len(hechos)} de "
                          f"{MINIMO_ORIGINAL}); súmale {' o '.join(faltan)}")
    efectiva = [{p: c.get(p) if c.get(p) is not None else original.get(p) for p in PALANCAS} for c in copias]
    pares = {}
    for i in range(len(copias)):
        for j in range(i + 1, len(copias)):
            distintas = tuple(p for p in PALANCAS if not mismo(p, efectiva[i][p], efectiva[j][p]))
            if len(distintas) < MINIMO_ENTRE_COPIAS:
                pares.setdefault(distintas, []).append(f"{i + 1} y {j + 1}")
    for distintas, cuales in pares.items():
        if len(cuales) == 1:
            avisos.append(f"copias {cuales[0]}: entre ellas solo cambia {_lista(distintas)}" if distintas
                          else f"copias {cuales[0]}: entre ellas no cambia nada grande")
        elif distintas:
            avisos.append(f"{len(cuales)} parejas de copias solo se diferencian en {_lista(distintas)} "
                          f"({', '.join(cuales[:4])}{'…' if len(cuales) > 4 else ''})")
        else:
            avisos.append(f"{len(cuales)} parejas de copias no se diferencian en nada grande "
                          f"({', '.join(cuales[:4])}{'…' if len(cuales) > 4 else ''})")
    return avisos


def aviso(avisos, seguir="--aun-asi", arreglos=ARREGLOS):
    """El texto que se le enseña a la persona, entero, antes de hacer nada."""
    return ("\n⚠ ESTAS COPIAS NO SON LO BASTANTE DISTINTAS\n"
            "Instagram reconoce un vídeo por lo que se ve y se oye: el color, la velocidad, el zoom o el espejo no lo\n"
            "esconden. Copias casi iguales se quedan en 0 visualizaciones y, si se repite, Instagram puede dejar de\n"
            "recomendar la cuenta.\n\n"
            + "\n".join("  · " + a for a in avisos)
            + "\n\nCómo arreglarlo (de más a menos eficaz):\n"
            + "\n".join(f"  {k}. {a}" for k, a in enumerate(arreglos, 1))
            + f"\n\nSi aun así quiere hacerlas, se vuelve a lanzar con {seguir}, solo después de que la persona haya\n"
              "leído este aviso y diga que sí.\n")
