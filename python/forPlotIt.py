from ROOT import * 

def forPlotIt(year):
    f_in = TFile.Open("../output/unfold"+str(year)+"/hist_input.root")
    group = ['data_obs','ttbb','ttbj','ttcc','ttLF','ttbkg','other', 'qcd']
    for mem in group:
        print mem
        f_out = TFile.Open('../output/draw'+str(year)+'/'+mem+'_postfit_histos.root', 'recreate')
        dRnom = f_in.Get('h_mindR_RecoAddbJetDeltaR_Ch2_S3_'+str(mem))
        dRnom.SetName('h_mindR_RecoAddbJetDeltaR_Ch2_S3')
        dRnom.Write()
        if not 'data' in mem:
            dRup = f_in.Get('h_mindR_RecoAddbJetDeltaR_Ch2_S3_'+str(mem)+'__postfitup')
            dRdown = f_in.Get('h_mindR_RecoAddbJetDeltaR_Ch2_S3_'+str(mem)+'__postfitdown')
            dRup.SetName('h_mindR_RecoAddbJetDeltaR_Ch2_S3__postfitup')
            dRdown.SetName('h_mindR_RecoAddbJetDeltaR_Ch2_S3__postfitdown')
            dRup.Write()
            dRdown.Write()
        Mnom = f_in.Get('h_mindR_RecoAddbJetInvMass_Ch2_S3_'+str(mem))
        Mnom.SetName('h_mindR_RecoAddbJetInvMass_Ch2_S3')
        Mnom.Write()
        if not 'data' in mem:
            Mup = f_in.Get('h_mindR_RecoAddbJetInvMass_Ch2_S3_'+str(mem)+'__postfitup')
            Mdown = f_in.Get('h_mindR_RecoAddbJetInvMass_Ch2_S3_'+str(mem)+'__postfitdown')
            Mup.SetName('h_mindR_RecoAddbJetInvMass_Ch2_S3__postfitup')
            Mdown.SetName('h_mindR_RecoAddbJetInvMass_Ch2_S3__postfitdown')
            Mup.Write()
            Mdown.Write()
        f_out.Close()

forPlotIt(16)
forPlotIt(17)
forPlotIt(18)

