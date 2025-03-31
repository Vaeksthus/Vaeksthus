from time import sleep

from relay import Relay
from temperatur87 import LMT87

# Konfiguration af pins
PIN_LMT87 = 35
PIN_RELAY = 26

# Kalibreringsværdier for LMT87
T1, ADC1 = 25.2, 2659
T2, ADC2 = 24.2, 2697

def main():
    """Hovedfunktion der overvåger temperatur og styrer relæet."""
    relay = Relay(PIN_RELAY)
    sensor = LMT87(PIN_LMT87)
    sensor.calibrate(T1, ADC1, T2, ADC2)

    while True:
        temperature = sensor.get_temperature()
        relay_status = "NO" if relay.relay.value() else "NC"

        if temperature > 18:
            relay.on()
            relay_status = "NO"
        else:
            relay.off()
            relay_status = "NC"

        print("Temperatur: {:.2f}°C | Relæ: {}".format(temperature, relay_status))
        sleep(1)

# Hvis filen køres direkte, start hovedfunktionen
if __name__ == "__main__":
    main()
