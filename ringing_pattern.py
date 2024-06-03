#!/usr/bin/python3

"""
This script generates gcode for one of three patterns to tune input shaping. Each pattern
performs a number of frequency scans, starting from 0Hz and going up to some maximum (default
60Hz). A frequency scan is a zig-zag line which is drawn at steadily increasing speed.

Horizontal lines are oscillating in the Y direction. e.g.

  ^^^^^^^^^^^^^^^^^^^^

And vertical lines are oscillating in the X direction. e.g.

  >
  >
  >
  >
  >
  >
  >
  >

Don't get them confused! You read X frequencies off the vertical lines and Y frequencies off
the horizontal line.

At the resonant frequency, the oscillations become noticeably larger and there may even
be layer shifts. If this is a problem, reduce the value of the amplitude variable.

The "freq" pattern draws one frequency scan for Y and then one for X. Measure from the start of
the line to where the oscillations are worst. Divide distance in mm by wavelength (default 2)
to get the frequency.

The "zeta_x" and "zeta_y" patterns draw a series of frequency scans all in one direction. The
zeta value increases by 0.05 for every frequency scan drawn, starting with a value of 0.05.
Find the line which has the most uniform amplitude of oscillation across the whole line. This
gives you the X or Y zeta value.
"""

### Parameters for generating the gcode

layer_height = 0.3          # (mm)
line_width = 0.5            # (mm)
filament_dia = 1.75         # (mm)
nozzle_temp = 220           # °C
bed_temp = 50               # °C

z_speed = 10.0              # (mm/s) Z movement speed
travel_speed = 100.0        # (mm/s) speed for travel moves
anchor_line_speed = 40.0    # (mm/s) speed for start line

wavelength = 2.0            # (mm) the width of one ful zig-zag
amplitude = 0.5             # (mm) the peak to peak size of the zig-zag pattern
top_freq = 60               # (Hz) the frequency scans from 0Hz to this value
decel = 1000                # (mm/s^2) rate of deceleration at the end of the pattern

pattern_type = "freq_z"       # choose one of "freq_x", "freq_y", "freq_z", "zeta_x", "zeta_y" or "zeta_z"


### Start of the script proper

from math import pi
from math import sin

filament_flow_ratio = layer_height * line_width / (pi * filament_dia*filament_dia / 4)

x = 0.0
y = 0.0
z = 0.0
e = 0.0

def go_to(new_x, new_y, new_z, f = None):
  global x, y, z, e
  x = new_x
  y = new_y
  z = new_z
  line = "G0 X%.2f Y%.2f Z%.2f E%.2f" % (x, y, z, e)
  if f is not None: line += " F%.1f" % (f * 60)
  print(line)

def line_to(new_x, new_y, new_z, f = None):
  global x, y, z, e
  e += filament_flow_ratio * ((new_x - x)**2 + (new_y - y)**2 + (new_z - z)**2)**0.5
  x = new_x
  y = new_y
  z = new_z
  line = "G1 X%.2f Y%.2f Z%.2f E%.2f" % (x, y, z, e)
  if f is not None: line += " F%.1f" % (f * 60)
  print(line)

# default settings
print("M501")
print()

# settings for the print
print("M205 S0 T0           ; minimum extruding and travel feed rate")
if pattern_type[:4] == "freq":
  print("M593 F0              ; input shaping off")
print("M900 K0              ; linear advance off")
print("G90                  ; absolute positioning")
print()

# heating and cooling
print("M107                 ; fan off")
print("M140 S%d             ; bed temperature" % bed_temp)
print("M104 S%d             ; head temperature" % nozzle_temp)
print()

# home and reset extruder pos
print("G28                  ; home")
print("G92 E0")
print()

# wait for temperatures
print("M190 S%d             ; bed temperature" % bed_temp)
print("M109 S%d             ; head temperature" % nozzle_temp)
print()

# level bed
print("G29                  ; level bed")
print()

# draw anchor lines
go_to(150.0, 150.0, 2.0, travel_speed)
go_to(x, y, layer_height, z_speed)
line_to(20.0, 150.0, z, anchor_line_speed)
line_to(20.0, 20.0, z, anchor_line_speed)

# remove lots of limits
print("M203 X500 Y500 Z500  ; maximum feedrates")
print("M204 P10000          ; print acceleration")
print("M205 X500 Y500 Z500  ; jerk limits very high")
print("M205 J0.3            ; junction deviation maximum")
print()

# generate accelerating zigzag and end coast patterns
zigzags = []
seg_length = (amplitude**2 + wavelength**2 / 4.0)**0.5
f = 0
for i in range(top_freq):
  zigzags.append((wavelength * (i + 0.5), amplitude, seg_length * 2 * (i + 0.5)))
  zigzags.append((wavelength * (i + 1.0), 0,         seg_length * 2 * (i + 1.0)))

max_x_speed = wavelength * top_freq
coast_dist = max_x_speed**2 / 2 / decel

def draw_z_zigzags(zigzags, coast_dist):
  print("M201 X10000 Z10000")

  start_x = x
  start_z = z
  for x_offs, z_offs, f in zigzags:
    line_to(start_x + x_offs, y, start_z + z_offs, f)

  # go back to resonable acceleration limits
  print("M201 X%d Z%d" % (decel, decel))

  # coast down to stop
  line_to(x + coast_dist, y, z)

  print()

