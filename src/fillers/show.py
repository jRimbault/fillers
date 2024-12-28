from dataclasses import dataclass
from functools import cached_property


@dataclass(kw_only=True)
class Show:
    """
    Represents a TV show with a specified number of episodes per season and
    a set of absolute episode numbers that are fillers.

    Example:
        >>> show = Show(
        ...     seasons_episodes=[5, 3],
        ...     fillers_compressed=[2, 5]
        ... )
        >>> all_seasons = show.seasons()
        >>> # Access the first season
        >>> first_season = all_seasons[0]
        >>> # Retrieve filler instructions for the first season
        >>> instructions = first_season.fillers().instruction()
        >>> print(instructions)
        2
    """

    seasons_episodes: list[int]
    """number of episodes per seasons"""
    fillers_compressed: list[int | tuple[int, int]]
    """filler episodes in absolute numbering"""

    @cached_property
    def seasons(self):
        return [
            Season(self, season) for season in generate_ranges(self.seasons_episodes)
        ]

    @cached_property
    def fillers(self) -> set[int]:
        return decompress_range(self.fillers_compressed)


def generate_ranges(ints: list[int]):
    start = 1
    for i in ints:
        yield list(range(start, start + i))
        start += i


@dataclass
class Season:
    show: Show
    absolute_episodes: list[int]

    def __len__(self):
        return len(self.absolute_episodes)

    def episodes(self) -> list[int]:
        return list(range(1, len(self) + 1))

    def fillers(self):
        return Fillers(self)

    @cached_property
    def filler_episodes(self):
        return [
            relative_n
            for relative_n, absolute_n in enumerate(self.absolute_episodes, start=1)
            if absolute_n in self.show.fillers
        ]


@dataclass
class Fillers:
    season: Season

    @cached_property
    def instruction(self):
        season_filler = self.season.filler_episodes
        if len(season_filler) == len(self.season):
            return "skip season"
        elif season_filler:
            return format_ranges(season_filler)
        else:
            return "no filler"


def format_ranges(nums: list[int]) -> str:
    if not nums:
        return ""

    ranges: list[str] = []
    start = nums[0]
    end = nums[0]

    for i in range(1, len(nums)):
        if nums[i] == end + 1:
            end = nums[i]
        else:
            if start == end:
                ranges.append(f"{start}")
            else:
                ranges.append(f"{start}-{end}")
            start = end = nums[i]

    # Add the final range
    if start == end:
        ranges.append(f"{start}")
    else:
        ranges.append(f"{start}-{end}")

    return ", ".join(ranges)


def compress_ranges(nums: list[int]) -> list[int | tuple[int, int]]:
    if not nums:
        return []

    nums = sorted(set(nums))  # Sort and remove duplicates
    compressed: list[int | tuple[int, int]] = []
    start = nums[0]
    end = nums[0]

    for i in range(1, len(nums)):
        if nums[i] == end + 1:
            end = nums[i]
        else:
            if start == end:
                compressed.append(start)
            else:
                compressed.append((start, end + 1))
            start = end = nums[i]

    # Append the last range or number
    if start == end:
        compressed.append(start)
    else:
        compressed.append((start, end + 1))

    return compressed


def decompress_range(ranges: list[int | tuple[int, int]]):
    decompressed: set[int] = set()
    for item in ranges:
        match item:
            case int() as i:
                decompressed.add(i)
            case tuple() as t:
                a, b = t
                decompressed.update(range(a, b))
    return decompressed
