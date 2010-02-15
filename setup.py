from setuptools import setup, find_packages
import sys, os

version = '0.5'

setup(name='Musync',
      version=version,
      description="Music Synchronizer",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='music',
      author='John-John Tedro',
      author_email='johnjohn.tedro@gmail.com',
      url='musync.sf.net',
      license='GPLv3',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          "mutagen>=1.12",
      ],
      entry_points={
          'console_scripts': [
              'musync = musync:entrypoint',
          ],
      }
      )
