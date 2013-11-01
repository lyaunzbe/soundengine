"""
soundEngine.py - source code for CS4500 semester project
Ben Lyaunzon
Rory Sawyer
Alec Schwartz
Eduardo Romeiro
"""

import sys, wave, struct
import numpy as np
 
def main(file1, file2):
    # If either file1 or file2 aren't WAVE, wave.open() throws an error
    try:
      # Read in both files and extract the number of audio frames, frame
      # rate, and read all audio frames, then close the file and perform
      # a Fast Fourier Transform on the files
      sound1 = wave.open(file1, 'r')
      sound2 = wave.open(file2, 'r')
      # Get frames of length n
      size1 = sound1.getnframes()
      size2 = sound2.getnframes()
      # read number of frames of size n
      data1 = sound1.readframes(size1)
      data2 = sound2.readframes(size2)
      #instantiate some framerates
      frate1 = sound1.getframerate()
      frate2 = sound2.getframerate()
      #close audio files 
      sound1.close()
      sound2.close()
      #Unpack strings into an array of values
      data1 = struct.unpack('{n}h'.format(n=len(data1)/2), data1)
      data2 = struct.unpack('{n}h'.format(n=len(data2)/2), data2)
      #Calculate samples per frame
      samplesPerFrame1 = 0.03*frate1   # size  of frame in samples. 30 ms frame size
      samplesPerFrame2 = 0.03*frate2
      framedSignal1 = []
      framedSignal2 = []
      i = 0
      # Frame signals
      # TODO: apply hamming, overlap windows
      while i < len(data1):
        framedSignal1.append(data1[i:int(i + samplesPerFrame1)])
        framedSignal2.append(data2[i:int(i + samplesPerFrame2)])
        i = int(i + samplesPerFrame1)
      ffts1 = []
      ffts2 = []
      #Calculate FFT values from framed signals
      for signal in framedSignal1:
        if (len(signal) == 0): break
        ffts1.append(np.fft.fft(signal))
      for signal in framedSignal2:
        if (len(signal) == 0): break
        ffts2.append(np.fft.fft(signal))
      # Setup hamming wind0ow 
      hammingWindow1 = np.hamming(samplesPerFrame1)
      hammingWindow2 = np.hamming(samplesPerFrame2)
      #print len(framedSignal1)
      #print len(data1), len(data2)
      data1 = np.array(data1)
      data2 = np.array(data2)
      # w1, w2 contain fft of each sound file
      # freqs1, freqs2 contain DFT sample frequencies
      w1 = np.fft.fft(data1)
      w2 = np.fft.fft(data2)
      #print len(w1), len(w2)
      freqs1 = np.fft.fftfreq(len(w1))
      freqs2 = np.fft.fftfreq(len(w2))
      # compare the two ffts and frequency spectrums, with the smaller file
      # driving the comparison
      if len(w1) < len(w2):
        compare(w1, w2, freqs1, freqs2)
      else:
        compare(w2, w1, freqs2, freqs1)
    except (wave.Error):
      sys.stderr.write("ERROR: Improper command line use.  Both files must be WAVE type.")
      exit(-1) 
 
# Compare two sets of FFT and corresponding frequencies
# Look at the strongest FFT values,
#  get the frequencies corresponding to those values
#  check if those frequencies are a subset of the frequencies from
#  the other audio file
# The shorter file drives this 
def compare(w1, w2, f1, f2):
  sortedFFT = np.sort(w1, kind='mergesort')
  topFFT = sortedFFT[len(sortedFFT) - 20:]
  topFFTindices = []
  topFreqs = []
  for val in topFFT:
    topFFTindices.append(np.where(w1==val)[0][0])
  for i in topFFTindices:
    topFreqs.append(f1[i])
  setFreqs = set(topFreqs)
  if setFreqs.issubset(f2):
    print "MATCH"
  else:
    print "NO MATCH"

def exit(val):
  return val
 
if __name__ == '__main__':
  if len(sys.argv) != 3:
    sys.stderr.write('Error: Proper command line usage is "./p4500 <pathname> <pathname>"\n')
    exit(-1)
  else:
    main(sys.argv[1], sys.argv[2])
