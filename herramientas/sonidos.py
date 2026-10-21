"""Los efectos de sonido: uno por idea, en su remate, nunca al entrar el bloque ni al cambiar el titular.

Así lo hacen los reels editados que funcionan (medido en uno de 49 s: 21 de sus 35 cambios en pantalla van en
silencio y unos 20 efectos caen cada uno en el momento en que la idea aterriza): la campana en el resultado, un
golpe grave al abrir un paso o al llegar un mensaje, un ding cuando aparece un nombre o aterriza una cifra, y el
silbido solo en los dos o tres giros grandes del vídeo.

Se fabrican aquí con numpy, sin ficheros de nadie, y se mezclan en una sola pista (`sonidos.wav`). Qué suena y
cuándo sale de leer el guion con las mismas reglas de tiempo que kit/motor.js.
"""
import re
import wave
from html.parser import HTMLParser

import numpy as np

SR = 48000


def _t(dur):
    return np.arange(int(dur * SR)) / SR


def barrido(f0, f1, dur, caida, ataque=0.004):
    """Un tono que sube o baja y se apaga."""
    t = _t(dur)
    return np.sin(2 * np.pi * (f0 * t + (f1 - f0) * t * t / (2 * dur))) * np.minimum(1, t / ataque) * np.exp(-caida * t)


def soplo(dur, centro, semilla=7):
    """Ruido filtrado que crece y se va: el «fsss» de un cambio de bloque."""
    n = int(dur * SR)
    espectro = np.fft.rfft(np.random.default_rng(semilla).standard_normal(n))
    f = np.maximum(np.fft.rfftfreq(n, 1 / SR), 1)
    y = np.fft.irfft(espectro * np.exp(-0.5 * (np.log2(f / centro) / 0.7) ** 2), n)
    return y / np.abs(y).max() * np.sin(np.pi * np.arange(n) / n) ** 2


def nota(hz, dur=0.5, caida=9):
    """Una nota corta de madera."""
    t = _t(dur)
    return (0.5 * np.sin(2 * np.pi * hz * t) * np.exp(-caida * t)
            + 0.1 * np.sin(2 * np.pi * hz * 3 * t) * np.exp(-caida * 2.6 * t)) * np.minimum(1, t * 300)


def sobre(base, otro, en):
    """Suma `otro` dentro de `base` a partir del segundo `en`."""
    i = int(en * SR)
    salida = np.zeros(max(len(base), i + len(otro)))
    salida[:len(base)] += base
    salida[i:i + len(otro)] += otro
    return salida


def silbido(dur, f0, f1, semilla=3, ancho=0.55):
    """Ruido cuya banda sube de f0 a f1 y se apaga: el «fiuuu» brillante de un giro grande
    (ruido de 3 a 12 kHz durante 0,5 a 0,8 s: los apagados, de menos de 2 kHz, suenan a pitido)."""
    n = int(dur * SR)
    espectro = np.fft.rfft(np.random.default_rng(semilla).standard_normal(n))
    f = np.maximum(np.fft.rfftfreq(n, 1 / SR), 1)
    t = np.arange(n) / n
    salida, tramos = np.zeros(n), 10
    for k in range(tramos):                      # la banda se mueve a saltos que se funden entre sí
        centro = f0 * (f1 / f0) ** (k / (tramos - 1))
        y = np.fft.irfft(espectro * np.exp(-0.5 * (np.log2(f / centro) / ancho) ** 2), n)
        salida += y * np.maximum(0, 1 - np.abs(t * (tramos - 1) - k))
    sobre_ = t ** 0.7 * (1 - t) ** 1.8
    return salida / np.abs(salida).max() * sobre_ / sobre_.max()


def clic(centro=5000, semilla=11):
    """Un clic seco y brillante."""
    return soplo(0.008, centro, semilla) * np.exp(-np.arange(int(0.008 * SR)) / SR * 500)


