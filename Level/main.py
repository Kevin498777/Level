import tkinter as tk
from tkinter import ttk
import random
import pygame
from habilidades import HABILIDADES_DISPONIBLES, crear_habilidad
from herramientas import EspadaLigera
from mundo import iniciar_mundo

# -----------------------------
# PALETA DE COLORES
# -----------------------------
COLORES = {
    "Azul": (0, 150, 255),
    "Rojo": (255, 60, 60),
    "Verde": (0, 210, 110),
    "Amarillo": (255, 220, 0),
    "Morado": (160, 80, 255),
    "Naranja": (255, 140, 30),
    "Cian": (0, 230, 240)
}

# -----------------------------
# GENERACIÓN DE VALORES ALEATORIOS
# -----------------------------
def generar_estadisticas():
    return {
        "vida": random.randint(15, 25),
        "fuerza": random.randint(1, 5),
        "velocidad": random.randint(1, 4),
        "energia": random.randint(1, 100),
        "defensa": random.randint(0, 10),
        "tamano": 1  # Estático en 1 por ahora
    }


# -----------------------------
# PERSONAJE DE PRUEBAS (NOMBRE CLAVE)
# -----------------------------
NOMBRE_CLAVE_PRUEBAS = "shadow498"

STATS_PRUEBAS = {
    "velocidad": 99,
    "fuerza": 999,      # Daño base = fuerza -> 999 (con Espada Ligera x2)
    "energia": 999,
    "vida": 999,
    "defensa": 999
}


def aplicar_stats_pruebas(nombre, stats):
    """Si el nombre es el nombre clave, sobrescribe las estadísticas con las de pruebas."""
    if nombre.strip().lower() == NOMBRE_CLAVE_PRUEBAS:
        stats = dict(stats)
        stats.update(STATS_PRUEBAS)
    return stats

