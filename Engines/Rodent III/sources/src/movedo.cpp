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

void POS::DoMove(int move, UNDO *u) {

  int sd = side;          // moving side
  int op = Opp(sd);       // side not to move
  int fsq = Fsq(move);    // start square
  int tsq = Tsq(move);    // target square
  int ftp = Tp(pc[fsq]);  // moving piece
  int ttp = Tp(pc[tsq]);  // captured piece

  // Save data for undoing a move

  u->ttp = ttp;
  u->c_flags = c_flags;
  u->ep_sq = ep_sq;
  u->rev_moves = rev_moves;
  u->hash_key = hash_key;
  u->pawn_key = pawn_key;

  // Update reversible moves counter

  rep_list[head++] = hash_key;
  if (ftp == P || ttp != NO_TP) rev_moves = 0;
  else                          rev_moves++;

  // Update pawn hash on pawn or king move

  if (ftp == P || ftp == K)
    pawn_key ^= zob_piece[Pc(sd, ftp)][fsq] ^ zob_piece[Pc(sd, ftp)][tsq];

  // Update castling rights

  hash_key ^= zob_castle[c_flags];
  c_flags &= castle_mask[fsq] & castle_mask[tsq];
  hash_key ^= zob_castle[c_flags];

  // Clear en passant square

  if (ep_sq != NO_SQ) {
    hash_key ^= zob_ep[File(ep_sq)];
    ep_sq = NO_SQ;
  }

  // Move own piece

  pc[fsq] = NO_PC;
  pc[tsq] = Pc(sd, ftp);
  hash_key ^= zob_piece[Pc(sd, ftp)][fsq] ^ zob_piece[Pc(sd, ftp)][tsq];
  cl_bb[sd] ^= SqBb(fsq) | SqBb(tsq);
  tp_bb[ftp] ^= SqBb(fsq) | SqBb(tsq);
  mg_sc[sd] += Par.mg_pst[sd][ftp][tsq] - Par.mg_pst[sd][ftp][fsq];
  eg_sc[sd] += Par.eg_pst[sd][ftp][tsq] - Par.eg_pst[sd][ftp][fsq];

  // Update king location

  if (ftp == K)
    king_sq[sd] = tsq;

  // Capture enemy piece

  if (ttp != NO_TP) {
    hash_key ^= zob_piece[Pc(op, ttp)][tsq];

    if (ttp == P)
      pawn_key ^= zob_piece[Pc(op, ttp)][tsq];

    cl_bb[op] ^= SqBb(tsq);
    tp_bb[ttp] ^= SqBb(tsq);
    mg_sc[op] -= Par.mg_pst[op][ttp][tsq];
    eg_sc[op] -= Par.eg_pst[op][ttp][tsq];
    phase -= ph_value[ttp];
    cnt[op][ttp]--;
  }

  switch (MoveType(move)) {
  case NORMAL:
    break;

  // Castling 

  case CASTLE:

    // define complementary rook move

    switch (tsq) {
      case C1: { fsq = A1; tsq = D1; break; }
      case G1: { fsq = H1; tsq = F1; break; }
      case C8: { fsq = A8; tsq = D8; break; }
      case G8: { fsq = H8; tsq = F8; break; }
    }

    pc[fsq] = NO_PC;
    pc[tsq] = Pc(sd, R);
    hash_key ^= zob_piece[Pc(sd, R)][fsq] ^ zob_piece[Pc(sd, R)][tsq];
    cl_bb[sd] ^= SqBb(fsq) | SqBb(tsq);
    tp_bb[R] ^= SqBb(fsq) | SqBb(tsq);
    mg_sc[sd] += Par.mg_pst[sd][R][tsq] - Par.mg_pst[sd][R][fsq];
    eg_sc[sd] += Par.eg_pst[sd][R][tsq] - Par.eg_pst[sd][R][fsq];
    break;

  // En passant capture

  case EP_CAP:
    tsq ^= 8;
    pc[tsq] = NO_PC;
    hash_key ^= zob_piece[Pc(op, P)][tsq];
    pawn_key ^= zob_piece[Pc(op, P)][tsq];
    cl_bb[op] ^= SqBb(tsq);
    tp_bb[P] ^= SqBb(tsq);
    mg_sc[op] -= Par.mg_pst[op][P][tsq];
    eg_sc[op] -= Par.eg_pst[op][P][tsq];
    phase -= ph_value[P];
    cnt[op][P]--;
    break;

  // Double pawn move

  case EP_SET:
    tsq ^= 8;
    if (BB.PawnAttacks(sd, tsq) & Pawns(op)) {
      ep_sq = tsq;
      hash_key ^= zob_ep[File(tsq)];
    }
    break;

  // Promotion

  case N_PROM: case B_PROM: case R_PROM: case Q_PROM:
    ftp = PromType(move);
    pc[tsq] = Pc(sd, ftp);
    hash_key ^= zob_piece[Pc(sd, P)][tsq] ^ zob_piece[Pc(sd, ftp)][tsq];
    pawn_key ^= zob_piece[Pc(sd, P)][tsq];
    tp_bb[P] ^= SqBb(tsq);
    tp_bb[ftp] ^= SqBb(tsq);
    mg_sc[sd] += Par.mg_pst[sd][ftp][tsq] - Par.mg_pst[sd][P][tsq];
    eg_sc[sd] += Par.eg_pst[sd][ftp][tsq] - Par.eg_pst[sd][P][tsq];
    phase += ph_value[ftp] - ph_value[P];
    cnt[sd][P]--;
    cnt[sd][ftp]++;
    break;
  }

  // Change side to move

  side ^= 1;
  hash_key ^= SIDE_RANDOM;
}

void POS::DoNull(UNDO *u) {

  u->ep_sq = ep_sq;
  u->hash_key = hash_key;
  rep_list[head++] = hash_key;
  rev_moves++;
  if (ep_sq != NO_SQ) {
    hash_key ^= zob_ep[File(ep_sq)];
    ep_sq = NO_SQ;
  }
  side ^= 1;
  hash_key ^= SIDE_RANDOM;
}
