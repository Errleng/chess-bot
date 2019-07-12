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
#include <math.h>

// QuiescenceChecks() allows the engine to consider most of the checking moves
// as well as special quiet moves (hash and killers). It improves engines'
// tactical awareness near the leaves and after a null move.

int cEngine::QuiesceChecks(POS *p, int ply, int alpha, int beta, int *pv) {

  int best, score, move, new_pv[MAX_PLY];
  int mv_type, fl_check;
  int is_pv = (alpha != beta - 1);
  MOVES m[1];
  UNDO u[1];
  eData e;

  if (InCheck(p)) return QuiesceFlee(p, ply, alpha, beta, pv);

  // EARLY EXIT AND NODE INITIALIZATION

  Glob.nodes++;
  local_nodes++;
  Slowdown();
  if (Glob.abort_search && root_depth > 1) return 0;
  *pv = 0;
  if (IsDraw(p) && ply) return DrawScore(p);
  move = 0;

  best = EvalScaleByDepth(p, ply, Evaluate(p, &e));
  if (best >= beta) return best;
  if (best > alpha) alpha = best;

  // RETRIEVE MOVE FROM TRANSPOSITION TABLE

  if (TransRetrieve(p->hash_key, &move, &score, alpha, beta, 0, ply)) {
    if (score >= beta) UpdateHistory(p, -1, move, 1, ply);
    if (!is_pv) return score;
  }

  // SAFEGUARD AGAINST REACHING MAX PLY LIMIT

  if (ply >= MAX_PLY - 1) return EvalScaleByDepth(p, ply, Evaluate(p, &e));

  fl_check = InCheck(p);

  // PREPARE FOR SEARCH

  InitMoves(p, m, move, -1, -1, ply);

  // MAIN LOOP

  while ((move = NextSpecialMove(m, &mv_type))) {

    // MAKE MOVE    

    p->DoMove(move, u);
    if (Illegal(p)) { p->UndoMove(move, u); continue; }

    score = -Quiesce(p, ply + 1, -beta, -alpha, new_pv);

    // UNDO MOVE

    p->UndoMove(move, u);
    if (Glob.abort_search && root_depth > 1) return 0;

    // BETA CUTOFF

    if (score >= beta) {
      TransStore(p->hash_key, move, score, LOWER, 0, ply);
      return score;
    }

    // NEW BEST MOVE

    if (score > best) {
      best = score;
      if (score > alpha) {
        alpha = score;
        BuildPv(pv, new_pv, move);
      }
    }

  } // end of main loop

  // RETURN CORRECT CHECKMATE/STALEMATE SCORE
  
  if (best == -INF)
    return InCheck(p) ? -MATE + ply : 0;

  // SAVE RESULT IN THE TRANSPOSITION TABLE

  if (*pv) TransStore(p->hash_key, *pv, best, EXACT, 0, ply);
  else     TransStore(p->hash_key,   0, best, UPPER, 0, ply);

  return best;
}

int cEngine::QuiesceFlee(POS *p, int ply, int alpha, int beta, int *pv) {

  int best, score, move, new_pv[MAX_PLY];
  int mv_type, fl_check;
  int is_pv = (alpha != beta - 1);
  MOVES m[1];
  UNDO u[1];
  eData e;

  // EARLY EXIT AND NODE INITIALIZATION

  Glob.nodes++;
  local_nodes++;
  Slowdown();
  if (Glob.abort_search && root_depth > 1) return 0;
  *pv = 0;
  if (IsDraw(p) && ply) return DrawScore(p);
  move = 0;

  // RETRIEVE MOVE FROM TRANSPOSITION TABLE

  if (TransRetrieve(p->hash_key, &move, &score, alpha, beta, 0, ply)) {
    if (score >= beta) UpdateHistory(p, -1, move, 1, ply);
    if (!is_pv) return score;
  }

  // SAFEGUARD AGAINST REACHING MAX PLY LIMIT

  if (ply >= MAX_PLY - 1) return EvalScaleByDepth(p, ply, Evaluate(p, &e));

  fl_check = InCheck(p);

  // PREPARE FOR MAIN SEARCH

  best = -INF;
  InitMoves(p, m, move, -1, -1, ply);

  // MAIN LOOP

  while ((move = NextMove(m, &mv_type))) {

    // MAKE MOVE    

    p->DoMove(move, u);
    if (Illegal(p)) { p->UndoMove(move, u); continue; }

    score = -Quiesce(p, ply + 1, -beta, -alpha, new_pv);

    // UNDO MOVE

    p->UndoMove(move, u);
    if (Glob.abort_search && root_depth > 1) return 0;

    // BETA CUTOFF

    if (score >= beta) {
      TransStore(p->hash_key, move, score, LOWER, 0, ply);
      return score;
    }

    // NEW BEST MOVE

    if (score > best) {
      best = score;
      if (score > alpha) {
        alpha = score;
        BuildPv(pv, new_pv, move);
      }
    }

  } // end of main loop

  // RETURN CORRECT CHECKMATE/STALEMATE SCORE
  
  if (best == -INF)
    return InCheck(p) ? -MATE + ply : DrawScore(p);

  // SAVE RESULT IN THE TRANSPOSITION TABLE

  if (*pv) TransStore(p->hash_key, *pv, best, EXACT, 0, ply);
  else     TransStore(p->hash_key,   0, best, UPPER, 0, ply);

  return best;
}

