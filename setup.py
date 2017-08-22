from setuptools import setup

VERSION = '0.0.1'
BASE_CVS_URL = 'https://github.com/weirdkhar/spindrift.git'

setup(
    name='spindrift',
    packages=['spindrift', ],
    version=VERSION,
    author='Ruhi Humphries, Kristina Johnson',
    author_email='Ruhi.Humphries@csiro.au',
    install_requires=[x.strip() for x in open('requirements.txt').readlines()],
    url=BASE_CVS_URL,
    download_url='{}/tarball/{}'.format(BASE_CVS_URL, VERSION),
    test_suite='tests',
    tests_require=[x.strip() for x in open('requirements_test.txt').readlines()],
    keywords=[],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
)
