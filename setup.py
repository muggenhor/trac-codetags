#!/usr/bin/env python

from setuptools import setup

setup(
    name='TracCodeTags',
    version='0.4',
    author='Giel van Schijndel',
    author_email='me@mortis.eu',
    url='https://trac-hacks.org/wiki/CodeTagsPlugin',
    download_url='https://github.com/trac-hacks/codetags.git',
    license='BSD',
    classifiers=[
        'Framework :: Trac',
        'License :: OSI Approved :: BSD License',
    ],
    keywords='trac plugin',
    packages=['codetags'],
    package_data={
        'codetags': ['templates/*.cs', 'templates/*.html', 'htdocs/*.css']
    },
    entry_points={
        'trac.plugins': ['codetags = codetags.web_ui']
    },
    install_requires=['Trac'],
)
