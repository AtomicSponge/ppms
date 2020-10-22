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

import os, sys, time, json, asyncio, queue
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
        #  Config settings
        'sample_rate': 44100.0,
        'impact_weight': 10000,
        'preset_folder': "presets",

        #  Key bindings
        'note_on': 144,
        'note_off': 128,
        'preset_msg': 192,

        #  List modules to load
        #  Patchboard processes these in order
        'modules': [ 'mod.test' ],

        #  For storing preset files
        'presets': [],

        #  MIDI control bindings
        #  Format:  binding_name, midi[0], midi[1]
        'bindings': [
            #  Default bindings
            [ 'master_volume', 176, 24 ],
            [ 'pitch_wheel', 224, 0 ],
            [ 'mod_wheel', 176, 1 ],

            #  Module bindings
            #  Binding names should have the format class_name.member_name
            [ 'test_module.set_a_value', 176, 20 ]
        ],

        #  For saving module data
        'module_data': [],

        #  Variables
        'master_volume': 50,
        'pitch_bend': 0,
        'mod_value': 0,
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
#  Function to load module parameter data
##################################################################
def load_module_data(settings, patches):
    for module_data in settings['module_data']:
        mod = module_data[0].split(".", 1)
        getattr(patches.get_module(mod[0]), mod[1])(patches.get_module(mod[0]), module_data[1])

##################################################################
#  Input coroutine
##################################################################
async def ppms_input(exit_event, settings, patches, gate, port, noimpact, verbose):
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

            if(self.__noimpact): impact = 80 / self.__weight
            else: impact = message[2] * 3 / self.__weight

            #  ༼つ ◕_◕ ༽つ  Play saw note
            if message[0] == settings['note_on']:
                gate.put({'status': 'on', 'note': message[1], 'waveform': 'sawtooth', 'impact': impact})
                return
            if message[0] == settings['note_off']:
                gate.put({'status': 'off', 'note': message[1], 'waveform': 'sawtooth', 'impact': impact})
                return

            #  ༼つ ◕_◕ ༽つ  Play triangle note
            if message[0] == settings['note_on'] + 1:
                gate.put({'status': 'on', 'note': message[1], 'waveform': 'triangle', 'impact': impact})
                return
            if message[0] == settings['note_off'] + 1:
                gate.put({'status': 'off', 'note': message[1], 'waveform': 'triangle', 'impact': impact})
                return

            #  ༼つ ◕_◕ ༽つ  Play square note
            if message[0] == settings['note_on'] + 2:
                gate.put({'status': 'on', 'note': message[1], 'waveform': 'square', 'impact': impact})
                return
            if message[0] == settings['note_off'] + 2:
                gate.put({'status': 'off', 'note': message[1], 'waveform': 'square', 'impact': impact})
                return

            #  ༼つ ◕_◕ ༽つ  Play sine note
            if message[0] == settings['note_on'] + 3:
                gate.put({'status': 'on', 'note': message[1], 'waveform': 'sine', 'impact': impact})
                return
            if message[0] == settings['note_off'] + 3:
                gate.put({'status': 'off', 'note': message[1], 'waveform': 'sine', 'impact': impact})
                return

            #  (☞ﾟヮﾟ)☞  Check bindings
            for bindings in settings['bindings']:
                if(message[0] >= bindings[1] and message[0] <= bindings[1] + 3
                and message[1] == bindings[2]):
                    #  Adjust master volume
                    if(bindings[0] == "master_volume"):
                        settings['master_volume'] = message[2]
                        break
                    #  Check the pitch wheel
                    elif(bindings[0] == "pitch_wheel"):
                        settings['pitch_bend'] = message[2]
                        break
                    #  Check the mod wheel
                    elif(bindings[0] == "mod_wheel"):
                        settings['mod_value'] = message[2]
                        break
                    #elif:
                        #break
                    #  Find the loaded module and process its control
                    else:
                        mod = bindings[0].split(".", 1)
                        getattr(patches.get_module(mod[0]), mod[1])(patches.get_module(mod[0]), message[2])
                        break
    ##################################################################
    #  \END/ MIDI Input handler         ( ຈ ﹏ ຈ )
    ##################################################################

    #  Connect to MIDI device and start handler
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

    #  Run until exit event
    await exit_event.wait()
    del midiin

