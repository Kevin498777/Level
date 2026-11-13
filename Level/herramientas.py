import pygame
import math

# -----------------------------
# CLASE BASE DE HERRAMIENTAS
# -----------------------------
class HerramientaBase:
    def __init__(self, nombre, tecla, tecla_str, debuff_velocidad=0.0):
        self.nombre = nombre
        self.tecla = tecla
        self.tecla_str = tecla_str
        self.activa = False
        self.cooldown_toggle = 0.5  # 0.5s de tiempo entre sacar y guardar
        self.tiempo_transcurrido_toggle = 0.5
        self.debuff_velocidad = debuff_velocidad
        self.hitbox = None  # Hitbox de colisión (pygame.Rect)

    def toggle(self):
        """Alterna entre sacar y guardar la herramienta si ha pasado el cooldown de 0.5s."""
        if self.tiempo_transcurrido_toggle >= self.cooldown_toggle:
            self.activa = not self.activa
            self.tiempo_transcurrido_toggle = 0.0
            if not self.activa:
                self.hitbox = None
            return True
        return False

    def actualizar(self, dt, jugador=None):
        """Actualiza el temporizador de cooldown y la hitbox."""
        if self.tiempo_transcurrido_toggle < self.cooldown_toggle:
            self.tiempo_transcurrido_toggle += dt

        if jugador and self.activa:
            self.actualizar_hitbox(jugador)
        else:
            self.hitbox = None

    def actualizar_hitbox(self, jugador):
        pass

    def calcular_dano(self, jugador):
        return 0.0

    def dibujar(self, pantalla, jugador):
        pass


# -----------------------------
# HERRAMIENTA: ESPADA LIGERA
# -----------------------------
class EspadaLigera(HerramientaBase):
    def __init__(self):
        super().__init__(
            nombre="Espada Ligera",
            tecla=pygame.K_1,
            tecla_str="1",
            debuff_velocidad=0.20  # -20% de velocidad acumulable
        )
        self.multiplicador_dano = 2.0  # Daño = Fuerza x 2
        self.color_hoja = (175, 182, 195)       # Gris acero
        self.color_empunadura = (95, 102, 115)  # Gris oscuro
        self.color_filo = (225, 230, 242)       # Brillo metálico
        self.inclinacion = 15.0                 # Grados: la punta se abre hacia afuera como si la sujetara

    def calcular_dano(self, jugador):
        """Daño proporcional a la fuerza actual del personaje multiplicado por 2."""
        return round(jugador.fuerza * self.multiplicador_dano, 2)

    def obtener_segmento(self, jugador):
        """Calcula los puntos extremos (pomo y punta) de la espada rotada."""
        pos_x = jugador.posicion.x
        pos_y = jugador.posicion.y
        radio = jugador.radio
        rad = math.radians(jugador.angulo)

        frente_x = math.sin(rad)
        frente_y = -math.cos(rad)
        derecha_x = math.cos(rad)
        derecha_y = math.sin(rad)

        distancia_flanco = radio + 6.0
        centro_esp_x = pos_x + (derecha_x * distancia_flanco)
        centro_esp_y = pos_y + (derecha_y * distancia_flanco)

        # Inclinar la hoja: rotar los ejes de la espada hacia afuera (punta hacia el flanco derecho)
        inc = math.radians(self.inclinacion)
        cos_i, sin_i = math.cos(inc), math.sin(inc)
        frente_x, frente_y, derecha_x, derecha_y = (
            frente_x * cos_i + derecha_x * sin_i,
            frente_y * cos_i + derecha_y * sin_i,
            derecha_x * cos_i - frente_x * sin_i,
            derecha_y * cos_i - frente_y * sin_i,
        )

        largo_hoja = max(24.0, radio * 1.35)
        mitad_largo = largo_hoja / 2.0

        punta_x = centro_esp_x + (frente_x * mitad_largo)
        punta_y = centro_esp_y + (frente_y * mitad_largo)

        pomo_x = centro_esp_x - (frente_x * mitad_largo)
        pomo_y = centro_esp_y - (frente_y * mitad_largo)

        return (pomo_x, pomo_y), (punta_x, punta_y), (frente_x, frente_y), (derecha_x, derecha_y), largo_hoja

    def actualizar_hitbox(self, jugador):
        """Calcula el área de colisión (hitbox rectangular) de la espada."""
        (pomo_x, pomo_y), (punta_x, punta_y), _, _, _ = self.obtener_segmento(jugador)
        min_x = min(pomo_x, punta_x) - 4
        min_y = min(pomo_y, punta_y) - 4
        max_x = max(pomo_x, punta_x) + 4
        max_y = max(pomo_y, punta_y) + 4
        self.hitbox = pygame.Rect(
            round(min_x),
            round(min_y),
            round(max_x - min_x),
            round(max_y - min_y)
        )

    def dibujar(self, pantalla, jugador, desplazamiento=(0, 0)):
        """
        Dibuja la espada ligera pegada al flanco derecho del círculo, inclinada 15° (  o/  ).
        Gira en sincronía con la dirección del personaje:
        - Si va hacia arriba (0°), la espada queda casi vertical con la punta abierta hacia afuera.
        - Si va hacia abajo (180°), la espada gira 180° quedando apuntando hacia abajo.
        `desplazamiento` es el offset de la cámara (mundo -> pantalla).
        """
        if not self.activa:
            return

        (pomo_x, pomo_y), (punta_x, punta_y), (frente_x, frente_y), (derecha_x, derecha_y), largo_hoja = self.obtener_segmento(jugador)
        pomo_x -= desplazamiento[0]
        pomo_y -= desplazamiento[1]
        punta_x -= desplazamiento[0]
        punta_y -= desplazamiento[1]

        # 1. Borde de la hoja
        pygame.draw.line(
            pantalla,
            (18, 22, 28),
            (round(pomo_x + derecha_x), round(pomo_y + derecha_y)),
            (round(punta_x + derecha_x), round(punta_y + derecha_y)),
            4
        )

        # 2. Hoja principal gris acero
        pygame.draw.line(
            pantalla,
            self.color_hoja,
            (round(pomo_x), round(pomo_y)),
            (round(punta_x), round(punta_y)),
            3
        )

        # 3. Filo con brillo metálico fino
        filo_inicio_x = pomo_x + (frente_x * 4.0)
        filo_inicio_y = pomo_y + (frente_y * 4.0)
        pygame.draw.line(
            pantalla,
            self.color_filo,
            (round(filo_inicio_x), round(filo_inicio_y)),
            (round(punta_x), round(punta_y)),
            1
        )

        # 4. Empuñadura / Guarda
        guarda_centro_x = pomo_x + (frente_x * (largo_hoja * 0.25))
        guarda_centro_y = pomo_y + (frente_y * (largo_hoja * 0.25))
        ancho_guarda = 3.5

        g_izq_x = guarda_centro_x - (derecha_x * ancho_guarda)
        g_izq_y = guarda_centro_y - (derecha_y * ancho_guarda)
        g_der_x = guarda_centro_x + (derecha_x * ancho_guarda)
        g_der_y = guarda_centro_y + (derecha_y * ancho_guarda)

        pygame.draw.line(
            pantalla,
            self.color_empunadura,
            (round(g_izq_x), round(g_izq_y)),
            (round(g_der_x), round(g_der_y)),
            2
        )
