"""python3 distintas_test.py: la regla de mínimos de las copias (distintas.py)."""
from distintas import aviso, mismo, revisar

REEL = {"cancion": "time", "subtitulos": "el del reel", "contenido": ("A", "1"),
        "titular": "Claude ya usa tu móvil", "velocidad": 1.0}
SUBS = ["contorno", "caja negra", "amarillo", "caja blanca", "mayúsculas"]
COMBOS = [("B", "1"), ("C", "2"), ("A", "3"), ("B", "2"), ("C", "3")]
TITULOS = ["Tu móvil ya trabaja solo", "La IA ya maneja tu móvil", "Claude toca la pantalla por ti",
           "Ya no tocas tu móvil", "Un asistente dentro del teléfono"]


def buenas():
    return [{"cancion": f"c{k}", "subtitulos": SUBS[k], "contenido": COMBOS[k], "titular": TITULOS[k],
             "velocidad": [1.05, 1.08, 1.03, 1.10, 1.06][k]} for k in range(5)]


# Las 6 distintas en las cuatro: pasa
assert revisar(buenas(), REEL) == [], revisar(buenas(), REEL)

# La misma canción en dos copias
c = buenas(); c[3]["cancion"] = "c1"
assert any("la canción se repite: la copia 2 y la copia 4" in a for a in revisar(c, REEL)), revisar(c, REEL)

# Una copia con la canción del reel (None = como el reel)
c = buenas(); c[0]["cancion"] = None
assert any("el reel y la copia 1" in a for a in revisar(c, REEL))

# Una copia con el contenido del reel (A1)
c = buenas(); c[2]["contenido"] = ("A", "1")
assert any(a.startswith("el contenido") for a in revisar(c, REEL))

# Subtítulos repetidos; un titular con una palabra de más sigue siendo otro si cambia bastante
c = buenas(); c[4]["subtitulos"] = "contorno"
assert any(a.startswith("el estilo de subtítulos") for a in revisar(c, REEL))
c = buenas(); c[1]["titular"] = "Claude ya usa tu movil!"
assert any(a.startswith("el titular se repite: el reel y la copia 2") for a in revisar(c, REEL))

# Un vídeo sin subtítulos (UGC mudo): esa palanca no se pide
mudo = dict(REEL, subtitulos="sin subtítulos")
c = buenas()
for x in c:
    x["subtitulos"] = "sin subtítulos"
assert not any(a.startswith("el estilo") for a in revisar(c, mudo))

# Solo cambia el titular: avisa de canción, subtítulos y contenido (las 15 parejas de 6 vídeos)
solo = revisar([{"titular": t} for t in TITULOS], REEL)
assert len(solo) == 3 and "15 parejas" in solo[0], solo

assert mismo("titular", '6 virales / en <span class="acento">10 minutos</span>', "6 virales en 10 minutos")
assert "--aun-asi" in aviso(solo) and "NO SON LO BASTANTE DISTINTAS" in aviso(solo)
print("distintas: 10 comprobaciones bien")
