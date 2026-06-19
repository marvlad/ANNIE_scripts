#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <map>
#include <bitset>
#include "PsecData.h"
#include "BoostStore.h"
#include "lappd_helper.h"

// ══════════════════════════════════════════════════════════════════════════════
// CSV HEADER
// ══════════════════════════════════════════════════════════════════════════════
void WriteCSVHeader(std::ofstream& csv) {
    csv << "global_entry,file_entry,filename,lappd_key,lappd_id,board_id,";

    // ── PSEC0–3: plain threshold word (not packed) ────────────────────────
    for (int chip = 0; chip < 4; chip++) {
        std::string c = "psec" + std::to_string(chip) + "_";
        csv << c << "wilkinson_current,"
            << c << "wilkinson_target,"
            << c << "vbias,"
            << c << "selftrig_threshold,"
            << c << "provdd,"
            << c << "selftrig_mask,"
            << c << "selftrig_thresh_raw,"   // plain ADC value, NOT packed
            << c << "vcdl_count,";
        for (int ch = 0; ch < 6; ch++)
            csv << c << "ch" << ch << "_trig_rate,";
    }

    // ── PSEC4: threshold word IS word 87 — packed trigger config ─────────
    // [15:12]=trig_mode  [11]=sma_invert  [10]=st_sign  [9:0]=coinc_min
    csv << "psec4_wilkinson_current,"
        << "psec4_wilkinson_target,"
        << "psec4_vbias,"
        << "psec4_selftrig_threshold,"
        << "psec4_provdd,"
        << "psec4_selftrig_mask,"
        << "psec4_trig_mode,"       // word87 [15:12]
        << "psec4_sma_invert,"      // word87 [11]
        << "psec4_st_sign,"         // word87 [10]
        << "psec4_coinc_min,"       // word87 [9:0]
        << "psec4_vcdl_count,";
    for (int ch = 0; ch < 6; ch++)
        csv << "psec4_ch" << ch << "_trig_rate,";

    csv << "beamgate_raw,beamgate_ns,"
        << "timestamp_raw,timestamp_ns,"
        << "clockcycle,"
        << "combined_trig_rate"
        << "\n";
}

