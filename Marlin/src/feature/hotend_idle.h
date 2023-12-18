/**
 * Marlin 3D Printer Firmware
 * Copyright (c) 2020 MarlinFirmware [https://github.com/MarlinFirmware/Marlin]
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
#pragma once

#include "../inc/MarlinConfig.h"

typedef struct {
  int16_t timeout, bed_timeout, trigger, nozzle_target;
  #if HAS_HEATED_BED
    int16_t bed_trigger, bed_target;
  #endif

  #ifndef BED_IDLE_TIMEOUT_SEC
    #define BED_IDLE_TIMEOUT_SEC HOTEND_IDLE_TIMEOUT_SEC
  #endif

  void set_defaults() {
    timeout       = HOTEND_IDLE_TIMEOUT_SEC;
    bed_timeout   = BED_IDLE_TIMEOUT_SEC;
    trigger       = HOTEND_IDLE_MIN_TRIGGER;
    nozzle_target = HOTEND_IDLE_NOZZLE_TARGET;
    bed_trigger   = BED_IDLE_MIN_TRIGGER;
    bed_target    = BED_IDLE_TARGET;
  }
} hotend_idle_settings_t;

class HotendIdleProtection {
public:
  static void check();
  static hotend_idle_settings_t cfg;
private:
  static millis_t next_protect_ms;
  static millis_t next_bed_protect_ms;
  static void check_hotends(const millis_t &ms);
  static void check_e_motion(const millis_t &ms);
  static void timed_out();
  static void bed_timed_out();
};

extern HotendIdleProtection hotend_idle;
