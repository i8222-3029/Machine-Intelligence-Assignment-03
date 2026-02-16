from typing import Dict, Tuple

Coords = Tuple[int, int]


def _has_matplotlib():
    try:
        import matplotlib.pyplot as plt  # type: ignore
        return True
    except Exception:
        return False


def render_grid_image(status: Dict[Coords, Dict[str, str]], path: str, title: str = ''):
    """
    If matplotlib is available, save a PNG at `path`. Otherwise write an ASCII
    representation to `path + '.txt'`.
    """
    if _has_matplotlib():
        import matplotlib.pyplot as plt

        def color_for_label(label: str):
            if label == 'Safe':
                return '#8BC34A'
            if label == 'Risk':
                return '#F44336'
            return '#BDBDBD'

        fig, ax = plt.subplots(figsize=(3, 3))
        ax.set_xticks([])
        ax.set_yticks([])

        for i in range(1, 4):
            for j in range(1, 4):
                cell = (i, j)
                st = status.get(cell, {})
                if st.get('Safe') == 'always_true':
                    label = 'Safe'
                elif st.get('Safe') == 'always_false':
                    label = 'Risk'
                else:
                    label = 'Unknown'
                color = color_for_label(label)
                rect = plt.Rectangle((j - 1, 3 - i), 1, 1, facecolor=color, edgecolor='k')
                ax.add_patch(rect)
                ax.text(j - 0.5, 3 - i + 0.5, label, ha='center', va='center', fontsize=8)

        ax.set_xlim(0, 3)
        ax.set_ylim(0, 3)
        if title:
            ax.set_title(title)
        plt.savefig(path, bbox_inches='tight')
        plt.close(fig)
    else:
        # fallback: write ASCII grid file
        lines = []
        for i in range(1, 4):
            row = []
            for j in range(1, 4):
                cell = (i, j)
                st = status.get(cell, {})
                if st.get('Safe') == 'always_true':
                    label = 'Safe'
                elif st.get('Safe') == 'always_false':
                    label = 'Risk'
                else:
                    label = 'Unknown'
                row.append(label.center(7))
            lines.append('|'.join(row))
        with open(path + '.txt', 'w', encoding='utf-8') as f:
            if title:
                f.write(title + '\n')
            f.write('\n'.join(lines))