def campana(parciales, dur=0.55):
    """Campanita con armónicos (2,5 / 3,7 / 4,2 / 5,2 kHz que se apagan en medio segundo): el resultado."""
    t = _t(dur)
    onda = sum(a * np.sin(2 * np.pi * hz * t) * np.exp(-c * t) for hz, a, c in parciales)
    return onda * np.minimum(1, t / 0.002)


def _cuenta():
    pista = np.zeros(1)
    for k in range(12):                          # clics cada vez más separados: el número frena
        pista = sobre(pista, clic(4200 + 150 * k, semilla=k) * (1 - k * 0.04), 0.03 * k + 0.002 * k * k)
    return pista


def golpe(dur=0.4):
    """Un golpe grave, de 110 a 45 Hz, con un clic encima para que se note en el móvil: el «boom» de abrir un paso
    o de que llegue un mensaje."""
    t = _t(dur)
    f = 45 + 65 * np.exp(-t * 18)
    cuerpo = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9) * np.minimum(1, t / 0.003)
    return sobre(cuerpo, clic(2500) * 0.35, 0)


CAMPANA = [(2500, 1.0, 7), (3700, 0.6, 9), (4200, 0.5, 11), (5200, 0.35, 14)]
DING = [(1320, 1.0, 14), (2640, 0.35, 20), (1980, 0.25, 18)]   # más corto y más grave que la campana

# nombre → (onda, fuerza). Con sonido=0.14 quedan, contra la voz y en ventanas de 0,3 s: campana −9 dB, golpe −11,5,
# ding −13, hecho −14, silbido −15: lo medido en el reel de referencia.
SONIDOS = {
    "entra": (silbido(0.55, 1800, 8500), 0.91),                                               # cambia el bloque
    "sube": (silbido(0.3, 1400, 6500, semilla=5), 0.7),                                      # entra un gráfico
    "pop": (sobre(campana(CAMPANA) * 0.8, clic(6000), 0), 2.18),                              # salta un logo
    "tic": (clic(4800), 0.55),                                                               # una fila, un chip
    "tecla": (clic(3600, semilla=9), 0.5),                                                   # se teclea una letra
    "hecho": (sobre(nota(1568), nota(2093), 0.08), 0.7),                                     # se marca, se sella
    "cuenta": (_cuenta(), 0.6),                                                              # un número cuenta
    "ding": (sobre(campana(DING, 0.3), clic(5000) * 0.5, 0), 1.37),                           # un nombre o una cifra aterriza
    "golpe": (golpe(), 0.98),                                                                 # abre un paso, llega un mensaje
    # data-son="mensaje" en una notificación: un «tin» de mensaje, fuerte, que al principio suena solo
    "mensaje": (sobre(campana([(2000, 1.0, 6), (6400, 0.35, 12), (12300, 0.12, 18)], 0.6), clic(7000), 0), 2.0),
}
VACIOS = {"br", "img", "hr", "input", "meta", "link", "source", "wbr"}
HUECO = 0.8   # dos remates más juntos que esto se pisan: se queda el que pesa más
SILBIDOS_CADA = 15   # s entre dos silbidos como poco
# Cuánto pesa cada sonido para ser EL de su idea: se queda el que más pesa y, si empatan, el último (el remate)
PESO = {"entra": 5, "pop": 4, "golpe": 3, "ding": 2, "hecho": 1, "tic": 0, "sube": 0, "tecla": 0, "cuenta": 0, "mensaje": 6}
PASO = re.compile(r"^\s*(?:paso\s*)?\d+\s*[.):]")   # «1. Te escribe el guion», «Paso 2», «03 Explica…»


