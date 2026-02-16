from inference import ALL_CELLS, enumerate_models, analyze_models, render_grid
from viz import render_grid_image
from typing import Dict, Tuple


def coord(i, j):
    return (i, j)


def pretty_models_summary(models):
    return f"{len(models)} model(s)"


def main():
    # --- Physics (encoded in code and comments) ---
    # 1) S(i,j) is True iff at least one neighbor cell has damaged floor B
    # 2) R(i,j) is True iff at least one neighbor cell has broken forklift F
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
    models = enumerate_models(obs_S, obs_R, forced_B=forced_B, forced_F=forced_F, semantics='implication')
    print("Models:", pretty_models_summary(models))
    status = analyze_models(models)
    print("Derived status (Safe/Risk/Unknown):")
    print(render_grid(status))
    render_grid_image(status, 'initial_implication.png', title='Initial (implication)')

    # Step-by-step reasoning summary (human-readable):
    print("\nStep-by-step derivation for initial observations:")
    print("1) From S(1,1)=False => no neighbor of (1,1) has damaged floor (B false at (1,2) and (2,1)).")
    print("2) From R(1,1)=False => no neighbor of (1,1) has forklift (F false at (1,2) and (2,1)).")
    print("3) Therefore (1,2) and (2,1) satisfy not B and not F => they are Safe.")

    # --- Exploration: robot moves to (2,1), hears squeak but no roar ---
    print('\n=== Exploration: moved to (2,1), hears Squeak=True, Roar=False ===')
    # add new observations
    obs_S2 = dict(obs_S)
    obs_R2 = dict(obs_R)
    obs_S2[coord(2, 1)] = True
    obs_R2[coord(2, 1)] = False

    models2 = enumerate_models(obs_S2, obs_R2, forced_B=forced_B, forced_F=forced_F, semantics='implication')
    print("Models after exploration:", pretty_models_summary(models2))
    status2 = analyze_models(models2)
    print("Derived status after exploration:")
    print(render_grid(status2))
    render_grid_image(status2, 'after_explore_implication.png', title='After explore (implication)')

    print('\nStep-by-step derivation for exploration:')
    print('1) From previous we had (1,2) and (2,1) safe. (1,1) also safe by start assumption.')
    print('2) At (2,1) S=True => at least one neighbor of (2,1) has damaged floor.')
    print('   Neighbors of (2,1): (1,1), (2,2), (3,1). (1,1) is safe => B false there.')
    print('   So damaged floor must be in (2,2) or (3,1) (or both).')
    print('3) At (2,1) R=False => none of neighbors (1,1),(2,2),(3,1) have forklift => F false at these cells.')
    print('   Thus forklifts must be in other cells (e.g., the right/top-right area) to satisfy "at least one forklift exists".')

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

    # Also run the original equivalence semantics for comparison and save images
    print('\n=== Running equivalence semantics for comparison ===')
    models_eq = enumerate_models(obs_S2, obs_R2, forced_B=forced_B, forced_F=forced_F, semantics='equiv')
    print('Equiv models:', pretty_models_summary(models_eq))
    status_eq = analyze_models(models_eq)
    print(render_grid(status_eq))
    render_grid_image(status_eq, 'after_explore_equiv.png', title='After explore (equiv)')


if __name__ == '__main__':
    main()
