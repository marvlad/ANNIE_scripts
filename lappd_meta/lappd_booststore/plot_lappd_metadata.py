import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

# ── Load ──────────────────────────────────────────────────────────────────────
df = pd.read_csv("lappd_metadata.csv")

lappd_ids = sorted(df["lappd_id"].unique())
boards     = sorted(df["board_id"].unique())
PSEC       = list(range(5))

# Color scheme: one color per LAPPD, marker per board
lappd_colors  = ["tab:blue", "tab:orange", "tab:green", "tab:red"]
board_markers = ["o", "s"]   # board 0 = circle, board 1 = square
chip_colors   = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple"]

def lappd_df(df, lid):
    return df[df["lappd_id"] == lid].sort_values("global_entry")

def lappd_board_df(df, lid, bid):
    return df[(df["lappd_id"] == lid) & (df["board_id"] == bid)].sort_values("global_entry")

def savefig(fig, name):
    fig.savefig(name, dpi=150, bbox_inches="tight")
    print(f"  saved → {name}")

# ══════════════════════════════════════════════════════════════════════════════
# 1. TIMESTAMPS  — one subplot per LAPPD
# ══════════════════════════════════════════════════════════════════════════════
print("Plotting timestamps …")
fig, axes = plt.subplots(len(lappd_ids), 2,
                         figsize=(14, 5 * len(lappd_ids)))
if len(lappd_ids) == 1:
    axes = [axes]   # ensure 2-D indexing works
fig.suptitle("Timestamps per Event", fontsize=14, fontweight="bold")

for row, lid in enumerate(lappd_ids):
    col = lappd_colors[row % len(lappd_colors)]
    for bid in boards:
        d = lappd_board_df(df, lid, bid)
        if d.empty: continue
        mk = board_markers[bid % len(board_markers)]
        lbl = f"Bd{bid}"
        axes[row][0].plot(d["global_entry"], d["beamgate_ns"] / 1e9,
                          marker=mk, color=col, alpha=0.7, label=lbl)
        axes[row][1].plot(d["global_entry"], d["timestamp_ns"] / 1e9,
                          marker=mk, color=col, alpha=0.7, label=lbl)

    axes[row][0].set_title(f"Beamgate — LAPPD {lid}")
    axes[row][0].set_xlabel("Global entry"); axes[row][0].set_ylabel("Time [s]")
    axes[row][0].legend(fontsize=8); axes[row][0].grid(True, alpha=0.3)

    axes[row][1].set_title(f"Timestamp — LAPPD {lid}")
    axes[row][1].set_xlabel("Global entry"); axes[row][1].set_ylabel("Time [s]")
    axes[row][1].legend(fontsize=8); axes[row][1].grid(True, alpha=0.3)

plt.tight_layout()
savefig(fig, "plot_timestamps.png")
plt.close()

# ── timestamp diff between boards (per LAPPD) ────────────────────────────────
if len(boards) >= 2:
    fig, axes = plt.subplots(len(lappd_ids), 2,
                             figsize=(12, 4 * len(lappd_ids)))
    if len(lappd_ids) == 1: axes = [axes]
    fig.suptitle("Timestamp difference Board 0 − Board 1", fontweight="bold")

    for row, lid in enumerate(lappd_ids):
        d0 = lappd_board_df(df, lid, 0).set_index("global_entry")
        d1 = lappd_board_df(df, lid, 1).set_index("global_entry")
        common = d0.index.intersection(d1.index)
        if len(common) == 0:
            axes[row][0].set_title(f"LAPPD {lid} — no common entries")
            continue
        bg_diff = d0.loc[common, "beamgate_ns"]  - d1.loc[common, "beamgate_ns"]
        ts_diff = d0.loc[common, "timestamp_ns"] - d1.loc[common, "timestamp_ns"]

        col = lappd_colors[row % len(lappd_colors)]
        axes[row][0].bar(common, bg_diff, color=col, alpha=0.8)
        axes[row][0].set_title(f"Beamgate diff [ns] — LAPPD {lid}")
        axes[row][0].set_xlabel("Global entry"); axes[row][0].set_ylabel("Δ [ns]")
        axes[row][0].grid(True, alpha=0.3)

        axes[row][1].bar(common, ts_diff, color=col, alpha=0.8)
        axes[row][1].set_title(f"Timestamp diff [ns] — LAPPD {lid}")
        axes[row][1].set_xlabel("Global entry"); axes[row][1].set_ylabel("Δ [ns]")
        axes[row][1].grid(True, alpha=0.3)

    plt.tight_layout()
    savefig(fig, "plot_timestamp_diff.png")
    plt.close()

