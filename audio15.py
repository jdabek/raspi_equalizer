import pyaudio
import wave
import numpy as np
import os
import sys
import RPi.GPIO as GPIO
import time
import threading
from threading import Thread

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 4096
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "file.wav"

pins = [26,19,13,6,5,16,20,21]

def getBases(nsamp, fs):
    fn = "bases.txt"
    f = open(fn, "w")
    f.write("")
    f.close()
    f0 = [50]
#    f0 += [np.round((fs/nsamp)*2.3**i) for i in range(1, 9)]
    f0 += [100,200,400,800,1600,3200,6400,12800]
    print(f0)
    freqs = [[1+f0[i],f0[i+1]] for i in range(0,len(f0)-1)]
    Fv = [[0.5*(x[0]+x[1]), x[1]-x[0]+1.0] for x in freqs]
    tv = []
    dt = 1.0/fs
    for i in range(0, nsamp):
        tv.append(dt*(i-0.5*nsamp))
    bases = []
    for F in Fv:
        re = []
        im = []
        for i in range(0, nsamp):
            x = F[0]*tv[i]
            temp = np.min(F)
            if np.abs(temp*tv[i]) > 1:
                continue
            x = 2*np.pi*x
            cos = np.cos(x)
            sin = np.sin(x)
            sinc = np.sinc(F[1]*tv[i])
            re.append(cos*sinc)
            im.append(sin*sinc)
#        f = open(fn, "a")
#        f.write(str(F) + "\n" + str(re) + "\n" + str(im) + "\n")
#        f.close()
        bases.append([re,im])

    for j in range(0, len(bases)):
        valRe = 0.0
        valIm = 0.0
        for i in range(0, len(bases[j][0])):
            valRe += bases[j][0][i]**2
            valIm += bases[j][0][i]**2
        val = np.sqrt((valRe+valIm)/len(bases[j][0]))
        for i in range(0, len(bases[j][0])):
            bases[j][0][i] /= val*np.sqrt(nsamp)
            bases[j][1][i] /= val*np.sqrt(nsamp)
        f = open(fn, "a")
        f.write(str(Fv[j]) + "\n" + str(bases[j][0]) + "\n" + str(bases[j][1]) + "\n")
        f.close()

    return [Fv, bases]

def getBaseAmplitudes(Fv, bases, signal):
    valuesRe = [0.0]*len(bases)
    valuesIm = [0.0]*len(bases)
    values = [0.0]*len(bases)
    for j in range(0, len(bases)):
        npt = 0
        for i in range(0, len(bases[j][0])):
            npt += 1
            valuesRe[j] += bases[j][0][i]*signal[i]
            valuesIm[j] += bases[j][1][i]*signal[i]
        values[j] = np.sqrt(valuesRe[j]**2 + valuesIm[j]**2)/npt
    return(values)

def lightLeds(pins, maxamp, duration):
    dt = 0.001
    t = 0.0
    thrd = threading.currentThread()
    amps = getattr(thrd, "amps")
    while len(amps) == 0:
        amps = getattr(thrd, "amps")
    maxamp = 10
    prevAmps = amps[:]
    while getattr(thrd, "do_run"):
        amps = getattr(thrd, "amps")
        for ntime in range(0,maxamp):
            for m in range(0,8):
                prevAmps[m] = 0.7*prevAmps[m] + 0.3*amps[m]
                amp = int(prevAmps[m]*maxamp)
                if amp < 1:
                    GPIO.output(pins[m],GPIO.LOW)
                    continue
                if amp < ntime:
                    GPIO.output(pins[m],GPIO.LOW)
                else:
                    GPIO.output(pins[m],GPIO.HIGH)
            time.sleep(dt)

    GPIO.output(pins,GPIO.LOW)

def initLights(pins):
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(pins,GPIO.OUT)
    thrd = threading.currentThread()
    while getattr(thrd, "do_run"):
        GPIO.output(pins,GPIO.HIGH)
    GPIO.output(pins,GPIO.LOW)

ithread = Thread(target = initLights, args=[pins])
ithread.do_run = True
ithread.start()

print("Generating base signals...")
[Fv, bases] = getBases(CHUNK, RATE)

audio = pyaudio.PyAudio()

# start Recording
stream = audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,
                frames_per_buffer=CHUNK)
print "recording..."
frames = []

#wf = wave.open(WAVE_OUTPUT_FILENAME, 'rb')

# instantiate PyAudio (1)
p = pyaudio.PyAudio()

# open stream (2)
pstream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                frames_per_buffer=CHUNK,
                output=True)
lim = 0
#for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
nloop = 0

maxamp = 10.0
duration = 10.0*(0.0+CHUNK)/RATE
thread = Thread(target = lightLeds, args=[pins, maxamp, duration])
thread.do_run = True
thread.amps = []
ithread.do_run = False
thread.start()

while True:
    nloop += 1
#    if nloop > 50:
#        break
    data = stream.read(CHUNK, exception_on_overflow=False)
    pstream.write(data)
    waveData = wave.struct.unpack("%dh"%(CHUNK), data)
    vec = getBaseAmplitudes(Fv, bases, waveData)
    s = ""
    amps = []
#    lim = -1.0
    for v in vec:
        x = 2.0*np.log(1.0+v)
        max = int(x*(1.0-np.exp(-50.0/(1.0+x))))
        lim = max if max > lim else lim
        y = x*(1.0-np.exp(-50.0/(1.0+x)))
        for i in range(0, int(y)):
            s += "*"
        amps.append(np.min([1.0,y/maxamp]))
#        lim = amps[-1] if amps[-1] > lim else lim
        s += "\n"

    thread.amps = amps

    os.system("clear")
    print(s+"\n")
    print(str(lim))
#    break
#    frames.append(data)

thread.do_run = False

print "finished recording"

# stop Recording
stream.stop_stream()
stream.close()
audio.terminate()

#waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
#waveFile.setnchannels(CHANNELS)
#waveFile.setsampwidth(audio.get_sample_size(FORMAT))
#waveFile.setframerate(RATE)
#waveFile.writeframes(b''.join(frames))
#waveFile.close()

# stop stream (4)
pstream.stop_stream()
pstream.close()

# close PyAudio (5)
p.terminate()
