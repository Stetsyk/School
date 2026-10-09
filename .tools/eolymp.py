#!/usr/bin/env python3
"""Витягує умову задачі з eolymp.com через публічний API (без логіну).

  python3 eolymp.py 2            # укр. умова задачі #2
  python3 eolymp.py 2 en         # англійська
  python3 eolymp.py 1 2 3 14     # кілька задач підряд
"""
import json, subprocess, sys

SPACE = "00000000-0000-0000-0000-000000000000"
BASE = f"https://api.eolymp.com/spaces/{SPACE}"

def get(url):
    return subprocess.run(
        ["curl", "-sL", "-m", "30", "-A", "Mozilla/5.0", url],
        stdout=subprocess.PIPE, check=True).stdout

def gj(url):
    return json.loads(get(url))

BLOCK = {"p", "heading", "li", "pre", "problem-input", "problem-output",
         "problem-example", "problem-examples", "blockquote", "div", "tr"}
LABEL = {"problem-input": "\n## Вхідні дані\n", "problem-output": "\n## Вихідні дані\n",
         "problem-examples": "\n## Приклади\n"}

def flatten(node, out):
    t = node.get("type", "")
    if t in LABEL:
        out.append(LABEL[t])
    if t == "span":
        out.append(node.get("attr", {}).get("text", ""))
    elif t in ("inline-math", "math", "display-math"):
        exp = node.get("attr", {}).get("exp", "")
        out.append("$" + exp + "$" if exp else "")
    for c in node.get("children", []) or []:
        flatten(c, out)
    if t in BLOCK:
        out.append("\n")

def problem(num, locale="uk"):
    raw = gj(f"{BASE}/problems/{num}")
    if "problem" not in raw:
        raise RuntimeError(raw.get("message", "задачу не знайдено"))
    p = raw["problem"]
    sts = gj(f"{BASE}/problems/{num}/statements")["items"]
    st = next((s for s in sts if s.get("locale") == locale), None) or \
         next((s for s in sts if s.get("locale") == "en"), sts[0])
    full = gj(f"{BASE}/problems/{num}/statements/{st['id']}?render=1")["statement"]
    out = []
    flatten(full.get("content", {}).get("render", {}), out)
    text = "".join(out)
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")

    c = p.get("constraints", {})
    head = (f"# eolymp #{num} — {p.get('title')}\n"
            f"https://eolymp.com/uk/problems/{num}\n"
            f"складність {p.get('difficulty')} · прийнято "
            f"{round(p.get('acceptanceRate', 0) * 100, 1)}% · "
            f"час {c.get('cpuLimitMax', '?')} мс · "
            f"пам'ять {int(c.get('memoryLimitMax', 0)) // 1024 // 1024} МБ\n")

    ex = []
    for e in p.get("examples", []) or []:
        try:
            i = get(e["inputUrl"]).decode("utf-8", "replace").strip()
            a = get(e["answerUrl"]).decode("utf-8", "replace").strip()
            ex.append(f"\nПриклад {e.get('index', '')}\nвхід:\n{i}\nвихід:\n{a}\n")
        except Exception as err:
            ex.append(f"\n(приклад недоступний: {err})\n")
    return head + "\n" + text.strip() + "\n" + "".join(ex)

if __name__ == "__main__":
    args = sys.argv[1:]
    loc = "uk"
    if args and args[-1].isalpha():
        loc = args.pop()
    for n in args:
        try:
            print(problem(n, loc))
        except Exception as e:
            print(f"# eolymp #{n}: помилка — {e}")
        print("\n" + "=" * 70 + "\n")
