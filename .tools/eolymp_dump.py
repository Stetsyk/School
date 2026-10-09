#!/usr/bin/env python3
"""Викачує всі задачі eolymp.com у /Users/oleksiistetsyk/Desktop/Eolymp.

  python3 eolymp_dump.py catalog     # 1) зібрати каталог (номери/теми/складність)
  python3 eolymp_dump.py fetch       # 2) викачати умови (можна перезапускати — продовжить)
  python3 eolymp_dump.py fetch 50    # тестовий прогін на 50 задачах
"""
import json, os, re, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor

SPACE = "00000000-0000-0000-0000-000000000000"
BASE = f"https://api.eolymp.com/spaces/{SPACE}"
GQL = f"{BASE}/graphql"
OUT = "/Users/oleksiistetsyk/Desktop/Eolymp"
CATALOG = os.path.join(OUT, "_catalog.json")
LOCALE = "uk"

DIFF = {1: "Дуже легка", 2: "Легка", 3: "Середня", 4: "Складна", 5: "Дуже складна"}


def curl(url, data=None, tries=4):
    cmd = ["curl", "-sL", "-m", "45", "-A", "Mozilla/5.0"]
    if data is not None:
        cmd += ["-X", "POST", "-H", "Content-Type: application/json", "--data-binary", data]
    cmd.append(url)
    for a in range(tries):
        r = subprocess.run(cmd, stdout=subprocess.PIPE)
        if r.returncode == 0 and r.stdout:
            return r.stdout
        time.sleep(1.5 * (a + 1))
    raise RuntimeError(f"не вдалося завантажити {url}")


def cj(url, data=None):
    return json.loads(curl(url, data))


# ---------------------------------------------------------------- каталог
Q = ("query($first:Int,$offset:Int,$locale:String!){problems("
     "first:$first,offset:$offset,locale:$locale,extra:[\"TITLE\"])"
     "{totalCount nodes{id number title difficulty topics(locale:$locale){name}}}}")


def catalog():
    items, offset, total = [], 0, None
    while total is None or offset < total:
        body = json.dumps({"query": Q, "variables": {
            "first": 100, "offset": offset, "locale": LOCALE}})
        d = cj(GQL, body)["data"]["problems"]
        total = d["totalCount"]
        nodes = d["nodes"]
        if not nodes:
            break
        items += nodes
        offset += len(nodes)
        print(f"\rкаталог: {len(items)}/{total}", end="", flush=True)
    os.makedirs(OUT, exist_ok=True)
    with open(CATALOG, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=1)
    print(f"\nзбережено {len(items)} задач -> {CATALOG}")


# ------------------------------------------------------------ рендер тексту
BLOCK = {"p", "heading", "li", "pre", "blockquote", "div", "tr",
         "problem-input", "problem-output"}
LABEL = {"problem-input": "\n## Вхідні дані\n",
         "problem-output": "\n## Вихідні дані\n",
         "problem-interaction": "\n## Взаємодія\n",
         "problem-notes": "\n## Примітки\n"}
SKIP = {"problem-constraints", "problem-attachments", "problem-examples"}


def flatten(node, out):
    t = node.get("type", "")
    if t in SKIP:
        return
    if t in LABEL:
        out.append(LABEL[t])
    a = node.get("attr") or {}
    if t == "span":
        out.append(a.get("text", ""))
    elif t in ("inline-math", "math", "display-math"):
        if a.get("exp"):
            out.append("$" + a["exp"] + "$")
    elif t == "image":
        out.append(f"\n![]({a.get('src', '')})\n")
    elif t == "br":
        out.append("\n")
    for c in node.get("children") or []:
        flatten(c, out)
    if t in BLOCK:
        out.append("\n")


def safe(name):
    name = re.sub(r'[/\\:*?"<>|\n\r\t]', "-", name).strip(" .")
    return name[:90] or "untitled"


