/****************************************************************************
 *   Written By Brian Kahl 2023 - FAME3D.                                   *
 *                                                                          *
 *   This program is free software: you can redistribute it and/or modify   *
 *   it under the terms of the GNU General Public License as published by   *
 *   the Free Software Foundation, either version 3 of the License, or      *
 *   (at your option) any later version.                                    *
 *                                                                          *
 *   This program is distributed in the hope that it will be useful,        *
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of         *
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          *
 *   GNU General Public License for more details.                           *
 *                                                                          *
 *   To view a copy of the GNU General Public License, go to the following  *
 *   location: <http://www.gnu.org/licenses/>.                              *
 ****************************************************************************/

#include "../../../inc/MarlinConfig.h"

#if ENABLED(SHOW_TOOL_HEAD_ID)

#include "../../gcode.h"
#include "../../../feature/tool_head_id.h"
#include "../../../module/planner.h"
/**
 * M891: Set the Tool Head ID value.
 *
 *   T<Tool Head ID>     Set value of Tool Head Id (1 to 10)
 *
 * Type M891 without any arguments to show active value.
 */
void GcodeSuite::M891() {
  bool noArgs = true;

  if (parser.seen('T')) {
    planner.synchronize();
    tool_head.id = parser.value_linear_units();
    noArgs = false;
    }

  if (noArgs) {
    #if ENABLED(TOOLHEAD_Galaxy_Series)
      SERIAL_ECHOPGM("1=MET175 2=MET285 3=AST285");
    #elif ENABLED(TOOLHEAD_Legacy_Universal)
      SERIAL_ECHOPGM("1=M175 2=SL 3=SE 4=HE 5=HS 6=HS+ 7=H175");
    #endif
    SERIAL_ECHOLNPAIR("  Tool Head ID:", tool_head.id);
  }
}

void GcodeSuite::M891_report(const bool forReplay/*=true*/) {
  report_heading_etc(forReplay, F(STR_TOOLHEAD_ID));
  SERIAL_ECHOLNPGM_P(
    PSTR("  M891 T"), tool_head.id()
  );
}

#endif