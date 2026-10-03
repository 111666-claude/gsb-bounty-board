import unittest

from bounty.core import Board


def board():
    return Board(daily_limit=2, ttl_ms=1000)


class BasicTest(unittest.TestCase):
    def test_empty_open(self):
        self.assertEqual(board().open_bounties(0), [])

    def test_accept_then_open(self):
        target = board()
        target.accept("p1", "b1", 0, "r1")
        self.assertEqual(target.open_bounties(0), ["b1"])

    def test_refresh_starts_empty(self):
        self.assertEqual(board().taken, {})

    def test_scanned_starts_at_zero(self):
        self.assertEqual(board().scanned_count(), 0)


if __name__ == "__main__":
    unittest.main()
