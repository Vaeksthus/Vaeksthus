from time import sleep
from relay import Relay
from temperatur87 import LMT87
from float_switch import Flydekontakt  # Import af flydekontakten

# Konfiguration af pins
PIN_LMT87 = 35
PIN_RELAY = 26
PIN_FLOAT = 34  # GPIO til flydekontakten

# Kalibreringsværdier for LMT87
T1, ADC1 = 25.2, 2659
T2, ADC2 = 24.2, 2697

def main():
    """Hovedfunktion der overvåger temperatur og styrer relæet."""
    relay = Relay(PIN_RELAY)
    sensor = LMT87(PIN_LMT87)
    flyder = Flydekontakt(PIN_FLOAT)  # Initialiser flydekontakten

    sensor.calibrate(T1, ADC1, T2, ADC2)

    # Gem tidligere status for flydekontakten for at spore ændringer
    sidste_vandstatus = flyder.er_aktiveret()

    while True:
        temperature = sensor.get_temperature()
        relay_status = "NO" if relay.relay.value() else "NC"
        aktuel_vandstatus = flyder.er_aktiveret()

        # Omvendt logik for vandniveau
        vand_status = "Lavt" if aktuel_vandstatus else "Højt"

        # Temperaturstyret relæ
        if temperature > 23:
            relay.on()
            relay_status = "NO"
        else:
            relay.off()
            relay_status = "NC"

        # Print ændring i flydekontakt
        if aktuel_vandstatus != sidste_vandstatus:
            if aktuel_vandstatus:
                print("💧 Flydekontakt aktiveret – vandniveau er LAVT.")
            else:
                print("⚠️  Flydekontakt deaktiveret – vandniveau er HØJT.")

        print("Temperatur: {:.2f}°C | Relæ: {} | Vandniveau: {}".format(
            temperature, relay_status, vand_status))

        sidste_vandstatus = aktuel_vandstatus  # Opdater status
        sleep(1)

# Hvis filen køres direkte, start hovedfunktionen
if __name__ == "__main__":
    main()
