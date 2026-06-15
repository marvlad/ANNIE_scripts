import sys
import matplotlib.pyplot as plt
from pathlib import Path

# ─────────────────────────────────────────────────────────────────
# All metadata word definitions
# ─────────────────────────────────────────────────────────────────
METADATA = {
    0:  ("Board",  "Board ID",                  ""),
    1:  ("PSEC0",  "PSEC ID",                   "expect 0xDCB0"),
    2:  ("PSEC0",  "Wilkinson current",          ""),
    3:  ("PSEC0",  "Wilkinson target",           ""),
    4:  ("PSEC0",  "Vbias (pedestal)",           ""),
    5:  ("PSEC0",  "Self trig threshold",        ""),
    6:  ("PSEC0",  "PROVDD",                     ""),
    7:  ("PSEC0",  "Beamgate TS [63:48]",        ""),
    8:  ("PSEC0",  "Selftrig mask",              ""),
    9:  ("PSEC0",  "Selftrig threshold",         ""),
    10: ("PSEC0",  "Timestamp [15:0]",           "bits[2:0]=clock cycle"),
    11: ("PSEC0",  "Event count [15:0]",         "lo word"),
    12: ("PSEC0",  "VCDL count [15:0]",          "lo word"),
    13: ("PSEC0",  "VCDL count [31:16]",         "hi word"),
    14: ("PSEC0",  "DLLVDD",                     ""),
    15: ("PSEC0",  "ch0 self trig rate",         ""),
    16: ("PSEC0",  "ch1 self trig rate",         ""),
    17: ("PSEC0",  "ch2 self trig rate",         ""),
    18: ("PSEC0",  "ch3 self trig rate",         ""),
    19: ("PSEC0",  "ch4 self trig rate",         ""),
    20: ("PSEC0",  "ch5 self trig rate",         ""),
    21: ("PSEC1",  "PSEC ID",                   "expect 0xDCB1"),
    22: ("PSEC1",  "Wilkinson current",          ""),
    23: ("PSEC1",  "Wilkinson target",           ""),
    24: ("PSEC1",  "Vbias (pedestal)",           ""),
    25: ("PSEC1",  "Self trig threshold",        ""),
    26: ("PSEC1",  "PROVDD",                     ""),
    27: ("PSEC1",  "Beamgate TS [47:32]",        ""),
    28: ("PSEC1",  "Selftrig mask",              ""),
    29: ("PSEC1",  "Selftrig threshold",         ""),
    30: ("PSEC1",  "Timestamp [31:16]",          ""),
    31: ("PSEC1",  "Event count [31:16]",        "hi word"),
    32: ("PSEC1",  "VCDL count [15:0]",          "lo word"),
    33: ("PSEC1",  "VCDL count [31:16]",         "hi word"),
    34: ("PSEC1",  "DLLVDD",                     ""),
    35: ("PSEC1",  "ch0 self trig rate",         ""),
    36: ("PSEC1",  "ch1 self trig rate",         ""),
    37: ("PSEC1",  "ch2 self trig rate",         ""),
    38: ("PSEC1",  "ch3 self trig rate",         ""),
    39: ("PSEC1",  "ch4 self trig rate",         ""),
    40: ("PSEC1",  "ch5 self trig rate",         ""),
    41: ("PSEC2",  "PSEC ID",                   "expect 0xDCB2"),
    42: ("PSEC2",  "Wilkinson current",          ""),
    43: ("PSEC2",  "Wilkinson target",           ""),
    44: ("PSEC2",  "Vbias (pedestal)",           ""),
    45: ("PSEC2",  "Self trig threshold",        ""),
    46: ("PSEC2",  "PROVDD",                     ""),
    47: ("PSEC2",  "Beamgate TS [31:16]",        ""),
    48: ("PSEC2",  "Selftrig mask",              ""),
    49: ("PSEC2",  "Selftrig threshold",         ""),
    50: ("PSEC2",  "Timestamp [47:32]",          ""),
    51: ("PSEC2",  "Reserved",                   "expect 0x0000"),
    52: ("PSEC2",  "VCDL count [15:0]",          "lo word"),
    53: ("PSEC2",  "VCDL count [31:16]",         "hi word"),
    54: ("PSEC2",  "DLLVDD",                     ""),
    55: ("PSEC2",  "ch0 self trig rate",         ""),
    56: ("PSEC2",  "ch1 self trig rate",         ""),
    57: ("PSEC2",  "ch2 self trig rate",         ""),
    58: ("PSEC2",  "ch3 self trig rate",         ""),
    59: ("PSEC2",  "ch4 self trig rate",         ""),
    60: ("PSEC2",  "ch5 self trig rate",         ""),
    61: ("PSEC3",  "PSEC ID",                   "expect 0xDCB3"),
    62: ("PSEC3",  "Wilkinson current",          ""),
    63: ("PSEC3",  "Wilkinson target",           ""),
    64: ("PSEC3",  "Vbias (pedestal)",           ""),
    65: ("PSEC3",  "Self trig threshold",        ""),
    66: ("PSEC3",  "PROVDD",                     ""),
    67: ("PSEC3",  "Beamgate TS [15:0]",         ""),
    68: ("PSEC3",  "Selftrig mask",              ""),
    69: ("PSEC3",  "Selftrig threshold",         ""),
    70: ("PSEC3",  "Timestamp [63:48]",          ""),
    71: ("PSEC3",  "Reserved",                   "expect 0x0000"),
    72: ("PSEC3",  "VCDL count [15:0]",          "lo word"),
    73: ("PSEC3",  "VCDL count [31:16]",         "hi word"),
    74: ("PSEC3",  "DLLVDD",                     ""),
    75: ("PSEC3",  "ch0 self trig rate",         ""),
    76: ("PSEC3",  "ch1 self trig rate",         ""),
    77: ("PSEC3",  "ch2 self trig rate",         ""),
    78: ("PSEC3",  "ch3 self trig rate",         ""),
    79: ("PSEC3",  "ch4 self trig rate",         ""),
    80: ("PSEC3",  "ch5 self trig rate",         ""),
    81: ("PSEC4",  "PSEC ID",                   "expect 0xDCB4"),
    82: ("PSEC4",  "Wilkinson current",          ""),
    83: ("PSEC4",  "Wilkinson target",           ""),
    84: ("PSEC4",  "Vbias (pedestal)",           ""),
    85: ("PSEC4",  "Self trig threshold",        ""),
    86: ("PSEC4",  "PROVDD",                     ""),
    87: ("PSEC4",  "Trigger info 0",             "mode[15:12]/invert[11]/sign[10]/coinc[9:0]"),
    88: ("PSEC4",  "Selftrig mask",              ""),
    89: ("PSEC4",  "Selftrig threshold",         ""),
    90: ("PSEC4",  "Reserved",                   "expect 0x0000"),
    91: ("PSEC4",  "Reserved",                   "expect 0x0000"),
    92: ("PSEC4",  "VCDL count [15:0]",          "lo word"),
    93: ("PSEC4",  "VCDL count [31:16]",         "hi word"),
    94: ("PSEC4",  "DLLVDD",                     ""),
    95: ("PSEC4",  "ch0 self trig rate",         ""),
    96: ("PSEC4",  "ch1 self trig rate",         ""),
    97: ("PSEC4",  "ch2 self trig rate",         ""),
    98: ("PSEC4",  "ch3 self trig rate",         ""),
    99: ("PSEC4",  "ch4 self trig rate",         ""),
   100: ("PSEC4",  "ch5 self trig rate",         ""),
   101: ("Board",  "Combined trig rate",         ""),
   102: ("Board",  "Endword",                    "expect 0xEEEE"),
}

