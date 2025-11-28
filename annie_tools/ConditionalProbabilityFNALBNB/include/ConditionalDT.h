#ifndef CONDITIONAL_DT_H
#define CONDITIONAL_DT_H

#include <TH2F.h>
#include <TH1D.h>
#include <TFile.h>
#include <TString.h>
#include <vector>
#include <string>

class ConditionalDT {

public:
    ConditionalDT(const std::string& filename,
                  const std::string& histname)
    {
        load(filename, histname);
    }

    ~ConditionalDT() {
        for (auto* h : condSlices_) delete h;
    }

    // Sample delta_t for a given neutrino energy
    double sample(double Enu) const {
        if (!h_cond_) return -999;

        int Nx = h_cond_->GetNbinsX();
        int binx = h_cond_->GetXaxis()->FindBin(Enu);

        if (binx < 1) binx = 1;
        if (binx > Nx) binx = Nx;

        TH1D* pdf = condSlices_[binx];
        if (!pdf || pdf->Integral() == 0) return -999;

        return pdf->GetRandom();
    }

    // Retrieve the 1D delta_t PDF for bin index ix
    TH1D* getSlice(int ix) const {
        if (ix < 1 || ix >= (int)condSlices_.size()) return nullptr;
        return condSlices_[ix];
    }

    bool isValid() const { return valid_; }

private:
    bool valid_ = false;
    TH2F* h_cond_ = nullptr;
    std::vector<TH1D*> condSlices_;

    void load(const std::string& filename,
              const std::string& histname)
    {
        TFile* f = TFile::Open(filename.c_str());
        if (!f || f->IsZombie()) return;

        TH2F* h = (TH2F*)f->Get(histname.c_str());
        if (!h) return;

        int Nx = h->GetNbinsX();
        int Ny = h->GetNbinsY();

        // Clone for normalized conditional map
        h_cond_ = (TH2F*)h->Clone("h_cond");
        h_cond_->Reset();
        condSlices_.resize(Nx + 1, nullptr);

        // Build conditional probabilities
        for (int ix = 1; ix <= Nx; ix++) {

            double colSum = 0;
            for (int iy = 1; iy <= Ny; iy++)
                colSum += h->GetBinContent(ix, iy);

            if (colSum > 0) {
                for (int iy = 1; iy <= Ny; iy++) {
                    double v = h->GetBinContent(ix, iy);
                    h_cond_->SetBinContent(ix, iy, v / colSum);
                }
            }

            TString name = Form("dt_pdf_bin%d", ix);
            TH1D* proj = h_cond_->ProjectionY(name, ix, ix);
            proj->SetDirectory(0);
            condSlices_[ix] = proj;
        }

        valid_ = true;
    }
};
#endif
