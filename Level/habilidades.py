import pygame
import math

# -----------------------------
# CLASE PROYECTIL DE ENERGÍA (DISPARO VELOZ)
# -----------------------------
class ProyectilEnergia:
    def __init__(self, x, y, dx, dy, velocidad=10.0, dano=1.0, radio=6):
        self.posicion = pygame.Vector2(x, y)
        if dx != 0 or dy != 0:
            self.direccion = pygame.Vector2(dx, dy).normalize()
        else:
            self.direccion = pygame.Vector2(0, -1)

        self.velocidad = velocidad
        self.dano = dano
        self.radio = radio
        self.activo = True
        self.hitbox = pygame.Rect(
            round(x - radio),
            round(y - radio),
            radio * 2,
            radio * 2
        )

    def actualizar(self, dt, limites_mundo):
        """Mueve la esfera en línea recta a velocidad 10 y actualiza su hitbox."""
        min_x, min_y, max_x, max_y = limites_mundo

        # Desplazamiento recto
        self.posicion += self.direccion * self.velocidad

        # Actualizar hitbox
        self.hitbox.x = round(self.posicion.x - self.radio)
        self.hitbox.y = round(self.posicion.y - self.radio)

        # Desactivar si sale de los límites del mundo
        if (self.posicion.x < min_x - self.radio or self.posicion.x > max_x + self.radio or
            self.posicion.y < min_y - self.radio or self.posicion.y > max_y + self.radio):
            self.activo = False

    def dibujar(self, pantalla, desplazamiento=(0, 0)):
        """Dibuja la esfera de energía con núcleo y resplandor (con offset de cámara)."""
        px = round(self.posicion.x - desplazamiento[0])
        py = round(self.posicion.y - desplazamiento[1])

        # Resplandor exterior
        pygame.draw.circle(pantalla, (255, 235, 90), (px, py), self.radio + 2)
        # Núcleo blanco brillante
        pygame.draw.circle(pantalla, (255, 255, 255), (px, py), self.radio)
        # Centro energético dorado
        pygame.draw.circle(pantalla, (255, 175, 20), (px, py), max(2, self.radio - 2))


# -----------------------------
# CLASE BASE DE HABILIDADES
# -----------------------------
class HabilidadBase:
    def __init__(self, nombre, descripcion, costo_energia, duracion_activa, duracion_cooldown, tecla, tecla_str):
        self.nombre = nombre
        self.descripcion = descripcion
        self.costo_energia = costo_energia
        self.duracion_activa = duracion_activa
        self.duracion_cooldown = duracion_cooldown
        self.tecla = tecla
        self.tecla_str = tecla_str

        # Estados posibles: "LISTA", "ACTIVA", "COOLDOWN"
        self.estado = "LISTA"
        self.tiempo_restante_activo = 0.0
        self.tiempo_restante_cooldown = 0.0
        self.mensaje_alerta = ""
        self.tiempo_alerta = 0.0

    def asignar_tecla(self, tecla, tecla_str):
        """Asigna dinámicamente la tecla (2, 3 o 4) según la selección de habilidades."""
        self.tecla = tecla
        self.tecla_str = tecla_str

    def obtener_costo_base(self, jugador):
        return self.costo_energia

    def intentar_activar(self, jugador):
        """
        Intenta activar la habilidad.
        Si otra habilidad ya está en estado ACTIVA, se aplica un sobrecosto
        del 5% de la energía total actual del jugador (redondeada).
        """
        if self.estado != "LISTA":
            return False

        # Verificar si hay otra habilidad activa
        otra_activa = False
        if hasattr(jugador, "habilidades"):
            for h in jugador.habilidades:
                if h != self and h.estado == "ACTIVA":
                    otra_activa = True
                    break

        costo_base = self.obtener_costo_base(jugador)

        # Sobrecosto del 5% de la energía actual
        sobrecosto = 0
        if otra_activa:
            sobrecosto = int(round(jugador.energia * 0.05))
            if sobrecosto < 1 and jugador.energia > 0:
                sobrecosto = 1

        costo_total = costo_base + sobrecosto

        if jugador.energia < costo_total:
            self.mensaje_alerta = f"¡Falta energía! (Req. {costo_total})"
            self.tiempo_alerta = 2.5
            return False

        # Descontar energía
        jugador.energia -= costo_total

        # Ejecutar efecto específico
        self.ejecutar_activacion(jugador)

        if sobrecosto > 0:
            self.mensaje_alerta = f"¡Combo activo! (+{sobrecosto} En.)"
            self.tiempo_alerta = 2.0

        return True

    def ejecutar_activacion(self, jugador):
        """Por defecto activa la duración activa."""
        self.estado = "ACTIVA"
        self.tiempo_restante_activo = self.duracion_activa
        self.aplicar_efecto_activo(jugador)

    def aplicar_efecto_activo(self, jugador):
        pass

    def aplicar_efecto_cooldown(self, jugador):
        pass

    def restaurar_efecto(self, jugador):
        pass

    def actualizar(self, dt, jugador):
        """Actualiza temporizadores según delta time transcurrido (segundos)."""
        if self.tiempo_alerta > 0:
            self.tiempo_alerta -= dt
            if self.tiempo_alerta <= 0:
                self.mensaje_alerta = ""

        if self.estado == "ACTIVA":
            self.tiempo_restante_activo -= dt
            if self.tiempo_restante_activo <= 0:
                self.estado = "COOLDOWN"
                self.tiempo_restante_activo = 0.0
                self.tiempo_restante_cooldown = self.duracion_cooldown
                self.aplicar_efecto_cooldown(jugador)

        elif self.estado == "COOLDOWN":
            self.tiempo_restante_cooldown -= dt
            if self.tiempo_restante_cooldown <= 0:
                self.estado = "LISTA"
                self.tiempo_restante_cooldown = 0.0
                self.restaurar_efecto(jugador)


