"""Python question bank for Daily Drill.

Each Q(...) is one four-option question. Rules:
  * `id` is permanent. Never renumber or reuse one. A materially different
    question gets a new id; an improved explanation bumps `rev`.
  * `answer` is zero-based (0 = A ... 3 = D).
  * `verify=True` means build.py runs `code` and checks that its stdout
    (plus the exception class name, if it raises) equals the correct choice.
"""
from textwrap import dedent

TOPICS = [
    ("basics", "Basics & Types"),
    ("strings", "Strings"),
    ("lists", "Lists & Tuples"),
    ("dicts", "Dicts & Sets"),
    ("comprehensions", "Comprehensions & Iteration"),
    ("functions", "Functions & Scope"),
    ("oop", "Classes & OOP"),
    ("errors", "Exceptions & Context Managers"),
    ("generators", "Generators & Decorators"),
    ("stdlib", "Standard Library Toolkit"),
    ("internals", "Performance & Internals"),
]

QUESTIONS = []


def Q(id, topic, difficulty, choices, answer, key, why, trap, prompt=None,
      code=None, verify=False, mono=None, rev=1):
    code = dedent(code).strip("\n") if code else None
    if prompt is None:
        prompt = "What does this print?" if code else ""
    QUESTIONS.append(dict(
        id=id, revision=rev, subject="python", topic=topic,
        difficulty=difficulty, prompt=prompt, code=code, choices=choices,
        correctIndex=answer, keyIdea=key, reasoning=why, commonTrap=trap,
        verify=verify, monoChoices=bool(verify if mono is None else mono),
    ))


# ───────────────────────────── Basics & Types ─────────────────────────────

Q("PY-BAS-001", "basics", "easy", verify=True,
  code="print(7 // 2, 7 / 2, 7 % 2)",
  choices=["3 3.5 1", "3.5 3.5 1", "3 3 1", "4 3.5 1"], answer=0,
  key="`//` is floor division, `/` is true division (always float), `%` is remainder.",
  why="7 // 2 floors 3.5 down to 3. 7 / 2 gives 3.5 even though both operands are ints. 7 % 2 is the remainder, 1.",
  trap="Expecting `/` to behave like integer division, as it did in Python 2 or does in C++.")

Q("PY-BAS-002", "basics", "easy", verify=True,
  code="print(-7 // 2)",
  choices=["-3", "-4", "-3.5", "-4.0"], answer=1,
  key="Floor division rounds toward negative infinity, not toward zero.",
  why="-7 / 2 is -3.5. Flooring moves to the next lower integer, which is -4.",
  trap="Assuming truncation toward zero (-3), which is what C, C++ and Java do.")

Q("PY-BAS-003", "basics", "easy", mono=True,
  prompt="Which of these values is truthy?",
  choices=["0.0", '""', "[0]", "{}"], answer=2,
  key="Empty containers, zero and None are falsy. Any non-empty container is truthy.",
  why="`[0]` is a list with one element, so it is non-empty and truthy, even though the element itself is falsy.",
  trap="Looking at the contents (0) instead of whether the container is empty.")

Q("PY-BAS-004", "basics", "easy", verify=True,
  code="""
  a = [1, 2]
  b = [1, 2]
  print(a == b, a is b)
  """,
  choices=["True True", "True False", "False False", "False True"], answer=1,
  key="`==` compares values; `is` compares identity (same object in memory).",
  why="Two separate list literals build two distinct objects with equal contents, so == is True and `is` is False.",
  trap="Using `is` to compare values. Reserve `is` for singletons like None.")

Q("PY-BAS-005", "basics", "easy", mono=True,
  prompt="What is the idiomatic way to check whether `x` is None?",
  choices=["if x == None:", "if x is None:", "if not x:", "if x is 'None':"], answer=1,
  key="None is a singleton, so test it by identity with `is`.",
  why="`x is None` is exact and cannot be fooled by a custom `__eq__`. PEP 8 recommends it.",
  trap="`if not x:` also fires for 0, '' and [], which is a different question.")

Q("PY-BAS-006", "basics", "easy", verify=True,
  code="print(type(6 / 3))",
  choices=["<class 'int'>", "<class 'float'>", "<class 'decimal'>", "<class 'number'>"], answer=1,
  key="True division always returns a float, even when the result is whole.",
  why="6 / 3 is 2.0, a float. Use 6 // 3 if you need the int 2.",
  trap="Assuming an exact division keeps the int type.")

Q("PY-BAS-007", "basics", "medium", verify=True,
  code="print(0.1 + 0.2 == 0.3)",
  choices=["True", "False", "0.3", "TypeError"], answer=1,
  key="Floats are binary approximations; compare them with a tolerance.",
  why="0.1 + 0.2 is 0.30000000000000004 in binary floating point. Use `math.isclose(a, b)` for comparisons.",
  trap="Trusting `==` on floats. This shows up constantly in numeric and ML code.")

Q("PY-BAS-008", "basics", "easy", verify=True,
  code="""
  a, b = 1, 2
  a, b = b, a + b
  print(a, b)
  """,
  choices=["2 3", "2 4", "1 3", "2 2"], answer=0,
  key="The whole right-hand side is evaluated before any assignment happens.",
  why="The right side becomes the tuple (2, 1 + 2) = (2, 3) using the old values, then it is unpacked into a and b. This is the Fibonacci step idiom.",
  trap="Reading it as two sequential assignments, which would give 2 4.")

Q("PY-BAS-009", "basics", "medium", verify=True,
  code='print(int("08"), int(3.9), round(2.5))',
  choices=["8 3 2", "8 4 3", "8 3 3", "ValueError"], answer=0,
  key="`int()` truncates floats toward zero; `round()` uses banker's rounding (ties go to even).",
  why="int('08') parses to 8. int(3.9) truncates to 3. round(2.5) rounds the tie to the even neighbour, 2.",
  trap="Expecting round(2.5) to be 3. round(3.5) is 4, but round(2.5) is 2.")

Q("PY-BAS-010", "basics", "medium", verify=True,
  code="print(1 < 3 > 2)",
  choices=["True", "False", "TypeError", "1"], answer=0,
  key="Comparisons chain: `a < b > c` means `a < b and b > c`.",
  why="1 < 3 is True and 3 > 2 is True, so the chain is True. Chaining is also why `0 <= i < n` reads naturally.",
  trap="Evaluating left to right as (1 < 3) > 2, i.e. True > 2, which would be False.")

Q("PY-BAS-011", "basics", "medium", verify=True,
  code='print(True + True, bool("False"))',
  choices=["2 True", "2 False", "True False", "TypeError"], answer=0,
  key="bool is a subclass of int (True == 1). Any non-empty string is truthy.",
  why="True + True is 1 + 1 = 2. The string 'False' is non-empty, so bool('False') is True.",
  trap="Thinking bool() parses the text. Use `s == 'True'` or a lookup to parse strings.")

Q("PY-BAS-012", "basics", "medium", verify=True,
  code='print(0 or "" or [] or "end", 3 and 0 and 5)',
  choices=["end 0", "True False", "end 5", "True 0"], answer=0,
  key="`or` returns the first truthy operand; `and` returns the first falsy one. Both return operands, not booleans.",
  why="The `or` chain skips 0, '' and [] and returns 'end'. The `and` chain stops at 0, the first falsy value, and returns it.",
  trap="Expecting `and`/`or` to produce True/False. They return one of the operands.")

Q("PY-BAS-013", "basics", "medium", verify=True,
  code="print(2 ** 3 ** 2)",
  choices=["64", "512", "729", "36"], answer=1,
  key="`**` is right-associative.",
  why="It parses as 2 ** (3 ** 2) = 2 ** 9 = 512, not (2 ** 3) ** 2 = 64.",
  trap="Assuming every operator groups left to right.")

Q("PY-BAS-014", "basics", "medium", verify=True,
  code="""
  nums = [3, 8, 1, 9]
  if (n := len(nums)) > 3:
      print(f"{n} items")
  """,
  choices=["4 items", "True items", "3 items", "SyntaxError"], answer=0,
  key="The walrus operator `:=` assigns and returns a value inside an expression (Python 3.8+).",
  why="`n := len(nums)` binds n to 4 and the expression evaluates to 4, so 4 > 3 is True and the f-string prints '4 items'.",
  trap="Forgetting the parentheses. Without them, n would be bound to the comparison result.")

Q("PY-BAS-015", "basics", "easy",
  prompt="Why do scripts use `if __name__ == \"__main__\":`?",
  choices=["It makes the script run faster",
           "The block runs only when the file is executed directly, not when it is imported",
           "It is required for any Python file to run",
           "It declares the main class of the module"], answer=1,
  key="`__name__` is '__main__' for the executed script and the module name when imported.",
  why="Code under the guard (CLI parsing, training loops, tests) does not run when another module imports your functions. It also matters for multiprocessing on spawn-based platforms.",
  trap="Thinking it is mandatory boilerplate. Python runs top-level code either way.")

# ──────────────────────────────── Strings ────────────────────────────────

Q("PY-STR-001", "strings", "easy", verify=True,
  code="""
  s = "python"
  print(s[1:4], s[-1], s[::-1])
  """,
  choices=["yth n nohtyp", "pyt n nohtyp", "ytho n nohtyp", "yth p python"], answer=0,
  key="Slices are `[start:stop:step]` with stop excluded; negative indices count from the end.",
  why="s[1:4] takes indices 1, 2, 3 → 'yth'. s[-1] is the last char 'n'. A step of -1 reverses the string.",
  trap="Including the stop index, which would give 'ytho'.")

Q("PY-STR-002", "strings", "easy", verify=True,
  code="""
  s = "cat"
  s[0] = "b"
  print(s)
  """,
  choices=["bat", "cat", "TypeError", "IndexError"], answer=2,
  key="Strings are immutable; you build new strings instead of editing in place.",
  why="Item assignment on a str raises TypeError. Write `s = 'b' + s[1:]` or use `s.replace(...)`.",
  trap="Treating a string like a list of characters you can mutate.")

Q("PY-STR-003", "strings", "easy", verify=True,
  code='print("a,b,,c".split(","))',
  choices=["['a', 'b', '', 'c']", "['a', 'b', 'c']", "['a,b,,c']", "('a', 'b', '', 'c')"], answer=0,
  key="`split(sep)` keeps empty fields between consecutive separators.",
  why="Between the two commas there is an empty string, so you get four items. Calling `split()` with no argument instead splits on runs of whitespace and drops empties.",
  trap="Assuming empty pieces are dropped. That only happens with the no-argument form.")

Q("PY-STR-004", "strings", "easy", mono=True,
  prompt="`words = ['a', 'b', 'c']`. Which expression produces `'a-b-c'`?",
  choices=['words.join("-")', '"-".join(words)', '"-".split(words)', 'join("-", words)'], answer=1,
  key="`join` is a string method called on the separator, taking an iterable of strings.",
  why='"-".join(words) inserts "-" between each element. Lists have no join method.',
  trap="Calling join on the list, as in JavaScript's `arr.join('-')`.")

