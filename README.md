# nvALT to Evernote

Convert plain text notes stored in [Notational Velocity](http://notational.net/) or [nvALT](http://brettterpstra.com/projects/nvalt/) to an .enex file to import into [Evernote](https://evernote.com/). 

While Evernote can import a folder of plain text files as notes, it does not preserve their metadata. This script preserves a note's creation time, modified time, and [OpenMeta](https://code.google.com/archive/p/openmeta/) tags.

## Requirements

- OS X
- Python 3
- The Python packages listed in `requirements.txt` (install with `pip3 install -r requirements.txt`)

## Usage

1. Save `nvalt2evernote.py` somewhere on your computer.
2. Modify `note_files` to point to the notes you want to import
    - When I ran this, I copied my notes from `~/Dropbox/Notational Velocity` to `./Notes`, for convenience
    - You may need to run the script multiple times for each file type you use. I had both `.txt` and `.md` files.
3. Modify `out_file` to the name of the final Evernote export file.
4. Run the script.
