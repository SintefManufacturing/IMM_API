import os
from distutils.core import setup
from distutils.command.install_data import install_data
# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'RevPI_DAQ',
    version='1.0',
    description = 'RevPI DAQ for Python.',
    author = 'Mats Larsen, Olga Ogorodnyk',
    author_email = 'Mats.Larsen@sintef.no',
    packages = ['revpi_daq'],
    provides = ['revpi_daq'],
    long_description=read('README.md'),
    classifiers = [
        'Development Status :: Development',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
    ],
license = 'mit'
)