# ─────────────────────────────────────────────────────────────────
# Logical plot groups: title -> (word indices, combine_as_32bit)
# Words listed in PSEC0..4 order where applicable
# ─────────────────────────────────────────────────────────────────
PLOT_GROUPS = [
    # (group_title,          [word_indices],              combine_pairs_32bit)
    # combine_pairs_32bit: list of (lo_idx, hi_idx) to reconstruct 32-bit values
    # if set, one combined value per PSEC is plotted instead of raw lo/hi words

    ("Wilkinson current",    [2, 22, 42, 62, 82],        None),
    ("Wilkinson target",     [3, 23, 43, 63, 83],        None),
    ("Vbias (pedestal)",     [4, 24, 44, 64, 84],        None),
    ("Self trig threshold",  [5, 25, 45, 65, 85],        None),
    ("PROVDD",               [6, 26, 46, 66, 86],        None),
    ("DLLVDD",               [14, 34, 54, 74, 94],       None),
    ("Selftrig mask",        [8, 28, 48, 68, 88],        None),
    ("Selftrig threshold",   [9, 29, 49, 69, 89],        None),
    ("Timestamp",            [10, 30, 50, 70],           None),   # PSEC4 has none
    ("PSEC ID",              [1, 21, 41, 61, 81],        None),
    ("Board ID",             [0],                        None),
    ("Combined trig rate",   [101],                      None),
    ("Endword",              [102],                      None),

    # VCDL: reconstruct 32-bit per PSEC from lo+hi pairs
    ("VCDL count (32-bit)",  [],   [(12,13),(32,33),(52,53),(72,73),(92,93)]),

    # Beamgate: reconstruct 64-bit from 4 x 16-bit words
    ("Beamgate TS (64-bit)", [],   [(7, 27, 47, 67)]),   # special: 4-word 64-bit

    # Event count: 32-bit from words 11 (lo) + 31 (hi)
    ("Event count (32-bit)", [],   [(11, 31)]),

    # Self-trig rates: all 6 channels per PSEC on one plot
    ("Self trig rate PSEC0", [15, 16, 17, 18, 19, 20],  None),
    ("Self trig rate PSEC1", [35, 36, 37, 38, 39, 40],  None),
    ("Self trig rate PSEC2", [55, 56, 57, 58, 59, 60],  None),
    ("Self trig rate PSEC3", [75, 76, 77, 78, 79, 80],  None),
    ("Self trig rate PSEC4", [95, 96, 97, 98, 99, 100], None),

    # Trigger info word 87 — raw value (bit-field decode printed separately)
    ("Trigger info raw",     [87],                       None),
]

