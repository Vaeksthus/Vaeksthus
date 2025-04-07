from machine import Pin

class Flydekontakt:
    def __init__(self, pin_nr):
        self.pin = Pin(pin_nr, Pin.IN, Pin.PULL_UP)

    def er_aktiveret(self):
        """Returnerer True hvis flydekontakten er lukket (fx høj vandstand)."""
        return self.pin.value() == 0

    def __str__(self):
        return "Aktiveret" if self.er_aktiveret() else "Inaktiv"
