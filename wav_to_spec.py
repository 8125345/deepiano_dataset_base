
import librosa
import math
import tensorflow as tf
import numpy as np
from PIL import Image
from deepiano.wav2mid import configs
from deepiano.music import audio_io
from deepiano.music import midi_io
from deepiano.wav2mid.data import wav_to_spec

# mid to sequence(no sustain_control)
midi_file = './data/high-note_20210513/high-note-test_20210513/01-Audio-210513_1153.mid'
ns = midi_io.midi_file_to_note_sequence(midi_file)
config = configs.CONFIG_MAP['onsets_frames']

sample_rate = 16000
wav_file = './data/high-note_20210513/high-note-test_20210513/01-Audio-210513_1153.wav'
wav_data = tf.gfile.Open(wav_file, 'rb').read()

try:
    samples = audio_io.wav_data_to_samples(wav_data, sample_rate)
except audio_io.AudioIOReadError as e:
    print('Exception %s', e)

samples = librosa.util.normalize(samples, norm=np.inf)

# Add padding to samples if notesequence is longer.
pad_to_samples = int(math.ceil(ns.total_time * sample_rate))
padding_needed = pad_to_samples - samples.shape[0]
samples = np.pad(samples, (0, max(0, padding_needed)), 'constant')
new_wav_data = audio_io.samples_to_wav_data(samples, sample_rate)

spec = wav_to_spec(new_wav_data, config.hparams)
np.save('spec.npy', spec)
# show spec.
spec_image = Image.fromarray(spec.astype(np.uint8))
spec_image.show()
spec_image.save('spec.png')
 