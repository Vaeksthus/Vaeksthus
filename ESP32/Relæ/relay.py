from machine import Pin
from time import sleep

class Relay:
    """Klasse til at styre et relæ på ESP32."""
    
    def __init__(self, pin):
        """Initialiserer relæet på den angivne pin."""
        self.relay = Pin(pin, Pin.OUT)
        self.relay.off()  # Start med relæet slukket

    def on(self):
        """Tænder relæet (NO = Normally Open)."""
        self.relay.on()

    def off(self):
        """Slukker relæet (NC = Normally Closed)."""
        self.relay.off()

    def status(self):
        """Returnerer relæets status som 'NO' eller 'NC'."""
        return "NO" if self.relay.value() else "NC"

# Hvis filen køres direkte, test relæet
if __name__ == "__main__":
    relay_pin = 26
    relay = Relay(relay_pin)

#    print("Relætest starter...")
    for _ in range(5):
        relay.on()
        print("Relæ: NO (Tændt)")
        sleep(1)
        relay.off()
        print("Relæ: NC (Slukket)")
        sleep(1)
