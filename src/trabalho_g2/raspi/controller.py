from threading import Lock

import RPi.GPIO as GPIO
from RPLCD import common as c
from RPLCD.gpio import CharLCD


class _LgpioCharLCD(CharLCD):
    def _init_connection(self) -> None:
        GPIO.setmode(GPIO.BCM)
        for pin in (pin for pin in self.pins[:-1] if pin is not None):
            GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

        c.msleep(50)
        GPIO.output(self.pins.rs, GPIO.LOW)
        GPIO.output(self.pins.e, GPIO.LOW)
        if self.pins.rw is not None:
            GPIO.output(self.pins.rw, GPIO.LOW)


class RaspiController:
    def __init__(self) -> None:
        self._lcd = _LgpioCharLCD(
            numbering_mode=GPIO.BCM,
            cols=16,
            rows=2,
            pin_rs=26,
            pin_e=19,
            pins_data=[13, 6, 5, 12],
        )
        self._write_lock = Lock()

    def write_lcd(self, text: str) -> None:
        with self._write_lock:
            self._lcd.clear()
            self._lcd.write_string(text)

    def close(self) -> None:
        with self._write_lock:
            self._lcd.close(clear=True)