SIDE_COLORS  = {"A": "#1f77b4", "B": "#d62728"}
SIDE_MARKERS = {"A": "o",       "B": "s"}
CH_COLORS    = plt.cm.tab10.colors


# ─────────────────────────────────────────────────────────────────
# Read
# ─────────────────────────────────────────────────────────────────
def read_all_metadata(filepath, max_events=None):
    path = Path(filepath)
    with open(path) as f:
        lines = [l.strip() for l in f if l.strip()]

    rows_per_event = 256
    n_events = len(lines) // rows_per_event
    if max_events:
        n_events = min(n_events, max_events)

    print(f"File  : {path.name}")
    print(f"Events: {n_events}")

    data = {idx: {"A": [], "B": []} for idx in METADATA}

    for ev in range(n_events):
        block = lines[ev * rows_per_event: (ev + 1) * rows_per_event]
        for word_idx in METADATA:
            cols = block[word_idx].split()
            for side, col in [("A", 31), ("B", 62)]:
                try:
                    data[word_idx][side].append(int(cols[col], 16))
                except (IndexError, ValueError):
                    data[word_idx][side].append(None)

    return data, n_events


# ─────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────
def combine32(data, n_events, lo_idx, hi_idx):
    out = {"A": [], "B": []}
    for side in ["A", "B"]:
        for ev in range(n_events):
            lo = data[lo_idx][side][ev]
            hi = data[hi_idx][side][ev]
            out[side].append(((hi << 16) | lo) if (lo is not None and hi is not None) else None)
    return out


def combine64(data, n_events, idx0, idx1, idx2, idx3):
    out = {"A": [], "B": []}
    for side in ["A", "B"]:
        for ev in range(n_events):
            parts = [data[i][side][ev] for i in (idx0, idx1, idx2, idx3)]
            if all(p is not None for p in parts):
                val = (parts[0] << 48) | (parts[1] << 32) | (parts[2] << 16) | parts[3]
                out[side].append(val)
            else:
                out[side].append(None)
    return out


