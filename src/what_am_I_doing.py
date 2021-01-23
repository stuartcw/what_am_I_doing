#! /usr/bin/env python3

import re
import click
import os
from datetime import datetime
import pathlib
import collections

DEFAULT_OUTPUT_FOLDER = "~/what_am_I_doing"

IGNORE_THESE_FILES = [
    ".DS_Store"
]


def create_folder(path):
    outputfolder = os.path.expanduser(path)
    if not os.path.exists(outputfolder):
        os.makedirs(outputfolder)
    return pathlib.Path(outputfolder)


@click.command()
@click.argument('folderpath', type=click.Path(exists=True))
def create_report(folderpath):
    """Creates Markdown Reports on what you are doing."""

    outputfolder = create_folder(DEFAULT_OUTPUT_FOLDER)

    folderpath = os.path.expanduser(folderpath)
    updatesByHour = collections.defaultdict(list)

    now = datetime.now()

    for root, folders, files in os.walk(folderpath, followlinks=False):
        for filename in files:
            if filename not in IGNORE_THESE_FILES:
                filepath = pathlib.Path(root, filename)
                mtime = datetime.fromtimestamp(filepath.stat().st_mtime)

                if mtime.year == now.year and mtime.month == now.month:
                    # For now only deal with this month
                    mtime_str = mtime.strftime("%Y-%m-%d %H:00")
                    updatesByHour[mtime_str].append((root,filename))

    outputFilePath = pathlib.Path(outputfolder, now.strftime("%Y-%m.md"))

    with open(outputFilePath, "w") as output_file:
        output_file.write("# "+folderpath+"\n")
        for updateTime in sorted(updatesByHour.keys()):
            output_file.write("## "+updateTime+"\n")
            previous_root = None
            previous_pattern=None
            s=""
            for root, filename in sorted(updatesByHour[updateTime]):
                if not previous_root == root:
                    # Print a Directory heading
                    this_folder=root[len(folderpath):]
                    if not len(this_folder.strip()):
                        this_folder=folderpath
                    output_file.write("### "+this_folder+" \n")
                this_pattern=re.sub("[0-9]","x",filename)
                if not previous_pattern==this_pattern:
                    if len(s):
                        listItem = "* " + s 
                        output_file.write(listItem[:-2]+"\n")
                        s=""
                s=s+str(filename)+", "
                previous_root = root
                previous_pattern=this_pattern

    
if __name__ == '__main__':
    create_report()
