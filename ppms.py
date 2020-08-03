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
#       https://www.wtfsystems.net/
#  See LICENSE.md for copyright information.
#
#  See README.md for usage information.
#
#  Requires a MIDI input device.
#  Virtual one should work as long as rtmidi can see the port.
#
##########################################################

import sys, time, json, argparse, importlib
from pydoc import locate

import numpy as np
import sounddevice as sd

import rtmidi
from rtmidi.midiutil import open_midiinput

from mod.osc import oscillator
from mod.patch import patchboard

##########################################################
#  Function to return a map of the default settings
##########################################################
def create_default_settings():
    return {
        'master_volume': 50,
        'sample_rate': 44100,
        'note_on': 144,
        'note_off': 128,

        #  List modules to load
        #  Patchboard processes these in order
        'modules': [ 'mod.test' ],

        #  MIDI bindings
        #  Format:  binding_name, midi[0], midi[1]
        'bindings': [
            #  Default bindings
            [ 'master_volume', 176, 29 ],

            #  Module bindings
            #  Binding names should have the format class_name.member_name
            [ 'test_module.set_a_value', 176, 118 ]
        ],

        #  For saving module data
        'module_data': []
    }
##########################################################

##########################################################
#  Function to load modules into patchboard
##########################################################
def load_ppms_modules():
    global settings, patches
    patches.clear_modules()

    #  Take modules listed in settings and load into the patchboard
    for load_module in settings['modules']:
        mod = importlib.import_module(load_module)
        #print(mod.__name__)
        #  Find the class name, should be the only non-private member
        for member_name in dir(mod):
            if member_name.__contains__("__") == False:
                patches.add_module(locate(mod.__name__ + "." + member_name))
                #print(mod.__name__ + "." + member_name)

    #  Now load data for the modules
    for module_data in settings['module_data']:
        mod = module_data[0].split(".", 1)
        getattr(patches.get_module(mod[0]), mod[1])(patches.get_module(mod[0]), module_data[1])

    print("Modules loaded!")
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
        if message[0] == settings['note_on']:
            temp_signal = settings['master_volume'] * message[2] * patches.patch(osc.sawtooth(message[1]))
            audio_signal = np.add(audio_signal, np.array(temp_signal, dtype=np.int16))
            self.__note_map.update({message[1]: temp_signal})
            return

        #  ༼つ ◕_◕ ༽つ  Play triangle note
        if message[0] == settings['note_on'] + 1:
            temp_signal = settings['master_volume'] * message[2] * patches.patch(osc.triangle(message[1]))
            audio_signal = np.add(audio_signal, np.array(temp_signal, dtype=np.int16))
            self.__note_map.update({message[1]: temp_signal})
            return

        #  ༼つ ◕_◕ ༽つ  Play square note
        if message[0] == settings['note_on'] + 2:
            temp_signal = settings['master_volume'] * message[2] * patches.patch(osc.square(message[1]))
            audio_signal = np.add(audio_signal, np.array(temp_signal, dtype=np.int16))
            self.__note_map.update({message[1]: temp_signal})
            return

        #  ༼つ ◕_◕ ༽つ  Play sine note
        if message[0] == settings['note_on'] + 3:
            temp_signal = settings['master_volume'] * message[2] * patches.patch(osc.sine(message[1]))
            audio_signal = np.add(audio_signal, np.array(temp_signal, dtype=np.int16))
            self.__note_map.update({message[1]: temp_signal})
            return

        #  ༼つ ◕_◕ ༽つ  Stop note
        if message[0] >= settings['note_off'] and message[0] <= settings['note_off'] + 3:
            temp_signal = self.__note_map.get(message[1])
            audio_signal = np.subtract(audio_signal, np.array(temp_signal, dtype=np.int16))
            del self.__note_map[message[1]]
            return

        #  (☞ﾟヮﾟ)☞  Check bindings
        for bindings in settings['bindings']:
            if(message[0] >= bindings[1] and message[0] <= bindings[1] + 3
            and message[1] == bindings[2]):
                #  Adjust master volume
                if(bindings[0] == "master_volume"):
                    settings['master_volume'] = message[2]
                    return
                #elif
                    #return
                #  Find the loaded module and process its control
                else:
                    mod = bindings[0].split(".", 1)
                    getattr(patches.get_module(mod[0]), mod[1])(patches.get_module(mod[0]), message[2])
                    return

##########################################################
#  \END/ MIDI Input handler         ( ຈ ﹏ ຈ )
##########################################################

##########################################################
#  Main program                     ԅ║ ⁰ ۝ ⁰ ║┐
##########################################################
#  Parse arguments
parser = argparse.ArgumentParser(description="Play some notes.")
parser.add_argument("-p", "--port", metavar="N", type=int, help="MIDI Port number to connect to.")
parser.add_argument("--defaults", dest="defaults", action="store_true", help="Generate default settings.json file and exit.")
parser.set_defaults(defaults=False)
args = parser.parse_args()

print()

#  If --defaults was passed, create default settings.json file then exit.
if(args.defaults):
    settings = create_default_settings()
    try:
        with open("settings.json", "w") as json_file:
            json.dump(settings, json_file, indent=4)
            print("Default settings.json created.  Exiting...")
    except IOError:
        print("Error creating settings.json!  Exiting...")
    sys.exit(0)

#  Try loading settings
try:
    with open("settings.json", "r") as json_file:
        settings = json.load(json_file)
#  Otherwise create default settings
except IOError:
    print("Settings not found, using defaults...")
    settings = create_default_settings()

#  Make sure settings were created
if settings is None:
    print("Error creating settings!  Exiting...")
    sys.exit()
#print(settings)

#  Connect to MIDI input port.  Will prompt if not passed.
try:
    midiin, port_name = open_midiinput(args.port)
except (EOFError, KeyboardInterrupt):
    print("Error opening MIDI port!  Exiting...")
    sys.exit()

#  Initialize synth objects
osc = oscillator(settings['sample_rate'])
patches = patchboard()
load_ppms_modules()

#  Index for audio output stream
frame_index = 0
#  The output data
audio_signal = np.zeros(shape=(settings['sample_rate']), dtype=np.int16)

#  Set MIDI callback
midiin.set_callback(midi_input_handler(port_name))

running = True

#  Play sounds while running
try:
    with sd.OutputStream(callback=audio_callback, channels=1, dtype=np.int16,
                         blocksize=int(settings['sample_rate'] / 30), samplerate=settings['sample_rate']):
        print("PPMS loaded!  Press Control-C to exit.")
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
        #  First update the module save data
        settings['module_data'] = patches.save_data()
        with open("settings.json", "w") as json_file:
            json.dump(settings, json_file, indent=4)
            print("Settings saved!")
    except IOError:
        print("Error saving settings!")
    print("PPMS unloaded!")
    print()

#  ( ⌐■-■)
#  ( ⌐■-■)>⌐■-■
#  EOF
