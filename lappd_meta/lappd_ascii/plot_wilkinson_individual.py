#!/usr/bin/env python3

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


INPUT_FILE = Path("data/Ascii20242904_084248.txt")

EVENT_SAMPLES = 256
N_COLUMNS = 63

# Python 0-based columns
COL_COUNTER = 0
COL_META_A = 31   # column 32
COL_META_B = 62   # column 63


# Metadata word map for Wilkinson information
WILKINSON_WORDS = {
    2:  {"chip": 0, "quantity": "current"},
    3:  {"chip": 0, "quantity": "target"},

    22: {"chip": 1, "quantity": "current"},
    23: {"chip": 1, "quantity": "target"},

    42: {"chip": 2, "quantity": "current"},
    43: {"chip": 2, "quantity": "target"},

    62: {"chip": 3, "quantity": "current"},
    63: {"chip": 3, "quantity": "target"},

    82: {"chip": 4, "quantity": "current"},
    83: {"chip": 4, "quantity": "target"},
}


def hex_to_int(raw):
    """
    Convert metadata hex word to integer.

    Examples
    --------
    ca08 -> 51720
    800  -> 2048
    0    -> 0
    """
    return int(str(raw).strip(), 16)


def read_wilkinson_metadata(filename):
    """
    Read only Wilkinson metadata from a multi-event ASCII file.

    Expected format per row:
        counter | 30 data A | metadata A | 30 data B | metadata B

    Metadata word index = counter column.
    One event = 256 rows.
    """
    filename = Path(filename)

    if not filename.exists():
        raise FileNotFoundError(f"File not found: {filename}")

    rows = []
    valid_line_index = 0

    with filename.open("r") as f:
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

            counter = int(parts[COL_COUNTER])
            event_id = valid_line_index // EVENT_SAMPLES

            # The metadata word is selected by the counter/sample number.
            word = counter

            if word in WILKINSON_WORDS:
                info = WILKINSON_WORDS[word]

                raw_a = parts[COL_META_A]
                raw_b = parts[COL_META_B]

                rows.append({
                    "event": event_id,
                    "side": "A",
                    "chip": info["chip"],
                    "quantity": info["quantity"],
                    "word": word,
                    "raw_hex": raw_a,
                    "value": hex_to_int(raw_a),
                })

                rows.append({
                    "event": event_id,
                    "side": "B",
                    "chip": info["chip"],
                    "quantity": info["quantity"],
                    "word": word,
                    "raw_hex": raw_b,
                    "value": hex_to_int(raw_b),
                })

            valid_line_index += 1

    if valid_line_index % EVENT_SAMPLES != 0:
        print(
            f"Warning: {valid_line_index} valid rows is not divisible by "
            f"{EVENT_SAMPLES}. Last event may be incomplete."
        )

    return pd.DataFrame(rows)


def make_wide_table(df):
    """
    Convert long Wilkinson table into one row per event/side/chip.

    Output columns:
        event, side, chip, current, target, current_hex, target_hex, difference
    """
    value_wide = df.pivot_table(
        index=["event", "side", "chip"],
        columns="quantity",
        values="value",
        aggfunc="first"
    ).reset_index()

    hex_wide = df.pivot_table(
        index=["event", "side", "chip"],
        columns="quantity",
        values="raw_hex",
        aggfunc="first"
    ).reset_index()

    value_wide.columns.name = None
    hex_wide.columns.name = None

    hex_wide = hex_wide.rename(
        columns={
            "current": "current_hex",
            "target": "target_hex",
        }
    )

    out = pd.merge(
        value_wide,
        hex_wide,
        on=["event", "side", "chip"],
        how="left"
    )

    out["difference"] = out["current"] - out["target"]

    return out.sort_values(["side", "chip", "event"])


def print_human_readable(df_wide, n_events=5):
    """
    Print Wilkinson information in human-readable form.
    """
    events = sorted(df_wide["event"].unique())[:n_events]

    for event in events:
        print()
        print("=" * 80)
        print(f"EVENT {event}")
        print("=" * 80)

        event_df = df_wide[df_wide["event"] == event]

        for side in ["A", "B"]:
            print(f"\nSide {side}")
            print("-" * 80)

            side_df = event_df[event_df["side"] == side]

            for _, row in side_df.iterrows():
                chip = int(row["chip"])

                print(
                    f"Chip {chip}: "
                    f"current = {int(row['current'])} "
                    f"(hex {row['current_hex']}), "
                    f"target = {int(row['target'])} "
                    f"(hex {row['target_hex']}), "
                    f"current - target = {int(row['difference'])}"
                )


