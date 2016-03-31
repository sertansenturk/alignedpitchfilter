import numpy as np
import copy


class AlignedPitchFilter(object):
    def __init__(self):
        self.max_boundary_tol = 3  # seconds

    def filter(self, pitch, notes):
        # IMPORTANT: In the audio-score alignment step, the pitch value
        # of each note is computed from the theoretical pitch distance
        # from the tonic and de-normalized according to the tonic
        # frequency of the performance. The value is not computed from
        # THE PITCH TRAJECTORY OF THE NOTE; it is just the THEORETICAL
        # FREQUENCY OF THE NOTE SYMBOL ACCORDING TO THE TONIC FREQUENY
        # The performed stable pitch of the note will be computed in the
        # aligned-note-models

        pitch_corrected = np.copy(pitch)
        notes_corrected = copy.deepcopy(notes)

        # remove skipped notes
        notes_corrected = ([n for n in notes_corrected
                            if not n['Interval'][0] == n['Interval'][1]])

        # remove rests
        notes_corrected = [n for n in notes_corrected if
                           n['TheoreticalPitch']['Value']]

        # group the notes into sections
        synth_pitch = self._notes_to_synth_pitch(
            notes_corrected, pitch_corrected[:, 0])

        # octave correction
        for i, sp in enumerate(synth_pitch):
            pitch_corrected[i][1] = self._move_to_same_octave(
                pitch_corrected[i][1], sp)

        for nc in notes_corrected:
            trajectory = np.vstack(
                p[1] for p in pitch_corrected
                if nc['Interval'][0] <= p[0] <= nc['Interval'][1])
            nc['PerformedPitch']['Value'] = np.median(trajectory).tolist()

        return pitch_corrected, synth_pitch, notes_corrected

    def _notes_to_synth_pitch(self, notes, time_stamps):
        synth_pitch = np.array([0] * len(time_stamps))

        for i in range(0, len(notes)):
            prevlabel = ([] if i == 0 else
                         notes[i - 1]['Label'].split('--')[0])
            label = notes[i]['Label'].split('--')[0]
            nextlabel = ([] if i == len(notes) - 1 else
                         notes[i + 1]['Label'].split('--')[0])

            # pre interpolation start time on the first note
            if not prevlabel:
                startidx = self._find_closest_sample_idx(
                    notes[i]['Interval'][0] - self.max_boundary_tol,
                    time_stamps)
            elif not label == prevlabel:
                # post interpolation start time on a group start

                # recalculate the end time of the previous
                tempstartidx = self._find_closest_sample_idx(
                    notes[i]['Interval'][0], time_stamps)
                prevendidx = self._find_closest_sample_idx(
                    notes[i - 1]['Interval'][1] + self.max_boundary_tol,
                    time_stamps[:tempstartidx])

                startidx = prevendidx + self._find_closest_sample_idx(
                    notes[i]['Interval'][0] - self.max_boundary_tol,
                    time_stamps[prevendidx:]) + 1
            else:  # no pre interpolation
                startidx = self._find_closest_sample_idx(
                    notes[i]['Interval'][0], time_stamps)

            if not nextlabel:
                # post interpolation end time on the last note
                endidx = self._find_closest_sample_idx(
                    notes[i]['Interval'][1] + self.max_boundary_tol,
                    time_stamps)
            elif not label == nextlabel:
                # post interpolation end time on a group end
                nextstartidx = self._find_closest_sample_idx(
                    notes[i + 1]['Interval'][0], time_stamps)
                endidx = self._find_closest_sample_idx(
                    notes[i]['Interval'][1] + self.max_boundary_tol,
                    time_stamps[:nextstartidx])
            else:
                # post interpolation within a group
                nextstartidx = self._find_closest_sample_idx(
                    notes[i + 1]['Interval'][0], time_stamps)
                endidx = nextstartidx - 1

            synth_pitch[startidx:endidx + 1] = \
                notes[i]['TheoreticalPitch']['Value']

        return synth_pitch

    @staticmethod
    def _find_closest_sample_idx(val, sample_vals):
        return np.argmin(abs(sample_vals - val))

    @classmethod
    def _move_to_same_octave(cls, pp, sp):
        minpp = pp
        if not (pp == 0 or sp == 0):
            direction = 1 if sp > pp else -1

            prev_cent_diff = 1000000  # assign an absurd number
            decr = True
            while decr:
                cent_diff = abs(cls._hz2cent(pp, sp))
                if prev_cent_diff > cent_diff:
                    minpp = pp
                    pp *= 2 ** direction
                    prev_cent_diff = cent_diff
                else:
                    decr = False

        return minpp

    @staticmethod
    def _cent2hz(cent_val, ref_hz):
        try:
            return ref_hz * 2 ** (cent_val / 1200.0)
        except TypeError:  # _NaN_; rest
            return None

    @staticmethod
    def _hz2cent(val, ref_hz):
        return 1200.0 * np.log2(val / ref_hz)

    @staticmethod
    def _decompose_into_chunks(pitch, bottom_limit=0.7, upper_limit=1.3):
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
                    if len(temp_pitch) > 0:
                        pitch_chunks.append(temp_pitch)
                    temp_pitch = np.array([])
        if len(temp_pitch) > 0:
            pitch_chunks.append(temp_pitch)

        return pitch_chunks
