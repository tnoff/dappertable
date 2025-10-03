import setuptools
import os

THIS_DIR = os.path.dirname(__file__)
VERSION_FILE = os.path.join(THIS_DIR, 'VERSION')
REQUIREMENTS_FILES = [os.path.join(THIS_DIR, 'requirements.txt')]

try:
    with open(VERSION_FILE) as r:
        version = r.read().strip()
except FileNotFoundError:
    version = '0.0.1'

required = []
for file_name in REQUIREMENTS_FILES:
    # Not sure why but tox seems to miss the file here
    # So add the check
    if os.path.exists(file_name):
        with open(file_name) as f:
            required += f.read().splitlines()

setuptools.setup(
    name='dappertable',
    description='Print python formatted tables',
    author='Tyler D. North',
    author_email='ty_north@yahoo.com',
    install_requires=required,
    entry_points={},
    packages=setuptools.find_packages(exclude=['tests']),
    version=version,
)
