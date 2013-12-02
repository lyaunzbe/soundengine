"""
soundEngine.py - source code for CS4500 semester project
Ben Lyaunzon
Rory Sawyer
Alec Schwartz
Eduardo Romeiro
"""


import sys, wave, struct, math, subprocess, os
import numpy as np
from scipy.fftpack import dct

# Path to LAME executable in the CS4500 course directory
LAME = '/course/cs4500f13/bin/lame'

# TODO: Add rabin-karp on fft windows

# Main method for comparing two given files
def main(file1, file2):
  # Open the file described by the given path
  sound1 = openFile(file1)
  sound2 = openFile(file2)
  # Get the total number of samples from the file
  size1 = sound1.getnframes()
  size2 = sound2.getnframes()
  # read number of frames of size n
  data1 = sound1.readframes(size1)
  data2 = sound2.readframes(size2)
  #instantiate the framerates
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
  # Divide each signal into overlapping frames
  framedSignal1 = frameSignal(data1, samplesPerFrame1)
  framedSignal2 = frameSignal(data2, samplesPerFrame2)
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
  # Apply a discrete cosine transform to get the MFCC values for each frame
  mfcc1 = applyDCT(filteredSpectrum1, 12);
  mfcc2 = applyDCT(filteredSpectrum2, 12);
  # Compare the two sets of MFCC values
  compareDistances(mfcc1, mfcc2)

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
      command = [LAME, '--quiet', '--decode', '--mp3input', fileName, '/tmp/sound.wav']
      process = subprocess.check_call(command)
    except (subprocess.CalledProcessError):
      sys.stderr.write('ERROR: Improper file type.')
      sys.stderr.write(' Both files must be WAVE or MP3.\n')
      sys.exit(-1)
    # Once we have converted the file, open the newly formed WAVE file
    try:
      sound = wave.open('/tmp/sound.wav', 'r')
    except (wave.Error):
      sys.stderr.write('ERROR: Converted file not readable\n')
      sys.exit(-1)
  return sound


# Given a power spectrum and a mel filterbank, apply the mel filterbank and
# then return the log of the result
def applyMelFilterBank(powerSpectrum, filterBank):
  filteredSpectrum = []
  for x in xrange(0, len(powerSpectrum)):
    filteredSpectrum.append(np.dot(filterBank, powerSpectrum[x]))
  return np.log10(filteredSpectrum)

# Given a filtered spectrum and a number of cepstrum, applies the
# DCT to the filtered spectrum, but only keeps num amount of results.
def applyDCT(filteredSpectrum, numCepstrum):
  mfcc = []
  for x in xrange(0, len(filteredSpectrum)):
    mfcc.append(dct(filteredSpectrum[x][4:], norm='ortho')[:numCepstrum])
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
  hamWindowLen = len(hammingWindow)
  for frame in signal:
    frameLength = len(frame)
    if len(frame) < hamWindowLen:
      frame = list(frame)
      frame[frameLength:hamWindowLen] = [0] * (hamWindowLen - frameLength)
      frame = tuple(frame)
    result.append(frame * hammingWindow)
  return result

# Compute the Mel-Frequency filterbank.  This can be applied to each frame
# to get the Mel-Frequency Cepstral Coefficients of each frame
def filterbank(nfilt, nfft, samplerate):
  # The highest recorded frequency, calculated from the sample rate
  hfreq = samplerate/2
  # The lowest recorded frequency
  lfreq = 0
  
  # Convert the lower and upper frequency values to the mel scale
  lmel = freqToMel(lfreq)
  hmel = freqToMel(hfreq)

  melpts = np.linspace(lmel, hmel, nfilt+2)
  fftbin = np.floor((nfft+1)*melToFreq(melpts)/samplerate)
  fbank = np.zeros([nfilt, nfft])

  # Fill the two-dimentional filterbank according to the FFT bins
  for x in xrange(0, nfilt):
    for y in xrange(int(fftbin[x]), int(fftbin[x + 1])):
      fbank[x, y] = (y - fftbin[x])/(fftbin[x + 1] - fftbin[x])
    for y in xrange(int(fftbin[x + 1]), int(fftbin[x + 2])):
      fbank[x, y] = (fftbin[x + 2] - y)/(fftbin[x + 2] - fftbin[x + 1])
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
  sigLen1 = len(signal1)
  sigLen2 = len(signal2)
  # Compare the number of close frames to the shorter signal
  if sigLen1 > sigLen2:
    prop = float(len(distances))/float(sigLen2)
  else:
    prop = float(len(distances))/float(sigLen1)
  if prop > 0.15:
    print 'MATCH'
  else:
    print 'NO MATCH'
  # Delete the temporary WAVE file if necessary
  try:
    subprocess.check_call('rm /tmp/sound.wav')
  except OSError:
    pass
  #sys.exit(0)

