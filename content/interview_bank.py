"""Interview Track: questions in the style of AI-lab coding and ML rounds.

These are original questions modelled on publicly reported interview formats
(practical build-and-extend coding in Python, concurrency, DSA patterns,
numerics, transformer engineering). They are not leaked or official questions
from any company. Authoring rules are in qlib.py.
"""
from qlib import make_q

TOPICS = [
    ("practical", "Practical Build Rounds"),
    ("dsa", "DSA Patterns in Python"),
    ("numerics", "ML Numerics"),
    ("llm", "LLM & Transformer Engineering"),
]

QUESTIONS = []
Q = make_q("interview", QUESTIONS)

# ───────────────────────── Practical Build Rounds ─────────────────────────

Q("IV-PRC-001", "practical", "medium", verify=True,
  code="""
  class Bank:
      def __init__(self):
          self.balances = {}
      def deposit(self, acct, amt):
          self.balances[acct] = self.balances.get(acct, 0) + amt
          return self.balances[acct]
      def transfer(self, src, dst, amt):
          if self.balances.get(src, 0) < amt:
              return None
          self.balances[src] -= amt
          self.deposit(dst, amt)
          return self.balances[src]
  b = Bank()
  b.deposit("a", 100)
  print(b.transfer("a", "b", 30), b.transfer("a", "c", 80), b.balances)
  """,
  choices=["70 None {'a': 70, 'b': 30}", "70 -10 {'a': -10, 'b': 30, 'c': 80}",
           "70 None {'a': 70, 'b': 30, 'c': 0}", "None None {'a': 100}"], answer=0,
  key="Validate first, then mutate: a failed operation must leave state untouched.",
  why="The first transfer succeeds and returns the new source balance, 70. The second asks for 80 but only 70 is available, so it returns None before touching any balance. 'c' is never created.",
  trap="Mutating before validating, which leaves half-applied state when a later check fails. Graders' hidden tests target exactly this.")

Q("IV-PRC-002", "practical", "medium", verify=True,
  code="""
  from collections import OrderedDict
  class LRU:
      def __init__(self, cap):
          self.cap, self.d = cap, OrderedDict()
      def get(self, k):
          if k not in self.d:
              return -1
          self.d.move_to_end(k)
          return self.d[k]
      def put(self, k, v):
          self.d[k] = v
          self.d.move_to_end(k)
          if len(self.d) > self.cap:
              self.d.popitem(last=False)
  c = LRU(2)
  c.put("a", 1); c.put("b", 2); c.get("a"); c.put("c", 3)
  print(list(c.d))
  """,
  choices=["['a', 'c']", "['b', 'c']", "['a', 'b']", "['c', 'a']"], answer=0,
  key="An LRU cache is an OrderedDict: move_to_end on every access, popitem(last=False) to evict the oldest.",
  why="get('a') makes 'a' the most recent, so 'b' is now the least recent. Inserting 'c' pushes the size to 3, so 'b' is evicted.",
  trap="Forgetting to refresh recency on get(), which evicts 'a' instead.")

Q("IV-PRC-003", "practical", "hard", verify=True,
  code="""
  class TTLStore:
      def __init__(self):
          self.data = {}
      def set(self, k, v, now, ttl=None):
          self.data[k] = (v, None if ttl is None else now + ttl)
      def get(self, k, now):
          if k not in self.data:
              return None
          v, exp = self.data[k]
          if exp is not None and now >= exp:
              del self.data[k]
              return None
          return v
  s = TTLStore()
  s.set("x", 1, now=0, ttl=10)
  s.set("y", 2, now=5)
  print(s.get("x", now=9), s.get("x", now=10), s.get("y", now=1000))
  """,
  choices=["1 None 2", "1 1 2", "1 None None", "None None 2"], answer=0,
  key="Pass time in as a parameter and define the expiry boundary precisely: here, a key is dead at now >= expiry.",
  why="x expires at 10. At 9 it is alive; at exactly 10 it is expired and removed. y has no TTL, so it never expires.",
  trap="Calling time.time() inside the store, which makes tests flaky and boundary cases impossible to pin down.")

Q("IV-PRC-004", "practical", "medium",
  prompt="In a timed, multi-level coding assessment (each level adds features and unlocks only after the previous one passes), what usually separates candidates who finish from those who stall?",
  choices=["Choosing the most optimal algorithm from level 1",
           "Getting each level passing quickly with simple, extensible state (plain dicts, small helper methods), so later features slot in without rewrites",
           "Writing extensive docstrings before coding",
           "Building a class hierarchy with abstract base classes up front"], answer=1,
  key="These rounds reward implementation speed and code that extends cleanly, not clever algorithms.",
  why="Later levels typically add things like TTLs, history, or backup/restore to the same store. Simple data layouts and one place per operation make each extension a small diff.",
  trap="Over-engineering early, then running out of time on the last level.")

