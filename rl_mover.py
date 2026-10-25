"""
Mueve el coche de Rocket League hacia adelante durante 1 segundo cada 5 segundos,
aunque estés en otra ventana (Twitter, Discord, etc.), sin quitarle el control a tu mando real.

Controles (funcionan desde cualquier ventana):
  F8  -> activar / pausar
  F9  -> salir

Cómo acelera:
  - Rocket League en segundo plano -> mando de Xbox virtual, gatillo RT (necesita vgamepad).
    Si vgamepad no está instalado, manda la W directamente a la ventana del juego.
  - Rocket League delante         -> tecla W simulada. No se crea ningún mando virtual.

Para no interferir con tu mando:
  - El mando virtual solo existe mientras el script está activo y el juego está en segundo plano.
    Al pausar, salir o poner el juego delante, se desconecta.
  - Si vuelves al juego desde otra ventana, el script se pausa solo (PAUSAR_AL_VOLVER):
    entiende que vuelves a jugar. Pulsa F8 para reactivarlo.
"""
import ctypes
import gc
import os
import time
from ctypes import wintypes

INTERVALO = 5.0          # segundos entre cada movimiento
DURACION = 1.0           # segundos acelerando
PAUSAR_AL_VOLVER = True  # pausar solo al volver a Rocket League desde otra ventana
PROCESO_JUEGO = "rocketleague.exe"

VK_F8 = 0x77
VK_F9 = 0x78
VK_W = 0x57
SCAN_W = 0x11
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008
INPUT_KEYBOARD = 1
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000

user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
ULONG_PTR = ctypes.c_size_t


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD), ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD), ("dwExtraInfo", ULONG_PTR)]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", wintypes.LONG), ("dy", wintypes.LONG), ("mouseData", wintypes.DWORD),
                ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD), ("dwExtraInfo", ULONG_PTR)]


class _INPUTUNION(ctypes.Union):
    _fields_ = [("ki", KEYBDINPUT), ("mi", MOUSEINPUT)]


class INPUT(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD), ("u", _INPUTUNION)]


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


def proceso_de_ventana(hwnd):
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return nombre_proceso(pid.value)


def ventana_juego():
    """Devuelve el handle de la ventana principal de Rocket League, o None si no está abierto."""
    encontradas = []

    def callback(hwnd, _):
        if user32.IsWindowVisible(hwnd) and proceso_de_ventana(hwnd) == PROCESO_JUEGO:
            encontradas.append(hwnd)
            return False  # parar la búsqueda
        return True

    user32.EnumWindows(WNDENUMPROC(callback), 0)
    return encontradas[0] if encontradas else None


def juego_delante():
    hwnd = user32.GetForegroundWindow()
    return bool(hwnd) and proceso_de_ventana(hwnd) == PROCESO_JUEGO


# --- Formas de acelerar ---------------------------------------------------------------

class TeclaSimulada:
    """W simulada con SendInput. Solo llega a la ventana que está delante."""
    nombre = "tecla W"

    def _enviar(self, soltar):
        flags = KEYEVENTF_SCANCODE | (KEYEVENTF_KEYUP if soltar else 0)
        inp = INPUT(type=INPUT_KEYBOARD, u=_INPUTUNION(ki=KEYBDINPUT(0, SCAN_W, flags, 0, 0)))
        user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))

    def pulsar(self, hwnd):
        self._enviar(False)

    def soltar(self, hwnd):
        self._enviar(True)


class TeclaAVentana:
    """Manda WM_KEYDOWN/WM_KEYUP de la W a la ventana del juego, sin traerla al frente."""
    nombre = "W enviada a la ventana"

    def pulsar(self, hwnd):
        user32.PostMessageW(hwnd, WM_KEYDOWN, VK_W, 1 | (SCAN_W << 16))

    def mantener(self, hwnd):
        # Repetición automática, como cuando dejas una tecla pulsada de verdad
        user32.PostMessageW(hwnd, WM_KEYDOWN, VK_W, 1 | (SCAN_W << 16) | (1 << 30))

    def soltar(self, hwnd):
        user32.PostMessageW(hwnd, WM_KEYUP, VK_W, 1 | (SCAN_W << 16) | (1 << 30) | (1 << 31))


