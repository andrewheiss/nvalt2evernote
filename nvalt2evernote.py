#!/usr/bin/env python3
import glob
import os.path
import time
import subprocess
import markdown
from mdx_gfm import GithubFlavoredMarkdownExtension
from collections import namedtuple
from bs4 import BeautifulSoup, CData, Doctype

note_files = 'Notes/*.txt'
out_file = 'nvalt.enex'


def create_note(note_data, soup):
    """Create an ENEX note element"""

    note = soup.new_tag('note')

    title = soup.new_tag('title')
    title.string = note_data.title
    note.append(title)

    content_inside = BeautifulSoup(features="xml")
    content_inside.append(Doctype('en-export SYSTEM "http://xml.evernote.com/pub/evernote-export3.dtd"'))

    content_inside_note = soup.new_tag('en-note')
    content_inside_note.string = note_data.content
    content_inside.append(content_inside_note)

    content_inside_str = str(content_inside).replace('&lt;', '<').replace('&gt;', '>')

    content = soup.new_tag('content')
    content.string = CData(content_inside_str)
    note.append(content)

    created = soup.new_tag('created')
    created.string = str(note_data.created)
    note.append(created)

    updated = soup.new_tag('updated')
    updated.string = str(note_data.updated)
    note.append(updated)

    for single_tag in note_data.tags:
        if single_tag is not None:
            tag = soup.new_tag('tag')
            tag.string = single_tag
            note.append(tag)

    attributes = soup.new_tag('note-attributes')
    author = soup.new_tag('author')
    author.string = "Andrew Heiss"

    attributes.append(author)
    note.append(attributes)

    return note

def extract_tags(note):
    # mdls returns tags in a comma-separated list form that needs to be cleaned up
    # Here are potential outcomes
    #
    # Multiple tags: b'kMDItemOMUserTags = (\n    philanthropy,\n    giving\n)\n'
    # Single tag:    b'kMDItemOMUserTags = (\n    Quote\n)\n'
    # No tag:        b'kMDItemOMUserTags = (null)\n'
    #
    # There's probably some fancy Python way of parsing those, but I don't know
    # it. So instead, replace to the rescue!

    cmd = subprocess.Popen(['mdls', '-name', 'kMDItemOMUserTags', note],
                           stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    tags_raw, err = cmd.communicate()

    tags_raw = str(tags_raw)
    tags_semiclean = (tags_raw.
                      replace("b'kMDItemOMUserTags = (", "").
                      replace(")\\n'", "").
                      replace("\\n", "").
                      split(","))

    tags_clean = [tag.lstrip() for tag in tags_semiclean]
    tags_clean = [None if tag == 'null' else tag for tag in tags_clean]

    return(tags_clean)

def generate_enex():
    # Note data structure
    Note = namedtuple('Note', ['title', 'content', 'created', 'updated', 'tags'])

    # Generate empty XML document
    soup = BeautifulSoup(features="xml")
    soup.append(Doctype('en-export SYSTEM "http://xml.evernote.com/pub/evernote-export3.dtd"'))

    # Everything is wrapped in <en-export>
    root_tag = soup.new_tag("en-export")

    # Parse each note
    original_notes = glob.glob(note_files)

    for original_note in original_notes:
        title = os.path.basename(os.path.splitext(original_note)[0])

        with open(original_note, 'r') as f:
            text = f.read()

            content = markdown.markdown(text,
                                        extensions=[GithubFlavoredMarkdownExtension()])

        fileinfo = os.stat(original_note)
        created = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime(fileinfo.st_birthtime))
        modified = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime(fileinfo.st_mtime))

        tags = extract_tags(original_note)

        parsed_note = Note(title, content, created, modified, tags)

        # Append to <en-export> element
        root_tag.append(create_note(parsed_note, soup))

    # Append <en-export> to the empty XML document
    soup.append(root_tag)

    with open(out_file, 'w') as f:
        f.write(str(soup))

if __name__ == '__main__':
    generate_enex()
