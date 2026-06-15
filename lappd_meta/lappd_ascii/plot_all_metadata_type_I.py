#!/usr/bin/env python3

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


INPUT_FILE = Path("data/Ascii20242904_084248.txt")

EVENT_SAMPLES = 256
N_COLUMNS = 63

COL_COUNTER = 0
COL_META_A = 31   # column 32
COL_META_B = 62   # column 63


# ------------------------------------------------------------
# Metadata word definitions
# ------------------------------------------------------------

META_WORDS = {
    0: "board_id",

    # PSEC chip 0
    1: "psec0_id",
    2: "psec0_wilkinson_current",
    3: "psec0_wilkinson_target",
    4: "psec0_vbias_pedestal",
    5: "psec0_self_trigger_threshold_setting",
    6: "psec0_provdd",
    7: "beamgate_timestamp_63_48",
    8: "psec0_selftrigger_mask",
    9: "psec0_selftrigger_threshold",
    10: "psec0_timestamp_15_0",
    11: "psec_event_count_15_0",
    12: "psec0_vcdl_15_0",
    13: "psec0_vcdl_31_16",
    14: "psec0_dllvdd",
    15: "psec0_ch0_self_trigger_rate",
    16: "psec0_ch1_self_trigger_rate",
    17: "psec0_ch2_self_trigger_rate",
    18: "psec0_ch3_self_trigger_rate",
    19: "psec0_ch4_self_trigger_rate",
    20: "psec0_ch5_self_trigger_rate",

    # PSEC chip 1
    21: "psec1_id",
    22: "psec1_wilkinson_current",
    23: "psec1_wilkinson_target",
    24: "psec1_vbias_pedestal",
    25: "psec1_self_trigger_threshold_setting",
    26: "psec1_provdd",
    27: "beamgate_timestamp_47_32",
    28: "psec1_selftrigger_mask",
    29: "psec1_selftrigger_threshold",
    30: "psec1_timestamp_31_16",
    31: "psec_event_count_31_16",
    32: "psec1_vcdl_15_0",
    33: "psec1_vcdl_31_16",
    34: "psec1_dllvdd",
    35: "psec1_ch0_self_trigger_rate",
    36: "psec1_ch1_self_trigger_rate",
    37: "psec1_ch2_self_trigger_rate",
    38: "psec1_ch3_self_trigger_rate",
    39: "psec1_ch4_self_trigger_rate",
    40: "psec1_ch5_self_trigger_rate",

    # PSEC chip 2
    41: "psec2_id",
    42: "psec2_wilkinson_current",
    43: "psec2_wilkinson_target",
    44: "psec2_vbias_pedestal",
    45: "psec2_self_trigger_threshold_setting",
    46: "psec2_provdd",
    47: "beamgate_timestamp_31_16",
    48: "psec2_selftrigger_mask",
    49: "psec2_selftrigger_threshold",
    50: "psec2_timestamp_47_32",
    51: "unused_51",
    52: "psec2_vcdl_15_0",
    53: "psec2_vcdl_31_16",
    54: "psec2_dllvdd",
    55: "psec2_ch0_self_trigger_rate",
    56: "psec2_ch1_self_trigger_rate",
    57: "psec2_ch2_self_trigger_rate",
    58: "psec2_ch3_self_trigger_rate",
    59: "psec2_ch4_self_trigger_rate",
    60: "psec2_ch5_self_trigger_rate",

    # PSEC chip 3
    61: "psec3_id",
    62: "psec3_wilkinson_current",
    63: "psec3_wilkinson_target",
    64: "psec3_vbias_pedestal",
    65: "psec3_self_trigger_threshold_setting",
    66: "psec3_provdd",
    67: "beamgate_timestamp_15_0",
    68: "psec3_selftrigger_mask",
    69: "psec3_selftrigger_threshold",
    70: "psec3_timestamp_63_48",
    71: "unused_71",
    72: "psec3_vcdl_15_0",
    73: "psec3_vcdl_31_16",
    74: "psec3_dllvdd",
    75: "psec3_ch0_self_trigger_rate",
    76: "psec3_ch1_self_trigger_rate",
    77: "psec3_ch2_self_trigger_rate",
    78: "psec3_ch3_self_trigger_rate",
    79: "psec3_ch4_self_trigger_rate",
    80: "psec3_ch5_self_trigger_rate",

    # PSEC chip 4
    81: "psec4_id",
    82: "psec4_wilkinson_current",
    83: "psec4_wilkinson_target",
    84: "psec4_vbias_pedestal",
    85: "psec4_self_trigger_threshold_setting",
    86: "psec4_provdd",
    87: "trigger_setup_info",
    88: "psec4_selftrigger_mask",
    89: "psec4_selftrigger_threshold",
}


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def hex_to_int(x):
    return int(str(x).strip(), 16)


