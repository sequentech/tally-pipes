#!/usr/bin/env python3

from setuptools import setup
from pip.req import parse_requirements

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements("requirements.txt")

# reqs is a list of requirement
# e.g. ['django==1.5.1', 'mezzanine==1.4.6']
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='Agora Tongo',
    version='0.0.1',
    author='Eduardo Robles Elvira',
    author_email='edulix@agoravoting.com',
    packages=['agora_tongo', 'agora_tongo.pipes'],
    scripts=['agora-tongo'],
    url='http://pypi.python.org/pypi/agora_tongo/',
    license='LICENSE',
    description='agora tongo results processing system',
    long_description=open('README.md').read(),
    install_requires=reqs,
    dependency_links = [
        'git+https://github.com/OpenTechStrategies/openstv.git',
        'git+https://github.com/agoraciudadana/agora-tally.git'
    ]
)
