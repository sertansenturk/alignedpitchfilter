#!/usr/bin/env python
from setuptools import setup


setup(name='alignedpitchfilter',
      version='1.1',
      author='Sertan Senturk',
      author_email='contact AT sertansenturk DOT com',
      license='agpl 3.0',
      description='Correct the an audio (predominant) melody according to '
                  'the aligned score',
      url='http://sertansenturk.com',
      packages=['alignedpitchfilter'],
      install_requires=[
          "numpy",
          "matplotlib",
      ],
      )