# Input: two two-dimensional arrays
# Compute the euclidean distance between each sub-array
def compareEuclid(ray1, ray2):
  result = []
  length1 = len(ray1)
  length2 = len(ray2)
  # If the arrays are of unequal length, then compare all elements of
  # the shorter array to the corresponding elements of the longer array
  if length1 > length2:
    for i in range(len(ray2)):
      distance = eDist(ray1[i], ray2[i])
      if distance < 7:
        result.append(distance)
  else:
    for i in range(len(ray1)):
      distance = eDist(ray1[i], ray2[i])
      if distance < 7:
        result.append(distance)
  return result

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


# If we are calling this program directly, then check the command-line
# arguments and start the comparison
if __name__ == '__main__':
  if len(sys.argv) != 5:
    sys.stderr.write('ERROR: Proper command line usage is one of:')
    sys.stderr.write(' "./p4500 -f <pathname> -f <pathname>"\n')
    sys.stderr.write(' "./p4500 -f <pathname> -d <pathname>"\n')
    sys.stderr.write(' "./p4500 -d <pathname> -f <pathname>"\n')
    sys.stderr.write(' "./p4500 -d <pathname> -d <pathname>"\n')
    sys.exit(-1)
  else:
    if not ((sys.argv[1] == '-f' or sys.argv[1] == '-d') and (sys.argv[3] == '-f' sys.argv[3] == '-d')):
      sys.stderr.write('ERROR: Proper command line usage is one of:\n')
      sys.stderr.write(' "./p4500 -f <pathname> -f <pathname>"\n')
      sys.stderr.write(' "./p4500 -f <pathname> -d <pathname>"\n')
      sys.stderr.write(' "./p4500 -d <pathname> -f <pathname>"\n')
      sys.stderr.write(' "./p4500 -d <pathname> -d <pathname>"\n')
      sys.exit(-1)
    else:
      # Run through the different input cases.
      # If both pathnames are just files, run main then exit
      if sys.argv[1] == '-f' and sys.argv[3] == '-f':
        main(sys.argv[2], sys.argv[4])
        sys.exit(0)
      # If the second pathname is a directory, then run main for all files in
      # that directory against the other file provided
      elif sys.argv[1] == '-f' and sys.argv[3] == '-d':
        try:
          files = os.listdir(sys.argv[4])
        except OSError:
          # Throw an error if the pathname given after -d is not a directory
          sys.stderr.write('ERROR: pathname after -d flag must be directory')
          sys.exit(-1)
        for song in files:
          main(sys.argv[2], sys.argv[4] + song)
        sys.exit(0)
      # If the first pathname is a directory, then run main for all files in
      # that directory against the other file provided
      elif sys.argv[1] == '-d' and sys.argv[3] == '-f':
        try:
          files = os.listdir(sys.argv[2])
        except OSError:
          sys.stderr.write('ERROR: pathname after -d flag must be directory')
          sys.exit(-1)
        for song in files:
          main(sys.argv[4], sys.argv[2] + song)
        sys.exit(0)
      # If both pathnames are directories then check each file in each
      # directory against each other.
      elif sys.argv[1] == '-d' and sys.argv[3] == '-d':
        try:
          firstDir = os.listdir(sys.argv[2])
        except OSError:
          sys.stderr.write('ERROR: pathname after -d flag must be directory')
          sys.exit(-1)
        try:
          secondDir = os.listdir(sys.argv[4])
        except OSError:
          sys.stderr.write('ERROR: pathname after -d flag must be directory')
          sys.exit(-1)
        for each in firstDir:
          for song in secondDir:
            main(sys.argv[2] + each, sys.argv[4] + song)
        sys.exit(0)


