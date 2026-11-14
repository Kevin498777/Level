# Level: contexto del proyecto

Juego 2D en Python (Tkinter + pygame-ce 2.5.8, Python 3.14). Hablar siempre en **español** con el usuario.
Ejecutar con `python main.py`.

## Entorno (importante)
- La carpeta está en **Documentos** y Windows Defender tiene activado el **Acceso controlado a carpetas**:
  bash/PowerShell/git/python **no pueden crear, borrar ni modificar archivos** aquí.
  La herramienta Write/Edit de Claude **sí** puede escribir.
- Por eso **no hay git** (falló `git init`). Sin historial: si un cambio no gusta, se revierte a mano.
- Pendiente de que el usuario lo borre: `_prueba_escritura.txt` (archivo de prueba).
- Para probar sin ventana: `SDL_VIDEODRIVER=dummy python -B -c "..."` (`-B` evita escribir `__pycache__`).
  El juego real lo prueba el usuario.

## Archivos
- `main.py`: ventana Tkinter de creación de personaje (nombre, color, habilidades, stats aleatorias).
  - Personaje de pruebas: nombre clave **`shadow498`** (sin importar mayúsculas ni espacios) → velocidad 99,
    fuerza 999 (daño 999; con espada x2), energía 999, vida 999, defensa 999 (`STATS_PRUEBAS`).
    Las stats se actualizan en vivo al escribir el nombre.
- `mundo.py`: bucle pygame a pantalla completa, paneles laterales (izq. stats 230px, der. habilidades 240px).
  - Mapa **circular de radio 3000** (`RADIO_MUNDO`), personaje aparece en el centro, cámara con seguimiento
    suave (`SUAVIZADO_CAMARA`). Se dibuja solo lo visible (`dibujar_suelo` + offset `desplazamiento`).
  - **Rocas**: 30 a 100 por mundo (`MIN_ROCAS`/`MAX_ROCAS`), cuadrados café pálido, pequeñas (22-45) y grandes (70-130),
    sólidas (no se pueden atravesar ni empujar).
  - **Charcos**: 3 por mapa, forma de nube, radio 30-200, agua azul con orilla de barro café; **-50% velocidad**.
  - Indicador inferior: posición, distancia al centro, rocas, charcos, "EN AGUA" y "OCULTO EN ARBUSTO".
  - [H] muestra hitboxes (incluye rocas, charcos y tipo de arbusto). [ESC] sale.
- `vegetacion.py`: arbustos con forma de nube y los mismos 3 verdes (no se distinguen a simple vista).
  - Escondite (10-30), Venenoso (5-10, 1 de daño cada 2 s, ignora defensa), Frutal (1-5, con 1-5 orbes rojos
    que curan +2 sin pasar de `vida_max`; solo se ven desde dentro; al vaciarse el arbusto desaparece y a los
    60 s aparece otro frutal en un lugar aleatorio).
  - Diámetro 30-100 px (el usuario pidió "3 a 10"; se interpretó x10 porque el personaje mide 40 px).
    Los frutales miden al menos 50. Si el personaje no cabe, el arbusto es sólido.
  - Dentro: `personaje.oculto = True` (pensado para futuros personajes/IA), nombre oculto,
    arbusto semitransparente y el mapa oscurecido (`OSCURECIMIENTO`).
- `personaje.py`: clase `Personaje`. Movimiento por clic con sub-pasos (velocidades altas no atraviesan rocas),
  colisión círculo-rectángulo (rocas) y círculo-círculo (arbustos pequeños), límite circular,
  `en_agua`, `vida_max`, `oculto`, `arbusto_actual`. **Ojos**: 2 puntos negros que miran hacia donde se mueve.
- `herramientas.py`: Espada Ligera (tecla 1, daño = fuerza x2, -20% vel), **inclinada 15°** (`inclinacion`).
- `habilidades.py`: Destello, Burst de Fuerza, Disparo Veloz (teclas 2/3/4) y panel derecho.
- `word.py`: solo compatibilidad, llama a `main.py`.

## Convención de dibujo
Todo lo del mundo se dibuja con `desplazamiento = (vista.x - mundo_x, vista.y - mundo_y)`:
pantalla = mundo - desplazamiento. Las funciones `dibujar(...)` reciben ese offset.
Orden: suelo → charcos → rocas → personaje → arbustos → capa oscura + orbes (si está oculto) → hitboxes.

## Pendiente / ideas
- No hay muerte (la vida puede llegar a 0 y el juego sigue).
- Los proyectiles atraviesan las rocas (eran solo decoración).
- No hay otros personajes ni enemigos todavía (el sistema de ocultarse está preparado para ellos).
