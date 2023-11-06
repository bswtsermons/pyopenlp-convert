import os

import pytest
import dropbox
from truth.truth import AssertThat

from openlyrics import Song, Verse, Properties, Author, Title, Lines, Line, tostring


def process_verse_buf(verse_buf, current_verse_no) -> Verse:
    res = None
    if verse_buf:
        lines_instance = Lines()
        lines_instance.lines.extend([Line(markup) for markup in verse_buf])
        verse = Verse()
        verse.name = f'v{current_verse_no + 1}'
        verse.lines.append(lines_instance)

        res = verse

    return res


def test_openlyrics_output():
    # given
    # print(os.environ['PYTHONPATH'])
    title = Title('Test Sermon 1')
    # properties = Properties()
    # properties.titles.append(title)
    # properties.
    # verse = Verse()
    author = Author('Samuel Browning')
    song = Song()
    song.props.titles.append(title)
    song.props.authors.append(author)
    # song.add_verse(verse)

    data = """John 3:16
For god so loved the world,
That he gave his only begotten Son,
That whomsoever believeth in Him should not perish,
But have everlasting life.

So we see in our notes here that this is
a very important scripture.
"""

    current_verse_no = 0
    verse_buf = []
    for line in data.splitlines():
        if not line:
            verse = process_verse_buf(verse_buf, current_verse_no)
            if verse:
                song.verses.append(verse)
                current_verse_no += 1
            verse_buf = []
        else:
            verse_buf.append(line)

    verse = process_verse_buf(verse_buf, current_verse_no)
    if verse:
        song.verses.append(verse)

    # print()

    # when
    output = tostring(song)
    print(output)

    # then
    AssertThat(output).IsFalse()


@pytest.mark.skip(reason='integration')
def test_dropbox_integration():
    # given
    dbx = dropbox.Dropbox(os.environ['DROPBOX_ACCESS_TOKEN'])

    # when
    output = dbx.users_get_current_account()
    dbx.files_upload(bytes('hello', 'UTF-8'), '/brian-python-test.txt', mode=dropbox.files.WriteMode("overwrite"))

    # then
    AssertThat(output).IsNone()
