Remove invalid MIDI files from a directory to a designated dump directory.

Pre-condition
===

pretty_midi just prints a warning in a fail case where I need an exception. You need to change that. Let's assume you're working in a virtual environment. Go to the root folder of that venv. Then search it for the source code file ```pretty_midi.py```. For me thats "<<environment-name>>/lib/python2.7/site-packages/pretty_midi/pretty_midi.py". In that file, find that call to ```warnings.warn()```. For me, that's line 96. Change it to ```raise Exception(```. Then, get rid of the second parameter, ```RuntimeWarning```, so the call will be valid. Now my script will work.

Options:
```--location``` - relative path from working directory to directory containing files to filter
```--dump``` - relative path from working directory to directory where bad MIDIs should be dumped

Will output a list of bad files in working directory in `removed_files.csv`.

Example bash script
```
#!/bin/bash

python pretty_midi_crasher.py --location data/classical --dump removed/classical
python pretty_midi_crasher.py --location data/jazz --dump removed/jazz
```

Some final thoughts: This isn't pretty. I'm sure you can still find plenty of ways to crash it. However, it's simple, it's readable and it works.