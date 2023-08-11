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


# LDO-36STH20-1004AHG motor specs below

T = 21e-3                 # torque required to feed the filament at high speed
m = 1.6e-6 + 156e-9       # (kg m^2) moment of inertia of core
R = 2.1 + 1               # (Ω) resistance of each winding + Rdson of driver FETs
L = 1.6e-3                # (H) inductance of each winding
Vs = 12                   # (V) supply voltage
Ke = 2 * 0.1 / 1.414      # ratio of peak back EMF to shaft omega (for each coil)
steps = 200               # steps / rotation

# max speed for given acceleration
def v(a):
  I = (m * a + T) / Ke      # peak current (for each coil)
  Vl_f = 2 * pi * L * I     # peak voltage on inductor / two phase frequency
  Vb_f = Ke * 2 * pi / (steps / 4)   # peak back EMF / two phase frequency
  Vr = I * R                # peak voltage dropped through resistance
  f = (-Vr*Vb_f + ((Vr*Vb_f)**2 - (Vl_f**2 + Vb_f**2) * (Vr**2 - Vs**2))**0.5) / (Vl_f**2 + Vb_f**2)
  return f * 4 / steps * 2 * pi

accs = np.arange(2000, 4000.0, 1.0)

# plot the speeds possible at various accelerations
plt.plot(accs, v(accs), "r")
plt.show()
