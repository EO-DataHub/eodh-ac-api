"""Name utils - taken from MLFlow: https://github.com/mlflow/mlflow."""

from __future__ import annotations

import random
import uuid

_WF_ID_FIXED_WIDTH = 19


def _generate_unique_integer_id() -> int:
    """Utility function for generating a random fixed-length integer.

    Returns:
        A fixed-width integer

    """
    random_int = uuid.uuid4().int
    # Cast to string to get a fixed length
    random_str = str(random_int)[-_WF_ID_FIXED_WIDTH:]
    # append a random int as string to the end of the generated string for as many
    # leading zeros exist in the generated string in order to preserve the total length
    # once cast back to int
    for s in random_str:
        if s == "0":
            random_str += str(random.randint(0, 9))  # noqa: S311, B909, RUF100
        else:
            break
    return int(random_str)


def _generate_string(sep: str, integer_scale: int) -> str:
    """Generates a random human-readable string.

    Args:
        sep: Separator between string sections
        integer_scale: The integer scaling factor - will dictate max integer value

    Returns:
        A random string.

    """
    predicate = random.choice(_GENERATOR_PREDICATES).lower()  # noqa: S311
    noun = random.choice(_GENERATOR_NOUNS).lower()  # noqa: S311
    num = random.randint(0, 10**integer_scale)  # noqa: S311
    return f"{predicate}{sep}{noun}{sep}{num}"


def generate_random_name(sep: str = "-", integer_scale: int = 3, max_length: int = 18) -> str:
    """Helper function for generating a random predicate, noun, and integer combination.

    Args:
        sep: String separator for word spacing.
        integer_scale: Dictates the maximum scale range for random integer sampling (power of 10).
        max_length: Maximum allowable string length.

    Returns:
        A random string phrase comprised of a predicate, noun, and random integer.

    """
    name = ""
    for _ in range(10):
        name = _generate_string(sep, integer_scale)
        if len(name) <= max_length:
            return name
    # If the combined length isn't below the threshold after 10 iterations, truncate it.
    return name[:max_length]


_GENERATOR_NOUNS = [
    "ant",
    "ape",
    "asp",
    "auk",
    "bass",
    "bat",
    "bear",
    "bee",
    "bird",
    "boar",
    "bug",
    "calf",
    "carp",
    "cat",
    "chimp",
    "cod",
    "colt",
    "conch",
    "cow",
    "crab",
    "crane",
    "croc",
    "crow",
    "cub",
    "deer",
    "doe",
    "dog",
    "dolphin",
    "donkey",
    "dove",
    "duck",
    "eel",
    "elk",
    "fawn",
    "finch",
    "fish",
    "flea",
    "fly",
    "foal",
    "fowl",
    "fox",
    "frog",
    "gnat",
    "gnu",
    "goat",
    "goose",
    "grouse",
    "grub",
    "gull",
    "hare",
    "hawk",
    "hen",
    "hog",
    "horse",
    "hound",
    "jay",
    "kit",
    "kite",
    "koi",
    "lamb",
    "lark",
    "loon",
    "lynx",
    "mare",
    "midge",
    "mink",
    "mole",
    "moose",
    "moth",
    "mouse",
    "mule",
    "newt",
    "owl",
    "ox",
    "panda",
    "penguin",
    "perch",
    "pig",
    "pug",
    "quail",
    "ram",
    "rat",
    "ray",
    "robin",
    "roo",
    "rook",
    "seal",
    "shad",
    "shark",
    "sheep",
    "shoat",
    "shrew",
    "shrike",
    "shrimp",
    "skink",
    "skunk",
    "sloth",
    "slug",
    "smelt",
    "snail",
    "snake",
    "snipe",
    "sow",
    "sponge",
    "squid",
    "squirrel",
    "stag",
    "steed",
    "stoat",
    "stork",
    "swan",
    "tern",
    "toad",
    "trout",
    "turtle",
    "vole",
    "wasp",
    "whale",
    "wolf",
    "worm",
    "wren",
    "yak",
    "zebra",
]

_GENERATOR_PREDICATES = [
    "abundant",
    "able",
    "abrasive",
    "adorable",
    "adaptable",
    "adventurous",
    "aged",
    "agreeable",
    "ambitious",
    "amazing",
    "amusing",
    "angry",
    "auspicious",
    "awesome",
    "bald",
    "beautiful",
    "bemused",
    "bedecked",
    "big",
    "bittersweet",
    "blushing",
    "bold",
    "bouncy",
    "brawny",
    "bright",
    "burly",
    "bustling",
    "calm",
    "capable",
    "carefree",
    "capricious",
    "caring",
    "casual",
    "charming",
    "chill",
    "classy",
    "clean",
    "clumsy",
    "colorful",
    "crawling",
    "dapper",
    "debonair",
    "dashing",
    "defiant",
    "delicate",
    "delightful",
    "dazzling",
    "efficient",
    "enchanting",
    "entertaining",
    "enthused",
    "exultant",
    "fearless",
    "flawless",
    "fortunate",
    "fun",
    "funny",
    "gaudy",
    "gentle",
    "gifted",
    "glamorous",
    "grandiose",
    "gregarious",
    "handsome",
    "hilarious",
    "honorable",
    "illustrious",
    "incongruous",
    "indecisive",
    "industrious",
    "intelligent",
    "inquisitive",
    "intrigued",
    "invincible",
    "judicious",
    "kindly",
    "languid",
    "learned",
    "legendary",
    "likeable",
    "loud",
    "luminous",
    "luxuriant",
    "lyrical",
    "magnificent",
    "marvelous",
    "masked",
    "melodic",
    "merciful",
    "mercurial",
    "monumental",
    "mysterious",
    "nebulous",
    "nervous",
    "nimble",
    "nosy",
    "omniscient",
    "orderly",
    "overjoyed",
    "peaceful",
    "painted",
    "persistent",
    "placid",
    "polite",
    "popular",
    "powerful",
    "puzzled",
    "rambunctious",
    "rare",
    "rebellious",
    "respected",
    "resilient",
    "righteous",
    "receptive",
    "redolent",
    "resilient",
    "rogue",
    "rumbling",
    "salty",
    "sassy",
    "secretive",
    "selective",
    "sedate",
    "serious",
    "shivering",
    "skillful",
    "sincere",
    "skittish",
    "silent",
    "smiling",
    "sneaky",
    "sophisticated",
    "spiffy",
    "stately",
    "suave",
    "stylish",
    "tasteful",
    "thoughtful",
    "thundering",
    "traveling",
    "treasured",
    "trusting",
    "unequaled",
    "upset",
    "unique",
    "unleashed",
    "useful",
    "upbeat",
    "unruly",
    "valuable",
    "vaunted",
    "victorious",
    "welcoming",
    "whimsical",
    "wistful",
    "wise",
    "worried",
    "youthful",
    "zealous",
]
