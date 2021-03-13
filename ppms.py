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

from mod.parts import oscillator, patchboard, mod_control

##################################################################
#  Function to return a map of the default settings
##################################################################
def create_default_settings():
    return {
        #  Config settings
        'sample_rate': 44100.0,
        'impact_weight': 0.0006,
        'preset_folder': "presets",

        #  Key bindings
        'sawtooth_on': 144,
        'sawtooth_off': 128,
        'triangle_on': 145,
        'triangle_off': 129,
        'square_on': 146,
        'square_off': 130,
        'sine_on': 147,
        'sine_off': 131,
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
            [ 'bpm', 176, 61 ],

            #  Module bindings
            #  Binding names should have the format class_name.member_name
            [ 'test_module.set_a_value', 176, 20 ]
        ],

        #  For saving module data
        'module_data': [],

        #  Variables
        'master_volume': 50,
        'pitch_bend': 64,
        'mod_value': 0,
    }

##################################################################
#  Function to load modules into patchboard
##################################################################
def load_ppms_modules(settings, patches):
    patches.clear_modules()
    #  Take modules listed in settings and load into the patchboard
    for load_module in settings['modules']:
        try:
            mod = importlib.import_module(load_module)
            #  Search all objects in the loaded module
            for member_name, obj in inspect.getmembers(mod):
                #  Make sure we're loading a class from the module
                if inspect.isclass(obj) and obj.__module__ == mod.__name__:
                    #  Make sure the class extends synthmod base
                    if obj.IS_SYNTHMOD:
                        patches.add_module(obj)
                        print("Loaded module: ", obj.__module__)
                        break
        except:
            #  Report error and continue
            print("Failed loading module: ", load_module)
    importlib.invalidate_caches()

##################################################################
#  Function to load module parameter data
##################################################################
def load_module_data(settings, patches):
    for module_data in settings['module_data']:
        try:
            mod = module_data[0].split(".", 1)
            getattr(patches.get_module(mod[0]), mod[1])(patches.get_module(mod[0]), module_data[1])
        except:
            #  Report error and continue
            print("Unable to set: ", module_data[0])

##################################################################
#  Input coroutine
#  Get MIDI messages and process
#  Creates the MIDI input handler then sleeps until exit
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
                        #  Report error and continue
                        print("Error loading preset: ", settings['preset_folder'] + "/" + settings['presets'][message[1]])
                return

            #  ᕙ[･۝･]ᕗ  Calculate impact
            if(self.__noimpact): impact = self.__weight
            else: impact = ((message[2] / 127) * 1.01) * self.__weight

            #  ༼つ ◕_◕ ༽つ  Play saw note
            if message[0] == settings['sawtooth_on']:
                gate.put({'status': 'on', 'note': message[1], 'waveform': 'sawtooth', 'impact': impact})
                return
            if message[0] == settings['sawtooth_off']:
                gate.put({'status': 'off', 'note': message[1], 'waveform': 'sawtooth', 'impact': impact})
                return

            #  ༼つ ◕_◕ ༽つ  Play triangle note
            if message[0] == settings['triangle_on']:
                gate.put({'status': 'on', 'note': message[1], 'waveform': 'triangle', 'impact': impact})
                return
            if message[0] == settings['triangle_off']:
                gate.put({'status': 'off', 'note': message[1], 'waveform': 'triangle', 'impact': impact})
                return

            #  ༼つ ◕_◕ ༽つ  Play square note
            if message[0] == settings['square_on']:
                gate.put({'status': 'on', 'note': message[1], 'waveform': 'square', 'impact': impact})
                return
            if message[0] == settings['square_off']:
                gate.put({'status': 'off', 'note': message[1], 'waveform': 'square', 'impact': impact})
                return

            #  ༼つ ◕_◕ ༽つ  Play sine note
            if message[0] == settings['sine_on']:
                gate.put({'status': 'on', 'note': message[1], 'waveform': 'sine', 'impact': impact})
                return
            if message[0] == settings['sine_off']:
                gate.put({'status': 'off', 'note': message[1], 'waveform': 'sine', 'impact': impact})
                return

            #  (☞ﾟヮﾟ)☞  Check bindings
            for bindings in settings['bindings']:
                if(message[0] >= bindings[1] and message[0] <= bindings[1] + 3
                and message[1] == bindings[2]):
                    #  Adjust master volume
                    if(bindings[0] == "master_volume"):
                        settings['master_volume'] = message[2]
                        return
                    #  Check the pitch wheel
                    elif(bindings[0] == "pitch_wheel"):
                        settings['pitch_bend'] = message[2]
                        return
                    #  Check the mod wheel
                    elif(bindings[0] == "mod_wheel"):
                        settings['mod_value'] = message[2]
                        mod_control.set_mod_value(settings['mod_value'])
                        return
                    #  Add another binding
                    #elif:
                        #return
                    #  Find the loaded module and process its control
                    else:
                        try:
                            mod = bindings[0].split(".", 1)
                            getattr(patches.get_module(mod[0]), mod[1])(patches.get_module(mod[0]), message[2])
                        except:
                            pass  #  If binding not found, do nothing
                        return
    ##################################################################
    #  \END/ MIDI Input handler         ( ຈ ﹏ ຈ )
    ##################################################################

    #  Connect to MIDI device
    try:
        #  Prompt if port not given
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

    #  Create the MIDI handler
    try:
        midiin.set_callback(
            midi_input_handler(port_name, settings['impact_weight'], noimpact, verbose)
        )
    except:
        print("Error creating MIDI callback!  Exiting...")
        sys.exit(1)
    print("Connected to: ", port_name)

    #  Run until exit event
    await exit_event.wait()
    del midiin