Q("IV-PRC-005", "practical", "medium", verify=True,
  code="""
  from collections import deque
  class RateLimiter:
      def __init__(self, limit, window):
          self.limit, self.window, self.hits = limit, window, deque()
      def allow(self, now):
          while self.hits and self.hits[0] <= now - self.window:
              self.hits.popleft()
          if len(self.hits) < self.limit:
              self.hits.append(now)
              return True
          return False
  r = RateLimiter(limit=2, window=10)
  print([r.allow(t) for t in [0, 1, 2, 10, 11]])
  """,
  choices=["[True, True, False, True, True]", "[True, True, False, False, True]",
           "[True, True, True, True, True]", "[True, False, False, True, False]"], answer=0,
  key="A sliding-window limiter keeps recent timestamps in a deque and drops those that have fallen out of the window.",
  why="At t=2 there are already two hits, so it is refused. At t=10, the hit at 0 is out of the window (0 <= 10 - 10), so it is allowed. At t=11, the hit at 1 drops out, so it is allowed too.",
  trap="Off-by-one on the window edge (< vs <=). State the convention out loud in the interview.")

Q("IV-PRC-006", "practical", "hard", verify=True,
  code="""
  from collections import deque
  links = {"a": ["b", "c"], "b": ["a", "d"], "c": ["d"], "d": ["e"], "e": []}
  def crawl(start, max_depth):
      seen, order = {start}, []
      q = deque([(start, 0)])
      while q:
          url, d = q.popleft()
          order.append(url)
          if d == max_depth:
              continue
          for nxt in links[url]:
              if nxt not in seen:
                  seen.add(nxt)
                  q.append((nxt, d + 1))
      return order
  print(crawl("a", 2))
  """,
  choices=["['a', 'b', 'c', 'd']", "['a', 'b', 'c', 'd', 'e']", "['a', 'b', 'd', 'c']", "['a', 'b', 'c', 'd', 'd']"], answer=0,
  key="BFS crawl: mark a URL as seen when it is enqueued, and track depth alongside each URL.",
  why="a is at depth 0, b and c at depth 1, and d at depth 2. d is at max depth, so e is never enqueued. Marking on enqueue stops c from adding d a second time.",
  trap="Marking seen when dequeued, which enqueues duplicates on graphs with many paths to the same page.")

Q("IV-PRC-007", "practical", "medium", verify=True,
  code="""
  from concurrent.futures import ThreadPoolExecutor
  import time
  def fetch(n):
      time.sleep(0.03 * (3 - n))
      return n * 10
  with ThreadPoolExecutor(max_workers=3) as ex:
      print(list(ex.map(fetch, [0, 1, 2])))
  """,
  choices=["[0, 10, 20]", "[20, 10, 0]", "[0, 20, 10]", "It depends on scheduling"], answer=0,
  key="executor.map returns results in input order, even when tasks finish out of order.",
  why="Task 2 finishes first, but map yields results matching the input positions. Use `as_completed` on submitted futures if you want completion order.",
  trap="Assuming map yields results as they complete.")

Q("IV-PRC-008", "practical", "hard", mono=True,
  prompt="You must fetch 10,000 URLs with asyncio, with at most 50 requests in flight at any moment. Which pattern does that?",
  choices=["sem = asyncio.Semaphore(50)\nasync def one(u):\n    async with sem:\n        return await fetch(u)\nawait asyncio.gather(*(one(u) for u in urls))",
           "await asyncio.gather(*(fetch(u) for u in urls))",
           "for u in urls:\n    await fetch(u)",
           "with ThreadPoolExecutor(50) as ex:\n    ex.map(fetch, urls)"], answer=0,
  key="A semaphore bounds concurrency: every task is created, but only 50 hold the semaphore at once.",
  why="Option B opens 10,000 connections at once. Option C is sequential. Option D calls an async function from threads without an event loop, so it only creates coroutine objects.",
  trap="Unbounded gather, which works in testing and then exhausts sockets or gets rate-limited in production.")

Q("IV-PRC-009", "practical", "medium", verify=True,
  code="""
  import threading
  count = 0
  lock = threading.Lock()
  def work():
      global count
      for _ in range(100000):
          with lock:
              count += 1
  ts = [threading.Thread(target=work) for _ in range(4)]
  for t in ts: t.start()
  for t in ts: t.join()
  print(count)
  """,
  choices=["400000", "100000", "A number below 400000 that varies", "RuntimeError"], answer=0,
  key="`count += 1` is a read-modify-write; a lock makes it atomic across threads.",
  why="Each of 4 threads increments 100,000 times under the lock, so no updates are lost.",
  trap="Believing the GIL makes `+=` atomic. Without the lock, updates can be lost.")

Q("IV-PRC-010", "practical", "medium",
  prompt="You must serialise a dict[str, str] into one string so that ANY keys and values, including ':' ';' and newlines, round-trip exactly. Which design is correct?",
  choices=['";".join(f"{k}:{v}" for k, v in d.items())',
           "Length-prefix every key and value, e.g. 3:abc5:hello, so the parser reads exact character counts",
           "repr(d), then eval() to load it",
           "Join with a rare separator such as '|||' and split on it"], answer=1,
  key="Delimiters break when the data can contain them; length-prefixing or escaping makes the encoding unambiguous.",
  why="With a length prefix, the parser never searches for a delimiter inside the payload. `json.dumps` also works. eval executes arbitrary code, and 'rare' separators still collide eventually.",
  trap="Delimiter-joined formats that pass the simple tests and fail the hidden edge-case tests.")

