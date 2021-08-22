import math
import wave
import struct
import numpy as np
import matplotlib.pyplot as plt

audio = []
sample_rate = 44100.0

duration_milliseconds=20000

num_samples = duration_milliseconds * (sample_rate / 1000.0)

arg = 0.0

fw = [75.0,150.0,300.0,600.0,1200.0,2400.0,4800.0,9600.0]
fv = fw
pairs = [[0,7],[1,6],[2,5],[3,4],[2,5],[1,6],[0,7]]
cnt = 0
cnt1 = -1
cntDiminish = -1
T = num_samples/7.0
isDiminishing = False
isGrowing = True
ntrans = 1000
trans = []
muting = 1.0
mutingCoeff = 0.99
for nt in range(ntrans):
    trans.append(muting)
    muting *= mutingCoeff
nt = 0
for x in range(int(num_samples)):
    y = 0.0
    norm = 1.0
    cnt = int(7.0*x/num_samples)
    if T-np.mod(x,int(T)) < ntrans and cntDiminish != cnt:
        nt = 0
        isDiminishing = True
        isGrowing = False
        cntDiminish = cnt
    elif cnt != cnt1:
        nt = ntrans-1
        isDiminishing = False
        isGrowing = True
    cnt1 = cnt
    pair = pairs[cnt]
    prevPair = pairs[max(0,cnt-1)]
    fading = 1.0
    fc = -1
    gc = -1
    ampl = trans[nt]
    for f in fv:
        fc += 1
        norm *= 0.8
        if fc not in pair:
            continue
        arg = 2.0 * math.pi * f * ( x / sample_rate )
        gc += 1
        modulate = 1.0
        modulate = 0.5 + 0.5*math.cos(4.0*math.pi*x/T)
        if gc == 1:
            modulate = 1.0 - modulate
        y += modulate*ampl*math.sin(arg)*norm
    muting = mutingCoeff*muting
    audio.append(y/2.0)
    if isDiminishing:
        nt = np.min([ntrans-1,nt+1])
    elif isGrowing:
        nt = np.max([0,nt-1])

file_name = "output2.wav"

wav_file=wave.open(file_name,"w")

nchannels = 1
sampwidth = 2

nframes = len(audio)
comptype = "NONE"
compname = "not compressed"
wav_file.setparams((nchannels, sampwidth, sample_rate, nframes, comptype, compname))

for sample in audio:
    wav_file.writeframes(struct.pack('h', int( sample * 32767.0 )))

wav_file.close()
