### Python Polyphonic MIDI Synthesizer

[*Python3*](https://www.python.org/) script that simulates a synthesizer.

When a key is pressed, a sample is generated then added to the output stream.  It is then stored in a reference map.

When releasing a key, the sample is retrieved from the reference map and removed from the output stream.

Requires the following packages to be installed:
- [numpy](https://numpy.org/)
- [scipy](https://www.scipy.org/)
- [sounddevice](https://pypi.org/project/sounddevice/)
- [rtmidi](https://pypi.org/project/python-rtmidi/)