def combine_u16(high, low):
    return ((high & 0xFFFF) << 16) | (low & 0xFFFF)


def combine_u64(w63_48, w47_32, w31_16, w15_0):
    return (
        ((w63_48 & 0xFFFF) << 48)
        | ((w47_32 & 0xFFFF) << 32)
        | ((w31_16 & 0xFFFF) << 16)
        | (w15_0 & 0xFFFF)
    )


def decode_trigger_setup(value):
    return {
        "trigger_setup_mode": (value >> 12) & 0xF,
        "sma_invert": (value >> 11) & 0x1,
        "selftrigger_sign": (value >> 10) & 0x1,
        "selftrigger_coincidence_min": value & 0x3FF,
    }


# ------------------------------------------------------------
# Read raw metadata words
# ------------------------------------------------------------

def read_metadata_words(filename):
    rows = []
    valid_line = 0

    with open(filename, "r") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()

            if not line:
                continue

            parts = line.split()

            if len(parts) != N_COLUMNS:
                raise ValueError(
                    f"Line {line_number}: expected {N_COLUMNS} columns, "
                    f"got {len(parts)}"
                )

            event = valid_line // EVENT_SAMPLES
            word = int(parts[COL_COUNTER])

            for side, meta_col in [("A", COL_META_A), ("B", COL_META_B)]:
                raw_hex = parts[meta_col]
                value = hex_to_int(raw_hex)

                rows.append({
                    "event": event,
                    "side": side,
                    "word": word,
                    "parameter": META_WORDS.get(word, f"metadata_word_{word}"),
                    "raw_hex": raw_hex,
                    "value": value,
                })

            valid_line += 1

    if valid_line % EVENT_SAMPLES != 0:
        print(
            f"Warning: {valid_line} valid rows is not divisible by "
            f"{EVENT_SAMPLES}. Last event may be incomplete."
        )

    return pd.DataFrame(rows)


def get_value(event_df, word):
    match = event_df[event_df["word"] == word]
    if match.empty:
        return None
    return int(match.iloc[0]["value"])


def get_raw(event_df, word):
    match = event_df[event_df["word"] == word]
    if match.empty:
        return None
    return str(match.iloc[0]["raw_hex"])


# ------------------------------------------------------------
# Build one-row-per-event/side summary
# ------------------------------------------------------------

def build_metadata_summary(df_words):
    rows = []

    for event in sorted(df_words["event"].unique()):
        for side in sorted(df_words["side"].unique()):
            event_df = df_words[
                (df_words["event"] == event)
                & (df_words["side"] == side)
            ]

            row = {
                "event": event,
                "side": side,
            }

            # Store all documented single-word metadata parameters
            for word, name in META_WORDS.items():
                value = get_value(event_df, word)
                raw = get_raw(event_df, word)

                row[name] = value
                row[name + "_hex"] = raw

            # Reconstruct PSEC IDs as hex strings
            for chip in range(5):
                id_word = 1 + 20 * chip
                row[f"psec{chip}_id_readable"] = get_raw(event_df, id_word)

            # Reconstruct VCDL 32-bit values
            # Only chips 0-3 are documented with VCDL low/high pairs.
            vcdl_words = {
                0: (12, 13),
                1: (32, 33),
                2: (52, 53),
                3: (72, 73),
            }

            for chip, (low_word, high_word) in vcdl_words.items():
                low = get_value(event_df, low_word)
                high = get_value(event_df, high_word)

                if low is not None and high is not None:
                    row[f"psec{chip}_vcdl"] = combine_u16(high, low)
                else:
                    row[f"psec{chip}_vcdl"] = None

            # Reconstruct beamgate timestamp
            w7 = get_value(event_df, 7)
            w27 = get_value(event_df, 27)
            w47 = get_value(event_df, 47)
            w67 = get_value(event_df, 67)

            if None not in [w7, w27, w47, w67]:
                row["beamgate_timestamp"] = combine_u64(w7, w27, w47, w67)
            else:
                row["beamgate_timestamp"] = None

            # Reconstruct PSEC timestamp
            w10 = get_value(event_df, 10)
            w30 = get_value(event_df, 30)
            w50 = get_value(event_df, 50)
            w70 = get_value(event_df, 70)

            if None not in [w10, w30, w50, w70]:
                row["psec_timestamp"] = combine_u64(w70, w50, w30, w10)
                row["clock_cycle"] = w10 & 0b111
            else:
                row["psec_timestamp"] = None
                row["clock_cycle"] = None

            # Reconstruct event count
            w11 = get_value(event_df, 11)
            w31 = get_value(event_df, 31)

            if None not in [w11, w31]:
                row["psec_event_count"] = combine_u16(w31, w11)
            else:
                row["psec_event_count"] = None

            # Decode trigger setup info, word 87
            w87 = get_value(event_df, 87)
            if w87 is not None:
                row.update(decode_trigger_setup(w87))

            rows.append(row)

    return pd.DataFrame(rows)


