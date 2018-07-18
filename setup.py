from distutils.core import setup

setup(
    name="emakpy",
    version="0.0.1",
    description="Utilities for me",
    author="Ryosuke Kamesawa",
    author_email="emak.ryo@gmail.com",
    packages=['emakpy'],
    install_requires=[
        'filelock',
    ],
    test_suite='nose.collector',
    tests_require=['nose'],
)