int cEngine::Quiesce(POS *p, int ply, int alpha, int beta, int *pv) {

  int best, score, move, new_pv[MAX_PLY];
  int op = Opp(p->side);
  MOVES m[1];
  UNDO u[1];
  eData e;

  // USE DEDICATED EVASION SEARCH WHEN IN CHECK

  if (InCheck(p)) return QuiesceFlee(p, ply, alpha, beta, pv);

  Glob.nodes++;
  local_nodes++;
  Slowdown();

  // EARLY EXIT

  if (Glob.abort_search && root_depth > 1) return 0;
  *pv = 0;
  if (IsDraw(p)) return DrawScore(p);

  // SAFEGUARD AGAINST HITTIMG MAX PLY LIMIT

  if (ply >= MAX_PLY - 1) return EvalScaleByDepth(p, ply, Evaluate(p, &e));

  // GET STAND PAT SCORE

  best = EvalScaleByDepth(p, ply, Evaluate(p, &e));

  // CORRECTION OF SCORE FOR OWN SIDE IN RISKY MODE (Roman T. Sovanyan)

  if ((Par.riskydepth > 0) 
  && (ply >= Par.riskydepth) 
  && (p->side == Par.prog_side) 
  && (Abs(best) > 100) && (Abs(best) < 1000)) {
    int eval_adj = best<0 ? round(1.0*best*(Glob.nodes > 100 ? 0.5 : 1)*Par.riskydepth / ply) : round(1.0*best*(Glob.nodes > 100 ? 2 : 1)*ply / Par.riskydepth);
    if (eval_adj>1000) eval_adj = 1000;
    best = eval_adj;
  }

  // SET VARIABLES FOR DELTA PRUNING, EXIT IF STAND PAT SCORE ABOVE BETA

  int floor = best;
  int alpha_floor = alpha;
  if (best >= beta) return best;
  if (best > alpha) alpha = best;

  InitCaptures(p, m);

  // MAIN LOOP

  while ((move = NextCapture(m))) {

    // DELTA PRUNING
    // Prune insufficient captures (unless opponent has just one piece left). This is done in two stages:

    if (p->cnt[op][N] + p->cnt[op][B] + p->cnt[op][R] + p->cnt[op][Q] > 1) {

      // 1. Prune captures that are unlikely to raise alpha even if opponent does not recapture

      if (floor + tp_value[TpOnSq(p, Tsq(move))] + 150 < alpha_floor) continue;

      // 2. Prune captures that probably lose material

      if (BadCapture(p, move)) continue;
    }

    p->DoMove(move, u);
    if (Illegal(p)) { p->UndoMove(move, u); continue; }
    score = -Quiesce(p, ply + 1, -beta, -alpha, new_pv);
    p->UndoMove(move, u);
	if (Glob.abort_search && root_depth > 1) return 0;

	// BETA CUTOFF

	if (score >= beta) 
		return score;

	// ADJUST ALPHA AND SCORE
	
    if (score > best) {
      best = score;
      if (score > alpha) {
        alpha = score;
        BuildPv(pv, new_pv, move);
      }
    }
  }

  return best;
}