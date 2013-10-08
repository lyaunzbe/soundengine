import sys,os,scipy

if __name__ == '__main__':
  if len(sys.argv) != 3:
    print 'Error', sys.argv
  else:
    print 'OK', sys.argv[1], sys.argv[2]
