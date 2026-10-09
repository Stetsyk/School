# Публічний API eolymp.com

Нотатка про те, звідки беруться дані для `eolymp.py` та `eolymp_dump.py`.

## Чому не парсимо HTML

`https://eolymp.com/problems/2` — це Next.js SPA. У початковому HTML немає ні умови,
ні назви українською: лише `<title>Digits — Basecamp</title>` і лоадер. RSC-payload
(`curl -H "RSC: 1"`) теж порожній — усе довантажується на клієнті.

Умова приходить з окремого API-хоста `https://api.eolymp.com`, і — головне —
**без жодної авторизації** для публічних задач.

## База

Усі шляхи мають префікс простору (space). Публічний простір Basecamp — нульовий UUID:

```
https://api.eolymp.com/spaces/00000000-0000-0000-0000-000000000000
```

Цей рядок знайшовся прямо в HTML сторінки (`\"url\":\"https://api.eolymp.com/spaces/...\"`).

## REST-ендпоїнти

| Запит | Що віддає |
|---|---|
| `GET {BASE}/problems?size=100&offset=N` | сторінка списку задач, `size` жорстко обмежений сотнею |
| `GET {BASE}/problems/{номер}` | метадані: `title`, `difficulty`, `topics` (id), `constraints`, `acceptanceRate`, `examples` |
| `GET {BASE}/problems/{номер}/statements` | перелік умов по локалях: `az ca cs en es fr it ka pl ru sk tr uk` |
| `GET {BASE}/problems/{номер}/statements/{id}` | одна умова |

### Ключовий момент: `?render=1`

Без нього поле `content` завжди приходить порожнім — `"content":{}`. Це збиває з пантелику,
бо схоже на брак прав. Насправді рендер умови просто не вмикається за замовчуванням:

```bash
curl "{BASE}/problems/2/statements?render=1"     # усі локалі одразу, одним запитом
```

Параметр булевий (`1` / `true`). `render=HTML` поверне помилку парсингу — API так і каже:
`cannot parse "HTML" as bool`.

## GraphQL

```
POST {BASE}/graphql
Content-Type: application/json
```

Запит `ListProblems` я витяг із JS-чанків сайту. Він зручніший за REST-список, бо одразу
віддає **локалізовані назви** та **назви тем** (REST дає лише id тем, а ендпоїнта
`/topics` не існує — 404):

```graphql
query($first:Int,$offset:Int,$locale:String!){
  problems(first:$first, offset:$offset, locale:$locale, extra:["TITLE"]){
    totalCount
    nodes{ id number title difficulty topics(locale:$locale){ id name } }
  }
}
```

`first` теж обмежений сотнею. Повний каталог — 92 запити, ~4 хв.

## Структура умови

`content.render` — дерево документа, не HTML. Вузли, які трапляються:

- `document`, `heading`, `p`, `li`, `pre`, `blockquote`, `tr`
- `span` — текст лежить в `attr.text` (не в дітях!)
- `inline-math` / `math` — LaTeX у `attr.exp`
- `problem-input`, `problem-output` — секції «Вхідні/Вихідні дані»
- `problem-constraints` — ліміти в `attr` (дублює `constraints`, пропускаємо)
- `problem-examples` → `problem-example-hint` з `attr.input-ref` / `attr.output-ref`

Приклади тестів **не інлайняться** — це посилання на `eolympusercontent.com`,
їх треба довантажувати окремо.

## Шкала складності

`difficulty` — число 1..5. Підписи взяв із коду сайту
(`PROBLEM_DIFFICULTY_OPTIONS` у чанку `440788`):

| 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|
| Дуже легка | Легка | Середня | Складна | Дуже складна |

## Межі

- Публічні задачі читаються анонімно. Закриті віддають `{"code":16,"message":"unauthenticated"}`.
- Номери задач **не суцільні** — 9178 задач, але номери йдуть з пропусками
  (offset 5000 → задача №5701). Тому списком, а не циклом `for i in 1..N`.
- Хибний space-id дає `internal server error` з `reportId`, а не 404 — теж збиває з пантелику.
- 8 паралельних потоків проблем не викликали.

## Як знайшов

1. Завантажив 25 JS-чанків з `/_next/static/chunks/` зі сторінки задачі.
2. `grep` по них на `api.eolymp.com` → знайшовся згенерований SDK
   (`BookmarkService`, `SubmissionService`, `EditorService`…) з шаблонами шляхів.
3. У чанку `353399` лежали GraphQL-запити відкритим текстом.
4. Space-id і базовий URL — у вбудованому payload самої HTML-сторінки.