Q("IV-PRC-011", "practical", "hard", verify=True,
  code="""
  def encode(d):
      return "".join(f"{len(k)}:{k}{len(v)}:{v}" for k, v in d.items())
  def decode(s):
      out, i = {}, 0
      def read():
          nonlocal i
          j = s.index(":", i)
          n = int(s[i:j])
          val = s[j + 1:j + 1 + n]
          i = j + 1 + n
          return val
      while i < len(s):
          k = read()
          out[k] = read()
      return out
  s = encode({"a:b": "x;y", "": "1"})
  print(s, decode(s) == {"a:b": "x;y", "": "1"})
  """,
  choices=["3:a:b3:x;y0:1:1 True", "3:a:b3:x;y0:1:1 False", "a:b:x;y;:1 True", "ValueError"], answer=0,
  key="A length-prefixed codec handles empty strings and embedded delimiters.",
  why="Each field is written as <len>:<text>. The decoder finds the first ':' after the current position, reads the length, then slices exactly that many characters, so the ':' inside 'a:b' is never misread.",
  trap="Forgetting the empty-string key or value, a classic hidden test case.")

Q("IV-PRC-012", "practical", "easy",
  prompt="Your expiry logic calls `time.time()` internally and the tests are flaky. What is the cleanest fix?",
  choices=["Add time.sleep() calls to the tests",
           "Inject time: accept a `now` argument (or a clock function) so tests pass exact timestamps",
           "Round timestamps to whole seconds",
           "Retry flaky tests three times"], answer=1,
  key="Dependency injection of time (and randomness) makes behaviour deterministic and testable.",
  why="When tests control `now`, boundary cases such as 'exactly at expiry' become precise. Assessment specs often pass timestamps explicitly for this reason.",
  trap="Patching around nondeterminism instead of removing it.")

Q("IV-PRC-013", "practical", "medium", verify=True,
  prompt="This function should return the 2 most frequent words. What does it print?",
  code="""
  def top_k_words(text, k):
      counts = {}
      for w in text.lower().split():
          counts[w] = counts.get(w, 0) + 1
      return sorted(counts, key=counts.get)[:k]
  print(top_k_words("b a b c b a", 2))
  """,
  choices=["['c', 'a']", "['b', 'a']", "['a', 'b']", "['b', 'c']"], answer=0,
  key="Read the code you wrote against the spec: sorted() is ascending unless you ask otherwise.",
  why="Counts are b 3, a 2, c 1. Ascending order puts c, a, b, so the slice returns the two *least* frequent. Fix it with `reverse=True` or `Counter(...).most_common(k)`.",
  trap="Trusting a quick mental run. Always test the top and bottom of an ordering.")

Q("IV-PRC-014", "practical", "medium", verify=True,
  code="""
  def merge(iv):
      out = []
      for s, e in sorted(iv):
          if out and s <= out[-1][1]:
              out[-1][1] = max(out[-1][1], e)
          else:
              out.append([s, e])
      return out
  print(merge([(5, 8), (1, 3), (2, 4), (8, 9)]))
  """,
  choices=["[[1, 4], [5, 9]]", "[[1, 4], [5, 8], [8, 9]]", "[[1, 9]]", "[[1, 3], [2, 4], [5, 9]]"], answer=0,
  key="Merge intervals: sort by start, then extend the last interval while the next one overlaps it.",
  why="(1,3) and (2,4) merge to [1,4]. (5,8) and (8,9) touch at 8, and `<=` treats touching as overlapping, giving [5,9].",
  trap="Forgetting max(), which shrinks an interval when a contained one comes next, e.g. (1,10) then (2,3).")

Q("IV-PRC-015", "practical", "medium", verify=True,
  code="""
  import heapq
  q = []
  for seq, (t, name) in enumerate([(5, "c"), (1, "a"), (5, "b"), (3, "d")]):
      heapq.heappush(q, (t, seq, name))
  print([heapq.heappop(q)[2] for _ in range(len(q))])
  """,
  choices=["['a', 'd', 'c', 'b']", "['a', 'd', 'b', 'c']", "['c', 'a', 'b', 'd']", "TypeError"], answer=0,
  key="A task scheduler is a heap of (time, sequence, task); the sequence number breaks ties in FIFO order.",
  why="Tasks pop by time first. c and b both have time 5, so the smaller sequence (c, pushed first) wins. The tie-breaker also means Python never compares payloads such as dicts, which would raise TypeError.",
  trap="Pushing (time, task) and crashing when two tasks share a time and the tasks are not comparable.")

# ───────────────────────── DSA Patterns in Python ─────────────────────────

Q("IV-DSA-001", "dsa", "easy", verify=True,
  code="""
  def two_sum(nums, target):
      seen = {}
      for i, x in enumerate(nums):
          if target - x in seen:
              return [seen[target - x], i]
          seen[x] = i
  print(two_sum([3, 2, 4], 6))
  """,
  choices=["[1, 2]", "[0, 0]", "[0, 2]", "None"], answer=0,
  key="One-pass hash map: check for the complement before storing the current value.",
  why="At index 2 (value 4), the complement 2 is already stored at index 1. Checking before inserting stops 3 from pairing with itself.",
  trap="Inserting first, which pairs an element with itself (3 + 3 = 6 gives [0, 0]).")