def annotate_ax(ax, vals_a, vals_b):
    all_v = [v for v in vals_a + vals_b if v is not None]
    if not all_v:
        return
    mn, mx = min(all_v), max(all_v)
    pad = max((mx - mn) * 0.1, 1)
    ax.set_ylim(mn - pad, mx + pad)
    # Show hex annotation only if values fit in 16 bits
    if mx <= 0xFFFF:
        note = f"min=0x{mn:04X}  max=0x{mx:04X}  Δ={mx - mn}"
    else:
        note = f"min={mn}  max={mx}  Δ={mx - mn}"
    ax.text(0.01, 0.04, note, transform=ax.transAxes,
            fontsize=6, color="grey")


def plot_side(ax, events, vals, side, label=None, color=None, marker=None):
    valid = [(e, v) for e, v in zip(events, vals) if v is not None]
    if not valid:
        return
    ex, vy = zip(*valid)
    ax.plot(ex, vy,
            color=color or SIDE_COLORS[side],
            marker=marker or SIDE_MARKERS[side],
            markersize=2, linewidth=0.8,
            label=label or f"Side {side}",
            alpha=0.85)


def save_fig(fig, stem, name):
    safe = name.lower().replace(" ", "_").replace("/", "_").replace("-", "_").replace("(","").replace(")","")
    out = f"{stem}_{safe}.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"  Saved: {out}")
    plt.close(fig)


# ─────────────────────────────────────────────────────────────────
# Plot dispatcher
# ─────────────────────────────────────────────────────────────────
def make_plot(group_title, word_indices, combine_pairs, data, n_events, stem):
    events = list(range(n_events))
    PSEC_LABELS = ["PSEC0", "PSEC1", "PSEC2", "PSEC3", "PSEC4"]

    # ── Special: VCDL 32-bit (one subplot per PSEC) ──────────────
    if combine_pairs and len(combine_pairs[0]) == 2 and group_title.startswith("VCDL"):
        n = len(combine_pairs)
        fig, axes = plt.subplots(n, 1, figsize=(12, 2.8 * n), sharex=True)
        if n == 1:
            axes = [axes]
        fig.suptitle(f"{group_title} — per event", fontsize=11, fontweight="bold")
        for ax, (lo, hi), psec in zip(axes, combine_pairs, PSEC_LABELS):
            combined = combine32(data, n_events, lo, hi)
            plot_side(ax, events, combined["A"], "A")
            plot_side(ax, events, combined["B"], "B")
            ax.set_title(f"{psec} (words {lo}+{hi})", fontsize=8)
            ax.set_ylabel("count (dec)", fontsize=7)
            ax.legend(fontsize=6, loc="upper right")
            ax.grid(True, alpha=0.25)
            annotate_ax(ax, combined["A"], combined["B"])
        axes[-1].set_xlabel("Event number", fontsize=8)
        plt.tight_layout()
        save_fig(fig, stem, group_title)
        return

    # ── Special: Beamgate 64-bit ──────────────────────────────────
    if combine_pairs and len(combine_pairs[0]) == 4:
        idx0, idx1, idx2, idx3 = combine_pairs[0]
        combined = combine64(data, n_events, idx0, idx1, idx2, idx3)
        fig, ax = plt.subplots(figsize=(12, 3))
        fig.suptitle(f"{group_title} — per event", fontsize=11, fontweight="bold")
        plot_side(ax, events, combined["A"], "A")
        plot_side(ax, events, combined["B"], "B")
        ax.set_ylabel("timestamp (dec)", fontsize=8)
        ax.set_xlabel("Event number", fontsize=8)
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.25)
        annotate_ax(ax, combined["A"], combined["B"])
        plt.tight_layout()
        save_fig(fig, stem, group_title)
        return

    # ── Special: Event count 32-bit ───────────────────────────────
    if combine_pairs and len(combine_pairs[0]) == 2 and group_title.startswith("Event count"):
        lo, hi = combine_pairs[0]
        combined = combine32(data, n_events, lo, hi)
        fig, ax = plt.subplots(figsize=(12, 3))
        fig.suptitle(f"{group_title} — per event", fontsize=11, fontweight="bold")
        plot_side(ax, events, combined["A"], "A")
        plot_side(ax, events, combined["B"], "B")
        ax.set_ylabel("count (dec)", fontsize=8)
        ax.set_xlabel("Event number", fontsize=8)
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.25)
        annotate_ax(ax, combined["A"], combined["B"])
        plt.tight_layout()
        save_fig(fig, stem, group_title)
        return

    # ── Self-trig rates: all 6 channels, side A/B as subplots ────
    if group_title.startswith("Self trig rate PSEC"):
        psec = group_title.split()[-1]
        fig, axes = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
        fig.suptitle(f"{group_title} — per channel per event",
                     fontsize=11, fontweight="bold")
        for ax, side in zip(axes, ["A", "B"]):
            for ch, idx in enumerate(word_indices):
                vals = data[idx][side]
                plot_side(ax, events, vals, side,
                          label=f"ch{ch}",
                          color=CH_COLORS[ch % 10],
                          marker="o")
            ax.set_title(f"Side {side}", fontsize=9)
            ax.set_ylabel("rate count", fontsize=7)
            ax.legend(fontsize=6, ncol=6, loc="upper right")
            ax.grid(True, alpha=0.25)
        axes[-1].set_xlabel("Event number", fontsize=8)
        plt.tight_layout()
        save_fig(fig, stem, group_title)
        return

    # ── Standard: one subplot per word index ─────────────────────
    n = len(word_indices)
    if n == 0:
        return
    fig, axes = plt.subplots(n, 1, figsize=(12, max(2.8 * n, 3)), sharex=True)
    if n == 1:
        axes = [axes]
    fig.suptitle(f"{group_title} — per event", fontsize=11, fontweight="bold")

    for ax, idx in zip(axes, word_indices):
        psec, label, note = METADATA[idx]
        plot_side(ax, events, data[idx]["A"], "A")
        plot_side(ax, events, data[idx]["B"], "B")
        title = f"{psec} — {label}"
        if note:
            title += f"  [{note}]"
        ax.set_title(title, fontsize=8)
        ax.set_ylabel("value (dec)", fontsize=7)
        ax.legend(fontsize=6, loc="upper right")
        ax.grid(True, alpha=0.25)
        annotate_ax(ax, data[idx]["A"], data[idx]["B"])

    axes[-1].set_xlabel("Event number", fontsize=8)
    plt.tight_layout()
    save_fig(fig, stem, group_title)


