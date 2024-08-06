#!/usr/bin/env python3
"""
Share metadata tags between mp3/ogg/flac files in a directory

This is designed to fix the metadata for songs that lack metadata, but are in a
directory with other songs in the album that have it.

This will recursively execute on all directories under the directory it is called on

usage: share_tags directory
You may wish to run with -d first to see what changes will be made
"""
import argparse
import mutagen
import os

parser = argparse.ArgumentParser(
        prog='share_tags',
        description='Share mp3 tags between files in a directory')

# The starting directory to fix tags in
parser.add_argument('directory')
# Make no changes, but print metadata for files that would be affected
parser.add_argument('-d', '--dry-run', action='store_true')
# If there are files in the directory that have two different values for a tag,
# update what tags are common, and don't skip the directory
parser.add_argument('-l', '--loose', action='store_true')
# How to guess at name format for files missing name metadata
parser.add_argument('-n', '--name-format')

args = parser.parse_args()

# metadata tags that should be shared between files
shared_keys = ['album', 'artist', 'albumartist', 'genre', 'date']


# Share tags among the files in the given directory
def process_dir(working_dir):
    # mp3 files to process, list of (full file path, file name)
    targets = []
    # tag values to share
    tags = {}
    # tag values that conflict and will be skipped
    skipped_tags = set()
    # Find all the files in this directory
    for root, dirs, files in os.walk(working_dir):
        for file in files:
            full_path = os.path.join(root, file)
            if not full_path.endswith('.mp3'):
                targets.append((full_path, file))
        # Only look at this directory
        break
    # Get the tags from the files
    for file, local in targets:
        # Get the metadata with mutagen
        data = mutagen.File(file, easy=True)
        if 'title' not in data:
            # 'XX Title.mp3' if 'numbered', otherwise cut off the .mp3
            name_guess = local[3:-4] if args.name_format == 'numbered' else local[:-4]
            print('guessing "{}" for "{}"'.format(name_guess, local))
            # And give it a title
            data['title'] = name_guess
            data.save()
        # Look through the tags to find all the shared tags
        for tag,data in data.items():
            # If we're not sharing it, don't care
            if tag not in shared_keys:
                continue
            # If the tag hasn't been found, and the value isn't empty
            if tag not in tags and len(data) > 0:
                tags[tag] = data
            # If the tag has already been found, make sure it matches
            if tag in tags and tags[tag] != data:
                print("ERROR: {} does not match in {} ('{}' and '{}')".format( tag, working_dir, tags[tag], data))
                # If it's loose formatting, just skip this tag, and continue processing
                if args.loose:
                    skipped_tags.add(tag)
                # Otherwise, don't update this directory at all
                else:
                    return
    # If we're skipping any tags, give an alert
    if len(skipped_tags) > 0:
        print("For {}, not writing tags {}".format(working_dir, skipped_tags))
    # Then, update the tags on everything
    for file,local in targets:
        data = mutagen.File(file, easy=True)
        for tag in tags:
            if tag in skipped_tags:
                continue
            data[tag] = tags[tag]
        data.save()


# Examine the metadata recursively on files contained in the given directory
def print_dir(directory):
    for root,dirs,files in os.walk(directory):
        for file in files:
            if (not file.endswith('.mp3') and
                not file.endswith('.ogg') and
                not file.endswith('.flac')):
                continue
            data = mutagen.File(os.path.join(root, file), easy=True)
            print(data)


if __name__ == "__main__":
    if(args.dry_run):
        print_dir(args.directory)
    else:
        process_dir(args.directory)
        for root,dirs,files in os.walk(args.directory):
            for working_dir in dirs:
                process_dir(os.path.join(root, working_dir))
