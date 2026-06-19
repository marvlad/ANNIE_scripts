import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import os
import glob

# ── Load ───────────────────────────────────────────────────────────────────────
df = pd.read_csv("lappd_metadata.csv")

lappd_ids    = sorted(df["lappd_id"].unique())
boards       = sorted(df["board_id"].unique())
PSEC         = list(range(5))
lappd_colors = ["tab:blue", "tab:orange", "tab:green", "tab:red",
                "tab:purple", "tab:brown", "tab:pink", "tab:gray"]
board_markers = ["o", "s", "^", "D"]
chip_colors   = ["tab:blue","tab:orange","tab:green","tab:red","tab:purple"]

os.makedirs("plots", exist_ok=True)

def lbd(df, lid, bid):
    """Subset for one LAPPD + board, sorted by global_entry."""
    return df[(df["lappd_id"]==lid) & (df["board_id"]==bid)].sort_values("global_entry")

def savefig(fig, name):
    path = os.path.join("plots", name)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print("  saved ->", path)
    plt.close(fig)

def plot_per_chip_per_lappd_board(colname, title, ylabel, fname):
    """One figure per (lappd, board). One line per PSEC chip (0-4).
    colname must contain {chip} placeholder, e.g. 'psec{chip}_vbias'"""
    for lid in lappd_ids:
        for bid in boards:
            d = lbd(df, lid, bid)
            if d.empty: continue
            fig, ax = plt.subplots(figsize=(10, 4))
            for chip in PSEC:
                col = colname.format(chip=chip)
                if col in d.columns:
                    ax.plot(d["global_entry"], d[col],
                            marker="o", ms=4, color=chip_colors[chip],
                            label="PSEC %d" % chip)
            ax.set_title("%s  |  LAPPD %d  Board %d" % (title, lid, bid))
            ax.set_xlabel("Global entry")
            ax.set_ylabel(ylabel)
            ax.legend(fontsize=8, ncol=5)
            ax.grid(True, alpha=0.3)
            savefig(fig, "%s_lappd%d_bd%d.png" % (fname, lid, bid))

def plot_per_chip_per_lappd_board_all_chips_overlay(colname, title, ylabel, fname):
    """All LAPPDs and boards in one figure, subplots = chips."""
    fig, axes = plt.subplots(1, 5, figsize=(20, 4), sharey=False)
    fig.suptitle(title, fontweight="bold")
    for chip in PSEC:
        ax = axes[chip]
        col = colname.format(chip=chip)
        for lid in lappd_ids:
            lcol = lappd_colors[lappd_ids.index(lid) % len(lappd_colors)]
            for bid in boards:
                d = lbd(df, lid, bid)
                if d.empty or col not in d.columns: continue
                mk = board_markers[bid % len(board_markers)]
                ax.plot(d["global_entry"], d[col],
                        marker=mk, ms=4, color=lcol, alpha=0.8,
                        label="L%d Bd%d" % (lid, bid))
        ax.set_title("PSEC %d" % chip)
        ax.set_xlabel("Global entry")
        if chip == 0: ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.3)
    axes[-1].legend(fontsize=7, bbox_to_anchor=(1.01, 1), loc="upper left")
    plt.tight_layout()
    savefig(fig, fname + "_allchips.png")


# ══════════════════════════════════════════════════════════════════════════════
# 0. BOARD ID vs ENTRY  — detect if board ID changes during the run
# ══════════════════════════════════════════════════════════════════════════════
print("Plotting board ID vs entry ...")
# Color each dot by its board_id value — a swap shows up as a color change
bid_colors = ["tab:blue", "tab:orange", "tab:green", "tab:red",
              "tab:purple", "tab:brown", "tab:pink", "tab:gray"]

fig, axes = plt.subplots(len(lappd_ids), 1,
                         figsize=(14, 4*len(lappd_ids)), squeeze=False)
fig.suptitle("Board ID (physical ACC port) vs Entry\n"
             "Each color = one board_id value — a color jump = cable was swapped",
             fontsize=13, fontweight="bold")

