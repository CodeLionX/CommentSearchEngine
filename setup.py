#!/usr/bin/env python

import os
import distutils.cmd
import distutils.log
import subprocess
from setuptools import setup

with open(os.path.join('cse', 'VERSION')) as version_file:
    version = version_file.read().strip()

class CleanAllCommand(distutils.cmd.Command):
  """A custom command to clean the project directory."""

  description = 'remove build artifacts'
  user_options = [
      # The format is (long option, short option, description).
      ('includeDistributions=', 'd', 'removes distributions inside the `dist` folder as well'),
      ('includeVagrant=', 'v', 'removes vagrant mashines and their state as well'),
  ]

  def initialize_options(self):
    """Set default values for options."""
    self.includeDistributions = False
    self.includeVagrant = False

  def finalize_options(self):
    if self.includeDistributions:
      assert self.includeDistributions in ['true', 'True'], (
          '%s is not a valid option, use either true, True (shortcut: -d)' % self.includeDistributions)

    if self.includeVagrant:
      assert self.includeVagrant in ['true', 'True'], (
          '%s is not a valid option, use either true, True (shortcut: -v)' % self.includeVagrant)

  def run(self):
    command = ['rm', '-rf', 'build/*', '*.egg-info']
    if self.includeDistributions:
        command.append('dist/*')
    if self.includeVagrant:
        command.append('.vagrant')

    self.announce(
        'Running command: %s' % str(command),
        level=distutils.log.INFO)
    subprocess.run(command, stdout=subprocess.PIPE, shell=True, cwd=os.getcwd())
    #subprocess.check_call(command)

setup(
    name='CommentSearchEngine',
    version=version,
    description='Search Engine for Comments at news websites',
    author='Benedikt Bock, Sebastian Schmidl',
    author_email='mail@benedikt1992.de, sebastian.schmidl@t-online.de',
    url='https://github.com/CodeLionX/CommentSearchEngine',
    license='MIT',

    # own commands
    cmdclass={
        'cleanAll': CleanAllCommand,
    },

    # dependencies
    install_requires=[
        'scrapy>=1.4.0',
        'cffi>=1.7'
    ],

    # packages
    packages=['cse'],
    package_dir={'cse': './cse'},
    package_data={'cse': ['./VERSION', '../LICENSE']},
    include_package_data=True,

    # executable scripts
    entry_points={
        'console_scripts': [
            'crawl=scripts.crawl:main'
        ],
    },
)