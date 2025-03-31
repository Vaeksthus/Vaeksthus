from machine import ADC, Pin
from time import sleep

class LMT87:
    """Klasse til at læse temperatur fra LMT87 sensoren."""

    def __init__(self, pin):
        """Initialiserer LMT87 på den angivne pin."""
        self.sensor = ADC(Pin(pin))
        self.sensor.atten(ADC.ATTN_11DB)  # For at måle op til 3.3V
        self.t1 = None
        self.adc1 = None
        self.t2 = None
        self.adc2 = None

    def calibrate(self, t1, adc1, t2, adc2):
        """Kalibrerer sensoren baseret på to kendte temperatur/ADC-værdier."""
        self.t1, self.adc1, self.t2, self.adc2 = t1, adc1, t2, adc2

    def get_adc_value(self):
        """Returnerer den rå ADC-værdi fra sensoren."""
        return self.sensor.read()

    def get_temperature(self):
        """Beregner temperaturen baseret på den kalibrerede sensor."""
        if None in (self.t1, self.adc1, self.t2, self.adc2):
            raise ValueError("Sensoren er ikke kalibreret!")

        adc_val = self.get_adc_value()
        # Lineær interpolation for at finde temperaturen
        temperature = self.t1 + (adc_val - self.adc1) * ((self.t2 - self.t1) / (self.adc2 - self.adc1))
        return temperature

# Hvis filen køres direkte, test sensoren
if __name__ == "__main__":
    pin_lmt87 = 35
    lmt87 = LMT87(pin_lmt87)

    # Kalibreringsværdier
    t1, adc1 = 25.2, 2659
    t2, adc2 = 24.2, 2697
    lmt87.calibrate(t1, adc1, t2, adc2)

    print("LMT87 test starter...")
    while True:
        adc_val = lmt87.get_adc_value()
        temperature = lmt87.get_temperature()
        print("Temp: {:.2f}°C <- ADC: {}".format(temperature, adc_val))
        sleep(1)
