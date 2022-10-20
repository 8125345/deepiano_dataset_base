r"""Train Onsets and Frames piano transcription model."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
os.environ['TF_ENABLE_CONTROL_FLOW_V2'] = '1'

import sys

from deepiano.wav2mid import configs_tflite as configs
from deepiano.wav2mid import train_util

import tensorflow as tf

FLAGS = tf.app.flags.FLAGS

tf.app.flags.DEFINE_string('master', '',
                           'Name of the TensorFlow runtime to use.')
tf.app.flags.DEFINE_string('config', 'onsets_frames',
                           'Name of the config to use.')
tf.app.flags.DEFINE_string(
    'examples_path', '../../data/maestro/maestro-v1.0.0-tfrecord/validation.tfrecord*',
    'Path to a TFRecord file of train/eval examples.')
tf.app.flags.DEFINE_boolean(
    'preprocess_examples', True,
    'Whether to preprocess examples or assume they have already been '
    'preprocessed.')
tf.app.flags.DEFINE_string(
    'model_dir', '../../data/models/test-lite-lstm',
    'Path where checkpoints and summary events will be located during '
    'training and evaluation.')
tf.app.flags.DEFINE_string('eval_name', None, 'Name for this eval run.')
tf.app.flags.DEFINE_integer('num_steps', 10,
                            'Number of training steps or `None` for infinite.')
tf.app.flags.DEFINE_integer(
    'eval_num_steps', 1,
    'Number of eval steps or `None` to go through all examples.')
tf.app.flags.DEFINE_integer(
    'keep_checkpoint_max', 100,
    'Maximum number of checkpoints to keep in `train` mode or 0 for infinite.')
tf.app.flags.DEFINE_string(
    'hparams', '',
    'A comma-separated list of `name=value` hyperparameter values.')
tf.app.flags.DEFINE_boolean('use_tpu', False,
                            'Whether training will happen on a TPU.')
tf.app.flags.DEFINE_enum('mode', 'eval', ['train', 'eval'],
                         'Which mode to use.')
tf.app.flags.DEFINE_string(
    'log', 'INFO',
    'The threshold for what messages will be logged: '
    'DEBUG, INFO, WARN, ERROR, or FATAL.')


def run(config_map):
  """Run training or evaluation."""
  tf.logging.set_verbosity(FLAGS.log)
  tf.app.flags.mark_flags_as_required(['examples_path'])

  config = config_map[FLAGS.config]
  model_dir = os.path.expanduser(FLAGS.model_dir)

  hparams = config.hparams
  hparams.use_cudnn = tf.test.is_gpu_available()

  if sys.platform == 'darwin':
    # Force cqt in MacOS since the default 'mel' will crash
    hparams.spec_type = 'cqt'

  # Command line flags override any of the preceding hyperparameter values.
  hparams.parse(FLAGS.hparams)

  if FLAGS.mode == 'train':
    train_util.train(
        model_fn=config.model_fn,
        master=FLAGS.master,
        model_dir=model_dir,
        use_tpu=FLAGS.use_tpu,
        examples_path=FLAGS.examples_path,
        preprocess_examples=FLAGS.preprocess_examples,
        hparams=hparams,
        keep_checkpoint_max=FLAGS.keep_checkpoint_max,
        num_steps=FLAGS.num_steps)
  elif FLAGS.mode == 'eval':
    train_util.evaluate(
        model_fn=config.model_fn,
        master=FLAGS.master,
        model_dir=model_dir,
        name=FLAGS.eval_name,
        examples_path=FLAGS.examples_path,
        preprocess_examples=FLAGS.preprocess_examples,
        hparams=hparams,
        num_steps=FLAGS.eval_num_steps)
  else:
    raise ValueError('Unknown/unsupported mode: %s' % FLAGS.mode)


def main(argv):
  del argv
  run(configs.CONFIG_MAP)


def console_entry_point():
  tf.app.run(main)


if __name__ == '__main__':
  console_entry_point()
