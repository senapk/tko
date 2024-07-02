import pathlib
import re
from setuptools import setup, find_packages

here = pathlib.Path(__file__).parent.resolve()  # current path
long_description = (here / 'Readme.md').read_text(encoding='utf-8')  # Get the long description from the README file
# with open(here / 'requirements.txt') as fp:  # read requirements.txt
#     install_reqs = [r.rstrip() for r in fp.readlines() if not r.startswith('#')]


def get_version():
    file = here / 'src/tko/__init__.py'
    return re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]', file.read_text(), re.M).group(1)


setup(
    name='tko',  # Required https://packaging.python.org/specifications/core-metadata/#name
    version=get_version(),  # Required https://packaging.python.org/en/latest/single_source_version.html
    description='tko: Test Kit Operations',  # Optional
    long_description=long_description,  # Optional
    long_description_content_type='text/markdown',  # Optional
    url='https://github.com/senapk/tko',  # Optional, project's main homepage
    author='David Sena Oliveira',  # Optional, name or the name of the organization which owns the project
    author_email='sena@ufc.br',  # Optional
    classifiers=[
        'Development Status :: 3 - Alpha',  # 3 - Alpha, 4 - Beta, 5 - Production/Stable
        'Operating System :: OS Independent',  # Operating system
        'Topic :: Education',  # Topics
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',  # Pick your license as you wish
        'Programming Language :: Python :: 3.8',
    ],  # Classifiers help users find your project by categorizing it https://pypi.org/classifiers/
    keywords='programming, learning',  # Optional
    package_dir={'': 'src'},  # Optional, use if source code is in a subdirectory under the project root, i.e. `src/`
    packages=find_packages(where='src'),  # Required
    python_requires='>=3.8, <4',

    # Optional, additional pip packages to be installed by this package installation
    install_requires=[
        "windows-curses; platform_system=='Windows'",
        "appdirs"
    ],
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage', 'pytest'],
    },  # Optional

    tests_require=['pytest'],
    test_suite='tests',

    entry_points={'console_scripts': ['tko=tko.__main__:main']},

    project_urls={
        'Bug Reports': 'https://github.com/senapk/tko/issues',
        'Source': 'https://github.com/senapk/tko/',
    },  # Optional https://packaging.python.org/specifications/core-metadata/#project-url-multiple-use
)