// ══════════════════════════════════════════════════════════════════════════════
// CSV ROW
// ══════════════════════════════════════════════════════════════════════════════
void WriteCSVRow(std::ofstream& csv,
                 int entry, int globalEntry,
                 const std::string& filepath,
                 const std::string& lappdKey,
                 unsigned int lappdID,
                 const std::vector<unsigned short>& meta)
{
    if (meta.size() < 103) {
        std::cout << "  WARNING: meta too small (" << meta.size()
                  << "), skipping row." << std::endl;
        return;
    }

    // Extract filename from full path
    std::string fname = filepath.substr(filepath.find_last_of("/\\") + 1);

    // ── Identity ──────────────────────────────────────────────────────────
    csv << globalEntry << ","
        << entry       << ","
        << fname       << ","
        << lappdKey    << ","
        << lappdID     << ","
        << meta[0]     << ",";  // board ID

    // ── Per-chip fields ───────────────────────────────────────────────────
    // Layout in meta per chip (20 words each, starting at offset 1):
    //   o+0   chip header   (0xDCBN)
    //   o+1   wilkinson current
    //   o+2   wilkinson target
    //   o+3   vbias
    //   o+4   selftrig threshold setting
    //   o+5   provdd
    //   o+6   trigger info 0:
    //           PSEC0-3 → beamgate slice (decoded below, not written per-chip)
    //           PSEC4   → word 87, packed: [15:12] mode [11] inv [10] sign [9:0] coinc
    //   o+7   selftrig mask
    //   o+8   selftrig threshold word:
    //           PSEC0-3 → plain ADC threshold value
    //           PSEC4   → selftrig threshold for PSEC4 (separate from word87)
    //   o+9   timestamp slice (decoded below)
    //   o+10  event count slice
    //   o+11  vcdl [15:0]
    //   o+12  vcdl [31:16]
    //   o+13  dllvdd
    //   o+14..o+19  6 self-trig rate counts

    // ── PSEC0-3: write selftrig_thresh_raw (plain value, no decoding) ─────
    for (int chip = 0; chip < 4; chip++) {
        int o = 1 + chip * 20;

        unsigned int vcdl = ((unsigned int)meta[o + 12] << 16) | meta[o + 11];

        csv << meta[o + 1] << ","    // wilkinson current
            << meta[o + 2] << ","    // wilkinson target
            << meta[o + 3] << ","    // vbias
            << meta[o + 4] << ","    // selftrig threshold
            << meta[o + 5] << ","    // provdd
            << meta[o + 7] << ","    // selftrig mask
            << meta[o + 8] << ","    // selftrig_thresh_raw (plain ADC, NOT packed)
            << vcdl         << ",";  // vcdl combined 32-bit

        for (int ch = 0; ch < 6; ch++)
            csv << meta[o + 14 + ch] << ",";
    }

    // ── PSEC4: decode word 87 (o+6) into its 4 packed fields ─────────────
    {
        int o = 1 + 4 * 20;   // PSEC4 offset = 81

        unsigned int vcdl = ((unsigned int)meta[o + 12] << 16) | meta[o + 11];

        // word 87 = meta[o+6] for PSEC4
        unsigned short w87  = meta[o + 6];
        unsigned int trig_mode  = (w87 >> 12) & 0xF;   // [15:12]
        unsigned int sma_invert = (w87 >> 11) & 0x1;   // [11]
        unsigned int st_sign    = (w87 >> 10) & 0x1;   // [10]
        unsigned int coinc_min  = w87 & 0x3FF;          // [9:0]

        csv << meta[o + 1] << ","    // wilkinson current
            << meta[o + 2] << ","    // wilkinson target
            << meta[o + 3] << ","    // vbias
            << meta[o + 4] << ","    // selftrig threshold
            << meta[o + 5] << ","    // provdd
            << meta[o + 7] << ","    // selftrig mask
            << trig_mode   << ","    // word87 [15:12] trigger mode
            << sma_invert  << ","    // word87 [11]    SMA invert
            << st_sign     << ","    // word87 [10]    self-trig sign
            << coinc_min   << ","    // word87 [9:0]   coincidence minimum
            << vcdl        << ",";   // vcdl combined 32-bit

        for (int ch = 0; ch < 6; ch++)
            csv << meta[o + 14 + ch] << ",";
    }

    // ── Reconstruct 64-bit beamgate from 4 slices ────────────────────────
    // Slices at meta indices: 7, 27, 47, 67
    // (= o+6 for PSEC0,1,2,3 = 1+0*20+6, 1+1*20+6, 1+2*20+6, 1+3*20+6)
    unsigned long beamgate_raw =
        ((unsigned long)meta[7]  << 48) |
        ((unsigned long)meta[27] << 32) |
        ((unsigned long)meta[47] << 16) |
        ((unsigned long)meta[67]);

    // ── Reconstruct 64-bit timestamp from 4 slices ───────────────────────
    // Slices at meta indices: 70, 50, 30, 10 (note reversed bit order)
    unsigned long timestamp_raw =
        ((unsigned long)meta[70] << 48) |
        ((unsigned long)meta[50] << 32) |
        ((unsigned long)meta[30] << 16) |
        ((unsigned long)meta[10]);

    // ── Clock cycle: last 3 bits of timestamp[15:0] (meta[10]) ──────────
    int clockcycle = meta[10] & 0x7;

    // ── Convert to nanoseconds ────────────────────────────────────────────
    // Clock at 320 MHz → 1 tick = 25/8 ns
    // ns = (raw / 8) * 25 + (raw % 8) * 3
    unsigned long bg_trunc = beamgate_raw  % 8;
    unsigned long bg_ns    = (beamgate_raw  - bg_trunc) / 8 * 25 + bg_trunc * 3;

    unsigned long ts_trunc = timestamp_raw % 8;
    unsigned long ts_ns    = (timestamp_raw - ts_trunc) / 8 * 25 + ts_trunc * 3;

    // ── Combined trigger rate (meta[101]) ─────────────────────────────────
    unsigned short combined_trig = meta[101];

    csv << beamgate_raw  << ","
        << bg_ns         << ","
        << timestamp_raw << ","
        << ts_ns         << ","
        << clockcycle    << ","
        << combined_trig
        << "\n";
}

