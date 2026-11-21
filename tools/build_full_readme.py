"""Собирает все тематические файлы базы в один README-full.md.

Запуск из корня репозитория:  python tools/build_full_readme.py

Порядок тем — как в исходном README (Java Core → коллекции → многопоточность → JVM →
структуры данных → паттерны → БД → Spring → Hibernate → сети → микросервисы → брокеры),
новые темы — в конце. Ссылки между файлами переписываются на якоря внутри единого файла.
Править нужно тематические файлы, а README-full.md пересобирать этим скриптом.
"""
import os
import re
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = "README-full.md"

ORDER = [
    "java-core.md",
    "collections.md",
    "concurrency.md",
    "jvm.md",
    "kotlin.md",
    "algorithms.md",
    "patterns.md",
    "databases.md",
    "sql.md",
    "spring.md",
    "hibernate.md",
    "web.md",
    "microservices.md",
    "kafka.md",
    "testing.md",
    "devops.md",
    "system-design.md",
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


def main():
    texts = {}
    for name in ORDER:
        with open(os.path.join(ROOT, name), encoding="utf-8") as f:
            texts[name] = f.read().splitlines()

    # 1. Карта якорей: (файл, якорь в файле) → якорь в общем документе
    global_dedup = Dedup()
    global_dedup("подготовка-к-собеседованию-всё-в-одном-файле")   # заголовок самого документа
    global_dedup("оглавление")
    anchor_map, first_anchor, titles = {}, {}, []
    for name in ORDER:
        local_dedup = Dedup()
        for _, line, in_code in iter_lines_outside_code(texts[name]):
            m = HEADING.match(line)
            if in_code or not m:
                continue
            local = local_dedup(slug(m.group(2)))
            glob = global_dedup(slug(m.group(2)))
            anchor_map[(name, local)] = glob
            if name not in first_anchor:
                first_anchor[name] = glob
                titles.append((m.group(2), glob))

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

    title_of = {n: t for n, (t, _) in zip(ORDER, titles)}

    def relink(name, text, target):
        # «[sql.md](sql.md#...)» внутри единого файла читается странно — подставляем название темы
        if FILE_TEXT.match(text) and text in title_of:
            text = title_of[text]
        return f"[{text}]({rewrite(name, target)})"

    # 2. Сборка
    out = [
        "# Подготовка к собеседованию: всё в одном файле",
        "",
        "Все темы базы одним документом — в порядке исходного README. "
        "Файл собирается скриптом `tools/build_full_readme.py` из тематических файлов "
        "([оглавление по файлам](README.md)); правки вносить в тематические файлы и пересобирать.",
        "",
        "## Оглавление",
        "",
    ]
    out += [f"- [{title}](#{anchor})" for title, anchor in titles]
    out.append("")

    for name in ORDER:
        out += ["", "---", ""]
        for _, line, in_code in iter_lines_outside_code(texts[name]):
            if not in_code and NAV.match(line):
                continue
            if not in_code:
                line = LINK.sub(lambda m: relink(name, m.group(1), m.group(2)), line)
            out.append(line)

    with open(os.path.join(ROOT, OUT), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out).rstrip() + "\n")
    print(f"{OUT}: {len(out)} строк, тем: {len(titles)}")


if __name__ == "__main__":
    main()
