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


class LimitTest(unittest.TestCase):
    def test_third_accept_rejected(self):
        target = board()
        self.assertTrue(target.accept("p1", "b1", 0, "r1"))
        self.assertTrue(target.accept("p1", "b2", 0, "r2"))
        self.assertFalse(target.accept("p1", "b3", 0, "r3"))
        self.assertEqual(target.taken.get("p1"), 2)

    def test_limit_is_per_player(self):
        target = board()
        target.accept("p1", "b1", 0, "r1")
        target.accept("p1", "b2", 0, "r2")
        self.assertTrue(target.accept("p2", "b3", 0, "r3"))


class RefreshTest(unittest.TestCase):
    def test_new_day_resets_counts(self):
        target = board()
        target.refresh(1)
        target.accept("p1", "b1", 0, "r1")
        target.refresh(2)
        self.assertEqual(target.taken, {})
        self.assertTrue(target.accept("p1", "b2", 0, "r2"))

    def test_same_day_refresh_keeps_counts(self):
        target = board()
        target.refresh(1)
        target.accept("p1", "b1", 0, "r1")
        target.refresh(1)
        self.assertEqual(target.taken.get("p1"), 1)
        self.assertTrue(target.accept("p1", "b2", 0, "r2"))
        self.assertFalse(target.accept("p1", "b3", 0, "r3"))


class ExpireTest(unittest.TestCase):
    def test_expired_bounty_leaves_open(self):
        target = board()
        target.accept("p1", "b1", 0, "r1")
        self.assertEqual(target.open_bounties(1001), [])
        self.assertEqual(target.returned, 1)

    def test_not_expired_at_ttl_boundary(self):
        target = board()
        target.accept("p1", "b1", 0, "r1")
        self.assertEqual(target.open_bounties(1000), ["b1"])

    def test_expiry_releases_quota(self):
        target = board()
        target.accept("p1", "b1", 0, "r1")
        target.accept("p1", "b2", 0, "r2")
        target.open_bounties(1001)
        self.assertEqual(target.taken.get("p1", 0), 0)
        self.assertTrue(target.accept("p1", "b3", 1001, "r3"))

    def test_returned_bounty_acceptable_again(self):
        target = board()
        target.accept("p1", "b1", 0, "r1")
        target.open_bounties(1001)
        self.assertTrue(target.accept("p2", "b1", 1001, "r2"))
        self.assertEqual(target.open_bounties(1001), ["b1"])


class IdempotencyTest(unittest.TestCase):
    def test_same_req_id_only_once(self):
        target = board()
        self.assertTrue(target.accept("p1", "b1", 0, "same"))
        self.assertFalse(target.accept("p1", "b2", 0, "same"))
        self.assertEqual(target.taken.get("p1"), 1)

    def test_repeat_does_not_change_state(self):
        target = board()
        target.accept("p1", "b1", 0, "same")
        target.accept("p1", "b1", 0, "same")
        self.assertEqual(target.open_bounties(0), ["b1"])
        self.assertEqual(target.taken.get("p1"), 1)


class ScanTest(unittest.TestCase):
    def test_scanned_not_linear_in_queries(self):
        target = Board(daily_limit=100000, ttl_ms=100000)
        for index in range(3000):
            target.accept("p-%d" % index, "b-%d" % index, 0, "r-%d" % index)
        for _ in range(3000):
            target.open_bounties(0)
        self.assertLessEqual(target.scanned_count(), 6000)


if __name__ == "__main__":
    unittest.main()