for row, lid in enumerate(lappd_ids):
    ax   = axes[row, 0]
    dall = df[df["lappd_id"]==lid].sort_values("global_entry")
    if dall.empty: continue

    # Plot each point colored by its board_id
    unique_bids = sorted(dall["board_id"].unique())
    for b in unique_bids:
        mask = dall["board_id"] == b
        ax.scatter(dall.loc[mask, "global_entry"],
                   dall.loc[mask, "board_id"],
                   color=bid_colors[b % len(bid_colors)],
                   s=18, label="board_id = %d" % b, zorder=3)

    # Connect dots with a thin gray line so jumps are obvious
    ax.plot(dall["global_entry"], dall["board_id"],
            color="gray", lw=0.5, alpha=0.4, zorder=2)

    ax.set_title("LAPPD %d" % lid, fontsize=10)
    ax.set_xlabel("Global entry")
    ax.set_ylabel("board_id (ACC port)")
    ax.set_yticks(unique_bids)
    ax.set_ylim(min(unique_bids) - 0.5, max(unique_bids) + 0.5)
    ax.legend(fontsize=9, loc="upper right")
    ax.grid(True, alpha=0.3)

plt.tight_layout()
savefig(fig, "board_id_vs_entry.png")

# ══════════════════════════════════════════════════════════════════════════════
# 1. TIMESTAMPS
# ══════════════════════════════════════════════════════════════════════════════
print("Plotting timestamps ...")
fig, axes = plt.subplots(len(lappd_ids), 2, figsize=(14, 5*len(lappd_ids)))
if len(lappd_ids) == 1: axes = [axes]
fig.suptitle("Timestamps", fontsize=14, fontweight="bold")
for row, lid in enumerate(lappd_ids):
    lcol = lappd_colors[row % len(lappd_colors)]
    for bid in boards:
        d = lbd(df, lid, bid)
        if d.empty: continue
        mk = board_markers[bid % len(board_markers)]
        axes[row][0].plot(d["global_entry"], d["beamgate_ns"]/1e9,
                          marker=mk, color=lcol, alpha=0.8, label="Bd%d" % bid)
        axes[row][1].plot(d["global_entry"], d["timestamp_ns"]/1e9,
                          marker=mk, color=lcol, alpha=0.8, label="Bd%d" % bid)
    for col_idx, (ttl, yl) in enumerate([("Beamgate [s]","Time [s]"),
                                          ("Timestamp [s]","Time [s]")]):
        axes[row][col_idx].set_title("LAPPD %d — %s" % (lid, ttl))
        axes[row][col_idx].set_xlabel("Global entry")
        axes[row][col_idx].set_ylabel(yl)
        axes[row][col_idx].legend(fontsize=8)
        axes[row][col_idx].grid(True, alpha=0.3)
plt.tight_layout()
savefig(fig, "timestamps.png")

# ── Timestamp raw (ticks) ─────────────────────────────────────────────────────
fig, axes = plt.subplots(len(lappd_ids), 2, figsize=(14, 5*len(lappd_ids)))
if len(lappd_ids) == 1: axes = [axes]
fig.suptitle("Timestamps RAW (ticks)", fontsize=14, fontweight="bold")
for row, lid in enumerate(lappd_ids):
    lcol = lappd_colors[row % len(lappd_colors)]
    for bid in boards:
        d = lbd(df, lid, bid)
        if d.empty: continue
        mk = board_markers[bid % len(board_markers)]
        axes[row][0].plot(d["global_entry"], d["beamgate_raw"],
                          marker=mk, color=lcol, alpha=0.8, label="Bd%d" % bid)
        axes[row][1].plot(d["global_entry"], d["timestamp_raw"],
                          marker=mk, color=lcol, alpha=0.8, label="Bd%d" % bid)
    for col_idx, ttl in enumerate(["Beamgate raw [ticks]","Timestamp raw [ticks]"]):
        axes[row][col_idx].set_title("LAPPD %d — %s" % (lid, ttl))
        axes[row][col_idx].set_xlabel("Global entry")
        axes[row][col_idx].set_ylabel("Ticks")
        axes[row][col_idx].legend(fontsize=8)
        axes[row][col_idx].grid(True, alpha=0.3)
plt.tight_layout()
savefig(fig, "timestamps_raw.png")

