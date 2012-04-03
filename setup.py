from setuptools import setup, find_packages
import os

version = open(os.path.join(
    'collective', 'mollie', 'version.txt')).read().strip()

setup(name='collective.mollie',
      version=version,
      description="Wrapper for the Mollie iDeal API",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone :: 3.3",
        "Framework :: Plone :: 4.0",
        "Framework :: Plone :: 4.1",
        "Framework :: Plone :: 4.2",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.4",
        "Programming Language :: Python :: 2.6",
        ],
      keywords='ideal mollie plone',
      author='Edition1',
      author_email='info@edition.nl',
      url='http://github.com/collective/collective.mollie',
      license='GPL version 2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      extras_require={
          'test': ['plone.app.testing', 'mock']
      },
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
