from __future__ import annotations

from src.utils.names import _generate_unique_integer_id, generate_random_name

ADES_WF_ID_LEN_LIMIT = 19


def test_random_name_generation() -> None:
    # Validate exhausted loop truncation
    expected_len = 8
    name = generate_random_name(max_length=expected_len)
    assert len(name) == expected_len

    # Validate default behavior while calling 1000 times that names end in integer
    names = [generate_random_name() for _ in range(1000)]
    assert all(len(name) <= ADES_WF_ID_LEN_LIMIT for name in names)
    assert all(name[-1].isnumeric() for name in names)


def test_experiment_id_generation() -> None:
    generate_count = 1000000
    generated_values = {_generate_unique_integer_id() for _ in range(generate_count)}

    # validate that in 1 million WF IDs written to a set, no collisions occur
    assert len(generated_values) == generate_count