def draw_z_zigzags_rev(zigzags, coast_dist):
  # ramp up to speed
  line_to(x - coast_dist, y, z, zigzags[-1][2])

  print("M201 X10000 Z10000")

  start_x = x - zigzags[-1][0]
  start_z = z - zigzags[-1][1]
  x_offsets, z_offsets, fs = zip(*zigzags)
  x_offsets = ((0,) + x_offsets)[:-1]
  z_offsets = ((0,) + z_offsets)[:-1]
  zigzags = reversed(list(zip(x_offsets, z_offsets, fs)))
  for x_offs, z_offs, f in zigzags:
    line_to(start_x + x_offs, y, start_z + z_offs, f)

  # go back to resonable acceleration limits
  print("M201 X%d Z%d" % (decel, decel))

  print()

def draw_y_zigzags(zigzags, coast_dist):
  print("M201 X10000 Y10000")

  start_x = x
  start_y = y
  for x_offs, y_offs, f in zigzags:
    line_to(start_x + x_offs, start_y + y_offs, z, f)

  # go back to resonable acceleration limits
  print("M201 X%d Y%d" % (decel, decel))

  # coast down to stop
  line_to(x + coast_dist, y, z)

  print()

def draw_y_zigzags_rev(zigzags, coast_dist):
  # ramp up to speed
  line_to(x - coast_dist, y, z, zigzags[-1][2])

  print("M201 X10000 Y10000")

  start_x = x - zigzags[-1][0]
  start_y = y - zigzags[-1][1]
  x_offsets, y_offsets, fs = zip(*zigzags)
  x_offsets = ((0,) + x_offsets)[:-1]
  y_offsets = ((0,) + y_offsets)[:-1]
  zigzags = reversed(list(zip(x_offsets, y_offsets, fs)))
  for x_offs, y_offs, f in zigzags:
    line_to(start_x + x_offs, start_y + y_offs, z, f)

  # go back to resonable acceleration limits
  print("M201 X%d Y%d" % (decel, decel))

  print()

def draw_x_zigzags(zigzags, coast_dist):
  print("M201 X10000 Y10000")

  start_x = x
  start_y = y
  for y_offs, x_offs, f in zigzags:
    line_to(start_x + x_offs, start_y + y_offs, z, f)

  # go back to resonable acceleration limits
  print("M201 X%d Y%d" % (decel, decel))

  # coast down to stop
  line_to(x, y + coast_dist, z)

  print()

def draw_x_zigzags_rev(zigzags, coast_dist):
  # ramp up to speed
  line_to(x, y - coast_dist, z, zigzags[-1][2])

  print("M201 X10000 Y10000")

  start_x = x - zigzags[-1][1]
  start_y = y - zigzags[-1][0]
  y_offsets, x_offsets, fs = zip(*zigzags)
  x_offsets = ((0,) + x_offsets)[:-1]
  y_offsets = ((0,) + y_offsets)[:-1]
  zigzags = reversed(list(zip(y_offsets, x_offsets, fs)))
  for y_offs, x_offs, f in zigzags:
    line_to(start_x + x_offs, start_y + y_offs, z, f)

  # go back to resonable acceleration limits
  print("M201 X%d Y%d" % (decel, decel))

  print()

if pattern_type == "freq_z":
  # draw Z zigzags at constant X acceleration
  draw_z_zigzags(zigzags, coast_dist)

if pattern_type == "freq_y":
  # draw Y zigzags at constant X acceleration
  draw_y_zigzags(zigzags, coast_dist)

if pattern_type == "freq_x":
  # move a little away from the anchor line
  line_to(x + 5, y, z)

  # draw X zigzags at constant Y acceleration
  draw_x_zigzags(zigzags, coast_dist)

if pattern_type == "zeta_z":
  # move a little away from the anchor line
  line_to(x + 5, y, z)

  # draw alternating Z zigzags at constant X acceleration
  zeta = 0.0
  for i in range(10):
    zeta += 0.05
    print("M593 Z D%.2f" % zeta)
    draw_z_zigzags(zigzags, coast_dist)
    go_to(x, y + 5, z, travel_speed)
    zeta += 0.05
    print("M593 Z D%.2f" % zeta)
    draw_z_zigzags_rev(zigzags, coast_dist)
    go_to(x, y + 5, z, travel_speed)

if pattern_type == "zeta_y":
  # move a little away from the anchor line
  line_to(x + 5, y, z)

  # draw alternating Y zigzags at constant X acceleration
  zeta = 0.0
  for i in range(10):
    zeta += 0.05
    print("M593 Y D%.2f" % zeta)
    draw_y_zigzags(zigzags, coast_dist)
    go_to(x, y + 5, z, travel_speed)
    zeta += 0.05
    print("M593 Y D%.2f" % zeta)
    draw_y_zigzags_rev(zigzags, coast_dist)
    go_to(x, y + 5, z, travel_speed)

if pattern_type == "zeta_x":
  # move a little away from the anchor line
  line_to(x + 5, y, z)

  # draw alternating X zigzags at constant Y acceleration
  zeta = 0.0
  for i in range(10):
    zeta += 0.05
    print("M593 X D%.2f" % zeta)
    draw_x_zigzags(zigzags, coast_dist)
    go_to(x + 5, y, z, travel_speed)
    zeta += 0.05
    print("M593 X D%.2f" % zeta)
    draw_x_zigzags_rev(zigzags, coast_dist)
    go_to(x + 5, y, z, travel_speed)

# lift head
go_to(x, y, 2.0, z_speed)
print()

# heaters off and clean up
print("M140 S 0             ; bed temperature")
print("M104 S0              ; head temperature")
print("G92 E0")
print()

# default settings
print("M501")
