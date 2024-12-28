import pytest

from fillers import Show
from fillers.show import format_ranges


@pytest.fixture
def sample_show():
    """
    Fixture to create a Show with known data for testing.
    Show has:
      - 3 seasons
      - Season 1 has 5 episodes, Season 2 has 3 episodes, Season 3 has 4 episodes
      - Fillers are episodes in absolute numbering: {2, 3, 7, 12}
    """
    return Show(
        seasons_episodes=[5, 3, 4],
        fillers_compressed=[2, 3, 7, 12],
    )


def test_show_seasons_count(sample_show: Show):
    """Test that the Show creates the correct number of seasons."""
    seasons = sample_show.seasons
    assert len(seasons) == 3, "Show should have 3 seasons"


def test_show_season_episodes(sample_show: Show):
    """
    Test that each Season within the Show reports its episodes
    correctly (using the public episodes() method).
    """
    seasons = sample_show.seasons

    # Season 1 should have 5 episodes
    assert len(seasons[0]) == 5
    assert seasons[0].episodes() == [1, 2, 3, 4, 5]

    # Season 2 should have 3 episodes
    assert len(seasons[1]) == 3
    assert seasons[1].episodes() == [1, 2, 3]

    # Season 3 should have 4 episodes
    assert len(seasons[2]) == 4
    assert seasons[2].episodes() == [1, 2, 3, 4]


def test_season_fillers_partial(sample_show: Show):
    """
    Test that a Season with some filler episodes returns
    the correct range string from the Fillers.instruction property.
    """
    seasons = sample_show.seasons
    # Season 1's absolute episodes: [1, 2, 3, 4, 5]
    # Filler episodes in Season 1 (absolute): {2, 3}
    # => In Season numbering, those are episodes 2 and 3
    instruction_s1 = seasons[0].fillers().instruction
    assert instruction_s1 == "2-3", "Expected partial filler range '2-3' for Season 1"


def test_season_fillers_entire_season(sample_show: Show):
    """Test a scenario where an entire season is filler."""
    # Modify the show so that Season 2 is entirely filler.
    # Season 2's absolute episodes are [6, 7, 8]
    # We'll add 6, 7, 8 to the filler set
    new_filler_set = set(sample_show.fillers)
    new_filler_set.update([6, 7, 8])
    sample_show.fillers = new_filler_set

    seasons = sample_show.seasons
    instruction_s2 = seasons[1].fillers().instruction
    assert (
        instruction_s2 == "skip season"
    ), "Expected 'skip season' when entire season is filler"


def test_season_fillers_none(sample_show: Show):
    """
    Test that a Season without any filler episodes
    returns the correct 'no filler' message.
    """
    # Season 3's absolute episodes: [9, 10, 11, 12]
    # Currently 12 is filler in sample_show. Let's remove 12 from the filler set
    new_filler_set = set(sample_show.fillers)
    new_filler_set.discard(12)  # remove absolute episode 12 from fillers
    sample_show.fillers = new_filler_set

    seasons = sample_show.seasons
    # Now Season 3 should have no fillers
    instruction_s3 = seasons[2].fillers().instruction
    assert instruction_s3 == "no filler", "Expected 'no filler' for Season 3"


@pytest.mark.parametrize(
    "filler_episodes, expected_instruction",
    [
        # Single filler (absolute #2)
        ([2], "2"),
        # Multiple contiguous fillers (absolute #2 to 3)
        ([2, 3], "2-3"),
        # Multiple contiguous fillers (absolute #2 to 4)
        ([(2, 5)], "2-4"),
        # Multiple disjoint fillers (absolute #2 and 4)
        ([2, 4], "2, 4"),
        # No fillers
        ([], "no filler"),
    ],  # type: ignore
)
def test_fillers_instructions_variations(
    filler_episodes: list[int | tuple[int, int]], expected_instruction: str
):
    """
    Parametrized test to ensure that filler instructions
    are correct for a variety of filler episode sets.
    This uses a simple 1-season Show (episodes 1..5).
    """
    show = Show(
        seasons_episodes=[5],  # Single season with 5 episodes
        fillers_compressed=filler_episodes,
    )
    season = show.seasons[0]
    assert season.fillers().instruction == expected_instruction


def test_fillers_skip_entire_single_episode_season():
    """
    If the season has just 1 episode and that episode is filler,
    instruction should be 'skip season'.
    """
    show = Show(
        seasons_episodes=[1],
        fillers_compressed=[1],  # Absolute episode #1 is filler
    )
    season = show.seasons[0]
    assert season.fillers().instruction == "skip season"


def test_fillers_caching_behavior(sample_show: Show):
    """
    Show that Fillers and Seasons are cached properly and return
    the same instances upon repeated calls.
    """
    first_season = sample_show.seasons[0]
    second_season_call = sample_show.seasons[0]
    assert (
        first_season is second_season_call
    ), "Seasons should be cached and return identical objects"


@pytest.mark.parametrize(
    "nums, expected",
    [
        ([], ""),
        ([2], "2"),
        ([2, 3], "2-3"),
        ([2, 3, 5], "2-3, 5"),
        ([1, 2, 3, 4, 5], "1-5"),
    ],
)
def test_format_ranges(nums: list[int], expected: str):
    """
    Directly test the format_ranges() helper function for a variety
    of input lists, ensuring correct formatting of contiguous
    and disjoint episodes.
    """
    assert format_ranges(nums) == expected
