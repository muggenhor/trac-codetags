#!/usr/bin/env python
from setuptools import setup
import os

def version_from_tag(tag, prefix='v'):
    gitdir = dir = os.path.dirname(os.path.abspath(__file__))
    while gitdir != '/':
        if os.path.exists(os.path.join(gitdir, '.git/HEAD')):
            tag_hash = os.popen('git rev-list --max-count=1 %s %s' % (prefix + tag, dir)).read()
            head_hash = os.popen('git rev-list --max-count=1 HEAD %s' % (dir,)).read()
            if tag_hash != head_hash:
                import datetime
                date = os.popen('git log --pretty=format:%%ct --max-count=1 %s' % (head_hash,)).read()
                date = datetime.datetime.utcfromtimestamp(long(date))
                tag += date.strftime('-%Y%m%d%H%M%S')
            break
        gitdir = os.path.dirname(gitdir)
    return tag

setup(
    name='codetags',
    version=version_from_tag('0.3', prefix=''),
    install_requires='Trac >= 0.10',
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
        'codetags' : ['templates/*.cs', 'templates/*.html', 'htdocs/*.css']
    },
    entry_points = {
        'trac.plugins': ['codetags = codetags']
    }
)
