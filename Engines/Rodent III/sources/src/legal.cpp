/*
Rodent, a UCI chess playing engine derived from Sungorus 1.4
Copyright (C) 2009-2011 Pablo Vazquez (Sungorus author)
Copyright (C) 2011-2017 Pawel Koziol

Rodent is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

Rodent is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.
If not, see <http://www.gnu.org/licenses/>.
*/

#include "rodent.h"

int Legal(POS *p, int move) {

  int sd = p->side;
  int fsq = Fsq(move);
  int tsq = Tsq(move);
  int ftp = TpOnSq(p, fsq);
  int ttp = TpOnSq(p, tsq);

  if (ftp == NO_TP || Cl(p->pc[fsq]) != sd)
    return 0;
  if (ttp != NO_TP && Cl(p->pc[tsq]) == sd)
    return 0;
  switch (MoveType(move)) {
  case NORMAL:
    break;
  case CASTLE:
    if (sd == WC) {
      if (fsq != E1)
        return 0;
      if (tsq > fsq) {
        if ((p->c_flags & 1) && !(OccBb(p) & (U64)0x0000000000000060))
          if (!Attacked(p, E1, BC) && !Attacked(p, F1, BC))
            return 1;
      } else {
        if ((p->c_flags & 2) && !(OccBb(p) & (U64)0x000000000000000E))
          if (!Attacked(p, E1, BC) && !Attacked(p, D1, BC))
            return 1;
      }
    } else {
      if (fsq != E8)
        return 0;
      if (tsq > fsq) {
        if ((p->c_flags & 4) && !(OccBb(p) & (U64)0x6000000000000000))
          if (!Attacked(p, E8, WC) && !Attacked(p, F8, WC))
            return 1;
      } else {
        if ((p->c_flags & 8) && !(OccBb(p) & (U64)0x0E00000000000000))
          if (!Attacked(p, E8, WC) && !Attacked(p, D8, WC))
            return 1;
      }
    }
    return 0;
  case EP_CAP:
    if (ftp == P && tsq == p->ep_sq)
      return 1;
    return 0;
  case EP_SET:
    if (ftp == P && ttp == NO_TP && p->pc[tsq ^ 8] == NO_PC)
      if ((tsq > fsq && sd == WC) ||
          (tsq < fsq && sd == BC))
        return 1;
    return 0;
  }

  if (ftp == P) {
    if (sd == WC) {
      if (Rank(fsq) == RANK_7 && !IsProm(move))
        return 0;
      if (tsq - fsq == 8)
        if (ttp == NO_TP)
          return 1;
      if ((tsq - fsq == 7 && File(fsq) != FILE_A) ||
          (tsq - fsq == 9 && File(fsq) != FILE_H))
        if (ttp != NO_TP)
          return 1;
    } else {
      if (Rank(fsq) == RANK_2 && !IsProm(move))
        return 0;
      if (tsq - fsq == -8)
        if (ttp == NO_TP)
          return 1;
      if ((tsq - fsq == -9 && File(fsq) != FILE_A) ||
          (tsq - fsq == -7 && File(fsq) != FILE_H))
        if (ttp != NO_TP)
          return 1;
    }
    return 0;
  }

  if (IsProm(move))
    return 0;

  return (AttacksFrom(p, fsq) & SqBb(tsq)) != 0;
}
