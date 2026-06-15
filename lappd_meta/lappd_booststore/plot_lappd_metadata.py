import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

# ── Load ──────────────────────────────────────────────────────────────────────
df = pd.read_csv("lappd_metadata.csv")

boards  = sorted(df["board_id"].unique())
entries = sorted(df["global_entry"].unique())
colors  = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple"]
markers = ["o", "s"]          # board 0 = circle, board 1 = square
PSEC    = list(range(5))

def board_df(df, bid):
    return df[df["board_id"] == bid].sort_values("global_entry")

# ── Helper ────────────────────────────────────────────────────────────────────
def savefig(fig, name):
    fig.savefig(name, dpi=150, bbox_inches="tight")
    print(f"  saved → {name}")

# ══════════════════════════════════════════════════════════════════════════════
# 1. TIMESTAMPS
# ══════════════════════════════════════════════════════════════════════════════
print("Plotting timestamps …")
fig, axes = plt.subplots(2, 2, figsize=(14, 8))
fig.suptitle("Timestamps per Event", fontsize=14, fontweight="bold")

for bid, (ax_bg, ax_ts) in zip(boards, [(axes[0,0], axes[0,1]),
                                          (axes[1,0], axes[1,1])]):
    d = board_df(df, bid)
    ax_bg.plot(d["global_entry"], d["beamgate_ns"] / 1e9, marker=markers[bid],
               color=colors[bid], label=f"Board {bid}")
    ax_bg.set_title(f"Beamgate timestamp — Board {bid}")
    ax_bg.set_xlabel("Entry"); ax_bg.set_ylabel("Beamgate [s]")
    ax_bg.grid(True, alpha=0.3)

    ax_ts.plot(d["global_entry"], d["timestamp_ns"] / 1e9, marker=markers[bid],
               color=colors[bid], label=f"Board {bid}")
    ax_ts.set_title(f"LAPPD timestamp — Board {bid}")
    ax_ts.set_xlabel("Entry"); ax_ts.set_ylabel("Timestamp [s]")
    ax_ts.grid(True, alpha=0.3)

plt.tight_layout()
savefig(fig, "plot_timestamps.png")
plt.close()

# ── timestamp diff between boards ────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
fig.suptitle("Timestamp difference Board 0 − Board 1", fontweight="bold")

d0 = board_df(df, 0).set_index("global_entry")
d1 = board_df(df, 1).set_index("global_entry")
common = d0.index.intersection(d1.index)

bg_diff = (d0.loc[common, "beamgate_ns"] - d1.loc[common, "beamgate_ns"])
ts_diff = (d0.loc[common, "timestamp_ns"] - d1.loc[common, "timestamp_ns"])

axes[0].bar(common, bg_diff, color="steelblue")
axes[0].set_title("Beamgate diff [ns]")
axes[0].set_xlabel("Entry"); axes[0].set_ylabel("Δ [ns]")
axes[0].grid(True, alpha=0.3)

axes[1].bar(common, ts_diff, color="darkorange")
axes[1].set_title("Timestamp diff [ns]")
axes[1].set_xlabel("Entry"); axes[1].set_ylabel("Δ [ns]")
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
savefig(fig, "plot_timestamp_diff.png")
plt.close()

# ══════════════════════════════════════════════════════════════════════════════
# 2. CLOCK CYCLE
# ══════════════════════════════════════════════════════════════════════════════
print("Plotting clock cycle …")
fig, axes = plt.subplots(1, 2, figsize=(12, 4)) 
fig.suptitle("Clock Cycle (0–7) per Event", fontweight="bold")

for bid, ax in zip(boards, axes):
    d = board_df(df, bid)
    ax.bar(d["global_entry"], d["clockcycle"], color=colors[bid], alpha=0.8)
    ax.set_title(f"Board {bid}")
    ax.set_xlabel("Entry"); ax.set_ylabel("Clock cycle")
    ax.set_ylim(0, 7.5)
    ax.grid(True, alpha=0.3)

plt.tight_layout()
savefig(fig, "plot_clockcycle.png")
plt.close()

# ══════════════════════════════════════════════════════════════════════════════
# 3. WILKINSON COUNTS (current vs target) — all chips, both boards
# ══════════════════════════════════════════════════════════════════════════════
print("Plotting Wilkinson counts …")
fig, axes = plt.subplots(len(boards), len(PSEC), figsize=(18, 6), 
                         sharex=True)
