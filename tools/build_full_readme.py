"""Собирает все тематические файлы базы в один README-full.md.

Запуск из корня репозитория:  python tools/build_full_readme.py

Порядок тем — как в исходном README (Java Core → коллекции → многопоточность → JVM →
структуры данных → паттерны → БД → Spring → Hibernate → сети → микросервисы → брокеры),
новые темы — в конце. Практика по алгоритмам (algorithms.md с раздела «Каталог приёмов»)
и SQL стоят в самом конце, перед нетехническими вопросами (решение владельца 26.11.2026):
algorithms.md при сборке делится на две части, сам файл не меняется.
Ссылки между файлами переписываются на якоря внутри единого файла.
Править нужно тематические файлы, а README-full.md пересобирать этим скриптом.
"""
import os
import re
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = "README-full.md"

# algorithms.md делится на «теорию» (до раздела «Каталог приёмов») и «практику» (с него до конца).
# Раздел ищется по названию, номер не важен — разбиение переживёт перенумерацию.
ALGO = "algorithms.md"
ALGO_SPLIT = re.compile(r"^##\s+(\d+\.\s+)?Каталог приёмов\s*$")
ALGO_PRACTICE_TITLE = "Решение алгоритмических задач: приёмы, live coding, задачи"

# Элемент — имя файла (тема целиком) или (имя файла, "theory" | "practice").
# Части одного файла должны идти в том же порядке, что и в файле.
ORDER = [
    "java-core.md",
    "collections.md",
    "concurrency.md",
    "jvm.md",
    "kotlin.md",
    (ALGO, "theory"),
    "patterns.md",
    "databases.md",
    "spring.md",
    "hibernate.md",
    "web.md",
    "microservices.md",
    "kafka.md",
    "testing.md",
    "devops.md",
    "system-design.md",
    "ai.md",
    (ALGO, "practice"),
    "sql.md",
    "behavioral.md",
]

FENCE = re.compile(r"^\s*```")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
LINK = re.compile(r"\[([^\]]*)\]\(([^)\s]+)\)")
FILE_TEXT = re.compile(r"^[\w-]+\.md$")
NAV = re.compile(r"^\[← Оглавление\]\(README\.md\).*$")


def slug(text):
    """Якорь заголовка по правилам GitHub: нижний регистр, только буквы/цифры/пробел/-/_, пробел → -."""
    text = text.strip().lower()
    kept = [ch for ch in text if ch in " -_" or unicodedata.category(ch)[0] in "LN"]
    return "".join(kept).replace(" ", "-")


class Dedup:
    """GitHub добавляет -1, -2… к повторяющимся якорям."""

    def __init__(self):
        self.seen = {}

    def __call__(self, s):
        if s in self.seen:
            self.seen[s] += 1
            return f"{s}-{self.seen[s]}"
        self.seen[s] = 0
        return s


def iter_lines_outside_code(lines):
    in_code = False
    for i, line in enumerate(lines):
        if FENCE.match(line):
            in_code = not in_code
            yield i, line, True
            continue
        yield i, line, in_code


class Part:
    """Кусок файла [start, end), который попадает в общий документ одной темой."""

    def __init__(self, name, start, end, title=None):
        self.name, self.start, self.end = name, start, end
        self.title = title          # свой заголовок H1, если у куска его нет (вторая часть файла)
        self.anchor = None
        self.heading = None         # (текст, якорь) первого заголовка — для оглавления


def build_parts(texts):
    split = None
    for i, line, in_code in iter_lines_outside_code(texts[ALGO]):
        if not in_code and ALGO_SPLIT.match(line):
            split = i
            break
    if split is None:
        raise SystemExit(f"В {ALGO} нет раздела «Каталог приёмов» — поправьте ALGO_SPLIT в {__file__}")

    parts, last_end = [], {}
    for item in ORDER:
        if isinstance(item, str):
            part = Part(item, 0, len(texts[item]))
        elif item[1] == "theory":
            part = Part(item[0], 0, split)
        else:
            part = Part(item[0], split, len(texts[item[0]]), ALGO_PRACTICE_TITLE)
        if part.start < last_end.get(part.name, 0):
            raise SystemExit(f"Части {part.name} в ORDER идут не по порядку файла")
        last_end[part.name] = part.end
        parts.append(part)
    return parts