# ══════════════════════════════════════════════════════════════════════════════
# 2. CLOCK CYCLE
# ══════════════════════════════════════════════════════════════════════════════
print("Plotting clock cycle …")
ncols = len(boards)
fig, axes = plt.subplots(len(lappd_ids), ncols,
                         figsize=(6 * ncols, 4 * len(lappd_ids)))
if len(lappd_ids) == 1: axes = [axes]
fig.suptitle("Clock Cycle (0–7) per Event", fontweight="bold")

for row, lid in enumerate(lappd_ids):
    col = lappd_colors[row % len(lappd_colors)]
    for bid in boards:
        d = lappd_board_df(df, lid, bid)
        ax = axes[row][bid] if ncols > 1 else axes[row]
        if not d.empty:
            ax.bar(d["global_entry"], d["clockcycle"], color=col, alpha=0.8)
        ax.set_title(f"LAPPD {lid} — Board {bid}")
        ax.set_xlabel("Global entry"); ax.set_ylabel("Clock cycle")
        ax.set_ylim(0, 7.5); ax.grid(True, alpha=0.3)

plt.tight_layout()
savefig(fig, "plot_clockcycle.png")
plt.close()

# ══════════════════════════════════════════════════════════════════════════════
# 3. WILKINSON COUNTS
# ══════════════════════════════════════════════════════════════════════════════
print("Plotting Wilkinson counts …")
fig, axes = plt.subplots(len(lappd_ids) * len(boards), len(PSEC),
                         figsize=(18, 4 * len(lappd_ids) * len(boards)),
                         sharex=False)
if axes.ndim == 1: axes = axes.reshape(1, -1)
fig.suptitle("Wilkinson Feedback Count (current vs target)", fontweight="bold")

row = 0
for lid in lappd_ids:
    col = lappd_colors[lappd_ids.index(lid) % len(lappd_colors)]
    for bid in boards:
        d = lappd_board_df(df, lid, bid)
        for chip in PSEC:
            ax = axes[row, chip]
            if not d.empty:
                ax.plot(d["global_entry"], d[f"psec{chip}_wilkinson_current"],
                        marker="o", ms=4, color=col, label="current")
                ax.axhline(d[f"psec{chip}_wilkinson_target"].iloc[0],
                           color="black", ls="--", lw=1, label="target")
            ax.set_title(f"L{lid} Bd{bid} P{chip}", fontsize=8)
            ax.grid(True, alpha=0.3)
            if chip == 0: ax.set_ylabel(f"L{lid} Bd{bid}", fontsize=8)
            if row == axes.shape[0]-1: ax.set_xlabel("Entry", fontsize=8)
        row += 1

handles = [plt.Line2D([0],[0], color="gray",  marker="o", label="current"),
           plt.Line2D([0],[0], color="black", ls="--",    label="target")]
fig.legend(handles=handles, loc="lower right", fontsize=9)
plt.tight_layout()
savefig(fig, "plot_wilkinson.png")
plt.close()

# ══════════════════════════════════════════════════════════════════════════════
# 4. VBIAS
# ══════════════════════════════════════════════════════════════════════════════
print("Plotting Vbias …")
fig, axes = plt.subplots(1, len(PSEC), figsize=(16, 4), sharey=True)
fig.suptitle("Vbias (Pedestal) Setting per PSEC chip", fontweight="bold")

for chip in PSEC:
    ax = axes[chip]
    for lid in lappd_ids:
        col = lappd_colors[lappd_ids.index(lid) % len(lappd_colors)]
        for bid in boards:
            d = lappd_board_df(df, lid, bid)
            if d.empty: continue
            mk = board_markers[bid % len(board_markers)]
            ax.plot(d["global_entry"], d[f"psec{chip}_vbias"],
                    marker=mk, color=col, alpha=0.8,
                    label=f"L{lid} Bd{bid}")
    ax.set_title(f"PSEC {chip}")
    ax.set_xlabel("Global entry")
    if chip == 0: ax.set_ylabel("Vbias [ADC counts]")
    ax.grid(True, alpha=0.3)

axes[-1].legend(fontsize=7)
plt.tight_layout()
savefig(fig, "plot_vbias.png")
plt.close()

# ══════════════════════════════════════════════════════════════════════════════
# 5. SELF-TRIGGER THRESHOLD
# ══════════════════════════════════════════════════════════════════════════════
print("Plotting self-trigger threshold …")
fig, axes = plt.subplots(1, len(PSEC), figsize=(16, 4), sharey=True)
fig.suptitle("Self-Trigger Threshold per PSEC chip", fontweight="bold")

