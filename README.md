# Rocket League AFK Avoid

Script for Windows that drives your Rocket League car forward a little every few seconds so the game doesn't count you as idle. **It keeps working while you're in another window** (a browser, Discord…) and **doesn't take control away from your real controller** when you come back to play.

When it's on, it accelerates for 1 second every 5 seconds.

> 🇪🇸 [Versión en español más abajo](#español)

## Requirements

- Windows 10/11
- [Python 3](https://www.python.org/downloads/)
- Recommended: [`vgamepad`](https://pypi.org/project/vgamepad/) (installs the ViGEmBus driver; accept the installer when it appears):
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
3. Press **F8** to turn it on, then go to any other window.
4. When you come back to Rocket League, the script **pauses itself** and removes its virtual controller, so your own controller is back in charge. Press **F8** again before you leave next time.

| Key  | Action                                |
|------|---------------------------------------|
| `F8` | Turn on / pause (from any window)     |
| `F9` | Quit (from any window)                |

## How it accelerates

| Rocket League is…  | Method | Notes |
|--------------------|--------|-------|
| In the background  | Virtual Xbox 360 controller, right trigger (RT) | XInput reaches the game whether or not it has focus. If `vgamepad` isn't installed, it posts `WM_KEYDOWN`/`WM_KEYUP` for W straight to the game window instead. |
| In front           | Simulated W key (`SendInput`, scan code) | No virtual controller is created. |

### Not interfering with your controller

Rocket League can treat a newly plugged virtual controller as the main one, and then your real controller stops working. To avoid that:

- The virtual controller only exists **while the script is active and the game is in the background**.
- It's **unplugged** when you pause (F8), quit (F9), close the console, or bring Rocket League to the front.
- With `PAUSAR_AL_VOLVER = True` (the default), switching back to the game from another window also pauses the script, because it assumes you're back to play.

If your controller still doesn't respond after the virtual one is removed, unplug and reconnect it, or restart Rocket League.

## Settings

At the top of `rl_mover.py`:

```python
INTERVALO = 5.0          # seconds between movements
DURACION = 1.0           # seconds accelerating
PAUSAR_AL_VOLVER = True  # pause by itself when you switch back to the game
```

## Files

| File                   | Description           |
|------------------------|-----------------------|
| `rl_mover.py`          | The script            |
| `iniciar_rl_mover.bat` | Double-click launcher |

## Disclaimer

Using automation to dodge AFK detection in online matches may break Psyonix/Epic's terms of service and can get you penalized. It's safer to use it in private matches, free play or offline. You use it at your own risk.

---

## Español

Script para Windows que mueve tu coche de Rocket League un poco hacia adelante cada pocos segundos, para que el juego no te cuente como inactivo.

- **Funciona aunque estés en otra ventana** (Twitter, Discord…).
- **No le quita el control a tu mando real** cuando vuelves a jugar.

### Instalación

```bash
py -m pip install vgamepad
```

### Uso

1. Haz doble clic en `iniciar_rl_mover.bat`.
2. Pulsa **F8** para activarlo y vete a otra ventana.
3. Cuando vuelves a Rocket League, el script **se pausa solo** y desconecta su mando virtual, así que tu mando vuelve a funcionar. Antes de irte otra vez, pulsa **F8**.
4. **F9** lo cierra.

### Cómo evita interferir con tu mando

- El mando virtual solo existe mientras el script está activo y el juego está en segundo plano.
- Se desconecta en cuanto pausas, sales, cierras la consola o pones el juego delante.
- Si aun así tu mando no responde, desconéctalo y vuelve a conectarlo, o reinicia Rocket League.

### Aviso

Usarlo para no salir por inactividad en partidas online puede ir contra las normas de Psyonix/Epic. Mejor úsalo en partidas privadas o en entrenamiento libre. Lo usas bajo tu responsabilidad.