Q("IV-DSA-002", "dsa", "medium", verify=True,
  code="""
  def longest(s):
      last, start, best = {}, 0, 0
      for i, ch in enumerate(s):
          if ch in last and last[ch] >= start:
              start = last[ch] + 1
          last[ch] = i
          best = max(best, i - start + 1)
      return best
  print(longest("abcabcbb"), longest("pwwkew"), longest("abba"))
  """,
  choices=["3 3 2", "3 4 2", "3 3 3", "3 3 4"], answer=0,
  key="Sliding window: move the left edge past the previous occurrence, but never backwards.",
  why="The `last[ch] >= start` guard matters for 'abba'. When the second 'a' arrives, its earlier index 0 is already left of start (2), so start must not jump back.",
  trap="Dropping that guard, which returns 3 for 'abba'.")

Q("IV-DSA-003", "dsa", "medium", verify=True,
  code="""
  def first_ge(a, x):
      lo, hi = 0, len(a)
      while lo < hi:
          mid = (lo + hi) // 2
          if a[mid] < x:
              lo = mid + 1
          else:
              hi = mid
      return lo
  print(first_ge([1, 3, 3, 5], 3), first_ge([1, 3, 3, 5], 6))
  """,
  choices=["1 4", "2 4", "1 3", "1 -1"], answer=0,
  key="Half-open binary search [lo, hi) returns the first index whose value is >= x, or len(a) if there is none.",
  why="The first 3 is at index 1. Nothing is >= 6, so it returns 4. This template also powers 'binary search on the answer' problems.",
  trap="Mixing inclusive and exclusive bounds, which causes infinite loops or off-by-one errors.")

Q("IV-DSA-004", "dsa", "medium", verify=True,
  code="""
  from collections import deque
  grid = ["..#",
          ".#.",
          "..."]
  def shortest(grid):
      R, C = len(grid), len(grid[0])
      q, dist = deque([(0, 0)]), {(0, 0): 0}
      while q:
          r, c = q.popleft()
          for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
              nr, nc = r + dr, c + dc
              if 0 <= nr < R and 0 <= nc < C and grid[nr][nc] == "." and (nr, nc) not in dist:
                  dist[(nr, nc)] = dist[(r, c)] + 1
                  q.append((nr, nc))
      return dist.get((R - 1, C - 1), -1)
  print(shortest(grid))
  """,
  choices=["4", "3", "6", "-1"], answer=0,
  key="BFS gives shortest paths on unweighted grids; the dist dict doubles as the visited set.",
  why="The route is down, down, right, right: 4 steps. The walls at (0,2) and (1,1) block the shorter-looking paths.",
  trap="Using DFS, which finds *a* path but not necessarily the shortest.")

Q("IV-DSA-005", "dsa", "medium",
  prompt="A stream has 10^9 numbers and you must keep the k = 100 largest. What is the best approach?",
  choices=["Store everything and sort: O(n log n) time, O(n) memory",
           "A min-heap of size k: push each number and pop when size exceeds k. O(n log k) time, O(k) memory",
           "A max-heap of all numbers",
           "Sorted insertion into a Python list for each number"], answer=1,
  key="To find the top-k largest, keep a min-heap of size k: its root is the smallest of the current top-k, so it is cheap to evict.",
  why="Each item costs O(log k), and memory stays at k items. `heapq.nlargest` does this internally.",
  trap="Reaching for a max-heap when the question says 'k largest'.")

Q("IV-DSA-006", "dsa", "hard", verify=True,
  code="""
  parent = list(range(5))
  def find(x):
      while parent[x] != x:
          parent[x] = parent[parent[x]]
          x = parent[x]
      return x
  def union(a, b):
      parent[find(a)] = find(b)
  for a, b in [(0, 1), (1, 2), (3, 4)]:
      union(a, b)
  print(len({find(i) for i in range(5)}), find(0) == find(2))
  """,
  choices=["2 True", "3 True", "2 False", "5 False"], answer=0,
  key="Union-find answers 'are these connected?' and counts components in near-constant amortised time.",
  why="{0, 1, 2} and {3, 4} form two components, and 0 and 2 share a root. The `parent[x] = parent[parent[x]]` line is path halving.",
  trap="Setting `parent[a] = b` instead of linking the roots, which corrupts the trees.")

Q("IV-DSA-007", "dsa", "hard", verify=True,
  code="""
  from collections import deque
  deps = {"train": ["data", "model"], "model": ["config"], "data": ["config"], "config": []}
  indeg = {k: len(v) for k, v in deps.items()}
  users = {k: [] for k in deps}
  for k, vs in deps.items():
      for v in vs:
          users[v].append(k)
  q = deque(k for k, d in indeg.items() if d == 0)
  order = []
  while q:
      n = q.popleft()
      order.append(n)
      for u in users[n]:
          indeg[u] -= 1
          if indeg[u] == 0:
              q.append(u)
  print(order)
  """,
  choices=["['config', 'model', 'data', 'train']", "['train', 'model', 'data', 'config']",
           "['config', 'data', 'model', 'train']", "['config', 'train']"], answer=0,
  key="Kahn's algorithm: repeatedly take nodes with no unmet dependencies. If fewer nodes come out than went in, there is a cycle.",
  why="config has no dependencies. Finishing it frees model and data, in the order they appear in users['config']. Once both are done, train is freed.",
  trap="Reversing the edge direction, which produces the order backwards.")

