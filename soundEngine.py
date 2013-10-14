import sys, wave, struct
import numpy as np
 
def main(file1, file2):
    # If either file1 or file2 aren't WAVE, wave.open() throws an error
    try:
        sound1 = wave.open(file1, 'r')
        sound2 = wave.open(file2, 'r')
        size1 = sound1.getnframes()
        size2 = sound2.getnframes()
        data1 = sound1.readframes(size1)
        data2 = sound2.readframes(size2)
        sound1.close()
        sound2.close()
        data1 = struct.unpack('{n}h'.format(n=len(data1)/2), data1)
        data2 = struct.unpack('{n}h'.format(n=len(data2)/2), data2)
        data1 = np.array(data1)
        data2 = np.array(data2)
        # w1, w2 contain fft of each sound file
        # freqs1, freqs2 contain DFT sample frequencies
        w1 = np.fft.fft(data1)
        w2 = np.fft.fft(data2)
        freqs1 = np.fft.fftfreq(len(w1))
        freqs2 = np.fft.fftfreq(len(w2))
        x = set(w1)
        y = set(w2)
        matched = 0
        if len(w1) < len(w2):
          print len(w1), len(w2)
          compare(w1, w2, freqs1, freqs2)
        else:
          compare(w2, w1, freqs2, freqs1)
    except (wave.Error):
        print "Improper command line use.  Both files must be WAVE type."
 
 
 
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
 
 
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Error: Proper command line usage is "./p4500 <pathname> <pathname>"\n'
    else:
        main(sys.argv[1], sys.argv[2])