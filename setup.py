# coding=utf-8
"""
locatebash
-
Active8 (04-03-15)
author: erik@a8.nl
license: GNU-GPL2
"""
from setuptools import setup
setup(name='locatebash',
      version='5',
      description='Combines mdfind and locate',
      url='https://github.com/erikdejonge/locatebash',
      author='Erik de Jonge',
      author_email='erik@a8.nl',
      license='GPL',
      entry_points={
          'console_scripts': [
              'loc=locatebash:main',
          ],
      },
      packages=['locatebash'],
      zip_safe=True,
      install_requires=['consoleprinter', 'arguments', 'fuzzywuzzy', 'argparse'],
      classifiers=[
          "Programming Language :: Python :: 2",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
          "Operating System :: POSIX",
          "Environment :: MacOS X",
          "Topic :: System",
      ])