Q("PY-STR-005", "strings", "medium", verify=True,
  code="""
  pi = 3.14159
  print(f"{pi:.2f}|{42:05d}|{'hi':>4}")
  """,
  choices=["3.14|00042|  hi", "3.14|42000|hi  ", "3.1|00042|  hi", "3.14|42|hi"], answer=0,
  key="Format specs follow the colon: `.2f` decimals, `05d` zero-pad to width 5, `>4` right-align in width 4.",
  why="pi rounds to 3.14, 42 pads to 00042, and 'hi' is right-aligned in 4 characters, giving two leading spaces.",
  trap="Mixing up `<` (left-align) and `>` (right-align).")

Q("PY-STR-006", "strings", "easy", verify=True,
  code='print("Hello".lower().count("l"), "hello".find("z"))',
  choices=["2 -1", "2 ValueError", "1 -1", "2 None"], answer=0,
  key="`find` returns -1 when the substring is missing; `index` raises ValueError.",
  why="'hello' contains two 'l's. 'z' is not present, so find returns -1.",
  trap="Writing `if s.find(x):`, which is truthy for -1 and falsy when x is at position 0. Use `x in s`.")

Q("PY-STR-007", "strings", "medium", verify=True,
  code='print(repr("--a-b--".strip("-")))',
  choices=["'a-b'", "'ab'", "'a-b--'", "'--a-b'"], answer=0,
  key="`strip(chars)` removes those characters from both ends only, never from the middle.",
  why="Leading and trailing '-' are removed; the '-' between a and b stays.",
  trap="Expecting strip to remove every occurrence. Use `replace` for that.")

Q("PY-STR-008", "strings", "easy", verify=True,
  code='print("ab" * 3, "ba" in "abab")',
  choices=["ababab True", "ababab False", "ab3 True", "TypeError"], answer=0,
  key="`*` repeats a sequence; `in` tests for a substring.",
  why="'ab' * 3 is 'ababab'. 'ba' appears at index 1 of 'abab', so `in` is True.",
  trap="Thinking `in` on strings checks single characters only.")

Q("PY-STR-009", "strings", "medium",
  prompt="Why is `''.join(parts)` preferred over `s += piece` inside a long loop?",
  choices=["join sorts the pieces first",
           "Strings are immutable, so repeated += can copy the growing string each time (O(n²) worst case); join sizes the result once",
           "+= is not allowed on strings",
           "join automatically removes duplicates"], answer=1,
  key="Building strings incrementally can be quadratic; collect pieces in a list and join once.",
  why="Each += may allocate a new string and copy everything so far. join computes the total length, allocates once and copies each piece once.",
  trap="Assuming CPython's occasional in-place += optimisation always applies. It is not guaranteed.")

Q("PY-STR-010", "strings", "easy", verify=True,
  code='print(sorted("banana"))',
  choices=["['a', 'a', 'a', 'b', 'n', 'n']", "aaabnn", "['b', 'a', 'n']", "TypeError"], answer=0,
  key="`sorted()` accepts any iterable and always returns a new list.",
  why="Iterating a string yields characters, which sorted puts in order. Use `''.join(sorted(s))` to get a string back.",
  trap="Expecting sorted to return the same type it was given.")

Q("PY-STR-011", "strings", "medium", verify=True,
  code='print("{} {}".format(*"ab"), "%s-%d" % ("x", 7))',
  choices=["a b x-7", "ab x-7", "{} {} x-7", "a b %s-%d"], answer=0,
  key="`*` unpacks an iterable into positional arguments; `%` is the older printf-style formatting.",
  why="*'ab' passes 'a' and 'b' to format. The % operator fills %s with 'x' and %d with 7.",
  trap="Forgetting that a string is iterable and unpacks character by character.")

Q("PY-STR-012", "strings", "easy", verify=True,
  code="""
  s = "Python"
  t = s.replace("o", "0")
  print(t, s)
  """,
  choices=["Pyth0n Python", "Pyth0n Pyth0n", "Python Python", "None Python"], answer=0,
  key="String methods return new strings; the original is unchanged.",
  why="replace builds a new string bound to t. s still refers to 'Python'.",
  trap="Calling `s.replace(...)` without assigning the result and expecting s to change.")

Q("PY-STR-013", "strings", "easy", verify=True,
  code='print(ord("a"), chr(98))',
  choices=["97 b", "65 B", "1 b", "97 98"], answer=0,
  key="`ord` maps a character to its Unicode code point; `chr` is the inverse.",
  why="'a' is code point 97, so 98 is 'b'. This is handy for `ord(c) - ord('a')` letter indexing in interview problems.",
  trap="Mixing up uppercase (65 = 'A') and lowercase (97 = 'a').")

Q("PY-STR-014", "strings", "hard", verify=True,
  code='print("abc" < "abd", "Z" < "a", "10" < "9")',
  choices=["True True True", "True False False", "True True False", "False True True"], answer=0,
  key="Strings compare lexicographically by code point, character by character.",
  why="'c' < 'd'. Uppercase letters (65–90) come before lowercase (97–122). '1' < '9' at the first character, so '10' < '9'.",
  trap="Expecting numeric comparison of digit strings. Convert with int() first.")

# ───────────────────────────── Lists & Tuples ─────────────────────────────

Q("PY-LST-001", "lists", "easy", mono=True,
  prompt="Which literal creates an empty list?",
  choices=["{}", "[]", "()", "set()"], answer=1,
  key="`[]` is an empty list, `()` an empty tuple, `{}` an empty dict.",
  why="Square brackets make lists. `list()` also works.",
  trap="Using `{}` and expecting a set or list. It is a dict.")

Q("PY-LST-002", "lists", "easy", verify=True,
  code="""
  a = [1, 2]
  a.append([3, 4])
  b = [1, 2]
  b.extend([3, 4])
  print(a, b)
  """,
  choices=["[1, 2, [3, 4]] [1, 2, 3, 4]", "[1, 2, 3, 4] [1, 2, 3, 4]",
           "[1, 2, 3, 4] [1, 2, [3, 4]]", "[1, 2, [3, 4]] [1, 2, [3, 4]]"], answer=0,
  key="`append` adds one object; `extend` adds each item of an iterable.",
  why="append puts the whole list [3, 4] in as a single element. extend iterates [3, 4] and adds 3 and 4.",
  trap="Using append to concatenate lists and ending up with a nested list.")

Q("PY-LST-003", "lists", "easy", verify=True,
  code="""
  nums = [10, 20, 30, 40, 50]
  print(nums[1:3], nums[-2:], nums[::2])
  """,
  choices=["[20, 30] [40, 50] [10, 30, 50]", "[20, 30, 40] [40, 50] [10, 30, 50]",
           "[10, 20] [50] [20, 40]", "[20, 30] [50, 40] [10, 30, 50]"], answer=0,
  key="Slices exclude the stop index; `[-2:]` means the last two; `[::2]` takes every second item.",
  why="Indices 1 and 2 give [20, 30]. From index -2 to the end gives [40, 50]. Step 2 from the start gives 10, 30, 50.",
  trap="Including the stop index in the slice.")

Q("PY-LST-004", "lists", "easy", verify=True,
  code="""
  a = [1, 2, 3]
  b = a
  b.append(4)
  print(a)
  """,
  choices=["[1, 2, 3]", "[1, 2, 3, 4]", "[4, 1, 2, 3]", "None"], answer=1,
  key="Assignment binds another name to the same object; it never copies.",
  why="a and b refer to one list, so appending through b is visible through a. Use `a.copy()` or `a[:]` for a copy.",
  trap="Thinking `b = a` makes an independent copy.")

Q("PY-LST-005", "lists", "medium", verify=True,
  code="""
  grid = [[0] * 3] * 2
  grid[0][0] = 1
  print(grid)
  """,
  choices=["[[1, 0, 0], [0, 0, 0]]", "[[1, 0, 0], [1, 0, 0]]", "[[1, 1, 1], [0, 0, 0]]", "TypeError"], answer=1,
  key="Multiplying a list of lists repeats references to the same inner list.",
  why="`* 2` puts the same inner list object in both rows, so a change through one row shows in both. Build grids with `[[0] * 3 for _ in range(2)]`.",
  trap="This is the classic 2D-grid bug in DP and matrix interview problems.")

Q("PY-LST-006", "lists", "easy", verify=True,
  code="""
  nums = [3, 1, 2]
  result = nums.sort()
  print(result, nums)
  """,
  choices=["[1, 2, 3] [1, 2, 3]", "None [1, 2, 3]", "[1, 2, 3] [3, 1, 2]", "None [3, 1, 2]"], answer=1,
  key="`list.sort()` sorts in place and returns None; `sorted()` returns a new list.",
  why="Methods that mutate in place return None by convention, so result is None while nums is now sorted.",
  trap="Writing `nums = nums.sort()` and losing the list.")

Q("PY-LST-007", "lists", "medium", verify=True,
  code="""
  a = [[1, 2], [3]]
  b = a.copy()
  b[0].append(99)
  b.append([4])
  print(a)
  """,
  choices=["[[1, 2], [3]]", "[[1, 2, 99], [3]]", "[[1, 2, 99], [3], [4]]", "[[1, 2], [3], [4]]"], answer=1,
  key="A shallow copy duplicates the outer list but shares the inner objects.",
  why="b is a new outer list, so appending [4] to b does not touch a. b[0] is the same inner list as a[0], so 99 shows up in a. Use `copy.deepcopy` for full independence.",
  trap="Assuming `.copy()` or `[:]` copies nested structures.")

Q("PY-LST-008", "lists", "easy", verify=True,
  code="""
  t = (5)
  u = (5,)
  print(type(t).__name__, type(u).__name__)
  """,
  choices=["tuple tuple", "int tuple", "int int", "tuple int"], answer=1,
  key="The comma makes a tuple, not the parentheses.",
  why="(5) is just 5 in grouping parentheses. (5,) is a one-element tuple. `t = 5,` would also be a tuple.",
  trap="Forgetting the trailing comma for single-element tuples.")

Q("PY-LST-009", "lists", "medium", verify=True,
  code="""
  first, *mid, last = [1, 2, 3, 4, 5]
  print(first, mid, last)
  """,
  choices=["1 [2, 3, 4] 5", "1 (2, 3, 4) 5", "1 2 5", "ValueError"], answer=0,
  key="Starred assignment collects the leftover items into a list.",
  why="first takes 1, last takes 5, and *mid gathers everything in between as a list.",
  trap="Expecting the starred name to be a tuple. It is always a list.")

Q("PY-LST-010", "lists", "medium", verify=True,
  code="""
  nums = [2, 4, 6, 7]
  for n in nums:
      if n % 2 == 0:
          nums.remove(n)
  print(nums)
  """,
  choices=["[7]", "[4, 7]", "[2, 4, 6, 7]", "RuntimeError"], answer=1,
  key="Removing items from a list while iterating over it skips elements.",
  why="The loop uses an index. Removing 2 shifts 4 into index 0, but the loop moves on to index 1 (now 6). 6 is removed and the loop ends, leaving [4, 7]. Filter into a new list instead.",
  trap="Expecting a RuntimeError like dicts raise. Lists fail silently with wrong results.")

Q("PY-LST-011", "lists", "easy", verify=True,
  code="""
  s = [1, 2, 3]
  s.pop()
  s.insert(0, 9)
  print(s)
  """,
  choices=["[9, 1, 2]", "[9, 2, 3]", "[1, 2, 9]", "[9, 1, 2, 3]"], answer=0,
  key="`pop()` removes the last item by default; `insert(i, x)` places x before index i.",
  why="pop removes 3, leaving [1, 2]. insert(0, 9) puts 9 at the front.",
  trap="Thinking pop() removes the first item. That is pop(0).")