// ══════════════════════════════════════════════════════════════════════════════
// MAIN
// ══════════════════════════════════════════════════════════════════════════════
int main(int argc, char* argv[]) {

    // ── Read input.txt (or path passed as argument) ───────────────────────
    std::string inputFile = "input.txt";
    if (argc > 1) inputFile = argv[1];

    std::ifstream fin(inputFile);
    if (!fin.is_open()) {
        std::cerr << "ERROR: cannot open input file: " << inputFile << std::endl;
        return 1;
    }

    std::vector<std::string> filePaths;
    std::string line;
    while (std::getline(fin, line)) {
        // skip empty lines and comment lines starting with #
        if (!line.empty() && line[0] != '#')
            filePaths.push_back(line);
    }
    fin.close();

    if (filePaths.empty()) {
        std::cerr << "ERROR: no file paths found in " << inputFile << std::endl;
        return 1;
    }

    std::cout << "Found " << filePaths.size()
              << " file(s) to process." << std::endl;

    // ── LAPPD keys to try ─────────────────────────────────────────────────
    std::vector<std::string> lappdKeys = {
        "LAPPDData"
    };

    // ── Open CSV ──────────────────────────────────────────────────────────
    std::ofstream csv("lappd_metadata.csv");
    if (!csv.is_open()) {
        std::cerr << "ERROR: cannot open lappd_metadata.csv for writing" << std::endl;
        return 1;
    }
    WriteCSVHeader(csv);

    verbosity        = 0;
    int globalEntry  = 0;
    int totalSkipped = 0;
    int totalFailed  = 0;

    // Track which LAPPD keys were found
    std::map<std::string, int> lappdKeysFound;
    for (const std::string& key : lappdKeys)
        lappdKeysFound[key] = 0;

    // Track data frames per LAPPD_ID
    std::map<unsigned int, int> lappdIDDataFrames;
    std::map<unsigned int, int> lappdIDPPSFrames;

    // ── Loop over files ───────────────────────────────────────────────────
    for (const std::string& path : filePaths) {
        std::cout << "\n=== Processing: " << path << " ===" << std::endl;

        BoostStore* RawData = new BoostStore(false, 0);
        RawData->Initialise(path);

        BoostStore* LAPPDData = new BoostStore(false, 2);
        RawData->Get("LAPPDData", *LAPPDData);

        int lappdtotalentries = 0;
        LAPPDData->Header->Get("TotalEntries", lappdtotalentries);
        std::cout << "  Entries in file: " << lappdtotalentries << std::endl;

        int fileDataEvents = 0;
        int filePPSEvents  = 0;

        // ── Loop over entries ─────────────────────────────────────────────
        for (int entry = 0; entry < lappdtotalentries; entry++) {
            LAPPDData->GetEntry(entry);

            bool anyDataFound = false;

            // ── Try each LAPPD key ────────────────────────────────────────
            for (const std::string& key : lappdKeys) {

                PsecData* Ldata = new PsecData;
                bool success = LAPPDData->Get(key, *Ldata);

                if (!success) {
                    delete Ldata;
                    continue;
                }

                std::vector<unsigned short>& Raw_Buffer    = Ldata->RawWaveform;
                std::vector<int>&            BoardId_Buffer = Ldata->BoardIndex;
                unsigned int lappdID = Ldata->LAPPD_ID;

                if (Raw_Buffer.empty() || BoardId_Buffer.empty()) {
                    delete Ldata;
                    continue;
                }

                int frametype = (int)(Raw_Buffer.size() / BoardId_Buffer.size());

                // Skip PPS frames
                if (frametype != NUM_VECTOR_DATA) {
                    filePPSEvents++;
                    totalSkipped++;
                    lappdIDPPSFrames[lappdID]++;
                    delete Ldata;
                    continue;
                }

                // This key has real data
                lappdKeysFound[key]++;
                lappdIDDataFrames[lappdID]++;
                anyDataFound = true;

                // ── Loop over boards ──────────────────────────────────────
                int nbi = (int)BoardId_Buffer.size();
                for (int bi = 0; bi < nbi; bi++) {
                    meta.clear();
                    Parse_Buffer.clear();

                    for (int c = bi * frametype; c < (bi + 1) * frametype; c++)
                        Parse_Buffer.push_back(Raw_Buffer[c]);

                    int retval = getParsedMeta(Parse_Buffer, BoardId_Buffer[bi]);
                    if (retval != 0) {
                        std::cout << "  WARNING: meta parse failed"
                                  << " key="      << key
                                  << " lappd_id=" << lappdID
                                  << " entry="    << entry
                                  << " board="    << BoardId_Buffer[bi] << std::endl;
                        totalFailed++;
                        continue;
                    }

                    WriteCSVRow(csv, entry, globalEntry, path, key, lappdID, meta);
                }

                delete Ldata;
            } // end LAPPD key loop

            if (anyDataFound) {
                fileDataEvents++;
                globalEntry++;
            }

        } // end entry loop

        std::cout << "  Data frames : " << fileDataEvents << std::endl;
        std::cout << "  PPS skipped : " << filePPSEvents  << std::endl;

        delete LAPPDData;
        delete RawData;

    } // end file loop

    csv.close();

    // ── Summary ───────────────────────────────────────────────────────────
    std::cout << "\n══════════════════════════════════════" << std::endl;
    std::cout << "Done!"                                    << std::endl;
    std::cout << "  Files processed  : " << filePaths.size() << std::endl;
    std::cout << "  Data events      : " << globalEntry       << std::endl;
    std::cout << "  PPS skipped      : " << totalSkipped      << std::endl;
    std::cout << "  Meta failures    : " << totalFailed       << std::endl;
    std::cout << "  CSV written to   : lappd_metadata.csv"    << std::endl;
    std::cout << "──────────────────────────────────────"      << std::endl;

    // Per key summary
    int nLAPPDsFound = 0;
    for (const std::string& key : lappdKeys)
        if (lappdKeysFound[key] > 0) nLAPPDsFound++;

    std::cout << "  LAPPDs found     : " << nLAPPDsFound << std::endl;
    for (const std::string& key : lappdKeys) {
        if (lappdKeysFound[key] > 0)
            std::cout << "    ✓ " << key << " → "
                      << lappdKeysFound[key] << " data frames" << std::endl;
        else
            std::cout << "    ✗ " << key << " → not found"    << std::endl;
    }

    // Per LAPPD_ID summary
    std::cout << "──────────────────────────────────────"      << std::endl;
    std::cout << "  Per LAPPD_ID breakdown:"                   << std::endl;

    std::map<unsigned int, bool> allIDs;
    for (auto& kv : lappdIDDataFrames) allIDs[kv.first] = true;
    for (auto& kv : lappdIDPPSFrames)  allIDs[kv.first] = true;

    for (auto& kv : allIDs) {
        unsigned int id  = kv.first;
        int dataFrames   = lappdIDDataFrames.count(id) ? lappdIDDataFrames[id] : 0;
        int ppsFrames    = lappdIDPPSFrames.count(id)  ? lappdIDPPSFrames[id]  : 0;
        std::cout << "    LAPPD_ID=" << id
                  << "  data=" << dataFrames
                  << "  pps="  << ppsFrames  << std::endl;
    }

    std::cout << "══════════════════════════════════════" << std::endl;

    return 0;
}
