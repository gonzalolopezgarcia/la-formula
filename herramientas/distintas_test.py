"""python3 distintas_test.py: la regla de las copias distintas (distintas.py)."""
from distintas import aviso, cambios, mismo, revisar

ORIGINAL = {"gancho": "A", "cuerpo": "1", "titular": "Claude ya usa tu móvil", "cancion": "time"}

# Solo otro titular y otra canción: 2 de 3, no llega
solo_titular = [{"titular": f"Titular {k}", "cancion": f"c{k}"} for k in range(5)]
avisos = revisar(solo_titular, ORIGINAL)
assert len(avisos) == 5 and all("2 de 3" in a for a in avisos), avisos   # entre ellas sí cambian titular y canción
solo_titulo = revisar([{"titular": f"T {k}"} for k in range(5)], ORIGINAL)
assert len(solo_titulo) == 6 and "10 parejas" in solo_titulo[-1], solo_titulo

# Gancho, titular y canción distintos en cada una: pasa
buenas = [{"gancho": g, "cuerpo": c, "titular": f"Otro {k}", "cancion": f"c{k}"}
          for k, (g, c) in enumerate([("B", "1"), ("C", "2"), ("A", "3"), ("B", "2"), ("C", "3")])]
assert revisar(buenas, ORIGINAL) == [], revisar(buenas, ORIGINAL)

# Dos copias que solo se diferencian en la canción
pareja = [{"gancho": "B", "cuerpo": "2", "titular": "Uno", "cancion": "x"},
          {"gancho": "B", "cuerpo": "2", "titular": "Uno", "cancion": "y"}]
assert any("copias 1 y 2" in a for a in revisar(pareja, ORIGINAL))

# Un titular con una palabra cambiada es el mismo titular
assert mismo("titular", "Claude ya usa tu móvil", "Claude YA usa tu movil!")
assert mismo("titular", "La IA ya maneja tu móvil hoy", "La IA ya maneja tu móvil")
assert mismo("titular", '6 virales / en <span class="acento">10 minutos</span>', "6 virales en 10 minutos")
assert not mismo("titular", "Tu móvil ya trabaja solo", "Claude ya usa tu móvil")

# El mismo titular que el original no cuenta; None = como el original
assert cambios({"titular": "Claude ya usa tu móvil", "cancion": "otra"}, ORIGINAL) == ["cancion"]
assert cambios({}, ORIGINAL) == []

assert "--aun-asi" in aviso(avisos) and "NO SON LO BASTANTE DISTINTAS" in aviso(avisos)
print("distintas: 9 comprobaciones bien")
