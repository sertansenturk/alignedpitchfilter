import pdb
import numpy as np

def correctOctaveErrors(pitch, notes, tonic, ):
	# convert the symbolic pitch heights recorded in notes to Hz wrt tonic
	for note in notes:
		note['SymbolicPitch'] = note['Pitch']
		note['Pitch'] = {'Value': cent2hz(note['Pitch']['Value'],
			tonic['Value']),'Unit':'Hz'}

	# remove skipped notes
	notes = ([n for n in notes 
		if not n['Interval'][0] == n['Interval'][1]])

	# group the notes into sections
	synth_pitch = notes2synthPitch(notes, pitch[:,0])

	# octave correction
	pitch_corrected = np.copy(pitch)
	for i, sp in enumerate(synth_pitch):
		pitch_corrected[i][1] = move2sameOctave(pitch[i][1], sp)

	return pitch_corrected, synth_pitch, notes

def notes2synthPitch(notes, time_stamps, max_boundary_tol = 6):
	synthPitch = np.array([0] * len(time_stamps))

	for i in range(0,len(notes)):
		prevlabel = ([] if i == 0 else
			notes[i-1]['Label'].split('--')[0])
		label = notes[i]['Label'].split('--')[0]
		nextlabel = ([] if i == len(notes)-1 else
			notes[i+1]['Label'].split('--')[0])

		# pre interpolation start time on the first note and the groups start
		if (not prevlabel) or (not label == prevlabel):
			startidx = find_closest_sample_idx(
				notes[i]['Interval'][0]-max_boundary_tol, time_stamps)
		else:  # no pre interpolation
			startidx = find_closest_sample_idx(
				notes[i]['Interval'][0], time_stamps)

		if not nextlabel:
			# post interpolation end time on the last note
			endidx = find_closest_sample_idx(
				notes[i]['Interval'][1]+max_boundary_tol, time_stamps)
		elif not label == nextlabel:
			# post interpolation end time on group end
			nextstartidx = find_closest_sample_idx(
				notes[i+1]['Interval'][0], time_stamps)
			endidx = find_closest_sample_idx(
				notes[i]['Interval'][1]+max_boundary_tol, 
				time_stamps[:nextstartidx])
		else:
			# post interpolation within a group
			nextstartidx = find_closest_sample_idx(
				notes[i+1]['Interval'][0], time_stamps)
			endidx = nextstartidx-1
		
		synthPitch[startidx:endidx+1] = notes[i]['Pitch']['Value']

	return synthPitch

def find_closest_sample_idx(val, sampleVals):
	return np.argmin(abs(sampleVals - val))

def move2sameOctave(pp, sp):
	minpp = pp
	if not(pp == 0 or sp == 0):
		direction = 1 if sp > pp else -1

		prev_cent_diff = 1000000 # assign an absurd number
		decr = True
		while decr:
			cent_diff = abs(hz2cent(pp,sp))
			if prev_cent_diff > cent_diff:
				minpp = pp
				pp = pp * (2 ** direction)
				prev_cent_diff = cent_diff
			else:
				decr = False

	return minpp

def cent2hz(centVal, refHz):
	return refHz * 2**(centVal/1200)

def hz2cent(val, refHz):
	return 1200 * np.log2(val/refHz)

def decompose_into_chunks(pitch, bottom_limit=0.7, upper_limit=1.3):
    """
    decomposes the given pitch track into the chunks.
    """

    pitch_chunks = []
    temp_pitch = np.array([])
    # starts at the first sample
    for i in range(1, len(pitch) - 1):
        # ignore chunks with 0 frequency values
        if pitch[i][1] == 0:
            pass
        # non-zero chunks
        else:
            interval = float(pitch[i + 1][1]) / float(pitch[i][1])
            temp_pitch = (np.vstack((temp_pitch, pitch[i])) 
            	if temp_pitch.size > 0 else pitch[i])

            if not bottom_limit < interval < upper_limit:
                if len(temp_pitch) > 0: pitch_chunks.append(temp_pitch)
                temp_pitch = np.array([])
    if len(temp_pitch) > 0: pitch_chunks.append(temp_pitch)

    return pitch_chunks