Q("IV-DSA-008", "dsa", "easy", verify=True,
  code="""
  from itertools import accumulate
  a = [2, 4, 1, 3]
  p = [0, *accumulate(a)]
  print(p, p[3] - p[1])
  """,
  choices=["[0, 2, 6, 7, 10] 5", "[2, 6, 7, 10] 5", "[0, 2, 6, 7, 10] 4", "[0, 2, 6, 7, 10] 7"], answer=0,
  key="With a leading-zero prefix array, sum(a[i:j]) == p[j] - p[i].",
  why="p[3] - p[1] = 7 - 2 = 5 = a[1] + a[2] = 4 + 1. Any range sum is answered in O(1) after O(n) setup.",
  trap="Omitting the leading 0, which leads to off-by-one range sums.")

Q("IV-DSA-009", "dsa", "medium", verify=True,
  code="""
  from functools import lru_cache
  coins = (1, 2, 5)
  @lru_cache(maxsize=None)
  def ways(amount, i=0):
      if amount == 0:
          return 1
      if amount < 0 or i == len(coins):
          return 0
      return ways(amount - coins[i], i) + ways(amount, i + 1)
  print(ways(5))
  """,
  choices=["4", "9", "3", "5"], answer=0,
  key="Indexing by coin position counts combinations, not orderings.",
  why="The ways are 5, 2+2+1, 2+1+1+1 and 1×5. The state (amount, i) means 'use coins from i onward', so each multiset is counted once.",
  trap="Recursing over all coins at every step, which counts ordered sequences (9 here).")

Q("IV-DSA-010", "dsa", "medium",
  prompt="You run a recursive DFS over a graph that is a single chain of 100,000 nodes. What happens in CPython?",
  choices=["It works; Python optimises tail calls",
           "RecursionError: the default recursion limit is about 1000 frames; use an explicit stack",
           "It silently returns partial results",
           "It is fine as long as you use lru_cache"], answer=1,
  key="Python has no tail-call optimisation and a modest recursion limit.",
  why="Convert the DFS to iterative form with a list as a stack. Raising sys.setrecursionlimit can crash the interpreter on very deep recursion.",
  trap="Writing recursive DFS for large inputs in an interview and hitting this on the hidden tests.")

Q("IV-DSA-011", "dsa", "medium", verify=True,
  code="""
  def next_greater(a):
      res, st = [-1] * len(a), []
      for i, x in enumerate(a):
          while st and a[st[-1]] < x:
              res[st.pop()] = x
          st.append(i)
      return res
  print(next_greater([2, 1, 3, 2, 4]))
  """,
  choices=["[3, 3, 4, 4, -1]", "[3, 3, 4, 4, 4]", "[-1, 3, 4, 4, -1]", "[1, 3, 2, 4, -1]"], answer=0,
  key="A monotonic stack holds indices still waiting for a greater element. Each index is pushed and popped once, so it is O(n).",
  why="When 3 arrives it resolves both 1 and 2. When 4 arrives it resolves 2 and 3. Nothing is greater than the final 4.",
  trap="Writing the O(n²) nested-loop version when the follow-up asks for linear time.")

Q("IV-DSA-012", "dsa", "easy", verify=True,
  code="""
  from collections import defaultdict
  g = defaultdict(list)
  for w in ["eat", "tea", "tan", "ate", "nat"]:
      g["".join(sorted(w))].append(w)
  print(list(g.values()))
  """,
  choices=["[['eat', 'tea', 'ate'], ['tan', 'nat']]", "[['eat', 'tea', 'tan', 'ate', 'nat']]",
           "[['aet'], ['ant']]", "[['ate', 'eat', 'tea'], ['nat', 'tan']]"], answer=0,
  key="Group by a canonical key: sorted letters identify an anagram class.",
  why="'eat', 'tea' and 'ate' all sort to 'aet'. Insertion order is preserved within each group.",
  trap="Using sorted(w) (a list) as the key, which is unhashable. Join it into a string or use a tuple.")

# ─────────────────────────────── ML Numerics ───────────────────────────────

Q("IV-NUM-001", "numerics", "medium", verify=True,
  code="""
  import math
  xs = [1000.0, 1001.0]
  try:
      e = [math.exp(x) for x in xs]
      print([v / sum(e) for v in e])
  except OverflowError:
      print("OverflowError")
  """,
  choices=["OverflowError", "[0.269, 0.731]", "[0.5, 0.5]", "[nan, nan]"], answer=0,
  key="Naive softmax overflows: exp(1000) exceeds the float range.",
  why="math.exp raises OverflowError here. NumPy or PyTorch would return inf and then nan. The fix is to subtract the max logit first.",
  trap="Assuming large logits are harmless. They are routine in un-normalised model outputs.")

Q("IV-NUM-002", "numerics", "medium", verify=True,
  code="""
  import math
  def softmax(xs):
      m = max(xs)
      e = [math.exp(x - m) for x in xs]
      s = sum(e)
      return [round(v / s, 3) for v in e]
  print(softmax([1000.0, 1001.0]))
  """,
  choices=["[0.269, 0.731]", "[0.5, 0.5]", "[0.0, 1.0]", "OverflowError"], answer=0,
  key="softmax(x) == softmax(x - c) for any constant c; choosing c = max(x) keeps exp() in range.",
  why="After shifting, the inputs are -1 and 0, giving e^-1 / (e^-1 + 1) ≈ 0.269. Only the *differences* between logits matter.",
  trap="Thinking the shift changes the result. It cancels in the ratio.")

