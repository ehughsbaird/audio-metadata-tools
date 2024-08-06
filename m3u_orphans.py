#!/usr/bin/env python3
"""
Check m3u playlists for orphaned references

Only checks for physical files
usage: m3u_orphans path/to/playlist -b path/to/playlist/items/base
"""
import argparse
import sys

from pathlib import Path

PLAYLIST_MAGIC="#EXTM3U"


parser = argparse.ArgumentParser(
        prog='m3u_orphans',
        description="identify orphaned tracks")
# need a playlist file to check
parser.add_argument('filename', help="playlist file to check")
# where to start search
parser.add_argument('-b', '--base', action="store",
                    help="where to search from files on the playlist")
# where to put corrected playlist
parser.add_argument('-o', '--output-file',
                    help="where to put playlist with corrections made")

args = parser.parse_args()

def main():
    # verify playlist is a valid file
    playlist = Path(args.filename)
    if not playlist.is_file():
        print("'{}' is not a file!".format(args.filename))
        sys.exit()

    # corrected playlist
    out = ""
    with playlist.open() as file:
        lines = file.readlines()
        # strip newline and check if it matches the magic
        if lines[0][:-1] != PLAYLIST_MAGIC:
            print("'{}' is not a valid playlist!".format(args.filename))
            sys.exit()
        out += lines[0]
        # check all the songs
        for line in lines[1:]:
            # strip newline
            song = line[:-1]
            base = "." if args.base is None else args.base
            song_path = Path(base, song)
            # if it's fine, just add it
            if song_path.is_file():
                out += line
                continue
            # otherwise, try some corrections
            #TODO: use arguments to do this
            #song = song.replace('/wrong/path/', '/right/path/')
            song_path = Path(song)
            if not song_path.is_file():
                print("'{}' is orphaned!".format(song))
            else:
                print("applied correction to '{}'".format(song))
                out += song + "\n"
    
    if args.output_file:
        with open(args.output_file, "w") as file:
            file.write(out)
    else:
        print("Nothing to write")
        

if __name__ == "__main__":
    main()
