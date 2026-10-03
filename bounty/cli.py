"""命令行入口：跑悬赏板样例。"""

import argparse

from .core import Board


def main(argv=None):
    parser = argparse.ArgumentParser(prog="bounty-board", description="悬赏板")
    parser.add_argument("--sample", default="limit", help="limit / expire / dup / scan")
    args = parser.parse_args(argv)
    if args.sample == "limit":
        board = Board(daily_limit=2, ttl_ms=100000)
        ok = True
        for index in range(3):
            ok = board.accept("p1", "b-%d" % index, index, "r-%d" % index)
        print("third=%s taken=%d" % (str(ok).lower(), board.taken.get("p1", 0)))
    elif args.sample == "expire":
        board = Board(daily_limit=5, ttl_ms=1000)
        board.accept("p1", "b1", 0, "r1")
        open_list = board.open_bounties(1001)
        print("returned=%d open=%d" % (board.returned, len(open_list)))
    elif args.sample == "dup":
        board = Board(daily_limit=5, ttl_ms=100000)
        board.accept("p1", "b1", 0, "same")
        print("second=%s" % str(board.accept("p1", "b2", 0, "same")).lower())
    elif args.sample == "scan":
        board = Board(daily_limit=100000, ttl_ms=100000)
        for index in range(3000):
            board.accept("p-%d" % index, "b-%d" % index, 0, "r-%d" % index)
        for index in range(3000):
            board.open_bounties(0)
        print("scanned=%d" % board.scanned_count())
    else:
        raise SystemExit("需要 --sample limit|expire|dup|scan")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
