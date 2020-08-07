import numpy as np
from pandas import DataFrame as df
import lmfit
from lmfit import model
from lmfit.models import GaussianModel, LinearModel, VoigtModel, PolynomialModel
import AnalysisTools

class Run :

    def __init__(self) :

        pass

    def Parameters(self,Region) :

        dic = {
            'FolderPath': '../../Binned/BT2/',
            'Runs': 'XAS_000_000',
            'BackgroundRun': 'XAS_017_017_E50.h5',
    #         'BackgroundRun': 'None',
            'NormROI': (285, 286.4),
            'xOffset': -0.31,
            'Normalize': False,
            'ScalingFactor': 1,
        }

        if Region == 'Pi Star' :
            dic['ROI'] = (286, 290)
            dic['NumPeaks'] = 7
            dic['NumRefPeaks'] = 1
            dic['TrendDelayRange'] = (-2000,11000)
            dic['TrendFits'] = {
                            'G1_amp': {'a': 0.002, 'b': 0.003, 't0': 0, 'sigma': 237},
                            'G2_amp': {'a': 0.011, 'b': 0.0004, 't0': 260, 'sigma': 990},
                            'G6_amp': {'a': 0.006, 'b': 0, 't0': 1000, 'sigma': 1500},
                            'G5_amp': {'a': 0.003, 'b': 0, 't0': 1000, 'sigma': 1500},
                            }
            dic['TrendData'] = {
                            'Low': {'Range': (286.6,287.0), 'a': 0.002, 'b': 0.003, 't0': 0, 'sigma': 237},
                            'Vibrational1': {'Range': (287.4,287.5), 'a': 0.011, 'b': 0.0004, 't0': 260, 'sigma': 990},
                            'Vibrational2': {'Range': (287.6,287.7), 'a': 0.011, 'b': 0.0004, 't0': 260, 'sigma': 990},
                            'Negative': {'Range': (288.2,289), 'a': -0.004, 'b': 0.0076, 't0': 315, 'sigma': 415},
                            }

        if Region == 'Middle' :
            dic['ROI'] = (289,291.8)
            dic['NumPeaks'] = 1
            dic['NumRefPeaks'] = 0

        if Region == 'Shape Resonance' :
            dic['ROI'] = (292,295)
            dic['NumPeaks'] = 1
            dic['NumRefPeaks'] = 0

        return dic

    def FitData(self,Energy,Delay,Signal,ErrorBars,Region,NumberPeaks,NumRefPeaks) :

        ##### Build fit model #####

        ModelString = 'L'
        i = 0
        while i < NumberPeaks :
            ModelString = ModelString + 'G'
            i+=1
        fit = AnalysisTools.FitTools(ModelString)
        Params = fit.Model.make_params()

        ##### Fit data #####

        i = 0
        while i < len(Delay) :

            ##### Remove NaNs #####

            remove = np.argwhere(np.isnan(Signal[i]))
            x = np.delete(Energy,remove)
            y = np.delete(Signal[i],remove)
            err = np.delete(ErrorBars[i],remove)

            ##### Fitting parameters #####

            """
            CO desorption on Ru(0001) values:
                CO (adsorbed):  288.01 eV  Unpumped
                                287.92 eV  Pumped
                CO (gas phase): 287.42 eV  0-0 transition
                                0.256  eV  vibrational spacing
            """

            Vibrational_Sigma = 0.12

            if Region == 'Pi Star' :

                Name = 'L1'
                Params[Name+'_intercept'].value = -0.003396881
                Params[Name+'_intercept'].vary = True
                Params[Name+'_slope'].value = 1.19E-05
                Params[Name+'_slope'].vary = True
                Name = 'G1'
                Params[Name+'_amplitude'].value = 0.02
                Params[Name+'_amplitude'].min = 0
                Params[Name+'_center'].value = 288.01
                Params[Name+'_center'].min = 287.92
                Params[Name+'_center'].vary = True
                Params[Name+'_sigma'].value = 0.415
                Params[Name+'_sigma'].vary = False
                if NumberPeaks >= 2 :
                    Name = 'G2'
                    Params[Name+'_amplitude'].value = 0.01
                    Params[Name+'_amplitude'].vary = True
                    Params[Name+'_amplitude'].min = 0
                    Params[Name+'_center'].value = 287.42
                    Params[Name+'_center'].vary = False
                    Params[Name+'_sigma'].value = Vibrational_Sigma
                    Params[Name+'_sigma'].min = 0.1
                    Params[Name+'_sigma'].vary = False
                if NumberPeaks >= 3 :
                    Name = 'G3'
                    Params[Name+'_amplitude'].set(expr='G2_amplitude*1.18/4.1')
                    Params[Name+'_amplitude'].min = 0
                    Params[Name+'_amplitude'].vary = True
                    Params[Name+'_center'].set(expr='G2_center+0.256')
                    Params[Name+'_center'].vary = False
                    Params[Name+'_sigma'].value = Vibrational_Sigma
                    Params[Name+'_sigma'].min = 0.1
                    Params[Name+'_sigma'].vary = False
                if NumberPeaks >= 4 :
                    Name = 'G4'
                    Params[Name+'_amplitude'].set(expr='G2_amplitude*0.21/4.1')
                    Params[Name+'_amplitude'].vary = True
                    Params[Name+'_amplitude'].min = 0
                    Params[Name+'_center'].set(expr='G2_center+2*0.256')
                    Params[Name+'_center'].vary = False
                    Params[Name+'_sigma'].value = Vibrational_Sigma
                    Params[Name+'_sigma'].min = 0.1
                    Params[Name+'_sigma'].vary = False
                if NumberPeaks >= 5 :
                    Name = 'G5'
    #                 Params['G5_amplitude'].set(expr='G2_amplitude*0.381932549')
                    Params[Name+'_amplitude'].min = 0
                    Params[Name+'_amplitude'].vary = True
                    Params[Name+'_center'].set(expr='G2_center-0.256')
                    Params[Name+'_center'].vary = False
                    Params[Name+'_sigma'].value = Vibrational_Sigma
                    Params[Name+'_sigma'].vary = False
                if NumberPeaks >= 6 :
                    Name = 'G6'
                    Params[Name+'_amplitude'].set(expr='G5_amplitude/1.8')
                    Params[Name+'_amplitude'].min = 0
    #                 Params['G6_amplitude'].vary = True
                    Params[Name+'_center'].set(expr='G2_center-2*0.256')
                    Params[Name+'_center'].vary = False
                    Params[Name+'_sigma'].value = Vibrational_Sigma
                    Params[Name+'_sigma'].vary = False
                if NumberPeaks >= 7 :
                    Name = 'G7'
                    Params[Name+'_amplitude'].value= 0.01
                    Params[Name+'_amplitude'].min = 0
                    Params[Name+'_amplitude'].vary = True
                    Params[Name+'_center'].value = 287.65     # 287.64
                    Params[Name+'_center'].vary = False
                    Params[Name+'_sigma'].value = 0.08
                    Params[Name+'_sigma'].vary = False

                # Reference delay
                if NumRefPeaks >= 1 :
                    if i == 0 :
                        if NumberPeaks >= 2 :
                            Params['G2_amplitude'].value = 0
                            Params['G2_amplitude'].vary = False
                        if NumberPeaks >= 3 :
                            Params['G3_amplitude'].value = 0
                            Params['G3_amplitude'].vary = False
                        if NumberPeaks >= 4 :
                            Params['G4_amplitude'].value = 0
                            Params['G4_amplitude'].vary = False
                        if NumberPeaks >= 5 :
                            Params['G5_amplitude'].value = 0
                            Params['G5_amplitude'].vary = False
                        if NumberPeaks >= 6 :
                            Params['G6_amplitude'].value = 0
                            Params['G6_amplitude'].vary = False
                        if NumberPeaks >= 7 :
                            Params['G7_amplitude'].value = 0
                            Params['G7_amplitude'].vary = False
                    else :
                        Params['L1_intercept'].value = FitParameters[0,1]
                        Params['L1_intercept'].vary = False
                        Params['L1_slope'].value = FitParameters[0,2]
                        Params['L1_slope'].vary = False
                        Params['G1_amplitude'].value = FitParameters[0,3]
                        Params['G1_center'].value = FitParameters[0,4]
                        Params['G1_sigma'].value = FitParameters[0,5]

                        Shift = 0
                        if Delay[i] > 4000 :
                            Shift = -0.09
    #                     if Delay[i] > 5000 :
    #                         Shift = -0.22
                        Params['G1_center'].value = FitParameters[0,4] + Shift

            if Region == 'Middle' :

                Params['L1_slope'].value = -0.003129523
                Params['L1_slope'].vary = False
                Params['L1_intercept'].value = 0.916163878
                Params['L1_intercept'].vary = False
                Params['G1_amplitude'].value = 0.03
                Params['G1_amplitude'].min = 0
                Params['G1_center'].value = 290.9
                Params['G1_center'].vary = False
                Params['G1_sigma'].value = 0.35

            if Region == 'Shape Resonance' :

                Params['L1_slope'].value = -0.003402839
                Params['L1_slope'].vary = False
                Params['L1_intercept'].value = 0.997181538
                Params['L1_intercept'].vary = False
                Params['G1_amplitude'].value = 0.03
                Params['G1_amplitude'].min = 0
                Params['G1_center'].value = 293.76
                Params['G1_center'].vary = False
                Params['G1_sigma'].value = 0.34
                Params['G1_sigma'].vary = False

            ##### Fit the data #####

            FitResults = fit.Fit(x,y,err,Delay[i],Params)
            fit.Plot()
            if i == 0 :
                FitParameters = np.zeros((len(Delay),len(fit.Parameters)))
                Fit_Signal = np.zeros((len(Delay),len(fit.fit_y)))
            FitParameters[i] = fit.Parameters
            Fit_Energy = fit.fit_x
            Fit_Signal[i] = fit.fit_y

            i += 1

            print('_'*110)

        FitParameters = df(data=FitParameters,columns=fit.ParameterNames)

        fit.PlotAnalysis('amp',FitParameters,fit.ParameterNames)
        fit.PlotAnalysis('ω',FitParameters,fit.ParameterNames)
        fit.PlotAnalysis('σ',FitParameters,fit.ParameterNames)
        fit.PlotDataAndFits(Energy, Signal, Fit_Energy, Fit_Signal, Delay)

        self.fit = fit
        self.FitParameters = FitParameters
        self.Fit_Energy = Fit_Energy
        self.Fit_Signal = Fit_Signal
