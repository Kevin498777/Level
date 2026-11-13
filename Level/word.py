"""
Punto de compatibilidad.
La aplicación ha sido modularizada:
- main.py: Interfaz principal de creación de personajes (Tkinter) y orquestador.
- mundo.py: Lógica y renderizado del mundo en Pygame (pantalla completa, HUDs, loop).
- personaje.py: Clase Personaje, movimiento, rotación y atributos.
- habilidades.py: Sistema de habilidades (Destello, Burst de Fuerza) y manual.
- herramientas.py: Sistema de herramientas (Espada Ligera y rotación paralela).
"""

from main import iniciar_aplicacion

if __name__ == "__main__":
    iniciar_aplicacion()
