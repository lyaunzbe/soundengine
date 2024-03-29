SOUNDENGINE README

Team:
(1) Ben Lyaunzon, lyaunzon.b@gmail.com
(2) Rory Sawyer, sawyer.r@husky.neu.edu
(3) Alec Schwartz, schwartz.c@husky.neu.edu
(4) Eduardo Romeiro, romeiro.e@husky.neu.edu

No compilation needed, simply cd to the directory containing this 
software's executable and executing a command of the following form:

    ./p4500 <pathname> <pathname>

This software is written with the Python programming langauge and 
depends on the following libraries: numpy, wave and a few minor 
standard libraries (sys, struct).

To improve on our prototype the following changes will be made:
 1) Run FFT on windowed segments instead of the whole file.
 2) Compute the Mel-frequency cepstral coefficients to extract features
    from the file to obtain an audio fingerprint.
 3) Compare those fingerprints to find any possible matches.
 4) Expand our program to handle different types of audio files.
 6) Remove any egregiously inefficient code.
