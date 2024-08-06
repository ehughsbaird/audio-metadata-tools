#!/usr/bin/env python3
"""
Strip characters from filenames that may not be allowed on more restrictive
filesystems. Originally developed for transfer from linux (ext4) to android
filesystem.

Invalid characters are normal ascii characters that may be invalid, in addition
to any non-printable characters.

usage: fix_filenames [-r] directory_or_file
"""
import argparse
import os
import string
import sys

INVALID_CHARS = "\"'*+/:<>?[\\]|"

parser = argparse.ArgumentParser(
        prog='fix_filenames',
        description='Remove characters from filenames that may be invalid on other filesystems')

parser.add_argument('file', help='file to fix or directory to fix in')
# fix names in subdirectories
parser.add_argument('-r', '--recurse', action='store_true',
                    help='recurse into subdirectories')
# dry run: only show what changes would happen, but do not make changes
parser.add_argument('-n', '--dry-run', action='store_true',
                    help='do not make any changes, just print changes that would be made')
# verbose: extra output (file name has no valid characters, print file rename info)
parser.add_argument('-v', '--verbose', action='store_true',
                    help='show extra output')
# TODO: option to fix names of directories
#parser.add_argument('-d', '--fix-directories', action='store_true',
#                    help='fix the names of directories as well as files')

args = parser.parse_args()

def fix_name(name):
    outname = ""
    for char in name:
        if char in INVALID_CHARS or char not in string.printable:
            continue
        outname += char
    if len(outname) == 0:
        if args.verbose:
            print("file {} has no valid characters in it's name".format(name))
        return "invalid_name"
    return outname


def main():
    changes = []
    for root,dirs,files in os.walk(args.file):
        for file in files:
            name = fix_name(file)
            if file != name:
                changes.append((os.path.join(root, file), os.path.join(root, name)))
        # only scan the first directory
        if not args.recurse:
            break

    for of, to in changes:
        if os.path.isfile(to) or os.path.isdir(to):
            print("ERROR: could not move '{}', file already exists at destination '{}'".format(of, to))
            if args.dry_run:
                continue
            else:
                sys.exit()
        if args.dry_run or args.verbose:
            print(of, '-->', to)
        if not args.dry_run:
            os.rename(of, to)


if __name__ == '__main__':
    main()