# ------------------------------------------------------------
# Human-readable printout
# ------------------------------------------------------------

def print_event_summary(df_summary, event=0):
    event_df = df_summary[df_summary["event"] == event]

    print()
    print("=" * 100)
    print(f"EVENT {event}")
    print("=" * 100)

    for _, row in event_df.iterrows():
        side = row["side"]

        print()
        print(f"SIDE {side}")
        print("-" * 100)

        print(f"Board ID: {row['board_id']}")

        print()
        print("PSEC IDs:")
        for chip in range(5):
            print(f"  chip {chip}: {row[f'psec{chip}_id_readable']}")

        print()
        print("VCDL:")
        for chip in range(4):
            print(f"  chip {chip}: {row[f'psec{chip}_vcdl']}")

        print()
        print("Wilkinson:")
        for chip in range(5):
            cur = row[f"psec{chip}_wilkinson_current"]
            tar = row[f"psec{chip}_wilkinson_target"]
            print(f"  chip {chip}: current={cur}, target={tar}, current-target={cur - tar}")

        print()
        print("Pedestal / thresholds / voltages:")
        for chip in range(5):
            print(
                f"  chip {chip}: "
                f"Vbias={row[f'psec{chip}_vbias_pedestal']}, "
                f"self-trigger threshold setting={row[f'psec{chip}_self_trigger_threshold_setting']}, "
                f"PROVDD={row[f'psec{chip}_provdd']}"
            )

        print()
        print("Timing:")
        print(f"  beamgate timestamp: {row['beamgate_timestamp']}")
        print(f"  PSEC timestamp:     {row['psec_timestamp']}")
        print(f"  PSEC event count:   {row['psec_event_count']}")
        print(f"  clock cycle:        {row['clock_cycle']}")

        print()
        print("Trigger setup:")
        print(f"  trigger setup mode:          {row.get('trigger_setup_mode')}")
        print(f"  SMA invert:                  {row.get('sma_invert')}")
        print(f"  selftrigger sign:            {row.get('selftrigger_sign')}")
        print(f"  selftrigger coincidence min: {row.get('selftrigger_coincidence_min')}")


# ------------------------------------------------------------
# Plotting
# ------------------------------------------------------------

def plot_group(df, columns, title, ylabel, output_file):
    plt.figure(figsize=(12, 7))

    for col in columns:
        if col not in df.columns:
            continue

        plt.plot(
            df["event"],
            df[col],
            marker="o",
            markersize=3,
            linewidth=1,
            label=col
        )

    plt.xlabel("Event")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True)
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(output_file, dpi=150)
    plt.close()

    print(f"Saved {output_file}")


