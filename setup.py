# coding=utf8

from setuptools import setup, find_packages
import sys, os, re

version = None
with open('tubbe/__init__.py', 'r') as f:
    for line in f:
        m = re.match(r'^__version__\s*=\s*(["\'])([^"\']+)\1', line)
        if m:
            version = m.group(2)
            break


setup(name='tubbe',
      version=version,
      description="A failure-tolerant library for fallback acquired module.",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='failure-tolerant fallback',
      author='torpedoallen',
      author_email='torpedoallen@gmail.com',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'gevent>=1.2.2',
          'switch>=0.0.3',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
