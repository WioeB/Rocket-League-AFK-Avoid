# Rocket League AFK Avoid

Script for Windows that drives your Rocket League car forward a little every few seconds so the game doesn't count you as idle.

When it's on, it holds **W** for 1 second every 5 seconds, and only while Rocket League is the active window.

> 🇪🇸 [Versión en español más abajo](#español)

## Requirements

- Windows 10/11
- [Python 3](https://www.python.org/downloads/) (standard library only, nothing to install with `pip`)
- Rocket League using the default keyboard controls (W = throttle)

## Usage

1. Download or clone the repository:
   ```bash
   git clone https://github.com/WioeB/Rocket-League-AFK-Avoid.git
   ```
2. Double-click `iniciar_rl_mover.bat`, or run:
   ```bash
   python rl_mover.py
   ```
3. Leave the console window open and switch back to Rocket League.
4. Use the hotkeys:

| Key  | Action          |
|------|-----------------|
| `F8` | Turn on / pause |
| `F9` | Quit            |

The console prints what the script is doing (`ACTIVADO`, `Adelante...`, `PAUSADO`, …).

## Settings

Edit the constants at the top of `rl_mover.py`:

```python
INTERVALO = 5.0      # seconds between movements
DURACION = 1.0       # seconds W is held down
PROCESO_JUEGO = "rocketleague.exe"
```

## How it works

- It sends the key with `SendInput` using the **scan code** for W (`0x11`). Games read the physical keyboard that way, so a plain virtual-key press often doesn't reach them.
- Before each movement it checks that the foreground window belongs to `rocketleague.exe`. If you're in another app, it skips that movement, so it never types "w" anywhere else.
- It watches F8/F9 with `GetAsyncKeyState`, so the hotkeys work while the game has focus.
- It's pure `ctypes`, with no external libraries.

## Files

| File                   | Description                    |
|------------------------|--------------------------------|
| `rl_mover.py`          | The script                     |
| `iniciar_rl_mover.bat` | Double-click launcher          |

## Disclaimer

Using automation to dodge AFK detection in online matches may break Psyonix/Epic's terms of service and can get you penalized. It's safer to use it in private matches, free play or offline. You use it at your own risk.

---

## Español

Script para Windows que mueve tu coche de Rocket League un poco hacia adelante cada pocos segundos, para que el juego no te cuente como inactivo.

Cuando está activado, mantiene **W** pulsada 1 segundo cada 5 segundos, y solo si Rocket League es la ventana activa.

### Requisitos

- Windows 10/11
- Python 3 (solo la librería estándar)
- Controles de teclado por defecto en Rocket League (W = acelerar)

### Uso

1. Haz doble clic en `iniciar_rl_mover.bat`.
2. Deja la consola abierta y vuelve a Rocket League.
3. Pulsa **F8** para activarlo o pausarlo y **F9** para salir.

### Configuración

Cambia `INTERVALO` (segundos entre movimientos) y `DURACION` (segundos con W pulsada) al principio de `rl_mover.py`.

### Aviso

Usarlo para no salir por inactividad en partidas online puede ir contra las normas de Psyonix/Epic. Mejor úsalo en partidas privadas o en entrenamiento libre. Lo usas bajo tu responsabilidad.
