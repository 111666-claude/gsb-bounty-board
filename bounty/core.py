"""悬赏板：按服务日刷新、每日接取上限、过期回池与请求幂等。"""

import heapq


class Board:
    def __init__(self, daily_limit, ttl_ms):
        self.daily_limit = daily_limit
        self.ttl_ms = ttl_ms
        self.accepted = {}
        self.taken = {}
        self.memo = set()
        self.day = None
        self.returned = 0
        self.scanned = 0
        self._expiry = []
        self._seq = 0

    def refresh(self, day):
        if day == self.day:
            return 0
        self.day = day
        self.taken = {}
        return 0

    def accept(self, player, bounty, now_ms, req_id):
        self._sweep(now_ms)
        if req_id in self.memo:
            return False
        self.memo.add(req_id)
        if bounty in self.accepted:
            return False
        if self.taken.get(player, 0) >= self.daily_limit:
            return False
        self.accepted[bounty] = (player, now_ms)
        self._seq += 1
        heapq.heappush(self._expiry, (now_ms + self.ttl_ms, self._seq, now_ms, bounty))
        self.taken[player] = self.taken.get(player, 0) + 1
        return True

    def open_bounties(self, now_ms):
        self._sweep(now_ms)
        return sorted(self.accepted)

    def scanned_count(self):
        return self.scanned

    def _sweep(self, now_ms):
        while self._expiry and self._expiry[0][0] < now_ms:
            _, _, accepted_ms, bounty = heapq.heappop(self._expiry)
            self.scanned += 1
            current = self.accepted.get(bounty)
            if current is None or current[1] != accepted_ms:
                continue
            del self.accepted[bounty]
            self.returned += 1
            count = self.taken.get(current[0], 0)
            if count <= 1:
                self.taken.pop(current[0], None)
            else:
                self.taken[current[0]] = count - 1