def main():
    names = list(dict.fromkeys(i if isinstance(i, str) else i[0] for i in ORDER))
    texts = {}
    for name in names:
        with open(os.path.join(ROOT, name), encoding="utf-8") as f:
            texts[name] = f.read().splitlines()
    parts = build_parts(texts)

    # 1. Карта якорей: (файл, якорь в файле) → якорь в общем документе
    global_dedup = Dedup()
    global_dedup("подготовка-к-собеседованию-всё-в-одном-файле")   # заголовок самого документа
    global_dedup("оглавление")
    anchor_map, first_anchor, title_of, local_dedups = {}, {}, {}, {}
    for part in parts:
        if part.title:
            part.anchor = global_dedup(slug(part.title))
            part.heading = (part.title, part.anchor)
        local_dedup = local_dedups.setdefault(part.name, Dedup())
        lines = texts[part.name][part.start:part.end]
        for _, line, in_code in iter_lines_outside_code(lines):
            m = HEADING.match(line)
            if in_code or not m:
                continue
            local = local_dedup(slug(m.group(2)))
            glob = global_dedup(slug(m.group(2)))
            anchor_map[(part.name, local)] = glob
            first_anchor.setdefault(part.name, glob)
            title_of.setdefault(part.name, m.group(2))
            if part.heading is None:
                part.anchor = glob
                part.heading = (m.group(2), glob)

    def rewrite(name, target):
        if target.startswith(("http://", "https://", "img/", "mailto:")):
            return target
        path, _, frag = target.partition("#")
        ref = os.path.normpath(path) if path else name
        if ref not in texts:
            return target                       # файл вне сборки (README.md, my-questions) — ссылка как есть
        if not frag:
            return "#" + first_anchor[ref]
        mapped = anchor_map.get((ref, frag))
        if mapped is None:
            raise SystemExit(f"Битая ссылка в {name}: {target}")
        return "#" + mapped

    def relink(name, text, target):
        # «[sql.md](sql.md#...)» внутри единого файла читается странно — подставляем название темы
        if FILE_TEXT.match(text) and text in title_of:
            text = title_of[text]
        return f"[{text}]({rewrite(name, target)})"

    # Ссылки между частями одного файла: «продолжение — в конце документа» и «начало темы — выше»
    part_of_file = {}
    for part in parts:
        part_of_file.setdefault(part.name, []).append(part)

    # 2. Сборка
    out = [
        "# Подготовка к собеседованию: всё в одном файле",
        "",
        "Все темы базы одним документом — в порядке исходного README; практика по алгоритмам "
        "и SQL — в конце, перед нетехническими вопросами. "
        "Файл собирается скриптом `tools/build_full_readme.py` из тематических файлов "
        "([оглавление по файлам](README.md)); правки вносить в тематические файлы и пересобирать.",
        "",
        "## Оглавление",
        "",
    ]
    out += [f"- [{title}](#{anchor})" for title, anchor in (p.heading for p in parts)]
    out.append("")

    for part in parts:
        siblings = part_of_file[part.name]
        idx = siblings.index(part)
        out += ["", "---", ""]
        if part.title:
            first = siblings[0].heading
            out += [f"# {part.title}", "", f"Продолжение темы «[{first[0]}](#{first[1]})».", ""]
        lines = texts[part.name][part.start:part.end]
        for _, line, in_code in iter_lines_outside_code(lines):
            if not in_code and NAV.match(line):
                continue
            if not in_code:
                line = LINK.sub(lambda m: relink(part.name, m.group(1), m.group(2)), line)
            out.append(line)
        if idx + 1 < len(siblings):
            nxt = siblings[idx + 1].heading
            while out and not out[-1].strip():
                out.pop()
            out += ["", f"Продолжение темы — «[{nxt[0]}](#{nxt[1]})», ближе к концу документа."]

    with open(os.path.join(ROOT, OUT), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out).rstrip() + "\n")
    print(f"{OUT}: {len(out)} строк, тем: {len(parts)}")


if __name__ == "__main__":
    main()
