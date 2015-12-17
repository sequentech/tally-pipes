#!/usr/bin/env python3

from setuptools import setup
from pip.req import parse_requirements
from pip.download import PipSession

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements("requirements.txt", session=PipSession())

# reqs is a list of requirement
# e.g. ['django==1.5.1', 'mezzanine==1.4.6']
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='Agora Results',
    version='1.0.0',
    author='Agora Voting Team',
    author_email='agora@agoravoting.com',
    packages=['agora_results', 'agora_results.pipes'],
    scripts=['agora-results'],
    url='http://pypi.python.org/pypi/agora_results/',
    license='LICENSE.AGPL3',
    description='agora results processing system',
    long_description=open('README.md').read(),
    install_requires=reqs,
    dependency_links = [
        'git+https://github.com/agoravoting/openstv.git@next#egg=openstv-1.7',
        'git+https://github.com/agoravoting/agora-tally.git@next#egg=agora-tally-0.0.1',
        'git+https://github.com/Julian/jsonschema.git@v2.5.1#egg=jsonschema-2.5.1'
    ]
)
