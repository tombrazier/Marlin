#!/usr/bin/python3

import matplotlib.pyplot as plt
import numpy as np
from math import pi

# If f is the frequency of the sin waveform delivered by the stepper driver
# (i.e. f = step rate / 4) and Vs is the supply voltage (as a complex number)
# and R is the series resistance of the coil and Rdson and I (complex) is the
# current and Vb (complex) is the back EMF then at max torque angle of 90°:
#
# Vs = I*R + Vb + 2 * pi * f * L * I * j
#
# and at minimum torque angle of 0°:
#
# Vs = I*R + Vb * j + 2 * pi * f * L * I * j
#
# and using scalar magnitudes instead of complex numbers at 90° torque angle:
#
# Vs = sqrt((I*R + Vb)**2 + (2 * pi * f * L * I)**2)
#
# or, at 0° torque angle:
#
# Vs = sqrt((I*R)**2 + (Vb + 2 * pi * f * L * I)**2)


m = 1.175                 # (kg) mass of Y axis
Vs = 12                   # (V) supply voltage
R_fet = 0.34              # (Ω) Rdson of driver FETs
imargin = 0.2             # margin added to current to account for torque loss at speed

R_m = 7.4                 # (Ω) resistance of each winding
L = 16.3e-3               # (H) inductance of each winding
Ke = 6.1 / (2*pi*270/50)  # ratio of peak back EMF to shaft omega
steps = 200               # steps / rotation

# current, given acceleration and pulley radius
def i(a, r):
  I = 2 * a * r * m / Ke  # peak current
  return I

# max acceleration for given speed and pulley radius
def a(v, r):
  f = v / r / 2 / pi * steps / 4  # two phase frequency
  Vb = Ke * 2 * pi / 50 * f       # peak back EMF
  Xl = 2 * pi * f * L             # reactance of inductor
  R = R_m + R_fet                 # total series resistance
  # peak current
  I = (-R*Vb + (R**2 * Vb**2 - (R**2 + Xl**2)*(Vb**2 - Vs**2))**0.5) / (R**2 + Xl**2)
  I /= (1 + imargin)
  a = 0.5 * I / r / m * Ke        # acceleration
  return a

# plot the max acceleration vs various speeds at various pulley radii
rs = (("r", "5mm", 0.005), ("g", "7.5mm", 0.0075), ("b", "10mm", 0.010), ("m", "12.5mm", 0.0125))
vs = np.arange(10e-3, 500e-3, 1e-3)

fig, axs = plt.subplots(1, 2)
fig.set_size_inches(10, 5)

for colour, label, r in rs:
  axs[0].plot(vs * 1000, a(vs, r) * 1000, colour, label = label)
axs[0].set_ylabel("Max acceleration (mm/s/s)")
axs[0].set_xlabel("Speed (mm/s)")
axs[0].legend(title = "Pulley radius")

for colour, label, r in rs:
  axs[1].plot(vs * 1000, i(a(vs, r), r) * 0.5**0.5, colour, label = label)
axs[1].set_ylabel("RMS current (A)")
axs[1].set_xlabel("Speed (mm/s)")
axs[1].legend(title = "Pulley radius")

plt.show()
