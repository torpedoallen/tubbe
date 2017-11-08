from setuptools import setup, find_packages
import sys, os

version = '0.2'

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
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
