#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <bitset>
#include "PsecData.h"
#include "BoostStore.h"
#include "lappd_helper.h"

// ══════════════════════════════════════════════════════════════════════════════
// CSV HEADER
// ══════════════════════════════════════════════════════════════════════════════
void WriteCSVHeader(std::ofstream& csv) {
    csv << "global_entry,file_entry,filename,board_id,";
    for (int chip = 0; chip < 5; chip++) {
        std::string c = "psec" + std::to_string(chip) + "_";
        csv << c << "wilkinson_current,"
            << c << "wilkinson_target,"
            << c << "vbias,"
            << c << "selftrig_threshold,"
            << c << "provdd,"
            << c << "selftrig_mask,"
            << c << "selftrig_thresh_word,"
            << c << "vcdl_count,";
        for (int ch = 0; ch < 6; ch++)
            csv << c << "ch" << ch << "_trig_rate,";
    }   
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
                 const std::vector<unsigned short>& meta)
{
    if (meta.size() < 103) {
        std::cout << "  WARNING: meta too small (" << meta.size()
                  << "), skipping row." << std::endl;
        return;
    }   

    // Extract filename from full path
    std::string fname = filepath.substr(filepath.find_last_of("/\\") + 1); 

    // ── Identity ─────────────────────────────────────────────────────────
    csv << globalEntry << "," 
        << entry       << "," 
        << fname       << "," 
        << meta[0]     << ",";   // board ID

    // ── Per-chip fields ───────────────────────────────────────────────────
    // Layout in meta per chip (20 words each, starting at offset 1):
    //   o+0  chip header (0xDCBN)
    //   o+1  wilkinson current
    //   o+2  wilkinson target
    //   o+3  vbias
    //   o+4  selftrig threshold setting
    //   o+5  provdd
    //   o+6  trigger info 0 (beamgate slice — decoded below)
    //   o+7  selftrig mask
    //   o+8  selftrig threshold word
    //   o+9  timestamp slice  (decoded below)
    //   o+10 event count slice
    //   o+11 vcdl [15:0]
    //   o+12 vcdl [31:16]
    //   o+13 dllvdd
    //   o+14..o+19  6 self-trig rate counts (one per channel)
    for (int chip = 0; chip < 5; chip++) {
        int o = 1 + chip * 20; 

        unsigned int vcdl = ((unsigned int)meta[o + 12] << 16) | meta[o + 11];

        csv << meta[o + 1] << ","    // wilkinson current
            << meta[o + 2] << ","    // wilkinson target
            << meta[o + 3] << ","    // vbias
            << meta[o + 4] << ","    // selftrig threshold
            << meta[o + 5] << ","    // provdd
            << meta[o + 7] << ","    // selftrig mask
            << meta[o + 8] << ","    // selftrig threshold word
            << vcdl         << ",";  // vcdl combined 32-bit

        for (int ch = 0; ch < 6; ch++)
            csv << meta[o + 14 + ch] << ",";
    }   

    // ── Reconstruct 64-bit beamgate from 4 slices ─────────────────────────
    // Slices live at meta indices: 7, 27, 47, 67
    // (= o+6 for chip 0,1,2,3 = 1+0*20+6, 1+1*20+6, 1+2*20+6, 1+3*20+6)
    unsigned long beamgate_raw =
        ((unsigned long)meta[7]  << 48) |
        ((unsigned long)meta[27] << 32) |
        ((unsigned long)meta[47] << 16) |
        ((unsigned long)meta[67]);

    // ── Reconstruct 64-bit timestamp from 4 slices ────────────────────────
    // Slices live at meta indices: 70, 50, 30, 10
    // (= o+9 for chip 3,2,1,0 — note reversed bit order per firmware spec)
    unsigned long timestamp_raw =
        ((unsigned long)meta[70] << 48) |
        ((unsigned long)meta[50] << 32) |
        ((unsigned long)meta[30] << 16) |
        ((unsigned long)meta[10]);

    // ── Clock cycle: last 3 bits of timestamp[15:0] (meta[10]) ───────────
    int clockcycle = meta[10] & 0x7;

    // ── Convert to nanoseconds (integer arithmetic avoids precision loss) ──
    // Clock runs at 320 MHz → 1 tick = 25/8 ns
    // ns = (raw / 8) * 25 + (raw % 8) * 3   [integer approx, same as SaveTimeStamps]
    unsigned long bg_trunc  = beamgate_raw  % 8;
    unsigned long bg_ns     = (beamgate_raw  - bg_trunc)  / 8 * 25 + bg_trunc  * 3;

    unsigned long ts_trunc  = timestamp_raw % 8;
    unsigned long ts_ns     = (timestamp_raw - ts_trunc) / 8 * 25 + ts_trunc * 3;

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

    // ── Open CSV (written once across all files) ──────────────────────────
    std::ofstream csv("lappd_metadata.csv");
    if (!csv.is_open()) {
        std::cerr << "ERROR: cannot open lappd_metadata.csv for writing" << std::endl;
        return 1;
    }   
    WriteCSVHeader(csv);

    verbosity    = 0;   // suppress lappd_helper internal prints
    int globalEntry   = 0;   // data-event counter across all files
    int totalSkipped  = 0;   // PPS frames skipped
    int totalFailed   = 0;   // meta parse failures

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

            PsecData* Ldata = new PsecData;
            LAPPDData->Get("LAPPDData", *Ldata);

            std::vector<unsigned short>& Raw_Buffer    = Ldata->RawWaveform;
            std::vector<int>&            BoardId_Buffer = Ldata->BoardIndex;

            // Skip entries with empty buffers
            if (Raw_Buffer.empty() || BoardId_Buffer.empty()) {
                delete Ldata;
                continue;
            }   

            int frametype = (int)(Raw_Buffer.size() / BoardId_Buffer.size());

            // Skip PPS frames
            if (frametype != NUM_VECTOR_DATA) {
                filePPSEvents++;
                totalSkipped++;
                delete Ldata;
                continue;
            }   

            // ── Loop over boards ──────────────────────────────────────────
            int nbi = (int)BoardId_Buffer.size();
            for (int bi = 0; bi < nbi; bi++) {
                meta.clear();
                Parse_Buffer.clear();

                for (int c = bi * frametype; c < (bi + 1) * frametype; c++)
                    Parse_Buffer.push_back(Raw_Buffer[c]);

                int retval = getParsedMeta(Parse_Buffer, BoardId_Buffer[bi]);
                if (retval != 0) {
                    std::cout << "  WARNING: meta parse failed"
                              << " entry=" << entry
                              << " board=" << BoardId_Buffer[bi]
                              << " retval=" << retval << std::endl;
                    totalFailed++;
                    continue;
                }   

                WriteCSVRow(csv, entry, globalEntry, path, meta);
            }   

            globalEntry++;
            fileDataEvents++;
            delete Ldata;
        }   

        std::cout << "  Data frames: " << fileDataEvents
                  << "  PPS frames skipped: " << filePPSEvents << std::endl;

        delete LAPPDData;
        delete RawData;
    }   

    csv.close();

    // ── Summary ───────────────────────────────────────────────────────────
    std::cout << "\n══════════════════════════════════════" << std::endl;
    std::cout << "Done!" << std::endl;
    std::cout << "  Files processed  : " << filePaths.size()  << std::endl;
    std::cout << "  Data events      : " << globalEntry        << std::endl;
    std::cout << "  PPS skipped      : " << totalSkipped       << std::endl;
    std::cout << "  Meta failures    : " << totalFailed        << std::endl;
    std::cout << "  CSV written to   : lappd_metadata.csv"     << std::endl;
    std::cout << "══════════════════════════════════════" << std::endl;

    return 0;
}
