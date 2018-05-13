import os
import sys
import re
from setuptools import setup, find_packages

# reading version (same way sqlalchemy does)
with open(os.path.join(os.path.dirname(__file__), 'easyq', '__init__.py')) as v_file:
    package_version = re.compile(r'.*__version__ = \'(.*?)\'', re.S).match(v_file.read()).group(1)

dependencies = [
    'pymlconf',
    'argcomplete'
]


setup(
    name='easyq',
    version=package_version,
    author='Vahid Mardani',
    author_email='vahid.mardani@gmail.com',
    url='http://github.com/pylover/easyq',
    description='Simple and easy message queue tcp server',
    packages=find_packages(),
    platforms=['any'],
    install_requires=dependencies,
    classifiers=[
        'Programming Language :: Python :: 3.5',
    ],
    entry_points={
        'console_scripts': [
            'easyq = easyq:main'
        ]
    },
    test_suite='easyq.tests',
)