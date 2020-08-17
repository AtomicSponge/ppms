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
#
#  See LICENSE.md for copyright information.
#  See README.md for usage information.
#
##########################################################

import sys, time, json, argparse, importlib, inspect

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
        'sample_rate': 44100.0,
        'impact_weight': 20000,
        'preset_folder': "presets",

        #  Key bindings
        'note_on': 144,
        'note_off': 128,
        'preset': 192,

        #  List modules to load
        #  Patchboard processes these in order
        'modules': [ 'mod.test' ],

        #  MIDI control bindings
        #  Format:  binding_name, midi[0], midi[1]
        'bindings': [
            #  Default bindings
            [ 'master_volume', 176, 24 ],

            #  Module bindings
            #  Binding names should have the format class_name.member_name
            [ 'test_module.set_a_value', 176, 20 ]
        ],

        #  For storing preset files
        'presets': [],

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
        #  Find the class and add to patches
        for member_name, obj in inspect.getmembers(mod):
            if inspect.isclass(obj):
                patches.add_module(obj)
                print("Loaded: ", mod.__name__)
    print("Modules loaded!")
##########################################################

##########################################################
#  Function to load module data
##########################################################
def load_module_data():
    global settings, patches

    for module_data in settings['module_data']:
        mod = module_data[0].split(".", 1)
        getattr(patches.get_module(mod[0]), mod[1])(patches.get_module(mod[0]), module_data[1])
##########################################################

##########################################################
#  Audio callback function
##########################################################
def audio_callback(outdata, frames, time, status):
    global settings, audio_signal, frame_index
    outdata[:] = np.reshape(audio_signal[frame_index:frame_index + frames], (frames, 1))
    frame_index += frames
    if(frame_index > settings['sample_rate'] - frames): frame_index = 0
##########################################################

##########################################################
#  \START/ MIDI Input handler   ♪ヽ( ⌒o⌒)人(⌒-⌒ )v ♪
##########################################################
class midi_input_handler(object):
    def __init__(self, port, weight, noimpact, noupdate, verbose):
        self.__port = port
        self.__weight = weight
        self.__noimpact = noimpact
        self.__noupdate = noupdate
        self.__verbose = verbose
        self.__wallclock = time.time()
        self.__note_map = dict()

    #  ᕕ(⌐■_■)ᕗ ♪♬  MIDI Input handler callback
    def __call__(self, event, data=None):
        global settings, audio_signal, osc, patches

        message, deltatime = event
        self.__wallclock += deltatime
        if(self.__verbose): print("[%s] @%0.6f %r" % (self.__port, self.__wallclock, message))

        if(self.__noimpact): impact = 40 / self.__weight
        else: impact = message[2] / self.__weight

        #  ༼つ ◕_◕ ༽つ  Play saw note
        if message[0] == settings['note_on']:
            temp_signal = settings['master_volume'] * impact * patches.patch(osc.sawtooth(message[1]))
            audio_signal = np.add(audio_signal, np.array(temp_signal, dtype=np.float32))
            self.__note_map.update({message[1]: [ temp_signal, impact, "sawtooth" ] })
            return

        #  ༼つ ◕_◕ ༽つ  Play triangle note
        if message[0] == settings['note_on'] + 1:
            temp_signal = settings['master_volume'] * impact * patches.patch(osc.triangle(message[1]))
            audio_signal = np.add(audio_signal, np.array(temp_signal, dtype=np.float32))
            self.__note_map.update({message[1]: [ temp_signal, impact, "triangle" ] })
            return

        #  ༼つ ◕_◕ ༽つ  Play square note
        if message[0] == settings['note_on'] + 2:
            temp_signal = settings['master_volume'] * impact * patches.patch(osc.square(message[1]))
            audio_signal = np.add(audio_signal, np.array(temp_signal, dtype=np.float32))
            self.__note_map.update({message[1]: [ temp_signal, impact, "square" ] })
            return

        #  ༼つ ◕_◕ ༽つ  Play sine note
        if message[0] == settings['note_on'] + 3:
            temp_signal = settings['master_volume'] * impact * patches.patch(osc.sine(message[1]))
            audio_signal = np.add(audio_signal, np.array(temp_signal, dtype=np.float32))
            self.__note_map.update({message[1]: [ temp_signal, impact, "sine" ] })
            return

        #  ༼つ ◕_◕ ༽つ  Stop note
        if message[0] >= settings['note_off'] and message[0] <= settings['note_off'] + 3:
            temp_signal = self.__note_map.get(message[1])[0]
            audio_signal = np.subtract(audio_signal, np.array(temp_signal, dtype=np.float32))
            del self.__note_map[message[1]]
            return

        #  ᕕ( ᐛ )ᕗ  Load a preset
        if message[0] == settings['preset']:
            if message[1] < len(settings['presets']):
                #  Try loading preset
                try:
                    with open(settings['preset_folder'] + "/" + settings['presets'][message[1]], "r") as json_file:
                        settings['module_data'] = json.load(json_file)
                #  If not found just return
                except IOError:
                    print("Error loading preset: ", settings['preset_folder'] + "/" + settings['presets'][message[1]])
                    return
                #  Now make the preset active
                load_module_data()
                print(f"Preset {settings['preset_folder']}/{settings['presets'][message[1]]} loaded!")
            return

        #  (☞ﾟヮﾟ)☞  Check bindings
        for bindings in settings['bindings']:
            if(message[0] >= bindings[1] and message[0] <= bindings[1] + 3
            and message[1] == bindings[2]):
                #  Adjust master volume
                if(bindings[0] == "master_volume"):
                    settings['master_volume'] = message[2]
                    break
                #elif
                    #break
                #  Find the loaded module and process its control
                else:
                    mod = bindings[0].split(".", 1)
                    getattr(patches.get_module(mod[0]), mod[1])(patches.get_module(mod[0]), message[2])
                    break

        if(self.__noupdate): return
        #  ╚═〳 ͡ᵔ ▃ ͡ᵔ 〵═╝  Recalculate note map
        #  After a parameter update, reprocess all playing notes
        for note in self.__note_map:
            data = self.__note_map.get(note)
            audio_signal = np.subtract(audio_signal, np.array(data[0], dtype=np.float32))
            del self.__note_map[note]
            #  Re-create the note with the new parameters
            if(data[2] == "sawtooth"):
                temp_signal = settings['master_volume'] * data[1] * patches.patch(osc.sawtooth(note))
            elif(data[2] == "triangle"):
                temp_signal = settings['master_volume'] * data[1] * patches.patch(osc.triangle(note))
            elif(data[2] == "square"):
                temp_signal = settings['master_volume'] * data[1] * patches.patch(osc.square(note))
            elif(data[2] == "sine"):
                temp_signal = settings['master_volume'] * data[1] * patches.patch(osc.sine(note))
            else: continue  #  Not valid, don't update note map
            audio_signal = np.add(audio_signal, np.array(temp_signal, dtype=np.float32))
            self.__note_map.update({note: [ temp_signal, data[1], data[2] ] })
