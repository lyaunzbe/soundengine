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
      command = [LAME, fileName, ' /tmp/sound.wav']
      process = subprocess.check_call(command)
    except (subprocess.CalledProcessError):
      sys.stderr.write('ERROR: Improper file type.')
      sys.stderr.write('Both files must be WAVE or MP3.\n')
      sys.exit(-1)
    try:
      sound = wave.open('/tmp/sound.wav', 'r')
    except (wave.Error):
      sys.stderr.write('ERROR: Converted file not readable\n')
      sys.exit(-1)
  return sound
  

def getFileMetadata(sound1, sound2):
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
  # Size of frame in samples. 30 ms frame size
  samplesPerFrame1 = 0.03*frate1
  samplesPerFrame2 = 0.03*frate2
  framedSignal1 = []
  framedSignal2 = []
  i = 0
  # We want a quarter of the frame size to overlap for each signal
  overlap1 = samplesPerFrame1 * 0.25
  overlap2 = samplesPerFrame2 * 0.25
  # Frame signals
  while i < len(data1):
    framedSignal1.append(data1[i:int(i + samplesPerFrame1)])
    i = int(i + samplesPerFrame1 - overlap1)
  j = 0
  while j < len(data1):
    framedSignal2.append(data2[j:int(j + samplesPerFrame2)])
    j = int(j + samplesPerFrame2 - overlap2)
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
  #compareEuclid(ffts1, ffts2)
  #compareEuclid(powerSpectrum1, powerSpectrum2)
  frameFrequencies1 = np.fft.fftfreq(int(samplesPerFrame1))
  frameFrequencies2 = np.fft.fftfreq(int(samplesPerFrame2))
  compare(ffts1[0], ffts2[0], frameFrequencies1, frameFrequencies2)
  melFilterBank = filterbank(20, len(powerSpectrum1[0]), frate1)
  print np.shape(melFilterBank)
  print np.shape(powerSpectrum1[0])


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
# applied to each window to get the Mel-Frequency Cepstral Coefficients
# of each frame
def filterbank(nfilt=20,nfft=512,samplerate=44100,lfreq=0,hfreq=None):
  hfreq = hfreq or (samplerate/2)
  
  lmel = freqToMel(lfreq)
  hmel = freqToMel(hfreq)
  melpts = np.linspace(lmel, hmel, nfilt+2)
  #print melpts
  fftbin = np.floor((nfft+1)*melToFreq(melpts)/samplerate)
  #print fftbin
  fbank = np.zeros([nfilt, nfft/2+1])

  for x in xrange(0, nfilt):
    for y in xrange(int(fftbin[x]),int(fftbin[x+1])):
      fbank[x,y] = (y - fftbin[x])/(fftbin[x+1]-fftbin[x])
    for y in xrange(int(fftbin[x+1]),int(fftbin[x+2])):
      fbank[x,y] = (fftbin[x+2]-y)/(fftbin[x+2]-fftbin[x+1])
  return fbank

# Convert 
def freqToMel(freq):
  return 2595 * np.log10(1+freq/700.0)

def melToFreq(mel):
  return 700 * (10**(mel / 2595.0 - 1))

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
def eDist(vec1, vec2):
  result = 0
  if len(vec1) != len(vec2):
    return -1
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

def exit(val):
  return val

if __name__ == '__main__':
  if len(sys.argv) != 5:
    sys.stderr.write('ERROR: Proper command line usage is "./p4500 -f <pathname> -f <pathname>"\n')
    sys.exit(-1)
  else:
    if sys.argv[1] != '-f' or sys.argv[3] != '-f':
      sys.stderr.write('ERROR: Proper command line usage is "./p4500 -f <pathname> -f <pathname>')
      sys.exit(-1)
    else:
      main(sys.argv[2], sys.argv[4])