fig.suptitle("Wilkinson Feedback Count  (current vs target)", fontweight="bold")

for row, bid in enumerate(boards):
    d = board_df(df, bid)
    for chip in PSEC:
        ax = axes[row, chip]
        cur = f"psec{chip}_wilkinson_current"
        tgt = f"psec{chip}_wilkinson_target"
        ax.plot(d["global_entry"], d[cur], marker="o", ms=5,
                color=colors[chip], label="current")
        ax.axhline(d[tgt].iloc[0], color="black", ls="--",
                   lw=1, label="target")
        ax.set_title(f"Bd{bid} PSEC{chip}", fontsize=9)
        ax.grid(True, alpha=0.3)
        if chip == 0:
            ax.set_ylabel(f"Board {bid}\nADC counts")
        if row == len(boards)-1:
            ax.set_xlabel("Entry")

handles = [plt.Line2D([0],[0], color="gray",  marker="o", label="current"),
           plt.Line2D([0],[0], color="black", ls="--",    label="target")]
fig.legend(handles=handles, loc="lower right", fontsize=9)
plt.tight_layout()
savefig(fig, "plot_wilkinson.png")
plt.close()

# ══════════════════════════════════════════════════════════════════════════════
# 4. VBIAS / PEDESTAL
# ══════════════════════════════════════════════════════════════════════════════
print("Plotting Vbias …")
fig, axes = plt.subplots(1, len(PSEC), figsize=(16, 4), sharey=True)
fig.suptitle("Vbias (Pedestal) Setting per PSEC chip", fontweight="bold")

for chip in PSEC:
    ax = axes[chip]
    for bid in boards:
        d = board_df(df, bid)
        ax.plot(d["global_entry"], d[f"psec{chip}_vbias"],
                marker=markers[bid], color=colors[bid],
                label=f"Board {bid}", alpha=0.8)
    ax.set_title(f"PSEC {chip}")
    ax.set_xlabel("Entry")
    if chip == 0: ax.set_ylabel("Vbias [ADC counts]")
    ax.grid(True, alpha=0.3)

axes[-1].legend(fontsize=8)
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
    for bid in boards:
        d = board_df(df, bid)
        ax.plot(d["global_entry"], d[f"psec{chip}_selftrig_threshold"],
                marker=markers[bid], color=colors[bid],
                label=f"Board {bid}", alpha=0.8)
    ax.set_title(f"PSEC {chip}")
    ax.set_xlabel("Entry")
    if chip == 0: ax.set_ylabel("Threshold [ADC counts]")
    ax.grid(True, alpha=0.3)

axes[-1].legend(fontsize=8)
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
    for bid in boards:
        d = board_df(df, bid)
        ax.plot(d["global_entry"], d[f"psec{chip}_vcdl_count"],
                marker=markers[bid], color=colors[bid],
                label=f"Board {bid}", alpha=0.8)
    ax.set_title(f"PSEC {chip}")
    ax.set_xlabel("Entry")
    if chip == 0: ax.set_ylabel("VCDL count")
    ax.grid(True, alpha=0.3)

axes[-1].legend(fontsize=8)
plt.tight_layout()
savefig(fig, "plot_vcdl.png")
plt.close()

# ══════════════════════════════════════════════════════════════════════════════
# 7. SELF-TRIGGER RATE COUNTS  per channel (6 ch × 5 chips × 2 boards)
# ══════════════════════════════════════════════════════════════════════════════
print("Plotting self-trigger rate counts …")
for bid in boards:
    d = board_df(df, bid)
    fig, axes = plt.subplots(5, 6, figsize=(18, 12), sharex=True, sharey=True)
    fig.suptitle(f"Self-Trigger Rate Counts — Board {bid}  (PSEC × channel)",
                 fontsize=13, fontweight="bold")

    for chip in PSEC:
        for ch in range(6):
            ax = axes[chip, ch] 
            col = f"psec{chip}_ch{ch}_trig_rate"
            ax.plot(d["global_entry"], d[col], marker="o", ms=4,
                    color=colors[chip])
            ax.set_title(f"P{chip}-ch{ch}", fontsize=8)
            ax.grid(True, alpha=0.3)
            if ch == 0:   ax.set_ylabel(f"PSEC{chip}", fontsize=8)
            if chip == 4: ax.set_xlabel("Entry", fontsize=8)

    plt.tight_layout()
    savefig(fig, f"plot_trigrate_board{bid}.png")
    plt.close()

