import sys, wave, struct, math, subprocess
import numpy as np


LAME = '/course/cs4500f13/bin/lame'

try:
  command = [LAME, 'sine2.mp3', '/tmp/sound.wav']
  process = subprocess.check_output(command, shell=False)
  print process
except (subprocess.CalledProcessError):
  sys.stderr.write('ERROR: Improper file type.')
  sys.stderr.write(' Both files must be WAVE or MP3.\n')
  sys.exit(-1)
