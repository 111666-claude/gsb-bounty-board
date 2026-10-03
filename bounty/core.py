"""悬赏板：按服务日刷新、每日接取上限、过期回池与请求幂等。

缺陷：不按服务日刷新、每日上限不生效、过期悬赏不回池、请求不幂等、
每次查询扫描全部悬赏。
"""


class Board:
    def __init__(self, daily_limit, ttl_ms):
        self.daily_limit = daily_limit
        self.ttl_ms = ttl_ms
        self.accepted = {}
        self.taken = {}
        self.memo = set()
        self.scanned = 0

    def refresh(self, day):
        self.taken = {}
        return 0

    def accept(self, player, bounty, now_ms, req_id):
        self.scanned += len(self.accepted)
        self.accepted[bounty] = (player, now_ms)
        self.taken[player] = self.taken.get(player, 0) + 1
        self.memo.add(req_id)
        return True

    def open_bounties(self, now_ms):
        self.scanned += len(self.accepted)
        return sorted(self.accepted)

    def scanned_count(self):
        return self.scanned
