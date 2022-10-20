"""A setuptools based setup module for deepiano."""

import sys

from setuptools import find_packages
from setuptools import setup

# Bit of a hack to parse the version string stored in version.py without
# executing __init__.py, which will end up requiring a bunch of dependencies to
# execute (e.g., tensorflow, pretty_midi, etc.).
# Makes the __version__ variable available.
with open('deepiano/version.py') as in_file:
  exec(in_file.read())  # pylint: disable=exec-used

if '--gpu' in sys.argv:
  gpu_mode = True
  sys.argv.remove('--gpu')
else:
  gpu_mode = False

REQUIRED_PACKAGES = [
    'librosa >= 0.6.2',
    'mir_eval >= 0.4',
    'numpy >= 1.14.6',  # 1.14.6 is required for colab compatibility.
    'pretty_midi >= 0.2.6',
    'protobuf == 3.7.1', # 3.8 causes crash
    'scipy >= 0.18.1, <= 1.2.0',  # 1.2.1 causes segfaults in pytest.
    'sox >= 1.3.7',
    'futures;python_version=="2.7"',
    'apache-beam[gcp] >= 2.8.0;python_version=="2.7"',
]

if gpu_mode:
  REQUIRED_PACKAGES.append('tensorflow-gpu == 1.14.0')
else:
  REQUIRED_PACKAGES.append('tensorflow == 1.14.0')

# pylint:disable=line-too-long
CONSOLE_SCRIPTS = [
    'deepiano.wav2mid.create_dataset_maps',
    'deepiano.wav2mid.create_dataset_maestro',
    'deepiano.wav2mid.infer',
    'deepiano.wav2mid.train',
    'deepiano.wav2mid.transcribe',
]
# pylint:enable=line-too-long

setup(
    name='deepiano-gpu' if gpu_mode else 'deepiano',
    version=__version__,  # pylint: disable=undefined-variable
    description='Deep learning for piano music',
    long_description='',
    author='Wanaka Inc.',

    packages=find_packages(),
    install_requires=REQUIRED_PACKAGES,
    entry_points={
        'console_scripts': ['%s = %s:console_entry_point' % (n, p) for n, p in
                            ((s.split('.')[-1], s) for s in CONSOLE_SCRIPTS)],
    },

    include_package_data=True,
    package_data={
        'deepiano': ['models/image_stylization/evaluation_images/*.jpg'],
    },
    setup_requires=['pytest-runner', 'pytest-pylint'],
    tests_require=[
        'pytest',
        'pylint < 2.0.0;python_version<"3"',
        # pylint 2.3.0 and astroid 2.2.0 caused spurious errors,
        # so lock them down to known good versions.
        'pylint == 2.2.2;python_version>="3"',
        'astroid == 2.0.4;python_version>="3"',
    ],
)
