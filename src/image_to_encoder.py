"""!
Script Name: image_to_encoder.py
Description: This script defines a class to interface with an MLX90640 thermal infrared camera for image capture and analysis.

Author: Dr. Ridgley

Modified by: Conor Schott, Fermin Moreno, Berent Baysal
Date: 3/14/2024

Dependencies:
- utime
- machine
- mlx90640
"""

import utime as time
from machine import Pin, I2C
from mlx90640 import MLX90640
from mlx90640.calibration import NUM_ROWS, NUM_COLS, TEMP_K
from mlx90640.image import ChessPattern, InterleavedPattern

class MLX_Cam:
    """
    @brief   Class which wraps an MLX90640 thermal infrared camera driver to
             make it easier to grab and use an image.
    !"""

    def __init__(self, i2c, address=0x33, pattern=ChessPattern,
                 width=NUM_COLS, height=NUM_ROWS):
        """
        @brief   Set up an MLX90640 camera.
        @param   i2c An I2C bus which has been set up to talk to the camera;
                 this must be a bus object which has already been set up
        @param   address The address of the camera on the I2C bus (default 0x33)
        @param   pattern The way frames are interleaved, as we read only half
                 the pixels at a time (default ChessPattern)
        @param   width The width of the image in pixels; leave it at default
        @param   height The height of the image in pixels; leave it at default
        !"""
        ## The I2C bus to which the camera is attached
        self._i2c = i2c
        ## The address of the camera on the I2C bus
        self._addr = address
        ## The pattern for reading the camera, usually ChessPattern
        self._pattern = pattern
        ## The width of the image in pixels, which should be 32
        self._width = width
        ## The height of the image in pixels, which should be 24
        self._height = height

        # The MLX90640 object that does the work
        self._camera = MLX90640(i2c, address)
        self._camera.set_pattern(pattern)
        self._camera.setup()

        ## A local reference to the image object within the camera driver
        self._image = self._camera.raw

    def ascii_art(self, array):
        """
        @brief   Show a data array from the IR image as ASCII art.
        @details Each character is repeated twice so the image isn't squished
                 laterally. A code of "><" indicates an error, probably caused
                 by a bad pixel in the camera. 
        @param   array The array to be shown, probably @c image.v_ir
        !"""
        asc = " -.:=+*#%@"
        scale = len(asc) / (max(array) - min(array))
        offset = -min(array)
        for row in range(self._height):
            line = ""
            for col in range(self._width):
                pix = int((array[row * self._width + (self._width - col - 1)]
                           + offset) * scale)
                try:
                    the_char = asc[pix]
                    print(f"{the_char}{the_char}", end='')
                except IndexError:
                    print("><", end='')
            print('')
        return

    def get_image(self):
        """
        @brief   Get one image from a MLX90640 camera.
        @details Grab one image from the given camera and return it. Both
                 subframes (the odd checkerboard portions of the image) are
                 grabbed and combined (maybe; this is the raw version, so the
                 combination is sketchy and not fully tested). It is assumed
                 that the camera is in the ChessPattern (default) mode as it
                 probably should be.
        @returns A reference to the image object we've just filled with data
        !"""
        for subpage in (0, 1):
            while not self._camera.has_data:
                time.sleep_ms(50)
                print('.', end='')
            image = self._camera.read_image(subpage)

        return image

    def find_hotSpot(self, array):
        """
        @brief   Find the hottest average cluster of 1x4 pixels in the image.
        @details Each pixel in the image is checked and its value is used to
                 compute a local average (in groups of four). These averages
                 are then compiled into an array, and the indices are used to
                 pinpoint the location of this cluster in a 24x32 array.
        @param   array The array to be shown, probably @c image
        @returns A set of coordinates pertaining to the hottest average cluster,
                 with the assumption that the array is 24x32.
        !"""
        cluster_temps = []
        for row in range(self._height - 1):
            for col in range(self._width - 3):
                cluster_temp = sum(array[row * self._width + col: row * self._width + col + 4]) / 4
                cluster_temps.append((cluster_temp, col, row))

        max_temp, x, y = max(cluster_temps)
        return [x, y]

    def hotspot_to_encoder_position(self, hotspot_location, total_hotspot_locations):
        """
        @brief   Convert hotspot location to encoder position.
        @param   hotspot_location Hotspot location
        @returns Encoder position
        !"""
        # Define the arrays for hotspot locations and corresponding encoder positions
        hotspots = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
        encoders = [-25475, -25648, -25822, -25995, -26169, -26343, -26516, -26690, -26864, -27037, -27211, -27385, -27558, -27732, -27906, -28079]
        
        # Check if the provided hotspot_location is within the range of hotspots
        if hotspot_location < hotspots[0] or hotspot_location > hotspots[-1]:
            return None  # Return None if hotspot_location is out of range
        
        # Find the index of the nearest hotspot_location in the hotspots array
        idx = hotspots.index(min(hotspots, key=lambda x: abs(x - hotspot_location)))
        
        # Return the corresponding encoder position
        return encoders[idx]

    def hotspot_to_encoder(self, hotspot_location):
        """
        @brief   Convert hotspot location to encoder position.
        @param   hotspot_location Hotspot location
        @returns Encoder position
        !"""
        total_hotspot_locations = self._width * (self._height - 1) * 3
        encoder_position_a = self.hotspot_to_encoder_position(hotspot_location, total_hotspot_locations)
        return encoder_position_a

if __name__ == "__main__":
    try:
        from pyb import info
    except ImportError:
        i2c_bus = I2C(1, scl=Pin(22), sda=Pin(21))
    else:
        i2c_bus = I2C(1)

    print("MXL90640 Easy(ish) Driver Test")

    i2c_address = 0x33
    scanhex = [f"0x{addr:X}" for addr in i2c_bus.scan()]
    print(f"I2C Scan: {scanhex}")

    camera = MLX_Cam(i2c_bus)

    while True:
        try:
            image = camera.get_image()
            camera.ascii_art(image)
            hot_spot = camera.find_hotSpot(image)
            print("Hottest spot coordinates:", hot_spot)
            encoder_position = camera.hotspot_to_encoder(hot_spot[0])
            print("Encoder Position:", encoder_position)
            time.sleep_ms(1000)

        except KeyboardInterrupt:
            break
