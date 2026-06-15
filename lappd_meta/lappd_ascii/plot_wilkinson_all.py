import sys
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path

# Wilkinson metadata word indices and labels
WILKINSON_WORDS = {
    2:  ("PSEC0", "Wilkinson feedback count (current)"),
    3:  ("PSEC0", "Wilkinson feedback target"),
    22: ("PSEC1", "Wilkinson feedback count (current)"),
    23: ("PSEC1", "Wilkinson feedback target"),
    42: ("PSEC2", "Wilkinson feedback count (current)"),
    43: ("PSEC2", "Wilkinson feedback target"),
    62: ("PSEC3", "Wilkinson feedback count (current)"),
    63: ("PSEC3", "Wilkinson feedback target"),
    82: ("PSEC4", "Wilkinson feedback count (current)"),
    83: ("PSEC4", "Wilkinson feedback target"),
}

def read_wilkinson(filepath, max_events=None):
    path = Path(filepath)
    if not path.exists():
        print(f"File not found: {filepath}")
        return None, None

    with open(path) as f:
        lines = [l.strip() for l in f if l.strip()]

    rows_per_event = 256
    n_events = len(lines) // rows_per_event
    if max_events is not None:
        n_events = min(n_events, max_events)

    print(f"File: {path.name}")
    print(f"Total events found: {len(lines) // rows_per_event}, reading: {n_events}\n")

    # Storage: {word_index: {"A": [val_ev0, val_ev1, ...], "B": [...]} }
    data = {idx: {"A": [], "B": []} for idx in WILKINSON_WORDS}

    for ev in range(n_events):
        event_rows = lines[ev * rows_per_event : (ev + 1) * rows_per_event]

        for word_idx in WILKINSON_WORDS:
            row_line = event_rows[word_idx]
            cols = row_line.split()
            if len(cols) >= 63:
                try:
                    val_a = int(cols[31], 16)
                    val_b = int(cols[62], 16)
                except ValueError:
                    val_a = val_b = None
            else:
                val_a = val_b = None

            data[word_idx]["A"].append(val_a)
            data[word_idx]["B"].append(val_b)

    return data, n_events


def print_wilkinson_table(data, n_events):
    print(f"{'Event':<6}", end="")
    for idx, (psec, label) in WILKINSON_WORDS.items():
        short = f"{psec} {'cur' if 'current' in label else 'tgt'}"
        print(f"  {short+' A':>12}  {short+' B':>12}", end="")
    print()
    print("-" * (6 + len(WILKINSON_WORDS) * 28))

    for ev in range(n_events):
        print(f"{ev:<6}", end="")
        for idx in WILKINSON_WORDS:
            va = data[idx]["A"][ev]
            vb = data[idx]["B"][ev]
            sa = f"0x{va:04X} ({va})" if va is not None else "N/A"
            sb = f"0x{vb:04X} ({vb})" if vb is not None else "N/A"
            print(f"  {sa:>12}  {sb:>12}", end="")
        print()


def plot_wilkinson(data, n_events, filepath):
    events = list(range(n_events))

    # One figure per PSEC chip, 2 subplots each (current + target), side A and B overlaid
    psec_chips = ["PSEC0", "PSEC1", "PSEC2", "PSEC3", "PSEC4"]

    # Group word indices by PSEC chip
    psec_words = {}
    for idx, (psec, label) in WILKINSON_WORDS.items():
        psec_words.setdefault(psec, {})[label] = idx

    fig, axes = plt.subplots(
        nrows=5, ncols=2,
        figsize=(14, 18),
        sharex=True
    )
    fig.suptitle(
        f"Wilkinson Feedback per Event\n{Path(filepath).name}",
        fontsize=13, fontweight="bold"
    )

    colors = {"A": "#1f77b4", "B": "#d62728"}  # blue / red
    markers = {"A": "o", "B": "s"}

    for row, psec in enumerate(psec_chips):
        words = psec_words[psec]

        for col, label_key in enumerate(["Wilkinson feedback count (current)",
                                          "Wilkinson feedback target"]):
            ax = axes[row][col]
            idx = words[label_key]
            short_label = "Current count" if "current" in label_key else "Target count"

            all_vals = []
            for side in ["A", "B"]:
                vals = data[idx][side]
                valid = [(e, v) for e, v in zip(events, vals) if v is not None]
                if not valid:
                    continue
                ev_x, v_y = zip(*valid)
                ax.plot(
                    ev_x, v_y,
                    color=colors[side],
                    marker=markers[side],
                    markersize=3,
                    linewidth=1,
                    label=f"Side {side}",
                    alpha=0.8
                )
                all_vals.extend(v_y)

            ax.set_title(f"{psec} — {short_label}", fontsize=9)
            ax.set_ylabel("ADC count (dec)", fontsize=8)
            ax.legend(fontsize=7, loc="upper right")
            ax.grid(True, alpha=0.3)

            # Annotate hex range
            if all_vals:
                mn, mx = min(all_vals), max(all_vals)
                ax.set_ylim(mn - 10, mx + 10)
                ax.text(
                    0.01, 0.05,
                    f"min: 0x{mn:04X}  max: 0x{mx:04X}  Δ={mx-mn}",
                    transform=ax.transAxes,
                    fontsize=7, color="gray"
                )

    for ax in axes[-1]:
        ax.set_xlabel("Event number", fontsize=9)

    plt.tight_layout()
    outpath = Path(filepath).stem + "_wilkinson.png"
    plt.savefig(outpath, dpi=150)
    print(f"\nPlot saved to: {outpath}")
    plt.show()


if __name__ == "__main__":
    filepath = sys.argv[1] if len(sys.argv) > 1 else "Ascii20242904_085847.txt"
    max_events = int(sys.argv[2]) if len(sys.argv) > 2 else None

    data, n_events = read_wilkinson(filepath, max_events)
    if data is None:
        sys.exit(1)

    print_wilkinson_table(data, n_events)
    plot_wilkinson(data, n_events, filepath)
