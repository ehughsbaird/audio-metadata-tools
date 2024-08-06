#!/usr/bin/env python3
"""
Generate a TSV file with metadata tags for mp3/ogg/flac files, or apply metadata
tags from such a file to the files referenced by it

Expected usage:
tagedit -d DIR -o tags.tsv
# edit tags.tsv to desired values
tagedit -a tags.tsv
"""
import argparse
import mutagen
import os

parser = argparse.ArgumentParser(
        prog='tagedit',
        description='Generate and apply TSV files to edit metadata tags on mp3/ogg/flac files')
# TSV file to output to
parser.add_argument('-o', '--output-file', action='store',
                    help="location of TSV output file. If not specified, outputs to stdout")
# directory to scan music files in
parser.add_argument('-d', '--directory', action='store', help="directory to scan")
# Where the get tags from
parser.add_argument('-a', '--apply', action='store',
                    help="TSV file to apply metadata changes from")
# Whether to recurse when scanning directories
parser.add_argument('-r', '--recurse', action='store_true',
                    help="Recurse into subdirectories when scanning")


args = parser.parse_args()

# An entry corresponding to the editable data for a file and the location of it
class Record:
    def __init__(self, path, number, title, artist, album):
        self.path = path
        self.number = number
        self.title = title
        self.artist = artist
        self.album = album
    def stringify(record):
        return f"{record.artist}\t{record.album}\t{record.number}\t{record.title}\t{record.path}"


# Get a correctly formatted value for a metadata key
def get_value_for(data, key):
    if key not in data:
        return "unknown_" + key
    if len(data[key]) != 1:
        print("value for '{}' has multiples: {}!".format(key, data[key]))
        return None
    return data[key][0]


# Generate a record for a file type that mutagen has an easy handler for
def easy_handler(path):
    data = mutagen.File(path, easy=True)

    track = get_value_for(data, "tracknumber")
    title = get_value_for(data, "title")
    artist = get_value_for(data, "artist")
    album = get_value_for(data, "album")

    if(track is None or title is None or
       artist is None or album is None):
        print("Error in data for {}".format(path))
        return None

    return Record(path, track, title, artist, album)


# Handlers all the same, but separated for future-proofing
def ogg_handler(path):
    return easy_handler(path)


def flac_handler(path):
    return easy_handler(path)


def mp3_handler(path):
    return easy_handler(path)


# Find the records for a directory (root)
def read_dir(root, files):
    records = []
    for file in files:
        full_path = os.path.join(root, file)
        record = None
        if file.endswith('.ogg'):
            record = ogg_handler(full_path)
        elif file.endswith('.flac'):
            record = flac_handler(full_path)
        elif file.endswith('.mp3'):
            record = mp3_handler(full_path)

        if record is not None:
                  records.append(record)

    def key(record):
        return int(record.number)
    return sorted(records, key=key)


# given a tsv string representing a record, update the metadata in the corresponding file
def update_tags(record):
    tags = record.split("\t")
    if len(tags) != 5:
        print("Bad tags! Expected format is 'artist\talbum\tnumber\ttitle\tpath")
        return
    data = mutagen.File(tags[4], easy=True)
    data["artist"] = [tags[0]]
    data["album"] = [tags[1]]
    data["tracknumber"] = [tags[2]]
    data["title"] = [tags[3]]
    data.save()
    print(f"Updated '{tags[1]}' #{tags[2]} by '{tags[0]}' {tags[3]}")


# Read a tsv file with records, and update the metadata for each record
def update_tags_from(file):
    with open(file, "r") as fd:
        records = fd.readlines()
        for record in records:
            # Remove newline
            update_tags(record[:-1])


def write_tags_to(file, records):
    with open(file, "w") as fd:
        for record in records:
            fd.write(record + "\n")


def main():
    if args.directory:
        # All the records
        records = []
        # generated from each directory scanned
        for root,dirs,files in os.walk(args.directory):
            records += read_dir(root, files)
            if not args.recurse:
                break
        # stringify them for easier printing
        records = map(Record.stringify, records)
        # With no output file, just output to stdout
        if args.output_file:
            write_tags_to(args.output_file, records)
        else:
            for line in records:
                print(line)
    elif args.apply:
        update_tags_from(args.apply)
    else:
        print("No arguments provided")


if __name__ == "__main__":
    main()
