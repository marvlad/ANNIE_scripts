#include "ConditionalDT.h"
#include <iostream>
#include <TRandom3.h>
#include <TCanvas.h>

int main() {

    gRandom->SetSeed(0);

    ConditionalDT cond("analysis.root", "h_deltat_vs_energy_numu_all");

    if (!cond.isValid()) {
        std::cout << "Could not load conditional Delta_t map.\n";
        return 1;
    }

    double Enu = 0.82;
    double dt = cond.sample(Enu);

    //std::cout << "Sampled Delta t for Enu=" << Enu << " GeV: " << dt << " ns\n";

    // Example: draw PDF for a bin
    // cond.getSlice(5)->Draw();
    TH1D* h = (TH1D*)cond.getSlice(5)->Clone("test");
    h->Reset();

    int size = 1000000;
    for(int i=0; i<size; i++){
       std::cout << "\r\033[K";
       std::cout << "Progress " << 100*i/size << "%" << std::flush;
       h->Fill(cond.sample(0.44));
    }

    TCanvas* c = new TCanvas("c","my canvas",800,600);
    h->Draw("hist E");
    c->SaveAs("plot.pdf");

    delete c;
    delete h;
    
    return 0;
}
