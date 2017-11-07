#!/usr/bin/env python
from setuptools import setup

setup(
    name='fire-ws',
    version='0.0.1',
    description="Fire webservice",
    long_description="Fire webservice",
    author="EyeSeeTea Team",
    author_email='info@eyeseetea.com',
    url='https://github.com/EyeSeeTea/FIRE-WS',
    packages=['fire'],
    package_dir={'fire-ws': 'fire-ws'},
    scripts=[],
    include_package_data=True,
    install_requires=[
        "Flask-HTTPAuth",
        "Flask-Cors",
        "Flask-RESTful",
        "Flask-SQLAlchemy",
        "marshmallow_sqlalchemy",
        "inflection",
        "Flask-ServiceLayer",
        "SAValidation",
        "Flask-Migrate",
    ],
    license="GPL3",
    keywords='fire webservice sip',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Topic :: Internet :: WWW/HTTP',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests.suite.get_test_suite',
    tests_require=[],
)
