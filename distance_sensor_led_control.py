"""
This module is used to enable a distance sensor to control RGB LEDs
based on the proximity calculated by the sensor, setting different
colors for them based on the distance registered by the sensor.

For this project, the components needed are:
- Raspberry Pi with a connected distance sensor and 3 RGB LEDs
- Proper configuration between the RPi and the components
  using a breadboard and resistances.

Using GPIO and setting the pins to a device, the flow implies sending
electrical impulse to the pins (to enable and send the trigger)
or by not sending it, thus setting the voltage to either HIGH or LOW,
both being interpreted in the algorithm and the device behaving based on this.

The program configures the distance sensor and the LEDs,
set their respective voltage to LOW (no impulse received), after which:
- continuously asserts the distance in front of the sensor
- based on the perceived distance, the LEDs are enabled using a color
  related to a certain proximity level defined (in 20 cm increments).
"""

# Importing from the Raspberry Pi's library the GPIO module
# GPIO (general-purpose input/output) is a 40-pin double-row present on
# any Raspberry Pi board. Any of the GPIO pins can be designated (in software)
# as an input or output pin and used for a wide range of purposes.
import RPi.GPIO as GPIO
import time
import logging

# Setting the log level to INFO (default is WARNING)
logging.getLogger().setLevel(logging.INFO)

# Setting the mode to BOARD, since we will use that for the pin's layout
GPIO.setmode(GPIO.BOARD)

# Choosing a frequency for PWM(Pulse Width Modulation)
frequency = 100

# Distance Sensor constant
distance_sensor_constant = 17150


# Defining an object for a LED, with pins assigned
# to each of their respective RGB corresponding pin-to-anode connection
class RGB_LED():
    """
    Object used to encompass a LEDs methods and functions.
    This class is used for RGB LEDs, defining a pin number for each of them.

    Contains method to setup the pins correctly for output,
    as well as control each of the LED color's frequency(high/low).
    """

    def __init__(self, red=1, green=2, blue=3):
        """
        Prepares the available configuration for a RGB LED.

        Available parameters:
        - red: the number of the RPi's pin configured as output for red
        - green: the number of the RPi's pin configured as output for green
        - blue: the number of the RPi's pin configured as output for blue

        Defines the pins for red, green and blue and defines them
        using GPIO for output.
        """
        self.red = red
        self.green = green
        self.blue = blue
        self.led_pins = {
            "red": red,
            "green": green,
            "blue": blue
        }
        self.configure_pins_for_output()

    def configure_pins_for_output(self):
        """
        Configures the pins used by the RGB LED for output in GPIO.
        """
        for pin in self.led_pins:
            GPIO.setup(self.led_pins[pin], GPIO.OUT)
            GPIO.PWM(self.led_pins[pin], frequency)

    def shut_off_colors(self):
        """Closes off all colors and sets the pins to LOW on GPIO."""
        # Setting no impulse for each of the pins corresponding to a LED color
        for color_pin in self.led_pins:
            GPIO.output(self.led_pins[color_pin], GPIO.LOW)

    def enable_all_colors(self):
        """Enables all colors and sets the pins to HIGH on GPIO."""
        # Setting impulse for each of the pins corresponding to a LED color
        for color_pin in self.led_pins:
            GPIO.output(self.led_pins[color_pin], GPIO.HIGH)

    def set_color(self, desired_color="blue"):
        """
        Sets a specific color for the RGB LED, using its specified pins.
        """
        # Iterating through the configured pins,
        # and setting impulse only on the one for the desired color.
        for color_pin in self.led_pins:
            if color_pin == desired_color:
                # If the pin is for our desired color,
                # enable it and set it to HIGH (send impulse)
                GPIO.output(self.led_pins[color_pin], GPIO.HIGH)
            else:
                # If it's not the color we are looking for,
                # set it to low and don't send impulse there
                # e.g. turn it off
                GPIO.output(self.led_pins[color_pin], GPIO.LOW)


def proximity_level_0():
    """
    Proximity Level 0. (Farthest away from the sensor)

    On this level, all LEDs are shut off.
    """
    controlled_leds["LED 1"].shut_off_colors()
    controlled_leds["LED 2"].shut_off_colors()
    controlled_leds["LED 3"].shut_off_colors()


def proximity_level_1():
    """
    Proximity Level 1.

    On this level, only the first LED is turned on, on Green.
    """
    controlled_leds["LED 1"].set_color(desired_color="green")
    controlled_leds["LED 2"].shut_off_colors()
    controlled_leds["LED 3"].shut_off_colors()


def proximity_level_2():
    """
    Proximity Level 2.

    On this level, first LED is Blue and second is Green.
    """
    controlled_leds["LED 1"].set_color(desired_color="blue")
    controlled_leds["LED 2"].set_color(desired_color="green")
    controlled_leds["LED 3"].shut_off_colors()