# ══════════════════════════════════════════════════════════════════════════════
# 8. SUMMARY DASHBOARD  (one page overview)
# ══════════════════════════════════════════════════════════════════════════════
print("Plotting summary dashboard …")
fig = plt.figure(figsize=(18, 10))
fig.suptitle("LAPPD Metadata Summary Dashboard", fontsize=15, fontweight="bold")
gs = gridspec.GridSpec(3, 4, figure=fig, hspace=0.45, wspace=0.35)

# Row 0: timestamps (both boards overlaid)
ax_bg = fig.add_subplot(gs[0, :2])
ax_ts = fig.add_subplot(gs[0, 2:])
for bid in boards:
    d = board_df(df, bid)
    ax_bg.plot(d["global_entry"], d["beamgate_ns"]/1e9,
               marker=markers[bid], color=colors[bid], label=f"Bd{bid}")
    ax_ts.plot(d["global_entry"], d["timestamp_ns"]/1e9,
               marker=markers[bid], color=colors[bid], label=f"Bd{bid}")
ax_bg.set_title("Beamgate [s]"); ax_bg.legend(fontsize=8); ax_bg.grid(True, alpha=0.3)
ax_ts.set_title("Timestamp [s]"); ax_ts.legend(fontsize=8); ax_ts.grid(True, alpha=0.3)

# Row 1: Wilkinson current (per chip, board 0 only for clarity)
ax_wlk = fig.add_subplot(gs[1, :2])
d0 = board_df(df, 0)
for chip in PSEC:
    ax_wlk.plot(d0["global_entry"], d0[f"psec{chip}_wilkinson_current"],
                marker="o", ms=4, color=colors[chip], label=f"PSEC{chip}")
ax_wlk.set_title("Wilkinson current — Board 0")
ax_wlk.legend(fontsize=7, ncol=5); ax_wlk.grid(True, alpha=0.3)

# Row 1: VCDL (per chip, board 0)
ax_vcdl = fig.add_subplot(gs[1, 2:])
for chip in PSEC:
    ax_vcdl.plot(d0["global_entry"], d0[f"psec{chip}_vcdl_count"],
                 marker="o", ms=4, color=colors[chip], label=f"PSEC{chip}")
ax_vcdl.set_title("VCDL count — Board 0")
ax_vcdl.legend(fontsize=7, ncol=5); ax_vcdl.grid(True, alpha=0.3)

# Row 2: clock cycle both boards
ax_cc0 = fig.add_subplot(gs[2, 0]) 
ax_cc1 = fig.add_subplot(gs[2, 1]) 
for bid, ax in zip(boards, [ax_cc0, ax_cc1]):
    d = board_df(df, bid)
    ax.bar(d["global_entry"], d["clockcycle"], color=colors[bid], alpha=0.8)
    ax.set_title(f"Clock cycle Bd{bid}"); ax.set_ylim(0,8); ax.grid(True,alpha=0.3)

# Row 2: vbias all chips board 0
ax_vb = fig.add_subplot(gs[2, 2]) 
for chip in PSEC:
    ax_vb.plot(d0["global_entry"], d0[f"psec{chip}_vbias"],
               marker="o", ms=4, color=colors[chip], label=f"P{chip}")
ax_vb.set_title("Vbias — Board 0"); ax_vb.legend(fontsize=7); ax_vb.grid(True,alpha=0.3)

# Row 2: combined trig rate
ax_ctr = fig.add_subplot(gs[2, 3]) 
for bid in boards:
    d = board_df(df, bid)
    ax_ctr.plot(d["global_entry"], d["combined_trig_rate"],
                marker=markers[bid], color=colors[bid], label=f"Bd{bid}")
ax_ctr.set_title("Combined trig rate"); ax_ctr.legend(fontsize=8); ax_ctr.grid(True,alpha=0.3)

savefig(fig, "plot_dashboard.png")
plt.close()

print("\nAll done! Files written:")
for f in ["plot_timestamps.png", "plot_timestamp_diff.png",
          "plot_clockcycle.png", "plot_wilkinson.png",
          "plot_vbias.png", "plot_selftrig_threshold.png",
          "plot_vcdl.png", "plot_trigrate_board0.png",
          "plot_trigrate_board1.png", "plot_dashboard.png"]:
    print(f"  {f}")
:set nonu     
