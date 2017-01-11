# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='datapackage',
    version='0.1.0',
    description='Data package representation for cell migration tracking data',
    long_description=readme,
    author='paola masuzzo',
    author_email='paola.masuzzo@ugent.be',
    url='https://github.com/pcmasuzzo/dpkg',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
