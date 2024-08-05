#!/usr/bin/env python3
"""
list metadata tags for mp3/ogg/flac music files
"""
import argparse
import mutagen
import os

parser = argparse.ArgumentParser(
        prog='list_tags',
        description='list metadata tags on mp3/ogg/flac music files')

# The starting directory or file to list tags from
parser.add_argument('file', help="file or directory to list tags from/in")
# whether to continue past the first directory
parser.add_argument('-r', '--recurse', action="store_true",
                    help="also scan subdirectories of the provided directory")
# Scan tags other than tracknumber, title, artist & album
parser.add_argument('-a', '--all-tags', action="store_true",
                    help="print all tags, not just tracknumber, title, artist, and album")

args = parser.parse_args()

# print the tags on a music file
def print_tags_on(path):
        data = mutagen.File(path, easy=True)
        print(f"#{data['tracknumber']} {data['title']} by {data['artist']} on {data['album']}")
        if args.all_tags:
            # list of lines that will have tags, so that it's not just one big mass
            other_tags = ["\t"]
            # currently modified line of tags
            tag_idx = 0
            for tag in data:
                # already printed
                if (tag == 'tracknumber' or tag == 'title' or
                    tag == 'artist' or tag == 'album'):
                    continue
                tag_str = "{}: {} ".format(tag, data[tag]) 
                # add a new line, this one is too long
                if len(other_tags[tag_idx]) + len(tag_str) > 80:
                    other_tags.append("\t")
                    tag_idx += 1
                other_tags[tag_idx] += tag_str
            for line in other_tags:
                print(line)


# print the tags on all the music files in a directory (root)
def print_dir(root, files):
    for file in files:
        if (not file.endswith('.ogg') and
            not file.endswith('.mp3') and
            not file.endswith('.flac')):
            continue

        full_path = os.path.join(root, file)
        print_tags_on(full_path)


# Examine the metadata recursively on files contained in the given directory
def recurse_scan_tags(directory):
    for root,dirs,files in os.walk(directory):
        print_dir(root, files)
        if not args.recurse:
            break


if __name__ == "__main__":
    if os.path.isfile(args.file):
        print_tags_on(args.file)
    else:
        recurse_scan_tags(args.file)
