import setuptools
import os

THIS_DIR = os.path.dirname(__file__)
VERSION_FILE = os.path.join(THIS_DIR, 'VERSION')

try:
    with open(VERSION_FILE) as r:
        version = r.read().strip()
except FileNotFoundError:
    version = '0.0.1'

setuptools.setup(
    name='dappertable',
    description='Print python formatted tables',
    author='Tyler D. North',
    author_email='ty_north@yahoo.com',
    install_requires=[],
    entry_points={},
    packages=setuptools.find_packages(exclude=['tests']),
    version=version,
)
