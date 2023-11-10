import pytest
from truth.truth import AssertThat

from openlp_convert.convert import notes_to_song, process_verse_buf


def test_notes_to_song_empty():
    # given
    fake_verse_buf = []

    # when
    output = process_verse_buf(fake_verse_buf)

    # then
    AssertThat(output).IsNone()