Q("PY-LST-012", "lists", "hard", verify=True,
  code="""
  s = [1, 2, 3]
  print(s, s.pop())
  """,
  choices=["[1, 2, 3] 3", "[1, 2] 3", "[1, 2] [3]", "[1, 2, 3] [1, 2]"], answer=1,
  key="All arguments are evaluated before the function runs, and a list argument is a reference.",
  why="print receives a reference to s, then s.pop() runs and removes 3. When print finally formats s, the list is already [1, 2].",
  trap="Assuming the first argument is snapshotted before the second is evaluated.")

Q("PY-LST-013", "lists", "easy", verify=True,
  code="print([1, 2] * 2, [1, 2] + [3])",
  choices=["[1, 2, 1, 2] [1, 2, 3]", "[2, 4] [1, 2, 3]", "[2, 4] [4, 5]", "[[1, 2], [1, 2]] [1, 2, [3]]"], answer=0,
  key="On lists, `*` repeats and `+` concatenates. They are not element-wise math.",
  why="Sequence operators work on the list as a whole. Element-wise arithmetic needs a comprehension or NumPy.",
  trap="Bringing NumPy intuition to plain lists.")

Q("PY-LST-014", "lists", "medium", verify=True,
  code="""
  t = ([1], 2)
  t[0].append(3)
  print(t)
  """,
  choices=["([1], 2)", "([1, 3], 2)", "TypeError", "([1], 2, 3)"], answer=1,
  key="A tuple cannot change which objects it holds, but those objects can be mutable.",
  why="t[0] is a list, and lists can be appended to. The tuple still holds the same list object, so nothing about the tuple itself changed.",
  trap="Believing a tuple makes everything inside it immutable. It also stays unhashable if it contains a list.")

Q("PY-LST-015", "lists", "easy", verify=True,
  code="""
  nums = [5, 1, 4]
  print(sorted(nums, reverse=True), max(nums), nums.index(4))
  """,
  choices=["[5, 4, 1] 5 2", "[1, 4, 5] 5 2", "[5, 4, 1] 5 4", "[5, 4, 1] 4 1"], answer=0,
  key="`sorted(..., reverse=True)` sorts descending; `index(x)` returns the position of x.",
  why="Descending order is [5, 4, 1]. max is 5. The value 4 sits at index 2 in the original list.",
  trap="Confusing `index(x)`, which searches for a value, with `nums[x]`, which reads a position.")

# ────────────────────────────── Dicts & Sets ──────────────────────────────

Q("PY-DCT-001", "dicts", "easy", mono=True,
  prompt="Which expression creates an empty set?",
  choices=["{}", "set()", "[]", "{,}"], answer=1,
  key="`{}` is an empty dict; an empty set needs `set()`.",
  why="Braces with key: value pairs or nothing make dicts. Non-empty set literals like {1, 2} work, but there is no empty-set literal.",
  trap="Writing `seen = {}` and later calling `seen.add(x)`, which fails on a dict.")

Q("PY-DCT-002", "dicts", "easy", verify=True,
  code="""
  d = {"a": 1}
  print(d.get("b"), d.get("b", 0))
  """,
  choices=["None 0", "KeyError", "0 0", "None None"], answer=0,
  key="`dict.get(key, default)` returns the default (None if omitted) instead of raising.",
  why="'b' is missing, so the first call returns None and the second returns the given default 0.",
  trap="Using `d[key]` for keys that may be missing.")

Q("PY-DCT-003", "dicts", "easy", verify=True,
  code="""
  d = {"a": 1}
  print(d["b"])
  """,
  choices=["None", "KeyError", "0", "IndexError"], answer=1,
  key="Square-bracket lookup of a missing key raises KeyError.",
  why="Use `in`, `.get()`, or a defaultdict when a key may be absent.",
  trap="Expecting None, as JavaScript's undefined would suggest.")

Q("PY-DCT-004", "dicts", "easy", verify=True,
  code="""
  counts = {}
  for w in "a b a c a".split():
      counts[w] = counts.get(w, 0) + 1
  print(counts)
  """,
  choices=["{'a': 3, 'b': 1, 'c': 1}", "{'a': 1, 'b': 1, 'c': 1}", "{'a': 3, 'c': 1, 'b': 1}", "KeyError"], answer=0,
  key="`d[k] = d.get(k, 0) + 1` is the plain-dict counting idiom; dicts keep insertion order.",
  why="Each word starts from 0 via get and increments. Keys appear in the order first inserted: a, b, c. `collections.Counter` does the same in one call.",
  trap="Writing `counts[w] += 1` without initialising, which raises KeyError.")

Q("PY-DCT-005", "dicts", "medium", verify=True,
  code="""
  from collections import defaultdict
  groups = defaultdict(list)
  for word in ["apple", "avocado", "banana"]:
      groups[word[0]].append(word)
  print(dict(groups))
  """,
  choices=["{'a': ['apple', 'avocado'], 'b': ['banana']}", "{'a': 'avocado', 'b': 'banana'}",
           "KeyError", "{'apple': 'a', 'avocado': 'a', 'banana': 'b'}"], answer=0,
  key="`defaultdict(factory)` creates a missing key's value by calling the factory.",
  why="The first access to groups['a'] creates an empty list, then append adds to it. This is the standard grouping idiom (e.g. group anagrams).",
  trap="Passing `list()` (an instance) instead of `list` (the factory).")

Q("PY-DCT-006", "dicts", "medium", verify=True,
  code="""
  d = {[1, 2]: "x"}
  print(d)
  """,
  choices=["{[1, 2]: 'x'}", "{(1, 2): 'x'}", "TypeError", "KeyError"], answer=2,
  key="Dict keys and set elements must be hashable; mutable built-ins like lists are not.",
  why="A list's hash could change as it mutates, which would break lookups, so lists are unhashable. Use a tuple `(1, 2)` as the key.",
  trap="Trying to memoise on a list argument. Convert it to a tuple first.")

Q("PY-DCT-007", "dicts", "easy", verify=True,
  code="""
  d = {"x": 1, "y": 2}
  for k, v in d.items():
      print(k, v)
  """,
  choices=["x 1\ny 2", "x\ny", "('x', 1)\n('y', 2)", "1\n2"], answer=0,
  key="`.items()` yields (key, value) pairs that unpack in the for loop.",
  why="Each pair is unpacked into k and v. Looping over `d` alone yields only keys.",
  trap="Writing `for k, v in d:`, which tries to unpack each key string.")

Q("PY-DCT-008", "dicts", "medium", verify=True,
  code="print({n: n * n for n in range(4) if n % 2})",
  choices=["{1: 1, 3: 9}", "{0: 0, 2: 4}", "{0: 0, 1: 1, 2: 4, 3: 9}", "[1, 9]"], answer=0,
  key="Dict comprehensions use `{key: value for ... if ...}`.",
  why="n % 2 is truthy for odd n, so only 1 and 3 are kept and mapped to their squares.",
  trap="Reading `if n % 2` as 'if even'. A non-zero remainder means odd.")

Q("PY-DCT-009", "dicts", "easy", verify=True,
  code="""
  a = {1, 2, 3}
  b = {2, 3, 4}
  print(a & b, a | b, a - b)
  """,
  choices=["{2, 3} {1, 2, 3, 4} {1}", "{1, 4} {1, 2, 3, 4} {1}", "{2, 3} {1, 2, 3, 4} {4}", "TypeError"], answer=0,
  key="`&` intersection, `|` union, `-` difference, `^` symmetric difference.",
  why="Common elements are 2 and 3. Union has all four. a - b keeps what is only in a: 1.",
  trap="Mixing up `a - b` and `b - a`.")

Q("PY-DCT-010", "dicts", "medium", verify=True,
  code="""
  d = {"a": 1, "a": 2, "b": 3}
  print(len(d), d["a"])
  """,
  choices=["3 1", "2 2", "2 1", "SyntaxError"], answer=1,
  key="Repeated keys in a dict literal are allowed; the last value wins.",
  why="The second 'a' overwrites the first, so the dict has two keys and d['a'] is 2.",
  trap="Expecting an error on duplicate keys.")

Q("PY-DCT-011", "dicts", "medium", verify=True,
  code="""
  a = {"x": 1, "y": 2}
  b = {"y": 20, "z": 30}
  print(a | b)
  """,
  choices=["{'x': 1, 'y': 20, 'z': 30}", "{'x': 1, 'y': 2, 'z': 30}", "TypeError", "{'y': 2}"], answer=0,
  key="`a | b` (Python 3.9+) merges dicts; on conflicts the right-hand value wins.",
  why="y appears in both and b's value 20 is kept. `{**a, **b}` gives the same result on older versions.",
  trap="Thinking the left side wins on conflicts.")

Q("PY-DCT-012", "dicts", "hard", verify=True,
  code="""
  d = {"a": 1, "b": 2}
  for k in d:
      d["c"] = 3
  print(d)
  """,
  choices=["{'a': 1, 'b': 2, 'c': 3}", "RuntimeError", "{'a': 1, 'b': 2}", "Infinite loop"], answer=1,
  key="Adding or removing dict keys while iterating the dict raises RuntimeError.",
  why="Python detects that the dict changed size during iteration. Iterate over `list(d)` if you must modify it.",
  trap="Assuming it behaves like the silent list case. Dicts fail loudly.")

Q("PY-DCT-013", "dicts", "medium", verify=True,
  code="""
  from collections import Counter
  c = Counter("mississippi")
  print(c.most_common(2))
  """,
  choices=["[('i', 4), ('s', 4)]", "[('s', 4), ('i', 4)]", "[('m', 1), ('i', 4)]", "{'i': 4, 's': 4}"], answer=0,
  key="`Counter.most_common(k)` returns (item, count) pairs sorted by count; ties keep first-seen order.",
  why="i and s both appear 4 times. 'i' is encountered before 's' in the string, so it is listed first.",
  trap="Expecting a dict back. most_common returns a list of tuples.")

Q("PY-DCT-014", "dicts", "medium", verify=True,
  code="""
  d = {}
  d.setdefault("k", []).append(1)
  d.setdefault("k", []).append(2)
  print(d)
  """,
  choices=["{'k': [1, 2]}", "{'k': [2]}", "{'k': [1]}", "KeyError"], answer=0,
  key="`setdefault(k, v)` inserts v only if k is missing, then returns the stored value.",
  why="The first call stores a new list and returns it. The second call finds 'k' and returns that same list, so both appends land in it.",
  trap="Thinking setdefault overwrites an existing value.")

Q("PY-DCT-015", "dicts", "easy",
  prompt="Since Python 3.7, what does the language guarantee about iterating a dict?",
  choices=["Keys come out sorted", "Keys come out in insertion order",
           "Order is random on every run", "Order is guaranteed only for string keys"], answer=1,
  key="Dicts preserve insertion order as a language guarantee from 3.7.",
  why="Updating an existing key's value keeps its position. Deleting and re-adding a key moves it to the end.",
  trap="Assuming sorted order. Use `sorted(d)` when you need that.")

