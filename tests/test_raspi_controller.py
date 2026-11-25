from unittest import TestCase
from unittest.mock import call, patch

import RPi.GPIO as GPIO
from RPLCD.gpio import PinConfig

from trabalho_g2.raspi.controller import _LgpioCharLCD, RaspiController


class RaspiControllerTests(TestCase):
    @patch("trabalho_g2.raspi.controller._LgpioCharLCD")
    def test_write_lcd_clears_and_writes_text(self, lcd_class) -> None:
        lcd = lcd_class.return_value
        controller = RaspiController()

        controller.write_lcd("Climatizador OK")

        lcd.clear.assert_called_once_with()
        lcd.write_string.assert_called_once_with("Climatizador OK")

    @patch("trabalho_g2.raspi.controller._LgpioCharLCD")
    def test_close_clears_and_closes_lcd(self, lcd_class) -> None:
        lcd = lcd_class.return_value
        controller = RaspiController()

        controller.close()

        lcd.close.assert_called_once_with(clear=True)

    @patch("trabalho_g2.raspi.controller.c.msleep")
    @patch("trabalho_g2.raspi.controller.GPIO.output")
    @patch("trabalho_g2.raspi.controller.GPIO.setup")
    @patch("trabalho_g2.raspi.controller.GPIO.setmode")
    def test_gpio_outputs_are_initialized_low(
        self, setmode, setup, output, _sleep
    ) -> None:
        lcd = object.__new__(_LgpioCharLCD)
        lcd.numbering_mode = GPIO.BCM
        lcd.pins = PinConfig(
            rs=26,
            rw=None,
            e=19,
            d0=None,
            d1=None,
            d2=None,
            d3=None,
            d4=13,
            d5=6,
            d6=5,
            d7=12,
            backlight=None,
            mode=GPIO.BCM,
        )

        lcd._init_connection()

        setmode.assert_called_once_with(GPIO.BCM)
        setup.assert_has_calls([
            call(26, GPIO.OUT, initial=GPIO.LOW),
            call(19, GPIO.OUT, initial=GPIO.LOW),
            call(13, GPIO.OUT, initial=GPIO.LOW),
            call(6, GPIO.OUT, initial=GPIO.LOW),
            call(5, GPIO.OUT, initial=GPIO.LOW),
            call(12, GPIO.OUT, initial=GPIO.LOW),
        ])
        self.assertEqual(setup.call_count, 6)
        output.assert_has_calls([
            call(26, GPIO.LOW),
            call(19, GPIO.LOW),
        ])
        _sleep.assert_called_once_with(50)
