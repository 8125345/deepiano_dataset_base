# Lint as: python3
r"""Beam job for creating tfrecord files from datasets.

Expects a CSV with the following fields: audio_filename, midi_filename, split

Usage:
onsets_frames_transcription_create_tfrecords \
  --csv="/path/to/dataset.csv" \
  --output_directory="/path/to/output" \
  --num_shards="0" \
  --wav_dir="/path/to/dataset/audio" \
  --midi_dir="/path/to/dataset/midi" \
  --expected_splits="train,validation,test"

"""

import collections
import copy
import csv
import os

from absl import app
from absl import flags
from absl import logging

import apache_beam as beam
from apache_beam.metrics import Metrics
from deepiano.wav2mid import audio_label_data_utils
from deepiano.music import midi_io
from deepiano.protobuf import music_pb2

import tensorflow.compat.v1 as tf

FLAGS = flags.FLAGS

flags.DEFINE_string('csv', None, 'Path to dataset CSV')
flags.DEFINE_string('output_directory', None, 'Path to output_directory')
flags.DEFINE_string('wav_dir', None, 'Directory for wav files.')
flags.DEFINE_string('midi_dir', None, 'Directory for midi files.')
flags.DEFINE_integer('num_shards', 0, 'number of output shards')
flags.DEFINE_string('expected_splits', 'train,validation,test',
                    'Comma separated list of expected splits.')
flags.DEFINE_boolean(
    'add_wav_glob', False,
    'If true, will add * to end of wav paths and use all matching files.')
flags.DEFINE_list(
    'pipeline_options', '--runner=DirectRunner',
    'A comma-separated list of command line arguments to be used as options '
    'for the Beam Pipeline.')


class CreateExampleDoFn(beam.DoFn):
  """Splits wav and midi files for the dataset."""

  def __init__(self, wav_dir, midi_dir, add_wav_glob,
               *unused_args, **unused_kwargs):
    self._wav_dir = wav_dir
    self._midi_dir = midi_dir
    self._add_wav_glob = add_wav_glob
    super(CreateExampleDoFn, self).__init__(*unused_args, **unused_kwargs)

  def process(self, paths):
    midi_path, wav_path_base = paths

    if self._add_wav_glob:
      wav_paths = tf.io.gfile.glob(wav_path_base + '*')
    else:
      wav_paths = [wav_path_base]

    if midi_path:
      base_ns = midi_io.midi_file_to_note_sequence(midi_path)
      base_ns.filename = midi_path
    else:
      base_ns = music_pb2.NoteSequence()

    for wav_path in wav_paths:
      logging.info('Creating Example %s:%s', midi_path, wav_path)
      wav_data = tf.io.gfile.GFile(wav_path, 'rb').read()

      ns = copy.deepcopy(base_ns)

      # Use base names.
      ns.id = '%s:%s' % (wav_path.replace(self._wav_dir, ''),
                         midi_path.replace(self._midi_dir, ''))

      Metrics.counter('create_example', 'read_midi_wav').inc()

      example = audio_label_data_utils.create_example(ns.id, ns, wav_data)

      Metrics.counter('create_example', 'created_example').inc()
      yield example


def main(argv):
  del argv


  flags.mark_flags_as_required(['csv', 'output_directory'])

  tf.io.gfile.makedirs(FLAGS.output_directory)

  with tf.io.gfile.GFile(FLAGS.csv) as f:
    reader = csv.DictReader(f)

    splits = collections.defaultdict(list)
    for row in reader:
      splits[row['split']].append(
          (os.path.join(FLAGS.midi_dir, row['midi_filename']),
           os.path.join(FLAGS.wav_dir, row['audio_filename'])))

  if sorted(splits.keys()) != sorted(FLAGS.expected_splits.split(',')):
    raise ValueError('Got unexpected set of splits: %s' % list(splits.keys()))

  pipeline_options = beam.options.pipeline_options.PipelineOptions(
      FLAGS.pipeline_options)
  with beam.Pipeline(options=pipeline_options) as p:
    for split in splits:
      split_p = p | 'prepare_split_%s' % split >> beam.Create(splits[split])
      split_p |= 'create_examples_%s' % split >> beam.ParDo(
          CreateExampleDoFn(FLAGS.wav_dir, FLAGS.midi_dir, FLAGS.add_wav_glob))
      split_p |= 'write_%s' % split >> beam.io.WriteToTFRecord(
          os.path.join(FLAGS.output_directory, '%s.tfrecord' % split),
          coder=beam.coders.ProtoCoder(tf.train.Example),
          num_shards=FLAGS.num_shards)


if __name__ == '__main__':
  app.run(main)