Q("PY-DCT-016", "dicts", "hard", verify=True,
  code='print({1: "a", True: "b", 1.0: "c"})',
  choices=["{1: 'c'}", "{1: 'a', True: 'b', 1.0: 'c'}", "{True: 'c'}", "{1.0: 'c'}"], answer=0,
  key="Keys that compare equal and hash equal are the same key: 1 == True == 1.0.",
  why="All three collapse into one entry. The key object stays the first one inserted (1); the value is the last one assigned ('c').",
  trap="Treating True and 1 as distinct keys.")

# ──────────────────────── Comprehensions & Iteration ───────────────────────

Q("PY-CMP-001", "comprehensions", "easy", verify=True,
  code="print([x * 2 for x in range(5) if x % 2 == 0])",
  choices=["[0, 4, 8]", "[0, 2, 4, 6, 8]", "[2, 6]", "[0, 2, 4]"], answer=0,
  key="`[expr for x in iterable if cond]` filters first, then transforms.",
  why="range(5) gives 0–4. The evens are 0, 2, 4; doubling them gives 0, 4, 8.",
  trap="Applying the condition to the transformed value instead of x.")

Q("PY-CMP-002", "comprehensions", "easy", verify=True,
  code="""
  for i, ch in enumerate("ab", start=1):
      print(i, ch)
  """,
  choices=["1 a\n2 b", "0 a\n1 b", "a 1\nb 2", "(1, 'a')\n(2, 'b')"], answer=0,
  key="`enumerate(it, start=k)` yields (index, item) pairs, counting from k.",
  why="With start=1, the indices are 1 and 2. Prefer enumerate over `range(len(...))`.",
  trap="Forgetting that the index comes first in each pair.")

Q("PY-CMP-003", "comprehensions", "easy", verify=True,
  code='print(list(zip([1, 2, 3], "ab")))',
  choices=["[(1, 'a'), (2, 'b')]", "[(1, 'a'), (2, 'b'), (3, None)]", "ValueError", "[1, 'a', 2, 'b']"], answer=0,
  key="`zip` pairs items and stops at the shortest input.",
  why="'ab' has only two characters, so 3 is dropped silently. Use `zip(..., strict=True)` (3.10+) to raise instead, or `itertools.zip_longest` to pad.",
  trap="Assuming zip pads with None.")

Q("PY-CMP-004", "comprehensions", "medium", verify=True,
  code="""
  matrix = [[1, 2], [3, 4]]
  print([x for row in matrix for x in row])
  """,
  choices=["[1, 2, 3, 4]", "[[1, 2], [3, 4]]", "[1, 3, 2, 4]", "NameError"], answer=0,
  key="In a nested comprehension, the `for` clauses read in the same order as nested loops.",
  why="It means `for row in matrix:` then `for x in row:`, so it flattens row by row.",
  trap="Writing the clauses in reverse (`for x in row for row in matrix`), which raises NameError.")

Q("PY-CMP-005", "comprehensions", "medium", verify=True,
  code="""
  matrix = [[1, 2], [3, 4]]
  print([[row[i] for row in matrix] for i in range(2)])
  """,
  choices=["[[1, 3], [2, 4]]", "[[1, 2], [3, 4]]", "[1, 3, 2, 4]", "[[1, 2], [1, 2]]"], answer=0,
  key="An outer comprehension over column i with an inner one over rows builds the transpose.",
  why="For i = 0 it collects the first item of each row, [1, 3]; for i = 1, [2, 4]. `list(map(list, zip(*matrix)))` does the same.",
  trap="Confusing which comprehension is the outer loop.")

Q("PY-CMP-006", "comprehensions", "medium", verify=True,
  code="""
  nums = [1, 2, 3, 4]
  print(list(map(lambda n: n ** 2, filter(lambda n: n % 2 == 0, nums))))
  """,
  choices=["[4, 16]", "[1, 9]", "[1, 4, 9, 16]", "[2, 4]"], answer=0,
  key="`filter` keeps items where the function is truthy; `map` transforms each item.",
  why="filter keeps 2 and 4; map squares them. The comprehension `[n**2 for n in nums if n % 2 == 0]` is usually more readable.",
  trap="Forgetting map and filter are lazy iterators in Python 3, so you need list() to see values.")

Q("PY-CMP-007", "comprehensions", "medium", verify=True,
  code="""
  squares = (n * n for n in range(3))
  print(sum(squares), sum(squares))
  """,
  choices=["5 5", "5 0", "0 5", "TypeError"], answer=1,
  key="A generator can be consumed only once.",
  why="The first sum uses up 0, 1, 4 → 5. The generator is then exhausted, so the second sum sees nothing and returns 0.",
  trap="Reusing a generator as if it were a list.")

Q("PY-CMP-008", "comprehensions", "easy", verify=True,
  code="print(list(range(10, 0, -3)))",
  choices=["[10, 7, 4, 1]", "[10, 7, 4, 1, -2]", "[10, 7, 4]", "[]"], answer=0,
  key="`range(start, stop, step)` excludes stop and can count down with a negative step.",
  why="Start at 10 and subtract 3 while staying above 0: 10, 7, 4, 1.",
  trap="Writing `range(10, 0)` without a negative step, which is empty.")

Q("PY-CMP-009", "comprehensions", "easy", mono=True,
  prompt="Which expression maps each word in `words` to its length?",
  choices=["{w: len(w) for w in words}", "[w: len(w) for w in words]",
           "{len(w) for w in words}", "dict(w, len(w) for w in words)"], answer=0,
  key="Braces with `key: value` make a dict comprehension; braces with one expression make a set.",
  why="Option A builds {'cat': 3, ...}. Option C is a set of lengths. Option B is a syntax error.",
  trap="Confusing set comprehensions and dict comprehensions.")

Q("PY-CMP-010", "comprehensions", "medium", verify=True,
  code='print(["even" if n % 2 == 0 else "odd" for n in range(3)])',
  choices=["['even', 'odd', 'even']", "['even', 'even']", "['odd', 'even', 'odd']", "SyntaxError"], answer=0,
  key="An if/else that transforms goes before `for`; an `if` that filters goes after it.",
  why="`A if cond else B` is a conditional expression applied to every item, so all three values appear.",
  trap="Writing `[x for x in xs if c else y]`, which is a syntax error.")

Q("PY-CMP-011", "comprehensions", "hard", verify=True,
  code="""
  x = 10
  result = [x for x in range(3)]
  print(x)
  """,
  choices=["10", "2", "3", "NameError"], answer=0,
  key="In Python 3, a comprehension's loop variable is local to the comprehension.",
  why="The x inside the brackets does not leak, so the outer x stays 10. A plain for loop would rebind x.",
  trap="Carrying over Python 2 behaviour, where list comprehension variables leaked.")

Q("PY-CMP-012", "comprehensions", "medium", verify=True,
  code='print(all([]), any([]), any([0, "", None, 1]))',
  choices=["True False True", "False False True", "True True True", "False False False"], answer=0,
  key="`all` of an empty iterable is True; `any` of an empty iterable is False.",
  why="all asks 'is there no falsy element?', which holds for empty input. any asks 'is there a truthy element?' The last list contains 1.",
  trap="Expecting all([]) to be False, which leads to edge-case bugs in validation code.")

Q("PY-CMP-013", "comprehensions", "hard", verify=True,
  code="""
  pairs = [(1, "a"), (2, "b")]
  nums, letters = zip(*pairs)
  print(nums, letters)
  """,
  choices=["(1, 2) ('a', 'b')", "[1, 2] ['a', 'b']", "(1, 'a') (2, 'b')", "ValueError"], answer=0,
  key="`zip(*pairs)` unzips a list of pairs into tuples by position.",
  why="*pairs passes each pair as a separate argument, so zip groups the first items together and the second items together.",
  trap="Expecting lists back. zip yields tuples.")

Q("PY-CMP-014", "comprehensions", "medium", verify=True,
  code="""
  words = ["bb", "a", "ccc", "dd"]
  print(sorted(words, key=len))
  """,
  choices=["['a', 'bb', 'dd', 'ccc']", "['a', 'dd', 'bb', 'ccc']", "['a', 'bb', 'ccc', 'dd']", "['ccc', 'bb', 'dd', 'a']"], answer=0,
  key="Python's sort is stable: items with equal keys keep their original order.",
  why="'bb' and 'dd' both have length 2 and 'bb' came first, so it stays first.",
  trap="Expecting ties to be broken alphabetically automatically.")

Q("PY-CMP-015", "comprehensions", "hard", verify=True,
  code="""
  people = [("bob", 25), ("amy", 30), ("cat", 25)]
  print(sorted(people, key=lambda p: (-p[1], p[0])))
  """,
  choices=["[('amy', 30), ('bob', 25), ('cat', 25)]", "[('bob', 25), ('cat', 25), ('amy', 30)]",
           "[('amy', 30), ('cat', 25), ('bob', 25)]", "TypeError"], answer=0,
  key="A tuple key sorts by several fields; negate a number to sort that field descending.",
  why="Age is sorted descending via -age, then name ascending breaks ties. amy (30) comes first, then bob and cat.",
  trap="Using reverse=True, which would also reverse the name order.")

# ──────────────────────────── Functions & Scope ────────────────────────────

Q("PY-FUN-001", "functions", "easy", verify=True,
  code="""
  def f():
      pass
  print(f())
  """,
  choices=["None", "0", "''", "Nothing is printed"], answer=0,
  key="A function without a return statement returns None.",
  why="Falling off the end of a function returns None, and print shows it.",
  trap="Forgetting `return` in a helper and getting None downstream.")

Q("PY-FUN-002", "functions", "medium", verify=True,
  code="""
  def add(item, bucket=[]):
      bucket.append(item)
      return bucket
  print(add(1), add(2))
  """,
  choices=["[1] [2]", "[1, 2] [1, 2]", "[1] [1, 2]", "TypeError"], answer=1,
  key="Default values are evaluated once, when the function is defined, so a mutable default is shared.",
  why="Both calls append to the same list object. Both returned references point to [1, 2]. Use `bucket=None` and create the list inside.",
  trap="The most famous Python interview gotcha.")

Q("PY-FUN-003", "functions", "medium", verify=True,
  code="""
  def f(a, *args, **kwargs):
      print(a, args, kwargs)
  f(1, 2, 3, x=4)
  """,
  choices=["1 (2, 3) {'x': 4}", "1 [2, 3] {'x': 4}", "(1, 2, 3) {'x': 4}", "TypeError"], answer=0,
  key="`*args` collects extra positional arguments into a tuple; `**kwargs` collects extra keyword arguments into a dict.",
  why="1 binds to a, 2 and 3 go into args as a tuple, and x=4 goes into kwargs.",
  trap="Expecting args to be a list.")

Q("PY-FUN-004", "functions", "medium", verify=True,
  code="""
  count = 0
  def inc():
      count += 1
  inc()
  print(count)
  """,
  choices=["1", "0", "UnboundLocalError", "NameError"], answer=2,
  key="Assigning to a name anywhere in a function makes it local for the whole function.",
  why="`count += 1` assigns, so count is local to inc, and it is read before it has a value. Declare `global count`, or better, return the new value.",
  trap="Expecting the global to be read and updated automatically.")