def plot_wilkinson_current(df_wide, output_dir):
    """
    Plot Wilkinson current value versus event.
    One figure per side.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    for side in sorted(df_wide["side"].unique()):
        side_df = df_wide[df_wide["side"] == side]

        plt.figure(figsize=(10, 6))

        for chip in sorted(side_df["chip"].unique()):
            chip_df = side_df[side_df["chip"] == chip]

            plt.plot(
                chip_df["event"],
                chip_df["current"],
                marker="o",
                linestyle="-",
                label=f"chip {chip}"
            )

        plt.xlabel("Event")
        plt.ylabel("Wilkinson feedback count current")
        plt.title(f"Wilkinson current vs event, side {side}")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()

        out = output_dir / f"wilkinson_current_side_{side}.png"
        plt.savefig(out, dpi=150)
        plt.close()

        print(f"Saved: {out}")


def plot_wilkinson_difference(df_wide, output_dir):
    """
    Plot current - target versus event.
    This is useful to see whether the feedback count is stable around target.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    for side in sorted(df_wide["side"].unique()):
        side_df = df_wide[df_wide["side"] == side]

        plt.figure(figsize=(10, 6))

        for chip in sorted(side_df["chip"].unique()):
            chip_df = side_df[side_df["chip"] == chip]

            plt.plot(
                chip_df["event"],
                chip_df["difference"],
                marker="o",
                linestyle="-",
                label=f"chip {chip}"
            )

        plt.axhline(0, linestyle="--")
        plt.xlabel("Event")
        plt.ylabel("Wilkinson current - target")
        plt.title(f"Wilkinson current minus target vs event, side {side}")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()

        out = output_dir / f"wilkinson_difference_side_{side}.png"
        plt.savefig(out, dpi=150)
        plt.close()

        print(f"Saved: {out}")


def plot_current_and_target_per_chip(df_wide, output_dir):
    """
    Plot current and target together for each side/chip.
    This gives one image per side/chip.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    for side in sorted(df_wide["side"].unique()):
        for chip in sorted(df_wide["chip"].unique()):
            chip_df = df_wide[
                (df_wide["side"] == side)
                & (df_wide["chip"] == chip)
            ]

            if chip_df.empty:
                continue

            plt.figure(figsize=(10, 6))

            plt.plot(
                chip_df["event"],
                chip_df["current"],
                marker="o",
                linestyle="-",
                label="current"
            )

            plt.plot(
                chip_df["event"],
                chip_df["target"],
                marker="s",
                linestyle="--",
                label="target"
            )

            plt.xlabel("Event")
            plt.ylabel("Wilkinson count")
            plt.title(f"Wilkinson current and target, side {side}, chip {chip}")
            plt.grid(True)
            plt.legend()
            plt.tight_layout()

            out = output_dir / f"wilkinson_side_{side}_chip_{chip}.png"
            plt.savefig(out, dpi=150)
            plt.close()

            print(f"Saved: {out}")


if __name__ == "__main__":
    output_dir = Path("wilkinson_output")
    output_dir.mkdir(exist_ok=True)

    df_long = read_wilkinson_metadata(INPUT_FILE)
    df_wide = make_wide_table(df_long)

    n_events = df_wide["event"].nunique()

    print(f"Input file: {INPUT_FILE}")
    print(f"Number of events: {n_events}")
    print(f"Number of Wilkinson rows: {len(df_wide)}")

    print_human_readable(df_wide, n_events=5)

    # Save tables
    df_long.to_csv(output_dir / "wilkinson_long.csv", index=False)
    df_wide.to_csv(output_dir / "wilkinson_per_event.csv", index=False)

    print()
    print(f"Saved table: {output_dir / 'wilkinson_long.csv'}")
    print(f"Saved table: {output_dir / 'wilkinson_per_event.csv'}")

    # Make plots
    plot_wilkinson_current(df_wide, output_dir)
    plot_wilkinson_difference(df_wide, output_dir)
    plot_current_and_target_per_chip(df_wide, output_dir)
