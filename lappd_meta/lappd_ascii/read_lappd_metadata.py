#!/usr/bin/env python3

from pathlib import Path
import pandas as pd


# -----------------------------
# Configuration
# -----------------------------

INPUT_FILE = Path("data/Ascii20242904_084248.txt")

EVENT_SAMPLES = 256
N_COLUMNS = 63

# 0-based Python indices
COL_COUNTER = 0
COL_META_A = 31   # column 32
COL_META_B = 62   # column 63


# -----------------------------
# Metadata word descriptions
# -----------------------------

META_NAMES = {
    0:  "Board ID",

    1:  "PSEC ID chip 0",
    2:  "Wilkinson feedback count, chip 0",
    3:  "Wilkinson feedback target, chip 0",
    4:  "Vbias pedestal setting, chip 0",
    5:  "Self trigger threshold, chip 0",
    6:  "PROVDD setting, chip 0",
    7:  "Beamgate timestamp [63:48]",
    8:  "Selftrigger mask PSEC 0",
    9:  "Selftrigger threshold PSEC 0",
    10: "PSEC0 timestamp [15:0]",
    11: "PSEC event count [15:0]",
    12: "VCDL count [15:0], chip 0",
    13: "VCDL count [31:16], chip 0",
    14: "DLLVDD setting, chip 0",
    15: "PSEC0 ch0 self trigger rate",
    16: "PSEC0 ch1 self trigger rate",
    17: "PSEC0 ch2 self trigger rate",
    18: "PSEC0 ch3 self trigger rate",
    19: "PSEC0 ch4 self trigger rate",
    20: "PSEC0 ch5 self trigger rate",

    21: "PSEC ID chip 1",
    22: "Wilkinson feedback count, chip 1",
    23: "Wilkinson feedback target, chip 1",
    24: "Vbias pedestal setting, chip 1",
    25: "Self trigger threshold, chip 1",
    26: "PROVDD setting, chip 1",
    27: "Beamgate timestamp [47:32]",
    28: "Selftrigger mask PSEC 1",
    29: "Selftrigger threshold PSEC 1",
    30: "PSEC1 timestamp [31:16]",
    31: "PSEC event count [31:16]",
    32: "VCDL count [15:0], chip 1",
    33: "VCDL count [31:16], chip 1",
    34: "DLLVDD setting, chip 1",
    35: "PSEC1 ch0 self trigger rate",
    36: "PSEC1 ch1 self trigger rate",
    37: "PSEC1 ch2 self trigger rate",
    38: "PSEC1 ch3 self trigger rate",
    39: "PSEC1 ch4 self trigger rate",
    40: "PSEC1 ch5 self trigger rate",

    41: "PSEC ID chip 2",
    42: "Wilkinson feedback count, chip 2",
    43: "Wilkinson feedback target, chip 2",
    44: "Vbias pedestal setting, chip 2",
    45: "Self trigger threshold, chip 2",
    46: "PROVDD setting, chip 2",
    47: "Beamgate timestamp [31:16]",
    48: "Selftrigger mask PSEC 2",
    49: "Selftrigger threshold PSEC 2",
    50: "PSEC2 timestamp [47:32]",
    51: "Unused / zero",
    52: "VCDL count [15:0], chip 2",
    53: "VCDL count [31:16], chip 2",
    54: "DLLVDD setting, chip 2",
    55: "PSEC2 ch0 self trigger rate",
    56: "PSEC2 ch1 self trigger rate",
    57: "PSEC2 ch2 self trigger rate",
    58: "PSEC2 ch3 self trigger rate",
    59: "PSEC2 ch4 self trigger rate",
    60: "PSEC2 ch5 self trigger rate",

    61: "PSEC ID chip 3",
    62: "Wilkinson feedback count, chip 3",
    63: "Wilkinson feedback target, chip 3",
    64: "Vbias pedestal setting, chip 3",
    65: "Self trigger threshold, chip 3",
    66: "PROVDD setting, chip 3",
    67: "Beamgate timestamp [15:0]",
    68: "Selftrigger mask PSEC 3",
    69: "Selftrigger threshold PSEC 3",
    70: "PSEC3 timestamp [63:48]",
    71: "Unused / zero",
    72: "VCDL count [15:0], chip 3",
    73: "VCDL count [31:16], chip 3",
    74: "DLLVDD setting, chip 3",
    75: "PSEC3 ch0 self trigger rate",
    76: "PSEC3 ch1 self trigger rate",
    77: "PSEC3 ch2 self trigger rate",
    78: "PSEC3 ch3 self trigger rate",
    79: "PSEC3 ch4 self trigger rate",
    80: "PSEC3 ch5 self trigger rate",

    81: "PSEC ID chip 4",
    82: "Wilkinson feedback count, chip 4",
    83: "Wilkinson feedback target, chip 4",
    84: "Vbias pedestal setting, chip 4",
    85: "Self trigger threshold, chip 4",
    86: "PROVDD setting, chip 4",
    87: "Trigger setup info",
    88: "Selftrigger mask PSEC 4",
    89: "Selftrigger threshold PSEC 4",
}


