#!/usr/bin/env python
from setuptools import setup

PACKAGE = 'codetags'
VERSION = '0.1'

setup(
    name=PACKAGE,
    version=VERSION,
    author='Giel van Schijndel',
    author_email='me@mortis.eu',
    url='http://trac-hacks.org/wiki/CodeTagsPlugin',
    download_url='http://git.mortis.eu/codetags.git',
    license='BSD',
    classifiers=[
        'Framework :: Trac',
        'License :: OSI Approved :: BSD License',
    ],
    keywords='trac plugin',
    packages=['codetags'],
    package_data={
        'codetags' : ['templates/*.cs', 'htdocs/*.css']
    },
    entry_points = {
        'trac.plugins': ['codetags = codetags']
    }
)
