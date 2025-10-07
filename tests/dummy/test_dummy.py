from typing import Sequence

import pytest

from auto_sim.dummy import Dummy


class TestDummy:
    """Test that `Dummy` methods works as expected."""

    @staticmethod
    @pytest.fixture
    def dummy() -> Dummy:
        """Dummy instance."""
        return Dummy()

    @staticmethod
    @pytest.mark.parametrize("params, expected", [([1, 2], 3), ([2, 3], 5)])
    def test_addition(dummy: Dummy, params: Sequence[int], expected: int) -> None:
        """Test that `dummy.addition` adds two ints correctly."""
        a, b = params
        result = dummy.addition(a, b)

        assert result == expected, "output of dummy.addition is wrong"
