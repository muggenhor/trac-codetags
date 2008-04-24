from setuptools import setup

PACKAGE = 'codetags'
VERSION = '0.1'

setup(
    name=PACKAGE,
    version=VERSION,
    packages=['codetags'],
    package_data={
        'codetags' : ['templates/*.cs', 'htdocs/*.css']
    },
    entry_points = {
        'trac.plugins': ['codetags = codetags']
    }
)