# ─────────────────────────────────────────────────────────────────
# Human-readable table for one event
# ─────────────────────────────────────────────────────────────────
def print_event(data, event_idx):
    print(f"\n{'='*76}")
    print(f"  EVENT {event_idx} — Full Metadata Dump")
    print(f"{'='*76}")
    print(f"{'Idx':>4}  {'PSEC':<6}  {'Label':<26}  {'Side A':>14}  {'Side B':>14}  Note")
    print(f"{'-'*76}")
    for idx, (psec, label, note) in METADATA.items():
        va = data[idx]["A"][event_idx]
        vb = data[idx]["B"][event_idx]
        sa = f"0x{va:04X} ({va:5d})" if va is not None else "N/A"
        sb = f"0x{vb:04X} ({vb:5d})" if vb is not None else "N/A"
        print(f"{idx:>4}  {psec:<6}  {label:<26}  {sa:>14}  {sb:>14}  {note}")


# ─────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    filepath   = sys.argv[1] if len(sys.argv) > 1 else "Ascii20242904_085847.txt"
    max_events = int(sys.argv[2]) if len(sys.argv) > 2 else None

    data, n_events = read_all_metadata(filepath, max_events)
    stem = Path(filepath).stem

    print_event(data, event_idx=0)

    print(f"\nGenerating {len(PLOT_GROUPS)} plots for {n_events} events...")
    for group_title, word_indices, combine_pairs in PLOT_GROUPS:
        print(f"  Plotting: {group_title}")
        make_plot(group_title, word_indices, combine_pairs, data, n_events, stem)

    print(f"\nDone. All PNGs saved with prefix '{stem}_'")
