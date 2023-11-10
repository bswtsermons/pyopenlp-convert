

import pytest
from unittest import mock
from unittest.mock import call
from truth.truth import AssertThat
from faker import Faker
from openlyrics import Verse, Lines, Line, tostring

from openlp_convert.convert import notes_to_verses, process_verse_buf, notes_to_song


fake = Faker()


def test_process_verse_buf_empty():
    # given
    fake_verse_buf = []
    fake_current_verse_no = fake.pyint()

    # when
    output = process_verse_buf(fake_verse_buf, fake_current_verse_no)

    # then
    AssertThat(output).IsNone()


def test_process_verse_buf():
    # given
    fake_verse_buf = [fake.pystr(), fake.pystr()]
    fake_current_verse_no = fake.pyint()

    # when
    output = process_verse_buf(fake_verse_buf, fake_current_verse_no)

    # then
    verse = output
    AssertThat(verse).IsInstanceOf(Verse)
    AssertThat(verse.lines).HasSize(1)
    lines = verse.lines[0]
    AssertThat(lines).IsInstanceOf(Lines)
    AssertThat(lines.lines).HasSize(2)
    for idx, line in enumerate(lines.lines):
        fake_verse = fake_verse_buf[idx]
        AssertThat(line).IsInstanceOf(Line)
        AssertThat(line.markup).IsEqualTo(fake_verse)


@mock.patch('openlp_convert.convert.process_verse_buf')
def test_notes_to_verses(mock_pvb):
    # given
    fake_pystrs = [fake.pystr() for i in range(3)]
    print(fake_pystrs)
    fake_notes = f"""{fake_pystrs[0]}
    {fake_pystrs[1]}

    {fake_pystrs[2]}"""

    # when
    output = notes_to_verses(fake_notes)

    # then
    # AssertThat(output).IsEqualTo('no')
    AssertThat(output).IsEqualTo([mock_pvb.return_value, mock_pvb.return_value])
    mock_pvb.assert_has_calls([
        call([fake_pystrs[0], fake_pystrs[1]], 0),
        call([fake_pystrs[2]], 1)
        # call([fake_pystrs[2]], 1)
    ], any_order=True)


@pytest.mark.skip(reason='integration')
def test_notes_to_song_integration():
    # given
    fake_title = fake.pystr()
    fake_author = fake.pystr()
    fake_notes = f"{fake.pystr()}\n{fake.pystr()}\n\n\n{fake.pystr()}"

    # when
    output = notes_to_song(fake_title, fake_author, fake_notes)


    # then
    print(tostring(output))
    AssertThat(tostring(output)).IsEqualTo('foo')