for chip in PSEC:
    ax = axes[chip]
    for lid in lappd_ids:
        col = lappd_colors[lappd_ids.index(lid) % len(lappd_colors)]
        for bid in boards:
            d = lappd_board_df(df, lid, bid)
            if d.empty: continue
            mk = board_markers[bid % len(board_markers)]
            ax.plot(d["global_entry"], d[f"psec{chip}_selftrig_threshold"],
                    marker=mk, color=col, alpha=0.8,
                    label=f"L{lid} Bd{bid}")
    ax.set_title(f"PSEC {chip}")
    ax.set_xlabel("Global entry")
    if chip == 0: ax.set_ylabel("Threshold [ADC counts]")
    ax.grid(True, alpha=0.3)

axes[-1].legend(fontsize=7)
plt.tight_layout()
savefig(fig, "plot_selftrig_threshold.png")
plt.close()

# ══════════════════════════════════════════════════════════════════════════════
# 6. VCDL COUNTS
# ══════════════════════════════════════════════════════════════════════════════
print("Plotting VCDL counts …")
fig, axes = plt.subplots(1, len(PSEC), figsize=(16, 4))
fig.suptitle("VCDL Count per PSEC chip", fontweight="bold")

for chip in PSEC:
    ax = axes[chip]
    for lid in lappd_ids:
        col = lappd_colors[lappd_ids.index(lid) % len(lappd_colors)]
        for bid in boards:
            d = lappd_board_df(df, lid, bid)
            if d.empty: continue
            mk = board_markers[bid % len(board_markers)]
            ax.plot(d["global_entry"], d[f"psec{chip}_vcdl_count"],
                    marker=mk, color=col, alpha=0.8,
                    label=f"L{lid} Bd{bid}")
    ax.set_title(f"PSEC {chip}")
    ax.set_xlabel("Global entry")
    if chip == 0: ax.set_ylabel("VCDL count")
    ax.grid(True, alpha=0.3)

axes[-1].legend(fontsize=7)
plt.tight_layout()
savefig(fig, "plot_vcdl.png")
plt.close()

# ══════════════════════════════════════════════════════════════════════════════
# 7. SELF-TRIGGER RATE COUNTS — one figure per LAPPD per board
# ══════════════════════════════════════════════════════════════════════════════
print("Plotting self-trigger rate counts …")
for lid in lappd_ids:
    col = lappd_colors[lappd_ids.index(lid) % len(lappd_colors)]
    for bid in boards:
        d = lappd_board_df(df, lid, bid)
        if d.empty:
            print(f"  Skipping LAPPD {lid} Board {bid} — no data")
            continue
        fig, axes = plt.subplots(5, 6, figsize=(18, 12),
                                 sharex=True, sharey=True)
        fig.suptitle(f"Self-Trigger Rate Counts — LAPPD {lid}  Board {bid}",
                     fontsize=13, fontweight="bold")
        for chip in PSEC:
            for ch in range(6):
                ax = axes[chip, ch]
                ax.plot(d["global_entry"], d[f"psec{chip}_ch{ch}_trig_rate"],
                        marker="o", ms=4, color=chip_colors[chip])
                ax.set_title(f"P{chip}-ch{ch}", fontsize=8)
                ax.grid(True, alpha=0.3)
                if ch == 0:   ax.set_ylabel(f"PSEC{chip}", fontsize=8)
                if chip == 4: ax.set_xlabel("Entry", fontsize=8)
        plt.tight_layout()
        savefig(fig, f"plot_trigrate_lappd{lid}_board{bid}.png")
        plt.close()

# ══════════════════════════════════════════════════════════════════════════════
# 8. SUMMARY DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
print("Plotting summary dashboard …")
fig = plt.figure(figsize=(20, 12))
fig.suptitle("LAPPD Metadata Summary Dashboard", fontsize=15, fontweight="bold")
gs = gridspec.GridSpec(4, 4, figure=fig, hspace=0.5, wspace=0.35)

# Row 0: timestamps all LAPPDs overlaid
ax_bg = fig.add_subplot(gs[0, :2])
ax_ts = fig.add_subplot(gs[0, 2:])
for lid in lappd_ids:
    col = lappd_colors[lappd_ids.index(lid) % len(lappd_colors)]
    for bid in boards:
        d = lappd_board_df(df, lid, bid)
        if d.empty: continue
        mk = board_markers[bid % len(board_markers)]
        ax_bg.plot(d["global_entry"], d["beamgate_ns"]/1e9,
                   marker=mk, color=col, alpha=0.7, label=f"L{lid} Bd{bid}")
        ax_ts.plot(d["global_entry"], d["timestamp_ns"]/1e9,
                   marker=mk, color=col, alpha=0.7, label=f"L{lid} Bd{bid}")
