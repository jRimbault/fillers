#!/usr/bin/env python3

import argparse
from dataclasses import dataclass
from pathlib import Path

import pandas
from tabulate import tabulate

import fillers
import fillers.scrape


class Memory(str):
    pass


class Lookup(str):
    pass


@dataclass
class Options:
    show: Memory | Lookup
    output: Path | None


def main(opts: Options) -> int:
    show = (
        fillers.SHOWS[opts.show]
        if isinstance(opts.show, Memory)
        else fillers.scrape.look_for(opts.show)
    )
    filler_df = pandas.DataFrame(
        (
            {
                "Season": i,
                "Filler": season.fillers().instruction,
                "Total": len(season),
            }
            for i, season in enumerate(show.seasons, start=1)
        ),
        index=None,
    )
    if opts.output is None:
        print(filler_df.to_string(index=False))
    else:
        markdown_table = tabulate(
            filler_df,  # type: ignore
            headers="keys",
            tablefmt="github",
            colalign=["left", "right", "right"],
            showindex="never",
        )
        opts.output.write_text(markdown_table)
        print(f"Filler data saved to {opts.output}")
    return 0


def parse_args(argv: list[str]) -> Options:
    parser = argparse.ArgumentParser(description="Format filler episode data.")

    subparser = parser.add_subparsers(required=True)

    memory = subparser.add_parser("memory")
    memory.add_argument("memory", type=str, choices=list(fillers.SHOWS.keys()))

    lookup = subparser.add_parser("lookup")
    lookup.add_argument("lookup", type=str)

    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Path to save the filler data markdown.",
        default=None,
    )
    args = parser.parse_args(argv)
    show = Memory(args.memory) if hasattr(args, "memory") else Lookup(args.lookup)
    return Options(output=args.output, show=show)


if __name__ == "__main__":
    import sys

    sys.exit(main(parse_args(sys.argv[1:])))
