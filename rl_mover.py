"""
Mueve el coche de Rocket League hacia adelante durante 1 segundo cada 5 segundos,
aunque estés en otra ventana (Twitter, Discord, etc.).

Controles (funcionan desde cualquier ventana):
  F8  -> activar / pausar
  F9  -> salir

Métodos para mandar el "acelerar" al juego:
  - "mando":  crea un mando de Xbox virtual y aprieta el gatillo derecho (RT).
              Es el más fiable en segundo plano. Requiere: py -m pip install vgamepad
  - "teclas": manda W directamente a la ventana de Rocket League con mensajes de Windows.
              No necesita instalar nada, pero puede que el juego lo ignore si no está delante.
  - "auto":   usa "mando" si vgamepad está instalado y si no, "teclas".
"""
import ctypes
import os
import sys
import time
from ctypes import wintypes

INTERVALO = 5.0      # segundos entre cada movimiento
DURACION = 1.0       # segundos acelerando
METODO = "auto"      # "auto", "mando" o "teclas"
PROCESO_JUEGO = "rocketleague.exe"

VK_F8 = 0x77
VK_F9 = 0x78
VK_W = 0x57
SCAN_W = 0x11
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000

user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)


def nombre_proceso(pid):
    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not handle:
        return ""
    try:
        buf = ctypes.create_unicode_buffer(1024)
        size = wintypes.DWORD(len(buf))
        if not kernel32.QueryFullProcessImageNameW(handle, 0, buf, ctypes.byref(size)):
            return ""
        return os.path.basename(buf.value).lower()
    finally:
        kernel32.CloseHandle(handle)


def ventana_juego():
    """Devuelve el handle de la ventana principal de Rocket League, o None si no está abierto."""
    encontradas = []

    def callback(hwnd, _):
        if user32.IsWindowVisible(hwnd):
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            if nombre_proceso(pid.value) == PROCESO_JUEGO:
                encontradas.append(hwnd)
                return False  # parar la búsqueda
        return True

    user32.EnumWindows(WNDENUMPROC(callback), 0)
    return encontradas[0] if encontradas else None


class AceleradorMando:
    """Mando de Xbox virtual (ViGEmBus). XInput llega al juego aunque no tenga el foco."""
    nombre = "mando virtual (gatillo RT)"

    def __init__(self):
        import vgamepad
        self.mando = vgamepad.VX360Gamepad()
        self.mando.reset()
        self.mando.update()

    def pulsar(self, hwnd):
        self.mando.right_trigger(value=255)
        self.mando.update()

    def soltar(self, hwnd):
        self.mando.right_trigger(value=0)
        self.mando.update()


class AceleradorTeclas:
    """Manda WM_KEYDOWN/WM_KEYUP de la W a la ventana del juego, sin traerla al frente."""
    nombre = "teclas a la ventana (W)"

    def pulsar(self, hwnd):
        user32.PostMessageW(hwnd, WM_KEYDOWN, VK_W, 1 | (SCAN_W << 16))

    def mantener(self, hwnd):
        # Repetición automática, como cuando dejas una tecla pulsada de verdad
        user32.PostMessageW(hwnd, WM_KEYDOWN, VK_W, 1 | (SCAN_W << 16) | (1 << 30))

    def soltar(self, hwnd):
        user32.PostMessageW(hwnd, WM_KEYUP, VK_W, 1 | (SCAN_W << 16) | (1 << 30) | (1 << 31))


def crear_acelerador():
    if METODO in ("auto", "mando"):
        try:
            return AceleradorMando()
        except ImportError:
            if METODO == "mando":
                sys.exit("Falta vgamepad. Instálalo con:  py -m pip install vgamepad")
            print("vgamepad no está instalado, uso el método de teclas.")
            print("Si el coche no se mueve en segundo plano:  py -m pip install vgamepad")
        except Exception as e:
            if METODO == "mando":
                sys.exit(f"No se pudo crear el mando virtual: {e}")
            print(f"No se pudo crear el mando virtual ({e}), uso el método de teclas.")
    return AceleradorTeclas()


def tecla_pulsada(vk):
    # Bit 0 = pulsada desde la última consulta
    return user32.GetAsyncKeyState(vk) & 0x0001


def esperar(segundos, al_esperar=None):
    """Espera vigilando F8/F9. Devuelve 'toggle', 'salir' o None."""
    fin = time.time() + segundos
    while time.time() < fin:
        if tecla_pulsada(VK_F9):
            return "salir"
        if tecla_pulsada(VK_F8):
            return "toggle"
        if al_esperar:
            al_esperar()
        time.sleep(0.05)
    return None


def main():
    acelerador = crear_acelerador()
    activo = False
    print(f"RL mover listo, método: {acelerador.nombre}")
    print("F8 = activar/pausar   F9 = salir   (funcionan desde cualquier ventana)")
    tecla_pulsada(VK_F8)  # limpia pulsaciones previas
    tecla_pulsada(VK_F9)
    while True:
        evento = esperar(INTERVALO if activo else 0.1)
        if evento == "salir":
            break
        if evento == "toggle":
            activo = not activo
            print("ACTIVADO" if activo else "PAUSADO")
            continue
        if not activo:
            continue
        hwnd = ventana_juego()
        if not hwnd:
            print("Rocket League no está abierto, me salto este movimiento.")
            continue
        print("Adelante...")
        mantener = getattr(acelerador, "mantener", None)
        acelerador.pulsar(hwnd)
        evento = esperar(DURACION, (lambda: mantener(hwnd)) if mantener else None)
        acelerador.soltar(hwnd)
        if evento == "salir":
            break
        if evento == "toggle":
            activo = False
            print("PAUSADO")
    print("Saliendo.")


if __name__ == "__main__":
    main()