# -----------------------------
# Helper functions
# -----------------------------

def parse_hex_word(raw):
    """
    Convert metadata text into integer.

    Examples:
        dcb0 -> 56496
        ca08 -> 51720
        800  -> 2048
        0    -> 0
    """
    raw = str(raw).strip()
    return int(raw, 16)


def decode_trigger_setup(value):
    """
    Decode metadata word 87.

    Bits:
        [15:12] trigger setup mode
        [11]    SMA invert setting
        [10]    selftrigger sign
        [9:0]   selftrigger coincidence minimum
    """
    return {
        "trigger_setup_mode": (value >> 12) & 0xF,
        "sma_invert": (value >> 11) & 0x1,
        "selftrigger_sign": (value >> 10) & 0x1,
        "selftrigger_coincidence_min": value & 0x3FF,
    }


def decode_single_metadata_word(word_index, raw_hex):
    """
    Decode one metadata word.
    """
    value = parse_hex_word(raw_hex)

    decoded = {
        "word": word_index,
        "name": META_NAMES.get(word_index, f"Metadata word {word_index}"),
        "raw_hex": str(raw_hex),
        "decimal": value,
    }

    # PSEC IDs are usually dcb0, dcb1, dcb2, ...
    raw_lower = str(raw_hex).lower()
    if raw_lower.startswith("dcb"):
        decoded["decoded"] = f"PSEC ID = {raw_lower[-1]}"

    # Word 10 includes the clock cycle in the last 3 bits.
    if word_index == 10:
        decoded["clock_cycle"] = value & 0b111

    # Word 87 contains packed trigger information.
    if word_index == 87:
        decoded.update(decode_trigger_setup(value))

    return decoded


def combine_u16(high, low):
    """
    Combine two 16-bit words into one 32-bit value.
    """
    return ((high & 0xFFFF) << 16) | (low & 0xFFFF)


def combine_u64(w63_48, w47_32, w31_16, w15_0):
    """
    Combine four 16-bit words into one 64-bit value.
    """
    return (
        ((w63_48 & 0xFFFF) << 48)
        | ((w47_32 & 0xFFFF) << 32)
        | ((w31_16 & 0xFFFF) << 16)
        | (w15_0 & 0xFFFF)
    )


# -----------------------------
# Main reader
# -----------------------------

