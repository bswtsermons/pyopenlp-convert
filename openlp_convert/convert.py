from typing import List

from openlyrics import Song, Verse, Lines, Line, Title, Author


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


def notes_to_verses(notes: str) -> List[Verse]:
    current_verse_no = 0
    verses = []
    verse_buf = []
    for line in notes.splitlines():
        line = line.strip()
        if not line:
            verse = process_verse_buf(verse_buf, current_verse_no)
            if verse:
                verses.append(verse)
                current_verse_no += 1
            verse_buf = []
        else:
            verse_buf.append(line)

    verse = process_verse_buf(verse_buf, current_verse_no)
    if verse:
        verses.append(verse)

    return verses


def notes_to_song(title: str, author: str, notes: str) -> Song:
    verses = notes_to_verses(notes)

    title = Title(title)
    author = Author(author)

    song = Song()
    song.props.titles.append(title)
    song.props.authors.append(author)
    song.verses.extend(verses)

    return song