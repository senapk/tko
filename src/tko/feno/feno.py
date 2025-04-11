import argparse

from .build import build_main
from .indexer import indexer_main
from .html import html_main
from .mdpp import mdpp_main
from .older import older_main
from .remote_md import remote_main
from tko.feno.filter import filter_main


def feno_main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='subcommands', help='help for subcommand.')

    # subparser for the 'build' command
    parser_r = subparsers.add_parser('build', help='build .mapi file.')
    parser_r.add_argument('targets', metavar='T', type=str, nargs='*', help='folders')
    parser_r.add_argument("--check", "-c", action="store_true", help="Check if the file needs to be rebuilt")
    parser_r.add_argument("--brief", "-b", action="store_true", help="Brief mode")
    parser_r.add_argument("--pandoc", "-p", action="store_true", help="Use pandoc rather than python markdown")
    parser_r.add_argument("--remote", "-r", action="store_true", help="Search for remote.cfg file and create absolute links")
    parser_r.add_argument("--erase", "-e", action="store_true", help="Erase .html and .tio temp files")
    parser_r.add_argument("--debug", "-d", action='store_true', help="Display debug msgs")
    parser_r.set_defaults(func=build_main)

    # subparser for the 'indexer' command
    parser_i = subparsers.add_parser('indexer', help='index Readme file.')
    parser_i.add_argument('path', type=str, help='Path to Markdown file')
    parser_i.add_argument("base", type=str, help="Folder with the problems")
    parser_i.set_defaults(func=indexer_main)

    # subparser for the 'html' command
    parser_h = subparsers.add_parser('html', help='generate HTML file from markdown file.')
    parser_h.add_argument('input', type=str, help='Input markdown file')
    parser_h.add_argument('output', type=str, help='Output HTML file')
    parser_h.add_argument('--no-latex', action='store_true', help='Disable LaTeX math rendering')
    parser_h.add_argument('--title', type=str, default="Problema", help='Title of the HTML file')
    parser_h.set_defaults(func=html_main)

    # subparser for the 'mdpp' command
    parser_m = subparsers.add_parser('mdpp', help='preprocessor for markdown files.')
    parser_m.add_argument('targets', metavar='T', type=str, nargs='*', help='Readmes or folders')
    parser_m.add_argument('--quiet', '-q', action="store_true", help='quiet mode')
    parser_m.add_argument('--clean', '-c', action="store_true", help='clean mode')
    parser_m.set_defaults(func=mdpp_main)

    # subparser for the 'older' command
    parser_o = subparsers.add_parser('older', help='check if the source is newer than the target')
    parser_o.add_argument('targets', type=str, nargs='+', help='Target files or directories')
    parser_o.set_defaults(func=older_main)

    # subparser for the 'remote' command
    parser_rm = subparsers.add_parser('remote', help='create remote markdown file.')
    parser_rm.add_argument('target', type=str, help='Folders')
    parser_rm.add_argument('--output', '-o', type=str, help='Output file')
    parser_rm.set_defaults(func=remote_main)

    # subparser for the 'filter' command
    parser_f = subparsers.add_parser('filter', help='filter code removing answers.')

    parser_f.add_argument('target', type=str, help='file or folder to process')
    parser_f.add_argument('-u', '--update', action="store_true", help='update source file')
    parser_f.add_argument('-c', '--cheat', action="store_true", help='recursive cheat mode cleaning comments on students files')
    parser_f.add_argument('-o', '--output', type=str, help='output target')
    parser_f.add_argument("-r", "--recursive", action="store_true", help="recursive mode")
    parser_f.add_argument("-f", "--force", action="store_true", help="force mode")
    parser_f.add_argument("-q", "--quiet", action="store_true", help="quiet mode")
    parser_f.add_argument("-i", "--indent", type=int, default=0, help="indent using spaces")
    parser_f.set_defaults(func=filter_main)



    args = parser.parse_args()


    args = parser.parse_args()
    if "func" not in args:
        parser.print_help()
        exit(1)
    else:
        args.func(args)