# ── Timestamp diff board0 - board1 ───────────────────────────────────────────
if len(boards) >= 2:
    fig, axes = plt.subplots(len(lappd_ids), 2, figsize=(12, 4*len(lappd_ids)))
    if len(lappd_ids) == 1: axes = [axes]
    fig.suptitle("Timestamp diff Board0 - Board1", fontweight="bold")
    for row, lid in enumerate(lappd_ids):
        lcol = lappd_colors[row % len(lappd_colors)]
        d0 = lbd(df, lid, 0).set_index("global_entry")
        d1 = lbd(df, lid, 1).set_index("global_entry")
        common = d0.index.intersection(d1.index)
        if len(common) == 0: continue
        bg_diff = (d0.loc[common,"beamgate_ns"] - d1.loc[common,"beamgate_ns"]).astype(float)
        ts_diff = (d0.loc[common,"timestamp_ns"] - d1.loc[common,"timestamp_ns"]).astype(float)
        for ax, diff, ttl in zip(axes[row],
                                  [bg_diff, ts_diff],
                                  ["Beamgate diff [ns]","Timestamp diff [ns]"]):
            ax.plot(common, diff, marker="o", ms=2, lw=0.8, color=lcol, alpha=0.8)
            ax.fill_between(common, diff, alpha=0.2, color=lcol)
            ax.axhline(0, color="black", lw=0.8, ls="--", alpha=0.4)
            ax.set_title("LAPPD %d — %s" % (lid, ttl))
            ax.set_xlabel("Global entry")
            ax.set_ylabel("Δ [ns]")
            ax.grid(True, alpha=0.3)
    plt.tight_layout()
    savefig(fig, "timestamp_diff.png")

# ══════════════════════════════════════════════════════════════════════════════
# 2. CLOCK CYCLE
# ══════════════════════════════════════════════════════════════════════════════
print("Plotting clock cycle ...")
fig, axes = plt.subplots(len(lappd_ids), max(len(boards),1),
                         figsize=(6*len(boards), 4*len(lappd_ids)), squeeze=False)
fig.suptitle("Clock Cycle (0-7)", fontweight="bold")
for row, lid in enumerate(lappd_ids):
    lcol = lappd_colors[row % len(lappd_colors)]
    for bid in boards:
        d   = lbd(df, lid, bid)
        ax  = axes[row][bid]
        if not d.empty:
            ax.bar(d["global_entry"], d["clockcycle"].astype(float),
                   color=lcol, alpha=0.8)
        ax.set_title("LAPPD %d Board %d" % (lid, bid))
        ax.set_xlabel("Global entry"); ax.set_ylabel("Clock cycle")
        ax.set_ylim(0, 8); ax.set_yticks(range(8))
        ax.grid(True, alpha=0.3)
plt.tight_layout()
savefig(fig, "clockcycle.png")

# ══════════════════════════════════════════════════════════════════════════════
# 3. WILKINSON CURRENT vs TARGET
# ══════════════════════════════════════════════════════════════════════════════
print("Plotting Wilkinson counts ...")
for lid in lappd_ids:
    for bid in boards:
        d = lbd(df, lid, bid)
        if d.empty: continue
        fig, axes = plt.subplots(1, 5, figsize=(20, 4), sharey=False)
        fig.suptitle("Wilkinson Current vs Target | LAPPD %d Board %d" % (lid, bid),
                     fontweight="bold")
        for chip in PSEC:
            ax = axes[chip]
            ax.plot(d["global_entry"], d["psec%d_wilkinson_current" % chip],
                    marker="o", ms=4, color=chip_colors[chip], label="current")
            ax.axhline(d["psec%d_wilkinson_target" % chip].iloc[0],
                       color="black", ls="--", lw=1.5, label="target")
            ax.set_title("PSEC %d" % chip); ax.set_xlabel("Global entry")
            if chip == 0: ax.set_ylabel("ADC counts")
            ax.legend(fontsize=8); ax.grid(True, alpha=0.3)
        plt.tight_layout()
        savefig(fig, "wilkinson_lappd%d_bd%d.png" % (lid, bid))

# ── Wilkinson deviation ───────────────────────────────────────────────────────
for lid in lappd_ids:
    for bid in boards:
        d = lbd(df, lid, bid)
        if d.empty: continue
        fig, axes = plt.subplots(1, 5, figsize=(20, 4), sharey=True)
        fig.suptitle("Wilkinson Deviation (current - target) | LAPPD %d Board %d" % (lid, bid),
                     fontweight="bold")
        for chip in PSEC:
            ax  = axes[chip]
            dev = d["psec%d_wilkinson_current" % chip] - d["psec%d_wilkinson_target" % chip]
            ax.plot(d["global_entry"], dev, marker="o", ms=4, color=chip_colors[chip])
            ax.axhline(0, color="black", ls="--", lw=1)
            ax.set_title("PSEC %d" % chip); ax.set_xlabel("Global entry")
            if chip == 0: ax.set_ylabel("Current - Target")
            ax.grid(True, alpha=0.3)
        plt.tight_layout()
        savefig(fig, "wilkinson_deviation_lappd%d_bd%d.png" % (lid, bid))

