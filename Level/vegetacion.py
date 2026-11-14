"""
Vegetación del mundo: arbustos con forma de nube (igual que los charcos, pero más pequeños).

Hay 3 tipos, pero TODOS se ven iguales (mezcla de los mismos 3 verdes) para que no se puedan identificar:
- Escondite: sirve para ocultarse.
- Venenoso: también oculta, pero hace 1 de daño cada 2 segundos.
- Frutal: oculta y tiene 1 a 5 orbes rojos de curación dentro. Al consumirlos todos,
  el arbusto desaparece y 1 minuto después aparece otro frutal en un lugar aleatorio del mapa.

Un personaje solo puede entrar si su diámetro cabe en el del arbusto; si no cabe, el arbusto es sólido.
Estando dentro no se le ve desde afuera (`personaje.oculto`) y él ve el mapa más oscuro.
"""
import math
import random
import pygame

# -----------------------------
# CONFIGURACIÓN
# -----------------------------
TIPO_ESCONDITE = "Escondite"
TIPO_VENENOSO = "Venenoso"
TIPO_FRUTAL = "Frutal"

CANTIDADES = {
    TIPO_ESCONDITE: (10, 30),
    TIPO_VENENOSO: (5, 10),
    TIPO_FRUTAL: (1, 5),
}

DIAMETRO_MIN = 30
DIAMETRO_MAX = 100
DIAMETRO_MIN_FRUTAL = 50       # Los frutales siempre deben poder usarse (personaje tamaño 1 = 40 de diámetro)

DANO_VENENO = 1
INTERVALO_VENENO = 2.0         # Segundos entre cada punto de daño

ORBES_MIN = 1
ORBES_MAX = 5
CURACION_ORBE = 2              # Vida que recupera cada orbe (sin pasar de la vida máxima)
RADIO_ORBE = 4
TIEMPO_REAPARICION_FRUTAL = 60.0

ALPHA_INTERIOR = 110           # Transparencia del arbusto en el que estás metido (para verte a ti mismo)
OSCURECIMIENTO = 95            # 0-255: cuánto se oscurece el mapa estando dentro de un arbusto

# Mismos 3 verdes para todos los tipos (no se distinguen a simple vista)
VERDES = [(44, 104, 50), (72, 142, 58), (112, 170, 74)]
VERDE_BORDE = (24, 58, 30)
COLOR_ORBE = (220, 36, 48)
COLOR_ORBE_BRILLO = (255, 150, 150)

# Colores solo para depuración [H] (ahí sí se revela el tipo)
COLOR_DEBUG = {
    TIPO_ESCONDITE: (120, 255, 120),
    TIPO_VENENOSO: (200, 80, 255),
    TIPO_FRUTAL: (255, 90, 90),
}


def circulos_nube(x, y, radio):
    """Devuelve los círculos (centro, radio) que forman una nube: núcleo + lóbulos alrededor."""
    circulos = [(pygame.Vector2(x, y), radio * 0.62)]
    lobulos = random.randint(5, 8)
    for i in range(lobulos):
        ang = (i / lobulos) * math.tau + random.uniform(-0.3, 0.3)
        r_lobulo = radio * random.uniform(0.32, 0.45)
        dist = (radio - r_lobulo) * random.uniform(0.85, 1.0)
        circulos.append((pygame.Vector2(x + math.cos(ang) * dist, y + math.sin(ang) * dist), r_lobulo))
    return circulos


