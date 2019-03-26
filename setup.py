import re
import os
import setuptools 

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(BASE_DIR, 'easyTCP2', '__init__.py'), 'r')as f:
	version = re.search("__version__ = '(.*?)'", f.read()).group(1)

with open("README.md", "r") as f:
    long_description = f.read()


setuptools.setup(
	name="easyTCP2",
	version=version,
	url='https://github.com/dsal3389/easyTCP2',
	download_url='https://github.com/dsal3389/easyTCP2.git',
	license='MIT',
	author="Daniel Sonbolian",
	author_email='dsal3389@gmail.com',
	description="rich async server and easy to config",
	python_requires='>=3.7.*',
	install_requires=[],
	packages=setuptools.find_packages(),
	long_description=long_description,
	classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
	]
)