# aligned-pitch-filter

Python package to filter/correct a pitch track according to the alignment with the relevant score.

Currently the algorithm is able to correct the octave errors by taking pitch heights of the aligned notes as the reference.

Usage
=======
All the relevant data can be easily obtained:

```python
from alignedpitchfilter.AlignedPitchFilter import AlignedPitchFilter

pitch_corrected, synth_pitch, notes = AlignedPitchFilter.filter(pitch, notes)
```

The inputs are:
```python
# pitch 		  :	an n-by-2 matrix, where the values in the first column are 
#					the timestamps and the values in the second column are frequency 
#					values
# notes			  :	list of note structure. This is read from the alignedNotes.json 
#					output from https://github.com/sertansenturk/fragmentLinker repository 
# tonic			  : The tonic frequency value
```

The outputs are:
```python
# pitch_corrected :	The octave corrected pitch track. The size is equal to the size of pitch
# synth_pitch	  :	Synthetic pitch track from the notes input that is used for octave correction
```

You can refer to [pitchExtract.ipynb](pitchExtract.ipynb) for an interactive demo.

Installation
============

If you want to install the repository, it is recommended to install the package and dependencies into a virtualenv. In the terminal, do the following:

    virtualenv env
    source env/bin/activate
    python setup.py install

If you want to be able to edit files and have the changes be reflected, then
install the repository like this instead

    pip install -e .

Now you can install the rest of the dependencies:

    pip install -r requirements

Authors
-------
Sertan Senturk
contact@sertansenturk.com

Reference
-------
Thesis
