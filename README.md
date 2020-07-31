### Python Polyphonic MIDI Synthesizer

WIP

When a key is pressed, a sample is generated then added to the output stream.  It is then stored in a reference map.

When releasing a key, the sample is retrieved from the reference map and removed from the output stream.

Requires the following packages to be installed:
- numpy
- scipy
- sounddevice
- rtmidi
