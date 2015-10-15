import pdb
import numpy as np

def cent2hz(centVal, refHz):
	return refHz * 2**(centVal/1200)

def correctOctaveErrors(pitch, notes, tonic, ):
	# convert the symbolic pitch heights recorded in notes to Hz wrt tonic
	for note in notes:
		note['SymbolicPitch'] = note['Pitch']
		note['Pitch'] = {'Value': cent2hz(note['Pitch']['Value'],
			tonic['Value']),'Unit':'Hz'}

	# group the notes into sections
	synthPitch = notes2synthPitch(notes, pitch[:,0])

	# divide pitch into chunks
	pitchChunks = decompose_into_chunks(pitch)

	return synthPitch, pitchChunks, notes

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
			# post interpolation end time on the last note and group ends
			nextstartidx = find_closest_sample_idx(
				notes[i+1]['Interval'][0], time_stamps)
			endidx = nextstartidx-1
		
		synthPitch[startidx:endidx+1] = notes[i]['Pitch']['Value']

	return synthPitch

def find_closest_sample_idx(val, sampleVals):
	return np.argmin(abs(sampleVals - val))

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