# ══════════════════════════════════════════════════════════════════════════════
# 4. VBIAS
# ══════════════════════════════════════════════════════════════════════════════
print("Plotting Vbias ...")
plot_per_chip_per_lappd_board(
    "psec{chip}_vbias", "Vbias (Pedestal)", "ADC counts", "vbias")
plot_per_chip_per_lappd_board_all_chips_overlay(
    "psec{chip}_vbias", "Vbias (Pedestal) — all", "ADC counts", "vbias")

# ══════════════════════════════════════════════════════════════════════════════
# 5. SELF-TRIGGER THRESHOLD
# ══════════════════════════════════════════════════════════════════════════════
print("Plotting self-trigger threshold ...")
plot_per_chip_per_lappd_board(
    "psec{chip}_selftrig_threshold", "Self-Trigger Threshold", "ADC counts", "selftrig_threshold")
plot_per_chip_per_lappd_board_all_chips_overlay(
    "psec{chip}_selftrig_threshold", "Self-Trigger Threshold — all", "ADC counts", "selftrig_threshold")

# ══════════════════════════════════════════════════════════════════════════════
# 6. PROVDD
# ══════════════════════════════════════════════════════════════════════════════
print("Plotting PROVDD ...")
plot_per_chip_per_lappd_board(
    "psec{chip}_provdd", "PROVDD (analog power)", "ADC counts", "provdd")
plot_per_chip_per_lappd_board_all_chips_overlay(
    "psec{chip}_provdd", "PROVDD — all", "ADC counts", "provdd")

# ══════════════════════════════════════════════════════════════════════════════
# 7. SELF-TRIGGER MASK  — raw value + per-bit breakdown + heatmap
# ══════════════════════════════════════════════════════════════════════════════
print("Plotting self-trigger mask ...")

# 7a. Raw mask value
plot_per_chip_per_lappd_board(
    "psec{chip}_selftrig_mask", "Self-Trigger Mask (raw 6-bit value)",
    "Mask value (0-63)", "selftrig_mask_raw")
plot_per_chip_per_lappd_board_all_chips_overlay(
    "psec{chip}_selftrig_mask", "Self-Trigger Mask raw — all",
    "Mask value", "selftrig_mask_raw")

# 7b. Per-bit breakdown: 5 chips x 6 channels
for lid in lappd_ids:
    for bid in boards:
        d = lbd(df, lid, bid)
        if d.empty: continue
        fig, axes = plt.subplots(5, 6, figsize=(20, 14), sharex=True, sharey=True)
        fig.suptitle(
            "Self-Trigger Mask per channel (0=OFF, 1=ON) | LAPPD %d Board %d" % (lid, bid),
            fontsize=13, fontweight="bold")
        for chip in PSEC:
            mask = d["psec%d_selftrig_mask" % chip]
            for ch in range(6):
                ax  = axes[chip, ch]
                bit = (np.right_shift(mask.values.astype(int), ch)) & 1
                ax.plot(d["global_entry"], bit, marker="o", ms=3, color=chip_colors[chip])
                ax.fill_between(d["global_entry"], bit, alpha=0.2, color=chip_colors[chip])
                ax.set_title("P%d ch%d" % (chip, ch), fontsize=8)
                ax.set_ylim(-0.2, 1.4); ax.set_yticks([0, 1])
                ax.set_yticklabels(["OFF","ON"], fontsize=7)
                ax.grid(True, alpha=0.3)
                if ch == 0: ax.set_ylabel("PSEC%d" % chip, fontsize=8)
                if chip == 4: ax.set_xlabel("Entry", fontsize=7)
        plt.tight_layout()
        savefig(fig, "selftrig_mask_bits_lappd%d_bd%d.png" % (lid, bid))