def make_all_plots(df_summary, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    for side in sorted(df_summary["side"].unique()):
        side_df = df_summary[df_summary["side"] == side].sort_values("event")

        # VCDL plots
        plot_group(
            side_df,
            [f"psec{i}_vcdl" for i in range(4)],
            f"VCDL over events, side {side}",
            "VCDL count",
            output_dir / f"vcdl_side_{side}.png"
        )

        # Wilkinson current
        plot_group(
            side_df,
            [f"psec{i}_wilkinson_current" for i in range(5)],
            f"Wilkinson current over events, side {side}",
            "Wilkinson current",
            output_dir / f"wilkinson_current_side_{side}.png"
        )

        # Wilkinson target
        plot_group(
            side_df,
            [f"psec{i}_wilkinson_target" for i in range(5)],
            f"Wilkinson target over events, side {side}",
            "Wilkinson target",
            output_dir / f"wilkinson_target_side_{side}.png"
        )

        # Vbias pedestal
        plot_group(
            side_df,
            [f"psec{i}_vbias_pedestal" for i in range(5)],
            f"Vbias pedestal over events, side {side}",
            "Vbias pedestal",
            output_dir / f"vbias_pedestal_side_{side}.png"
        )

        # PROVDD
        plot_group(
            side_df,
            [f"psec{i}_provdd" for i in range(5)],
            f"PROVDD over events, side {side}",
            "PROVDD",
            output_dir / f"provdd_side_{side}.png"
        )

        # DLLVDD, only chips 0-3 documented
        plot_group(
            side_df,
            [f"psec{i}_dllvdd" for i in range(4)],
            f"DLLVDD over events, side {side}",
            "DLLVDD",
            output_dir / f"dllvdd_side_{side}.png"
        )

        # Self-trigger threshold setting
        plot_group(
            side_df,
            [f"psec{i}_self_trigger_threshold_setting" for i in range(5)],
            f"Self-trigger threshold setting over events, side {side}",
            "Threshold setting",
            output_dir / f"self_trigger_threshold_setting_side_{side}.png"
        )

        # Self-trigger threshold
        plot_group(
            side_df,
            [f"psec{i}_selftrigger_threshold" for i in range(5)],
            f"Self-trigger threshold over events, side {side}",
            "Self-trigger threshold",
            output_dir / f"selftrigger_threshold_side_{side}.png"
        )

        # Self-trigger masks
        plot_group(
            side_df,
            [f"psec{i}_selftrigger_mask" for i in range(5)],
            f"Self-trigger mask over events, side {side}",
            "Self-trigger mask",
            output_dir / f"selftrigger_mask_side_{side}.png"
        )

        # Timing quantities
        plot_group(
            side_df,
            ["beamgate_timestamp"],
            f"Beamgate timestamp over events, side {side}",
            "Beamgate timestamp",
            output_dir / f"beamgate_timestamp_side_{side}.png"
        )

        plot_group(
            side_df,
            ["psec_timestamp"],
            f"PSEC timestamp over events, side {side}",
            "PSEC timestamp",
            output_dir / f"psec_timestamp_side_{side}.png"
        )

        plot_group(
            side_df,
            ["psec_event_count"],
            f"PSEC event count over events, side {side}",
            "PSEC event count",
            output_dir / f"psec_event_count_side_{side}.png"
        )

        plot_group(
            side_df,
            ["clock_cycle"],
            f"Clock cycle over events, side {side}",
            "Clock cycle",
            output_dir / f"clock_cycle_side_{side}.png"
        )

        # Trigger setup decoded fields
        plot_group(
            side_df,
            [
                "trigger_setup_mode",
                "sma_invert",
                "selftrigger_sign",
                "selftrigger_coincidence_min",
            ],
            f"Trigger setup decoded fields over events, side {side}",
            "Decoded trigger value",
            output_dir / f"trigger_setup_decoded_side_{side}.png"
        )

        # Self-trigger rates: one plot per PSEC chip
        for chip in range(4):
            plot_group(
                side_df,
                [f"psec{chip}_ch{ch}_self_trigger_rate" for ch in range(6)],
                f"PSEC {chip} channel self-trigger rates over events, side {side}",
                "Self-trigger rate counts",
                output_dir / f"psec{chip}_self_trigger_rates_side_{side}.png"
            )


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

if __name__ == "__main__":
    output_dir = Path("metadata_plots")
    output_dir.mkdir(exist_ok=True)

    df_words = read_metadata_words(INPUT_FILE)
    df_summary = build_metadata_summary(df_words)

    print(f"Input file: {INPUT_FILE}")
    print(f"Number of events: {df_summary['event'].nunique()}")
    print(f"Number of sides: {df_summary['side'].nunique()}")

    # Human readable example for first event
    print_event_summary(df_summary, event=0)

    # Save full metadata tables
    df_words.to_csv(output_dir / "metadata_words_all_events.csv", index=False)
    df_summary.to_csv(output_dir / "metadata_summary_all_events.csv", index=False)

    print()
    print(f"Saved raw metadata words: {output_dir / 'metadata_words_all_events.csv'}")
    print(f"Saved event summary:      {output_dir / 'metadata_summary_all_events.csv'}")

    # Make plots
    make_all_plots(df_summary, output_dir)

    print()
    print("Done.")
