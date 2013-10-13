import sys,os,scipy,wave, struct
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
    # need to use some other comparison method than np.any()
    # Also we need serious print statements
    if w1 is w2 or freqs1 is freqs2:
      print "MATCH: ", file1, file2, " 100%"
    elif w1 in w2 or w2 in w1:
      print "MATCH, BUT, HONESTLY, IT COULD BE ANYWHERE FROM 0 TO 100% (NON INCLUSIVE), SO TAKE FROM THAT WHAT YOU WILL"
    else:
      print "NO MATCH. JUST LIKE YOU AND EVERYBODY YOU'VE EVER DATED."
  except (wave.Error):
    print "Improper command line use.  Both files must be WAVE type."

# Takes a very long time to compare any significantly-sized audio samples.
# Perhaps we should try the divide-and-conquer approach
def compare(f1, f2, w1, w2):
  similarities = 0
  for freq in f1:
    if freq in f2:
      similarities += 1
  if similarities/len(f1) > 0.65 or similarities/len(f2) > 0.65:
    print "Greater than a 65% match in frequencies"
  fftSimilarities = 0
  for fft in w1:
    if fft in w2:
      fftSimilarities += 1
  if fftSimilarities/len(w1) > 0.65 or fftSimilarities/len(f2) > 0.65:
    print "Greater than 65% match in fft values"

if __name__ == '__main__':
  if len(sys.argv) != 3:
    print 'Error', sys.argv
  else:
    main(sys.argv[1], sys.argv[2])

