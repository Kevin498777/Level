import pygame
import math
from herramientas import EspadaLigera

# -----------------------------
# CLASE PERSONAJE
# -----------------------------
class Personaje:
    def __init__(self, nombre, x, y, tamano, velocidad, vida, fuerza, energia, defensa, color, habilidades=None, herramienta=None):
        self.nombre = nombre
        self.posicion = pygame.Vector2(x, y)
        self.destino = pygame.Vector2(x, y)

        # Ángulo de orientación en grados (0° = Arriba, 180° = Abajo)
        self.angulo = 0.0

        # Estadísticas principales
        self.tamano = tamano                       # Empieza estático en 1
        self.velocidad_base = float(velocidad)     # Velocidad base fija (1 a 4)
        self.velocidad = float(velocidad)          # Velocidad actual (afectada por buffs/debuffs)
        self.vida = vida                           # Vida (15 a 25)
        self.fuerza_base = float(fuerza)           # Fuerza base fija (1 a 5)
        self.fuerza = float(fuerza)                # Fuerza actual
        self.energia_max = energia                 # Energía máxima inicial (1 a 100)
        self.energia = energia                     # Energía actual
        self.defensa = defensa                     # Defensa (0 a 10)
        self.color = color
        self.habilidades = habilidades if habilidades is not None else []
        self.herramienta = herramienta if herramienta is not None else EspadaLigera()

        # Proyectiles activos disparados por el personaje (Disparo Veloz)
        self.proyectiles = []

        # Temporizador para la regeneración global de energía
        self.tiempo_regen = 0.0

        # Terreno: True si el personaje está pisando un charco de agua (-50% vel)
        self.en_agua = False
        self.debuff_agua = 0.50

        # Radio visual base escalado por el tamaño
        self.radio = int(20 * self.tamano)

        # Hitbox del personaje (coincide exactamente con el contorno físico exterior)
        self.hitbox = pygame.Rect(
            round(x - self.radio),
            round(y - self.radio),
            self.radio * 2,
            self.radio * 2
        )

    def esta_en_movimiento(self):
        """Devuelve True si el personaje se está desplazando hacia su destino."""
        return (self.destino - self.posicion).length() > 2.0

    def calcular_dano_total(self):
        """Calcula el daño total actual considerando fuerza y herramienta equipada."""
        if self.herramienta and self.herramienta.activa:
            return self.herramienta.calcular_dano(self)
        return round(self.fuerza, 2)

    def actualizar_regeneracion(self, dt):
        """
        Regeneración global de energía:
        - Parado: +1 de energía cada 3.0 segundos.
        - En movimiento: +1 de energía cada 6.0 segundos.
        """
        if self.energia < self.energia_max:
            intervalo = 6.0 if self.esta_en_movimiento() else 3.0
            self.tiempo_regen += dt
            if self.tiempo_regen >= intervalo:
                self.energia = min(self.energia_max, self.energia + 1)
                self.tiempo_regen -= intervalo
        else:
            self.tiempo_regen = 0.0

    def actualizar_velocidad(self):
        """
        Calcula la velocidad neta acumulando modificadores:
        - Destello activo: +50% (+0.50)
        - Destello cooldown (fatiga): -20% (-0.20)
        - Espada sacada: -20% (-0.20) acumulable (ej. cooldown -20% + espada -20% = -40% total)
        """
        modificador = 0.0

        # Modificadores de habilidades
        for hab in self.habilidades:
            if hab.nombre == "Destello":
                if hab.estado == "ACTIVA":
                    modificador += hab.porcentaje_buff
                elif hab.estado == "COOLDOWN":
                    modificador -= hab.porcentaje_debuff

        # Modificador acumulable de herramienta activa
        if self.herramienta and self.herramienta.activa:
            modificador -= self.herramienta.debuff_velocidad

        # Charco de agua: -50% acumulable
        if self.en_agua:
            modificador -= self.debuff_agua

        # Velocidad final con umbral mínimo seguro
        self.velocidad = max(0.4, round(self.velocidad_base * (1.0 + modificador), 2))

    def mover(self, limites_mundo, centro_mundo=None, radio_mundo=None, obstaculos=None):
        """
        Mueve al personaje hacia el destino, rota su orientación y actualiza su hitbox.
        - limites_mundo: rectángulo (min_x, min_y, max_x, max_y) de seguridad.
        - centro_mundo / radio_mundo: límite circular del mapa (opcional).
        - obstaculos: lista de rocas (pygame.Rect en .rect) que no se pueden atravesar.
        """
        min_x, min_y, max_x, max_y = limites_mundo
        posicion_previa = self.posicion.copy()

        direccion = self.destino - self.posicion
        distancia = direccion.length()

        if distancia > self.velocidad:
            paso = direccion.normalize() * self.velocidad
            self.posicion += paso

            # Actualizar ángulo de rotación:
            # 0° = Hacia arriba (0, -1), 180° = Hacia abajo (0, 1), 90° = Derecha (1, 0)
            dx = direccion.x
            dy = direccion.y
            self.angulo = math.degrees(math.atan2(dx, -dy)) % 360.0
        else:
            if distancia > 0.1:
                dx = direccion.x
                dy = direccion.y
                self.angulo = math.degrees(math.atan2(dx, -dy)) % 360.0
            self.posicion = self.destino.copy()

        # Restringir posición dentro del mundo jugable
        self.posicion.x = max(min_x + self.radio, min(self.posicion.x, max_x - self.radio))
        self.posicion.y = max(min_y + self.radio, min(self.posicion.y, max_y - self.radio))

        # Colisión con rocas (círculo vs rectángulo): empujar al personaje fuera de la roca
        if obstaculos:
            for obs in obstaculos:
                self._resolver_colision_rect(obs.rect)

        # Límite circular del mapa: no puede salir del círculo
        if centro_mundo is not None and radio_mundo is not None:
            desde_centro = self.posicion - centro_mundo
            limite = radio_mundo - self.radio
            if desde_centro.length() > limite:
                self.posicion = centro_mundo + desde_centro.normalize() * limite

        # Si quedó bloqueado (destino dentro de una roca o fuera del círculo), detenerse
        if self.esta_en_movimiento() and (self.posicion - posicion_previa).length() < 0.05:
            self.destino = self.posicion.copy()

        # Actualizar hitbox rectangular
        self.hitbox.x = round(self.posicion.x - self.radio)
        self.hitbox.y = round(self.posicion.y - self.radio)

    def _resolver_colision_rect(self, rect):
        """Separa el círculo del personaje de un rectángulo sólido si se están solapando."""
        # Punto del rectángulo más cercano al centro del personaje
        cerca_x = max(rect.left, min(self.posicion.x, rect.right))
        cerca_y = max(rect.top, min(self.posicion.y, rect.bottom))
        separacion = pygame.Vector2(self.posicion.x - cerca_x, self.posicion.y - cerca_y)
        dist = separacion.length()

        if dist >= self.radio:
            return  # Sin colisión

        if dist > 0.0001:
            # Empujar en la dirección de la separación
            self.posicion += separacion.normalize() * (self.radio - dist)
        else:
            # El centro quedó dentro del rectángulo: sacar por el lado más cercano
            empujes = [
                (self.posicion.x - rect.left + self.radio, pygame.Vector2(-1, 0)),
                (rect.right - self.posicion.x + self.radio, pygame.Vector2(1, 0)),
                (self.posicion.y - rect.top + self.radio, pygame.Vector2(0, -1)),
                (rect.bottom - self.posicion.y + self.radio, pygame.Vector2(0, 1)),
            ]
            cantidad, normal = min(empujes, key=lambda e: e[0])
            self.posicion += normal * cantidad

    def actualizar_proyectiles(self, dt, limites_mundo):
        """Actualiza la posición y ciclo de vida de los proyectiles."""
        for p in self.proyectiles:
            p.actualizar(dt, limites_mundo)
        # Filtrar proyectiles inactivos (que salieron del mundo)
        self.proyectiles = [p for p in self.proyectiles if p.activo]

    def dibujar(self, pantalla, fuente_nombre, desplazamiento=(0, 0)):
        """Dibuja al personaje. `desplazamiento` es el offset de la cámara (mundo -> pantalla)."""
        ox, oy = desplazamiento
        pos_x = round(self.posicion.x - ox)
        pos_y = round(self.posicion.y - oy)

        # Destino visual suave cuando se mueve
        if self.esta_en_movimiento():
            pygame.draw.circle(pantalla, (70, 85, 110), (round(self.destino.x - ox), round(self.destino.y - oy)), 5, 1)

        # Círculo base del personaje
        pygame.draw.circle(pantalla, self.color, (pos_x, pos_y), self.radio)

        # Círculos de habilidad cambiados al INTERIOR del círculo (para no alterar la percepción del hitbox)
        destello_activo = any(h.nombre == "Destello" and h.estado == "ACTIVA" for h in self.habilidades)
        burst_activo = any(h.nombre == "Burst de Fuerza" and h.estado == "ACTIVA" for h in self.habilidades)
        destello_cd = any(h.nombre == "Destello" and h.estado == "COOLDOWN" for h in self.habilidades)

        if destello_activo and burst_activo:
            # Combo interior: anillo magenta y núcleo cian
            pygame.draw.circle(pantalla, (230, 80, 255), (pos_x, pos_y), max(4, self.radio - 4), 2)
            pygame.draw.circle(pantalla, (0, 220, 255), (pos_x, pos_y), max(2, self.radio - 8), 2)
        elif destello_activo:
            # Anillo cian interior
            pygame.draw.circle(pantalla, (0, 220, 255), (pos_x, pos_y), max(4, self.radio - 4), 2)
        elif burst_activo:
            # Anillo naranja rojizo interior
            pygame.draw.circle(pantalla, (255, 90, 60), (pos_x, pos_y), max(4, self.radio - 4), 2)
        elif destello_cd:
            # Anillo ámbar interior de fatiga
            pygame.draw.circle(pantalla, (240, 140, 40), (pos_x, pos_y), max(4, self.radio - 5), 1)

        # Borde exterior blanco exacto (delimitador físico del radio / hitbox)
        pygame.draw.circle(pantalla, (255, 255, 255), (pos_x, pos_y), self.radio, 2)

        # Indicador frontal sutil (visor que rota indicando hacia dónde mira el círculo)
        rad = math.radians(self.angulo)
        frente_x = math.sin(rad)
        frente_y = -math.cos(rad)

        indicador_x = pos_x + (frente_x * (self.radio - 5))
        indicador_y = pos_y + (frente_y * (self.radio - 5))
        pygame.draw.circle(pantalla, (255, 255, 255), (round(indicador_x), round(indicador_y)), 3)

        # Dibujar herramienta rotada sincronizada con el personaje
        if self.herramienta:
            self.herramienta.dibujar(pantalla, self, desplazamiento)

        # Dibujar proyectiles activos
        for p in self.proyectiles:
            p.dibujar(pantalla, desplazamiento)

        # Etiqueta con el nombre flotando sobre el personaje
        texto_nombre = fuente_nombre.render(self.nombre, True, (255, 255, 255))
        rect_texto = texto_nombre.get_rect(center=(pos_x, pos_y - self.radio - 14))

        fondo_tag = pygame.Surface((rect_texto.width + 10, rect_texto.height + 4), pygame.SRCALPHA)
        pygame.draw.rect(fondo_tag, (18, 22, 28, 210), fondo_tag.get_rect(), border_radius=4)
        pantalla.blit(fondo_tag, (rect_texto.x - 5, rect_texto.y - 2))
        pantalla.blit(texto_nombre, rect_texto)
