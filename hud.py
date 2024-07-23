# Write your code here :-)
#
# Play a single animated GIF file (display_bus "fast" method)
#
# Documentation:
#   https://docs.circuitpython.org/en/latest/shared-bindings/gifio/
# Updated 4/5/2023

import time
import gc
import board
import gifio
import digitalio
import displayio
import terminalio
import busio
import gc9a01
import struct

# Release any resources currently in use for the displays
displayio.release_displays()



tft_clk  = board.SCK
tft_mosi = board.MOSI
tft_rst  = board.TX
tft_dc   = board.RX
tft_cs   = board.A3
tft_bl   = board.A2
spi = busio.SPI(clock=tft_clk, MOSI=tft_mosi)


# Make the displayio SPI bus and the GC9A01 display
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_rst)
display = gc9a01.GC9A01(display_bus, width=240, height=240, rotation=90, backlight_pin=tft_bl)

splash = displayio.Group()
display.root_group = splash

# Set BOOT button on ESP32-S2 Feather TFT to stop GIF
button = digitalio.DigitalInOut(board.BUTTON)
button.switch_to_input(pull=digitalio.Pull.UP)

# Open GIF file sample.gif
odg = gifio.OnDiskGif('/33.gif')

start = time.monotonic()
next_delay = odg.next_frame()  # Load the first frame
end = time.monotonic()
overhead = end - start

face = displayio.TileGrid(
    odg.bitmap,
    pixel_shader=displayio.ColorConverter(
        input_colorspace=displayio.Colorspace.RGB565_SWAPPED
    ),
)
splash.append(face)
display.refresh()

display.auto_refresh = False
display_bus = display.bus

# Backlight function
# Value between 0 and 1 where 0 is OFF, 0.5 is 50% and 1 is 100% brightness.
def set_backlight(val):
    val = max(0, min(1.0, val))
    display.auto_brightness = False
    display.brightness = val

# Display repeatedly & directly.
while True:
    set_backlight(1.0)
    # Sleep for the frame delay specified by the GIF,
    # minus the overhead measured to advance between frames.
    time.sleep(max(0, next_delay - overhead))
    next_delay = odg.next_frame()

    display_bus.send(42, struct.pack(">hh", 0, odg.bitmap.width - 1))
    display_bus.send(43, struct.pack(">hh", 0, odg.bitmap.height - 1))
    display_bus.send(44, odg.bitmap)

# The following optional code will free the OnDiskGif and allocated resources
# after use. This may be required before loading a new GIF in situations
# where RAM is limited and the first GIF took most of the RAM.
odg.deinit()
odg = None
gc.collect()