class MandoVirtual:
    """Mando de Xbox virtual (ViGEmBus). Solo se conecta mientras hace falta."""
    nombre = "mando virtual (RT)"

    def __init__(self):
        import vgamepad  # falla aquí si no está instalado
        self._vgamepad = vgamepad
        self.mando = None

    @property
    def conectado(self):
        return self.mando is not None

    def conectar(self):
        if self.mando is None:
            self.mando = self._vgamepad.VX360Gamepad()
            self.mando.reset()
            self.mando.update()
            print("Mando virtual conectado.")
            time.sleep(0.5)  # dar tiempo a que el juego lo detecte

    def desconectar(self):
        if self.mando is not None:
            self.mando.reset()
            self.mando.update()
            self.mando = None
            gc.collect()  # vgamepad desenchufa el mando al liberarse
            print("Mando virtual desconectado.")

    def pulsar(self, hwnd):
        self.conectar()
        self.mando.right_trigger(value=255)
        self.mando.update()

    def soltar(self, hwnd):
        if self.mando is not None:
            self.mando.right_trigger(value=0)
            self.mando.update()


def crear_mando():
    try:
        return MandoVirtual()
    except ImportError:
        print("vgamepad no está instalado: en segundo plano mandaré la W a la ventana.")
        print("Si así no se mueve:  py -m pip install vgamepad")
        return None


# --- Bucle principal ------------------------------------------------------------------

def tecla_pulsada(vk):
    # Bit 0 = pulsada desde la última consulta
    return user32.GetAsyncKeyState(vk) & 0x0001


class Estado:
    def __init__(self):
        self.activo = False
        self.mando = crear_mando()
        self.teclado = TeclaSimulada()
        self.ventana = TeclaAVentana()
        self.estaba_delante = juego_delante()

    def soltar_mando(self):
        if self.mando:
            self.mando.desconectar()

    def pausar(self, motivo=""):
        self.activo = False
        self.soltar_mando()
        print("PAUSADO" + (f" ({motivo})" if motivo else ""))

    def vigilar(self):
        """Se llama cada 0,05 s. Devuelve 'salir' o None."""
        if tecla_pulsada(VK_F9):
            return "salir"
        if tecla_pulsada(VK_F8):
            if self.activo:
                self.pausar()
            else:
                self.activo = True
                print("ACTIVADO")
        delante = juego_delante()
        if delante and not self.estaba_delante:
            # Has vuelto al juego: quitar el mando virtual para que mande el tuyo
            self.soltar_mando()
            if self.activo and PAUSAR_AL_VOLVER:
                self.pausar("has vuelto al juego, F8 para reactivar")
        self.estaba_delante = delante
        return None

    def esperar(self, segundos, al_esperar=None):
        fin = time.time() + segundos
        while time.time() < fin:
            if self.vigilar() == "salir":
                return "salir"
            if al_esperar:
                al_esperar()
            time.sleep(0.05)
        return None

    def mover(self):
        hwnd = ventana_juego()
        if not hwnd:
            print("Rocket League no está abierto, me salto este movimiento.")
            return None
        if juego_delante():
            acelerador = self.teclado
        elif self.mando:
            acelerador = self.mando
        else:
            acelerador = self.ventana
        print(f"Adelante ({acelerador.nombre})...")
        mantener = getattr(acelerador, "mantener", None)
        acelerador.pulsar(hwnd)
        evento = self.esperar(DURACION, (lambda: mantener(hwnd)) if mantener else None)
        acelerador.soltar(hwnd)
        return evento


def main():
    estado = Estado()
    print("RL mover listo.  F8 = activar/pausar   F9 = salir   (desde cualquier ventana)")
    tecla_pulsada(VK_F8)  # limpia pulsaciones previas
    tecla_pulsada(VK_F9)
    try:
        while True:
            if not estado.activo:
                if estado.esperar(0.1) == "salir":
                    break
                continue
            if estado.esperar(INTERVALO) == "salir":
                break
            if estado.activo and estado.mover() == "salir":
                break
    finally:
        estado.soltar_mando()
        print("Saliendo.")


if __name__ == "__main__":
    main()
