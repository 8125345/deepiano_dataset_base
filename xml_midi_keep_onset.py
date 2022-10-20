import glob
import os
from shutil import copyfile

import collections


from pkl_to_midi import pkl_to_mid
from deepiano.wav2mid import configs
from deepiano.music import midi_io
from deepiano.wav2mid import audio_label_data_utils
from deepiano.music import sequences_lib
from deepiano.wav2mid import constants
from deepiano.wav2mid.data import hparams_frames_per_second

config = configs.CONFIG_MAP['onsets_frames']

def generate_midi_list(base_path):
    assert os.path.isdir(base_path)
    dir_list = glob.glob(os.path.join(base_path, '*'))
    xml_SC55_midi_list = []
    xml_arachno_midi_list = []
    for dir_ in sorted(dir_list):
        if 'xml_SC55' in dir_:
            xml_SC55_midi_list = glob.glob(os.path.join(dir_, '*.mid'))
        if 'xml_arachno' in dir_:
            xml_arachno_midi_list = glob.glob(os.path.join(dir_, '*.mid'))
    return sorted(xml_SC55_midi_list), sorted(xml_arachno_midi_list)


def sequence_to_pianoroll_fn(sequence, velocity_range, hparams):
    """Converts sequence to pianorolls."""
    #sequence = sequences_lib.apply_sustain_control_changes(sequence)
    roll = sequences_lib.sequence_to_pianoroll(
        sequence,
        frames_per_second=hparams_frames_per_second(hparams),
        min_pitch=constants.MIN_MIDI_PITCH,
        max_pitch=constants.MAX_MIDI_PITCH,
        min_frame_occupancy_for_label=hparams.min_frame_occupancy_for_label,
        onset_mode=hparams.onset_mode,
        onset_length_ms=hparams.onset_length,
        offset_length_ms=hparams.offset_length,
        onset_delay_ms=hparams.onset_delay,
        min_velocity=velocity_range.min,
        max_velocity=velocity_range.max)
    return (roll.active, roll.weights, roll.onsets, roll.onset_velocities,
            roll.offsets)


def midi_process(midi_file_path, dst_dir):
    assert os.path.isfile(midi_file_path)
    print(midi_file_path)
    ns = midi_io.midi_file_to_note_sequence(midi_file_path)
    # print(ns.notes)
    print(ns.total_time)
    print(type(ns.notes))
    print(len(ns.notes))

    velocity_range = audio_label_data_utils.velocity_range_from_sequence(ns)
    _, _, onsets, _, _ = sequence_to_pianoroll_fn(ns, velocity_range, hparams=config.hparams)
    onset_count = collections.Counter(onsets.flatten())
    print(onsets.shape)
    print(onset_count)

    # file_dir, file_name = os.path.split(midi_file_path)
    # destination_dir = file_dir.replace(base_path, dst_dir)
    # if not os.path.exists(destination_dir):
    #     os.makedirs(destination_dir)
    # dst_file = os.path.join(destination_dir, file_name)
    dst_file = '/Users/xyz/Desktop/原始MIDIonset测试/20220826export-004_onset.mid'
    pkl_to_mid.convert_to_midi_single(onsets, dst_file)


if __name__ == '__main__':
    base_path = '/Users/xyz/Desktop/xml_wav_with_midi_Original'
    dst_dir = '/Users/xyz/Desktop/xml_wav_with_midi_Original_copy'
    # xml_SC55_midi_list, xml_arachno_midi_list = generate_midi_list(base_path)
    # test_midi = xml_arachno_midi_list[3]
    test_midi = '/Users/xyz/Desktop/音频数据和评估结果/新增数据/yl/Record_16k_bgm_resource/8月份数据/bgm_record_20220826/original/20220826export-004.mid'
    midi_process(test_midi, dst_dir)
    # for xml_SC55_midi in xml_SC55_midi_list:
    #     midi_process(xml_SC55_midi, dst_dir)
    # for xml_arachno_midi in xml_arachno_midi_list:
    #     midi_process(xml_arachno_midi, dst_dir)


