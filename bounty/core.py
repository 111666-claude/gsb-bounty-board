"""悬赏板：按服务日刷新、每日接取上限、过期回池与请求幂等。"""

import heapq


class Board:
    def __init__(self, daily_limit, ttl_ms):
        self.daily_limit = daily_limit
        self.ttl_ms = ttl_ms
        self.taken = {}
        self.returned = 0
        self.accepted = {}
        self.memo = set()
        self.scanned = 0
        self._day = None
        self._expiry_heap = []

    def refresh(self, day):
        if day != self._day:
            self._day = day
            self.taken = {}
        return 0

    def _reap_expired(self, now_ms):
        heap = self._expiry_heap
        while heap and now_ms - heap[0][0] > self.ttl_ms:
            accepted_at, bounty = heapq.heappop(heap)
            current = self.accepted.get(bounty)
            if current is None or current[1] != accepted_at:
                continue
            player, _, day = current
            del self.accepted[bounty]
            self.returned += 1
            self.scanned += 1
            if day == self._day:
                left = self.taken.get(player, 0) - 1
                if left > 0:
                    self.taken[player] = left
                else:
                    self.taken.pop(player, None)

    def accept(self, player, bounty, now_ms, req_id):
        self.scanned += 1
        self._reap_expired(now_ms)
        if req_id in self.memo:
            return False
        if bounty in self.accepted:
            return False
        if self.taken.get(player, 0) >= self.daily_limit:
            return False
        self.accepted[bounty] = (player, now_ms, self._day)
        heapq.heappush(self._expiry_heap, (now_ms, bounty))
        self.taken[player] = self.taken.get(player, 0) + 1
        self.memo.add(req_id)
        return True

    def open_bounties(self, now_ms):
        self.scanned += 1
        self._reap_expired(now_ms)
        return sorted(self.accepted)

    def scanned_count(self):
        return self.scanned
