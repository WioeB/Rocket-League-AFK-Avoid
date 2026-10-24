"""
Mueve el coche de Rocket League hacia adelante (tecla W) durante 1 segundo cada 5 segundos.

Controles:
  F8  -> activar / pausar
  F9  -> salir

Solo pulsa W cuando la ventana activa es Rocket League, así no escribe "w" en otras apps.
Sin dependencias: solo Python estándar (Windows).
"""
import ctypes
import os
import time
from ctypes import wintypes

INTERVALO = 5.0      # segundos entre cada movimiento
DURACION = 1.0       # segundos que se mantiene pulsada la W
PROCESO_JUEGO = "rocketleague.exe"

VK_F8 = 0x77
VK_F9 = 0x78
SCAN_W = 0x11        # scan code de W (los juegos leen scan codes, no virtual keys)

KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008
INPUT_KEYBOARD = 1
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000

user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

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


def enviar_tecla(scan, soltar=False):
    flags = KEYEVENTF_SCANCODE | (KEYEVENTF_KEYUP if soltar else 0)
    inp = INPUT(type=INPUT_KEYBOARD, u=_INPUTUNION(ki=KEYBDINPUT(0, scan, flags, 0, 0)))
    user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))


def juego_en_primer_plano():
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return False
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value)
    if not handle:
        return False
    try:
        buf = ctypes.create_unicode_buffer(1024)
        size = wintypes.DWORD(len(buf))
        if not kernel32.QueryFullProcessImageNameW(handle, 0, buf, ctypes.byref(size)):
            return False
        return os.path.basename(buf.value).lower() == PROCESO_JUEGO
    finally:
        kernel32.CloseHandle(handle)


def tecla_pulsada(vk):
    # Bit 0 = pulsada desde la última consulta
    return user32.GetAsyncKeyState(vk) & 0x0001


def esperar(segundos):
    """Espera vigilando F8/F9. Devuelve 'toggle', 'salir' o None."""
    fin = time.time() + segundos
    while time.time() < fin:
        if tecla_pulsada(VK_F9):
            return "salir"
        if tecla_pulsada(VK_F8):
            return "toggle"
        time.sleep(0.05)
    return None


def main():
    activo = False
    print("RL mover listo.  F8 = activar/pausar   F9 = salir")
    tecla_pulsada(VK_F8)  # limpia pulsaciones previas
    tecla_pulsada(VK_F9)
    while True:
        evento = esperar(INTERVALO if activo else 0.1)
        if evento == "salir":
            print("Saliendo.")
            break
        if evento == "toggle":
            activo = not activo
            print("ACTIVADO" if activo else "PAUSADO")
            continue
        if not activo:
            continue
        if not juego_en_primer_plano():
            print("Rocket League no está en primer plano, me salto este movimiento.")
            continue
        print("Adelante...")
        enviar_tecla(SCAN_W)
        evento = esperar(DURACION)
        enviar_tecla(SCAN_W, soltar=True)
        if evento == "salir":
            print("Saliendo.")
            break
        if evento == "toggle":
            activo = False
            print("PAUSADO")


if __name__ == "__main__":
    main()