Q("IV-NUM-003", "numerics", "hard", verify=True,
  code="""
  import math
  def logsumexp(xs):
      m = max(xs)
      return m + math.log(sum(math.exp(x - m) for x in xs))
  print(round(logsumexp([-1000.0, -1000.0]), 4))
  """,
  choices=["-999.3069", "-inf", "ValueError", "-1000.0"], answer=0,
  key="log-sum-exp with the max trick stays finite in both directions; cross-entropy is built on it.",
  why="The result is -1000 + log(2) ≈ -999.3069. The naive version computes exp(-1000) = 0.0, then log(0), which raises ValueError in math and gives -inf in NumPy.",
  trap="Computing log(softmax(x)) in two steps instead of using log_softmax or logsumexp.")

Q("IV-NUM-004", "numerics", "easy", verify=True,
  code="""
  import math
  probs = [0.7, 0.2, 0.1]
  target = 1
  print(round(-math.log(probs[target]), 3))
  """,
  choices=["1.609", "0.357", "0.2", "2.303"], answer=0,
  key="Cross-entropy for one example is -log(probability assigned to the true class).",
  why="-ln(0.2) ≈ 1.609. Only the true class's probability enters the loss directly; the others matter through normalisation.",
  trap="Using the predicted class (0.7, giving 0.357) instead of the target class.")

Q("IV-NUM-005", "numerics", "medium",
  prompt="Why does fp16 training typically need loss scaling, while bf16 usually does not?",
  choices=["bf16 has more mantissa bits than fp16",
           "fp16's narrow exponent range lets small gradients underflow to zero (and large values overflow past ~65504); bf16 keeps fp32's 8-bit exponent range at lower precision",
           "bf16 runs only on CPUs",
           "Loss scaling is needed for both equally"], answer=1,
  key="Range versus precision: fp16 has 5 exponent bits and 10 mantissa bits; bf16 has 8 exponent bits and 7 mantissa bits.",
  why="Loss scaling multiplies the loss so gradients stay representable in fp16, then unscales before the optimizer step. bf16's range matches fp32's, so underflow is rare.",
  trap="Thinking bf16 is 'more precise'. It is less precise but has far more range.")

Q("IV-NUM-006", "numerics", "hard", verify=True,
  code="""
  import struct
  f32 = lambda x: struct.unpack("f", struct.pack("f", x))[0]
  print(f32(f32(16777216.0) + 1.0))
  """,
  choices=["16777216.0", "16777217.0", "16777218.0", "inf"], answer=0,
  key="float32 has a 24-bit significand: above 2^24, consecutive integers cannot all be represented.",
  why="16777217 lies exactly halfway between two representable values and rounds to even, 16777216. This is why fp32 counters and accumulators lose small increments.",
  trap="Accumulating many small values into a large float32 sum and silently losing them.")

Q("IV-NUM-007", "numerics", "hard", verify=True,
  code="""
  xs = [1e16, 1.0, -1e16]
  total = 0.0
  for x in xs:
      total += x
  print(total, sum(xs))
  """,
  choices=["0.0 1.0", "1.0 1.0", "0.0 0.0", "1.0 0.0"], answer=0,
  key="Floating-point addition is not associative: a naive running sum loses small terms next to large ones.",
  why="1e16 + 1.0 rounds back to 1e16 (the spacing between floats there is 2), so the loop loses the 1. Since Python 3.12, built-in sum() uses compensated summation and recovers it (math.fsum is exact). GPU reductions do not, which is one reason results differ slightly across runs and hardware.",
  trap="Assuming sum() and a hand-written loop agree. Before Python 3.12 both gave 0.0.")

Q("IV-NUM-008", "numerics", "easy",
  prompt="x has shape (32, 128, 64) and b has shape (64,). What is the shape of x + b?",
  choices=["(32, 128, 64)", "(64, 32, 128)", "Error: shapes do not match", "(32, 128, 64, 64)"], answer=0,
  key="Broadcasting aligns shapes from the right; a missing or size-1 dimension stretches.",
  why="(64,) lines up with the last axis, so b is added to every (batch, position) vector. This is exactly how a bias is added.",
  trap="Aligning shapes from the left.")

Q("IV-NUM-009", "numerics", "medium",
  prompt="Q and K both have shape (B, H, T, d). What is the shape of Q @ K.transpose(-2, -1)?",
  choices=["(B, H, T, T)", "(B, H, d, d)", "(B, T, T)", "(B, H, T, d)"], answer=0,
  key="Batched matmul treats leading dimensions as batch: (T, d) @ (d, T) gives (T, T).",
  why="That is one attention score per (query, key) pair, per head, per batch element. This T × T matrix is why naive attention memory grows quadratically with sequence length.",
  trap="Transposing the wrong pair of dimensions and getting (d, d).")

Q("IV-NUM-010", "numerics", "medium",
  prompt="Which shape can be broadcast-added to an array of shape (3, 4)?",
  choices=["(3,)", "(4,)", "(4, 3)", "(2, 4)"], answer=1,
  key="Trailing dimensions must be equal or 1.",
  why="(4,) aligns with the last axis. To add a per-row value of shape (3,), reshape it to (3, 1) first.",
  trap="Expecting (3,) to align with the first axis. It aligns with the last axis and fails.")

# ────────────────────── LLM & Transformer Engineering ──────────────────────

