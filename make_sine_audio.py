import math
import wave
import struct
import numpy as np
import matplotlib.pyplot as plt

audio = []
sample_rate = 44100.0

freq1=50.0
freq2=12800.0
duration_milliseconds=20000
volume=0.5

num_samples = duration_milliseconds * (sample_rate / 1000.0)

freqs=[]
arg = 0.0
arg2 = 0.0
#for x in range(int(num_samples)):
#    freq=freq2-(np.log(num_samples-x)/np.log(num_samples))*(freq2-freq1)
#    freqB=freq2-(np.log(1.0+x)/np.log(num_samples))*(freq2-freq1)
##    freq=freq1+(x/num_samples)*(freq2-freq1)
##    freq=freq1+(x/num_samples)**2*(freq2-freq1)
#    freqs.append(freq+freqB)
#    arg += 2.0 * math.pi * freq * ( 1.0 / sample_rate )
#    arg2 += 2.0 * math.pi * freqB * ( 1.0 / sample_rate )
#    y=math.sin(arg)
#    y+=math.sin(arg2)
##    y+=math.sin(arg)
#    audio.append(volume * y)

fw = [75.0,150.0,300.0,600.0,1200.0,2400.0,4800.0,9600.0]
fv = fw
pairs = [[0,7],[1,6],[2,5],[3,4],[2,5],[1,6],[0,7]]
cnt = 0
cnt1 = 0
muting = 1.0
mutingCoeff = 1.0
for x in range(int(num_samples)):
    y = 0.0
    norm = 1.0
    cnt = int(7.0*x/num_samples)
    if cnt == 0 or cnt != cnt1:
        muting = 1.0
        mutingCoeff = 0.99
    muting = mutingCoeff*muting
    cnt1 = cnt
    pair = pairs[cnt]
    prevPair = pairs[max(0,cnt-1)]
    fading = 1.0
    fc = -1
    for f in fv:
        fc += 1
        norm *= 0.8
        if fc not in pair and fc not in prevPair:
            continue
        ampl = 1.0
        if cnt > 0 and fc in prevPair:
            ampl = muting
        elif cnt == 0:
            ampl = muting
        else:
            ampl = 1.0-muting
        arg = 2.0 * math.pi * f * ( x / sample_rate )
        y += ampl*math.sin(arg)*norm
    audio.append(y/2.0)

plt.plot(freqs)

file_name = "output.wav"

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
