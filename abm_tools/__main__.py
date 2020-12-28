"""Aramaic Bible Module tool"""
import argparse

from abm_tools.sedra.bible import parse_sedra3_bible_db_file
from abm_tools.sedra.db import parse_sedra3_words_db_file


def cli() -> int:
    """Main cli entry point"""
    parser = argparse.ArgumentParser(prog='abm_tools', description='Create Aramaic Sword modules')
    parser.add_argument('file_name', type=str, help='path to the BFBS.TXT')

    args = parser.parse_args()

    words = parse_sedra3_words_db_file()

    for book, chapter, verse, word_num, word_id in parse_sedra3_bible_db_file(
            file_name=args.file_name,
    ):
        word = words.loc[word_id]

        print(book, chapter, verse, word_num, word_id, word['strVocalised'])

    return 0


if __name__ == '__main__':
    cli()