class _Lector(HTMLParser):
    """Lee el guion y apunta los candidatos a sonar: (segundo, sonido, idea, forzado). Una idea es un bloque, o el
    trozo de bloque desde que cambia el titular. Mismas reglas de tiempo que kit/motor.js."""

    def __init__(self):
        super().__init__()
        self.pila, self.cand, self.bloque, self.relevos = [], [], 0, {}

    def _tiempo(self, valor, inicio):
        valor = valor.strip()
        return inicio + float(valor[1:]) if valor.startswith("+") else float(valor)

    def _suena(self, t, tipo, nodo, forzado=False):
        pedido = nodo["a"].get("data-son")
        if pedido == "no":
            return
        if pedido:
            tipo, forzado = pedido, True
        if tipo:
            self.cand.append((round(t, 3), tipo, self.bloque, forzado))

    def _abrir(self, etiqueta, attrs):
        a = {k: v or "" for k, v in attrs}
        clases = set(a.get("class", "").split())
        padre = self.pila[-1] if self.pila else None
        nodo = {"etiqueta": etiqueta, "a": a, "texto": "", "inicio": padre["inicio"] if padre else 0.0,
                "ref": padre["ref"] if padre else 0.0, "titular": "titular" in clases}
        if "data-a" in a:
            nodo["inicio"] = nodo["ref"] = float(a["data-a"])
            self.bloque += 1
            if "data-son" in a and a["data-son"] != "no":   # un bloque que abre con su sonido, porque lo pide
                self._suena(nodo["inicio"], None, nodo)
        if "data-en" in a:
            nodo["ref"] = self._tiempo(a["data-en"], nodo["inicio"])
        if nodo["titular"] and "relevo" in clases:   # cambia el titular: desde ahí, otra idea
            self.relevos.setdefault(self.bloque, []).append(nodo["ref"])
        como = a.get("data-como", "")
        tipo = None
        if nodo["titular"]:
            nodo["cuando"] = nodo["ref"]
        elif como in ("gira", "barre", "estira"):
            tipo = "entra"                               # los giros grandes, uno o dos por vídeo
        elif "sello" in clases:
            tipo = "pop"                                 # el resultado, lo que se sella
        elif como == "baja" or "noti" in clases or "aviso" in clases:
            tipo = "golpe"                               # llega algo: un mensaje, una notificación
        elif "icono" in clases or "captura" in clases or "palabra" in clases or como == "pop":
            tipo = "ding"                                # aparece un nombre, un logo, una palabra grande
        if tipo and ("data-en" in a or padre and "data-cascada" in padre["a"]):
            self._suena(nodo["ref"], tipo, nodo)
        elif "data-en" in a and a.get("data-son"):
            self._suena(nodo["ref"], None, nodo)
        if padre and "data-cascada" in padre["a"] and "data-son" in padre["a"]:
            t0, _, paso = padre["a"]["data-cascada"].partition(",")
            padre["hijos"] = padre.get("hijos", 0) + 1
            self._suena(self._tiempo(t0, padre["inicio"]) + (padre["hijos"] - 1) * float(paso or 0.1), None, padre)
        cuando = self._tiempo(a["data-t"], nodo["inicio"]) if "data-t" in a else nodo["ref"]
        for clave in ("data-cuenta", "data-rueda"):   # la cifra suena al aterrizar, no mientras gira
            if clave in a:
                self._suena(cuando + 0.05 + float(a.get("data-dur", "0.9" if clave == "data-cuenta" else "1.4")), "ding", nodo)
        if "data-clase" in a:
            self._suena(self._tiempo(a["data-clase"].split(":")[0], nodo["inicio"]), "hecho", nodo)
        if "data-clic" in a:
            self._suena(self._tiempo(a["data-clic"], nodo["inicio"]), "hecho", nodo)
        nodo["cuando"] = cuando
        return nodo

    def handle_starttag(self, etiqueta, attrs):
        nodo = self._abrir(etiqueta, attrs)
        if etiqueta not in VACIOS:
            self.pila.append(nodo)

    def handle_startendtag(self, etiqueta, attrs):
        self._abrir(etiqueta, attrs)

    def handle_data(self, texto):
        for nodo in self.pila:
            if nodo["titular"] or "data-escribe" in nodo["a"]:
                nodo["texto"] += texto

    def handle_endtag(self, etiqueta):
        while self.pila:
            nodo = self.pila.pop()
            if nodo["titular"] and PASO.match(nodo["texto"]):   # «1. …», «Paso 2»: el golpe de abrir un paso
                self._suena(nodo["ref"], "golpe", nodo)
            if "data-escribe" in nodo["a"] and nodo["a"].get("data-son") == "tecla":
                for i in range(len(nodo["texto"].strip())):
                    self.cand.append((round(nodo["cuando"] + i * 0.1, 3), "tecla", None, True))
            if nodo["etiqueta"] == etiqueta:
                break


