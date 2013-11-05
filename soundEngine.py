"""
soundEngine.py - source code for CS4500 semester project
Ben Lyaunzon
Rory Sawyer
Alec Schwartz
Eduardo Romeiro
"""


# TODO: fix MFCC/filterbank.  Properly compare values

import sys, wave, struct, math, subprocess
import numpy as np
from scipy.fftpack import dct

# Path to LAME executable in the CS4500 course directory
LAME = '/course/cs4500f13/bin/lame'


def main(file1, file2):
  sound1 = openFile(file1)
  sound2 = openFile(file2)
  getFileMetadata(sound1, sound2)


# Given a file path, try to read the file using the wave module.
# If that fails, try converting the file using the provided LAME executable
# If THAT fails, then the file is neither an MP3 file nor a WAVE file, and
# an error should be thrown
def openFile(fileName):
  # Try opening the file using the wave module
  try:
    sound = wave.open(fileName, 'r')
  # If the wave module cannot open the file, try converting to WAVE using
  # the provided LAME executable
  except (wave.Error):
    try:
      command = [LAME, fileName, '/tmp/sound.wav']
      process = subprocess.check_call(command)
    except (subprocess.CalledProcessError):
      sys.stderr.write('ERROR: Improper file type.')
      sys.stderr.write(' Both files must be WAVE or MP3.\n')
      sys.exit(-1)
    try:
      sound = wave.open('/tmp/sound.wav', 'r')
    except (wave.Error):
      sys.stderr.write('ERROR: Converted file not readable\n')
      sys.exit(-1)
  return sound
  

def getFileMetadata(sound1, sound2):
  # Get the total number of samples from the file
  size1 = sound1.getnframes()
  size2 = sound2.getnframes()
  # read number of frames of size n
  data1 = sound1.readframes(size1)
  data2 = sound2.readframes(size2)
  #instantiate some framerates
  frate1 = sound1.getframerate()
  frate2 = sound2.getframerate()
  # Close audio files 
  sound1.close()
  sound2.close()
  # Unpack strings into an array of values
  data1 = struct.unpack('{n}h'.format(n=len(data1)/2), data1)
  data2 = struct.unpack('{n}h'.format(n=len(data2)/2), data2)
  # Size of frame in samples. 30 ms frame size
  samplesPerFrame1 = 0.03*frate1
  samplesPerFrame2 = 0.03*frate2
  framedSignal1 = frameSignal(data1, samplesPerFrame1)
  framedSignal2 = frameSignal(data2, samplesPerFrame2)
  #Calculate FFT values from framed signals
  # Setup hamming window 
  hammingWindow1 = np.hamming(samplesPerFrame1)
  hammingWindow2 = np.hamming(samplesPerFrame2)
  # Apply the hamming window to each signal
  hammedSignal1 = applyHammingWindow(framedSignal1, hammingWindow1)
  hammedSignal2 = applyHammingWindow(framedSignal2, hammingWindow2)
  # Get the Fourier Transform and power spectrum of each signal
  ffts1, powerSpectrum1 = getFFTandPower(hammedSignal1)
  ffts2, powerSpectrum2 = getFFTandPower(hammedSignal2)
  # Get the mel filterbanks for each power spectrum
  melFilterBank1 = filterbank(20, len(powerSpectrum1[0]), frate1)
  melFilterBank2 = filterbank(20, len(powerSpectrum2[0]), frate2)
  # Apply the mel filterbank
  filteredSpectrum1 = applyMelFilterBank(powerSpectrum1, melFilterBank1)
  filteredSpectrum2 = applyMelFilterBank(powerSpectrum2, melFilterBank2)
  # Apply a discrete cosine transform
  mfcc1 = applyDCT(filteredSpectrum1, 12);
  mfcc2 = applyDCT(filteredSpectrum2, 12);
  # Apply filter to power spectrums to create filtered spectrums
  #compareEuclid(ffts1, ffts2)
  #compareEuclid(powerSpectrum1, powerSpectrum2)
  #frameFrequencies1 = np.fft.fftfreq(int(samplesPerFrame1))
  #frameFrequencies2 = np.fft.fftfreq(int(samplesPerFrame2))
  #compare(ffts1[0], ffts2[0], frameFrequencies1, frameFrequencies2)

# Given a power spectrum and a mel filterbank, apply the mel filter bank and
# then return the log of the result
def applyMelFilterBank(ps, fb):
  filteredSpectrum = []
  for x in xrange(0, len(ps)):
    filteredSpectrum.append(np.dot(fb, ps[x]))
  return np.log10(filteredSpectrum)

