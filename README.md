# bounty-board

悬赏板：按服务日刷新、每日接取上限、过期回池与请求幂等，只用 Python 标准库。

```
python3 -m bounty.cli --sample limit
python3 -m bounty.cli --sample expire
python3 -m bounty.cli --sample dup
python3 -m bounty.cli --sample scan
python3 -m unittest discover -s tests -v
```

## 口径（README 为准）

- **每日上限**：同一玩家同一服务日最多成功接取 `daily_limit` 个悬赏，超出返回 false。
- **服务日刷新**：`refresh(day)` 只在新服务日生效一次，当天重复调用不清零计数。
- **过期回池**：接取后超过 `ttl_ms` 未完成的悬赏回到可接池，并释放该玩家的当日额度。
- **幂等**：同一个 `req_id` 只生效一次。
- **不变量**：当日接取数不超过上限；回池后 `open_bounties` 重新包含它；重复执行结果相同。
- **代价**：`open_bounties` 不许扫描全部历史记录，`scanned_count` 不随记录数线性增长。
- **规模**：10 万条悬赏、每秒 10 万次查询，单次摊还 O(可接悬赏数)。

## 输出契约（不改格式）

```
third=.. taken=..
returned=.. open=..
second=..
scanned=..
```

## 目录

```
bounty/core.py   刷新、上限、回池与幂等
bounty/cli.py    命令行入口
tests/           unittest 用例
```
