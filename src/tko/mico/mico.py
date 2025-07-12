#!/usr/bin/env python3
from __future__ import annotations
import argparse
from .collect import Collect
from .pull import Pull
from .join import Join, update_reference_rep
from icecream import ic

def pull(args: argparse.Namespace) -> None:
    for target in args.targets:
        Pull.main(target, args.threads)

def collect(args: argparse.Namespace) -> None:
    for target in args.targets:
        Collect.main(target)

def join(args: argparse.Namespace) -> None:
    for target in args.targets:
        Join.main(target)

def refupdate(args: argparse.Namespace) -> None:
    for target in args.targets:
        update_reference_rep(target)

def combined(args: argparse.Namespace) -> None:
    
    if args.pull:
        for target in args.targets:
            Pull.main(target)
    if args.refupdate:
        for target in args.targets:
            update_reference_rep(target)
    if args.collect:
        for target in args.targets:
            Collect.main(target)
    if args.join:
        for target in args.targets:
            Join.main(target)

def mico_main():
    # Caminho do arquivo CSV
    parser = argparse.ArgumentParser(description="Ferramenta para lidar com tarefas do classroom usando o tko.")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode.")
    subcommands = parser.add_subparsers(dest="command", required=True)

    pull_cmd = subcommands.add_parser("pull", help="Pull data from the specified target.")
    pull_cmd.add_argument("targets", type=str, nargs="+", help="Json class task file")
    pull_cmd.add_argument("-t", "--threads", type=int, default=5, help="Number of threads to use for pulling data.")
    pull_cmd.set_defaults(func=pull)

    # Comando para atualizar repositório de referência
    refupdate_cmd = subcommands.add_parser("refupdate", help="Update the reference repository.")
    refupdate_cmd.add_argument("targets", type=str, nargs="+", help="Json class task file")
    refupdate_cmd.set_defaults(func=refupdate)

    collect_cmd = subcommands.add_parser("collect", help="Collect data from the specified target.")
    collect_cmd.add_argument("targets", type=str, nargs="+", help="Json class task files")
    collect_cmd.set_defaults(func=collect)

    join_cmd = subcommands.add_parser("join", help="Join collected data from the specified target.")
    join_cmd.add_argument("targets", type=str, nargs="+", help="Json class task files")
    join_cmd.set_defaults(func=join)

    combined_cmd = subcommands.add_parser("combi", help="Run many commands in many tasks.")
    combined_cmd.add_argument("targets", type=str, nargs="+", help="Json class task files")
    combined_cmd.add_argument("--refupdate", "-r", action="store_true", help="Update the reference repository.")
    combined_cmd.add_argument("--pull", "-p", action="store_true", help="Pull data from the specified targets.")
    combined_cmd.add_argument("--collect", "-c", action="store_true", help="Collect data from the specified targets.")
    combined_cmd.add_argument("--join", "-j", action="store_true", help="Join collected data from the specified targets.")
    combined_cmd.set_defaults(func=combined)

    args = parser.parse_args()
    if not args.debug:
        ic.disable()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    mico_main()
