import itertools
from typing import Dict, List, Tuple

Coords = Tuple[int, int]


def neighbors(cell: Coords) -> List[Coords]:
    i, j = cell
    nbrs = []
    for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        ni, nj = i + di, j + dj
        if 1 <= ni <= 3 and 1 <= nj <= 3:
            nbrs.append((ni, nj))
    return nbrs


ALL_CELLS: List[Coords] = [(i, j) for i in range(1, 4) for j in range(1, 4)]


def compute_observations_from_assignment(assign_B: Dict[Coords, bool], assign_F: Dict[Coords, bool]):
    S = {}
    R = {}
    for c in ALL_CELLS:
        S[c] = any(assign_B[n] for n in neighbors(c))
        R[c] = any(assign_F[n] for n in neighbors(c))
    return S, R


def enumerate_models(observed_S: Dict[Coords, bool], observed_R: Dict[Coords, bool],
                     forced_B: Dict[Coords, bool] = None, forced_F: Dict[Coords, bool] = None,
                     require_at_least_one_B=True, require_at_least_one_F=True,
                     semantics: str = "equiv"):
    """
    Enumerate all possible assignments of B (damaged floor) and F (forklift broken)
    that satisfy the observed S/R (squeak/roar) values and basic constraints.
    Returns list of models as tuples (B_assign, F_assign).
    """
    forced_B = forced_B or {}
    forced_F = forced_F or {}

    cells = ALL_CELLS

    models = []

    # iterate over B and F assignments; prune using forced values
    # For 3x3 grid there are 2^18 possibilities (≈262k) — manageable
    for bits in itertools.product([0, 1], repeat=18):
        bbits = bits[:9]
        fbits = bits[9:]
        B = {cells[idx]: bool(bbits[idx]) for idx in range(9)}
        F = {cells[idx]: bool(fbits[idx]) for idx in range(9)}

        skip = False
        for c, val in forced_B.items():
            if B[c] != val:
                skip = True
                break
        if skip:
            continue
        for c, val in forced_F.items():
            if F[c] != val:
                skip = True
                break
        if skip:
            continue

        # Check observations according to semantics
        ok = True
        if semantics == "equiv":
            # equivalence: S == OR_neighbors(B), R == OR_neighbors(F)
            S_calc, R_calc = compute_observations_from_assignment(B, F)
            for c, val in observed_S.items():
                if S_calc[c] != val:
                    ok = False
                    break
            if not ok:
                continue
            for c, val in observed_R.items():
                if R_calc[c] != val:
                    ok = False
                    break
            if not ok:
                continue
        elif semantics == "implication":
            # implication rules (as in the photo): B(neighbor) -> S(cell)
            # contrapositive: S(cell)=False => all neighbors are not B
            # Observed S=True does NOT force a neighbor B under pure implication
            for c, val in observed_S.items():
                if val is False:
                    for n in neighbors(c):
                        if B[n]:
                            ok = False
                            break
                    if not ok:
                        break
            if not ok:
                continue
            for c, val in observed_R.items():
                if val is False:
                    for n in neighbors(c):
                        if F[n]:
                            ok = False
                            break
                    if not ok:
                        break
            if not ok:
                continue
        else:
            raise ValueError("Unknown semantics: use 'equiv' or 'implication'")

        if require_at_least_one_B and not any(B.values()):
            continue
        if require_at_least_one_F and not any(F.values()):
            continue

        models.append((B, F))

    return models


def analyze_models(models: List[Tuple[Dict[Coords, bool], Dict[Coords, bool]]]):
    """Return per-cell status for B, F, and Safe across all models.
    Safe := not B and not F
    Status values: 'always_true', 'always_false', 'unknown'
    """
    status = {c: {} for c in ALL_CELLS}
    if not models:
        return status

    for c in ALL_CELLS:
        b_vals = [1 if m[0][c] else 0 for m in models]
        f_vals = [1 if m[1][c] else 0 for m in models]
        # B
        if all(b_vals):
            status[c]['B'] = 'always_true'
        elif not any(b_vals):
            status[c]['B'] = 'always_false'
        else:
            status[c]['B'] = 'unknown'
        # F
        if all(f_vals):
            status[c]['F'] = 'always_true'
        elif not any(f_vals):
            status[c]['F'] = 'always_false'
        else:
            status[c]['F'] = 'unknown'
        # Safe
        safe_vals = [1 if (not m[0][c] and not m[1][c]) else 0 for m in models]
        if all(safe_vals):
            status[c]['Safe'] = 'always_true'
        elif not any(safe_vals):
            status[c]['Safe'] = 'always_false'
        else:
            status[c]['Safe'] = 'unknown'

    return status


def grid_label_from_status(status_cell: Dict[str, str]):
    # prefer Safe determination
    if status_cell.get('Safe') == 'always_true':
        return 'Safe'
    if status_cell.get('Safe') == 'always_false':
        return 'Risk'
    # otherwise unknown
    return 'Unknown'


def render_grid(status):
    rows = []
    for i in range(1, 4):
        row = []
        for j in range(1, 4):
            cell = (i, j)
            label = grid_label_from_status(status.get(cell, {}))
            row.append(label.center(7))
        rows.append('|'.join(row))
    return '\n'.join(rows)
