try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.md') as f:
        longdesc = f.read()

version = '0.0.0'

config = {
    'description': 'Business Taxation',
    'url': 'https://github.com/PSLmodels/Business-Taxation',
    'download_url': 'https://github.com/PSLmodels/Business-Taxation',
    'description': 'biztax',
    'long_description': longdesc,
    'version': version,
    'license': 'CC0 1.0 Universal public domain dedication',
    'packages': ['biztax'],
    'include_package_data': True,
    'name': 'biztax',
    'install_requires': ['taxcalc'],
    'classifiers': [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: CC0 1.0 Universal public domain dedication',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules'],
    'tests_require': ['pytest']
}

setup(**config)
