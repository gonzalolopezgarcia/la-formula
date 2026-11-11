"""python3 encuadre_trials_test.py: el reparto de zoom y encuadre de las copias y lo que se mide (encuadre_trials.py)."""
from encuadre_trials import (MUEVE, ZOOMS, _es_letra, _laplaciano, _ventana, corta_letras, filtro, filtro_grano,
                             parecido, repartir)

REEL = {"gancho": "A", "cuerpo": "1", "espejo": False}
# Las 5 copias de «Explota Instagram con IA» (11-nov-2026): C4, A2 (espejo), B3, C2 (espejo), A3
COPIAS = [{"gancho": "C", "cuerpo": "4", "espejo": False}, {"gancho": "A", "cuerpo": "2", "espejo": True},
          {"gancho": "B", "cuerpo": "3", "espejo": False}, {"gancho": "C", "cuerpo": "2", "espejo": True},
          {"gancho": "A", "cuerpo": "3", "espejo": False}]

r = repartir(COPIAS, REEL)
# Cada copia, un zoom y un desplazamiento que no lleva otra
assert sorted(z for z, _ in r) == sorted(ZOOMS) and sorted(m for _, m in r) == sorted(MUEVE), r
# La que más se parece al reel (su gancho A y sin espejo) es la que más zoom lleva
assert r[4][0] == max(ZOOMS), r
# Lo que salió ese día (lo que se vio en la maqueta y él aprobó)
assert r == [(1.075, -12), (1.06, -24), (1.03, 0), (1.045, 24), (1.09, 12)], r
# Rehecha una copia sola (--desde 4 --n 1), con las otras ya hechas: le toca lo mismo
assert repartir(COPIAS, REEL, {k: r[k] for k in range(4)})[4] == r[4]
# Un retrial (6.ª copia): las 5 de antes no se tocan y la nueva no repite el encuadre de ninguna
seis = repartir(COPIAS + [{"gancho": "C", "cuerpo": "3", "espejo": True}], REEL, {k: r[k] for k in range(5)})
assert seis[:5] == r and seis[5] not in r, seis
# Copias viejas sin zoom (1.0, 0): la nueva sí lleva
assert repartir(COPIAS[:1], REEL, {})[0][0] > 1.0
assert repartir(COPIAS, REEL, {k: (1.0, 0) for k in range(4)})[4][0] > 1.0
# El parecido: gancho 2, cuerpo 1, espejo 1
assert parecido(REEL, COPIAS[4]) == 3 and parecido(COPIAS[0], COPIAS[3]) == 2 and parecido(COPIAS[1], COPIAS[2]) == 0

# El filtro: medidas pares, la cara se queda donde estaba y la imagen se corre lo pedido
assert filtro(1.0, 0) == "" and filtro(1.0, 12) == ""
W, H, x, y, (ax, ay) = _ventana(1.09, 12, 1080, 1920, 1030)
assert W % 2 == 0 and H % 2 == 0 and 0 <= x <= W - 1080 and 0 <= y <= H - 1920
assert abs(ax - (540 - 12)) <= 1 and abs(ay - 1030) <= 1, (ax, ay)
assert filtro(1.09, 12, 1080, 1920, 1030) == f"scale={W}:{H}:flags=lanczos,crop=1080:1920:{x}:{y}"
# Sin margen para correrse (zoom pequeño), el recorte no se sale del vídeo
W, H, x, y, _ = _ventana(1.03, -24, 1080, 1920, None)
assert x == 0 and y >= 0
assert filtro_grano(0, 7) == "" and filtro_grano(2, 7) == "noise=alls=2:allf=t:all_seed=7"

# Las letras: un titular pegado arriba se cortaría con 9 % y no con 3 %; uno en el centro, nunca
arriba = (200, 70, 880, 130)
assert corta_letras(1.09, 0, 1080, 1920, arriba) and not corta_letras(1.03, 0, 1080, 1920, arriba)
assert not corta_letras(1.09, 24, 1080, 1920, (100, 600, 980, 700)) and not corta_letras(1.09, 24, 1080, 1920, None)

# Un píxel de letra: muy claro junto a uno muy oscuro
fila = bytes([10, 10, 250, 250, 10, 10, 10, 10])
assert _es_letra(bytes(8) + fila + bytes(8), 8 + 2, 8)
assert not _es_letra(bytes([128] * 24), 10, 8)
# La nitidez: un tablero de ajedrez da mucha; un gris liso, nada
w = h = 20
tablero = bytes(255 if (i % w + i // w) % 2 else 0 for i in range(w * h))
assert _laplaciano(tablero, w, h, 10, 10, 8) > 1000 and _laplaciano(bytes([90] * (w * h)), w, h, 10, 10, 8) == 0
print("encuadre_trials: 22 comprobaciones bien")
