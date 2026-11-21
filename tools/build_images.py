"""Рисует схемы базы в SVG с тёмным фоном (img/*.svg).

Запуск из корня репозитория:  python tools/build_images.py
Только стандартная библиотека. Чтобы поправить схему — меняйте описание ниже и пересобирайте.
"""
import os
from xml.sax.saxutils import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "img")

# Палитра в духе тёмной темы GitHub
BG = "#0d1117"
TEXT = "#e6edf3"
MUTED = "#8b949e"
LINE = "#8b949e"
FONT = "Segoe UI, Helvetica, Arial, sans-serif"
MONO = "Consolas, Menlo, monospace"

C = {  # (заливка, рамка)
    "green": ("#1b4332", "#3fb950"),
    "red": ("#5c1a1b", "#f85149"),
    "blue": ("#132f55", "#58a6ff"),
    "orange": ("#5a3510", "#f0883e"),
    "purple": ("#35205a", "#a371f7"),
    "pink": ("#5a1f45", "#f778ba"),
    "cyan": ("#0f3b47", "#39c5cf"),
    "grey": ("#21262d", "#8b949e"),
    "yellow": ("#4a3f0f", "#d29922"),
}


class Svg:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.items = []

    def add(self, s):
        self.items.append(s)

    def text(self, x, y, lines, size=15, color=TEXT, anchor="middle", weight="normal", font=FONT):
        if isinstance(lines, str):
            lines = [lines]
        lh = size * 1.3
        y0 = y - (len(lines) - 1) * lh / 2
        for i, line in enumerate(lines):
            self.add(
                f'<text x="{x}" y="{y0 + i * lh:.1f}" fill="{color}" font-family="{font}" font-size="{size}" '
                f'font-weight="{weight}" text-anchor="{anchor}" dominant-baseline="central">{escape(line)}</text>'
            )

    def box(self, cx, cy, w, h, lines, color="grey", size=15, radius=6, weight="normal", dashed=False):
        fill, stroke = C[color]
        dash = ' stroke-dasharray="6 4"' if dashed else ""
        self.add(
            f'<rect x="{cx - w / 2}" y="{cy - h / 2}" width="{w}" height="{h}" rx="{radius}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="1.6"{dash}/>'
        )
        if lines:
            self.text(cx, cy, lines, size=size, weight=weight)

    def rect(self, x, y, w, h, fill="none", stroke=LINE, dashed=False, radius=0, width=1.6):
        dash = ' stroke-dasharray="7 5"' if dashed else ""
        self.add(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{width}"{dash}/>'
        )

    def path(self, points, dashed=False, arrow=True, color=LINE):
        d = "M " + " L ".join(f"{x} {y}" for x, y in points)
        dash = ' stroke-dasharray="5 4"' if dashed else ""
        mk = ' marker-end="url(#arrow)"' if arrow else ""
        self.add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="1.6"{dash}{mk}/>')

    def render(self, name):
        head = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
            f'viewBox="0 0 {self.w} {self.h}">\n'
            '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" '
            f'orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{LINE}"/></marker></defs>\n'
            f'<rect width="100%" height="100%" rx="10" fill="{BG}"/>\n'
        )
        with open(os.path.join(IMG, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(head + "\n".join(self.items) + "\n</svg>\n")
        print("img/" + name)


# ---------- Деревья (наследование) ----------

def tree(svg, nodes, edges, h=38, size=14):
    """nodes: имя → (cx, cy, w, цвет); edges: (ребёнок, родитель, пунктир, [промежуточные точки])."""
    for child, parent, dashed, via in edges:
        cx, cy, cw, _ = nodes[child]
        px, py, pw, _ = nodes[parent]
        if via == "side":            # вбок от левого края ребёнка к стволу под родителем
            trunk = px - pw / 2 + 14
            pts = [(cx - cw / 2, cy), (trunk, cy), (trunk, py + h / 2)]
        elif via:
            pts = [(cx, cy - h / 2)] + via + [(px, py + h / 2)]
        elif abs(cx - px) < 1:
            pts = [(cx, cy - h / 2), (px, py + h / 2)]
        else:
            mid = (cy - h / 2 + py + h / 2) / 2
            pts = [(cx, cy - h / 2), (cx, mid), (px, mid), (px, py + h / 2)]
        svg.path(pts, dashed=dashed)
    for name, (cx, cy, w, color) in nodes.items():
        svg.box(cx, cy, w, h, name, color, size=size)


def legend(svg, x, y, items):
    for i, (label, color, kind) in enumerate(items):
        yy = y + i * 30
        if kind == "box":
            svg.box(x + 18, yy, 36, 20, None, color, radius=4)
        else:
            svg.path([(x, yy), (x + 36, yy)], dashed=(kind == "dashed"))
        svg.text(x + 48, yy, label, size=13, color=MUTED, anchor="start")


def exception_hierarchy():
    s = Svg(1240, 500)
    n = {
        "Object": (590, 45, 120, "grey"),
        "Throwable": (590, 125, 150, "red"),
        "Error": (300, 215, 120, "green"),
        "Exception": (850, 215, 140, "red"),
        "VirtualMachineError": (190, 305, 200, "green"),
        "AssertionError": (420, 305, 160, "green"),
        "OutOfMemoryError": (100, 395, 180, "green"),
        "StackOverflowError": (295, 395, 190, "green"),
        "RuntimeException": (620, 305, 190, "green"),
        "IOException": (850, 305, 140, "red"),
        "SQLException": (1000, 305, 140, "red"),
        "InterruptedException": (1130, 395, 190, "red"),
        "NullPointerException": (495, 395, 200, "green"),
        "IllegalArgumentException": (720, 395, 220, "green"),
        "FileNotFoundException": (940, 465, 200, "red"),
    }
    e = [
        ("Throwable", "Object", False, None), ("Error", "Throwable", False, None),
        ("Exception", "Throwable", False, None), ("VirtualMachineError", "Error", False, None),
        ("AssertionError", "Error", False, None), ("OutOfMemoryError", "VirtualMachineError", False, None),
        ("StackOverflowError", "VirtualMachineError", False, None), ("RuntimeException", "Exception", False, None),
        ("IOException", "Exception", False, None), ("SQLException", "Exception", False, None),
        ("InterruptedException", "Exception", False, [(1130, 260), (850, 260)]),
        ("NullPointerException", "RuntimeException", False, None),
        ("IllegalArgumentException", "RuntimeException", False, None),
        ("FileNotFoundException", "IOException", False, [(940, 430), (850, 430)]),
    ]
    tree(s, n, e)
    legend(s, 20, 30, [
        ("checked — компилятор требует обработать", "red", "box"),
        ("unchecked — RuntimeException, Error и наследники", "green", "box"),
    ])
    s.render("exception-hierarchy.svg")


def collections_hierarchy():
    s = Svg(1120, 560)
    I, K = "green", "orange"
    n = {
        "Collection": (330, 45, 140, I),
        "List": (110, 125, 120, I),
        "Queue": (330, 125, 120, I),
        "Set": (590, 125, 120, I),
        "ArrayList": (150, 205, 140, K),
        "LinkedList": (150, 265, 140, K),
        "Vector": (150, 325, 140, K),
        "Stack": (150, 405, 140, K),
        "PriorityQueue": (400, 190, 150, K),
        "Deque": (330, 265, 120, I),
        "ArrayDeque": (330, 345, 140, K),
        "HashSet": (660, 190, 140, K),
        "LinkedHashSet": (660, 265, 150, K),
        "SortedSet": (590, 345, 130, I),
        "NavigableSet": (590, 415, 140, I),
        "TreeSet": (590, 485, 130, K),
        "Map": (960, 45, 120, I),
        "HashMap": (830, 125, 130, K),
        "LinkedHashMap": (830, 205, 150, K),
        "SortedMap": (1040, 125, 130, I),
        "NavigableMap": (1040, 205, 140, I),
        "TreeMap": (1040, 285, 120, K),
        "ConcurrentHashMap": (930, 345, 180, K),
    }
    e = [
        ("List", "Collection", False, None), ("Queue", "Collection", False, None),
        ("Set", "Collection", False, None),
        ("ArrayList", "List", True, "side"), ("LinkedList", "List", True, "side"),
        ("Vector", "List", True, "side"), ("Stack", "Vector", False, None),
        ("PriorityQueue", "Queue", True, [(400, 160), (360, 160)]),
        ("Deque", "Queue", False, [(300, 246), (300, 144)]),
        ("ArrayDeque", "Deque", True, None),
        ("LinkedList", "Deque", True, [(220, 265), (250, 265)]),
        ("HashSet", "Set", True, [(660, 160), (620, 160)]),
        ("LinkedHashSet", "HashSet", False, None),
        ("SortedSet", "Set", False, [(560, 326), (560, 144)]),
        ("NavigableSet", "SortedSet", False, None), ("TreeSet", "NavigableSet", True, None),
        ("HashMap", "Map", True, None), ("LinkedHashMap", "HashMap", False, None),
        ("SortedMap", "Map", False, None), ("NavigableMap", "SortedMap", False, None),
        ("TreeMap", "NavigableMap", True, None),
        ("ConcurrentHashMap", "Map", True, [(930, 85), (960, 85)]),
    ]
    # LinkedList → Deque: путь уходит вбок, поправим конец вручную
    e = [x for x in e if not (x[0] == "LinkedList" and x[1] == "Deque")]
    tree(s, n, e)
    s.path([(220, 265), (270, 265)], dashed=True)
    legend(s, 720, 430, [
        ("интерфейс", I, "box"), ("класс", K, "box"),
        ("extends — наследует", None, "solid"), ("implements — реализует", None, "dashed"),
    ])
    s.render("collections-hierarchy.svg")


# ---------- Жизненный цикл бина ----------

def bean_lifecycle():
    s = Svg(1160, 560)
    w, h, gap = 250, 120, 40
    x0 = 30 + w / 2
    steps = [
        ("blue", ["1. Чтение BeanDefinition", "BeanFactoryPostProcessor", "меняет определения"]),
        ("blue", ["2. Создание объекта", "конструктор +", "его зависимости"]),
        ("blue", ["3. Внедрение", "зависимостей", "в поля и сеттеры"]),
        ("blue", ["4. *Aware-методы", "BeanNameAware,", "ApplicationContextAware"]),
        ("purple", ["5. BeanPostProcessor", "postProcessBefore-", "Initialization"]),
        ("orange", ["6. Инициализация", "@PostConstruct →", "afterPropertiesSet() →", "init-method"]),
        ("purple", ["7. BeanPostProcessor", "postProcessAfter-", "Initialization", "здесь создаются прокси"]),
        ("green", ["8. Бин готов", "к использованию"]),
        ("red", ["9. Закрытие контекста", "@PreDestroy → destroy() →", "destroy-method", "(для prototype не вызывается)"]),
    ]
    pos = []
    for i in range(len(steps)):
        row, col = divmod(i, 4)
        pos.append((x0 + col * (w + gap), 90 + row * (h + 60)))
    for i in range(len(steps) - 1):
        (ax, ay), (bx, by) = pos[i], pos[i + 1]
        if ay == by:
            s.path([(ax + w / 2 + 4, ay), (bx - w / 2 - 4, by)])
        else:                                  # перенос на следующий ряд
            mid = ay + h / 2 + 30
            s.path([(ax, ay + h / 2 + 2), (ax, mid), (bx, mid), (bx, by - h / 2 - 4)])
    for (color, lines), (cx, cy) in zip(steps, pos):
        s.box(cx, cy, w, h, lines, color, size=15, radius=10)
    legend(s, 360, 450, [
        ("создание и внедрение зависимостей", "blue", "box"),
        ("BeanPostProcessor — обработка каждого бина", "purple", "box"),
        ("init-методы", "orange", "box"),
    ])
    legend(s, 760, 450, [("готов к работе", "green", "box"), ("уничтожение", "red", "box")])
    s.render("bean-lifecycle.svg")


# ---------- Достижимость объектов (GC) ----------

def garbage_collection():
    s = Svg(820, 560)
    s.rect(20, 20, 600, 520, fill="#161b22", stroke=MUTED, radius=24)
    s.path([(20, 160), (620, 160)], arrow=False)
    s.path([(20, 450), (620, 450)], arrow=False)
    s.text(720, 90, ["Недостижимые", "объекты = мусор", "(даже если ссылаются", "друг на друга)"], size=14)
    s.text(720, 300, ["Достижимые", "объекты"], size=14)
    s.text(720, 495, ["GC Roots"], size=15, weight="bold")

    r = 15

    def node(x, y, color="#58a6ff", fill="#132f55"):
        s.add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{color}" stroke-width="1.8"/>')

    def ref(a, b):
        (x1, y1), (x2, y2) = a, b
        dx, dy = x2 - x1, y2 - y1
        d = (dx * dx + dy * dy) ** 0.5
        s.path([(x1 + dx / d * r, y1 + dy / d * r), (x2 - dx / d * (r + 2), y2 - dy / d * (r + 2))])

    grey = ("#8b949e", "#21262d")
    # мусор: цикл A ⇄ B и маленькое дерево
    A, B, Cc, D, E = (110, 70), (210, 70), (360, 60), (330, 120), (400, 120)
    for p in (A, B, Cc, D, E):
        node(*p, *grey)
    s.add(f'<path d="M {A[0]+12} {A[1]-9} Q 160 40 {B[0]-14} {B[1]-7}" fill="none" stroke="{LINE}" stroke-width="1.6" marker-end="url(#arrow)"/>')
    s.add(f'<path d="M {B[0]-12} {B[1]+9} Q 160 100 {A[0]+14} {A[1]+7}" fill="none" stroke="{LINE}" stroke-width="1.6" marker-end="url(#arrow)"/>')
    s.text(160, 125, "цикл", size=12, color=MUTED)
    ref(Cc, D)
    ref(Cc, E)

    # корни
    roots = [(110, "стек потока"), (320, "static-поле"), (520, "стек потока")]
    for x, label in roots:
        s.box(x, 495, 130, 34, label, "cyan", size=13, radius=4)

    # достижимые: дерево от первого корня
    t1 = [(110, 400), (70, 330), (150, 330), (50, 255), (100, 255), (160, 255), (200, 200)]
    for p in t1:
        node(*p)
    ref((110, 478), t1[0])
    for a, b in [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (5, 6)]:
        ref(t1[a], t1[b])
    # от второго и третьего корня — общий граф
    t2 = [(320, 400), (520, 400), (280, 320), (380, 320), (470, 320), (560, 320),
          (330, 240), (430, 240), (520, 240), (380, 190), (480, 185)]
    for p in t2:
        node(*p)
    ref((320, 478), t2[0])
    ref((520, 478), t2[1])
    for a, b in [(0, 2), (0, 3), (1, 4), (1, 5), (3, 6), (3, 7), (4, 7), (5, 8), (6, 9), (7, 9), (8, 10), (7, 10)]:
        ref(t2[a], t2[b])
    s.render("garbage-collection.svg")


# ---------- Transactional outbox ----------

def transactional_outbox():
    s = Svg(1120, 500)
    # Сервис
    s.path([(290, 15), (290, 63)])
    s.box(290, 110, 180, 90, ["Order Service"], "green", size=17)
    # БД и транзакция
    s.rect(30, 200, 700, 280, fill=C["purple"][0], stroke=C["purple"][1], radius=8)
    s.text(45, 222, "База данных", size=16, anchor="start")
    s.rect(65, 245, 630, 210, fill="#1c1430", stroke=TEXT, dashed=True, radius=4)
    s.text(80, 268, "Одна локальная транзакция", size=15, anchor="start")

    def table(x, y, cells, cw=105):
        for i in range(cells):
            s.rect(x + i * cw, y, cw, 40, fill=BG, stroke=TEXT, width=1.3)

    table(95, 395, 2, 130)
    table(390, 395, 3, 100)
    s.text(225, 375, "таблица ORDER", size=15)
    s.text(540, 375, "таблица OUTBOX", size=15)
    s.path([(250, 155), (190, 390)])
    s.path([(330, 155), (450, 390)])
    s.text(185, 322, ["INSERT, UPDATE,", "DELETE заказа"], size=14, font=MONO, anchor="end")
    s.text(432, 322, ["INSERT", "события"], size=14, font=MONO, anchor="start")

    def badge(x, y, n):
        s.add(f'<circle cx="{x}" cy="{y}" r="15" fill="{TEXT}"/>')
        s.text(x, y, str(n), size=16, color=BG, weight="bold")

    badge(665, 275, 1)
    # Relay и брокер
    s.box(850, 360, 110, 180, ["Message", "relay"], "pink", size=16, radius=4)
    s.box(1040, 360, 110, 180, ["Брокер", "сообщений", "(Kafka)"], "cyan", size=16, radius=4)
    s.path([(795, 415), (700, 415)])
    s.text(748, 445, ["читает", "OUTBOX"], size=13)
    badge(748, 385, 2)
    s.path([(905, 360), (983, 360)])
    s.text(944, 390, "публикует", size=13)
    badge(944, 330, 3)
    s.text(870, 220, ["1 — заказ и событие пишутся атомарно",
                      "2 — relay (поллинг или Debezium/CDC) читает",
                      "3 — публикует; гарантия at-least-once"], size=13, color=MUTED)
    s.render("transactional-outbox.svg")


# ---------- Таблица сложности ----------

def complexity_table():
    cols = ["Индексация", "Поиск", "Вставка", "Удаление"]
    rows = [
        ("Обычный массив", ["1", "n", "-", "-"], ["1", "n", "-", "-"], "n"),
        ("Динамический массив", ["1", "n", "n", "n"], ["1", "n", "n", "n"], "n"),
        ("Односвязный список", ["n", "n", "1", "1"], ["n", "n", "1", "1"], "n"),
        ("Двусвязный список", ["n", "n", "1", "1"], ["n", "n", "1", "1"], "n"),
        ("Список с пропусками", ["log", "log", "log", "log"], ["n", "n", "n", "n"], "nlog"),
        ("Хеш-таблица", ["-", "1", "1", "1"], ["-", "n", "n", "n"], "n"),
        ("Бинарное дерево поиска", ["log", "log", "log", "log"], ["n", "n", "n", "n"], "n"),
        ("Декартово дерево", ["-", "log", "log", "log"], ["-", "n", "n", "n"], "n"),
        ("B-дерево", ["log", "log", "log", "log"], ["log", "log", "log", "log"], "n"),
        ("Красно-чёрное дерево", ["log", "log", "log", "log"], ["log", "log", "log", "log"], "n"),
    ]
    label = {"1": "O(1)", "log": "O(log n)", "n": "O(n)", "nlog": "O(n log n)", "-": "—"}
    style = {  # заливка, цвет текста
        "1": ("#1b4332", "#7ee2a8"), "log": ("#21412a", "#b4e08a"), "n": ("#5c1a1b", "#ffa198"),
        "nlog": ("#6e1a2c", "#ff8fa8"), "-": ("#21262d", MUTED),
    }
    first, cw, rh = 230, 104, 44
    w = first + cw * 9 + 40
    top = 20 + rh * 2
    s = Svg(w, top + rh * len(rows) + 70)
    x0 = 20
    hdr = "#161b22"
    s.rect(x0, 20, first, rh * 2, fill=hdr, stroke="#30363d")
    s.text(x0 + first / 2, 20 + rh, "Структура данных", size=15, weight="bold")
    groups = [("Время — в среднем", 4), ("Время — в худшем", 4), ("Память", 1)]
    x = x0 + first
    for title, k in groups:
        s.rect(x, 20, cw * k, rh, fill=hdr, stroke="#30363d")
        s.text(x + cw * k / 2, 20 + rh / 2, title, size=15, weight="bold")
        sub = cols if k == 4 else ["в худшем"]
        for i, name in enumerate(sub):
            s.rect(x + i * cw, 20 + rh, cw, rh, fill=hdr, stroke="#30363d")
            s.text(x + i * cw + cw / 2, 20 + rh * 1.5, name, size=13, color=MUTED)
        x += cw * k
    for r, (name, avg, worst, mem) in enumerate(rows):
        y = top + r * rh
        s.rect(x0, y, first, rh, fill=hdr, stroke="#30363d")
        s.text(x0 + 12, y + rh / 2, name, size=14, anchor="start")
        for i, v in enumerate(avg + worst + [mem]):
            fill, color = style[v]
            s.rect(x0 + first + i * cw, y, cw, rh, fill=fill, stroke="#30363d")
            s.text(x0 + first + i * cw + cw / 2, y + rh / 2, label[v], size=14, color=color, font=MONO)
    s.text(x0, top + rh * len(rows) + 30,
           "Вставка/удаление O(1) у списков — когда узел уже найден; поиск места — O(n). "
           "Хеш-таблица O(n) в худшем — все ключи в одном бакете (в Java 8+ HashMap — O(log n)).",
           size=13, color=MUTED, anchor="start")
    s.render("complexity-table.svg")


if __name__ == "__main__":
    exception_hierarchy()
    collections_hierarchy()
    bean_lifecycle()
    garbage_collection()
    transactional_outbox()
    complexity_table()
