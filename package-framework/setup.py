"""A setuptools based setup module.

See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib
from collections import OrderedDict, namedtuple
import tokenize
import json
import io
import re
import os

here = pathlib.Path(__file__).parent.resolve()

packages=find_packages(where='src')

def package_path_depth(package):
    return len(package.split('.'))

def by_depth(package_list):
    return sorted(package_list, key=package_path_depth)

def shortest_package(package_list):
    packs = by_depth(package_list)
    shortest = packs[0]
    if package_path_depth(shortest) != 1:
        msg = 'expect shortest package in src: {shortest} to be undotted'
        raise ValueError(msg)
    return shortest


def pkg_dir():
    return os.path.join('src', shortest_package(packages))

def write_version_py(version):
    vpy = (here / pkg_dir() / '__version__.py' )
    vpy.write_text(f"__version__ = '{version}'\n", encoding='ascii')


current_version = (here / '__version__').read_text(encoding='ascii').strip()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

def ignore_comments(d):
    ignored = OrderedDict(
            (k, v) for (k, v) in d.items() if not k.startswith('#')
            )
    return ignored

                
with (here / 'setup.json').open(encoding='utf-8') as cfg_file:
    cfg = json.load(cfg_file, object_hook=ignore_comments)

def key_value(nested_dicts, path, default=None):
    if not isinstance(path, tuple):
        path = str(path).split('.')
    d = nested_dicts
    for el in path:
        try:
            d = d[el]
        except KeyError:
            return default
    return d

pkg_name = key_value(cfg, 'package.name') or shortest_package(packages)


optional_kw = OrderedDict()

#for key in key_value(cfg, 'package.optional_setup_keys') or ():
#    optional_kw[key] =  k

extras_require = key_value(cfg, 'package.extras_require')
if extras_require:
    optional_kw['extras_require'] = extras_require

def str2lines(s):
    for line in io.StringIO(s):
        yield line

def summarize():
    """
    return first non-blank non-commented line in long_description
    """
    for line in str2lines(long_description):
        if line.startswith('#'):
            continue
        if not line.strip():
            continue
        return line.strip()

def description():
    desc = key_value(cfg, 'package.description')
    return desc or summarize()

def find_console_scripts(path2glob):
    """
    automatically find scripts requiring console script entry point entries

    path2glob should be an OrderedDict mapping
        "path_to_search" -> "glob pattern of files to check"
    path_to_search should be a path relative to src/<package-dir-name> in linux
    form (find_entry_points will use pathlib to convert to local paths)

    **/ at the end of path will recursively search all subdirectories
    """
    candidates = []
    root = pathlib.Path(pkg_dir())
#    print(path2glob)
    for rel_path in path2glob:
        pattern = path2glob[rel_path]
        full_pattern = os.path.join(rel_path, pattern)
        for match in root.glob(full_pattern):
            candidates.append(match)
    def cs_entry(script, root):
        return script + '='
    cs_entries = []
    for candidate in filter(has_main_fn, candidates):
        rel = candidate.relative_to(root)
        parts = list(rel.parts)
        script = re.sub('[.]py', '', parts[-1])
        from_pkg = '.'.join(parts[:-1] + [script])
        entry = f'{script}={from_pkg}:main'
        cs_entries.append(entry)
    return cs_entries
        


def has_main_fn(candidate):
# tokenize.open detects encoding of python files which
# follow PEP 263
    with tokenize.open(str(candidate)) as pyfile:
        for line in pyfile:
            if re.match('def main *( *) *:', line):
                return True
        return False

entry_points = dict()
console_scripts = entry_points.setdefault('console_scripts', [])
console_scripts.append(find_console_scripts(key_value(cfg, 'package.script_search')))



# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

def call_setup(setup_fn=setup):
    setup_fn(
        # This is the name of your project. The first time you publish this
        # package, this name will be registered for you. It will determine how
        # users can install this project, e.g.:
        #
        # $ pip install sampleproject
        #
        # And where it will live on PyPI: https://pypi.org/project/sampleproject/
        #
        # There are some restrictions on what makes a valid project name
        # specification here:
        # https://packaging.python.org/specifications/core-metadata/#name
        name=pkg_name,  # Required

        # Versions should comply with PEP 440:
        # https://www.python.org/dev/peps/pep-0440/
        #
        # For a discussion on single-sourcing the version across setup.py and the
        # project code, see
        # https://packaging.python.org/en/latest/single_source_version.html
        version=current_version,  # Required

        # This is a one-line description or tagline of what your project does. This
        # corresponds to the "Summary" metadata field:
        # https://packaging.python.org/specifications/core-metadata/#summary
        description=description(),  # Optional

        # This is an optional longer description of your project that represents
        # the body of text which users will see when they visit PyPI.
        #
        # Often, this is the same as your README, so you can just read it in from
        # that file directly (as we have already done above)
        #
        # This field corresponds to the "Description" metadata field:
        # https://packaging.python.org/specifications/core-metadata/#description-optional
        long_description=long_description,  # Optional

        # Denotes that our long_description is in Markdown; valid values are
        # text/plain, text/x-rst, and text/markdown
        #
        # Optional if long_description is written in reStructuredText (rst) but
        # required for plain-text or Markdown; if unspecified, "applications should
        # attempt to render [the long_description] as text/x-rst; charset=UTF-8 and
        # fall back to text/plain if it is not valid rst" (see link below)
        #
        # This field corresponds to the "Description-Content-Type" metadata field:
        # https://packaging.python.org/specifications/core-metadata/#description-content-type-optional
        long_description_content_type='text/markdown',  # Optional (see note above)

        # This should be a valid link to your project's main homepage.
        #
        # This field corresponds to the "Home-Page" metadata field:
        # https://packaging.python.org/specifications/core-metadata/#home-page-optional
        #    url='https://github.com/pypa/sampleproject',  
#=======> use optional_setup_keys in setup.json

        # This should be your name or the name of the organization which owns the
        # project.
#    author='A. Random Developer',  # Optional
#=======> use optional_setup_keys in setup.json

        # This should be a valid email address corresponding to the author listed
        # above.
#    author_email='author@example.com',  # Optional
#=======> use optional_setup_keys in setup.json

        # Classifiers help users find your project by categorizing it.
        #
        # For a list of valid classifiers, see https://pypi.org/classifiers/
#=======> use optional_setup_keys in setup.json
        #classifiers=[  # Optional
            # How mature is this project? Common values are
            #   3 - Alpha
            #   4 - Beta
            #   5 - Production/Stable
        #    'Development Status :: 3 - Alpha',

            # Indicate who your project is intended for
        #    'Intended Audience :: Developers',
        #    'Topic :: Software Development :: Build Tools',

            # Pick your license as you wish
        #    'License :: OSI Approved :: MIT License',

            # Specify the Python versions you support here. In particular, ensure
            # that you indicate you support Python 3. These classifiers are *not*
            # checked by 'pip install'. See instead 'python_requires' below.
        #    'Programming Language :: Python :: 3',
        #    'Programming Language :: Python :: 3.5',
        #    'Programming Language :: Python :: 3.6',
        #    'Programming Language :: Python :: 3.7',
        #    'Programming Language :: Python :: 3.8',
        #    'Programming Language :: Python :: 3 :: Only',
#    ],

        # This field adds keywords for your project which will appear on the
        # project page. What does your project relate to?
        #
        # Note that this is a list of additional keywords, separated
        # by commas, to be used to assist searching for the distribution in a
        # larger catalog.
#    keywords='sample, setuptools, development',  # Optional
#=======> use optional_setup_keys in setup.json

        # When your source code is in a subdirectory under the project root, e.g.
        # `src/`, it is necessary to specify the `package_dir` argument.
        package_dir={'': 'src'},  # Optional
#=======> do not change: structure of framework does use this convention

        packages=packages,  # Required

        # Specify which Python versions you support. In contrast to the
        # 'Programming Language' classifiers above, 'pip install' will check this
        # and refuse to install the project if the version does not match. See
        # https://packaging.python.org/guides/distributing-packages-using-setuptools/#python-requires
#    python_requires='>=3.5, <4',
#=======> use optional_setup_keys in setup.json

        # This field lists other packages that your project depends on to run.
        # Any package you put here will be installed by pip when your project is
        # installed, so they must be valid existing projects.
        #
        # For an analysis of "install_requires" vs pip's requirements files see:
        # https://packaging.python.org/en/latest/requirements.html
#    install_requires=['peppercorn'],  # Optional
#=======> use optional_setup_keys in setup.json

        # List additional groups of dependencies here (e.g. development
        # dependencies). Users will be able to install these using the "extras"
        # syntax, for example:
        #
        #   $ pip install sampleproject[dev]
        #
        # Similar to `install_requires` above, these must be valid existing
        # projects.
#    extras_require={  # Optional
#        'dev': ['check-manifest'],
#        'test': ['coverage'],
#    },
#        extras_require={
#                'dev': ['pytest'],
#                'test': ['pytest'],
#                },
#=======> use extras_require in setup.json

        # If there are data files included in your packages that need to be
        # installed, specify them here.
#    package_data={  # Optional
#        'sample': ['package_data.dat'],
#    },
#=======> use optional_setup_keys in setup.json

        # Although 'package_data' is the preferred approach, in some case you may
        # need to place data files outside of your packages. See:
        # http://docs.python.org/distutils/setupscript.html#installing-additional-files
        #
        # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
#    data_files=[('my_data', ['data/data_file'])],  # Optional
#=======> use optional_setup_keys in setup.json

        # To provide executable scripts, use entry points in preference to the
        # "scripts" keyword. Entry points provide cross-platform support and allow
        # `pip` to create the appropriate form of executable for the target
        # platform.
        #
        # For example, the following would provide a command called `sample` which
        # executes the function `main` from this package when invoked:
        entry_points=entry_points,
#    {  # Optional
#        'console_scripts': [
#            'sample=sample:main',
#        ],
#    },

        # List additional URLs that are relevant to your project as a dict.
        #
        # This field corresponds to the "Project-URL" metadata fields:
        # https://packaging.python.org/specifications/core-metadata/#project-url-multiple-use
        #
        # Examples listed include a pattern for specifying where the package tracks
        # issues, where the source is hosted, where to say thanks to the package
        # maintainers, and where to support the project financially. The key is
        # what's used to render the link text on PyPI.
#    project_urls={  # Optional
#        'Bug Reports': 'https://github.com/pypa/sampleproject/issues',
#        'Funding': 'https://donate.pypi.org',
#        'Say Thanks!': 'http://saythanks.io/to/example',
#        'Source': 'https://github.com/pypa/sampleproject/',
#    },
#=======> use optional_setup_keys in setup.json


# optional keys without hard-coded or computed default values 

        **optional_kw
    )

def dump_args(*args, **kw):
    for i, arg in enumerate(args):
        print(f'arg ({i}) = {arg}')
    for k in sorted(kw):
        print(f'{k} = {kw[k]}')

if __name__ == '__main__':
    write_version_py(current_version)
    call_setup()
