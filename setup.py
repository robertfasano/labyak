from distutils.core import setup
from setuptools import find_packages

setup(
    name='labyak',
    version='0.1',
    description='High-level wrappers around the LJM Python library for data acquisition and waveform or pattern generation',
    author='Robert Fasano',
    author_email='robert.j.fasano@colorado.edu',
    packages=find_packages(),
    license='MIT',
    long_description=open('README.md').read(),
    install_requires=['dash',
                      'labjack-ljm']
)
