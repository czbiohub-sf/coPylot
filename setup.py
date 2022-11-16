import sys
from setuptools import setup


if sys.version_info < (3, 8):
    sys.stderr.write(
        f'You are using Python '
        + "{'.'.join(str(v) for v in sys.version_info[:3])}.\n\n"
        + 'copylot only supports Python 3.9 and above.\n\n'
        + 'Please install Python 3.9 using:\n'
        + '  $ pip install python==3.9\n\n'
    )
    sys.exit(1)

setup(
    use_scm_version={"write_to": "copylot/_version.py"},
    setup_requires=['setuptools_scm'],
    entry_points={'console_scripts': ['copylot=copylot.gui.qt_main_window:main']},
)