# 7c. Heatmap: fraction ON per chip per channel
for lid in lappd_ids:
    for bid in boards:
        d = lbd(df, lid, bid)
        if d.empty: continue
        matrix = np.zeros((5, 6))
        for chip in PSEC:
            mask = d["psec%d_selftrig_mask" % chip]
            for ch in range(6):
                bit = (np.right_shift(mask.values.astype(int), ch)) & 1
                matrix[chip, ch] = bit.mean()
        fig, ax = plt.subplots(figsize=(8, 4))
        im = ax.imshow(matrix, aspect="auto", cmap="RdYlGn", vmin=0, vmax=1)
        ax.set_xticks(range(6)); ax.set_xticklabels(["ch%d" % c for c in range(6)])
        ax.set_yticks(range(5)); ax.set_yticklabels(["PSEC%d" % p for p in range(5)])
        ax.set_title("Self-Trigger Mask — fraction ON | LAPPD %d Board %d" % (lid, bid))
        plt.colorbar(im, ax=ax, label="Fraction of entries = ON")
        for chip in PSEC:
            for ch in range(6):
                ax.text(ch, chip, "%.0f%%" % (matrix[chip,ch]*100),
                        ha="center", va="center", fontsize=9, fontweight="bold", color="black")
        plt.tight_layout()
        savefig(fig, "selftrig_mask_heatmap_lappd%d_bd%d.png" % (lid, bid))

# ══════════════════════════════════════════════════════════════════════════════
# 8. SELF-TRIGGER THRESHOLD WORDS
#    PSEC0-3: psecN_selftrig_thresh_raw  — plain ADC value, NOT packed
#    PSEC4:   psec4_trig_mode / sma_invert / st_sign / coinc_min — pre-decoded by C++
# ══════════════════════════════════════════════════════════════════════════════
print("Plotting self-trigger threshold words ...")

# 8a. PSEC0-3: plain raw threshold values
for lid in lappd_ids:
    for bid in boards:
        d = lbd(df, lid, bid)
        if d.empty: continue
        fig, axes = plt.subplots(1, 4, figsize=(18, 4))
        fig.suptitle(
            "Self-trigger threshold word PSEC0-3 (raw ADC) | LAPPD %d Board %d\n"
            "Plain threshold values — NOT packed bit fields" % (lid, bid),
            fontsize=11, fontweight="bold")
        for chip in range(4):
            ax  = axes[chip]
            col = "psec%d_selftrig_thresh_raw" % chip
            if col in d.columns:
                ax.plot(d["global_entry"], d[col],
                        marker="o", ms=3, lw=1.0,
                        color=chip_colors[chip], alpha=0.85, label="PSEC%d" % chip)
            ax.set_title("PSEC%d" % chip, fontsize=9)
            ax.set_xlabel("Entry", fontsize=7)
            if chip == 0: ax.set_ylabel("threshold value (ADC)", fontsize=8)
            ax.grid(True, alpha=0.3); ax.tick_params(labelsize=7)
            ax.legend(fontsize=7)
        plt.tight_layout()
        savefig(fig, "selftrig_thresh_psec03_lappd%d_bd%d.png" % (lid, bid))

# 8b. PSEC4 only: word 87 decoded — columns pre-computed by C++
w87_fields = [
    ("psec4_trig_mode",  "Trig mode [15:12]"),
    ("psec4_sma_invert", "SMA invert [11]\n0=normal 1=invert"),
    ("psec4_st_sign",    "ST sign [10]\n0=above 1=below threshold"),
    ("psec4_coinc_min",  "Coinc. min [9:0]\nmin channels firing simultaneously"),
]
for lid in lappd_ids:
    for bid in boards:
        d = lbd(df, lid, bid)
        if d.empty: continue
        fig, axes = plt.subplots(1, 4, figsize=(18, 4))
        fig.suptitle(
            "Word 87 (PSEC4 only) — packed trigger config | LAPPD %d Board %d\n"
            "[15:12] mode  |  [11] SMA invert  |  [10] ST sign  |  [9:0] coinc min"
            % (lid, bid),
            fontsize=11, fontweight="bold")
        for fi, (col, ftitle) in enumerate(w87_fields):
            ax = axes[fi]
            if col in d.columns:
                ax.plot(d["global_entry"], d[col],
                        marker="o", ms=3, lw=1.0,
                        color=chip_colors[4], alpha=0.85)
            ax.set_title(ftitle, fontsize=8)
            ax.set_xlabel("Entry", fontsize=7)
            if fi == 0: ax.set_ylabel("value", fontsize=8)
            if fi == 0:  # trig_mode: add reference lines for all valid modes
                mode_labels = {0:"off", 1:"sw", 2:"ACC SMA", 3:"ACDC SMA",
                               4:"self", 5:"self+ACC", 6:"self+ACDC",
                               7:"ACC+ACDC val", 8:"ACDC+ACC val"}
                ax.set_ylim(-0.5, 9)
                ax.set_yticks(list(mode_labels.keys()))
                ax.set_yticklabels(["%d=%s"%(k,v) for k,v in mode_labels.items()],
                                   fontsize=6)
                for m in mode_labels:
                    ax.axhline(m, color="gray", lw=0.4, ls=":", alpha=0.5)
            if fi in [1, 2]:
                ax.set_ylim(-0.2, 1.4); ax.set_yticks([0, 1])
                ax.set_yticklabels(["0","1"], fontsize=7)
            ax.grid(True, alpha=0.3); ax.tick_params(labelsize=7)
        plt.tight_layout()
        savefig(fig, "word87_psec4_decoded_lappd%d_bd%d.png" % (lid, bid))