ax_bg.set_title("Beamgate [s]"); ax_bg.legend(fontsize=7, ncol=2)
ax_bg.grid(True, alpha=0.3); ax_bg.set_xlabel("Global entry")
ax_ts.set_title("Timestamp [s]"); ax_ts.legend(fontsize=7, ncol=2)
ax_ts.grid(True, alpha=0.3); ax_ts.set_xlabel("Global entry")

# Row 1: Wilkinson current per LAPPD (board 0, all chips)
for lidx, lid in enumerate(lappd_ids[:2]):   # max 2 LAPPDs in row
    col = lappd_colors[lidx % len(lappd_colors)]
    ax = fig.add_subplot(gs[1, lidx*2:(lidx+1)*2])
    d = lappd_board_df(df, lid, 0)
    if not d.empty:
        for chip in PSEC:
            ax.plot(d["global_entry"], d[f"psec{chip}_wilkinson_current"],
                    marker="o", ms=3, color=chip_colors[chip], label=f"P{chip}")
    ax.set_title(f"Wilkinson current — LAPPD {lid} Bd0")
    ax.legend(fontsize=7, ncol=5); ax.grid(True, alpha=0.3)
    ax.set_xlabel("Global entry")

# Row 2: VCDL per LAPPD (board 0, all chips)
for lidx, lid in enumerate(lappd_ids[:2]):
    col = lappd_colors[lidx % len(lappd_colors)]
    ax = fig.add_subplot(gs[2, lidx*2:(lidx+1)*2])
    d = lappd_board_df(df, lid, 0)
    if not d.empty:
        for chip in PSEC:
            ax.plot(d["global_entry"], d[f"psec{chip}_vcdl_count"],
                    marker="o", ms=3, color=chip_colors[chip], label=f"P{chip}")
    ax.set_title(f"VCDL count — LAPPD {lid} Bd0")
    ax.legend(fontsize=7, ncol=5); ax.grid(True, alpha=0.3)
    ax.set_xlabel("Global entry")

# Row 3: clock cycle + vbias + combined trig rate
ax_cc = fig.add_subplot(gs[3, :2])
for lid in lappd_ids:
    col = lappd_colors[lappd_ids.index(lid) % len(lappd_colors)]
    for bid in boards:
        d = lappd_board_df(df, lid, bid)
        if d.empty: continue
        mk = board_markers[bid % len(board_markers)]
        ax_cc.scatter(d["global_entry"], d["clockcycle"],
                      color=col, marker=mk, alpha=0.7, s=20,
                      label=f"L{lid} Bd{bid}")
ax_cc.set_title("Clock cycle (0–7)"); ax_cc.set_ylim(0, 8)
ax_cc.legend(fontsize=7, ncol=2); ax_cc.grid(True, alpha=0.3)
ax_cc.set_xlabel("Global entry")

ax_ctr = fig.add_subplot(gs[3, 2:])
for lid in lappd_ids:
    col = lappd_colors[lappd_ids.index(lid) % len(lappd_colors)]
    for bid in boards:
        d = lappd_board_df(df, lid, bid)
        if d.empty: continue
        mk = board_markers[bid % len(board_markers)]
        ax_ctr.plot(d["global_entry"], d["combined_trig_rate"],
                    marker=mk, color=col, alpha=0.7, label=f"L{lid} Bd{bid}")
ax_ctr.set_title("Combined trigger rate")
ax_ctr.legend(fontsize=7, ncol=2); ax_ctr.grid(True, alpha=0.3)
ax_ctr.set_xlabel("Global entry")

savefig(fig, "plot_dashboard.png")
plt.close()

# ── Print summary ─────────────────────────────────────────────────────────────
print("\nAll done! Files written:")
files = ["plot_timestamps.png", "plot_timestamp_diff.png",
         "plot_clockcycle.png", "plot_wilkinson.png",
         "plot_vbias.png", "plot_selftrig_threshold.png",
         "plot_vcdl.png", "plot_dashboard.png"]
for lid in lappd_ids:
    for bid in boards:
        files.append(f"plot_trigrate_lappd{lid}_board{bid}.png")
for f in files:
    print(f"  {f}")

print(f"\nLAPPD IDs found in CSV: {lappd_ids}")
print(f"Board IDs found in CSV: {boards}")
for lid in lappd_ids:
    n = len(lappd_df(df, lid))
    print(f"  LAPPD {lid}: {n} rows in CSV")
