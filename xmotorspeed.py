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



m = 0.36                  # (kg) mass of X axis
R = 8                     # (Ω) resistance of each winding + Rdson of driver FETs
L = 16.6e-3               # (H) inductance of each winding
Vs = 12                   # (V) supply voltage
Ke = 12.1 / (2*pi*461.33/50)  # ratio of peak back EMF to shaft omega
steps = 200               # steps / rotation

# max speed for given acceleration and shaft radius
def v(a, r):
  I = r * m * a / Ke                # peak current
  Vl_f = 2 * pi * L * I             # peak voltage on inductor / two phase frequency
  Vb_f = Ke * 2 * pi / (steps / 4)  # peak back EMF / two phase frequency
  Vr = I * R                        # peak voltage dropped through resistance
  f = (-Vr*Vb_f + ((Vr*Vb_f)**2 - (Vl_f**2 + Vb_f**2) * (Vr**2 - Vs**2))**0.5) / (Vl_f**2 + Vb_f**2)
  return f * 4 / steps * 2 * pi * r

# max acceleration for given speed and shaft radius
def a(v, r):
  f = v / r / 2 / pi * steps / 4  # two phase frequency
  Vb = Ke * 2 * pi / 50 * f       # peak back EMF
  Xl = 2 * pi * f * L             # reactance of inductor
  # peak current
  I = (-R*Vb + (R**2 * Vb**2 - (R**2 + Xl**2)*(Vb**2 - Vs**2))**0.5) / (R**2 + Xl**2)
  a = I / r / m * Ke              # acceleration
  return a

rs = np.arange(1e-3, 50e-3, 1e-3)

# plot the speeds possible at various accelerations and pulley radii
plt.plot(rs, v(5, rs), "r", rs, v(10, rs), "g", rs, v(15, rs), "b")
plt.show()

# plot the accelerations possible at various speeds and pulley radii
plt.plot(rs, a(0.25, rs), "r", rs, a(0.35, rs), "g", rs, a(0.45, rs), "b")
plt.show()