# -----------------------------
# HABILIDAD 1: DESTELLO
# -----------------------------
class Destello(HabilidadBase):
    def __init__(self):
        super().__init__(
            nombre="Destello",
            descripcion="Aumenta la velocidad un 50% (+0.5x) por 10s. Tras finalizar: 5s de enfriamiento con debuff (-20% velocidad).",
            costo_energia=10,
            duracion_activa=10.0,
            duracion_cooldown=5.0,
            tecla=pygame.K_2,
            tecla_str="2"
        )
        self.porcentaje_buff = 0.50
        self.porcentaje_debuff = 0.20

    def aplicar_efecto_activo(self, jugador):
        jugador.velocidad = jugador.velocidad_base * (1.0 + self.porcentaje_buff)

    def aplicar_efecto_cooldown(self, jugador):
        jugador.velocidad = max(0.5, jugador.velocidad_base * (1.0 - self.porcentaje_debuff))

    def restaurar_efecto(self, jugador):
        jugador.velocidad = jugador.velocidad_base


# -----------------------------
# HABILIDAD 2: BURST DE FUERZA
# -----------------------------
class BurstDeFuerza(HabilidadBase):
    def __init__(self):
        super().__init__(
            nombre="Burst de Fuerza",
            descripcion="Aumenta la fuerza base un 20% (+0.2x) durante 6s. Enfriamiento de 12s.",
            costo_energia=15,
            duracion_activa=6.0,
            duracion_cooldown=12.0,
            tecla=pygame.K_3,
            tecla_str="3"
        )
        self.porcentaje_buff = 0.20

    def aplicar_efecto_activo(self, jugador):
        jugador.fuerza = round(jugador.fuerza_base * (1.0 + self.porcentaje_buff), 2)

    def aplicar_efecto_cooldown(self, jugador):
        jugador.fuerza = jugador.fuerza_base

    def restaurar_efecto(self, jugador):
        jugador.fuerza = jugador.fuerza_base


# -----------------------------
# HABILIDAD 3: DISPARO VELOZ (NUEVA)
# -----------------------------
class DisparoVeloz(HabilidadBase):
    def __init__(self):
        super().__init__(
            nombre="Disparo Veloz",
            descripcion="Ataque a distancia: dispara una esfera de energía recta (vel 10) con 20% del daño total del personaje. Cuesta 15% de energía total. Cooldown de 2s.",
            costo_energia=15,  # Valor base referencial; se calcula con 15% de energía total
            duracion_activa=0.0,
            duracion_cooldown=2.0,
            tecla=pygame.K_4,
            tecla_str="4"
        )
        self.velocidad_proyectil = 10.0
        self.porcentaje_dano = 0.20  # 20% del daño total del personaje

    def obtener_costo_base(self, jugador):
        """Cuesta exactamente el 15% de la energía total del personaje (redondeada)."""
        return max(1, int(round(jugador.energia_max * 0.15)))

    def ejecutar_activacion(self, jugador):
        """Dispara una esfera recta en la dirección a la que apunta el personaje."""
        rad = math.radians(jugador.angulo)
        frente_x = math.sin(rad)
        frente_y = -math.cos(rad)

        # Origen justo en el borde frontal del personaje
        origen_x = jugador.posicion.x + (frente_x * (jugador.radio + 8))
        origen_y = jugador.posicion.y + (frente_y * (jugador.radio + 8))

        # Daño: 20% del daño total actual del personaje
        dano_total = jugador.calcular_dano_total() if hasattr(jugador, "calcular_dano_total") else (jugador.fuerza * 2.0)
        dano_proyectil = max(0.5, round(dano_total * self.porcentaje_dano, 2))

        proyectil = ProyectilEnergia(
            x=origen_x,
            y=origen_y,
            dx=frente_x,
            dy=frente_y,
            velocidad=self.velocidad_proyectil,
            dano=dano_proyectil,
            radio=6
        )

        if hasattr(jugador, "proyectiles"):
            jugador.proyectiles.append(proyectil)

        # Pasa inmediatamente a cooldown de 2 segundos
        self.estado = "COOLDOWN"
        self.tiempo_restante_activo = 0.0
        self.tiempo_restante_cooldown = self.duracion_cooldown


