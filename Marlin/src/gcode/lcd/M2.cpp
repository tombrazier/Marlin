/**
 * Written By Brian Kahl 2023 - FAME3D
 *
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

#include "../../inc/MarlinConfigPre.h"

#if HAS_END_PRINT_SCREEN

#include "../../inc/MarlinConfig.h"
#include "../gcode.h"


#if ENABLED(EXTENSIBLE_UI)
  #include "../../lcd/extui/ui_api.h"
#endif

/**
 * M2: Go to end print screen
 */
void GcodeSuite::M2() {

  #if ENABLED(EXTENSIBLE_UI)
    if (parser.string_arg)
      ExtUI::onPrintCompleteScreen(parser.string_arg); // String in an SRAM buffer
    else
      ExtUI::onPrintCompleteScreen(GET_TEXT_F(MSG_USERWAIT));
  #endif

}

#endif // HAS_END_PRINT_SCREEN