##################################################################
#  Output coroutine
#  Gets on/off signals from the gate and updates the playing notes
#  Creates the audio output callback then sleeps until exit
##################################################################
async def ppms_output(exit_event, device, settings, patches, note_queue, osc):
    time_index = 0  #  Index for audio output stream
    note_map = dict()  #  Map to store playing notes

    #  Audio callback.  Generates the waveforms based on the input
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

        #  Process note queue
        while True:
            try:
                signal = note_queue.get_nowait()
                if signal['status'] == 'on':
                    note_map.update({ signal['note']: [ signal['waveform'], signal['impact'] ] })
                if signal['status'] == 'off': del note_map[signal['note']]
                note_queue.task_done()
            except:
                break  #  Loop until queue is processed

        #  Generate the audio signal
        audio_signal = np.zeros(shape=(frame_size,1), dtype=np.float32)
        for note in note_map:
            try:
                note_data = note_map.get(note)
                #  volume * impact * waveform(note, pitch_bend, frame_size, time_index)
                audio_signal = np.add(audio_signal, (settings['master_volume'] * note_data[1]) *
                    patches.patch(note, getattr(osc, note_data[0])(note, pitch_bend, frame_size, time_index)))
            except:
                pass  #  On errors generate nothing
        outdata[:] = audio_signal

        #  Increment time index for next frame
        time_index += frame_size
        #  Just incase the time index gets too large
        if(time_index > sys.maxsize - frame_size - frame_size): time_index = 0

    #  Set the audio callback
    if device is not None:
        stream = sd.OutputStream(
            callback=audio_callback, channels=1, dtype=np.float32,
            device=device, samplerate=settings['sample_rate']
        )
    else:
        stream = sd.OutputStream(
            callback=audio_callback, channels=1, dtype=np.float32,
            samplerate=settings['sample_rate']
        )
    #  Run until exit event
    with stream: await exit_event.wait()

##################################################################
#  Control coroutine
#  Processes the gate
#  Sends exit event when keyboard interrupt detected
##################################################################
async def ppms_control(exit_event, gate, note_queue, patches):
    while True:
        #  Check for a gate signal
        gate_signal = None
        try:
            #  Get gate signal from input
            gate_signal = gate.get(block=True, timeout=0.01)
            #  Send gate signal to output
            note_queue.put(gate_signal)
            #  Done
            gate.task_done()
        except KeyboardInterrupt:
            break
        except:
            pass
    #  End while True

    #  While loop broken, send exit event
    exit_event.set()

##################################################################
#  Main function, starts coroutines
##################################################################
async def main(settings, port, device, noimpact, verbose):
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
        ppms_output(exit_event, device, settings, patches, note_queue, osc)
    )
    control_task = asyncio.create_task(
        ppms_control(exit_event, gate, note_queue, patches)
    )

    await in_task
    await out_task
    await control_task

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
        "-o", "--output", dest="device", default=None,
        metavar="#", type=int, help="Audio out device."
    )
    parser.add_argument(
        "-v", "--verbose", dest="verbose", default=False,
        action="store_true", help="Display MIDI messages."
    )
    parser.add_argument(
        "-c", "--config", dest="config", default="settings.json",
        metavar="file", type=str, help="Configuration file to load. Default: %(default)s"
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
        "--list_audio", dest="list_audio", default=False,
        action="store_true", help="Display a list of available audio devices and exit."
    )
    parser.add_argument(
        "--defaults", dest="set_defaults", default=False,
        action="store_true", help="Generate default settings.json file and exit."
    )
    args = parser.parse_args()

    #  If --defaults was passed, create default settings.json file then exit
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

    #  If --list_audio passed, show available audio devices and exit
    if(args.list_audio):
        print(sd.query_devices())
        sys.exit(0)

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

    #  If --build_presets was passed, load preset files into settings
    if(args.build_presets):
        print("Building preset list...")
        settings['presets'] = [f for f in os.listdir(settings['preset_folder'] + "/") if f.endswith(".json")]
        print("Done!")

    #  Check if MIDI port or Output Device is configured in settings
    #  Command line arguments will override
    try:
        if settings['midi_port'] is not None and args.port is None:
            args.port = settings['midi_port']
    except:
        pass
    try:
        if settings['output_device'] is not None and args.device is None:
            args.device = settings['output_device']
    except:
        pass

    #  Now run the main program
    asyncio.run(main(settings, args.port, args.device, args.noimpact, args.verbose), debug=False)

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