# -----------------------------
# DIBUJAR PANEL LATERAL DE HABILIDADES Y MANUAL
# -----------------------------
def dibujar_panel_habilidades(pantalla, x, y, ancho, alto, habilidades, jugador, fuentes):
    """
    Renderiza la interfaz lateral derecha para las habilidades equipadas (teclas 2, 3, 4),
    sus temporizadores dinámicos y el manual explicativo integrado.
    """
    fuente_titulo = fuentes["titulo"]
    fuente_sub = fuentes["sub"]
    fuente_contador = fuentes["contador"]
    fuente_mini = fuentes["mini"]

    panel = pygame.Surface((ancho, alto))
    panel.fill((20, 23, 30))
    pantalla.blit(panel, (x, y))

    pygame.draw.line(pantalla, (45, 52, 68), (x, y), (x, y + alto), 2)

    # Cabecera
    titulo = fuente_titulo.render("HABILIDADES", True, (255, 215, 0))
    pantalla.blit(titulo, (x + 15, y + 12))

    sub = fuente_sub.render(f"Equipadas ({len(habilidades)}/3)", True, (130, 140, 160))
    pantalla.blit(sub, (x + 15, y + 33))

    pygame.draw.line(pantalla, (45, 52, 68), (x + 15, y + 54), (x + ancho - 15, y + 54), 1)

    cur_y = y + 60

    # Altura ajustada dinámicamente si hay 3 habilidades
    tarjeta_h = 105 if len(habilidades) >= 3 else 125

    for hab in habilidades:
        tarjeta_w = ancho - 26
        tarjeta_x = x + 13

        if hab.estado == "ACTIVA":
            color_borde = (0, 220, 255) if hab.nombre == "Destello" else (255, 100, 70)
            color_fondo = (22, 38, 50) if hab.nombre == "Destello" else (48, 26, 26)
        elif hab.estado == "COOLDOWN":
            color_borde = (230, 140, 40)
            color_fondo = (40, 30, 24)
        else:
            color_borde = (55, 68, 90)
            color_fondo = (26, 30, 40)

        pygame.draw.rect(pantalla, color_fondo, (tarjeta_x, cur_y, tarjeta_w, tarjeta_h), border_radius=6)
        pygame.draw.rect(pantalla, color_borde, (tarjeta_x, cur_y, tarjeta_w, tarjeta_h), width=2, border_radius=6)

        # Nombre y Tecla asignada dinámicamente
        txt_nom = fuente_sub.render(hab.nombre, True, (255, 255, 255))
        pantalla.blit(txt_nom, (tarjeta_x + 10, cur_y + 6))

        txt_tecla = fuente_mini.render(f"Tecla [{hab.tecla_str}]", True, (255, 220, 80))
        pantalla.blit(txt_tecla, (tarjeta_x + tarjeta_w - txt_tecla.get_width() - 10, cur_y + 7))

        # Costo
        costo_mostrado = hab.obtener_costo_base(jugador)
        txt_costo = fuente_mini.render(f"Costo: {costo_mostrado} En.", True, (180, 140, 255))
        pantalla.blit(txt_costo, (tarjeta_x + 10, cur_y + 26))

        # Estado y Cuenta Regresiva
        if hab.estado == "LISTA":
            txt_est = fuente_mini.render("LISTA (Disponible)", True, (100, 255, 140))
            pantalla.blit(txt_est, (tarjeta_x + 10, cur_y + 46))

            bw = tarjeta_w - 20
            pygame.draw.rect(pantalla, (40, 50, 45), (tarjeta_x + 10, cur_y + 64, bw, 6), border_radius=3)
            pygame.draw.rect(pantalla, (100, 255, 140), (tarjeta_x + 10, cur_y + 64, bw, 6), border_radius=3)

        elif hab.estado == "ACTIVA":
            txt_est = fuente_mini.render("⚡ ACTIVA", True, (0, 220, 255) if hab.nombre == "Destello" else (255, 120, 80))
            pantalla.blit(txt_est, (tarjeta_x + 10, cur_y + 44))

            seg = max(0.0, hab.tiempo_restante_activo)
            txt_tiempo = fuente_contador.render(f"{seg:.1f}s", True, (255, 255, 255))
            pantalla.blit(txt_tiempo, (tarjeta_x + tarjeta_w - txt_tiempo.get_width() - 10, cur_y + 38))

            prog = seg / max(0.1, hab.duracion_activa)
            bw = tarjeta_w - 20
            ancho_l = int(bw * max(0.0, min(1.0, prog)))
            pygame.draw.rect(pantalla, (35, 45, 55), (tarjeta_x + 10, cur_y + 64, bw, 6), border_radius=3)
            if ancho_l > 0:
                pygame.draw.rect(pantalla, (0, 210, 255) if hab.nombre == "Destello" else (255, 90, 60), (tarjeta_x + 10, cur_y + 64, ancho_l, 6), border_radius=3)

        elif hab.estado == "COOLDOWN":
            txt_est = fuente_mini.render("⏳ ENFRIAMIENTO", True, (255, 150, 60))
            pantalla.blit(txt_est, (tarjeta_x + 10, cur_y + 44))

            seg = max(0.0, hab.tiempo_restante_cooldown)
            txt_tiempo = fuente_contador.render(f"{seg:.1f}s", True, (255, 200, 140))
            pantalla.blit(txt_tiempo, (tarjeta_x + tarjeta_w - txt_tiempo.get_width() - 10, cur_y + 38))

            prog = seg / max(0.1, hab.duracion_cooldown)
            bw = tarjeta_w - 20
            ancho_l = int(bw * max(0.0, min(1.0, prog)))
            pygame.draw.rect(pantalla, (45, 35, 30), (tarjeta_x + 10, cur_y + 64, bw, 6), border_radius=3)
            if ancho_l > 0:
                pygame.draw.rect(pantalla, (255, 140, 50), (tarjeta_x + 10, cur_y + 64, ancho_l, 6), border_radius=3)

        # Resumen del efecto
        if hab.nombre == "Destello":
            detalles = "10s (+50% Vel) | CD 5s (-20%)"
        elif hab.nombre == "Burst de Fuerza":
            detalles = "6s (+20% Fuerza) | CD 12s"
        else:
            detalles = "Disparo recto vel 10 | CD 2s"

        txt_det = fuente_mini.render(detalles, True, (160, 170, 190))
        pantalla.blit(txt_det, (tarjeta_x + 10, cur_y + 75))

        if hab.mensaje_alerta:
            txt_ale = fuente_mini.render(hab.mensaje_alerta, True, (255, 80, 80))
            pantalla.blit(txt_ale, (tarjeta_x + 10, cur_y + 88))

        cur_y += tarjeta_h + 8

    # -----------------------------
    # MANUAL DE REGLAS DE HABILIDADES
    # -----------------------------
    manual_y = cur_y + 2
    pygame.draw.line(pantalla, (45, 52, 68), (x + 15, manual_y), (x + ancho - 15, manual_y), 1)

    txt_man_tit = fuente_sub.render("📖 MANUAL DE REGLAS", True, (255, 215, 0))
    pantalla.blit(txt_man_tit, (x + 15, manual_y + 6))

    lineas_manual = [
        ("• Regeneración de Energía:", (220, 225, 235)),
        ("  - Parado: +1 c/3.0s | Móvil: +1 c/6.0s", (100, 255, 140)),
        ("", None),
        ("• Combo Simultáneo:", (220, 225, 235)),
        ("  +5% energía actual al lanzar", (180, 190, 205)),
        ("  habilidad con otra ya activa.", (255, 120, 80)),
        ("", None),
        ("• [1] Espada Ligera:", (220, 225, 235)),
        ("  Daño = Fuerza x2 | -20% Vel", (170, 180, 200)),
        ("• Habilidades asignadas:", (255, 215, 0)),
        ("  Slots en teclas [2], [3] y [4]", (180, 190, 205)),
        ("• Hitbox: [H] Activar/Desactivar visor", (120, 220, 255))
    ]

    my = manual_y + 26
    for linea, color in lineas_manual:
        if color is None:
            my += 3
            continue
        surf = fuente_mini.render(linea, True, color)
        pantalla.blit(surf, (x + 15, my))
        my += 15


# -----------------------------
# CATÁLOGO DE HABILIDADES DISPONIBLES
# -----------------------------
HABILIDADES_DISPONIBLES = {
    "Destello": Destello,
    "Burst de Fuerza": BurstDeFuerza,
    "Disparo Veloz": DisparoVeloz
}

def crear_habilidad(nombre):
    cls = HABILIDADES_DISPONIBLES.get(nombre)
    if cls:
        return cls()
    return None