# ══════════════════════════════════════════════════════════════════════════════
# 9. VCDL COUNT
# ══════════════════════════════════════════════════════════════════════════════
print("Plotting VCDL ...")
plot_per_chip_per_lappd_board(
    "psec{chip}_vcdl_count", "VCDL Count (fine timing delay)", "Count", "vcdl")
plot_per_chip_per_lappd_board_all_chips_overlay(
    "psec{chip}_vcdl_count", "VCDL Count — all", "Count", "vcdl")

# ══════════════════════════════════════════════════════════════════════════════
# 10. SELF-TRIGGER RATE per CHANNEL (6 channels x 5 chips)
# ══════════════════════════════════════════════════════════════════════════════
print("Plotting self-trigger rates per channel ...")
for lid in lappd_ids:
    for bid in boards:
        d = lbd(df, lid, bid)
        if d.empty: continue
        fig, axes = plt.subplots(5, 6, figsize=(20, 14), sharex=True, sharey=False)
        fig.suptitle("Self-Trigger Rate per Channel | LAPPD %d Board %d" % (lid, bid),
                     fontsize=13, fontweight="bold")
        for chip in PSEC:
            for ch in range(6):
                ax  = axes[chip, ch]
                col = "psec%d_ch%d_trig_rate" % (chip, ch)
                ax.plot(d["global_entry"], d[col], marker="o", ms=3, color=chip_colors[chip])
                ax.set_title("P%d ch%d" % (chip, ch), fontsize=8)
                ax.grid(True, alpha=0.3)
                if ch == 0: ax.set_ylabel("PSEC%d" % chip, fontsize=8)
                if chip == 4: ax.set_xlabel("Entry", fontsize=8)
        plt.tight_layout()
        savefig(fig, "trigrate_lappd%d_bd%d.png" % (lid, bid))

# ── Total trigger rate per chip ───────────────────────────────────────────────
for lid in lappd_ids:
    for bid in boards:
        d = lbd(df, lid, bid)
        if d.empty: continue
        fig, axes = plt.subplots(1, 5, figsize=(20, 4), sharey=False)
        fig.suptitle("Total Trigger Rate per PSEC chip | LAPPD %d Board %d" % (lid, bid),
                     fontweight="bold")
        for chip in PSEC:
            ax    = axes[chip]
            total = sum(d["psec%d_ch%d_trig_rate" % (chip, ch)] for ch in range(6))
            ax.plot(d["global_entry"], total, marker="o", ms=4, color=chip_colors[chip])
            ax.set_title("PSEC %d" % chip); ax.set_xlabel("Global entry")
            if chip == 0: ax.set_ylabel("Sum of 6 ch rates")
            ax.grid(True, alpha=0.3)
        plt.tight_layout()
        savefig(fig, "trigrate_total_lappd%d_bd%d.png" % (lid, bid))