Q("PY-FUN-005", "functions", "medium", verify=True,
  code="""
  def make_counter():
      n = 0
      def inc():
          nonlocal n
          n += 1
          return n
      return inc
  c = make_counter()
  c(); c()
  print(c())
  """,
  choices=["1", "3", "0", "UnboundLocalError"], answer=1,
  key="A closure keeps the enclosing function's variables alive; `nonlocal` lets it rebind them.",
  why="Each call increments the same n captured from make_counter, so the third call returns 3.",
  trap="Thinking n resets to 0 on every call. It resets only when make_counter is called again.")

Q("PY-FUN-006", "functions", "hard", verify=True,
  code="""
  funcs = [lambda: i for i in range(3)]
  print([f() for f in funcs])
  """,
  choices=["[0, 1, 2]", "[2, 2, 2]", "[3, 3, 3]", "NameError"], answer=1,
  key="Closures look up variables when called (late binding), not when defined.",
  why="All three lambdas refer to the same i, which is 2 when the loop finishes. Capture the current value with `lambda i=i: i`.",
  trap="Expecting each lambda to remember the i from its own iteration.")

Q("PY-FUN-007", "functions", "easy", verify=True,
  code="""
  def greet(name, greeting="Hi"):
      return f"{greeting}, {name}"
  print(greet(greeting="Yo", name="Sam"))
  """,
  choices=["Yo, Sam", "Sam, Yo", "Hi, Sam", "TypeError"], answer=0,
  key="Keyword arguments match parameters by name, so their order does not matter.",
  why="greeting gets 'Yo' and name gets 'Sam' regardless of the order they are passed in.",
  trap="Thinking keyword arguments must follow the parameter order.")

Q("PY-FUN-008", "functions", "medium", verify=True,
  code="""
  def area(w, h):
      return w * h
  dims = {"h": 3, "w": 4}
  print(area(*[2, 5]), area(**dims))
  """,
  choices=["10 12", "10 TypeError", "7 7", "[2, 5] 12"], answer=0,
  key="At a call site, `*` unpacks a sequence into positional arguments and `**` unpacks a dict into keyword arguments.",
  why="area(2, 5) is 10. area(h=3, w=4) is 12; keys are matched by name, so dict order does not matter.",
  trap="Mixing up `*` and `**` when forwarding arguments.")

Q("PY-FUN-009", "functions", "medium", verify=True,
  code="""
  def f(a, *, b):
      return a + b
  print(f(1, 2))
  """,
  choices=["3", "TypeError", "SyntaxError", "(1, 2)"], answer=1,
  key="Parameters after a bare `*` are keyword-only.",
  why="b must be passed as `b=2`. Passing it positionally raises TypeError. Libraries use this to keep call sites readable.",
  trap="Thinking `*` is a parameter that collects arguments. A bare star collects nothing.")

Q("PY-FUN-010", "functions", "easy", verify=True,
  code="""
  x = "global"
  def outer():
      x = "enclosing"
      def inner():
          return x
      return inner()
  print(outer())
  """,
  choices=["enclosing", "global", "NameError", "None"], answer=0,
  key="Name lookup follows LEGB: Local, Enclosing, Global, Built-in.",
  why="inner has no local x, so lookup moves to the enclosing function's x before reaching the global.",
  trap="Skipping the enclosing scope and going straight to the global.")

Q("PY-FUN-011", "functions", "hard", verify=True,
  code="""
  def modify(lst, num):
      lst.append(4)
      num += 1
      lst = [0]
  nums, n = [1, 2, 3], 10
  modify(nums, n)
  print(nums, n)
  """,
  choices=["[1, 2, 3, 4] 10", "[0] 11", "[1, 2, 3] 10", "[1, 2, 3, 4] 11"], answer=0,
  key="Arguments are passed by object reference: mutating the object is visible to the caller, rebinding the local name is not.",
  why="append mutates the caller's list. `num += 1` rebinds a local name to a new int. `lst = [0]` rebinds the local name only.",
  trap="Framing it as pass-by-value vs pass-by-reference. Ask instead: mutation or rebinding?")

Q("PY-FUN-012", "functions", "easy", verify=True,
  code="""
  ops = {"add": lambda a, b: a + b, "mul": lambda a, b: a * b}
  print(ops["mul"](3, 4))
  """,
  choices=["12", "7", "TypeError", "<function <lambda>>"], answer=0,
  key="Functions are first-class objects: you can store them in dicts and call them later.",
  why="ops['mul'] is a function, and (3, 4) calls it. This dispatch-table pattern replaces long if/elif chains.",
  trap="Forgetting the call parentheses and printing the function object.")

Q("PY-FUN-013", "functions", "hard", verify=True,
  code="""
  def f(a, /, b):
      return a + b
  print(f(a=1, b=2))
  """,
  choices=["3", "TypeError", "SyntaxError", "None"], answer=1,
  key="Parameters before `/` are positional-only (Python 3.8+).",
  why="a cannot be passed by name. f(1, b=2) and f(1, 2) both work.",
  trap="Confusing `/` (positional-only before it) with `*` (keyword-only after it).")

Q("PY-FUN-014", "functions", "easy", verify=True,
  code="""
  def fact(n):
      return 1 if n <= 1 else n * fact(n - 1)
  print(fact(5))
  """,
  choices=["120", "24", "15", "RecursionError"], answer=0,
  key="Recursion needs a base case plus a step that moves toward it.",
  why="5 * 4 * 3 * 2 * 1 = 120. The base case n <= 1 stops the recursion. Python's default recursion limit is about 1000 frames.",
  trap="Writing the base case as n == 1, which recurses forever for 0 or negative input.")

Q("PY-FUN-015", "functions", "medium",
  prompt="What does Python do at runtime with the hints in `def f(x: int) -> str:`?",
  choices=["Raises TypeError if x is not an int",
           "Converts x to int automatically",
           "Nothing is enforced; hints are stored in `f.__annotations__` for tools like mypy",
           "Compiles f to faster machine code"], answer=2,
  key="Type hints are metadata. The interpreter does not check them.",
  why="f('hello') runs fine at runtime. Static checkers (mypy, pyright) and libraries like pydantic read the hints.",
  trap="Assuming hints give runtime validation.")

# ────────────────────────────── Classes & OOP ──────────────────────────────

Q("PY-OOP-001", "oop", "easy",
  prompt="In `def bark(self):` inside a class, what is `self`?",
  choices=["A keyword that refers to the class",
           "The instance the method was called on, passed automatically",
           "A global variable for the current object",
           "Optional; you can omit it in the definition"], answer=1,
  key="`obj.method()` is shorthand for `Class.method(obj)`; self is that obj.",
  why="self is an ordinary first parameter. The name is a convention, not a keyword, and Python passes the instance in for you.",
  trap="Leaving self out of the definition, which gives 'takes 0 positional arguments but 1 was given'.")

Q("PY-OOP-002", "oop", "medium", verify=True,
  code="""
  class Dog:
      tricks = []
      def __init__(self, name):
          self.name = name
      def add(self, t):
          self.tricks.append(t)
  a, b = Dog("a"), Dog("b")
  a.add("sit")
  print(b.tricks)
  """,
  choices=["[]", "['sit']", "AttributeError", "None"], answer=1,
  key="A class attribute is shared by every instance; a mutable one is shared state.",
  why="tricks lives on the class, and append mutates that one list. Create per-instance state in __init__: `self.tricks = []`.",
  trap="The class-level version of the mutable default argument bug.")

Q("PY-OOP-003", "oop", "medium", verify=True,
  code="""
  class C:
      count = 0
  a, b = C(), C()
  a.count = 5
  print(a.count, b.count, C.count)
  """,
  choices=["5 0 0", "5 5 5", "5 5 0", "0 0 0"], answer=0,
  key="Assigning through an instance creates an instance attribute that shadows the class attribute.",
  why="a.count = 5 adds count to a's own __dict__. b and C still see the class attribute 0.",
  trap="Expecting the assignment to update the class. Mutation (as with a list) differs from assignment.")

Q("PY-OOP-004", "oop", "easy", verify=True,
  code="""
  class A:
      def hello(self):
          return "A"
  class B(A):
      def hello(self):
          return "B+" + super().hello()
  print(B().hello())
  """,
  choices=["B+A", "B", "A", "RecursionError"], answer=0,
  key="`super()` calls the next class's version of a method in the MRO.",
  why="B overrides hello, then delegates to A's hello through super(). The same pattern appears as `super().__init__()` in PyTorch `nn.Module` subclasses.",
  trap="Calling `self.hello()` inside the override, which recurses forever.")

Q("PY-OOP-005", "oop", "medium", verify=True,
  code="""
  class P:
      def __repr__(self):
          return "P()"
      def __str__(self):
          return "a P"
  p = P()
  print(p, [p])
  """,
  choices=["a P [P()]", "a P [a P]", "P() [P()]", "P() [a P]"], answer=0,
  key="print uses __str__; containers display their items with __repr__.",
  why="print(p) shows 'a P'. Printing the list calls repr on each element, giving P().",
  trap="Implementing only __str__ and getting unhelpful default reprs in lists and the debugger. Implement __repr__ first.")

Q("PY-OOP-006", "oop", "hard", verify=True,
  code="""
  class Bag:
      def __init__(self, items):
          self.items = items
      def __len__(self):
          return len(self.items)
  print(len(Bag([1, 2, 3])), bool(Bag([])))
  """,
  choices=["3 False", "3 True", "TypeError", "3 None"], answer=0,
  key="With no __bool__, truth testing falls back to __len__ (0 means falsy).",
  why="len calls __len__, giving 3. The empty Bag has length 0, so it is falsy. Without either method, every object is truthy.",
  trap="Assuming custom objects are always truthy.")

Q("PY-OOP-007", "oop", "medium", verify=True,
  code="""
  class Temp:
      def __init__(self, c):
          self.c = c
      @property
      def f(self):
          return self.c * 9 / 5 + 32
  t = Temp(100)
  print(t.f)
  """,
  choices=["212.0", "<bound method>", "TypeError", "212"], answer=0,
  key="@property makes a method read like an attribute; you access it without parentheses.",
  why="t.f runs the getter and returns 212.0. Writing t.f() would call the float 212.0 and raise TypeError.",
  trap="Adding call parentheses to a property.")

Q("PY-OOP-008", "oop", "medium",
  prompt="Which decorator gives a method the class (`cls`) instead of an instance, and is typically used for alternate constructors like `Date.from_string(...)`?",
  choices=["@staticmethod", "@classmethod", "@property", "@abstractmethod"], answer=1,
  key="@classmethod receives cls; @staticmethod receives neither cls nor self.",
  why="A classmethod can call `cls(...)`, so subclasses inherit constructors that build the right type. A staticmethod is a plain function namespaced in the class.",
  trap="Using @staticmethod for factories and hard-coding the class name, which breaks for subclasses.")

Q("PY-OOP-009", "oop", "hard", verify=True,
  code="""
  class A:
      def who(self): return "A"
  class B(A):
      def who(self): return "B"
  class C(A):
      def who(self): return "C"
  class D(B, C):
      pass
  print(D().who(), [k.__name__ for k in D.__mro__])
  """,
  choices=["B ['D', 'B', 'C', 'A', 'object']", "C ['D', 'C', 'B', 'A', 'object']",
           "B ['D', 'B', 'A', 'C', 'object']", "TypeError"], answer=0,
  key="The method resolution order (C3 linearisation) lists base classes left to right, with each class before its parents.",
  why="D(B, C) checks B first. A comes after both B and C because they share it as a parent.",
  trap="Assuming depth-first order (D, B, A, C), which visits A too early.")

