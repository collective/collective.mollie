from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='collective.mollie',
      version=version,
      description="Python wrapper for the Mollie API",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 4.1",
        "Programming Language :: Python",
        ],
      keywords='ideal mollie plone',
      author='Edition1',
      author_email='info@edition.nl',
      url='https://github.com/collective/collective.mollie',
      license='GPLv2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
