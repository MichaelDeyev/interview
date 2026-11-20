# Алгоритмы и задачи на live coding

[← Оглавление](README.md) · Структуры данных — [collections.md](collections.md#10-структуры-данных--база)

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

## 3. Приёмы, которые решают большинство задач

- **HashMap / HashSet** — «видел ли я это раньше?», подсчёт частот → O(n) вместо O(n²).
- **Два указателя** — с двух концов отсортированного массива или «быстрый и медленный» (поиск цикла в списке).
- **Скользящее окно** — подмассивы/подстроки с условием («самая длинная подстрока без повторов»).
- **Стек** — скобки, «следующий больший элемент», обратная польская запись.
- **Сортировка + проход** — часто проще, чем кажется: O(n log n).
- **BFS / DFS** — графы, деревья, лабиринты.
- **Префиксные суммы** — сумма на отрезке за O(1).

Как вести себя на live coding: повторить условие своими словами, уточнить ограничения (размер входа, null, пустой массив, дубликаты, отрицательные числа), проговорить простое решение и его сложность, потом улучшить, написать код, **прогнать руками на примере и крайних случаях**.

## 4. Задачи с решениями

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

## Где тренироваться

LeetCode (списки «Top Interview 150», «NeetCode 150»), раздел Easy/Medium — для backend-собеседований обычно достаточно.