def proximity_level_3():
    """
    Proximity Level 3.

    On this level, first LED is Red, second is Blue and the third is Green.
    """
    controlled_leds["LED 1"].set_color(desired_color="red")
    controlled_leds["LED 2"].set_color(desired_color="blue")
    controlled_leds["LED 3"].set_color(desired_color="green")


def proximity_level_4():
    """
    Proximity Level 4.

    On this level, first LED is Red, second is Red and the third is Blue.
    """
    controlled_leds["LED 1"].set_color(desired_color="red")
    controlled_leds["LED 2"].set_color(desired_color="red")
    controlled_leds["LED 3"].set_color(desired_color="blue")


def proximity_level_5():
    """
    Proximity Level 5. (Closest to the sensor)

    On this level, all LEDs are Red.
    """
    controlled_leds["LED 1"].set_color(desired_color="red")
    controlled_leds["LED 2"].set_color(desired_color="red")
    controlled_leds["LED 3"].set_color(desired_color="red")


# Defining the proximity levels for the distance sensor
proximity_levels = {
    "level 0": proximity_level_0,  # Farthest from sensor
    "level 1": proximity_level_1,
    "level 2": proximity_level_2,
    "level 3": proximity_level_3,
    "level 4": proximity_level_4,
    "level 5": proximity_level_5,  # Closest to sensor
}


def prepare_distance_sensor(pin_trigger, pin_echo):
    """Method used to setup the pins used by the distance sensor."""
    GPIO.setup(pin_trigger, GPIO.OUT)
    GPIO.setup(pin_echo, GPIO.IN)
    GPIO.output(pin_trigger, GPIO.LOW)


def calculate_distance(pin_trigger, pin_echo):
    """
    Calculates distance from the sensor.

    Achieved by calculating the time when the impulse has been sent,
    and when it has been received, after which the duration between the two
    is deduced and rounded up using a standard constant for the sensor.
    """

    # Sending an impulse through the output pin
    GPIO.output(pin_trigger, GPIO.HIGH)
    # Waiting for a nanosecond (the time it needs
    # to register the input as an impulse)
    time.sleep(0.00001)
    # Disable the impulse towards to output pin
    GPIO.output(pin_trigger, GPIO.LOW)

    # Assert continuously the input pin on both LOW and HIGH impulse values
    # to ensure we have latest time frames for impulse travelling calculus
    while GPIO.input(pin_echo) == 0:
        pulse_start_time = time.time()
    while GPIO.input(pin_echo) == 1:
        pulse_end_time = time.time()

    # Deduce pulse travelling duration and use the correct formula
    # to calculate the travelled distance
    pulse_duration = pulse_end_time - pulse_start_time
    distance = round(pulse_duration * distance_sensor_constant, 2)
    return distance


# Defining the pins which are to be used by the distance sensor
PIN_TRIGGER = 13
PIN_ECHO = 11

# Defining the RGB LEDs to be used, and their corresponding pins.
# When creating the objects for the RGB LEDs, the constructor handles
# the setup for the pins(e.g. setting them to LOW in GPIO) automatically.
controlled_leds = {
    "LED 1": RGB_LED(
        red=7,
        green=3,
        blue=5
    ),
    "LED 2": RGB_LED(
        red=18,
        green=16,
        blue=15
    ),
    "LED 3": RGB_LED(
        red=12,
        green=10,
        blue=8
    ),
}


if __name__ == '__main__':
    try:
        # Firstly we prepare the distance sensor pins
        prepare_distance_sensor(PIN_TRIGGER, PIN_ECHO)

        logging.info("Waiting for sensor to settle\n")
        logging.info("Calculating distance on a 1s time frame...\n")

        time.sleep(2)

        # Continuously asserting the distance that the sensor perceives,
        # and enables the correct proximity level and corresponding colors
        # for LEDs based on the calculated distance (in centimeters).
        try:
            while True:
                calculated_distance = calculate_distance(PIN_TRIGGER, PIN_ECHO)
                logging.info(
                    "Distance registered by the sensor is %s",
                    calculated_distance)

                # Asserting the distance from the sensor,
                # and triggering the correct LED colors,
                # according to the specified proximity level
                if calculated_distance > 100:
                    proximity_levels["level 0"]()

                elif 80 < calculated_distance <= 100:
                    proximity_levels["level 1"]()

                elif 60 < calculated_distance <= 80:
                    proximity_levels["level 2"]()

                elif 40 < calculated_distance <= 60:
                    proximity_levels["level 3"]()

                elif 20 < calculated_distance <= 40:
                    proximity_levels["level 4"]()

                else:
                    proximity_levels["level 5"]()

                # Wait a short time frame to ensure optimal
                # impulse reading from the distance sensor
                time.sleep(0.5)

        except KeyboardInterrupt:
            # Statement to prompt the user that we are closing the program
            logging.info("\n\nShutting down gracefully...")

    finally:
        # We set the proximity level to 0 to shut off LEDs
        # and cleanup the system
        logging.info("Closing off LEDs...\n")
        proximity_levels["level 0"]()
        logging.info("Done!\n")
