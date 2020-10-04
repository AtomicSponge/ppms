##################################################################
#
#  Python Polyphonic MIDI Synthesizer
#
##################################################################
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
##################################################################

import sys, time, json, asyncio
import argparse, importlib, inspect

import numpy as np
import sounddevice as sd

import rtmidi
from rtmidi.midiutil import open_midiinput

from mod.osc import oscillator
from mod.patch import patchboard

##################################################################
#  Function to return a map of the default settings
##################################################################
def create_default_settings():
    return {
        'master_volume': 50,
        'sample_rate': 44100.0,
        'impact_weight': 20000,
        'preset_folder': "presets",

        #  Key bindings
        'note_on': 144,
        'note_off': 128,
        'preset_msg': 192,

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

##################################################################
#  Function to load modules into patchboard
##################################################################
def load_ppms_modules(settings, patches):
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

##################################################################
#  Function to load module data
##################################################################
def load_module_data(settings, patches):
    for module_data in settings['module_data']:
        mod = module_data[0].split(".", 1)
        getattr(patches.get_module(mod[0]), mod[1])(patches.get_module(mod[0]), module_data[1])

##################################################################
#  Input coro
##################################################################
async def ppms_input(settings, patches, note_map, port, noimpact, verbose):
    loop = asyncio.get_event_loop()
    event = asyncio.Event()

    ##################################################################
    #  \START/ MIDI Input handler   ♪ヽ( ⌒o⌒)人(⌒-⌒ )v ♪
    ##################################################################
    class midi_input_handler(object):
        def __init__(self, port, weight, noimpact, verbose):
            self.__port = port
            self.__weight = weight
            self.__noimpact = noimpact
            self.__verbose = verbose
            self.__wallclock = time.time()

        #  ᕕ(⌐■_■)ᕗ ♪♬  MIDI Input handler callback
        def __call__(self, event, data=None):
            message, deltatime = event
            self.__wallclock += deltatime
            if(self.__verbose): print("[%s] @%0.6f %r" % (self.__port, self.__wallclock, message))

            #  ᕕ( ᐛ )ᕗ  Load a preset
            if message[0] == settings['preset_msg']:
                if message[1] < len(settings['presets']):
                    try:
                        #  Open the preset file and load into module_data
                        with open(settings['preset_folder'] + "/" + settings['presets'][message[1]], "r") as json_file:
                            settings['module_data'] = json.load(json_file)
                            load_module_data(settings, patches)
                            print(f"Preset {settings['preset_folder']}/{settings['presets'][message[1]]} loaded!")
                    except IOError:
                        print("Error loading preset: ", settings['preset_folder'] + "/" + settings['presets'][message[1]])
                return

            if(self.__noimpact): impact = 40 / self.__weight
            else: impact = message[2] / self.__weight

            #  ༼つ ◕_◕ ༽つ  Play saw note
            if message[0] == settings['note_on']:
                note_map.update({message[1]: [ "sawtooth", impact ] })
                return

            #  ༼つ ◕_◕ ༽つ  Play triangle note
            if message[0] == settings['note_on'] + 1:
                note_map.update({message[1]: [ "triangle", impact ] })
                return

            #  ༼つ ◕_◕ ༽つ  Play square note
            if message[0] == settings['note_on'] + 2:
                note_map.update({message[1]: [ "square", impact ] })
                return

            #  ༼つ ◕_◕ ༽つ  Play sine note
            if message[0] == settings['note_on'] + 3:
                note_map.update({message[1]: [ "sine", impact ] })
                return

            #  ༼つ ◕_◕ ༽つ  Stop note
            if message[0] >= settings['note_off'] and message[0] <= settings['note_off'] + 3:
                del note_map[message[1]]
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
    ##################################################################
    #  \END/ MIDI Input handler         ( ຈ ﹏ ຈ )
    ##################################################################

    try:
        midiin, port_name = open_midiinput(port)
    except KeyboardInterrupt:
        print("Exiting...")
        sys.exit(0)
    except rtmidi.NoDevicesError:
        print("No MIDI devices available!  Exiting...")
        sys.exit(1)
    except rtmidi.SystemError:
        print("Error initializing RtMidi!  Exiting...")
        sys.exit(1)
    except EOFError:
        print("Error opening MIDI port!  Exiting...")
        sys.exit(1)

    print("Connected to: ", port_name)
    midiin.set_callback(
        midi_input_handler(port_name, settings['impact_weight'], noimpact, verbose)
    )

    try:
        await event.wait()
    except KeyboardInterrupt:
        pass
    finally:
        del midiin

##################################################################
#  Output coro
##################################################################
async def ppms_output(settings, patches, note_map, osc):
    loop = asyncio.get_event_loop()
    event = asyncio.Event()
    time_index = 0  #  Index for audio output stream

    def audio_callback(outdata, frame_size, time, status):
        nonlocal time_index, settings, osc, patches, note_map

        audio_signal = np.zeros(shape=(frame_size,1), dtype=np.float32)
        temp_note_map = note_map.copy()
        for note in temp_note_map:
            data = note_map.get(note)
            if data[0] == "sawtooth":
                audio_signal = np.add(audio_signal, (settings['master_volume'] + data[1]) * patches.patch(osc.sawtooth(note, frame_size, time_index)))
            if data[0] == "triangle":
                audio_signal = np.add(audio_signal, (settings['master_volume'] + data[1]) * patches.patch(osc.triangle(note, frame_size, time_index)))
            if data[0] == "square":
                audio_signal = np.add(audio_signal, (settings['master_volume'] + data[1]) * patches.patch(osc.square(note, frame_size, time_index)))
            if data[0] == "sine":
                audio_signal = np.add(audio_signal, (settings['master_volume'] + data[1]) * patches.patch(osc.sine(note, frame_size, time_index)))
        outdata[:] = audio_signal
        time_index += frame_size
        if(time_index > sys.maxsize - frame_size - frame_size): time_index = 0

    stream = sd.OutputStream(
        callback=audio_callback, channels=1, dtype=np.float32,
        samplerate=settings['sample_rate']
    )
    with stream:
        await event.wait()

##################################################################
#  Main program                     ԅ║ ⁰ ۝ ⁰ ║┐
##################################################################
async def main(**kwargs):
    print("•" * 60)
    print("༼つ ◕_◕ ༽つ " * 5)
    print("Python Polyphonic MIDI Synthesizer")
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
        "--defaults", dest="set_defaults", default=False,
        action="store_true", help="Generate default settings.json file and exit."
    )
    args = parser.parse_args()

    settings = None
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

    osc = oscillator(settings['sample_rate'])
    patches = patchboard()
    note_map = dict()

    #  Load data
    load_ppms_modules(settings, patches)
    load_module_data(settings, patches)

    in_task = asyncio.create_task(
        ppms_input(
            settings, patches, note_map,
            args.port, args.noimpact, args.verbose
        )
    )
    out_task = asyncio.create_task(
        ppms_output(settings, patches, note_map, osc)
    )

    try:
        await in_task
        await out_task
    except KeyboardInterrupt:
        pass
    finally:
        try:
            with open("settings.json", "w") as json_file:
                json.dump(settings, json_file, indent=4)
                print("Settings saved!  Exiting...")
        except IOError:
            print("Error saving settings.json!  Exiting...")
            sys.exit(1)
        print("PPMS Unloaded.")
        print()

##################################################################
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)

#  ( ⌐■-■)
#  ( ⌐■-■)>⌐■-■
#  EOF
