"""
Copyright 2023 Scott J. Brandenberg

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the “Software”),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR
THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import numpy as np

def smoothed_fas(fas, f, fc, b, w):
    '''
    Input Fourier amplitude spectrum, frequency array, smoothed frequency
    array, and Konno-Omachi smoothing parameters b and w. Export smoothed
    Fourier amplitude spectrum.

    fas = Fourier amplitude spectrum. Real-valued numpy array.
    f = Frequency array. Real-valued numpy array.
    fc = Frequency values for smoothed Fourier spectrum.
         Real-valued numpy array.
    b = Konno-Omachi smoothing parameter. Real-valued scalar.
    w = Konno-Omachi bandwidth parameter. Real-valued scalar.
    fac_c = Smoothed Fourier amplitude spectrum. Real-valued numpy array.
    '''
    fdivfc = f[:, np.newaxis]/fc
    filt = (fdivfc > w) & (fdivfc < 1/w) & (abs(fdivfc-1.0) > 1.e-6)
    weights = np.zeros(fdivfc.shape)
    weights[abs(fdivfc-1.0) < 1.e-6] = 1.0
    weights[filt] = abs(np.sin(b*np.log10(fdivfc[filt]))/(b*np.log10(fdivfc[filt])))**4.0
    weights = weights/np.sum(weights, axis=0)
    fas_c = fas@weights
    return fas_c

def get_smooth_eas(acc1, acc2, dt, b, w):
    '''
    Input two acceleration time series, time step, and Konno-Omachi
    smoothing parameters.
    
    Return smooth effective amplitude spectrum.
    acc1, acc2 = acceleration time series. Real-valued numpy arrays.
    dt = time step in seconds. Real-valued.
    b = Konno-Omachi smoothing parameter. Real-valued scalar.
    w = Konno-Omachi bandwidth parameter. Real-valued scalar.
    fc = Frequency values for smoothed spectrum. Real-valued numpy array.
    eas = effective amplitude spectrum. Real-valued numpy array.
    '''
    dt_vec = [0.005, 0.01, 0.02, 0.025, 0.05, 0.10]
    nfft_vec = [19, 18, 17, 17, 16, 15]
    nfft = 2**int(np.interp(dt, dt_vec, nfft_vec))
    
    f1 = np.fft.rfft(acc1, n=nfft) * dt
    f2 = np.fft.rfft(acc2, n=nfft) * dt
    eas = 0.5 * (np.abs(f1)**2 + np.abs(f2)**2)
    freq = np.fft.rfftfreq(nfft, d=dt)
    fc = np.asarray([0.01318257, 0.01348963, 0.01380385, 0.01412538,
                     0.0144544, 0.01479109, 0.01513562, 0.01548817,
                     0.015848932, 0.016218101, 0.01659587, 0.01698244,
                     0.01737801, 0.017782792, 0.01819701, 0.01862087,
                     0.019054604, 0.01949845, 0.019952621, 0.02041738,
                     0.02089296, 0.021379621, 0.02187762, 0.022387214,
                     0.02290868, 0.02344229, 0.02398833, 0.02454709,
                     0.02511887, 0.025703962, 0.026302684,
                     0.026915352, 0.027542291, 0.028183832,
                     0.02884032, 0.029512094, 0.03019952, 0.03090296,
                     0.031622774, 0.032359361, 0.03311311,
                     0.033884413, 0.03467368, 0.035481333, 0.0363078,
                     0.03715353, 0.038018941, 0.03890452, 0.03981072,
                     0.040738031, 0.04168694, 0.04265795, 0.04365158,
                     0.04466836, 0.04570882, 0.046773523, 0.04786302,
                     0.04897789, 0.05011873, 0.051286142, 0.05248075,
                     0.053703181, 0.05495409, 0.056234132,
                     0.057543992, 0.058884363, 0.06025596, 0.0616595,
                     0.06309573, 0.064565412, 0.06606936, 0.067608304,
                     0.0691831, 0.070794582, 0.0724436, 0.07413102,
                     0.075857751, 0.07762471, 0.079432822, 0.08128305,
                     0.08317637, 0.085113793, 0.08709637, 0.089125104,
                     0.0912011, 0.09332544, 0.095499262, 0.097723722,
                     0.1, 0.1023293, 0.1047129, 0.10715192,
                     0.10964782, 0.11220184, 0.1148154, 0.1174898,
                     0.12022643, 0.1230269, 0.12589254, 0.12882494,
                     0.1318257, 0.1348963, 0.13803841, 0.14125373,
                     0.144544, 0.14791083, 0.15135611, 0.1548817,
                     0.15848931, 0.162181, 0.1659587, 0.1698244,
                     0.1737801, 0.177828, 0.1819701, 0.18620871,
                     0.1905461, 0.19498443, 0.1995262, 0.2041738,
                     0.20892961, 0.2137962, 0.2187762, 0.22387212,
                     0.2290868, 0.2344229, 0.2398833, 0.2454709,
                     0.2511886, 0.25703954, 0.2630268, 0.26915344,
                     0.2754229, 0.2818383, 0.28840312, 0.29512092,
                     0.3019952, 0.30902954, 0.3162278, 0.32359364,
                     0.3311311, 0.33884412, 0.34673681, 0.3548134,
                     0.3630781, 0.37153521, 0.3801894, 0.38904511,
                     0.39810714, 0.4073803, 0.4168694, 0.42657953,
                     0.4365158, 0.4466836, 0.4570882, 0.4677351,
                     0.4786301, 0.48977881, 0.5011872, 0.51286131,
                     0.5248075, 0.5370318, 0.5495409, 0.5623413,
                     0.57543992, 0.5888436, 0.6025595, 0.61659491,
                     0.6309573, 0.6456543, 0.6606934, 0.676083,
                     0.69183093, 0.7079458, 0.72443592, 0.74131023,
                     0.7585776, 0.7762471, 0.79432821, 0.81283044,
                     0.8317637, 0.8511381, 0.8709636, 0.8912509,
                     0.9120108, 0.93325424, 0.9549925, 0.9772371, 1,
                     1.023293, 1.047129, 1.0715192, 1.096478,
                     1.1220182, 1.1481534, 1.1748973, 1.2022641,
                     1.230269, 1.258926, 1.28825, 1.318257, 1.348963,
                     1.3803842, 1.4125374, 1.44544, 1.4791082,
                     1.513561, 1.5488164, 1.584893, 1.62181, 1.659587,
                     1.698244, 1.737801, 1.7782794, 1.819701,
                     1.862087, 1.905461, 1.9498444, 1.9952621,
                     2.041738, 2.089296, 2.137962, 2.187761,
                     2.2387211, 2.290868, 2.344229, 2.398833,
                     2.454709, 2.5118863, 2.570396, 2.630268,
                     2.691535, 2.7542283, 2.818383, 2.884031,
                     2.951209, 3.019952, 3.090296, 3.162278, 3.235937,
                     3.311311, 3.3884413, 3.4673681, 3.548134,
                     3.63078, 3.715352, 3.8018932, 3.890451, 3.981071,
                     4.073803, 4.168694, 4.2657952, 4.365158,
                     4.4668354, 4.5708813, 4.677351, 4.7863001,
                     4.897787, 5.011872, 5.128613, 5.248074,
                     5.3703184, 5.495409, 5.623413, 5.7543992,
                     5.8884363, 6.025596, 6.1659493, 6.309573,
                     6.456542, 6.606934, 6.7608284, 6.9183082,
                     7.0794563, 7.24436, 7.413103, 7.585776, 7.762471,
                     7.9432821, 8.1283044, 8.3176364, 8.5113792,
                     8.709635, 8.912507, 9.120107, 9.332541, 9.549923,
                     9.7723722, 10, 10.23293, 10.471284, 10.715192,
                     10.96478, 11.220183, 11.481534, 11.748973,
                     12.022642, 12.302684, 12.589251, 12.882492,
                     13.182563, 13.489624, 13.80384, 14.12537,
                     14.454392, 14.79108, 15.135614, 15.48817,
                     15.848933, 16.218101, 16.59587, 16.98244,
                     17.37801, 17.782793, 18.19701, 18.62087,
                     19.05461, 19.498443, 19.952621, 20.41738,
                     20.89296, 21.37962, 21.877611, 22.38721,
                     22.908672, 23.442283, 23.988321, 24.54708,
                     25.11886, 25.70395, 26.30267, 26.91534,
                     27.542291, 28.183832, 28.84032, 29.512094,
                     30.19952, 30.902954, 31.62278, 32.359363,
                     33.11311, 33.884414, 34.673683, 35.481334,
                     36.3078, 37.153514, 38.018932, 38.90451,
                     39.81071, 40.73802, 41.68693, 42.65794, 43.65157,
                     44.668342, 45.70881, 46.7735, 47.862991,
                     48.97789, 50.11873, 51.286144, 52.480751,
                     53.703182, 54.95409, 56.23413, 57.543991,
                     58.884361, 60.255954, 61.6595, 63.09573,
                     64.565414, 66.06933, 67.608283, 69.183082,
                     70.79456, 72.443572, 74.131004, 75.857734,
                     77.62469, 79.432792, 81.28303, 83.17635,
                     85.11377, 87.096321, 89.1251, 91.2011, 93.32544,
                     95.49926, 97.723724, 100])
    fc = fc[fc<=np.max(freq)]
    eas_s = smoothed_fas(np.abs(eas), freq, fc, b, w)

    # Since we also return the FAS results(f1 and f2), we
    # need to convert any complex numbers into real amplitudes
    f1 = np.abs(f1)
    f2 = np.abs(f2)

    return([freq, f1, f2, eas, fc, np.sqrt(eas_s)])
