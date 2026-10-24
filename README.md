# Rocket League AFK Avoid

Script for Windows that drives your Rocket League car forward a little every few seconds so the game doesn't count you as idle. **It keeps working while you're in another window** (a browser, Discord…).

When it's on, it accelerates for 1 second every 5 seconds.

> 🇪🇸 [Versión en español más abajo](#español)

## Requirements

- Windows 10/11
- [Python 3](https://www.python.org/downloads/)
- Recommended: [`vgamepad`](https://pypi.org/project/vgamepad/) for the virtual controller method (installs the ViGEmBus driver; accept the installer when it appears):
  ```bash
  py -m pip install vgamepad
  ```

## Usage

1. Download or clone the repository:
   ```bash
   git clone https://github.com/WioeB/Rocket-League-AFK-Avoid.git
   ```
2. Double-click `iniciar_rl_mover.bat`, or run:
   ```bash
   py rl_mover.py
   ```
3. Leave the console open. You can now go to any other window.
4. Use the hotkeys (they work from any window):

| Key  | Action          |
|------|-----------------|
| `F8` | Turn on / pause |
| `F9` | Quit            |

## Methods

Set `METODO` at the top of `rl_mover.py`:

| Value      | How it accelerates | Works in background | Needs |
|------------|--------------------|---------------------|-------|
| `"mando"`  | Creates a virtual Xbox 360 controller and holds the right trigger (RT). XInput reaches the game whether or not it has focus. | Yes (most reliable) | `vgamepad` |
| `"teclas"` | Posts `WM_KEYDOWN`/`WM_KEYUP` for W straight to the Rocket League window, without bringing it to the front. | Depends on the game | Nothing |
| `"auto"` (default) | Uses `"mando"` if `vgamepad` is installed, otherwise `"teclas"`. | | |

The console prints which method is active when the script starts.

## Settings

```python
INTERVALO = 5.0      # seconds between movements
DURACION = 1.0       # seconds accelerating
METODO = "auto"      # "auto", "mando" or "teclas"
```

## How it works

1. It polls F8/F9 with `GetAsyncKeyState`, so the hotkeys work whichever window you're in.
2. Every `INTERVALO` seconds it looks for the `rocketleague.exe` window with `EnumWindows`. If the game isn't open, it skips that movement.
3. It accelerates for `DURACION` seconds with the chosen method, then releases.
4. It uses only `ctypes` from the standard library, plus `vgamepad` for the controller method.

## Files

| File                   | Description           |
|------------------------|-----------------------|
| `rl_mover.py`          | The script            |
| `iniciar_rl_mover.bat` | Double-click launcher |

## Disclaimer

Using automation to dodge AFK detection in online matches may break Psyonix/Epic's terms of service and can get you penalized. It's safer to use it in private matches, free play or offline. You use it at your own risk.

---

## Español

Script para Windows que mueve tu coche de Rocket League un poco hacia adelante cada pocos segundos, para que el juego no te cuente como inactivo. **Sigue funcionando aunque estés en otra ventana** (Twitter, Discord…).

### Instalación

```bash
py -m pip install vgamepad
```

Esto instala el mando virtual, el método más fiable. Acepta el instalador de ViGEmBus cuando aparezca. Sin `vgamepad`, el script manda la tecla W directamente a la ventana del juego, pero puede que el juego lo ignore si no está delante.

### Uso

1. Haz doble clic en `iniciar_rl_mover.bat`.
2. Pulsa **F8** para activarlo o pausarlo y **F9** para salir. Funcionan desde cualquier ventana.
3. Ya puedes irte a otra ventana.

### Configuración

Al principio de `rl_mover.py`:

- `INTERVALO`: segundos entre movimientos.
- `DURACION`: segundos acelerando.
- `METODO`: `"auto"`, `"mando"` o `"teclas"`.

### Aviso

Usarlo para no salir por inactividad en partidas online puede ir contra las normas de Psyonix/Epic. Mejor úsalo en partidas privadas o en entrenamiento libre. Lo usas bajo tu responsabilidad.
