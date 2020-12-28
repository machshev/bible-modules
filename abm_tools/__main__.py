"""Aramaic Bible Module tool"""
import argparse

from abm_tools.sedra.bible import parse_sedra3_bible_db_file


if __name__ == '__main__':
    """Main cli entry point"""
    parser = argparse.ArgumentParser(prog='abm_tools', description='Create Aramaic Sword modules')
    parser.add_argument('file_name', type=str, help='path to the BFBS.TXT')

    args = parser.parse_args()

    for entry in parse_sedra3_bible_db_file(file_name=args.file_name):
        print(entry)