# --------------------------------------------------------------- одна задача
def render(meta, path):
    num = meta["number"]          # номер на сайті (для імені файлу й посилання)
    pid = meta.get("id") or num   # внутрішній id для API — у ~1000 задач НЕ збігається з number
    p = cj(f"{BASE}/problems/{pid}").get("problem", {})

    sts = cj(f"{BASE}/problems/{pid}/statements?render=1").get("items", [])
    st = (next((s for s in sts if s.get("locale") == LOCALE), None)
          or next((s for s in sts if s.get("locale") == "en"), None)
          or (sts[0] if sts else None))
    body = ""
    if st:
        buf = []
        flatten((st.get("content") or {}).get("render") or {}, buf)
        body = re.sub(r"\n{3,}", "\n\n", "".join(buf)).strip()
        # прибрати дубльований заголовок H1
        first, _, rest = body.partition("\n")
        if first.strip() == (st.get("title") or "").strip():
            body = rest.strip()

    c = p.get("constraints") or {}
    mem = int(c.get("memoryLimitMax") or 0) // 1024 // 1024
    topics = ", ".join(t["name"] for t in meta.get("topics") or []) or "—"
    rate = p.get("acceptanceRate")

    head = [
        "---",
        f"number: {num}",
        f'title: "{(st or meta).get("title", "")}"',
        f'difficulty: {meta.get("difficulty") or ""}',
        f'difficulty_label: "{DIFF.get(meta.get("difficulty"), "—")}"',
        f'topics: "{topics}"',
        f'time_limit_ms: {c.get("cpuLimitMax") or ""}',
        f"memory_limit_mb: {mem}",
        f'acceptance_rate: {round(rate * 100, 1) if rate else ""}',
        f'url: https://eolymp.com/{LOCALE}/problems/{num}',
        "---",
        "",
        f'# {num}. {(st or meta).get("title", "")}',
        "",
        f'Складність: **{DIFF.get(meta.get("difficulty"), "—")}** · '
        f'Теми: {topics} · {c.get("cpuLimitMax") or "?"} мс · {mem} МБ'
        + (f" · прийнято {round(rate * 100, 1)}%" if rate else ""),
        "",
        "",
    ]

    ex = []
    for e in p.get("examples") or []:
        try:
            i = curl(e["inputUrl"]).decode("utf-8", "replace").rstrip()
            a = curl(e["answerUrl"]).decode("utf-8", "replace").rstrip()
            ex.append(f"\n### Приклад {e.get('index', '')}\n\n"
                      f"Вхідні дані:\n```\n{i}\n```\n\n"
                      f"Вихідні дані:\n```\n{a}\n```\n")
        except Exception:
            pass
    if ex:
        ex.insert(0, "\n## Приклади\n")

    text = "\n".join(head) + body + "\n" + "".join(ex) + "\n"
    tmp = path + ".part"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)


# ---------------------------------------------------------------- прогін
def fetch(limit=None):
    items = json.load(open(CATALOG, encoding="utf-8"))
    if limit:
        items = items[:limit]
    os.makedirs(OUT, exist_ok=True)
    existing = {f.split(" ", 1)[0] for f in os.listdir(OUT) if f.endswith(".md")}

    todo = []
    for m in items:
        n = f'{int(m["number"]):04d}'
        if n in existing:
            continue
        todo.append((m, os.path.join(OUT, f'{n} {safe(m.get("title") or "")}.md')))

    print(f"всього {len(items)}, вже є {len(items) - len(todo)}, качаємо {len(todo)}")
    done, failed, lock, t0 = [0], [], threading.Lock(), time.time()

    def work(job):
        m, path = job
        try:
            render(m, path)
        except Exception as e:
            with lock:
                failed.append((m["number"], str(e)))
        with lock:
            done[0] += 1
            d = done[0]
            if d % 10 == 0 or d == len(todo):
                el = time.time() - t0
                eta = el / d * (len(todo) - d)
                print(f"\r{d}/{len(todo)} · збоїв {len(failed)} · "
                      f"лишилось ~{int(eta // 60)}хв {int(eta % 60)}с", end="", flush=True)

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(work, todo))

    print()
    if failed:
        with open(os.path.join(OUT, "_failed.json"), "w", encoding="utf-8") as f:
            json.dump(failed, f, ensure_ascii=False, indent=1)
        print(f"не вдалося: {len(failed)} (див. _failed.json) — перезапусти, щоб добрати")
    else:
        print("готово, збоїв немає")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "fetch"
    if cmd == "catalog":
        catalog()
    else:
        fetch(int(sys.argv[2]) if len(sys.argv) > 2 else None)