Q("PY-OOP-010", "oop", "medium", verify=True,
  code="""
  from dataclasses import dataclass
  @dataclass
  class Point:
      x: int
      y: int = 0
  p = Point(3)
  print(p, p == Point(3, 0))
  """,
  choices=["Point(x=3, y=0) True", "<Point object> False", "Point(3, 0) True", "TypeError"], answer=0,
  key="@dataclass generates __init__, __repr__ and __eq__ from the annotated fields.",
  why="Defaults fill y = 0. The generated __eq__ compares fields, so equal values mean equal objects.",
  trap="Using a mutable default like `items: list = []`. Use `field(default_factory=list)`.")

Q("PY-OOP-011", "oop", "hard", verify=True,
  code="""
  class K:
      def __init__(self, v):
          self.v = v
      def __eq__(self, other):
          return self.v == other.v
  s = {K(1)}
  print(s)
  """,
  choices=["{<K object>}", "TypeError", "set()", "{1}"], answer=1,
  key="Defining __eq__ without __hash__ sets __hash__ to None, making instances unhashable.",
  why="Equal objects must have equal hashes, so Python removes the default identity hash. Define `__hash__` (e.g. `hash(self.v)`) or use `@dataclass(frozen=True)`.",
  trap="Adding __eq__ and then being surprised that instances fail as dict keys.")

Q("PY-OOP-012", "oop", "medium", verify=True,
  code="""
  class A: pass
  class B(A): pass
  print(isinstance(B(), A), issubclass(A, B), type(B()) == A)
  """,
  choices=["True False False", "True True False", "False False False", "True False True"], answer=0,
  key="isinstance respects inheritance; an exact `type(x) == C` check does not.",
  why="A B instance is also an A. A is not a subclass of B. type(B()) is exactly B, not A.",
  trap="Using `type(x) == C` for type checks and breaking subclasses.")

Q("PY-OOP-013", "oop", "hard",
  prompt="What does `__slots__ = ('x', 'y')` in a class body do?",
  choices=["Makes x and y private",
           "Removes the per-instance __dict__, saving memory and blocking attributes not listed",
           "Makes x and y class-level constants",
           "Makes the class thread-safe"], answer=1,
  key="__slots__ replaces the instance __dict__ with fixed storage for the listed attributes.",
  why="Each instance gets compact fixed storage, which matters when you create millions of small objects. Assigning an attribute not in __slots__ raises AttributeError.",
  trap="Treating it as an access-control feature.")

Q("PY-OOP-014", "oop", "medium", verify=True,
  code="""
  class Acct:
      def __init__(self):
          self.__bal = 100
  a = Acct()
  print(a._Acct__bal)
  print(a.__bal)
  """,
  choices=["100\nAttributeError", "100\n100", "AttributeError", "100\nNone"], answer=0,
  key="A double leading underscore triggers name mangling to `_ClassName__attr`. It is not real privacy.",
  why="Inside the class, self.__bal is stored as _Acct__bal. From outside, `a.__bal` is not mangled, so it is not found.",
  trap="Believing `__x` makes an attribute truly private. A single `_x` is the usual 'internal' convention.")

Q("PY-OOP-015", "oop", "medium", verify=True,
  code="""
  from abc import ABC, abstractmethod
  class Shape(ABC):
      @abstractmethod
      def area(self): ...
  s = Shape()
  print(s)
  """,
  choices=["<Shape object>", "TypeError", "NotImplementedError", "None"], answer=1,
  key="A class with unimplemented abstract methods cannot be instantiated.",
  why="Python raises TypeError at instantiation. A subclass that implements area can be created normally.",
  trap="Expecting the error only when the abstract method is called.")

# ─────────────────────── Exceptions & Context Managers ──────────────────────

Q("PY-ERR-001", "errors", "easy", verify=True,
  code="""
  try:
      x = 1
  except ValueError:
      print("except")
  else:
      print("else")
  finally:
      print("finally")
  """,
  choices=["else\nfinally", "finally", "except\nfinally", "else"], answer=0,
  key="`else` runs only if the try block raised nothing; `finally` always runs.",
  why="No exception occurred, so the else block runs, then finally.",
  trap="Thinking `else` belongs to the except clause.")

Q("PY-ERR-002", "errors", "medium", verify=True,
  code="""
  def f():
      try:
          return "try"
      finally:
          print("cleanup")
  print(f())
  """,
  choices=["cleanup\ntry", "try\ncleanup", "try", "cleanup"], answer=0,
  key="`finally` runs before the function actually returns.",
  why="The return value is prepared, finally prints 'cleanup', and then the caller receives 'try' and prints it.",
  trap="Assuming `return` skips the finally block.")

Q("PY-ERR-003", "errors", "medium", verify=True,
  code="""
  try:
      int("x")
  except Exception:
      print("general")
  except ValueError:
      print("value")
  """,
  choices=["general", "value", "general\nvalue", "SyntaxError"], answer=0,
  key="Except clauses are checked top to bottom, and the first match wins.",
  why="ValueError is a subclass of Exception, so the first clause catches it and the second can never run. Put specific exceptions first.",
  trap="Expecting Python to pick the most specific handler.")

Q("PY-ERR-004", "errors", "easy", verify=True,
  code='int("abc")',
  prompt="What happens when this runs?",
  choices=["TypeError", "ValueError", "SyntaxError", "KeyError"], answer=1,
  key="ValueError means the right type with an unacceptable value; TypeError means the wrong type.",
  why="'abc' is a string, which int() accepts, but its content is not a number. `int([1])` would be a TypeError.",
  trap="Mixing up ValueError and TypeError.")

Q("PY-ERR-005", "errors", "easy",
  prompt="What does `with open('f.txt') as fh:` guarantee?",
  choices=["The file is read into memory",
           "The file is closed when the block exits, even if an exception is raised",
           "The file is locked against other processes",
           "The file is created if it does not exist"], answer=1,
  key="`with` calls the object's __exit__ on every exit path.",
  why="It replaces try/finally: close(). The same pattern manages locks, database transactions and `torch.no_grad()`.",
  trap="Thinking `with` is only about files.")

Q("PY-ERR-006", "errors", "medium", verify=True,
  code="""
  class InsufficientFunds(Exception):
      pass
  try:
      raise InsufficientFunds("need 50")
  except Exception as e:
      print(type(e).__name__, e)
  """,
  choices=["InsufficientFunds need 50", "Exception need 50", "InsufficientFunds", "need 50"], answer=0,
  key="Custom exceptions subclass Exception; str(e) is the message passed in.",
  why="The handler catches the subclass through its base class. type(e) is still the custom class.",
  trap="Subclassing BaseException, which bare `except Exception` handlers will not catch.")

Q("PY-ERR-007", "errors", "hard", verify=True,
  code="""
  class Guard:
      def __enter__(self):
          print("enter")
          return self
      def __exit__(self, exc_type, exc, tb):
          print("exit", exc_type.__name__ if exc_type else None)
          return True
  with Guard():
      1 / 0
  print("after")
  """,
  choices=["enter\nexit ZeroDivisionError\nafter", "enter\nZeroDivisionError",
           "enter\nexit None\nafter", "enter\nexit ZeroDivisionError\nZeroDivisionError"], answer=0,
  key="If __exit__ returns a truthy value, the exception is suppressed.",
  why="__exit__ receives the exception details, prints them, and returns True, so execution continues after the with block.",
  trap="Returning True by accident and hiding real errors. Return None or False to let them propagate.")

Q("PY-ERR-008", "errors", "medium", verify=True,
  code="""
  from contextlib import contextmanager
  @contextmanager
  def tag(name):
      print(f"<{name}>")
      yield
      print(f"</{name}>")
  with tag("b"):
      print("hi")
  """,
  choices=["<b>\nhi\n</b>", "hi\n<b>\n</b>", "<b>\n</b>\nhi", "TypeError"], answer=0,
  key="@contextmanager turns a generator into a context manager: code before yield is setup, code after is teardown.",
  why="The with body runs at the yield point. To guarantee teardown when the body raises, wrap the yield in try/finally.",
  trap="Forgetting try/finally around the yield, so cleanup is skipped on error.")

Q("PY-ERR-009", "errors", "medium",
  prompt="Inside an `except` block, what does a bare `raise` do?",
  choices=["Raises a new generic Exception",
           "Re-raises the exception being handled, keeping its traceback",
           "Exits the program silently",
           "It is a SyntaxError"], answer=1,
  key="A bare `raise` re-raises the current exception unchanged.",
  why="Use it to log and propagate. `raise NewError(...) from e` wraps it while keeping the original as the cause.",
  trap="Writing `raise e`, which works but adds the current line to the traceback.")

Q("PY-ERR-010", "errors", "hard", verify=True,
  code="""
  def f():
      try:
          return 1
      finally:
          return 2
  print(f())
  """,
  choices=["1", "2", "1\n2", "SyntaxError"], answer=1,
  key="A `return` in finally overrides any earlier return or exception.",
  why="The finally block runs last and its return replaces the pending value 1. It would also swallow an exception, which is why linters (and Python 3.14's SyntaxWarning) flag it.",
  trap="Putting return or break in finally and hiding errors.")

Q("PY-ERR-011", "errors", "medium",
  prompt="What does the Pythonic 'EAFP' style mean?",
  choices=["Check every precondition before acting (if key in d: ...)",
           "Attempt the operation and handle the exception if it fails",
           "Use assert statements for all validation",
           "Avoid exceptions entirely for performance"], answer=1,
  key="EAFP is 'Easier to Ask Forgiveness than Permission': try, then catch.",
  why="`try: v = d[k] except KeyError: ...` avoids race conditions between a check and its use, and is idiomatic Python. The opposite style is LBYL, 'Look Before You Leap'.",
  trap="Wrapping huge blocks in try. Keep the try body small so you catch only the error you expect.")

Q("PY-ERR-012", "errors", "medium", verify=True,
  code="""
  d = {}
  try:
      d["x"]
  except KeyError as e:
      print("missing", e)
  """,
  choices=["missing 'x'", "missing x", "missing KeyError", "KeyError"], answer=0,
  key="str() of a KeyError is the repr of the missing key, so it includes quotes.",
  why="The handler catches the error and prints 'missing' followed by 'x' in quotes.",
  trap="Not knowing which key was missing. The exception message tells you.")

# ───────────────────────── Generators & Decorators ─────────────────────────

Q("PY-GEN-001", "generators", "easy", verify=True,
  code="""
  def gen():
      yield 1
      yield 2
  g = gen()
  print(next(g), next(g))
  """,
  choices=["1 2", "1 1", "[1, 2]", "<generator> <generator>"], answer=0,
  key="Each next() resumes the generator until its next yield.",
  why="The first next stops at `yield 1`, the second resumes and stops at `yield 2`.",
  trap="Thinking calling gen() runs the body. It only creates the generator object.")

Q("PY-GEN-002", "generators", "medium", verify=True,
  code="""
  g = (x for x in [1])
  next(g)
  next(g)
  """,
  prompt="What happens when this runs?",
  choices=["None", "StopIteration", "IndexError", "1"], answer=1,
  key="An exhausted iterator raises StopIteration on next().",
  why="The single value is consumed by the first next. For loops catch StopIteration for you; manual next() calls do not.",
  trap="Expecting None at the end. Use `next(g, default)` to avoid the exception.")