# -----------------------------
# INTERFAZ PRINCIPAL DE CREACIÓN
# -----------------------------
def iniciar_aplicacion():
    stats_actuales = generar_estadisticas()

    ventana = tk.Tk()
    ventana.title("Creador de Personaje - Level")
    ventana.geometry("560x830")
    ventana.resizable(False, False)
    ventana.configure(bg="#1E2229")

    # Centrar ventana en pantalla
    ancho = 560
    alto = 830
    x = (ventana.winfo_screenwidth() - ancho) // 2
    y = (ventana.winfo_screenheight() - alto) // 2
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

    # Título Principal
    titulo = tk.Label(
        ventana,
        text="CREACIÓN DE PERSONAJE",
        font=("Segoe UI", 16, "bold"),
        fg="#FFFFFF",
        bg="#1E2229"
    )
    titulo.pack(pady=(10, 2))

    subtitulo = tk.Label(
        ventana,
        text="Configura tu héroe, herramientas y habilidades antes de comenzar.",
        font=("Segoe UI", 8),
        fg="#9DA5B4",
        bg="#1E2229"
    )
    subtitulo.pack(pady=(0, 6))

    # -----------------------------
    # ENTRADA: NOMBRE DEL PERSONAJE
    # -----------------------------
    frame_nombre = tk.Frame(ventana, bg="#1E2229")
    frame_nombre.pack(pady=2, padx=26, fill="x")

    tk.Label(
        frame_nombre,
        text="Nombre del Personaje:",
        font=("Segoe UI", 10, "bold"),
        fg="#E5C07B",
        bg="#1E2229"
    ).pack(anchor="w", pady=(0, 2))

    nombre_var = tk.StringVar(value="Héroe")
    entry_nombre = tk.Entry(
        frame_nombre,
        textvariable=nombre_var,
        font=("Segoe UI", 11),
        bg="#282C34",
        fg="white",
        insertbackground="white",
        relief="flat",
        highlightthickness=1,
        highlightbackground="#4B5263",
        highlightcolor="#61AFEF"
    )
    entry_nombre.pack(fill="x", ipady=3)

    # -----------------------------
    # SELECCIÓN DE COLOR Y VISTA PREVIA
    # -----------------------------
    frame_color_prev = tk.Frame(ventana, bg="#1E2229")
    frame_color_prev.pack(pady=3, padx=26, fill="x")

    frame_selector = tk.Frame(frame_color_prev, bg="#1E2229")
    frame_selector.pack(side="left", fill="both", expand=True)

    tk.Label(
        frame_selector,
        text="Color del personaje:",
        font=("Segoe UI", 10, "bold"),
        fg="#61AFEF",
        bg="#1E2229"
    ).pack(anchor="w", pady=(0, 2))

    color_var = tk.StringVar(value="Azul")
    combo_color = ttk.Combobox(
        frame_selector,
        textvariable=color_var,
        values=list(COLORES.keys()),
        state="readonly",
        font=("Segoe UI", 10)
    )
    combo_color.pack(anchor="w", fill="x", pady=2)

    vista_canvas = tk.Canvas(
        frame_color_prev,
        width=55,
        height=55,
        bg="#282C34",
        highlightthickness=1,
        highlightbackground="#4B5263"
    )
    vista_canvas.pack(side="right", padx=(10, 0))

    def actualizar_vista_previa(*args):
        vista_canvas.delete("all")
        nombre_color = color_var.get()
        rgb = COLORES.get(nombre_color, (0, 150, 255))
        color_hex = "#{:02x}{:02x}{:02x}".format(*rgb)

        radio = 16
        cx, cy = 27, 27
        vista_canvas.create_oval(
            cx - radio, cy - radio,
            cx + radio, cy + radio,
            fill=color_hex,
            outline="white",
            width=2
        )
        # Espada gris paralela ( o| )
        vista_canvas.create_line(cx + radio + 3, cy - 10, cx + radio + 3, cy + 10, fill="#B0B5C0", width=2)

    color_var.trace_add("write", actualizar_vista_previa)

    # -----------------------------
    # SELECCIÓN DE EQUIPO Y HABILIDADES (SLOTS 2, 3, 4)
    # -----------------------------
    frame_equipo = tk.LabelFrame(
        ventana,
        text="  Equipo y Habilidades (Asignación en Teclas 2, 3 y 4)  ",
        font=("Segoe UI", 10, "bold"),
        fg="#61AFEF",
        bg="#282C34",
        padx=12,
        pady=5,
        relief="groove",
        bd=1
    )
    frame_equipo.pack(padx=26, pady=3, fill="x")

    tk.Label(
        frame_equipo,
        text="🗡 [1] Espada Ligera (Herramienta principal): Sacar/Guardar con [1]. Daño = Fuerza x2 | -20% Vel",
        font=("Segoe UI", 8, "italic"),
        fg="#ABB2BF",
        bg="#282C34"
    ).pack(anchor="w", pady=(0, 3))

    hab_destello_var = tk.BooleanVar(value=True)
    hab_burst_var = tk.BooleanVar(value=True)
    hab_disparo_var = tk.BooleanVar(value=True)

    chk_destello = tk.Checkbutton(
        frame_equipo,
        text="Destello (+50% vel por 10s -> CD 5s con -20% debuff | Costo: 10 En.)",
        variable=hab_destello_var,
        font=("Segoe UI", 8, "bold"),
        fg="#56B6C2",
        bg="#282C34",
        selectcolor="#1E2229",
        activebackground="#282C34",
        activeforeground="#56B6C2"
    )
    chk_destello.pack(anchor="w", pady=1)

    chk_burst = tk.Checkbutton(
        frame_equipo,
        text="Burst de Fuerza (+20% fuerza por 6s | CD 12s | Costo: 15 En.)",
        variable=hab_burst_var,
        font=("Segoe UI", 8, "bold"),
        fg="#E5C07B",
        bg="#282C34",
        selectcolor="#1E2229",
        activebackground="#282C34",
        activeforeground="#E5C07B"
    )
    chk_burst.pack(anchor="w", pady=1)

    chk_disparo = tk.Checkbutton(
        frame_equipo,
        text="Disparo Veloz (Ataque a distancia recto vel 10, 20% daño total | Costo 15% En. Total | CD 2s)",
        variable=hab_disparo_var,
        font=("Segoe UI", 8, "bold"),
        fg="#98C379",
        bg="#282C34",
        selectcolor="#1E2229",
        activebackground="#282C34",
        activeforeground="#98C379"
    )
    chk_disparo.pack(anchor="w", pady=1)

    # -----------------------------
    # MANUAL INTEGRADO EN CREACIÓN
    # -----------------------------
    frame_manual = tk.LabelFrame(
        ventana,
        text="  📖 Manual de Reglas de Herramientas y Habilidades  ",
        font=("Segoe UI", 9, "bold"),
        fg="#ABB2BF",
        bg="#21252B",
        padx=12,
        pady=5,
        relief="solid",
        bd=1
    )
    frame_manual.pack(padx=26, pady=3, fill="x")

    txt_manual_gui = (
        "• Herramienta [1] Espada Ligera: Alternar con [1]. Debuff de -20% Vel acumulable.\n"
        "• Habilidades [2], [3] y [4]: Se asignan en orden según las habilidades que elijas.\n"
        "• Disparo Veloz: Lanza una esfera de energía en línea recta a vel 10 (20% daño total).\n"
        "• Hitboxes: Círculo y espada tienen hitboxes reales. Pulsa [H] en el mundo para verlas.\n"
        "• Efectos visuales de habilidad: Se muestran dentro del círculo para no distorsionar el tamaño.\n"
        "• Combo y Regeneración: +5% En. si lanzas con otra activa. Regen: +1 c/3s quieto | +1 c/6s móvil."
    )

    lbl_manual_texto = tk.Label(
        frame_manual,
        text=txt_manual_gui,
        font=("Segoe UI", 8),
        fg="#D19A66",
        bg="#21252B",
        justify="left"
    )
    lbl_manual_texto.pack(anchor="w")

    # -----------------------------
    # PANEL DE ESTADÍSTICAS ALEATORIAS
    # -----------------------------
    frame_stats = tk.LabelFrame(
        ventana,
        text="  Estadísticas Iniciales (Aleatorias / Fijas)  ",
        font=("Segoe UI", 10, "bold"),
        fg="#ABB2BF",
        bg="#282C34",
        padx=12,
        pady=5,
        relief="groove",
        bd=1
    )
    frame_stats.pack(padx=26, pady=3, fill="x")

    def renderizar_stats():
        for widget in frame_stats.winfo_children():
            widget.destroy()

        # Vista previa: si se escribe el nombre clave, mostrar las stats de pruebas
        stats_vista = aplicar_stats_pruebas(nombre_var.get(), stats_actuales)

        filas = [
            ("Vida (15 a 25):", stats_vista["vida"], "#E06C75"),
            ("Fuerza (1 a 5):", stats_vista["fuerza"], "#D19A66"),
            ("Velocidad (1 a 4):", stats_vista["velocidad"], "#56B6C2"),
            ("Energía (1 a 100):", stats_vista["energia"], "#C678DD"),
            ("Defensa (0 a 10):", stats_vista["defensa"], "#98C379"),
            ("Tamaño (Estático):", stats_vista["tamano"], "#E5C07B")
        ]

        for idx, (etiqueta, valor, color_destaque) in enumerate(filas):
            col = 0 if idx < 3 else 2
            fila = idx % 3

            tk.Label(
                frame_stats,
                text=etiqueta,
                font=("Segoe UI", 9, "bold"),
                fg="#ABB2BF",
                bg="#282C34"
            ).grid(row=fila, column=col, sticky="w", pady=2, padx=(0, 4))

            tk.Label(
                frame_stats,
                text=str(valor),
                font=("Segoe UI", 9, "bold"),
                fg=color_destaque,
                bg="#1E2229",
                width=5,
                relief="solid",
                bd=1
            ).grid(row=fila, column=col + 1, sticky="w", pady=2, padx=(0, 10))

    def reroll_stats():
        nonlocal stats_actuales
        stats_actuales = generar_estadisticas()
        renderizar_stats()

    btn_reroll = tk.Button(
        ventana,
        text="🎲 Tirar nuevos valores aleatorios",
        font=("Segoe UI", 8),
        bg="#3B4048",
        fg="#FFFFFF",
        activebackground="#4B5263",
        activeforeground="#FFFFFF",
        relief="flat",
        cursor="hand2",
        command=reroll_stats
    )
    btn_reroll.pack(pady=(0, 3))

    # -----------------------------
    # BOTÓN: COMENZAR MUNDO
    # -----------------------------
    def al_comenzar_mundo():
        nombre = nombre_var.get().strip()
        if not nombre:
            nombre = "Héroe"

        color_rgb = COLORES.get(color_var.get(), (0, 150, 255))

        # Recoger habilidades en el orden elegido
        habilidades_seleccionadas = []
        if hab_destello_var.get():
            habilidades_seleccionadas.append(crear_habilidad("Destello"))
        if hab_burst_var.get():
            habilidades_seleccionadas.append(crear_habilidad("Burst de Fuerza"))
        if hab_disparo_var.get():
            habilidades_seleccionadas.append(crear_habilidad("Disparo Veloz"))

        # Asignación dinámica de teclas a los slots 2, 3 y 4
        slots_teclas = [
            (pygame.K_2, "2"),
            (pygame.K_3, "3"),
            (pygame.K_4, "4")
        ]
        for idx, hab in enumerate(habilidades_seleccionadas[:3]):
            tecla, tecla_str = slots_teclas[idx]
            hab.asignar_tecla(tecla, tecla_str)

        # Personaje de pruebas: con el nombre clave se aplican stats especiales
        stats_finales = aplicar_stats_pruebas(nombre, stats_actuales)

        # Configuración para iniciar el mundo
        config_mundo = {
            "nombre": nombre,
            "color": color_rgb,
            "tamano": stats_finales["tamano"],
            "velocidad": stats_finales["velocidad"],
            "vida": stats_finales["vida"],
            "fuerza": stats_finales["fuerza"],
            "energia": stats_finales["energia"],
            "defensa": stats_finales["defensa"],
            "habilidades": habilidades_seleccionadas,
            "herramienta": EspadaLigera()
        }

        # Destruir ventana de creación
        ventana.destroy()

        # Iniciar el mundo modularmente
        iniciar_mundo(config_mundo)

    btn_comenzar = tk.Button(
        ventana,
        text="▶ Comenzar mundo (Pantalla Completa)",
        font=("Segoe UI", 12, "bold"),
        bg="#98C379",
        fg="#1E2229",
        activebackground="#7FA961",
        activeforeground="#1E2229",
        relief="flat",
        cursor="hand2",
        command=al_comenzar_mundo
    )
    btn_comenzar.pack(fill="x", padx=26, pady=(3, 10), ipady=5)

    # Re-dibujar estadísticas al escribir el nombre (detecta el nombre clave de pruebas)
    nombre_var.trace_add("write", lambda *args: renderizar_stats())

    # Inicializar vistas
    actualizar_vista_previa()
    renderizar_stats()

    # Bucle de la interfaz gráfica
    ventana.mainloop()


if __name__ == "__main__":
    iniciar_aplicacion()
