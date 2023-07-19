#!/usr/bin/python3

from sys import argv
import os
import re

EPSILON = 1.0e-6
TRANSITION_LENGTH = 0.5
PERIM_END_GAP = 0.1
SEAM_WIDTH_FACTOR = 0.5

fname = argv[1]

inf = open(fname, "rt")
outf = open(fname + ".out", "wt")

def lerp(alpha, x0, x1):
  return alpha * (x1 - x0) + x0

def writeg1(outf, x, y, e):
  x = f"{x:.3f}".strip("0")
  if x == ".": x = "0"
  y = f"{y:.3f}".strip("0")
  if y == ".": y = "0"
  e = f"{e:.5f}".strip("0")
  if e == ".": e = "0"
  outf.write(f"G1 X{x} Y{y} E{e}\n")

section_type = None
last_pos = (0.0, 0.0, 0.0, 0.0)
perim_lines = None
perim_start = None
perim_e = None
perim_dist = None
perim_transition = None
perim_moves = None
for line in inf:
  old_section_type = section_type
  if re.match(";TYPE:", line):
    section_type = line[6:].strip()

  g1line = None
  if re.match("G[01][^0-9]+", line):
    x, y, z, e = last_pos
    fr = None
    m = re.search("X[\+\-0-9\.]+", line)
    if m: x = float(m.group()[1:])
    m = re.search("Y[\+\-0-9\.]+", line)
    if m: y = float(m.group()[1:])
    m = re.search("Z[\+\-0-9\.]+", line)
    if m: z = float(m.group()[1:])
    m = re.search("E[\+\-0-9\.]+", line)
    if m: e = float(m.group()[1:])
    m = re.search("F[\+\-0-9\.]+", line)
    if m: fr = float(m.group()[1:])

    dist = ((x - last_pos[0])**2 + (y - last_pos[1])**2)**0.5
    dz = z - last_pos[2]
    de = e - last_pos[3]
    g1line = (last_pos, (x, y, z, e), fr, dist, dz, de)
    last_pos = (x, y, z, e)

  if re.match("G92[^0-9]+", line):
    assert(re.match("G92 E[\+\-0-9\.]+ *;*", line))
    m = re.search("E[\+\-0-9\.]+", line)
    e = float(m.group()[1:])
    last_pos = last_pos[:3] + (e,)

  abandon_perim = perim_lines is not None

  # a short travel movement that is not a Z movement is the first line of interest for external perimeters
  if perim_lines is None and g1line is not None and g1line[-3] > EPSILON and g1line[-3] < 1.0 and abs(g1line[-2]) < EPSILON and abs(g1line[-1]) < EPSILON:
    perim_lines = [line]
    line = None
    perim_start = g1line[1]
    perim_e = 0.0
    perim_dist = 0.0
    perim_moves = []

  # the second interesting line is a transition from type Perimeter to External perimeter
  elif perim_lines and len(perim_lines) == 1 and old_section_type == "Perimeter" and section_type == "External perimeter":
    abandon_perim = False
    perim_lines.append(line)
    line = None

  # the third interesting line is a "G1 F" line
  elif perim_lines and len(perim_lines) == 2 and g1line is not None and g1line[-3] < EPSILON and abs(g1line[-2]) < EPSILON and abs(g1line[-1]) < EPSILON and g1line[2] is not None:
    abandon_perim = False
    perim_lines.append(line)
    line = None

  # the perimeter continues with only G1 print moves until the the print head is close to the start position and a travel move occurs
  elif perim_lines and len(perim_lines) > 2 and g1line is not None:
    old_pos, new_pos, fr, dist, dz, de = g1line

    # there should be no further changes to feedrate and all moves should have distance
    assert(dist > EPSILON)
    assert(abs(dz) < EPSILON)

    # print move - so record it, tracking the transition section
    if fr is None and abs(de) > EPSILON:
      abandon_perim = False
      perim_lines.append(line)
      line = None

      # has the transition distance been reached?
      perim_e += de
      old_perim_dist = perim_dist
      perim_dist += dist
      if perim_transition is None and perim_dist >= TRANSITION_LENGTH:
        split = min(1.0, (TRANSITION_LENGTH - old_perim_dist) / dist)
        split_pos = (lerp(split, new_pos[0], old_pos[0]), lerp(split, new_pos[1], old_pos[1]), lerp(split, new_pos[2], old_pos[2]))
        perim_moves.append(split_pos + (split * de,))
        perim_transition = len(perim_moves)
        if split < 1.0:
          perim_moves.append(new_pos[:3] + (de * (1.0 - split),))
      else:
        perim_moves.append(new_pos[:3] + (de,))

    # travel move
    else:
      # confirm that we're back at the starting point and that we did actually pass the transition point, otherwise abandon
      dist_from_start = ((old_pos[0] - perim_start[0])**2 + (old_pos[1] - perim_start[1])**2)**0.5
      assert(dist_from_start < PERIM_END_GAP)
      if dist_from_start < PERIM_END_GAP and perim_transition is not None:
        abandon_perim = False

        # first output the TYPE and G1 F lines
        outf.write(perim_lines[1])
        outf.write(perim_lines[2])
        # then output a replacement seam travel move - but make it a print move
        writeg1(outf, *perim_moves[perim_transition-1][:2], perim_start[3] + SEAM_WIDTH_FACTOR * perim_e / perim_dist * TRANSITION_LENGTH)
        # then a G92 E
        e = perim_start[3] + sum(move[3] for move in perim_moves[:perim_transition])
        outf.write("G92 E%.5f\n" % e)
        # then all the movements after the transition
        for movement in perim_moves[perim_transition:]:
          e += movement[3]
          writeg1(outf, *movement[:2], e)
        # then the movements before the transition
        for movement in perim_moves[:perim_transition]:
          e += movement[3]
          writeg1(outf, *movement[:2], e)
        # then a G92 to get back in sync with the original gcode
        outf.write("G92 E%.5f\n" % (perim_start[3] + perim_e))

        # end recording, etc.
        perim_lines = None
        perim_start = None
        perim_e = None
        perim_dist = None
        perim_transition = None
        perim_moves = None

  if abandon_perim:
    for perim_line in perim_lines[0]:
      outf.write(perim_line)
    perim_lines = None
    perim_start = None
    perim_e = None
    perim_dist = None
    perim_transition = None
    perim_moves = None

  if line is not None:
    outf.write(line)

# output the lines of any incomplete perimeter
if perim_lines is not None:
  for perim_line in perim_lines[0]:
    outf.write(perim_line)

os.unlink(fname)
os.rename(fname + ".out", fname)
