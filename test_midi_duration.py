import os
from deepiano.music import midi_io

midi_xml_003 = '/Users/xyz/Desktop/音色渲染数据集合/xml_wav_with_midi_Original/xml_arachno/003.mid'
midi_onset_003 = '/Users/xyz/Desktop/音色渲染数据集合/xml_wav_with_midi_Original_onlyonset/xml_arachno/003.mid'

assert os.path.exists(midi_xml_003)
assert os.path.exists(midi_onset_003)
midi_xml_003_ns = midi_io.midi_file_to_note_sequence(midi_xml_003)
print(midi_xml_003_ns.total_time)
# print(midi_xml_003_ns.notes[-1])
print('='*100)
midi_onset_003_ns = midi_io.midi_file_to_note_sequence(midi_onset_003)
print(midi_onset_003_ns.total_time)
# print(midi_onset_003_ns.notes[-1])