Q("PY-GEN-003", "generators", "medium", verify=True,
  code="""
  def gen():
      print("start")
      yield 1
  g = gen()
  print("created")
  print(next(g))
  """,
  choices=["created\nstart\n1", "start\ncreated\n1", "created\n1", "start\n1\ncreated"], answer=0,
  key="Generators are lazy: no body code runs until the first next().",
  why="gen() only builds the generator. 'start' prints when next() first runs the body.",
  trap="Placing validation inside a generator and expecting it to run at call time.")

Q("PY-GEN-004", "generators", "easy", verify=True,
  code='print(next(iter([]), "empty"))',
  choices=["empty", "StopIteration", "None", "[]"], answer=0,
  key="`next(iterator, default)` returns the default instead of raising StopIteration.",
  why="The iterator over an empty list is exhausted immediately, so the default is returned. A common idiom: `next((x for x in xs if cond(x)), None)` to find the first match.",
  trap="Calling next on a list directly. You need iter() first.")

Q("PY-GEN-005", "generators", "medium", verify=True,
  code="""
  def inner():
      yield 1
      yield 2
  def outer():
      yield 0
      yield from inner()
  print(list(outer()))
  """,
  choices=["[0, 1, 2]", "[0, <generator>]", "[0, [1, 2]]", "[1, 2, 0]"], answer=0,
  key="`yield from` delegates to a sub-iterator, yielding each of its values.",
  why="outer yields 0, then every value from inner. It replaces `for v in inner(): yield v`.",
  trap="Writing `yield inner()`, which yields the generator object itself.")

Q("PY-GEN-006", "generators", "medium", verify=True,
  code="""
  def shout(fn):
      def wrapper(*args):
          return fn(*args).upper()
      return wrapper
  @shout
  def greet(name):
      return f"hi {name}"
  print(greet("ana"))
  """,
  choices=["HI ANA", "hi ana", "HI ana", "TypeError"], answer=0,
  key="`@deco` above a def means `func = deco(func)`.",
  why="greet now refers to wrapper, which calls the original greet and uppercases its result.",
  trap="Forgetting to return wrapper from the decorator, which leaves greet set to None.")

Q("PY-GEN-007", "generators", "hard", verify=True,
  code="""
  def deco(fn):
      def wrapper(*a, **k):
          return fn(*a, **k)
      return wrapper
  @deco
  def add(a, b):
      return a + b
  print(add.__name__)
  """,
  choices=["add", "wrapper", "deco", "AttributeError"], answer=1,
  key="Without `functools.wraps`, a decorator replaces the function's name and docstring.",
  why="add is now wrapper. Put `@functools.wraps(fn)` on wrapper to copy over the metadata.",
  trap="Leaving out wraps, which confuses logging, debugging and documentation tools.")

Q("PY-GEN-008", "generators", "hard", verify=True,
  code="""
  def tag(t):
      def deco(fn):
          def wrapper():
              return f"<{t}>{fn()}</{t}>"
          return wrapper
      return deco
  @tag("b")
  @tag("i")
  def word():
      return "hi"
  print(word())
  """,
  choices=["<b><i>hi</i></b>", "<i><b>hi</b></i>", "<b>hi</b>", "TypeError"], answer=0,
  key="Stacked decorators apply bottom-up: the one nearest the def wraps first.",
  why="It is `word = tag('b')(tag('i')(word))`, so the i tag is innermost. A decorator with arguments is a factory that returns the real decorator.",
  trap="Reading the stack top-down as the order of wrapping.")

Q("PY-GEN-009", "generators", "medium", verify=True,
  code="""
  from functools import lru_cache
  calls = 0
  @lru_cache(maxsize=None)
  def fib(n):
      global calls
      calls += 1
      return n if n < 2 else fib(n - 1) + fib(n - 2)
  fib(10)
  print(calls)
  """,
  choices=["11", "177", "10", "1"], answer=0,
  key="`lru_cache` memoises results, so each distinct argument is computed once.",
  why="fib(0) through fib(10) are 11 distinct inputs, each computed once. Without the cache, fib(10) makes 177 calls. Arguments must be hashable.",
  trap="Passing lists to a cached function, which raises TypeError.")

Q("PY-GEN-010", "generators", "medium",
  prompt="Which methods make an object an iterator?",
  choices=["__iter__ and __next__", "__getitem__ and __len__",
           "__enter__ and __exit__", "__call__ and __next__"], answer=0,
  key="An iterable has __iter__; an iterator has __iter__ (returning itself) and __next__.",
  why="for loops call iter(obj) and then next() repeatedly until StopIteration. Lists are iterables; iter(list) returns an iterator.",
  trap="Confusing iterables (reusable) with iterators (single pass).")

Q("PY-GEN-011", "generators", "hard", verify=True,
  code="""
  it = iter([1, 2, 3])
  print(2 in it, list(it))
  """,
  choices=["True [3]", "True [1, 2, 3]", "True []", "False [3]"], answer=0,
  key="A membership test on an iterator consumes items up to the match.",
  why="`2 in it` reads 1 and then 2, finds a match and stops. Only 3 is left for list(it).",
  trap="Treating an iterator like a list you can scan repeatedly.")

Q("PY-GEN-012", "generators", "medium",
  prompt="Why write `sum(x * x for x in range(10**8))` rather than `sum([x * x for x in range(10**8)])`?",
  choices=["The generator version gives a more accurate result",
           "The generator yields one value at a time, so memory stays constant instead of holding 100 million items",
           "List comprehensions cannot be passed to sum",
           "There is no difference"], answer=1,
  key="Generator expressions are lazy; list comprehensions build the whole list in memory.",
  why="The list version would allocate gigabytes. Streaming matters for data pipelines and large files.",
  trap="Defaulting to lists when you only iterate once.")

Q("PY-GEN-013", "generators", "hard", verify=True,
  code="""
  def acc():
      total = 0
      while True:
          x = yield total
          total += x
  g = acc()
  next(g)
  g.send(5)
  print(g.send(10))
  """,
  choices=["15", "10", "5", "TypeError"], answer=0,
  key="`send(v)` resumes a generator and makes the paused yield expression evaluate to v.",
  why="next primes it at yield 0. send(5) sets x = 5, total = 5, and pauses at yield 5. send(10) makes total 15 and yields it.",
  trap="Calling send with a value before priming with next(), which raises TypeError.")

# ──────────────────────── Standard Library Toolkit ────────────────────────

Q("PY-STD-001", "stdlib", "medium", verify=True,
  code="""
  import heapq
  h = [5, 1, 8, 3]
  heapq.heapify(h)
  print(heapq.heappop(h), heapq.nsmallest(2, h))
  """,
  choices=["1 [3, 5]", "1 [1, 3]", "8 [1, 3]", "5 [1, 3]"], answer=0,
  key="heapq is a min-heap on a plain list: heappop returns the smallest item.",
  why="heapify is O(n). heappop removes 1. The remaining items are 3, 5, 8, so the two smallest are [3, 5].",
  trap="Expecting a max-heap.")

Q("PY-STD-002", "stdlib", "medium",
  prompt="heapq only provides a min-heap. What is the common way to get max-heap behaviour for numbers?",
  choices=["heapq.heapify(h, reverse=True)", "Push negated values and negate them again when popping",
           "Sort the list descending once", "Use heapq.maxheap()"], answer=1,
  key="Negating keys turns a min-heap into a max-heap.",
  why="The largest x has the smallest -x. For top-k problems, a min-heap of size k is also standard.",
  trap="Looking for a reverse flag. heapq has none in its public API.")

Q("PY-STD-003", "stdlib", "medium", verify=True,
  code="""
  from collections import deque
  q = deque([1, 2, 3])
  q.appendleft(0)
  q.pop()
  print(list(q), q.popleft())
  """,
  choices=["[0, 1, 2] 0", "[1, 2] 0", "[0, 1, 2, 3] 0", "[0, 1] 2"], answer=0,
  key="A deque supports O(1) appends and pops at both ends.",
  why="appendleft gives [0, 1, 2, 3] and pop removes 3. list(q) is built before popleft runs, so it shows [0, 1, 2], then popleft returns 0.",
  trap="Forgetting that print's arguments are evaluated left to right.")

Q("PY-STD-004", "stdlib", "easy",
  prompt="For a BFS queue, why use `collections.deque` instead of a list with `pop(0)`?",
  choices=["deque is sorted", "deque.popleft() is O(1), while list.pop(0) is O(n) because every item shifts",
           "Lists cannot hold tuples", "deque uses less memory per item in every case"], answer=1,
  key="Removing from the front of a list shifts every remaining element.",
  why="Over n dequeues, a list makes BFS O(n²); deque keeps it O(n).",
  trap="Using list.pop(0) in BFS, which is a common interview performance flag.")

Q("PY-STD-005", "stdlib", "medium", verify=True,
  code="""
  import bisect
  a = [1, 3, 3, 7]
  print(bisect.bisect_left(a, 3), bisect.bisect_right(a, 3))
  """,
  choices=["1 3", "1 2", "2 3", "0 4"], answer=0,
  key="bisect_left gives the first index where x could be inserted; bisect_right gives the index after any existing equal items.",
  why="The 3s occupy indices 1 and 2. Left insertion point is 1; right is 3. Their difference counts the occurrences.",
  trap="Using bisect on an unsorted list. It assumes sorted input and does not check.")

Q("PY-STD-006", "stdlib", "medium", verify=True,
  code="""
  from itertools import combinations
  print(list(combinations("abc", 2)))
  """,
  choices=["[('a', 'b'), ('a', 'c'), ('b', 'c')]", "[('a', 'b'), ('b', 'a'), ('a', 'c'), ('c', 'a'), ('b', 'c'), ('c', 'b')]",
           "['ab', 'ac', 'bc']", "[('a', 'a'), ('a', 'b'), ('b', 'b')]"], answer=0,
  key="combinations ignores order and never repeats an element; permutations cares about order.",
  why="Choosing 2 of 3 gives C(3, 2) = 3 tuples in lexicographic order of position.",
  trap="Confusing combinations with permutations.")

Q("PY-STD-007", "stdlib", "medium", verify=True,
  code="""
  from itertools import permutations
  print(len(list(permutations(range(4), 2))))
  """,
  choices=["12", "6", "16", "24"], answer=0,
  key="The number of ordered selections is P(n, k) = n! / (n - k)!.",
  why="4 choices for the first slot times 3 for the second is 12.",
  trap="Computing combinations (6) or product with repetition (16).")

Q("PY-STD-008", "stdlib", "hard", verify=True,
  code="""
  from itertools import groupby
  data = "aabbba"
  print([(k, len(list(g))) for k, g in groupby(data)])
  """,
  choices=["[('a', 2), ('b', 3), ('a', 1)]", "[('a', 3), ('b', 3)]", "[('a', 2), ('b', 3)]", "{'a': 3, 'b': 3}"], answer=0,
  key="groupby groups consecutive equal items only.",
  why="The final 'a' is separate from the first run. Sort first if you want one group per key. Unsorted, it is perfect for run-length encoding.",
  trap="Expecting SQL-style GROUP BY behaviour.")

