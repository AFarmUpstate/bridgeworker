__version__ = '0.1'

import io
import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(here, 'README.rst'), encoding='utf8') as f:
    README = f.read()
with io.open(os.path.join(here, 'CHANGELOG.rst'), encoding='utf8') as f:
    CHANGES = f.read()

extra_options = {
    "packages": find_packages(),
}


setup(name="AutoPush",
      version=__version__,
      description='PunterGatherer Push Queue Manager',
      long_description=README + '\n\n' + CHANGES,
      classifiers=["Topic :: Internet :: WWW/HTTP",
                   "Programming Language :: Python :: Implementation :: PyPy",
                   'Programming Language :: Python',
                   "Programming Language :: Python :: 2",
                   "Programming Language :: Python :: 2.7"
                   ],
      keywords='push',
      author="jr conlin",
      author_email="jrconlin+push@gmail.com",
      url='http:///',
      license="MPL2",
      test_suite="nose.collector",
      include_package_data=True,
      zip_safe=False,
      tests_require=['nose', 'coverage', 'mock>=1.0.1', 'moto>=0.4.1'],
      install_requires=[
          "twisted>=15.0",
          "cryptography>=0.7.2",
          "boto>=2.36",
          "requests>=2.5.3",
          "txstatsd>=1.0.0",
          "configargparse>=0.9.3",
          "apns>=2.0.1",
          "gcm-client>=0.1.4",
          "datadog>=0.2.0",
      ],
      entry_points="""
      [console_scripts]
      pg_gcm = puntergatherer.gcm:main
      pg_apns = puntergatherer.apns:main
      """,
      **extra_options
      )
