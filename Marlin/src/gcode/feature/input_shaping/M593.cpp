/**
 * Marlin 3D Printer Firmware
 * Copyright (c) 2022 MarlinFirmware [https://github.com/MarlinFirmware/Marlin]
 *
 * Based on Sprinter and grbl.
 * Copyright (c) 2011 Camiel Gubbels / Erik van der Zalm
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 *
 */

#include "../../../inc/MarlinConfig.h"

#if ENABLED(INPUT_SHAPING)

#include "../../gcode.h"
#include "../../../module/stepper.h"

/**
 * M593: Get or Set Input Shaping Parameters
 *  D<factor>    Set the zeta/damping factor. If axes (X, Y, etc.) are not specified, set for all axes.
 *  F<frequency> Set the frequency. If axes (X, Y, etc.) are not specified, set for all axes.
 *  T[map]       Input Shaping type, 0:ZV, 1:EI, 2:2H EI (not implemented yet)
 *  X<1>         Set the given parameters only for the X axis.
 *  Y<1>         Set the given parameters only for the Y axis.
 */
void GcodeSuite::M593() {
  const bool seen_X = parser.seen('X'),
             for_X = seen_X ? parser.value_bool() : false;
  const bool seen_Y = parser.seen('Y'),
             for_Y = seen_Y ? parser.value_bool() : false;

  if (parser.seen('D')) {
    const float zeta = parser.value_float();
    if (WITHIN(zeta, 0, 1)) {
      if (for_X || (!for_X && !for_Y)) stepper.set_shaping_damping_ratio(X_AXIS, zeta);
      if (for_Y || (!for_X && !for_Y)) stepper.set_shaping_damping_ratio(Y_AXIS, zeta);
    } else {
      SERIAL_ECHO_START();
      SERIAL_ECHOLNPGM("Zeta (D) value out of range (0-1)");
    }
  }

  if (parser.seen('F')) {
    const float freq = parser.value_float();
    if (freq <= 0) {
      SERIAL_ECHO_START();
      SERIAL_ECHOLNPGM("Frequency (F) must be greater than 0");
    } else {
      if (for_X || (!for_X && !for_Y)) stepper.set_shaping_frequency(X_AXIS, freq);
      if (for_Y || (!for_X && !for_Y)) stepper.set_shaping_frequency(Y_AXIS, freq);
    }
  }

  if (!parser.seen_any()) {
    SERIAL_ECHO_START();
    SERIAL_ECHOLNPGM("Input Shaping:");
    #if HAS_SHAPING_X
      SERIAL_ECHO_START();
      SERIAL_ECHOLNPGM("  X axis: M593 X F", stepper.get_shaping_frequency(X_AXIS),
        " D", stepper.get_shaping_damping_ratio(X_AXIS));
    #endif
    #if HAS_SHAPING_Y
      SERIAL_ECHO_START();
      SERIAL_ECHOLNPGM("  Y axis: M593 Y F", stepper.get_shaping_frequency(Y_AXIS),
        " D", stepper.get_shaping_damping_ratio(Y_AXIS));
    #endif
  }

}


#endif // INPUT_SHAPING