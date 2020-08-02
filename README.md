## Python Polyphonic MIDI Synthesizer

[*Python3*](https://www.python.org/) script that simulates a modular synthesizer.  Requires a separate MIDI input device.

When a key is pressed, a sample is generated then added to the output stream.  It is then stored in a reference map.

When releasing a key, the sample is retrieved from the reference map and removed from the output stream.

Requires the following packages to be installed:
- [numpy](https://numpy.org/)
- [scipy](https://www.scipy.org/)
- [sounddevice](https://pypi.org/project/sounddevice/)
- [rtmidi](https://pypi.org/project/python-rtmidi/)

-----

## Modules

Requires:
```
def process(self, signal):
def save_data(self):
```

### Example
```
##  PPMS Synth Module for testing the patchboard.
class test_module:
    ##  Store test_value
    __test_value = 0

    ## Test process, simply print the test_value.
    #  @param self Object pointer
    #  @param signal Signal data to modify
    #  @return Modified signal data
    def process(self, signal):
        print("Test value:", self.__test_value)
        return signal

    ##  Build an array of save data for the module.
    #  Bindings should have the format class_name.member_name.
    #  @param self Object pointer
    #  @return Module data to save
    def save_data(self):
        return [
            [ 'test_module.set_a_value', self.__test_value ]
        ]

    ## Set test value.
    #  @param self Object pointer
    #  @param val New value to set
    def set_a_value(self, val):
        self.__test_value = val
```

-----

## Settings

Settings is loaded and saved from *settings.json*

### Loading modules
```
#  List modules to load
#  Patchboard processes these in order
'modules': [ 'mod.test' ],
```


### MIDI bindings
```
#  MIDI bindings
#  Format:  binding_name, midi[0], midi[1]
'bindings': [
    #  Default bindings
    [ 'master_volume', 176, 29 ],

    #  Module bindings
    #  Binding names should have the format class_name.member_name
    [ 'test_module.set_a_value', 176, 118 ]
],
```

### Saving data
```
#  For saving module data
'module_data': []
```