# ── Trigger rate heatmap ──────────────────────────────────────────────────────
for lid in lappd_ids:
    for bid in boards:
        d = lbd(df, lid, bid)
        if d.empty: continue
        matrix = np.zeros((5, 6))
        for chip in PSEC:
            for ch in range(6):
                matrix[chip, ch] = d["psec%d_ch%d_trig_rate" % (chip, ch)].mean()
        fig, ax = plt.subplots(figsize=(8, 4))
        im = ax.imshow(matrix, aspect="auto", cmap="hot_r")
        ax.set_xticks(range(6)); ax.set_xticklabels(["ch%d" % c for c in range(6)])
        ax.set_yticks(range(5)); ax.set_yticklabels(["PSEC%d" % p for p in range(5)])
        ax.set_title("Avg Trigger Rate Heatmap | LAPPD %d Board %d" % (lid, bid))
        plt.colorbar(im, ax=ax, label="Mean trigger rate")
        for chip in PSEC:
            for ch in range(6):
                tc = "white" if matrix[chip,ch] > matrix.max()*0.5 else "black"
                ax.text(ch, chip, "%.0f" % matrix[chip,ch],
                        ha="center", va="center", fontsize=8, color=tc)
        plt.tight_layout()
        savefig(fig, "trigrate_heatmap_lappd%d_bd%d.png" % (lid, bid))

# ══════════════════════════════════════════════════════════════════════════════
# 11. COMBINED TRIGGER RATE
# ══════════════════════════════════════════════════════════════════════════════
print("Plotting combined trigger rate ...")
fig, ax = plt.subplots(figsize=(10, 4))
fig.suptitle("Combined Trigger Rate", fontweight="bold")
for lid in lappd_ids:
    lcol = lappd_colors[lappd_ids.index(lid) % len(lappd_colors)]
    for bid in boards:
        d = lbd(df, lid, bid)
        if d.empty: continue
        mk = board_markers[bid % len(board_markers)]
        ax.plot(d["global_entry"], d["combined_trig_rate"],
                marker=mk, ms=4, color=lcol, alpha=0.8, label="L%d Bd%d" % (lid, bid))
ax.set_xlabel("Global entry"); ax.set_ylabel("Combined trigger rate")
ax.legend(fontsize=8); ax.grid(True, alpha=0.3)
plt.tight_layout()
savefig(fig, "combined_trigrate.png")