def eventos(guion, todos=False):
    """[(segundo, sonido)]: en cada idea, un solo sonido, en su remate (lo que más pesa y, si empata, lo último),
    nunca al entrar el bloque ni al cambiar el titular. Lo forzado con data-son suena siempre."""
    lector = _Lector()
    lector.feed(re.sub(r"<!--.*?-->", "", guion, flags=re.S))
    if todos:
        return sorted({(t, tipo) for t, tipo, _, _ in lector.cand})
    # Silbidos, pocos: 2 o 3 por vídeo, en los giros grandes. Uno a menos de 15 s de otro pasa a ding
    candidatos, ultimo = [], -99.0
    for t, tipo, bloque, forzado in sorted(lector.cand, key=lambda c: c[0]):
        if tipo == "entra" and not forzado:
            if t - ultimo < 15:
                tipo = "ding"
            else:
                ultimo = t
        candidatos.append((t, tipo, bloque, forzado))
    mejor, a_mano, elegidos = {}, set(), []
    for t, tipo, bloque, forzado in candidatos:
        idea = (bloque, sum(r <= t + 0.05 for r in lector.relevos.get(bloque, [])))   # por tiempo, no por orden
        if forzado:
            elegidos.append((t, tipo, PESO.get(tipo, 3) + 10))
            a_mano.add(idea)   # lo pedido a mano manda en su idea
        elif idea not in mejor or (PESO[tipo], t) >= (PESO[mejor[idea][1]], mejor[idea][0]):
            mejor[idea] = (t, tipo)
    elegidos += [(t, tipo, PESO[tipo]) for idea, (t, tipo) in mejor.items() if idea not in a_mano]
    limpios = []
    for t, tipo, peso in sorted(elegidos):
        if limpios and t - limpios[-1][0] < (0.06 if tipo == "tecla" else HUECO):
            if peso > limpios[-1][2]:
                limpios[-1] = (t, tipo, peso)
            continue
        limpios.append((t, tipo, peso))
    return [(t, tipo) for t, tipo, _ in limpios]


def _tono(onda, semitonos):
    """La misma onda, más aguda o más grave."""
    paso = 2 ** (semitonos / 12)
    return np.interp(np.arange(0, len(onda) - 1, paso), np.arange(len(onda)), onda)


def mezclar(lista, dur, destino, volumen):
    """Todos los sonidos en una pista mono del largo del vídeo. Cada uso, entre un semitono más grave y uno más
    agudo: el mismo sonido repetido suena a copiar y pegar. Fijo por su orden: el mismo guion suena igual siempre."""
    pista = np.zeros(int((dur + 1) * SR))
    for n, (t, tipo) in enumerate(lista):
        onda, fuerza = SONIDOS[tipo]
        if tipo != "mensaje":
            onda = _tono(onda, ((n * 7) % 5 - 2) / 2)
        i = int(max(t, 0) * SR)
        trozo = onda[:len(pista) - i]
        pista[i:i + len(trozo)] += trozo / np.abs(onda).max() * fuerza * volumen
    pista = np.clip(pista[:int(dur * SR)], -1, 1)
    with wave.open(str(destino), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((pista * 32767).astype(np.int16).tobytes())