# Given a filtered spectrum and a number of cepstrum, applies the
# DCT to the filtered spectrum, but only keeps num amount of results.
def applyDCT(fs, num):
  mfcc = []
  for x in xrange(0, len(fs)):
    mfcc.append(dct(fs[x][4:], norm='ortho')[:num])
  return mfcc 
 
# Given a signal and number of samples per frame, break up the signal
# into separate frames, with a quarter of each frame overlapping with
# adjacent frames
def frameSignal(signal, samplesPerFrame):
  i = 0
  # We want to overlap each frame with a quarter of the frame size
  overlap = samplesPerFrame * 0.25
  framedSignal = []
  length = len(signal)
  while i < length:
    framedSignal.append(signal[i:int(i + samplesPerFrame)])
    i = int(i + samplesPerFrame - overlap)
  return framedSignal

# Compute the Fourier transform and power spectrum of a given framed signal
def getFFTandPower(signal):
  fftValues, powerValues = [], []
  for frame in signal:
    if (len(frame) == 0): break
    fft = np.fft.fft(frame)
    power = abs(fft) ** 2
    fftValues.append(fft)
    powerValues.append(power)
  return (fftValues, powerValues)

# For each frame in each signal, apply the hamming window
# If the frame size is less than the hamming window, pad the frame with zeros
def applyHammingWindow(signal, hammingWindow):
  result = []
  for frame in signal:
    if len(frame) < len(hammingWindow):
      frame = list(frame)
      frame[len(frame):len(hammingWindow)] = [0] * (len(hammingWindow) - len(frame))
      frame = tuple(frame)
    result.append(frame * hammingWindow)
  return result

# Computer the Mel-Frequency filterbank.  Once that is done, it can be
# applied to each frame to get the Mel-Frequency Cepstral Coefficients
# of each frame
def filterbank(nfilt=20,nfft=512,samplerate=44100,lfreq=0,hfreq=None):
  hfreq = hfreq or (samplerate/2)
  
  lmel = freqToMel(lfreq)
  hmel = freqToMel(hfreq)
  melpts = np.linspace(lmel, hmel, nfilt+2)
  fftbin = np.floor((nfft+1)*melToFreq(melpts)/samplerate)
  fbank = np.zeros([nfilt, nfft])

  for x in xrange(0, nfilt):
    for y in xrange(int(fftbin[x]),int(fftbin[x+1])):
      fbank[x,y] = (y - fftbin[x])/(fftbin[x+1]-fftbin[x])
    for y in xrange(int(fftbin[x+1]),int(fftbin[x+2])):
      fbank[x,y] = (fftbin[x+2]-y)/(fftbin[x+2]-fftbin[x+1])
  return fbank

# Convert the given frequency to its mel-scale equivalent
def freqToMel(freq):
  return 2595 * np.log10(1+freq/700.0)

# Convert a value on the mel-scale to its equivalent frequency
def melToFreq(mel):
  return 700 * (10**(mel / 2595.0 - 1))

# Given two sets of MFCC values, compute the euclidean distances
# between each signal frame and declare a match or not
def compareDistances(signal1, signal2):
  distances = compareEuclid(signal1, signal2)
  print distances
  if sum(distances) < 100000:
    print 'MATCH'
  else:
    print 'NO MATCH'
  sys.exit(0)

# Input: two two-dimensional arrays of equal length
# Compute the euclidean distance between each sub-array
def compareEuclid(ray1, ray2):
  result = []
  if len(ray1) != len(ray2):
    return -1
  for i in range(len(ray1)):
    result.append(eDist(ray1[i], ray2[i]))
  print result

# Compute the euclidean distance between two arrays
# If the lists are of unequal length, compute the euclidean distance
# between only the first n elements, where n is the length of the shorter
# array
def eDist(vec1, vec2):
  result = 0
  length1 = len(vec1)
  length2 = len(vec2)
  if length1 > length2:
    for i in range(len(vec2)):
      dist = (vec1[i] - vec2[i]) ** 2
      result = result + dist
  else:
    for i in range(len(vec1)):
      dist = (vec1[i] - vec2[i]) ** 2
      result = result + dist
  return result

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
  sys.exit(0)

if __name__ == '__main__':
  if len(sys.argv) != 5:
    sys.stderr.write('ERROR: Proper command line usage is')
    sys.stderr.write(' "./p4500 -f <pathname> -f <pathname>"\n')
    sys.exit(-1)
  else:
    if sys.argv[1] != '-f' or sys.argv[3] != '-f':
      sys.stderr.write('ERROR: Proper command line usage is')
      sys.stderr.write(' "./p4500 -f <pathname> -f <pathname>"\n')
      sys.exit(-1)
    else:
      main(sys.argv[2], sys.argv[4])
