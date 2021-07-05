from setuptools import setup, find_packages

from jtrader.core.version import get_version

VERSION = get_version()

f = open('README.md', 'r')
LONG_DESCRIPTION = f.read()
f.close()

setup(
    name='jtrader',
    version=VERSION,
    description='Trade them thangs',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Andres OBrien',
    author_email='oban0601@gmail.com',
    url='https://github.com/javabudd/trade-strategies',
    license='unlicensed',
    packages=find_packages(exclude=['ez_setup', 'tests*']),
    package_data={
        'jtrader': [
            'templates/*',
            'files/*'
        ]
    },
    include_package_data=True,
    entry_points="""
        [console_scripts]
        jtrader = jtrader.main:main
    """,
)
