# Алгоритмы и задачи на live coding

[← Оглавление](README.md) · Структуры данных — [collections.md](collections.md#10-структуры-данных--база)

Как пользоваться файлом:
- разделы 3–5 — как прийти от лобового решения к хорошему и какие приёмы бывают, с шаблонами на Java;
- раздел 6 — как вести себя на live coding и что помнить из стандартной библиотеки;
- раздел 7 — как устроена алгоритмическая секция в Яндексе, по официальным материалам;
- раздел 8 — план подготовки на неделю;
- раздел 9 — задачи с решениями под спойлерами.

Код шаблонов скомпилирован и проверен тестами: результат сравнивался с лобовыми решениями на случайных данных.

## 1. Сложность (Big O)

| Сложность | Название | Пример |
|---|---|---|
| O(1) | константная | доступ к массиву по индексу, `HashMap.get` в среднем |
| O(log n) | логарифмическая | бинарный поиск, операции в сбалансированном дереве |
| O(n) | линейная | один проход по массиву |
| O(n log n) | линейно-логарифмическая | хорошие сортировки (merge sort, quick sort в среднем) |
| O(n²) | квадратичная | два вложенных цикла, пузырьковая сортировка |
| O(2ⁿ) | экспоненциальная | перебор всех подмножеств |

- Оценивают и **время**, и **дополнительную память**.
- Константы и младшие члены отбрасываются: O(2n + 10) = O(n).
- На собеседовании после решения всегда спросят: «какая сложность и можно ли лучше?»
- Какая сложность нужна при данном размере входа — [таблица в разделе 4](#размер-входа--нужная-сложность).

## 2. Сортировки

| Алгоритм | Время (среднее / худшее) | Память | Стабильная | Суть |
|---|---|---|---|---|
| Пузырьком | O(n²) / O(n²) | O(1) | да | соседние элементы меняются местами, большие «всплывают» |
| Вставками | O(n²) / O(n²), O(n) на почти отсортированных | O(1) | да | каждый элемент вставляется на место в уже отсортированную часть |
| **Быстрая (quick sort)** | O(n log n) / O(n²) | O(log n) | нет | опорный элемент, меньшие влево, большие вправо, рекурсия |
| **Слиянием (merge sort)** | O(n log n) / O(n log n) | O(n) | да | делим пополам, сортируем, сливаем |
| Пирамидальная (heap sort) | O(n log n) / O(n log n) | O(1) | нет | через кучу |

**Что в Java:** `Arrays.sort` для примитивов — **Dual-Pivot Quicksort** (стабильность для примитивов не важна); для объектов и `Collections.sort`/`List.sort` — **TimSort** (гибрид слияния и вставок, стабильный, очень быстр на частично отсортированных данных).

**Стабильная** сортировка сохраняет относительный порядок равных элементов — важно при сортировке по нескольким ключам по очереди.

```java
// Пузырьковая сортировка (для понимания; в коде — Arrays.sort)
static void bubbleSort(int[] arr) {
    for (int i = arr.length - 1; i > 0; i--) {
        boolean swapped = false;
        for (int j = 0; j < i; j++) {
            if (arr[j] > arr[j + 1]) {
                int tmp = arr[j]; arr[j] = arr[j + 1]; arr[j + 1] = tmp;
                swapped = true;
            }
        }
        if (!swapped) return;            // уже отсортировано — выходим раньше
    }
}

// Бинарный поиск в отсортированном массиве — O(log n)
static int binarySearch(int[] a, int target) {
    int lo = 0, hi = a.length - 1;
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;    // не (lo + hi) / 2 — переполнение int на больших массивах
        if (a[mid] == target) return mid;
        if (a[mid] < target) lo = mid + 1; else hi = mid - 1;
    }
    return -1;
}
```

## 3. От лобового решения к оптимальному

**Коротко:** лобовое решение — нормальный первый шаг. Его проговаривают за минуту и называют сложность. Затем находят самое дорогое место, обычно внутренний цикл, и спрашивают: какую работу он делает? Типовых ответов три, и у каждого свой набор приёмов.

| Внутренний цикл… | Чем заменить | Пример |
|---|---|---|
| **ищет** что-то: «есть ли число x?», «где пара?», «какой минимум?» | хэш — поиск за O(1); сортировка + бинарный поиск — O(log n); куча — минимум за O(log n) | Two Sum |
| **пересчитывает** то, что уже считал на прошлом шаге | скользящее окно; префиксные суммы; мемоизация и DP | сумма окна длины k |
| **перебирает лишнее** — варианты, которые заведомо не подойдут | сортировка + два указателя; бинарный поиск; отсечения | пара с суммой в отсортированном массиве, 3Sum ([5.2](#52-два-указателя)) |

Главный вопрос, который превращает O(n²) в O(n): **что нужно знать об уже пройденной части массива, чтобы сразу ответить для текущего элемента?** Это «что-то» и хранят в переменной, хэше, стеке или куче.

Порядок действий:
1. Проговорить лобовое решение и его сложность.
2. Сравнить с тем, что нужно при данном n ([таблица](#размер-входа--нужная-сложность)). Для n = 10⁵ квадрат не пройдёт: нужно O(n log n) или O(n).
3. Найти самое дорогое место и задать ему вопрос из таблицы выше.
4. Подобрать структуру данных, которая отвечает на этот вопрос быстрее.
5. Проверить, есть ли куда улучшать. Вход нужно хотя бы прочитать, поэтому O(n) обычно — предел. Если решение O(n log n) из-за сортировки, спросить себя, нельзя ли обойтись хэшем.

### Пример 1. Two Sum: «ищу» → HashMap

Найти индексы двух чисел, сумма которых равна `target` (LeetCode 1).

```java
// В лоб: все пары — O(n²) время, O(1) память
int[] twoSumBrute(int[] nums, int target) {
    for (int i = 0; i < nums.length; i++)
        for (int j = i + 1; j < nums.length; j++)          // ← дорогое место
            if (nums[i] + nums[j] == target) return new int[]{i, j};
    return new int[0];
}
```

<details><summary>Решение</summary>

Внутренний цикл **ищет** число `target - nums[i]` среди остальных. Поиск — работа для хэша: храним уже пройденные числа в `HashMap` «число → индекс». Поиск становится O(1), а всё решение — одним проходом.

```java
// Один проход: O(n) время, O(n) память
int[] twoSum(int[] nums, int target) {
    Map<Integer, Integer> seen = new HashMap<>();          // число → индекс, только пройденные
    for (int i = 0; i < nums.length; i++) {
        Integer j = seen.get(target - nums[i]);            // поиск за O(1) вместо цикла
        if (j != null) return new int[]{j, i};
        seen.put(nums[i], i);                              // кладём ПОСЛЕ проверки, иначе найдём сами себя
    }
    return new int[0];
}
```
Компромисс: память O(n) вместо O(1). Будь массив отсортирован, хватило бы двух указателей без доп. памяти — это уже «перебираю лишнее» ([5.2](#52-два-указателя)).
</details>

### Пример 2. Максимальная сумма окна длины k: «пересчитываю» → скользящее окно

Найти максимальную сумму k подряд идущих элементов, 1 ≤ k ≤ n (то же, что LeetCode 643).

```java
// В лоб: для каждого начала заново складываем k элементов — O(n·k)
long maxWindowSumBrute(int[] a, int k) {
    long best = Long.MIN_VALUE;
    for (int i = 0; i + k <= a.length; i++) {
        long sum = 0;
        for (int j = i; j < i + k; j++) sum += a[j];      // ← дорогое место
        best = Math.max(best, sum);
    }
    return best;
}
```

<details><summary>Решение</summary>

Соседние окна `[i, i+k)` и `[i+1, i+k+1)` отличаются двумя элементами, а k − 1 слагаемых у них общие. Внутренний цикл **пересчитывает** уже известное. Двигаем окно: прибавляем вошедший элемент и вычитаем вышедший.

```java
// Скользящее окно: O(n) время, O(1) память
long maxWindowSum(int[] a, int k) {
    long sum = 0;
    for (int i = 0; i < k; i++) sum += a[i];              // первое окно
    long best = sum;
    for (int i = k; i < a.length; i++) {
        sum += a[i];                                      // вошёл справа
        sum -= a[i - k];                                  // вышел слева
        best = Math.max(best, sum);
    }
    return best;
}
```
Вопросы к интервьюеру: что вернуть, если k > n? Насколько большие числа (сумма — в `long`)?
</details>

### Пример 3. Сколько подмассивов с суммой k: «пересчитываю» и «ищу» → префиксы + HashMap

Посчитать непрерывные подмассивы с суммой ровно k; числа могут быть отрицательными (LeetCode 560).

```java
// В лоб: все отрезки [i, j], сумму каждого считаем заново — O(n³)
int subarraySumBrute(int[] nums, int k) {
    int count = 0;
    for (int i = 0; i < nums.length; i++)
        for (int j = i; j < nums.length; j++) {
            int sum = 0;
            for (int t = i; t <= j; t++) sum += nums[t];  // ← пересчитываем
            if (sum == k) count++;
        }
    return count;
}
```

<details><summary>Решение</summary>

**Шаг 1 — «пересчитываю».** Сумма `[i, j]` — это сумма `[i, j−1]` плюс `nums[j]`. Её можно накапливать во втором цикле: O(n²).

```java
int subarraySumQuadratic(int[] nums, int k) {
    int count = 0;
    for (int i = 0; i < nums.length; i++) {
        int sum = 0;
        for (int j = i; j < nums.length; j++) {           // ← теперь этот цикл ищет j с нужной суммой
            sum += nums[j];
            if (sum == k) count++;
        }
    }
    return count;
}
```

**Шаг 2 — «ищу».** Пусть `prefix` — сумма элементов от начала до текущего включительно. Сумма любого подмассива, который кончается на текущем элементе, — это `prefix` минус какой-то более ранний префикс. Она равна k, когда ранний префикс равен `prefix - k`. Значит, для каждого элемента нужно знать, **сколько раз раньше встречалась** сумма `prefix - k`. Это вопрос к `HashMap` «сумма → сколько раз».

```java
// Префиксные суммы + HashMap: O(n) время, O(n) память
int subarraySum(int[] nums, int k) {
    Map<Integer, Integer> prefixCount = new HashMap<>();  // префиксная сумма → сколько раз встречалась
    prefixCount.put(0, 1);                                // пустой префикс — для подмассивов с начала
    int prefix = 0, count = 0;
    for (int x : nums) {
        prefix += x;
        count += prefixCount.getOrDefault(prefix - k, 0); // сначала ищем…
        prefixCount.merge(prefix, 1, Integer::sum);       // …потом добавляем текущий префикс
    }
    return count;
}
```
Почему не окно: с отрицательными числами сумма при расширении окна может и уменьшиться, поэтому непонятно, какую границу двигать. Окно работает, только когда все числа положительные.

Частые баги: забыть `put(0, 1)` — потеряются подмассивы, которые начинаются с первого элемента. Добавить префикс до поиска — при k = 0 каждый элемент засчитает пустой подмассив.
</details>

**Как тренировать этот переход.** После каждой задачи записать одну строку: лобовое решение и его сложность → дорогое место → какой вопрос оно задаёт → приём → итоговая сложность. Например: «Two Sum: все пары, O(n²) → внутренний цикл ищет дополнение → HashMap → O(n)».

## 4. Как выбрать приём: две таблицы

### Размер входа → нужная сложность

Java выполняет примерно 10⁸ простых операций в секунду, лимит времени у задач обычно 1–2 секунды. Отсюда:

| Размер n | Подойдёт | Типичные приёмы |
|---|---|---|
| ≤ 10–12 | O(n!) | перебор перестановок |
| ≤ 20–25 | O(2ⁿ) | перебор подмножеств, backtracking |
| ≤ 300–500 | O(n³) | три вложенных цикла, DP по отрезкам |
| ≤ 10⁴ | O(n²) | два вложенных цикла, DP по двум индексам |
| 10⁵–10⁶ | O(n log n) или O(n) | сортировка, куча, бинарный поиск, хэш, два указателя, окно |
| 10⁹ и больше (или значения до 10⁹) | O(log n) или O(1) | бинарный поиск по ответу, формула |

На собеседовании ограничения часто не называют — спросите сами: «какой размер входа?» Если ответ «большой» или «как в продакшене», цель — O(n) или O(n log n).

### Признак в условии → приём

| Признак в условии | Приём | Раздел |
|---|---|---|
| «встречалось ли раньше», «найти пару», «посчитать, сколько раз», «сгруппировать», анаграммы | HashMap, HashSet, `int[26]` | [5.1](#51-хэш-и-частоты) |
| массив отсортирован (или его можно отсортировать); пара или тройка с суммой; палиндром | два указателя | [5.2](#52-два-указателя) |
| непрерывный подмассив или подстрока; «самый длинный / самый короткий, где …» | скользящее окно | [5.3](#53-скользящее-окно) |
| сумма на отрезке; «сколько подмассивов с суммой k»; есть отрицательные числа | префиксные суммы + HashMap | [5.4](#54-префиксные-суммы--hashmap) |
| скобки, вложенность; «следующий больший», «ближайший меньший слева» | стек, монотонный стек | [5.5](#55-стек-и-монотонный-стек) |
| отсортированный массив, «найти позицию»; «минимальное X, при котором …» | бинарный поиск, в том числе по ответу | [5.6](#56-бинарный-поиск-в-том-числе-по-ответу) |
| связный список: середина, цикл, k-й с конца | быстрый и медленный указатели | [5.7](#57-быстрый-и-медленный-указатели) |
| дерево: глубина, путь, проверка свойства; «по уровням» | DFS рекурсией, BFS очередью | [5.8](#58-дерево-dfs-и-bfs) |
| сетка, лабиринт, острова; «кратчайший путь», «минимум шагов» | BFS по сетке и графу | [5.9](#59-сетка-и-граф-bfs-и-dfs) |
| «k наибольших / наименьших / частых», «k-й по величине», слияние k списков | куча | [5.10](#510-куча-top-k) |
| отрезки, встречи, бронирования | сортировка по началу + проход | [5.11](#511-интервалы) |
| «ближайший ключ ≤ x», упорядоченные данные со вставками и удалениями | TreeMap, TreeSet | [5.12](#512-treemap-и-treeset-ближайший-ключ) |
| «все комбинации / перестановки / подмножества», «сгенерировать все» | backtracking | [5.13](#513-backtracking-перебор-с-возвратом) |
| «сколько способов», «минимальная стоимость», «максимальная сумма» при выборе на каждом шаге | DP | [5.14](#514-динамическое-программирование-база) |
| зависимости, порядок выполнения, «можно ли выполнить все» | топологическая сортировка | [5.15](#515-топологическая-сортировка) |
| «объединить группы», «связаны ли», компоненты при добавлении рёбер | Union-Find | [5.16](#516-union-find-по-желанию) |
| числа от 1 до n, «найти пропущенное или повторяющееся» за O(1) памяти | сумма или XOR; значение как индекс | — |

## 5. Каталог приёмов

Для каждого приёма — когда применять, шаблон на Java и задачи LeetCode примерно по возрастанию сложности. Методы написаны в стиле LeetCode: без `static`, классы `ListNode` и `TreeNode` объявлены в [5.7](#57-быстрый-и-медленный-указатели) и [5.8](#58-дерево-dfs-и-bfs).

### 5.1. Хэш и частоты

**Когда:** «встречалось ли раньше», «найти пару», «посчитать, сколько раз», «сгруппировать», анаграммы. Хэш заменяет внутренний цикл поиска: O(n²) → O(n).

```java
// Частоты строчных латинских букв — массив int[26] вместо HashMap (LeetCode 242)
boolean isAnagram(String s, String t) {
    if (s.length() != t.length()) return false;
    int[] cnt = new int[26];
    for (int i = 0; i < s.length(); i++) {
        cnt[s.charAt(i) - 'a']++;
        cnt[t.charAt(i) - 'a']--;
    }
    for (int c : cnt) if (c != 0) return false;
    return true;
}

// Любые ключи — HashMap и merge
Map<String, Integer> countWords(List<String> words) {
    Map<String, Integer> freq = new HashMap<>();
    for (String w : words) freq.merge(w, 1, Integer::sum);
    return freq;
}

// «Видел ли раньше»: Set.add возвращает false, если элемент уже был (LeetCode 217)
boolean containsDuplicate(int[] nums) {
    Set<Integer> seen = new HashSet<>();
    for (int x : nums) if (!seen.add(x)) return true;
    return false;
}

// Самая длинная серия подряд идущих чисел за O(n) (LeetCode 128)
int longestConsecutive(int[] nums) {
    Set<Integer> set = new HashSet<>();
    for (int x : nums) set.add(x);
    int best = 0;
    for (int x : set) {
        if (set.contains(x - 1)) continue;                // считаем только от начала серии
        int len = 1;
        while (set.contains(x + len)) len++;
        best = Math.max(best, len);
    }
    return best;
}
```

**Подвохи:**
- `Integer` сравнивают через `equals`, а не `==`. Оператор `==` сравнивает ссылки и случайно работает только в кэше −128…127. `map.get(a) == map.get(b)` — классический баг.
- `Set` не помнит количество. Сравнивать анаграммы через множества букв нельзя: «aab» и «abb» дадут одно множество. Это типичная ошибка из материалов Яндекса.
- `int[26]` годится, только если алфавит известен. Спросите про регистр, пробелы и Unicode.

**Задачи:** 1 Two Sum · 242 Valid Anagram · 217 Contains Duplicate · 387 First Unique Character in a String · 49 Group Anagrams · 128 Longest Consecutive Sequence.

### 5.2. Два указателя

**Когда:** массив отсортирован или его можно отсортировать, если индексы не нужны. Ищем пару или тройку с суммой, проверяем палиндром, сливаем два отсортированных массива, удаляем или сдвигаем элементы на месте.

Почему это не перебор: если `a[l] + a[r] < target`, то `a[l]` не даст пару ни с одним элементом левее `r` — они ещё меньше. Значит, `a[l]` можно выбросить целиком: один шаг отсекает сразу много пар.

```java
// Встречные указатели: пара с суммой target в отсортированном массиве (LeetCode 167), O(n), O(1)
int[] twoSumSorted(int[] a, int target) {
    int l = 0, r = a.length - 1;
    while (l < r) {
        int sum = a[l] + a[r];
        if (sum == target) return new int[]{l, r};        // в LeetCode 167 индексы с единицы
        if (sum < target) l++;                            // a[l] мал даже с самым большим — выбрасываем
        else r--;                                         // a[r] велик даже с самым маленьким
    }
    return new int[0];
}

// В одну сторону: читаем всё подряд, пишем по указателю w (LeetCode 26)
int removeDuplicates(int[] a) {
    int w = 0;                                            // a[0..w) — уже без повторов
    for (int x : a)
        if (w == 0 || x != a[w - 1]) a[w++] = x;
    return w;
}

// 3Sum (LeetCode 15): сортировка + для каждого i встречные указатели, O(n²)
List<List<Integer>> threeSum(int[] nums) {
    Arrays.sort(nums);
    List<List<Integer>> res = new ArrayList<>();
    for (int i = 0; i + 2 < nums.length; i++) {
        if (i > 0 && nums[i] == nums[i - 1]) continue;    // тот же первый элемент — те же тройки
        int l = i + 1, r = nums.length - 1;
        while (l < r) {
            int sum = nums[i] + nums[l] + nums[r];
            if (sum < 0) l++;
            else if (sum > 0) r--;
            else {
                res.add(List.of(nums[i], nums[l], nums[r]));
                while (l < r && nums[l] == nums[l + 1]) l++;   // пропускаем повторы
                while (l < r && nums[r] == nums[r - 1]) r--;
                l++;
                r--;
            }
        }
    }
    return res;
}
```

**Задачи:** 167 Two Sum II – Input Array Is Sorted · 125 Valid Palindrome (задача 12 ниже) · 283 Move Zeroes · 26 Remove Duplicates from Sorted Array · 15 3Sum · 11 Container With Most Water.

### 5.3. Скользящее окно

**Когда:** непрерывный подмассив или подстрока: «самый длинный, где …», «самый короткий, где …», «сколько подмассивов, где …». Окно работает, если условие монотонно: при расширении окно может стать только «хуже», а при сужении — только «лучше». Если сумма может и расти, и падать (есть отрицательные числа), окно не годится — нужны префиксные суммы ([5.4](#54-префиксные-суммы--hashmap)).

Схема переменного окна:
1. Расширить окно вправо: добавить `a[r]`.
2. Пока окно «плохое», сжимать слева: убрать `a[l]`, `l++`.
3. Окно `[l, r]` хорошее — обновить ответ.

Окно фиксированной длины — [пример 2](#пример-2-максимальная-сумма-окна-длины-k-пересчитываю--скользящее-окно) выше.

```java
// Фиксированное окно с частотами: есть ли в s2 перестановка s1 (LeetCode 567)
boolean checkInclusion(String s1, String s2) {
    int k = s1.length();
    if (k > s2.length()) return false;
    int[] need = new int[26], window = new int[26];
    for (int i = 0; i < k; i++) {
        need[s1.charAt(i) - 'a']++;
        window[s2.charAt(i) - 'a']++;
    }
    if (Arrays.equals(need, window)) return true;
    for (int i = k; i < s2.length(); i++) {
        window[s2.charAt(i) - 'a']++;                     // вошёл справа
        window[s2.charAt(i - k) - 'a']--;                 // вышел слева
        if (Arrays.equals(need, window)) return true;     // 26 сравнений — O(1)
    }
    return false;
}

// Самое длинное окно: подстрока без повторов (LeetCode 3)
int longestUnique(String s) {
    Map<Character, Integer> cnt = new HashMap<>();
    int best = 0;
    for (int l = 0, r = 0; r < s.length(); r++) {
        char c = s.charAt(r);
        cnt.merge(c, 1, Integer::sum);                    // 1. расширили вправо
        while (cnt.get(c) > 1) {                          // 2. окно плохое — сжимаем слева
            cnt.merge(s.charAt(l), -1, Integer::sum);
            l++;
        }
        best = Math.max(best, r - l + 1);                 // 3. окно хорошее — обновили ответ
    }
    return best;
}

// Самое короткое окно: подмассив с суммой ≥ target, числа положительные (LeetCode 209)
int minSubArrayLen(int target, int[] nums) {
    int best = Integer.MAX_VALUE, sum = 0;
    for (int l = 0, r = 0; r < nums.length; r++) {
        sum += nums[r];
        while (sum >= target) {                           // окно хорошее — пробуем сузить
            best = Math.min(best, r - l + 1);
            sum -= nums[l++];
        }
    }
    return best == Integer.MAX_VALUE ? 0 : best;
}

// Подсчёт окон: сколько подмассивов, где все значения различны.
// Для каждого r подходят все начала от l до r — это r - l + 1 подмассивов
long countDistinctSubarrays(int[] a) {
    Map<Integer, Integer> cnt = new HashMap<>();
    long total = 0;
    for (int l = 0, r = 0; r < a.length; r++) {
        cnt.merge(a[r], 1, Integer::sum);
        while (cnt.get(a[r]) > 1) cnt.merge(a[l++], -1, Integer::sum);
        total += r - l + 1;
    }
    return total;
}
```

**Задачи:** 643 Maximum Average Subarray I · 567 Permutation in String · 3 Longest Substring Without Repeating Characters (задача 8 ниже — другой способ) · 209 Minimum Size Subarray Sum · 1004 Max Consecutive Ones III · 424 Longest Repeating Character Replacement.

### 5.4. Префиксные суммы + HashMap

**Когда:** нужно много раз считать сумму на отрезке; «сколько подмассивов с суммой k» или «делящихся на k»; есть отрицательные числа, и окно не работает; «поровну нулей и единиц» — заменить 0 на −1 и искать сумму 0.

Идея: `p[i]` — сумма первых i элементов. Сумма отрезка `[l, r]` равна `p[r + 1] - p[l]`. А вопрос «есть ли отрезок с суммой k» превращается в «встречался ли раньше префикс, равный текущему минус k» — и это работа для хэша. Подсчёт подмассивов с суммой k разобран в [примере 3](#пример-3-сколько-подмассивов-с-суммой-k-пересчитываю-и-ищу--префиксы--hashmap).

```java
// Сумма на отрезке за O(1) после O(n) подготовки (LeetCode 303)
long[] buildPrefix(int[] a) {
    long[] p = new long[a.length + 1];                    // p[i] = a[0] + … + a[i-1], p[0] = 0
    for (int i = 0; i < a.length; i++) p[i + 1] = p[i] + a[i];
    return p;
}

long rangeSum(long[] p, int l, int r) {                   // сумма a[l..r] включительно
    return p[r + 1] - p[l];
}

// Самый длинный подмассив, где поровну 0 и 1 (LeetCode 525): 0 → −1, ищем равные префиксы
int findMaxLength(int[] nums) {
    Map<Integer, Integer> firstIndex = new HashMap<>();   // префиксная сумма → где встретилась впервые
    firstIndex.put(0, -1);                                // пустой префикс «кончается» перед массивом
    int prefix = 0, best = 0;
    for (int i = 0; i < nums.length; i++) {
        prefix += nums[i] == 0 ? -1 : 1;
        Integer j = firstIndex.putIfAbsent(prefix, i);    // храним самое раннее появление
        if (j != null) best = Math.max(best, i - j);
    }
    return best;
}
```

**Задачи:** 303 Range Sum Query – Immutable · 238 Product of Array Except Self (префиксы и суффиксы произведений) · 560 Subarray Sum Equals K · 525 Contiguous Array · 974 Subarray Sums Divisible by K (остаток — через `Math.floorMod`).

### 5.5. Стек и монотонный стек

**Когда:** обычный стек — скобки и вложенность, «отменить последнее действие», вычисление выражений (скобки — задача 2 ниже). **Монотонный стек** — «следующий больший или меньший элемент», «сколько дней до потепления», «ближайший меньший слева». В стеке лежат элементы, для которых ответ ещё не найден. Каждый элемент кладётся и снимается один раз, поэтому O(n), хотя внутри цикла есть `while`.

```java
// Следующий больший элемент справа: res[i] — его индекс или −1 (основа LeetCode 739 и 496)
int[] nextGreater(int[] a) {
    int[] res = new int[a.length];
    Arrays.fill(res, -1);
    Deque<Integer> stack = new ArrayDeque<>();            // индексы без ответа; значения не растут от дна к вершине
    for (int i = 0; i < a.length; i++) {
        while (!stack.isEmpty() && a[stack.peek()] < a[i])
            res[stack.pop()] = i;                         // a[i] — первый больший для снятого элемента
        stack.push(i);
    }
    return res;
}
// Daily Temperatures (739): ответ для дня i — res[i] - i, если res[i] != -1, иначе 0
```

**Задачи:** 20 Valid Parentheses · 155 Min Stack · 150 Evaluate Reverse Polish Notation · 739 Daily Temperatures · 496 Next Greater Element I · 84 Largest Rectangle in Histogram (hard).

### 5.6. Бинарный поиск, в том числе по ответу

**Когда:** массив отсортирован: «найти позицию», «первый элемент ≥ x», «сколько элементов меньше x». **Бинпоиск по ответу:** «минимальная скорость, вместимость или время, при которых успеваем», «максимальное X, при котором ещё можно». Признак — проверка «подходит ли X» монотонна: если подходит X, то подходит и любое большее. Ещё один признак — значения до 10⁹: перебор не пройдёт, а log₂(10⁹) ≈ 30 шагов.

```java
// Первый индекс i, где a[i] >= target, или a.length, если такого нет. Работает и с повторами
int lowerBound(int[] a, int target) {
    int lo = 0, hi = a.length;                            // ответ всегда в [lo, hi]
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (a[mid] < target) lo = mid + 1;                // mid точно не ответ
        else hi = mid;                                    // mid может быть ответом
    }
    return lo;
}

// Бинпоиск по ответу: минимальная скорость, чтобы съесть все кучи за h часов (LeetCode 875)
int minEatingSpeed(int[] piles, int h) {
    int lo = 1, hi = Arrays.stream(piles).max().getAsInt();
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (canFinish(piles, h, mid)) hi = mid;           // успеваем — пробуем медленнее
        else lo = mid + 1;                                // не успеваем — нужно быстрее
    }
    return lo;
}

boolean canFinish(int[] piles, int h, int speed) {
    long hours = 0;
    for (int p : piles) hours += (p - 1) / speed + 1;     // деление с округлением вверх при p ≥ 1
    return hours <= h;
}
```

**Как не зациклиться:**
- Ищем **минимальное** подходящее: `ok(mid) → hi = mid`, иначе `lo = mid + 1`; `mid = lo + (hi - lo) / 2`.
- Ищем **максимальное** подходящее: `ok(mid) → lo = mid`, иначе `hi = mid - 1`; тогда `mid = lo + (hi - lo + 1) / 2`. С обычным `mid` при `hi = lo + 1` цикл зациклится.
- Перед кодом проговорить: какая граница точно подходит, какая точно нет, что вернуть, если подходящего нет.

**Задачи:** 704 Binary Search · 35 Search Insert Position · 34 Find First and Last Position of Element in Sorted Array · 33 Search in Rotated Sorted Array · 875 Koko Eating Bananas · 1011 Capacity To Ship Packages Within D Days.

### 5.7. Быстрый и медленный указатели

**Когда:** связный список — середина, цикл, начало цикла, k-й с конца (второй указатель отстаёт на k шагов), палиндромный список. Ещё последовательности вида x → f(x): 202 Happy Number, 287 Find the Duplicate Number. Разворот списка и обнаружение цикла — задачи 5 и 6 ниже.

```java
class ListNode {
    int val;
    ListNode next;
    ListNode(int val) { this.val = val; }
}

// Середина списка (LeetCode 876): fast идёт вдвое быстрее; при чётной длине — вторая из двух средних
ListNode middle(ListNode head) {
    ListNode slow = head, fast = head;
    while (fast != null && fast.next != null) {
        slow = slow.next;
        fast = fast.next.next;
    }
    return slow;
}

// Начало цикла (LeetCode 142): после встречи один указатель — в голову, дальше оба по одному шагу
ListNode cycleStart(ListNode head) {
    ListNode slow = head, fast = head;
    while (fast != null && fast.next != null) {
        slow = slow.next;
        fast = fast.next.next;
        if (slow == fast) {                               // встретились внутри цикла
            ListNode p = head;
            while (p != slow) { p = p.next; slow = slow.next; }
            return p;
        }
    }
    return null;                                          // цикла нет
}

// Удалить n-й узел с конца (LeetCode 19): второй указатель отстаёт на n шагов
ListNode removeNthFromEnd(ListNode head, int n) {
    ListNode dummy = new ListNode(0);                     // фиктивная голова: удаление первого узла — не особый случай
    dummy.next = head;
    ListNode fast = dummy, slow = dummy;
    for (int i = 0; i < n; i++) fast = fast.next;
    while (fast.next != null) {
        fast = fast.next;
        slow = slow.next;
    }
    slow.next = slow.next.next;                           // slow стоит перед удаляемым
    return dummy.next;
}
```

**Задачи:** 876 Middle of the Linked List · 141 Linked List Cycle · 21 Merge Two Sorted Lists (фиктивная голова) · 19 Remove Nth Node From End of List · 142 Linked List Cycle II · 234 Palindrome Linked List · 202 Happy Number.

### 5.8. Дерево: DFS и BFS

**Когда:** глубина, путь, сумма по пути, проверка свойства (BST, симметрия), общий предок → **DFS рекурсией**. Главный вопрос: «что функция должна вернуть для поддерева?» «По уровням», «вид справа», «минимальная глубина» → **BFS очередью**.

```java
class TreeNode {
    int val;
    TreeNode left, right;
    TreeNode(int val) { this.val = val; }
}

// DFS: функция возвращает ответ для поддерева. Высота дерева (LeetCode 104)
int maxDepth(TreeNode root) {
    if (root == null) return 0;                           // база — пустое дерево
    return 1 + Math.max(maxDepth(root.left), maxDepth(root.right));
}

// DFS с границами: проверка BST (LeetCode 98). long — чтобы не споткнуться об Integer.MIN_VALUE и MAX_VALUE
boolean isValidBST(TreeNode root) {
    return isValidBST(root, Long.MIN_VALUE, Long.MAX_VALUE);
}

boolean isValidBST(TreeNode node, long min, long max) {   // все значения поддерева строго в (min, max)
    if (node == null) return true;
    if (node.val <= min || node.val >= max) return false;
    return isValidBST(node.left, min, node.val) && isValidBST(node.right, node.val, max);
}

// Ответ не совпадает с тем, что возвращает рекурсия: диаметр (LeetCode 543). Рекурсия возвращает высоту,
// а ответ копится в поле
int diameter;

int diameterOfBinaryTree(TreeNode root) {
    diameter = 0;
    height(root);
    return diameter;
}

int height(TreeNode node) {
    if (node == null) return 0;
    int l = height(node.left), r = height(node.right);
    diameter = Math.max(diameter, l + r);                 // путь через node: рёбра влево и вправо
    return 1 + Math.max(l, r);
}

// BFS по уровням (LeetCode 102)
List<List<Integer>> levelOrder(TreeNode root) {
    List<List<Integer>> res = new ArrayList<>();
    Deque<TreeNode> queue = new ArrayDeque<>();
    if (root != null) queue.add(root);                    // ArrayDeque не принимает null
    while (!queue.isEmpty()) {
        int size = queue.size();                          // столько узлов на текущем уровне
        List<Integer> level = new ArrayList<>();
        for (int i = 0; i < size; i++) {
            TreeNode node = queue.poll();
            level.add(node.val);
            if (node.left != null) queue.add(node.left);
            if (node.right != null) queue.add(node.right);
        }
        res.add(level);
    }
    return res;
}
```

**Подвох:** вырожденное дерево (по сути список) глубиной 10⁵ уронит рекурсию со `StackOverflowError`. Тогда нужен явный стек или BFS. Сказать об этом интервьюеру — плюс.

**Задачи:** 104 Maximum Depth of Binary Tree · 226 Invert Binary Tree · 100 Same Tree · 102 Binary Tree Level Order Traversal · 98 Validate Binary Search Tree · 543 Diameter of Binary Tree · 236 Lowest Common Ancestor of a Binary Tree.

### 5.9. Сетка и граф: BFS и DFS

**Когда:** «кратчайший путь», «минимум шагов» в сетке или невзвешенном графе — **только BFS**: он обходит вершины слоями, в порядке расстояния. «Острова», «компоненты», «обойти всё» — подойдёт и DFS. «Заражение» или «распространение» из нескольких точек сразу — BFS, в начале в очередь кладут все источники.

```java
// Кратчайший путь в сетке из (0,0) в правый нижний угол: 0 — проход, 1 — стена.
// Возвращает число шагов или −1 (в LeetCode 1091 считают клетки, это на 1 больше, и ходят в 8 сторон)
int shortestPath(int[][] grid) {
    int m = grid.length, n = grid[0].length;
    if (grid[0][0] == 1) return -1;
    int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
    int[][] dist = new int[m][n];
    for (int[] row : dist) Arrays.fill(row, -1);          // −1 — ещё не были
    Deque<int[]> queue = new ArrayDeque<>();
    queue.add(new int[]{0, 0});
    dist[0][0] = 0;
    while (!queue.isEmpty()) {
        int[] cur = queue.poll();
        int r = cur[0], c = cur[1];
        if (r == m - 1 && c == n - 1) return dist[r][c];
        for (int[] d : dirs) {
            int nr = r + d[0], nc = c + d[1];
            if (nr < 0 || nr >= m || nc < 0 || nc >= n) continue;  // за границей
            if (grid[nr][nc] == 1 || dist[nr][nc] != -1) continue; // стена или уже были
            dist[nr][nc] = dist[r][c] + 1;                // помечаем при добавлении, а не при извлечении
            queue.add(new int[]{nr, nc});
        }
    }
    return -1;
}

// Граф списком смежности: кратчайшее число рёбер от start до каждой вершины (−1 — недостижима)
int[] bfs(List<List<Integer>> graph, int start) {
    int[] dist = new int[graph.size()];
    Arrays.fill(dist, -1);
    Deque<Integer> queue = new ArrayDeque<>();
    queue.add(start);
    dist[start] = 0;
    while (!queue.isEmpty()) {
        int v = queue.poll();
        for (int u : graph.get(v)) {
            if (dist[u] != -1) continue;
            dist[u] = dist[v] + 1;
            queue.add(u);
        }
    }
    return dist;
}

// Количество островов (LeetCode 200): каждый запуск обхода с новой клетки суши — новый остров
int numIslands(char[][] grid) {
    int count = 0;
    for (int r = 0; r < grid.length; r++)
        for (int c = 0; c < grid[0].length; c++)
            if (grid[r][c] == '1') {
                count++;
                sink(grid, r, c);
            }
    return count;
}

void sink(char[][] grid, int r, int c) {                  // DFS: «топим» остров, чтобы не посчитать дважды
    if (r < 0 || r >= grid.length || c < 0 || c >= grid[0].length || grid[r][c] != '1') return;
    grid[r][c] = '0';
    sink(grid, r + 1, c);
    sink(grid, r - 1, c);
    sink(grid, r, c + 1);
    sink(grid, r, c - 1);
}
```

**Подвохи:**
- Помечать клетку посещённой нужно при добавлении в очередь. Иначе одна клетка попадёт в очередь много раз.
- `sink` портит входную сетку — спросите, можно ли так. Если нельзя, заведите `boolean[][] visited`.
- Рекурсия DFS на сетке 1000×1000 может уйти на глубину 10⁶ и упасть. На больших сетках безопаснее BFS.

**Задачи:** 200 Number of Islands · 695 Max Area of Island · 733 Flood Fill · 994 Rotting Oranges (BFS из нескольких источников) · 1091 Shortest Path in Binary Matrix · 542 01 Matrix · 133 Clone Graph.

### 5.10. Куча: top-k

**Когда:** «k наибольших / наименьших / самых частых», «k-й по величине», «слить k отсортированных», «медиана потока», жадные задачи вида «каждый раз брать минимальный». Куча размера k даёт O(n log k) вместо O(n log n) у полной сортировки.

```java
// k-й по величине (LeetCode 215): min-куча размера k, на вершине — k-й наибольший
int findKthLargest(int[] nums, int k) {
    PriorityQueue<Integer> heap = new PriorityQueue<>();  // по умолчанию — min-куча
    for (int x : nums) {
        heap.offer(x);
        if (heap.size() > k) heap.poll();                 // выбрасываем самый маленький
    }
    return heap.peek();
}

// k самых частых (LeetCode 347): частоты в HashMap, затем min-куча по частоте
int[] topKFrequent(int[] nums, int k) {
    Map<Integer, Integer> freq = new HashMap<>();
    for (int x : nums) freq.merge(x, 1, Integer::sum);
    PriorityQueue<Map.Entry<Integer, Integer>> heap =
            new PriorityQueue<>((a, b) -> Integer.compare(a.getValue(), b.getValue()));
    for (Map.Entry<Integer, Integer> e : freq.entrySet()) {
        heap.offer(e);
        if (heap.size() > k) heap.poll();
    }
    int[] res = new int[k];
    for (int i = k - 1; i >= 0; i--) res[i] = heap.poll().getKey();   // от частых к редким
    return res;
}

// Слить k отсортированных списков (LeetCode 23): в куче — текущие головы, O(N log k)
ListNode mergeKLists(ListNode[] lists) {
    PriorityQueue<ListNode> heap = new PriorityQueue<>((a, b) -> Integer.compare(a.val, b.val));
    for (ListNode node : lists) if (node != null) heap.offer(node);
    ListNode dummy = new ListNode(0), tail = dummy;
    while (!heap.isEmpty()) {
        ListNode node = heap.poll();
        tail.next = node;
        tail = node;
        if (node.next != null) heap.offer(node.next);
    }
    return dummy.next;
}
```

**Подвохи:**
- Компаратор `(a, b) -> a - b` переполняется на больших и отрицательных числах. Пишите `Integer.compare(a, b)`.
- Max-куча — `new PriorityQueue<>(Comparator.reverseOrder())`.
- Для 215 есть quickselect за O(n) в среднем. Достаточно упомянуть, что он существует.

**Задачи:** 215 Kth Largest Element in an Array · 347 Top K Frequent Elements · 973 K Closest Points to Origin · 23 Merge k Sorted Lists (hard) · 295 Find Median from Data Stream (hard).

### 5.11. Интервалы

**Когда:** отрезки, встречи, бронирования: «пересекаются ли», «объединить», «сколько комнат нужно». Почти всегда решение одно: отсортировать по началу, идти слева направо и сравнивать с последним добавленным отрезком.

```java
// Слить пересекающиеся интервалы (LeetCode 56)
int[][] merge(int[][] intervals) {
    Arrays.sort(intervals, (a, b) -> Integer.compare(a[0], b[0]));   // по началу
    List<int[]> res = new ArrayList<>();
    for (int[] cur : intervals) {
        int[] last = res.isEmpty() ? null : res.get(res.size() - 1);
        if (last != null && cur[0] <= last[1]) last[1] = Math.max(last[1], cur[1]);  // пересекаются — расширяем
        else res.add(new int[]{cur[0], cur[1]});                                     // копия: вход не портим
    }
    return res.toArray(new int[0][]);
}

// Сколько переговорок нужно (LeetCode 253): в куче — время окончания занятых комнат
int minMeetingRooms(int[][] intervals) {
    Arrays.sort(intervals, (a, b) -> Integer.compare(a[0], b[0]));
    PriorityQueue<Integer> ends = new PriorityQueue<>();
    for (int[] in : intervals) {
        if (!ends.isEmpty() && ends.peek() <= in[0]) ends.poll();   // комната освободилась — занимаем её
        ends.offer(in[1]);
    }
    return ends.size();
}
```

**Уточнить у интервьюера:** касание `[1,2]` и `[2,3]` — это пересечение? В `merge` выше касающиеся отрезки сливаются (`<=`). В `minMeetingRooms` встреча, которая кончается в 10:00, освобождает комнату для встречи в 10:00.

**Задачи:** 56 Merge Intervals · 57 Insert Interval · 435 Non-overlapping Intervals · 986 Interval List Intersections · 253 Meeting Rooms II (платная).

### 5.12. TreeMap и TreeSet: ближайший ключ

**Когда:** нужно найти ближайший ключ слева или справа от x, при этом данные меняются: «есть ли бронь, пересекающая [start, end)», «ближайшее значение не больше x», «минимум и максимум с удалениями». Красно-чёрное дерево даёт O(log n) на поиск, вставку и удаление. Вторая задача алгоритмической секции Яндекса, по их же материалам, часто требует хэшей и деревьев поиска. В Java это `TreeMap` и `TreeSet`.

```java
// Бронирования без пересечений (LeetCode 729): соседи по началу ищутся за O(log n)
class MyCalendar {
    private final TreeMap<Integer, Integer> bookings = new TreeMap<>();   // начало → конец, отрезок [start, end)

    boolean book(int start, int end) {
        Map.Entry<Integer, Integer> prev = bookings.floorEntry(start);   // ближайшее начало ≤ start
        Map.Entry<Integer, Integer> next = bookings.ceilingEntry(start); // ближайшее начало ≥ start
        if (prev != null && prev.getValue() > start) return false;       // предыдущая ещё не кончилась
        if (next != null && next.getKey() < end) return false;           // следующая начнётся раньше нашего конца
        bookings.put(start, end);
        return true;
    }
}
```

Методы: `floorKey(x)` — ≤ x, `ceilingKey(x)` — ≥ x, `lowerKey(x)` — < x, `higherKey(x)` — > x. Если ключа нет, возвращают `null`. Ещё есть `firstKey`, `lastKey`, `pollFirstEntry`, `headMap(x)` и `tailMap(x)`. Для `TreeSet` — те же `floor`, `ceiling`, `lower`, `higher`, `first`, `last`.

**Задачи:** 729 My Calendar I · 981 Time Based Key-Value Store · 846 Hand of Straights · 220 Contains Duplicate III (hard).

### 5.13. Backtracking (перебор с возвратом)

**Когда:** «все варианты», «сгенерировать все», перестановки, подмножества, комбинации с суммой, расстановки. Размер входа маленький (≤ 15–20). Схема: **выбрать → рекурсия → отменить выбор**.

```java
// Все подмножества (LeetCode 78), O(2ⁿ · n)
List<List<Integer>> subsets(int[] nums) {
    List<List<Integer>> res = new ArrayList<>();
    backtrack(nums, 0, new ArrayList<>(), res);
    return res;
}

void backtrack(int[] nums, int start, List<Integer> path, List<List<Integer>> res) {
    res.add(new ArrayList<>(path));                       // КОПИЯ: path дальше будет меняться
    for (int i = start; i < nums.length; i++) {
        path.add(nums[i]);                                // выбрать
        backtrack(nums, i + 1, path, res);                // рекурсия
        path.remove(path.size() - 1);                     // отменить выбор (remove(int) — по индексу)
    }
}

// Все перестановки (LeetCode 46), O(n! · n): used[] — какие элементы уже в пути
List<List<Integer>> permute(int[] nums) {
    List<List<Integer>> res = new ArrayList<>();
    permute(nums, new boolean[nums.length], new ArrayList<>(), res);
    return res;
}

void permute(int[] nums, boolean[] used, List<Integer> path, List<List<Integer>> res) {
    if (path.size() == nums.length) {
        res.add(new ArrayList<>(path));
        return;
    }
    for (int i = 0; i < nums.length; i++) {
        if (used[i]) continue;
        used[i] = true;
        path.add(nums[i]);
        permute(nums, used, path, res);
        used[i] = false;
        path.remove(path.size() - 1);
    }
}

// Все правильные скобочные последовательности из n пар (LeetCode 22) — задача из материалов Яндекса
List<String> generateParenthesis(int n) {
    List<String> res = new ArrayList<>();
    generate(new StringBuilder(), 0, 0, n, res);
    return res;
}

void generate(StringBuilder sb, int open, int close, int n, List<String> res) {
    if (sb.length() == 2 * n) {
        res.add(sb.toString());
        return;
    }
    if (open < n) {
        sb.append('(');
        generate(sb, open + 1, close, n, res);
        sb.deleteCharAt(sb.length() - 1);                 // откат: без него ветки испортят друг другу строку
    }
    if (close < open) {
        sb.append(')');
        generate(sb, open, close + 1, n, res);
        sb.deleteCharAt(sb.length() - 1);
    }
}
```

**Типичная ошибка, по материалам Яндекса:** изменить общее состояние (строку, список) и не вернуть его после рекурсивного вызова. Вторая — положить в результат сам `path`, а не копию.

**Задачи:** 78 Subsets · 46 Permutations · 22 Generate Parentheses · 17 Letter Combinations of a Phone Number · 39 Combination Sum · 79 Word Search.

### 5.14. Динамическое программирование: база

**Когда:** «сколько способов», «минимальная или максимальная стоимость», «можно ли». Ответ складывается из ответов на подзадачи поменьше. Лобовое решение — рекурсия, которая много раз считает одно и то же: это «пересчитываю», и лечится оно запоминанием.

Рецепт из пяти вопросов:
1. Что такое `dp[i]` словами?
2. Как `dp[i]` выражается через предыдущие значения (переход)?
3. Какая база?
4. В каком порядке считать?
5. Где лежит ответ?

Если нужны только одно-два предыдущих значения, массив заменяют двумя переменными — память O(1). Мемоизация сверху вниз (рекурсия + кэш в `HashMap` или массиве) даёт ту же сложность, и её часто проще придумать.

```java
// Сколько способов подняться на n ступенек шагами 1 или 2 (LeetCode 70): dp[i] = dp[i-1] + dp[i-2]
int climbStairs(int n) {
    int prev = 1, cur = 1;                                // dp[0] = 1, dp[1] = 1
    for (int i = 2; i <= n; i++) {
        int next = prev + cur;
        prev = cur;
        cur = next;
    }
    return cur;
}

// Грабитель (LeetCode 198): dp[i] = max(dp[i-1], dp[i-2] + nums[i]) — пропустить дом или взять
int rob(int[] nums) {
    int prev = 0, cur = 0;                                // лучшие суммы до i-2 и до i-1
    for (int x : nums) {
        int next = Math.max(cur, prev + x);
        prev = cur;
        cur = next;
    }
    return cur;
}

// Размен монет (LeetCode 322): dp[s] — минимум монет на сумму s, −1 — нельзя набрать
int coinChange(int[] coins, int amount) {
    int[] dp = new int[amount + 1];
    Arrays.fill(dp, Integer.MAX_VALUE);                   // MAX_VALUE — «пока нельзя»
    dp[0] = 0;
    for (int s = 1; s <= amount; s++)
        for (int c : coins)
            if (c <= s && dp[s - c] != Integer.MAX_VALUE)
                dp[s] = Math.min(dp[s], dp[s - c] + 1);
    return dp[amount] == Integer.MAX_VALUE ? -1 : dp[amount];
}

// Двумерное DP: наибольшая общая подпоследовательность (LeetCode 1143). dp[i][j] — для префиксов длины i и j
int longestCommonSubsequence(String a, String b) {
    int[][] dp = new int[a.length() + 1][b.length() + 1];
    for (int i = 1; i <= a.length(); i++)
        for (int j = 1; j <= b.length(); j++)
            dp[i][j] = a.charAt(i - 1) == b.charAt(j - 1)
                    ? dp[i - 1][j - 1] + 1
                    : Math.max(dp[i - 1][j], dp[i][j - 1]);
    return dp[a.length()][b.length()];
}
```

**Задачи:** 70 Climbing Stairs · 198 House Robber · 53 Maximum Subarray (Кадане, задача 9 ниже) · 62 Unique Paths · 322 Coin Change · 300 Longest Increasing Subsequence · 1143 Longest Common Subsequence.

### 5.15. Топологическая сортировка

**Когда:** зависимости, порядок сборки или прохождения курсов, «можно ли выполнить все задачи», поиск цикла в ориентированном графе. Алгоритм Кана: считаем, сколько рёбер входит в каждую вершину; вершины без входящих рёбер кладём в очередь; снимаем вершину — уменьшаем счётчик её соседям.

```java
// Порядок курсов (LeetCode 210). Пустой массив — есть цикл, выполнить все нельзя
int[] findOrder(int n, int[][] prerequisites) {
    List<List<Integer>> graph = new ArrayList<>();
    for (int i = 0; i < n; i++) graph.add(new ArrayList<>());
    int[] indegree = new int[n];
    for (int[] p : prerequisites) {                       // p = {курс, что нужно пройти до него}
        graph.get(p[1]).add(p[0]);
        indegree[p[0]]++;
    }
    Deque<Integer> queue = new ArrayDeque<>();
    for (int v = 0; v < n; v++) if (indegree[v] == 0) queue.add(v);
    int[] order = new int[n];
    int k = 0;
    while (!queue.isEmpty()) {
        int v = queue.poll();
        order[k++] = v;
        for (int u : graph.get(v))
            if (--indegree[u] == 0) queue.add(u);         // все зависимости u выполнены
    }
    return k == n ? order : new int[0];                   // не все вершины вышли — есть цикл
}
```

**Задачи:** 207 Course Schedule · 210 Course Schedule II · 269 Alien Dictionary (платная, hard).

### 5.16. Union-Find (по желанию)

**Когда:** «объединить группы», «связаны ли a и b», число компонент при добавлении рёбер, лишнее ребро, которое создаёт цикл. Альтернатива BFS и DFS, когда рёбра приходят по одному.

```java
// Система непересекающихся множеств: почти O(1) на операцию
class UnionFind {
    private final int[] parent, size;
    int components;

    UnionFind(int n) {
        parent = new int[n];
        size = new int[n];
        for (int i = 0; i < n; i++) {
            parent[i] = i;
            size[i] = 1;
        }
        components = n;
    }

    int find(int x) {
        while (parent[x] != x) {
            parent[x] = parent[parent[x]];                // сжатие пути: перевешиваем через уровень
            x = parent[x];
        }
        return x;
    }

    boolean union(int a, int b) {                         // false — уже были в одном множестве
        int ra = find(a), rb = find(b);
        if (ra == rb) return false;
        if (size[ra] < size[rb]) { int t = ra; ra = rb; rb = t; }
        parent[rb] = ra;                                  // меньшее дерево — под большее
        size[ra] += size[rb];
        components--;
        return true;
    }
}
```

**Задачи:** 547 Number of Provinces · 684 Redundant Connection (лишнее ребро — то, на котором `union` вернул `false`) · 990 Satisfiability of Equality Equations · 721 Accounts Merge.

## 6. Протокол live coding и Java-шпаргалка

### Протокол на одну задачу

Время дано для секции на 45 минут с одной задачей. В Яндексе две задачи за час ([раздел 7](#7-алгоритмическая-секция-в-яндексе)), поэтому каждый шаг примерно вдвое короче.

| Шаг | Что делать | Время |
|---|---|---|
| 1. Понять условие | Пересказать своими словами. Спросить про размер входа и диапазон значений (отрицательные? переполнение?), пустой вход, повторы, отсортирован ли вход, что вернуть, если ответа нет, можно ли менять вход. Придумать 2–3 примера, один из них — крайний | 3–5 мин |
| 2. Лобовое решение вслух | «В лоб — перебрать все пары, O(n²)». Код не писать, если не просят | 1–2 мин |
| 3. Улучшить и согласовать | Найти дорогое место ([раздел 3](#3-от-лобового-решения-к-оптимальному)), назвать идею одной фразой и сложность. Спросить: «Такой подход подходит? Пишу?» | 5–10 мин |
| 4. Код | Понятные имена, без лишних особых случаев. Вслух говорить, что пишете и зачем | 10–15 мин |
| 5. Проверка руками | Пройти свой пример построчно и выписать значения переменных, потом крайние случаи. Нашли баг — сказать о нём и исправить | 5 мин |
| 6. Сложность | Время и память. Что можно улучшить и какой ценой | 1–2 мин |

**Фразы-заготовки:**
- «Уточню: массив может быть пустым? Числа бывают отрицательными? Какой размер входа?»
- «В лоб — … за O(n²). Внутренний цикл ищет …, его можно заменить на HashMap: будет O(n) по времени и O(n) по памяти. Пишу так?»
- «Прогоню на примере [2, 7, 11], target = 9: i = 0, в мапе пусто, кладу 2…»
- «Итого O(n) по времени и O(n) по памяти. Без доп. памяти можно за O(n log n) через сортировку и два указателя.»

**Если застряли:** проговорите, что уже понятно, вернитесь к лобовому решению и к таблицам из [раздела 4](#4-как-выбрать-приём-две-таблицы). Молчать хуже, чем рассуждать вслух неидеально. Подсказка интервьюера — нормальная часть секции, а не провал.

### Как проверить код без запуска

1. Взять маленький пример из 3–5 элементов и выписать таблицу: шаг, значения переменных, содержимое структуры (мапы, стека, очереди).
2. Прогнать крайние случаи: пустой вход, один элемент, все элементы одинаковые, ответ в самом начале или в самом конце, ответа нет.
3. Проверить границы: `<` или `<=`, длина окна `r - l + 1`, обработан ли последний элемент, обновлён ли ответ после цикла.
4. Проверить переполнение и деление: суммы в `long`, `mid = lo + (hi - lo) / 2`, деление на ноль.

### Крайние случаи и частые баги

**Крайние случаи:** пустой массив или строка; один элемент; все элементы одинаковые; отрицательные числа и ноль; переполнение `int` (сумма 10⁵ чисел до 10⁹ уже не влезает); уже отсортированный вход и обратный порядок; ответа нет; повторы; `null` — спросить, бывает ли.

**Частые баги:**
- Ответ обновляют только на «разрыве» серии и забывают последнюю серию после цикла. Надёжнее обновлять ответ на каждом шаге.
- Ошибка на единицу: длина окна `r - l + 1`, граница `i + k <= n`.
- Сравнение `Integer` через `==`.
- Компаратор `(a, b) -> a - b` переполняется. Нужен `Integer.compare(a, b)`.
- В backtracking в результат кладут сам `path`, а не копию, или забывают откатить выбор.
- Коллекцию меняют во время обхода for-each — `ConcurrentModificationException`.
- Строку собирают через `+=` в цикле — это O(n²), нужен `StringBuilder`.
- В `ArrayDeque` нельзя класть `null`. `pop()` на пустом стеке бросает исключение, а `peek()` возвращает `null`.
- Остаток от деления отрицательного числа отрицательный: `-7 % 3 == -1`. Нужен `Math.floorMod`.
- Рекурсия глубиной 10⁵ падает со `StackOverflowError`. Нужен явный стек или BFS.

### Java-шпаргалка

```java
// Map
Map<String, Integer> cnt = new HashMap<>();
cnt.merge(key, 1, Integer::sum);                          // счётчик +1
int c = cnt.getOrDefault(key, 0);
Map<String, List<String>> groups = new HashMap<>();
groups.computeIfAbsent(key, k -> new ArrayList<>()).add(value);   // группировка
Map<Integer, Integer> first = new HashMap<>();
first.putIfAbsent(x, i);                                  // запомнить первое появление
for (Map.Entry<String, Integer> e : cnt.entrySet()) {
    String name = e.getKey();
    int count = e.getValue();
}

// Стек и очередь — ArrayDeque (не Stack и не LinkedList)
Deque<Integer> stack = new ArrayDeque<>();
stack.push(x); stack.peek(); stack.pop();                 // вершина стека — голова deque
Deque<Integer> queue = new ArrayDeque<>();
queue.offer(x); queue.peek(); queue.poll();

// Куча
PriorityQueue<Integer> minHeap = new PriorityQueue<>();
PriorityQueue<Integer> maxHeap = new PriorityQueue<>(Comparator.reverseOrder());
PriorityQueue<int[]> byFirst = new PriorityQueue<>((a, b) -> Integer.compare(a[0], b[0]));

// TreeMap и TreeSet — всё за O(log n)
TreeMap<Integer, String> tm = new TreeMap<>();
tm.put(x, value);
tm.floorKey(x); tm.ceilingKey(x);                         // ближайший ключ ≤ x и ≥ x (или null)
tm.lowerKey(x); tm.higherKey(x);                          // строго < x и строго > x
tm.firstKey(); tm.lastKey(); tm.pollFirstEntry();         // firstKey и lastKey на пустой карте бросают исключение

// Сортировка
Arrays.sort(arr);                                         // int[] по возрастанию
Arrays.sort(intervals, (a, b) -> Integer.compare(a[0], b[0]));   // int[][] по первому элементу
Integer[] boxed = {3, 1, 2};
Arrays.sort(boxed, Collections.reverseOrder());           // по убыванию — только для объектов, не для int[]
words.sort(Comparator.comparingInt(String::length).thenComparing(Comparator.naturalOrder()));

// Строки и символы
int[] freq = new int[26];
freq[ch - 'a']++;                                         // частоты строчных латинских букв
int digit = ch - '0';
StringBuilder sb = new StringBuilder();
sb.append(x).append(',');
sb.setLength(sb.length() - 1);                            // убрать последний символ
sb.reverse();
String s = sb.toString();
char[] chars = s.toCharArray();
String back = new String(chars);
Character.isLetterOrDigit(ch); Character.isDigit(ch); Character.toLowerCase(ch);
String joined = String.join(",", words);
String[] parts = line.trim().split("\\s+");               // split принимает регулярное выражение

// Массивы, числа, преобразования
int[] a = new int[n];
Arrays.fill(a, -1);
int[][] grid = new int[m][n];
int[] part = Arrays.copyOfRange(a, from, to);             // [from, to)
System.out.println(Arrays.toString(a));                   // печать массива при отладке
long sum = 0;                                             // суммы — в long
int mod = Math.floorMod(-7, 3);                           // 2, а -7 % 3 == -1
int[] fromList = list.stream().mapToInt(Integer::intValue).toArray();
List<Integer> fromArray = Arrays.stream(a).boxed().toList();     // Java 16+
```

### Сложность методов стандартной библиотеки

На секции в Яндексе прямо просят объяснить, почему выбран метод и какая у него сложность ([раздел 7](#7-алгоритмическая-секция-в-яндексе)).

| Операция | Сложность |
|---|---|
| `HashMap`, `HashSet`: `get`, `put`, `containsKey`, `remove` | O(1) в среднем |
| `TreeMap`, `TreeSet`: `get`, `put`, `remove`, `floorKey`, `ceilingKey`, `firstKey` | O(log n) |
| `PriorityQueue`: `offer`, `poll` | O(log n); `peek` — O(1); `remove(Object)` и `contains` — O(n) |
| `ArrayList`: `get`, `set`, `add` в конец | O(1), `add` — амортизированно |
| `ArrayList`: `add(0, x)`, `remove(0)`, `contains`, `indexOf` | O(n) |
| `ArrayDeque`: добавить или снять с любого конца | O(1) |
| `LinkedList.get(i)` | O(n) |
| `Arrays.sort`, `Collections.sort`, `List.sort` | O(n log n) |
| `String`: `substring`, `toCharArray`, `equals`, `+` | O(длины): строка копируется или сравнивается целиком |
| `+=` для строки в цикле | O(n²) суммарно, нужен `StringBuilder` |
| `Arrays.equals` двух `int[26]` | O(26) = O(1) |

## 7. Алгоритмическая секция в Яндексе

Собрано по официальным материалам Яндекса, проверено 23.11.2026:
- [Как мы нанимаем бэкенд-разработчиков](https://yandex.ru/jobs/interview/backend) — страница найма, 2026 год;
- [Как пройти алгоритмическое собеседование в Яндекс](https://yandex.ru/jobs/interview/algorithms) — гайд от авторов задач;
- [Алгоритмические собеседования в Яндексе: как подготовиться и чего ожидать](https://education.yandex.ru/journal/algoritmicheskie-sobesedovaniya-v-yandekse-kak-podgotovitsya-i-chego-ozhidat) — Яндекс Образование, 19.12.2024;
- [Как проходят алгоритмические секции на собеседованиях в Яндекс](https://habr.com/ru/companies/yandex/articles/449890/) — блог Яндекса на Хабре, 2019, с тренировочным контестом.

**Коротко:** две алгоритмические задачи за час в онлайн-редакторе, без IDE. Сначала идея и сложность словами, потом код, потом проверка руками на тестах. Оценивают не только итог, но и процесс: как быстро нашли решение, как объяснили, сколько багов в коде и находите ли вы их сами.

### Формат секции

| Что | Как | Источник |
|---|---|---|
| Название этапа у бэкендеров | «Проверка базовых технических навыков» — две алгоритмические задачи | страница найма |
| Длительность | 1,5 часа: час на задачи и 30 минут на организационные вопросы | страница найма |
| Где | Zoom или Телемост, нужны демонстрация экрана и камера. Встречу могут записать, чтобы расшифровать AI-инструментами | страница найма |
| Редактор | онлайн-редактор на любом языке. Своя IDE — только на секции кодинга (ниже) | страница найма |
| Запуск кода | скомпилировать и запустить нельзя, код проверяют в уме на тестах | Яндекс Образование, 2024. ⚠ На странице 2026 года прямо не сказано — уточнить у рекрутера |
| Язык | обычно любой знакомый. Язык секций выбирают с рекрутером на HR-скрининге | гайд, страница найма |
| Сигнатуры методов | наизусть знать не нужно, но надо объяснить, почему выбран метод и какая у него сложность | гайд, страница найма |
| Задачи | первая проще: один-два прохода по массиву, возможно, сортировка. Вторая сложнее: хэш-таблицы, деревья поиска. Если останется время — третья, необязательная: нужна только идея, код не нужен | Яндекс Образование |
| Ход | идея словами → вопросы интервьюера и сложность → код → пара минут на перепроверку | Яндекс Образование |
| Темп | решение первой задачи желательно иметь примерно через полчаса | Яндекс Образование |

### Что оценивают

- Как быстро вы придумали решение и насколько понятно его объяснили.
- Умеете ли вы оценить сложность — и алгоритма, и методов стандартной библиотеки ([таблица](#сложность-методов-стандартной-библиотеки)).
- Сколько багов в коде и находите ли вы их сами. Ошибку, которую кандидат нашёл и исправил сам, засчитывают как внимательность.
- Внимание к деталям и крайним случаям. Наводящий вопрос интервьюера про крайний случай — не провал.
- Ясность кода: без дублирования, с минимумом особых случаев.

### Советы авторов задач (пересказ)

1. **Начинать с тестовых примеров, а не с кода.** Для задачи «самая длинная серия единиц в двоичном массиве» это, например, `[1,1,0,1] → 2`, `[0,0] → 0`, `[] → 0`, `[1,1,1] → 3`. Примеры проверяют, что условие понято, и сразу дают крайние случаи.
2. **Продумать алгоритм до кода:** описать логику словами, решить, какие переменные и структуры нужны. Самая частая ошибка — начать писать, не додумав решение. Пять лишних минут на размышление дешевле, чем двадцать минут на переписывание.
3. **Писать компактно и без лишних особых случаев.** Не начинать с `if (a.length == 0) return 0`, если общий алгоритм и так вернёт 0 на пустом входе (сравните с `removeDuplicates` в [5.2](#52-два-указателя)).
4. **Проверить код:** прогнать придуманные тесты, мысленно выполняя код и следя за значениями переменных.
5. **В рекурсии следить за состоянием между вызовами.** Их пример ошибки: в генерации скобок строку изменили и не откатили ([5.13](#513-backtracking-перебор-с-возвратом)).
6. **Следить за инвариантами.** Если решение «за один проход», убедиться, что массив пройден целиком и ровно один раз.
7. **Ошиблись — без паники:** найти ошибку на тестах, объяснить и исправить. Если на проблему указал интервьюер, разобраться и исправить.

**Типичные ошибки кандидатов (Яндекс Образование):**
- долго разбирают первую задачу, и на вторую не хватает времени;
- пропускают крайние случаи: пустой массив, пустую строку, ноль;
- не видят свою ошибку без подсказки, потому что не умеют проверять код без запуска.

### Что повторить и где тренироваться (по советам Яндекса)

- LeetCode easy и medium с тегами Array, String, Tree, Binary Search, Hash Table, Depth-First Search, Breadth-First Search, Two Pointers, Stack, Backtracking. Лучше быстро и без ошибок решать easy и medium, чем браться за hard.
- [CodeRun](https://coderun.yandex.ru/) и Яндекс Контест — тренажёры Яндекса. Ещё есть [тренировочный контест](https://contest.yandex.ru/contest/8458/enter/) к статье на Хабре: шесть задач, все из таблицы ниже.
- Темы: строки и массивы, хэш-таблицы, обход двоичного дерева, реализация простых примитивов вроде счётчиков и кэшей (LRU — задача 11 ниже).
- Писать код без IDE (Яндекс советует даже попробовать на бумаге) и проговаривать решение вслух.
- Codeforces — учиться искать ошибки в чужих решениях, то есть проверять код в уме.

### Задачи из официальных материалов Яндекса

| Задача | Где упомянута | На LeetCode |
|---|---|---|
| Самая длинная серия единиц в двоичном массиве | гайд, контест | 485 Max Consecutive Ones |
| Являются ли две строки анаграммами | гайд, контест | 242 Valid Anagram ([5.1](#51-хэш-и-частоты)) |
| Все правильные скобочные последовательности длины 2n | гайд, контест | 22 Generate Parentheses ([5.13](#513-backtracking-перебор-с-возвратом)) |
| Сколько символов строки S входят в строку J | контест | 771 Jewels and Stones |
| Удалить повторы из отсортированного массива | контест | 26 Remove Duplicates from Sorted Array ([5.2](#52-два-указателя)) |
| Слить k отсортированных массивов | контест | 23 Merge k Sorted Lists ([5.10](#510-куча-top-k)) |
| Самый длинный неубывающий подотрезок массива | Яндекс Образование | похожа на 674 Longest Continuous Increasing Subsequence (там строго возрастающий) |
| Сколько подмассивов, в которых все значения различны | Яндекс Образование | окно: `countDistinctSubarrays` в [5.3](#53-скользящее-окно) |

### Что не удалось подтвердить официально

- **Можно ли запускать код.** Статья Яндекс Образования 2024 года говорит, что нельзя. На странице найма 2026 года сказано только «онлайн-редактор», про запуск — ни слова.
- **Есть ли в редакторе подсветка и автодополнение.** Про алгоритмическую секцию не сказано. Про секцию кодинга на C++ сказано, что она проходит без компилятора и без автоподсказок.
- **Сколько будет алгоритмических секций** и будет ли отдельная секция кодинга на Java. На странице сказано, что процесс подстраивают под опыт и позицию, а детали сообщает рекрутер.

Готовиться к худшему: писать без автодополнения и без запуска. Вопросы рекрутеру: язык секции, редактор, можно ли запускать код, сколько алгоритмических секций, будет ли секция кодинга на Java.

### Другие секции бэкендера (кратко)

- **Секция кодинга на Java** — 1,5 часа в своей IDE с демонстрацией экрана. Практическая задача: написать несколько классов с нуля или доработать готовый код и покрыть его unit-тестами. Два варианта: базовая промышленная разработка или углублённая Java с многопоточностью и примитивами синхронизации ([concurrency.md](concurrency.md)). AI-ассистенты нужно выключить: Copilot, JetBrains AI Assistant, Full Line Code Completion. Обычное автодополнение оставить можно. Заранее подготовить пустой проект с JUnit и проверить, что тесты запускаются.
- **Архитектурная** — для тех, у кого есть опыт проектирования высоконагруженных распределённых систем ([system-design.md](system-design.md)).
- **Про опыт** — разговор о крупном проекте за последние 2–3 года, по схеме STAR ([behavioral.md](behavioral.md)).
- **Финалы** с командами, обычно от одной до трёх встреч, затем презентация оффера. Весь цикл занимает примерно 3–4 недели.

## 8. План на неделю до алгоритмической секции

**Коротко:** 7 дней по 1–1,5 часа. Приёмы идут по убыванию пользы: хэш, два указателя, окно, стек, бинарный поиск, деревья, BFS/DFS, куча, интервалы. DP — только база. Каждый день — три новые задачи и перерешивание задач прошлых дней.

**Распорядок дня:**
1. 10 минут — прочитать приём в [разделе 5](#5-каталог-приёмов) и написать шаблон по памяти, без IDE.
2. 45–60 минут — три задачи по 20 минут с таймером. Вслух, по [протоколу](#протокол-на-одну-задачу), в редакторе без автодополнения и без запуска. Запускать только после того, как решение «сдано»: сколько багов найдут компилятор и тесты, столько вы пропустили бы на секции.
3. 10–15 минут — перерешать задачи из колонки «Повтор». Записать для каждой задачи идею одной фразой и свои ошибки.

Не решилась за 20–25 минут — прочитать разбор, понять идею, записать её одной фразой и перерешать на следующий день без подсказок.

| День | Приёмы | Новые задачи | Если останется время | Повтор |
|---|---|---|---|---|
| 1 | [раздел 3](#3-от-лобового-решения-к-оптимальному), хэш и частоты, один проход | 1 Two Sum, 242 Valid Anagram, 485 Max Consecutive Ones | 49, 128 | — |
| 2 | два указателя, скользящее окно | 167, 3, 209 | 15, 567 | 1, 242 |
| 3 | префиксные суммы, стек | 560, 20, 739 | 525, 496 | 3, 209 |
| 4 | бинарный поиск, бинпоиск по ответу | 704 (через `lowerBound`), 33, 875 | 35, 1011 | 560, 739 |
| 5 | дерево: DFS и BFS; быстрый и медленный указатели | 104, 102, 98 | 543, 141 | 33, 875 |
| 6 | сетка и граф, куча | 200, 994, 215 | 347, 23 | 102, 98 |
| 7 | интервалы, DP — база, пробная секция | 56, 70, 198 | 322 | задачи с ошибками за неделю |

**Последний день перед секцией:**
- пробная секция: две незнакомые задачи (easy и medium) за час, вслух, без запуска;
- повторить таблицы [раздела 4](#4-как-выбрать-приём-две-таблицы) и [шпаргалку](#java-шпаргалка); новое не учить;
- проверить Zoom или Телемост: демонстрацию экрана и камеру.

**Если до секции меньше недели:** дни 1–4 обязательны, на них держатся первая и вторая задачи. Из дней 5–6 взять по одной задаче на тему. Пробную секцию не пропускать.

## 9. Задачи с решениями

<details><summary>1. Two Sum — найти индексы двух чисел с суммой target</summary>

```java
int[] twoSum(int[] nums, int target) {
    Map<Integer, Integer> seen = new HashMap<>();          // значение → индекс
    for (int i = 0; i < nums.length; i++) {
        Integer j = seen.get(target - nums[i]);
        if (j != null) return new int[]{j, i};
        seen.put(nums[i], i);
    }
    return new int[0];
}
```
O(n) время, O(n) память. Перебор пар — O(n²).
</details>

<details><summary>2. Правильная скобочная последовательность: "({[]})" → true, "(]" → false</summary>

```java
boolean isValid(String s) {
    Deque<Character> stack = new ArrayDeque<>();
    for (char c : s.toCharArray()) {
        switch (c) {
            case '(' -> stack.push(')');
            case '[' -> stack.push(']');
            case '{' -> stack.push('}');
            default -> { if (stack.isEmpty() || stack.pop() != c) return false; }
        }
    }
    return stack.isEmpty();
}
```
</details>

<details><summary>3. Первый неповторяющийся символ строки</summary>

```java
Character firstUnique(String s) {
    Map<Character, Integer> counts = new LinkedHashMap<>();   // сохраняет порядок
    for (char c : s.toCharArray()) counts.merge(c, 1, Integer::sum);
    return counts.entrySet().stream()
            .filter(e -> e.getValue() == 1)
            .map(Map.Entry::getKey)
            .findFirst().orElse(null);
}
```
</details>

<details><summary>4. Сгруппировать анаграммы: ["eat","tea","tan","ate","nat"] → [[eat,tea,ate],[tan,nat]]</summary>

```java
Collection<List<String>> groupAnagrams(List<String> words) {
    return words.stream().collect(Collectors.groupingBy(w -> {
        char[] chars = w.toCharArray();
        Arrays.sort(chars);
        return new String(chars);                              // ключ — отсортированные буквы
    })).values();
}
```
</details>

<details><summary>5. Развернуть односвязный список</summary>

```java
Node reverse(Node head) {
    Node prev = null;
    while (head != null) {
        Node next = head.next;
        head.next = prev;
        prev = head;
        head = next;
    }
    return prev;
}
```
O(n), O(1) памяти.
</details>

<details><summary>6. Есть ли цикл в связном списке?</summary>

Алгоритм Флойда («черепаха и заяц»): медленный указатель шагает на 1, быстрый на 2; если встретились — цикл есть.

```java
boolean hasCycle(Node head) {
    Node slow = head, fast = head;
    while (fast != null && fast.next != null) {
        slow = slow.next;
        fast = fast.next.next;
        if (slow == fast) return true;
    }
    return false;
}
```
</details>

<details><summary>7. Слить два отсортированных массива</summary>

```java
int[] merge(int[] a, int[] b) {
    int[] r = new int[a.length + b.length];
    int i = 0, j = 0, k = 0;
    while (i < a.length && j < b.length) r[k++] = a[i] <= b[j] ? a[i++] : b[j++];
    while (i < a.length) r[k++] = a[i++];
    while (j < b.length) r[k++] = b[j++];
    return r;
}
```
</details>

<details><summary>8. Самая длинная подстрока без повторяющихся символов</summary>

```java
int lengthOfLongestSubstring(String s) {
    Map<Character, Integer> lastIndex = new HashMap<>();
    int best = 0, left = 0;
    for (int right = 0; right < s.length(); right++) {
        char c = s.charAt(right);
        Integer prev = lastIndex.put(c, right);
        if (prev != null && prev >= left) left = prev + 1;    // сдвигаем левую границу окна
        best = Math.max(best, right - left + 1);
    }
    return best;
}
```
Скользящее окно, O(n).
</details>

<details><summary>9. Максимальная сумма подмассива (алгоритм Кадане)</summary>

```java
int maxSubArray(int[] nums) {
    int best = nums[0], current = nums[0];
    for (int i = 1; i < nums.length; i++) {
        current = Math.max(nums[i], current + nums[i]);   // продолжить отрезок или начать заново
        best = Math.max(best, current);
    }
    return best;
}
```
</details>

<details><summary>10. Топ-K самых частых слов</summary>

```java
List<String> topK(List<String> words, int k) {
    return words.stream()
            .collect(Collectors.groupingBy(w -> w, Collectors.counting()))
            .entrySet().stream()
            .sorted(Map.Entry.<String, Long>comparingByValue().reversed())
            .limit(k)
            .map(Map.Entry::getKey)
            .toList();
}
```
O(n log n). Для огромных данных — `PriorityQueue` размера k: O(n log k).
</details>

<details><summary>11. LRU-кэш</summary>

Самый короткий ответ — `LinkedHashMap` с `accessOrder = true` и `removeEldestEntry` ([collections.md](collections.md#5-другие-реализации-map)). Если просят «без готового» — `HashMap<K, Node>` + двусвязный список: при доступе узел переносится в голову, при переполнении удаляется хвост. Все операции O(1). Потокобезопасность — отдельный вопрос (блокировка или Caffeine).
</details>

<details><summary>12. Проверить, является ли строка палиндромом (игнорируя регистр и не буквы)</summary>

```java
boolean isPalindrome(String s) {
    int i = 0, j = s.length() - 1;
    while (i < j) {
        if (!Character.isLetterOrDigit(s.charAt(i))) { i++; continue; }
        if (!Character.isLetterOrDigit(s.charAt(j))) { j--; continue; }
        if (Character.toLowerCase(s.charAt(i)) != Character.toLowerCase(s.charAt(j))) return false;
        i++; j--;
    }
    return true;
}
```
</details>

## Где и как тренироваться

**Где:**
- LeetCode: списки NeetCode 150 и Grind 75 — в них задачи разложены по приёмам. Ещё есть Top Interview 150. Для backend-собеседований обычно хватает easy и medium.
- Тренажёры Яндекса — CodeRun и Яндекс Контест ([раздел 7](#что-повторить-и-где-тренироваться-по-советам-яндекса)).

**Как:**
- Решать по приёмам, а не вразнобой: несколько задач на один приём подряд, пока шаблон не станет привычным.
- Тратить на задачу не больше 20–25 минут, потом читать разбор.
- После задачи записать идею одной фразой. Например: «окно: расширяю вправо; когда появился повтор, сдвигаю левую границу».
- Перерешать задачу через день и через неделю, без подсказок.
- Иногда писать без автодополнения и без запуска — как на секции.
- Решать вслух, будто рядом сидит интервьюер.