Q("IV-LLM-001", "llm", "medium",
  prompt="For naive self-attention over a sequence of length T with model width d, how do compute and score memory scale?",
  choices=["Compute O(T·d²), memory O(T)",
           "Compute O(T²·d), memory O(T²) for the score matrix per head",
           "Compute O(T log T), memory O(T)",
           "Compute O(d³), memory O(d²)"], answer=1,
  key="Every token attends to every token: there are T² scores, each a d-dimensional dot product.",
  why="Doubling the context quadruples attention cost. FlashAttention avoids storing the T × T matrix but still does O(T²) work.",
  trap="Confusing attention's T² term with the MLP's T·d² term. Which one dominates depends on T relative to d.")

Q("IV-LLM-002", "llm", "hard",
  prompt="A model has 32 layers, 8 key/value heads (grouped-query attention), head dimension 128, and stores its KV cache in fp16. How much KV cache does one 4096-token sequence need?",
  choices=["512 MiB", "256 MiB", "1024 MiB", "128 MiB"], answer=0,
  check="print(2 * 32 * 8 * 128 * 2 * 4096 // 2**20, 'MiB')",
  key="KV bytes = 2 (K and V) × layers × kv_heads × head_dim × bytes per value × tokens.",
  why="2 × 32 × 8 × 128 × 2 bytes = 128 KiB per token, × 4096 tokens = 512 MiB. Multiply by the batch size: KV cache, not weights, often limits serving throughput.",
  trap="Forgetting the factor of 2 for K and V, or using the query-head count when the model uses grouped-query attention.")

Q("IV-LLM-003", "llm", "medium", verify=True,
  code="""
  T = 4
  mask = [[1 if j <= i else 0 for j in range(T)] for i in range(T)]
  print(sum(map(sum, mask)), mask[1])
  """,
  choices=["10 [1, 1, 0, 0]", "16 [1, 1, 1, 1]", "6 [0, 1, 0, 0]", "10 [0, 0, 1, 1]"], answer=0,
  key="A causal mask is lower-triangular: position i may attend only to positions j <= i.",
  why="There are T(T + 1)/2 = 10 allowed pairs. Row 1 can see positions 0 and 1. In practice, masked scores are set to -inf before the softmax.",
  trap="Using an upper-triangular mask, which lets tokens attend to the future and leaks the labels.")

Q("IV-LLM-004", "llm", "medium",
  prompt="Why are attention scores divided by sqrt(d_k)?",
  choices=["To make attention faster",
           "With unit-variance q and k, the dot product has variance d_k; scaling restores unit variance so the softmax does not saturate and gradients do not vanish",
           "To normalise the output to sum to 1",
           "It is required for the causal mask to work"], answer=1,
  key="Scaling keeps the logits' variance near 1, independent of head size.",
  why="Unscaled, large d_k makes the logits large, so the softmax becomes nearly one-hot and its gradient approaches zero.",
  trap="Confusing it with the softmax normalisation itself.")

Q("IV-LLM-005", "llm", "hard",
  prompt="Ignoring biases, norms and embeddings, roughly how many parameters are in one standard transformer block with d_model = 4096 and an MLP hidden size of 4·d_model?",
  choices=["≈201M", "≈67M", "≈134M", "≈805M"], answer=0,
  check="print(f'≈{round(12 * 4096**2 / 1e6)}M')",
  key="Per block: attention has 4d² (Q, K, V, O) and the MLP has 8d² (d→4d→d), so 12d² in total.",
  why="12 × 4096² ≈ 201M. A 32-layer model is then about 6.4B parameters before embeddings, which is roughly LLaMA-7B's scale.",
  trap="Counting the MLP as 4d² (one matrix) instead of 8d² (two matrices).")

Q("IV-LLM-006", "llm", "medium", verify=True,
  code="""
  import math
  def probs(logits, T):
      e = [math.exp(l / T) for l in logits]
      s = sum(e)
      return [round(v / s, 2) for v in e]
  print(probs([2.0, 1.0], 1.0), probs([2.0, 1.0], 0.1))
  """,
  choices=["[0.73, 0.27] [1.0, 0.0]", "[0.73, 0.27] [0.5, 0.5]", "[0.67, 0.33] [1.0, 0.0]", "[0.73, 0.27] [0.73, 0.27]"], answer=0,
  key="Temperature divides the logits: T < 1 sharpens toward greedy decoding, T > 1 flattens toward uniform.",
  why="At T = 0.1, the logit gap of 1 becomes 10, and e^10 ≈ 22000, so nearly all the mass goes to the top token.",
  trap="Thinking temperature changes which token ranks first. It only changes how peaked the distribution is.")

Q("IV-LLM-007", "llm", "medium", verify=True,
  code="""
  probs = {"the": 0.5, "a": 0.3, "an": 0.15, "zebra": 0.05}
  kept, total = [], 0.0
  for tok, p in sorted(probs.items(), key=lambda kv: -kv[1]):
      kept.append(tok)
      total += p
      if total >= 0.9:
          break
  print(kept)
  """,
  choices=["['the', 'a', 'an']", "['the', 'a']", "['the', 'a', 'an', 'zebra']", "['the']"], answer=0,
  key="Top-p (nucleus) sampling keeps the smallest high-probability set whose mass reaches p, then renormalises.",
  why="The cumulative mass goes 0.5, 0.8, then 0.95 ≥ 0.9, so three tokens are kept. Unlike top-k, the set size adapts to how confident the model is.",
  trap="Stopping just before crossing p, which keeps too few tokens.")