# -----------------------------
# ARBUSTO
# -----------------------------
class Arbusto:
    def __init__(self, x, y, radio, tipo):
        self.centro = pygame.Vector2(x, y)
        self.radio = radio
        self.tipo = tipo
        self.circulos = circulos_nube(x, y, radio)
        self.orbes = []

        # Pre-renderizado: borde oscuro + lóbulos con los 3 verdes + manchas de hojas
        extension = radio + 4
        lado = int(extension * 2)
        origen = pygame.Vector2(x - extension, y - extension)
        self.rect = pygame.Rect(round(origen.x), round(origen.y), lado, lado)

        self.superficie = pygame.Surface((lado, lado), pygame.SRCALPHA)
        locales = [(c - origen, r) for c, r in self.circulos]
        for c, r in locales:
            pygame.draw.circle(self.superficie, VERDE_BORDE, (round(c.x), round(c.y)), round(r + 2))
        for c, r in locales:
            pygame.draw.circle(self.superficie, random.choice(VERDES), (round(c.x), round(c.y)), round(r))
        for c, r in locales:
            for _ in range(2):
                ang = random.uniform(0, math.tau)
                d = random.uniform(0, r * 0.5)
                hoja = (round(c.x + math.cos(ang) * d), round(c.y + math.sin(ang) * d))
                pygame.draw.circle(self.superficie, random.choice(VERDES), hoja, max(2, round(r * 0.3)))

        # Versión semitransparente (la que se ve cuando estás metido dentro)
        self.superficie_interior = self.superficie.copy()
        self.superficie_interior.fill((255, 255, 255, ALPHA_INTERIOR), special_flags=pygame.BLEND_RGBA_MULT)

        if tipo == TIPO_FRUTAL:
            self._generar_orbes()

    def _generar_orbes(self):
        for _ in range(random.randint(ORBES_MIN, ORBES_MAX)):
            c, r = random.choice(self.circulos)
            ang = random.uniform(0, math.tau)
            d = random.uniform(0, max(0.0, r - RADIO_ORBE - 2))
            self.orbes.append(pygame.Vector2(c.x + math.cos(ang) * d, c.y + math.sin(ang) * d))

    def contiene(self, punto):
        """True si el punto (centro del personaje) está dentro de la forma del arbusto."""
        return any((punto - c).length() <= r for c, r in self.circulos)

    def puede_entrar(self, personaje):
        """Solo entran los personajes cuyo diámetro cabe en el del arbusto."""
        return personaje.radio <= self.radio

    def dibujar(self, pantalla, desplazamiento, interior=False):
        sup = self.superficie_interior if interior else self.superficie
        pantalla.blit(sup, (self.rect.x - desplazamiento[0], self.rect.y - desplazamiento[1]))

    def dibujar_orbes(self, pantalla, desplazamiento):
        ox, oy = desplazamiento
        for o in self.orbes:
            p = (round(o.x - ox), round(o.y - oy))
            pygame.draw.circle(pantalla, COLOR_ORBE, p, RADIO_ORBE)
            pygame.draw.circle(pantalla, COLOR_ORBE_BRILLO, (p[0] - 1, p[1] - 1), max(1, RADIO_ORBE // 2))


# -----------------------------
# SISTEMA DE VEGETACIÓN
# -----------------------------
class SistemaVegetacion:
    def __init__(self, centro_mundo, radio_mundo, zona_segura, zonas_ocupadas=()):
        self.centro_mundo = pygame.Vector2(centro_mundo)
        self.radio_mundo = radio_mundo
        self.zona_segura = zona_segura
        self.zonas_ocupadas = [z.rect for z in zonas_ocupadas]  # charcos, rocas...
        self.arbustos = []
        self.reapariciones_frutal = []  # temporizadores (segundos restantes)

        for tipo, (minimo, maximo) in CANTIDADES.items():
            for _ in range(random.randint(minimo, maximo)):
                arbusto = self._crear_en_lugar_libre(tipo)
                if arbusto:
                    self.arbustos.append(arbusto)

    def registrar_obstaculos(self, objetos):
        """Añade obstáculos (ej. rocas generadas después) para que los frutales nuevos no caigan encima."""
        self.zonas_ocupadas.extend(o.rect for o in objetos)

    def _crear_en_lugar_libre(self, tipo, evitar=None, intentos=500):
        minimo = DIAMETRO_MIN_FRUTAL if tipo == TIPO_FRUTAL else DIAMETRO_MIN
        for _ in range(intentos):
            radio = random.randint(minimo, DIAMETRO_MAX) // 2
            ang = random.uniform(0, math.tau)
            dist = math.sqrt(random.random()) * (self.radio_mundo - radio - 20)
            if dist - radio < self.zona_segura:
                continue
            x = self.centro_mundo.x + math.cos(ang) * dist
            y = self.centro_mundo.y + math.sin(ang) * dist

            # No aparecer encima del jugador (reapariciones)
            if evitar is not None and (pygame.Vector2(x, y) - evitar).length() < 300:
                continue

            caja = pygame.Rect(0, 0, radio * 2 + 30, radio * 2 + 30)
            caja.center = (round(x), round(y))
            if any(caja.colliderect(z) for z in self.zonas_ocupadas):
                continue
            if any(caja.colliderect(a.rect) for a in self.arbustos):
                continue
            return Arbusto(x, y, radio, tipo)
        return None

    def obstaculos_para(self, personaje):
        """Arbustos demasiado pequeños para el personaje: se comportan como sólidos."""
        return [(a.centro, a.radio) for a in self.arbustos if not a.puede_entrar(personaje)]

    def actualizar(self, dt, jugador):
        # ¿En qué arbusto está metido?
        jugador.arbusto_actual = None
        for a in self.arbustos:
            if a.puede_entrar(jugador) and a.contiene(jugador.posicion):
                jugador.arbusto_actual = a
                break
        jugador.oculto = jugador.arbusto_actual is not None
        arbusto = jugador.arbusto_actual

        # Hierba venenosa: 1 de daño cada 2 segundos
        if arbusto and arbusto.tipo == TIPO_VENENOSO:
            jugador.tiempo_veneno += dt
            while jugador.tiempo_veneno >= INTERVALO_VENENO:
                jugador.tiempo_veneno -= INTERVALO_VENENO
                jugador.vida = max(0, jugador.vida - DANO_VENENO)
        else:
            jugador.tiempo_veneno = 0.0

        # Arbusto frutal: consumir orbes al tocarlos
        if arbusto and arbusto.tipo == TIPO_FRUTAL:
            restantes = []
            for o in arbusto.orbes:
                if (o - jugador.posicion).length() <= jugador.radio + RADIO_ORBE:
                    jugador.vida = min(jugador.vida_max, jugador.vida + CURACION_ORBE)
                else:
                    restantes.append(o)
            arbusto.orbes = restantes

            # Sin orbes: el arbusto desaparece y se programa uno nuevo en 1 minuto
            if not arbusto.orbes:
                self.arbustos.remove(arbusto)
                self.reapariciones_frutal.append(TIEMPO_REAPARICION_FRUTAL)
                jugador.arbusto_actual = None
                jugador.oculto = False

        # Reaparición de frutales
        pendientes = []
        for t in self.reapariciones_frutal:
            t -= dt
            if t <= 0:
                nuevo = self._crear_en_lugar_libre(TIPO_FRUTAL, evitar=jugador.posicion)
                if nuevo:
                    self.arbustos.append(nuevo)
                else:
                    pendientes.append(1.0)  # Reintentar en 1 segundo si no hubo espacio
            else:
                pendientes.append(t)
        self.reapariciones_frutal = pendientes

    def dibujar(self, pantalla, vista, desplazamiento, jugador):
        for a in self.arbustos:
            if a.rect.colliderect(vista):
                a.dibujar(pantalla, desplazamiento, interior=(a is jugador.arbusto_actual))

    def dibujar_interior(self, pantalla, desplazamiento, jugador):
        """Lo que solo ve el personaje desde dentro: los orbes de su arbusto."""
        if jugador.arbusto_actual:
            jugador.arbusto_actual.dibujar_orbes(pantalla, desplazamiento)

    def dibujar_hitboxes(self, pantalla, vista, desplazamiento, fuente):
        ox, oy = desplazamiento
        for a in self.arbustos:
            if not a.rect.colliderect(vista):
                continue
            color = COLOR_DEBUG[a.tipo]
            for c, r in a.circulos:
                pygame.draw.circle(pantalla, color, (round(c.x - ox), round(c.y - oy)), round(r), 1)
            etiqueta = fuente.render(f"{a.tipo} Ø{a.radio * 2}", True, color)
            pantalla.blit(etiqueta, (round(a.centro.x - ox - etiqueta.get_width() / 2), round(a.centro.y - oy - a.radio - 14)))
            for o in a.orbes:
                pygame.draw.circle(pantalla, COLOR_ORBE, (round(o.x - ox), round(o.y - oy)), RADIO_ORBE, 1)
