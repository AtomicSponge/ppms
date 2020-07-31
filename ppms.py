##########################################################
#
#  Python Polyphonic MIDI Synthesizer
#
##########################################################
#
#               ~~~~~~~[]=¤ԅ(ˊᗜˋ* )੭
#
#  Filename:  ppms.py
#  By:  Matthew Evans
#  See LICENSE.md for copyright information.
#
#  Reads MIDI input and plays notes.
#
##########################################################

import sys, time, json

import numpy as np
import sounddevice as sd

import rtmidi
from rtmidi.midiutil import open_midiinput

from mod.osc import oscillator
from mod.patch import patchboard

from mod.test import test_module

##########################################################
#  Function to return a map of the default settings
##########################################################
def create_default_settings():
    return {
        'master_volume': 0,
        'sample_rate': 44100,
        'key_down': 144,
        'key_up': 128
    }
##########################################################

##########################################################
#  Audio callback function
##########################################################
def audio_callback(outdata, frames, time, status):
    global settings, audio_signal, frame_index
    #print(frames, frame_index)
    outdata[:] = np.reshape(audio_signal[frame_index:frame_index + frames], (frames, 1))
    frame_index += frames
    if(frame_index > settings['sample_rate'] - frames): frame_index = 0
##########################################################

##########################################################
#  \START/ MIDI Input handler   ♪ヽ( ⌒o⌒)人(⌒-⌒ )v ♪
##########################################################
class midi_input_handler(object):
    def __init__(self, port):
        self.port = port
        self._wallclock = time.time()

        self.__note_map = dict()
    #  ᕕ(⌐■_■)ᕗ ♪♬  MIDI Input handler callback
    def __call__(self, event, data=None):
        global settings, audio_signal, osc, patches

        message, deltatime = event
        self._wallclock += deltatime
        print("[%s] @%0.6f %r" % (self.port, self._wallclock, message))

        #  ༼つ ◕_◕ ༽つ  Play saw note
        if message[0] == settings['key_down']:
            temp_signal = settings['master_volume'] * message[2] * patches.patch(osc.sawtooth(message[1]))
            audio_signal = np.add(audio_signal, np.array(temp_signal, dtype=np.int16))
            self.__note_map.update({message[1]: temp_signal})

        #  ༼つ ◕_◕ ༽つ  Play triangle note
        if message[0] == settings['key_down'] + 1:
            temp_signal = settings['master_volume'] * message[2] * patches.patch(osc.triangle(message[1]))
            audio_signal = np.add(audio_signal, np.array(temp_signal, dtype=np.int16))
            self.__note_map.update({message[1]: temp_signal})

        #  ༼つ ◕_◕ ༽つ  Play square note
        if message[0] == settings['key_down'] + 2:
            temp_signal = settings['master_volume'] * message[2] * patches.patch(osc.square(message[1]))
            audio_signal = np.add(audio_signal, np.array(temp_signal, dtype=np.int16))
            self.__note_map.update({message[1]: temp_signal})

        #  ༼つ ◕_◕ ༽つ  Play sine note
        if message[0] == settings['key_down'] + 3:
            temp_signal = settings['master_volume'] * message[2] * patches.patch(osc.sine(message[1]))
            audio_signal = np.add(audio_signal, np.array(temp_signal, dtype=np.int16))
            self.__note_map.update({message[1]: temp_signal})

        #  ༼つ ◕_◕ ༽つ  Stop note
        if message[0] >= settings['key_up'] and message[0] <= settings['key_up'] + 3:
            temp_signal = self.__note_map.get(message[1])
            audio_signal = np.subtract(audio_signal, np.array(temp_signal, dtype=np.int16))
            del self.__note_map[message[1]]

        #  (☞ﾟヮﾟ)☞  Adjust volume
        if(message[0] >= 176 and message[0] <= 179 and message[1] == 29):
            settings['master_volume'] = message[2]
##########################################################
#  \END/ MIDI Input handler         ( ຈ ﹏ ຈ )
##########################################################

##########################################################
#  Main program                     ԅ║ ⁰ ۝ ⁰ ║┐
##########################################################
#  Check if MIDI input port was passed
port = sys.argv[1] if len(sys.argv) > 1 else None

#  Try loading settings
try:
    with open("settings.json", "r") as json_file:
        settings = json.load(json_file)
#  Otherwise create default settings
except IOError:
    print("Settings not found, using defaults...")
    settings = create_default_settings()

if settings is None:
    print("Error creating settings!  Exiting...")
    sys.exit()

#  Prompt for MIDI input port if not passed
try:
    midiin, port_name = open_midiinput(port)
except (EOFError, KeyboardInterrupt):
    print("Error opening MIDI port!  Exiting...")
    sys.exit()

#  Index for audio output stream
frame_index = 0
#  The output data
audio_signal = np.zeros(shape=(settings['sample_rate']), dtype=np.int16)

#  Initialize synth objects
osc = oscillator(settings['sample_rate'])
patches = patchboard()
#  For now add patches here
patches.add_module(test_module)

#  Set MIDI callback
midiin.set_callback(midi_input_handler(port_name))

running = True
print()
print("PPMS loaded!")

#  Play sounds while running
try:
    with sd.OutputStream(callback=audio_callback, channels=1, dtype=np.int16,
                         blocksize=int(settings['sample_rate'] / 30), samplerate=settings['sample_rate']):
        while running:  #  Loop until Ctrl+C break
            time.sleep(1)
except Exception as e:
    print(type(e).__name__ + ': ' + str(e))
    print("Exiting...")
except KeyboardInterrupt:
    print("Exiting...")
finally:
    #  Clean up
    midiin.close_port()
    del midiin
    #  Save settings
    try:
        with open("settings.json", "w") as json_file:
            json.dump(settings, json_file)
    except IOError:
        print("Error saving settings!")
    print("PPMS unloaded!")
    print()

#  ( ⌐■-■)
#  ( ⌐■-■)>⌐■-■
#  EOF