Q("IV-LLM-008", "llm", "hard", verify=True,
  code="""
  from collections import Counter
  words = [list("low"), list("lower"), list("lowest")]
  pairs = Counter()
  for w in words:
      for a, b in zip(w, w[1:]):
          pairs[a + b] += 1
  print(pairs.most_common(2))
  """,
  choices=["[('lo', 3), ('ow', 3)]", "[('ow', 3), ('lo', 3)]", "[('we', 2), ('lo', 3)]", "[('lo', 3), ('we', 2)]"], answer=0,
  key="BPE training counts adjacent symbol pairs and repeatedly merges the most frequent one.",
  why="'lo' and 'ow' each appear in all three words. Counter breaks the tie by first occurrence. A real implementation weights each word by its corpus frequency, merges the pair everywhere, and repeats.",
  trap="Counting pairs across word boundaries. BPE merges within pre-tokenised words.")

Q("IV-LLM-009", "llm", "medium",
  prompt="During autoregressive decoding, what does the KV cache avoid recomputing, and what does it cost?",
  choices=["It caches output tokens; it costs nothing",
           "It stores past keys and values so each step computes K and V only for the new token; memory grows linearly with sequence length and batch size",
           "It caches the weights on the GPU; it costs disk space",
           "It skips the attention computation entirely"], answer=1,
  key="The KV cache trades memory for compute: without it, step t recomputes K and V for all t previous tokens.",
  why="With the cache, each new token's query attends to stored keys and values. That makes decoding memory-bandwidth bound and is why paged attention exists.",
  trap="Thinking the cache removes attention cost. The new token still attends to all cached positions.")

Q("IV-LLM-010", "llm", "medium",
  prompt="The profiler shows your GPU idle between steps while the CPU decodes and augments audio. What should you try first?",
  choices=["Use a larger model so the GPU has more work",
           "Overlap loading with compute: DataLoader(num_workers>0, pin_memory=True, persistent_workers=True), prefetching, or moving heavy preprocessing offline",
           "Lower the learning rate",
           "Switch from fp16 to fp32"], answer=1,
  key="An input pipeline that is the bottleneck shows up as low GPU utilisation with busy CPU workers.",
  why="Parallel workers and pinned memory keep batches ready. Precomputing features (for example, mel spectrograms) removes repeated CPU work.",
  trap="Tuning the model when the bottleneck is the data pipeline.")

Q("IV-LLM-011", "llm", "medium",
  prompt="You want an effective batch size of 256, but only 32 fits in GPU memory. What is the correct gradient accumulation setup?",
  choices=["8 micro-batches; call optimizer.step() after each one",
           "8 micro-batches; divide each micro-batch loss by 8, call backward() each time, and step and zero the gradients once every 8",
           "Use a learning rate 8× smaller and step every micro-batch",
           "32 micro-batches of 8"], answer=1,
  key="Gradients add up across backward() calls, so scale each loss by 1/steps to reproduce the mean over the large batch.",
  why="Without the division, the gradient is 8× too large, which acts like an 8× learning rate. BatchNorm statistics still see only 32 samples, a known caveat.",
  trap="Forgetting optimizer.zero_grad() placement, or stepping on every micro-batch.")

Q("IV-LLM-012", "llm", "hard",
  prompt="An fp16 training run suddenly goes to NaN loss at step 12k. Which first checks are most informative?",
  choices=["Restart with a different random seed and hope",
           "Inspect the gradient norm and loss-scale history before the NaN, look for a learning-rate spike or bad batch, add gradient clipping, check activation maxima, and consider bf16",
           "Increase the batch size",
           "Remove the validation loop"], answer=1,
  key="NaNs usually follow an overflow or instability that is visible in the metrics just before them.",
  why="Logging gradient norms and maximum activations localises the problem. Clipping and bf16 address common causes, and replaying the offending batch tests the bad-data hypothesis.",
  trap="Changing several things at once, so you never learn the actual cause.")

Q("IV-LLM-013", "llm", "medium",
  prompt="A freshly initialised language model with a 50,000-token vocabulary should start with a cross-entropy loss of about:",
  choices=["10.82", "4.70", "0.69", "50000"], answer=0,
  check="import math; print(round(math.log(50000), 2))",
  key="At initialisation the predictions are roughly uniform, so the loss is about ln(vocab_size).",
  why="ln(50000) ≈ 10.82. A starting loss far from this suggests an initialisation, masking or label bug. It is a quick sanity check before any long run.",
  trap="Using log base 10 (4.70) instead of the natural log.")

Q("IV-LLM-014", "llm", "easy",
  prompt="A model's validation cross-entropy is 2.0 nats per token. What is its perplexity?",
  choices=["7.39", "4.0", "2.0", "100"], answer=0,
  check="import math; print(round(math.exp(2.0), 2))",
  key="Perplexity = exp(cross-entropy in nats).",
  why="e^2 ≈ 7.39, roughly 'as uncertain as choosing among about 7 equally likely tokens'. If the loss is in bits, use 2^loss instead.",
  trap="Mixing up nats and bits, or comparing perplexities across different tokenizers.")
