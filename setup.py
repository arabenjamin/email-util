#!/usr/bin/python
from setuptools import setup
#from mailer import __version__

__version__ ="0.1.6"

with open('requirements.txt') as f:
    reqs = f.read().splitlines()


#install_requires = open("requirements.txt").read().split('\n')
setup(
	name='mailer',
	version= __version__,
	install_requires=reqs,
	description='Send and Recieve emails via MS Exchange',
	author='Ara Benjamin',
	author_email='ara.benjamin@gmail.com',
	url= "https://github.com/arabenjamin/email-util",
	license='Creative Commons Attribution-Noncommercial-Share Alike license',
	packages=['mailer'],
	classifiers=['Programming Language :: Python :: 2.7'],
    zip_safe=False)