##########################################################
#  \END/ MIDI Input handler         ( ຈ ﹏ ຈ )
##########################################################

##########################################################
#  Main program                     ԅ║ ⁰ ۝ ⁰ ║┐
##########################################################
print("•" * 60)
print("Python Polyphonic MIDI Synthesizer")
print("༼つ ◕_◕ ༽つ " * 5)
print("•" * 60)
print()

#  Parse arguments
parser = argparse.ArgumentParser(description="Play some notes.")
parser.add_argument(
    "-p", "--port", dest="port", default=None,
    metavar="#", type=int, help="MIDI port number to connect to."
)
parser.add_argument(
    "-v", "--verbose", dest="verbose", default=False,
    action="store_true", help="Display MIDI messages."
)
parser.add_argument(
    "-c", "--config", dest="config", default="settings.json",
    metavar="file", type=str, help="Config file to load. Default: %(default)s"
)
parser.add_argument(
    "--noimpact", dest="noimpact", default=False,
    action="store_true", help="Disable keyboard impact."
)
parser.add_argument(
    "--noupdate", dest="noupdate", default=False,
    action="store_true", help="Disable note reprocessing after parameter update."
)
parser.add_argument(
    "--defaults", dest="set_defaults", default=False,
    action="store_true", help="Generate default settings.json file and exit."
)
args = parser.parse_args()

#  If --defaults was passed, create default settings.json file then exit.
if(args.set_defaults):
    settings = create_default_settings()
    try:
        with open("settings.json", "w") as json_file:
            json.dump(settings, json_file, indent=4)
            print("Default settings.json created.  Exiting...")
            sys.exit(0)
    except IOError:
        print("Error creating settings.json!  Exiting...")
        sys.exit(1)

#  Try loading settings
try:
    with open(args.config, "r") as json_file:
        settings = json.load(json_file)
        print("Settings loaded!")
#  Otherwise create default settings
except IOError:
    print("Settings not found, using defaults...")
    settings = create_default_settings()

#  Make sure settings were created
if settings is None:
    print("Error creating settings!  Exiting...")
    sys.exit(1)

#  Connect to MIDI input port.  Will prompt if not passed.
try:
    midiin, port_name = open_midiinput(args.port)
except KeyboardInterrupt:
    print("Exiting...")
    print()
    sys.exit(0)
except EOFError:
    print("Error opening MIDI port!  Exiting...")
    sys.exit(1)

#  Initialize synth objects
osc = oscillator(settings['sample_rate'])
patches = patchboard()
load_ppms_modules()
load_module_data()

#  Index for audio output stream
frame_index = 0
#  The output data
audio_signal = np.zeros(shape=(int(settings['sample_rate'])), dtype=np.float32)

#  Set MIDI callback
midiin.set_callback(
    midi_input_handler(port_name, settings['impact_weight'],
        args.noimpact, args.noupdate, args.verbose)
)

running = True

#  Play sounds while running
try:
    with sd.OutputStream(
        callback=audio_callback, channels=1, dtype=np.float32,
        blocksize=int(settings['sample_rate'] / 30), samplerate=settings['sample_rate']
    ):
        print()
        print("PPMS loaded!  Press Control-C to exit.")
        while running:  #  Loop until Ctrl+C break
            time.sleep(1)
except Exception as e:
    print(type(e).__name__ + ': ' + str(e))
    print("Exiting...")
    print()
except KeyboardInterrupt:
    print("Exiting...")
    print()
finally:
    #  Clean up
    midiin.close_port()
    del midiin
    #  Save settings
    try:
        #  First update the module save data
        settings['module_data'] = patches.save_data()
        with open(args.config, "w") as json_file:
            json.dump(settings, json_file, indent=4)
            print("Settings saved!")
    except IOError:
        print("Error saving settings!")
    print("PPMS unloaded!")
    print("•" * 60)

#  ( ⌐■-■)
#  ( ⌐■-■)>⌐■-■
#  EOF
