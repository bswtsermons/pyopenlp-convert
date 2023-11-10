from typing import List

from openlyrics import Song, Verse, Lines, Line


def process_verse_buf(verse_buf: List[str], current_verse_no: int) -> Verse:
    """Convert a list of strings (constituting a verse) to an openlyric verse
    object."""
    res = None
    if verse_buf:
        lines_instance = Lines()
        lines_instance.lines.extend([Line(markup) for markup in verse_buf])
        verse = Verse()
        verse.name = f'v{current_verse_no + 1}'
        verse.lines.append(lines_instance)

        res = verse

    return res


def notes_to_song(notes: str) -> Song:
    pass
