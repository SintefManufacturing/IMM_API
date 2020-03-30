import os
from distutils.core import setup
from distutils.command.install_data import install_data

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'Injection Moulding Machine API Python',
    version='1.0',
    description = 'IMM API package for Python.',
    author = 'Mats, Olga Ogorodnyk',
    author_email = 'Mats.Larsen@sintef.no',
    url = 'https://github.com/SintefManufacturing/IMM_API.git',
    packages = ['imm','imm_logging_system'],
    provides = ['imm','imm_logging_system'],
    long_description=read('README.md'),
    classifiers = [
        'Development Status :: Development',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
    ],
license = 'MIT'
)
