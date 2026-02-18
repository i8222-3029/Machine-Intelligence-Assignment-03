from inference import ALL_CELLS, enumerate_models, analyze_models, render_grid
from viz import render_grid_image
from typing import Dict, Tuple


def coord(i, j):
    return (i, j)


def pretty_models_summary(models):
    return f"{len(models)} model(s)"


def main():
    # --- Physics (encoded in code and comments) ---
    # model-answer setting: biconditionals (equivalence)
    # 1) S(i,j) <-> OR over neighboring damaged-floor cells B
    # 2) R(i,j) <-> OR over neighboring forklift cells F
    # 3) Safe(i,j) iff not B(i,j) and not F(i,j)

    # --- Initial/Background knowledge ---
    # Start at (1,1) and it is safe
    forced_B = {coord(1, 1): False}
    forced_F = {coord(1, 1): False}

    # At least one damaged floor exists and at least one forklift exists
    # (these are enforced by enumerate_models defaults)

    # --- Scenario 1 observations: at start robot at (1,1) hears nothing ---
    observed_S = {c: None for c in ALL_CELLS}
    observed_R = {c: None for c in ALL_CELLS}
    # specify observations only where known
    observed_S[coord(1, 1)] = False
    observed_R[coord(1, 1)] = False

    # Filter out None values for the enumerator
    obs_S = {c: v for c, v in observed_S.items() if v is not None}
    obs_R = {c: v for c, v in observed_R.items() if v is not None}

    print("=== Initial scenario: at (1,1) no squeak, no roar ===")
    models = enumerate_models(obs_S, obs_R, forced_B=forced_B, forced_F=forced_F, semantics='equiv')
    print("Models:", pretty_models_summary(models))
    status = analyze_models(models)
    print("Derived status (Safe/Risk/Unknown):")
    print(render_grid(status))
    render_grid_image(status, 'initial_equiv.png', title='Initial (equiv)')

    # Step-by-step reasoning summary (human-readable):
    print("\nStep-by-step derivation for initial observations:")
    print("1) From S(1,1)=False => no neighbor of (1,1) has damaged floor (B false at (1,2) and (2,1)).")
    print("2) From R(1,1)=False => no neighbor of (1,1) has forklift (F false at (1,2) and (2,1)).")
    print("3) Therefore (1,2) and (2,1) satisfy not B and not F => they are Safe.")
    print("4) For all other cells, damage/forklift status is still unknown at this stage.")

    # --- Exploration: robot moves to (2,1), hears squeak but no roar ---
    print('\n=== Exploration: moved to (2,1), hears Squeak=True, Roar=False ===')
    # add new observations
    obs_S2 = dict(obs_S)
    obs_R2 = dict(obs_R)
    obs_S2[coord(2, 1)] = True
    obs_R2[coord(2, 1)] = False

    models2 = enumerate_models(obs_S2, obs_R2, forced_B=forced_B, forced_F=forced_F, semantics='equiv')
    print("Models after exploration:", pretty_models_summary(models2))
    status2 = analyze_models(models2)
    print("Derived status after exploration:")
    print(render_grid(status2))
    render_grid_image(status2, 'after_explore_equiv.png', title='After explore (equiv)')

    print('\nStep-by-step derivation for exploration (equivalence semantics):')
    print('1) From previous we had (1,2) and (2,1) safe. (1,1) also safe by start assumption.')
    print('2) At (2,1) S=True and S(2,1) <-> (B(1,1) or B(2,2) or B(3,1)) imply:')
    print('   B(1,1) or B(2,2) or B(3,1). Since B(1,1)=False, we get B(2,2) or B(3,1).')
    print('3) At (2,1) R=False => none of neighbors (1,1),(2,2),(3,1) have forklift => F false at these cells.')
    print('   Together with previous exclusions and at-least-one-forklift, forklift must be in one or more of')
    print('   {(3,2), (1,3), (2,3), (3,3)}.')
    print('4) No individual uncleared square is provably dangerous yet:')
    print('   we know B(3,1) or B(2,2), but cannot decide exactly which one is damaged.')

    # Summarize definite safe / risk / unknown
    print('\nFinal summary:')
    for i in range(1, 4):
        for j in range(1, 4):
            cell = coord(i, j)
            st = status2.get(cell, {})
            label = 'Unknown'
            if st.get('Safe') == 'always_true':
                label = 'Safe'
            elif st.get('Safe') == 'always_false':
                label = 'Risk'
            print(f"Cell {cell}: {label} | B:{st.get('B')} F:{st.get('F')}")

    print('\nKey new knowledge after exploration: at least one of (3,1) and (2,2) is damaged floor;')
    print('forklift(s) are in the remaining uncleared set {(3,2), (1,3), (2,3), (3,3)}.')

    print('\n(Using biconditional/equivalence semantics as in the model answer.)')


if __name__ == '__main__':
    main()