def read_metadata_only(filename):
    """
    Read all events from an ASCII data file.

    Expected line format:
        counter | 30 data A | meta A | 30 data B | meta B

    Returns
    -------
    df : pandas.DataFrame
        One row per metadata word per side per event.
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
                    f"but got {len(parts)}"
                )

            counter = int(parts[COL_COUNTER])

            # Event number is based on blocks of 256 valid rows
            event_id = valid_line_index // EVENT_SAMPLES

            # Word index should usually be the same as counter: 0..255
            word_index = counter

            raw_meta_a = parts[COL_META_A]
            raw_meta_b = parts[COL_META_B]

            decoded_a = decode_single_metadata_word(word_index, raw_meta_a)
            decoded_a.update({
                "event": event_id,
                "line_number": line_number,
                "side": "A",
                "sample": counter,
            })
            rows.append(decoded_a)

            decoded_b = decode_single_metadata_word(word_index, raw_meta_b)
            decoded_b.update({
                "event": event_id,
                "line_number": line_number,
                "side": "B",
                "sample": counter,
            })
            rows.append(decoded_b)

            valid_line_index += 1

    df = pd.DataFrame(rows)

    if valid_line_index % EVENT_SAMPLES != 0:
        print(
            f"Warning: file has {valid_line_index} valid rows, "
            f"which is not divisible by {EVENT_SAMPLES}."
        )

    return df


# -----------------------------
# Event-level summaries
# -----------------------------

def get_word_value(event_df, side, word):
    """
    Get decimal value for one side and metadata word.
    """
    match = event_df[(event_df["side"] == side) & (event_df["word"] == word)]

    if match.empty:
        return None

    return int(match.iloc[0]["decimal"])


def build_event_summary(df):
    """
    Build compact summary with reconstructed timestamps and event counts.
    """
    summaries = []

    for event_id in sorted(df["event"].unique()):
        event_df = df[df["event"] == event_id]

        for side in ["A", "B"]:
            w7 = get_word_value(event_df, side, 7)
            w27 = get_word_value(event_df, side, 27)
            w47 = get_word_value(event_df, side, 47)
            w67 = get_word_value(event_df, side, 67)

            w10 = get_word_value(event_df, side, 10)
            w30 = get_word_value(event_df, side, 30)
            w50 = get_word_value(event_df, side, 50)
            w70 = get_word_value(event_df, side, 70)

            w11 = get_word_value(event_df, side, 11)
            w31 = get_word_value(event_df, side, 31)

            w87 = get_word_value(event_df, side, 87)

            beamgate_timestamp = None
            if None not in [w7, w27, w47, w67]:
                beamgate_timestamp = combine_u64(w7, w27, w47, w67)

            psec_timestamp = None
            if None not in [w10, w30, w50, w70]:
                psec_timestamp = combine_u64(w70, w50, w30, w10)

            event_count = None
            if None not in [w31, w11]:
                event_count = combine_u16(w31, w11)

            clock_cycle = None
            if w10 is not None:
                clock_cycle = w10 & 0b111

            summary = {
                "event": event_id,
                "side": side,
                "board_id": get_word_value(event_df, side, 0),

                "psec0_id_hex": get_raw_hex(event_df, side, 1),
                "psec1_id_hex": get_raw_hex(event_df, side, 21),
                "psec2_id_hex": get_raw_hex(event_df, side, 41),
                "psec3_id_hex": get_raw_hex(event_df, side, 61),
                "psec4_id_hex": get_raw_hex(event_df, side, 81),

                "beamgate_timestamp": beamgate_timestamp,
                "psec_timestamp": psec_timestamp,
                "event_count": event_count,
                "clock_cycle": clock_cycle,
            }

            if w87 is not None:
                summary.update(decode_trigger_setup(w87))

            summaries.append(summary)

    return pd.DataFrame(summaries)


def get_raw_hex(event_df, side, word):
    """
    Get raw hex string for one side and metadata word.
    """
    match = event_df[(event_df["side"] == side) & (event_df["word"] == word)]

    if match.empty:
        return None

    return str(match.iloc[0]["raw_hex"])


def print_event_human_readable(df, event_id=0, max_word=89):
    """
    Print metadata words for one event in readable form.

    max_word=89 prints the main documented metadata area.
    Use max_word=255 if you want every metadata row.
    """
    event_df = df[df["event"] == event_id]

    if event_df.empty:
        print(f"No event {event_id} found.")
        return

    print()
    print("=" * 80)
    print(f"EVENT {event_id}")
    print("=" * 80)

    for side in ["A", "B"]:
        side_df = event_df[event_df["side"] == side]
        side_df = side_df[side_df["word"] <= max_word]
        side_df = side_df.sort_values("word")

        print()
        print(f"SIDE {side}")
        print("-" * 80)

        for _, row in side_df.iterrows():
            word = int(row["word"])
            name = row["name"]
            raw_hex = row["raw_hex"]
            decimal = int(row["decimal"])

            text = f"word {word:3d} | {name:40s} | hex {raw_hex:>6s} | dec {decimal}"

            if "decoded" in row and pd.notna(row["decoded"]):
                text += f" | {row['decoded']}"

            if "clock_cycle" in row and pd.notna(row["clock_cycle"]):
                text += f" | clock_cycle={int(row['clock_cycle'])}"

            if "trigger_setup_mode" in row and pd.notna(row["trigger_setup_mode"]):
                text += (
                    f" | trigger_mode={int(row['trigger_setup_mode'])}"
                    f", sma_invert={int(row['sma_invert'])}"
                    f", selftrigger_sign={int(row['selftrigger_sign'])}"
                    f", coincidence_min={int(row['selftrigger_coincidence_min'])}"
                )

            print(text)


# -----------------------------
# Run example
# -----------------------------

if __name__ == "__main__":
    df_meta = read_metadata_only(INPUT_FILE)

    n_events = df_meta["event"].nunique()

    print(f"Input file: {INPUT_FILE}")
    print(f"Number of events: {n_events}")
    print(f"Metadata rows: {len(df_meta)}")
    print()

    # Print full readable metadata for the first event.
    print_event_human_readable(df_meta, event_id=0, max_word=89)

    # Build compact event-level summary.
    df_summary = build_event_summary(df_meta)

    print()
    print("=" * 80)
    print("COMPACT EVENT SUMMARY")
    print("=" * 80)
    print(df_summary.head(20).to_string(index=False))

    # Save outputs.
    output_dir = Path("metadata_output")
    output_dir.mkdir(exist_ok=True)

    df_meta.to_csv(output_dir / "metadata_words.csv", index=False)
    df_summary.to_csv(output_dir / "metadata_event_summary.csv", index=False)

    print()
    print(f"Saved full metadata words to: {output_dir / 'metadata_words.csv'}")
    print(f"Saved event summary to:      {output_dir / 'metadata_event_summary.csv'}")