Q("PY-STD-009", "stdlib", "medium", verify=True,
  code="""
  import copy
  a = [[1], [2]]
  b = copy.deepcopy(a)
  b[0].append(9)
  print(a)
  """,
  choices=["[[1], [2]]", "[[1, 9], [2]]", "[[1], [2], [9]]", "TypeError"], answer=0,
  key="deepcopy recursively copies nested objects, so nothing is shared.",
  why="b[0] is a brand-new inner list, so appending to it leaves a untouched.",
  trap="Using `.copy()` and expecting deep independence.")

Q("PY-STD-010", "stdlib", "medium", verify=True,
  code="""
  from collections import namedtuple
  Pt = namedtuple("Pt", "x y")
  p = Pt(1, 2)
  print(p.x + p[1], p)
  """,
  choices=["3 Pt(x=1, y=2)", "3 (1, 2)", "TypeError", "12 Pt(x=1, y=2)"], answer=0,
  key="A namedtuple is a tuple whose fields can also be accessed by name.",
  why="p.x is 1 and p[1] is 2. It is immutable and has a readable repr. Use dataclasses when you need mutability.",
  trap="Trying `p.x = 5`. Namedtuples are immutable; use `p._replace(x=5)`.")

Q("PY-STD-011", "stdlib", "medium", verify=True,
  code="""
  from functools import reduce
  print(reduce(lambda a, b: a * b, [1, 2, 3, 4]))
  """,
  choices=["24", "10", "[1, 2, 6, 24]", "TypeError"], answer=0,
  key="reduce folds an iterable into one value by applying a function cumulatively.",
  why="((1 * 2) * 3) * 4 = 24. `math.prod` does this specific case more readably.",
  trap="Confusing reduce, which returns one value, with accumulate, which returns the running values.")

Q("PY-STD-012", "stdlib", "medium", verify=True,
  code="""
  from collections import Counter
  print(Counter("aab") + Counter("bc"))
  """,
  choices=["Counter({'a': 2, 'b': 2, 'c': 1})", "Counter({'a': 2, 'b': 1, 'c': 1})", "TypeError", "{'a': 2, 'b': 2, 'c': 1}"], answer=0,
  key="Counters support +, -, & and | as multiset operations.",
  why="Counts add per key: a 2, b 1 + 1 = 2, c 1. Subtraction drops counts that reach zero or below.",
  trap="Merging counters manually with loops.")

Q("PY-STD-013", "stdlib", "easy", verify=True,
  code="""
  import math
  print(math.ceil(2.1), math.floor(-2.1), abs(-3))
  """,
  choices=["3 -3 3", "3 -2 3", "2 -3 3", "3 -2 -3"], answer=0,
  key="floor rounds toward negative infinity; ceil rounds toward positive infinity.",
  why="ceil(2.1) is 3. floor(-2.1) is -3, the next lower integer, not -2.",
  trap="Treating floor as truncation for negative numbers.")

Q("PY-STD-014", "stdlib", "medium", verify=True,
  code="""
  from itertools import accumulate
  print(list(accumulate([1, 2, 3, 4])))
  """,
  choices=["[1, 3, 6, 10]", "10", "[1, 2, 3, 4]", "[0, 1, 3, 6, 10]"], answer=0,
  key="accumulate yields running totals, i.e. prefix sums.",
  why="1, 1+2, 1+2+3, 1+2+3+4. Prefix sums power O(1) range-sum queries. Pass `initial=0` to get a leading 0.",
  trap="Expecting a leading 0 by default.")

Q("PY-STD-015", "stdlib", "medium", verify=True,
  code="""
  d = {"a": 3, "b": 7, "c": 5}
  print(sorted(d.items(), key=lambda kv: kv[1], reverse=True)[:2])
  """,
  choices=["[('b', 7), ('c', 5)]", "[('c', 5), ('b', 7)]", "['b', 'c']", "[7, 5]"], answer=0,
  key="Sort `.items()` with a key on the value to rank a dict by its values.",
  why="Sorted by value descending gives b, c, a; the slice keeps the top two pairs. `heapq.nlargest(2, d.items(), key=...)` avoids a full sort.",
  trap="Sorting `d` directly, which sorts keys only.")

# ───────────────────────── Performance & Internals ─────────────────────────

Q("PY-INT-001", "internals", "easy",
  prompt="Average time complexity of `x in my_list` versus `x in my_set`?",
  choices=["O(1) and O(1)", "O(n) and O(1)", "O(log n) and O(1)", "O(n) and O(log n)"], answer=1,
  key="Lists are scanned linearly; sets and dicts use hash tables.",
  why="Converting a list to a set once, then testing membership many times, turns O(n·m) into O(n + m).",
  trap="Running `if x in big_list` inside a loop, which hides a quadratic algorithm.")

Q("PY-INT-002", "internals", "medium", mono=True,
  prompt="Which operation on a Python list of length n is O(n)?",
  choices=["lst.append(x)", "lst.pop()", "lst.insert(0, x)", "lst[i]"], answer=2,
  key="Lists are dynamic arrays: the end is cheap, the front is expensive.",
  why="Inserting at the front shifts every element. append is amortised O(1), pop() from the end is O(1), indexing is O(1).",
  trap="Assuming every list operation is O(1).")

Q("PY-INT-003", "internals", "medium",
  prompt="In standard CPython, why might two threads fail to speed up a CPU-bound pure-Python loop?",
  choices=["Python does not support threads",
           "The Global Interpreter Lock lets only one thread execute Python bytecode at a time",
           "Threads always run on the same CPU core by OS rule",
           "Each thread copies the entire heap"], answer=1,
  key="The GIL serialises Python bytecode execution within one process.",
  why="Threads still help when work waits on I/O, or inside C extensions such as NumPy and PyTorch kernels that release the GIL. Python 3.13 offers an experimental free-threaded build without the GIL.",
  trap="Expecting linear speedups from threading pure-Python math.")

Q("PY-INT-004", "internals", "medium",
  prompt="What is the standard way to parallelise CPU-bound pure-Python work across cores?",
  choices=["threading.Thread", "asyncio.gather", "multiprocessing or concurrent.futures.ProcessPoolExecutor", "A bigger recursion limit"], answer=2,
  key="Separate processes each have their own interpreter and GIL.",
  why="Processes run truly in parallel. The cost is pickling arguments and results between processes. PyTorch's DataLoader with num_workers uses this model.",
  trap="Reaching for asyncio for CPU-bound work. It gives concurrency, not parallelism.")

Q("PY-INT-005", "internals", "easy",
  prompt="Which workload benefits most from threads in CPython?",
  choices=["Computing prime numbers in pure Python", "Downloading many URLs concurrently",
           "Sorting a large list", "Tight numeric loops"], answer=1,
  key="I/O-bound work releases the GIL while waiting, so threads can overlap the waits.",
  why="While one thread waits on the network, others run. CPU-bound loops never wait, so they contend for the GIL.",
  trap="Treating 'concurrent' and 'parallel' as the same thing.")

Q("PY-INT-006", "internals", "hard", verify=True,
  code="""
  import asyncio
  async def work(name, delay):
      await asyncio.sleep(delay)
      print(name)
  async def main():
      await asyncio.gather(work("slow", 0.05), work("fast", 0.01))
  asyncio.run(main())
  """,
  choices=["fast\nslow", "slow\nfast", "slow", "RuntimeError"], answer=0,
  key="`asyncio.gather` runs coroutines concurrently; each `await` lets the others make progress.",
  why="Both sleeps start together, and the shorter one finishes first. Total time is about 0.05s, not 0.06s.",
  trap="Calling time.sleep inside async code, which blocks the whole event loop.")

Q("PY-INT-007", "internals", "medium",
  prompt="What happens when you call an `async def` function without awaiting it?",
  choices=["It runs synchronously", "It returns a coroutine object and its body does not run",
           "It runs in a background thread", "SyntaxError"], answer=1,
  key="Calling a coroutine function only creates a coroutine; await, gather or asyncio.run executes it.",
  why="Python warns 'coroutine was never awaited' when such an object is garbage-collected.",
  trap="Forgetting await and silently skipping the work.")

Q("PY-INT-008", "internals", "hard",
  prompt="How does CPython free most objects?",
  choices=["Only via a periodic mark-and-sweep collector",
           "Reference counting frees objects as soon as their count hits zero; a cyclic GC handles reference cycles",
           "Objects are never freed until the process exits",
           "You must call `del` on every object"], answer=1,
  key="Reference counting provides deterministic cleanup; the `gc` module handles cycles.",
  why="`del x` only removes a name, decrementing the count. Cycles such as a parent and child referencing each other need the cyclic collector.",
  trap="Believing `del` immediately frees memory regardless of other references.")

Q("PY-INT-009", "internals", "easy",
  prompt="Average time complexity of looking up a key in a dict?",
  choices=["O(1)", "O(log n)", "O(n)", "O(n log n)"], answer=0,
  key="Dicts are hash tables, giving average O(1) get, set and delete.",
  why="The worst case degrades with many hash collisions, but that is rare in practice. This is why dicts are the default memo and lookup structure.",
  trap="Assuming dicts are tree-based and ordered by key, as C++ std::map is.")

Q("PY-INT-010", "internals", "medium",
  prompt="What algorithm does `sorted()` use, and what is its worst case?",
  choices=["Quicksort, O(n²)", "A stable hybrid merge/insertion sort (Timsort family), O(n log n)",
           "Heapsort, O(n log n), not stable", "Bubble sort, O(n²)"], answer=1,
  key="Python's sort is stable and O(n log n), and it is very fast on partly sorted data.",
  why="Timsort finds existing sorted runs and merges them, so nearly-sorted input approaches O(n). Stability enables multi-pass sorting.",
  trap="Assuming quicksort and its O(n²) worst case.")

Q("PY-INT-011", "internals", "medium",
  prompt="A module is imported in five different files. How many times does its top-level code run?",
  choices=["Five times", "Once; later imports reuse the cached module in sys.modules",
           "Zero times until a function is called", "Once per thread"], answer=1,
  key="Imports are cached in `sys.modules`.",
  why="The first import executes the module; later imports just bind the cached module object. `importlib.reload` forces a re-run.",
  trap="Putting expensive side effects at module top level and expecting them to rerun.")

Q("PY-INT-012", "internals", "easy",
  prompt="What does `python -m venv .venv` do?",
  choices=["Installs Python globally", "Creates an isolated environment with its own site-packages",
           "Upgrades pip", "Compiles the project"], answer=1,
  key="A virtual environment isolates a project's dependencies.",
  why="After activating it, pip installs go into .venv rather than the system Python. Conda environments solve the same problem and can also manage non-Python libraries.",
  trap="Installing everything into the base environment and creating version conflicts.")

Q("PY-INT-013", "internals", "hard", verify=True,
  code="""
  import sys
  a = []
  b = [a, a]
  print(sys.getrefcount(a) - sys.getrefcount([]))
  """,
  choices=["2", "3", "1", "0"], answer=1,
  key="Every name and every container slot holding an object adds to its reference count.",
  why="a is referenced by the name a and twice by list b, three references more than a fresh temporary list. getrefcount's own argument adds the same +1 to both sides.",
  trap="Forgetting that container slots count as references, which matters for memory leaks through caches.")