# ══════════════════════════════════════════════════════════════════════════════
# 12. COMPLETE OVERVIEW DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
print("Plotting complete overview dashboard ...")
for lid in lappd_ids:
    for bid in boards:
        d = lbd(df, lid, bid)
        if d.empty: continue

        fig = plt.figure(figsize=(24, 30))
        fig.suptitle("Complete Metadata Overview | LAPPD %d Board %d" % (lid, bid),
                     fontsize=16, fontweight="bold", y=1.005)
        gs = gridspec.GridSpec(8, 5, figure=fig, hspace=0.6, wspace=0.38)

        # Row 0: beamgate / timestamp / clock cycle
        ax_bg = fig.add_subplot(gs[0, :2])
        ax_ts = fig.add_subplot(gs[0, 2:4])
        ax_cc = fig.add_subplot(gs[0, 4])
        ax_bg.plot(d["global_entry"], d["beamgate_ns"]/1e9,
                   marker="o", ms=3, color="steelblue")
        ax_bg.set_title("Beamgate [s]"); ax_bg.grid(True, alpha=0.3)
        ax_bg.set_xlabel("Global entry")
        ax_ts.plot(d["global_entry"], d["timestamp_ns"]/1e9,
                   marker="o", ms=3, color="darkorange")
        ax_ts.set_title("Timestamp [s]"); ax_ts.grid(True, alpha=0.3)
        ax_ts.set_xlabel("Global entry")
        ax_cc.bar(d["global_entry"], d["clockcycle"].astype(float),
                  color="teal", alpha=0.8)
        ax_cc.set_title("Clock cycle (0-7)")
        ax_cc.set_ylim(0, 8); ax_cc.set_yticks(range(8))
        ax_cc.grid(True, alpha=0.3); ax_cc.set_xlabel("Global entry")

        # Rows 1-5: one per PSEC chip
        for chip in PSEC:
            row = chip + 1
            col = chip_colors[chip]

            # col 0: Wilkinson deviation
            ax = fig.add_subplot(gs[row, 0])
            dev = d["psec%d_wilkinson_current" % chip] - d["psec%d_wilkinson_target" % chip]
            ax.plot(d["global_entry"], dev, marker="o", ms=3, color=col)
            ax.axhline(0, color="black", ls="--", lw=1, alpha=0.5)
            ax.set_title("P%d Wilkinson dev" % chip, fontsize=9)
            ax.set_ylabel("cur−tgt", fontsize=7); ax.grid(True, alpha=0.3)
            ax.tick_params(labelsize=6)
            if chip == 4: ax.set_xlabel("Entry", fontsize=7)

            # col 1: Vbias + threshold
            ax = fig.add_subplot(gs[row, 1])
            ax.plot(d["global_entry"], d["psec%d_vbias" % chip],
                    marker="o", ms=3, color=col, label="vbias")
            ax.plot(d["global_entry"], d["psec%d_selftrig_threshold" % chip],
                    marker="s", ms=3, color="gray", label="thr")
            ax.set_title("P%d Vbias & Thr" % chip, fontsize=9)
            ax.set_ylabel("ADC", fontsize=7); ax.legend(fontsize=6)
            ax.grid(True, alpha=0.3); ax.tick_params(labelsize=6)
            if chip == 4: ax.set_xlabel("Entry", fontsize=7)

            # col 2: PROVDD + number of mask channels ON
            ax  = fig.add_subplot(gs[row, 2])
            ax.plot(d["global_entry"], d["psec%d_provdd" % chip],
                    marker="o", ms=3, color=col, label="provdd")
            mask     = d["psec%d_selftrig_mask" % chip]
            n_active = sum((np.right_shift(mask.values.astype(int), ch)) & 1
                           for ch in range(6))
            ax2 = ax.twinx()
            ax2.plot(d["global_entry"], n_active,
                     marker="s", ms=3, color="red", alpha=0.6, label="ch ON")
            ax2.set_ylim(-0.5, 6.5); ax2.set_yticks(range(7))
            ax2.set_ylabel("# ch ON", fontsize=6, color="red")
            ax.set_title("P%d PROVDD & Mask" % chip, fontsize=9)
            ax.set_ylabel("PROVDD", fontsize=6, color=col)
            ax.grid(True, alpha=0.3); ax.tick_params(labelsize=6)
            if chip == 4: ax.set_xlabel("Entry", fontsize=7)

            # col 3: VCDL
            ax = fig.add_subplot(gs[row, 3])
            ax.plot(d["global_entry"], d["psec%d_vcdl_count" % chip],
                    marker="o", ms=3, color=col)
            ax.set_title("P%d VCDL" % chip, fontsize=9)
            ax.set_ylabel("count", fontsize=7); ax.grid(True, alpha=0.3)
            ax.tick_params(labelsize=6)
            if chip == 4: ax.set_xlabel("Entry", fontsize=7)

            # col 4: trig rates all 6 channels
            ax = fig.add_subplot(gs[row, 4])
            for ch in range(6):
                ax.plot(d["global_entry"], d["psec%d_ch%d_trig_rate" % (chip, ch)],
                        marker="o", ms=2, label="ch%d" % ch, alpha=0.8)
            ax.set_title("P%d Trig rates" % chip, fontsize=9)
            ax.legend(fontsize=6, ncol=3); ax.grid(True, alpha=0.3)
            ax.tick_params(labelsize=6)
            if chip == 4: ax.set_xlabel("Entry", fontsize=7)

        # Row 7: combined trig rate + word 87 decoded (PSEC4 only)
        ax = fig.add_subplot(gs[7, :2])
        ax.plot(d["global_entry"], d["combined_trig_rate"],
                marker="o", ms=4, color="black")
        ax.set_title("Combined trigger rate")
        ax.set_xlabel("Global entry"); ax.grid(True, alpha=0.3)

        ax = fig.add_subplot(gs[7, 2:])
        for col, lbl in [("psec4_trig_mode","mode"),("psec4_sma_invert","SMA inv"),
                         ("psec4_st_sign","sign"),  ("psec4_coinc_min","coinc")]:
            if col in d.columns:
                ax.plot(d["global_entry"], d[col],
                        marker="o", ms=3, label=lbl, alpha=0.85)
        ax.set_title("Word 87 decoded (PSEC4 only): mode / SMA inv / sign / coinc")
        ax.set_xlabel("Global entry")
        ax.legend(fontsize=8, ncol=4); ax.grid(True, alpha=0.3)

        plt.tight_layout()
        savefig(fig, "dashboard_lappd%d_bd%d.png" % (lid, bid))

# ── Final summary ─────────────────────────────────────────────────────────────
all_plots = sorted(glob.glob("plots/*.png"))
print("\nAll done! %d plots written to ./plots/" % len(all_plots))
print("LAPPD IDs : %s" % lappd_ids)
print("Board IDs : %s" % boards)
for lid in lappd_ids:
    for bid in boards:
        n = len(lbd(df, lid, bid))
        print("  LAPPD %d Board %d : %d rows" % (lid, bid, n))