##################################################################
#  Output coroutine
##################################################################
async def ppms_output(exit_event, settings, patches, note_queue, osc):
    time_index = 0  #  Index for audio output stream
    note_map = dict()  #  Map to store playing notes

    #  Audio callback.  Generates the waveforms based on the input.
    def audio_callback(outdata, frame_size, time, status):
        nonlocal time_index, settings, osc, patches, note_map, note_queue

        #  Check pitch bend
        pitch_bend = 0
        if settings['pitch_bend'] < 64 or settings['pitch_bend'] > 64:
            #  Pitch down
            if settings['pitch_bend'] < 64:
                if settings['pitch_bend'] == 0: pitch_bend = 0.5 / -64
                else: pitch_bend = settings['pitch_bend'] / -64
            #  Pitch up
            if settings['pitch_bend'] > 64:
                pitch_bend = settings['pitch_bend'] / 127

        #  Process note map
        try:
            signal = note_queue.get_nowait()
            if signal['status'] == 'on':
                note_map.update({ signal['note']: [ signal['waveform'], signal['impact'] ] })
            if signal['status'] == 'off': del note_map[signal['note']]
            note_queue.task_done()
        except:
            pass

        #  Generate the audio signal
        audio_signal = np.zeros(shape=(frame_size,1), dtype=np.float32)
        for note in note_map:
            data = note_map.get(note)
            if data[0] == "sawtooth":
                audio_signal = np.add(audio_signal, (settings['master_volume'] * data[1]) * patches.patch(osc.sawtooth(note, pitch_bend, frame_size, time_index)))
            if data[0] == "triangle":
                audio_signal = np.add(audio_signal, (settings['master_volume'] * data[1]) * patches.patch(osc.triangle(note, pitch_bend, frame_size, time_index)))
            if data[0] == "square":
                audio_signal = np.add(audio_signal, (settings['master_volume'] * data[1]) * patches.patch(osc.square(note, pitch_bend, frame_size, time_index)))
            if data[0] == "sine":
                audio_signal = np.add(audio_signal, (settings['master_volume'] * data[1]) * patches.patch(osc.sine(note, pitch_bend, frame_size, time_index)))
        outdata[:] = audio_signal
        time_index += frame_size
        if(time_index > sys.maxsize - frame_size - frame_size): time_index = 0

    #  Set the audio callback
    stream = sd.OutputStream(
        callback=audio_callback, channels=1, dtype=np.float32,
        samplerate=settings['sample_rate']
    )
    #  Run until exit event
    with stream: await exit_event.wait()

##################################################################
#  Gate coroutine
#  Also controls exiting program
##################################################################
async def ppms_gate(exit_event, gate, note_queue, patches):
    while True:
        try:
            signal = gate.get(block=True, timeout=1)

            patches.send_gate(signal)
            note_queue.put(signal)

            gate.task_done()
        except KeyboardInterrupt:
            break
        except:
            pass
        finally:
            exit_event.set()  #  Send exit event

##################################################################
#  Main function, starts coroutines
##################################################################
async def main(settings, port, noimpact, verbose):
    #  Create the synth objects
    osc = oscillator(settings['sample_rate'])
    patches = patchboard()
    gate = queue.Queue()
    note_queue = queue.Queue()

    #  Load data
    load_ppms_modules(settings, patches)
    load_module_data(settings, patches)

    #  Event object for exiting program
    exit_event = asyncio.Event()

    #  Create coro tasks
    in_task = asyncio.create_task(
        ppms_input(
            exit_event, settings, patches, gate,
            port, noimpact, verbose
        )
    )
    out_task = asyncio.create_task(
        ppms_output(exit_event, settings, patches, note_queue, osc)
    )
    gate_task = asyncio.create_task(
        ppms_gate(exit_event, gate, note_queue, patches)
    )

    await in_task
    await out_task
    await gate_task

##################################################################
#  Start program
##################################################################
if __name__ == "__main__":
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
        "--build_presets", dest="build_presets", default=False,
        action="store_true", help="Detect presets."
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

    print("Starting PPMS.  Press Control-C to exit.")

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
        print("Error loading settings!  Exiting...")
        sys.exit(1)

    #  If --build_presets was passed, load preset files into settings.
    if(args.build_presets):
        print("Building preset list...")
        settings['presets'] = [f for f in os.listdir(settings['preset_folder'] + "/") if f.endswith(".json")]
        print("Done!")

    #  Now run the main program
    asyncio.run(main(settings, args.port, args.noimpact, args.verbose), debug=False)

    #  Wrap up by saving the settings
    try:
        with open(args.config, "w") as json_file:
            json.dump(settings, json_file, indent=4)
            print("Settings saved!  Exiting...")
    except IOError:
        print("Error saving settings.json!  Exiting...")
        sys.exit(1)
    print("PPMS Unloaded.")
    print()

#  ( ⌐■-■)
#  ( ⌐■-■)>⌐■-■
#  EOF
