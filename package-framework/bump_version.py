#!env python3 
"""
bump major, minor, or patch semantic version in __version__
"""

import sys
import os
import re
import argparse

from collections import namedtuple

here = os.path.abspath(os.path.dirname(__file__))

components = ('major', 'minor', 'patch')
semantic_version = namedtuple('version', components)
svi = dict((field, i) for (i, field) in 
    enumerate(semantic_version._fields))

def get_args():
    argp = argparse.ArgumentParser(description = __doc__)
    argp.add_argument('--dry-run',
        default=False,
        action='store_true',
        help='do not write updated version to file')
    argp.add_argument('-v', '--verbose',
        default=0,
        action='count',
        help='increase verbosity')
    argp.add_argument('component',
        nargs='?',
        default=components[-1],
        choices=components,
        help='which component of semantic version to bump'
        )
        
    return argp.parse_args()

def get_version():
    with open(os.path.join(here, '__version__'), 'r') as vfile:
        vstring = next(vfile).strip()
    vcomps = tuple([int(x) for x in vstring.split('.')])
    version = semantic_version(*vcomps)
    return version

def version_string(sversion):
    return '.'.join(str(comp) for comp in sversion)

def write_version(sversion):
    with open(os.path.join(here, '__version__'), 'w') as vfile:
        vfile.write(version_string(sversion))




def handle_write_error(old_version, new_version):
    try:
        now = get_version()
    except IOError:
        now = None
    if now != new_version:
        sys.stderr.write("error writing version to __version__\n")
        if now != old_version:
            msg = "You must manually edit __version__"
            msg = msg + " to restore it to {}\n"
            msg = msg.format(version_string(old_version))
        else:
            msg = "__version__ is unchanged at {}\n"
            msg = msg.format(version_string(old_version))
        sys.stderr.write(msg)
        sys.exit(1)

def main():
    args = get_args()
    current = get_version()
    if args.verbose:
        print('current version is {}'.format(current))
    which = args.component
    bumped = getattr(current, which) + 1
    i_bumped = svi[which]
    replacements = {}
    replacements[which] = bumped
    for i in range(i_bumped + 1, len(current)):
        replacements[current._fields[i]] = 0
    new_version = current._replace(**replacements)
    if args.verbose:
        print('new version will be {}'.format(new_version))
    current_str = '.'.join(str(comp) for comp in current)
    new_version_str = '.'.join(str(comp) for comp in new_version)
    print('{} -> {}'.format(current_str, new_version_str))
    if not args.dry_run:
        try:
            write_version(new_version)
        except IOError:
            handle_write_error(current, new_version)



if __name__ == '__main__':
    main()
