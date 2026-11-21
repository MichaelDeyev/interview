# SQL — с нуля до уровня собеседования

[← Оглавление](README.md) · Теория БД (изоляция, индексы, блокировки) — в [databases.md](databases.md)

Как пользоваться: сначала прочитать разделы 1–6, потом решать задачи из раздела 8, **не подглядывая** в ответ (он спрятан под «Решение»). Все примеры — PostgreSQL, но 95% работает в любой СУБД.

## 0. Учебная схема

Все примеры ниже — на этих таблицах. Её стоит один раз создать у себя (`docker run -d --name pg -e POSTGRES_PASSWORD=pg -p 5433:5432 postgres`, подключение: localhost:5433, пользователь `postgres`, пароль `pg`; порт 5433 — чтобы не конфликтовать с локально установленным PostgreSQL) и прогонять запросы руками — так SQL запоминается в разы быстрее.

```sql
create table departments (
    id   bigint primary key,
    name text   not null
);

create table employees (
    id            bigint primary key,
    name          text    not null,
    salary        numeric(12, 2) not null,
    department_id bigint  references departments (id),   -- может быть NULL: сотрудник без отдела
    manager_id    bigint  references employees (id),     -- ссылка на начальника (self-reference)
    hired_at      date    not null
);

create table customers (
    id    bigint primary key,
    name  text not null,
    email text
);

create table orders (
    id          bigint primary key,
    customer_id bigint not null references customers (id),
    amount      numeric(12, 2) not null,
    status      text not null,          -- 'NEW', 'PAID', 'CANCELLED'
    created_at  timestamptz not null
);
```

---

## 1. Порядок выполнения запроса — главное, что нужно понять

Мы **пишем** запрос в одном порядке, а СУБД **логически выполняет** его в другом:

| Пишем | Выполняется |
|---|---|
| 1. `SELECT` | 1. `FROM` + `JOIN` — собрать строки из таблиц |
| 2. `FROM` / `JOIN` | 2. `WHERE` — отфильтровать **строки** |
| 3. `WHERE` | 3. `GROUP BY` — сгруппировать |
| 4. `GROUP BY` | 4. `HAVING` — отфильтровать **группы** |
| 5. `HAVING` | 5. `SELECT` — посчитать выражения, оконные функции |
| 6. `ORDER BY` | 6. `DISTINCT` |
| 7. `LIMIT` / `OFFSET` | 7. `ORDER BY` → 8. `LIMIT` / `OFFSET` |

Отсюда сразу следуют ответы на частые вопросы:

- **Почему в `WHERE` нельзя использовать алиас из `SELECT`?** `WHERE` выполняется раньше `SELECT`, алиаса ещё нет. А в `ORDER BY` можно — он позже.
- **Почему в `WHERE` нельзя написать `count(*) > 5`?** На этапе `WHERE` групп ещё нет. Фильтр по агрегату пишут в `HAVING`.
- **Почему в `WHERE` нельзя использовать оконную функцию?** Она считается на этапе `SELECT`. Нужно обернуть в подзапрос или CTE и фильтровать снаружи.

```sql
-- Ошибка: column "yearly" does not exist
select name, salary * 12 as yearly from employees where yearly > 1000000;

-- Правильно
select name, salary * 12 as yearly from employees where salary * 12 > 1000000;
```

---

## 2. Базовый SELECT

```sql
select name, salary
from employees
where salary between 100000 and 200000      -- включительно с обеих сторон
  and name like 'Ив%'                       -- % — любое кол-во символов, _ — ровно один
  and department_id in (1, 2, 3)
order by salary desc, name                  -- сначала по зарплате (убыв.), при равенстве — по имени
limit 10;
```

- `DISTINCT` — убрать дубликаты строк: `select distinct department_id from employees`.
- `ILIKE` (PostgreSQL) — `LIKE` без учёта регистра.
- `CASE` — условие внутри выражения:

```sql
select name,
       case
           when salary >= 300000 then 'senior'
           when salary >= 150000 then 'middle'
           else 'junior'
       end as level
from employees;
```

---

## 3. NULL — источник половины подвохов

`NULL` — это «значение неизвестно». Любое сравнение с `NULL` даёт не `true` и не `false`, а `NULL` (unknown), и `WHERE` такую строку **отбрасывает**.

| Выражение | Результат |
|---|---|
| `NULL = NULL` | `NULL` (не true!) |
| `NULL <> 5` | `NULL` |
| `NULL + 10` | `NULL` |
| `NULL IS NULL` | `true` |
| `NULL IS DISTINCT FROM 5` | `true` — сравнение «с учётом NULL» |

Правила:
- Проверять только через `IS NULL` / `IS NOT NULL`. `where manager_id = null` не вернёт **ничего**.
- `COALESCE(a, b, c)` — первое не-NULL значение: `coalesce(email, 'нет почты')`.
- Агрегаты (`SUM`, `AVG`, `MIN`, `MAX`, `COUNT(col)`) **пропускают NULL**. `AVG` считает среднее только по не-NULL.
- `COUNT(*)` считает **строки**, `COUNT(email)` — строки, где `email` не NULL, `COUNT(DISTINCT email)` — уникальные не-NULL.
- **Подвох с `NOT IN`:** если в подзапросе есть хоть один `NULL`, `NOT IN` вернёт **пустой результат**.

```sql
-- Хотим сотрудников, которые никем не руководят.
-- У директора manager_id = NULL, значит, в подзапросе будет NULL → результат ПУСТОЙ!
select * from employees
where id not in (select manager_id from employees);

-- Правильно: NOT EXISTS не боится NULL
select * from employees e
where not exists (select 1 from employees s where s.manager_id = e.id);
```

Почему так: `x NOT IN (1, 2, NULL)` = `x <> 1 AND x <> 2 AND x <> NULL` → последнее всегда `NULL`, и всё выражение не может стать `true`.

---

## 4. JOIN — соединения таблиц

Представим две таблицы как два множества строк. `JOIN` склеивает строку слева со строкой справа, если выполнено условие `ON`.

| Вид | Что вернёт |
|---|---|
| `INNER JOIN` (или просто `JOIN`) | только пары, где условие выполнено. Сотрудник без отдела **пропадёт** |
| `LEFT JOIN` | все строки слева; если пары нет — справа `NULL` |
| `RIGHT JOIN` | зеркально `LEFT` (на практике почти не пишут, переставляют таблицы) |
| `FULL JOIN` | все строки с обеих сторон, недостающее — `NULL` |
| `CROSS JOIN` | декартово произведение: каждая с каждой (N × M строк) |
| self join | таблица соединяется сама с собой (сотрудник ↔ его начальник) |

```sql
-- Сотрудники и название отдела; сотрудники без отдела тоже попадут (dept_name = NULL)
select e.name, d.name as dept_name
from employees e
left join departments d on d.id = e.department_id;

-- Сотрудник и его начальник (self join)
select e.name as employee, m.name as manager
from employees e
left join employees m on m.id = e.manager_id;
```

### Anti-join: «найти то, чего нет»

```sql
-- Отделы, в которых нет ни одного сотрудника
select d.*
from departments d
left join employees e on e.department_id = d.id
where e.id is null;                 -- пары не нашлось → справа NULL

-- То же через NOT EXISTS (часто понятнее и не хуже по скорости)
select d.* from departments d
where not exists (select 1 from employees e where e.department_id = d.id);
```

### Подвох: условие в `ON` и в `WHERE` при `LEFT JOIN`

```sql
-- (А) Все клиенты + их ОПЛАЧЕННЫЕ заказы. Клиенты без оплаченных заказов останутся с NULL
select c.name, o.amount
from customers c
left join orders o on o.customer_id = c.id and o.status = 'PAID';

-- (Б) Фильтр в WHERE выбрасывает строки, где o.status = NULL,
--     то есть LEFT JOIN превращается в INNER JOIN — клиенты без заказов ПРОПАЛИ
select c.name, o.amount
from customers c
left join orders o on o.customer_id = c.id
where o.status = 'PAID';
```

Правило: условие на **правую** таблицу `LEFT JOIN` — в `ON`, если нужно сохранить все строки слева.

### Подвох: JOIN размножает строки

Если у клиента 3 заказа, после `JOIN` он встретится 3 раза. Поэтому `sum()` по полю клиента после `JOIN` с заказами посчитает его трижды. Агрегировать нужно до соединения (в подзапросе) или считать то, что относится к «многим».

---

## 5. Группировка и агрегаты

```sql
-- Сколько сотрудников и средняя зарплата по каждому отделу, только отделы с > 5 людей
select department_id,
       count(*)              as cnt,
       round(avg(salary), 2) as avg_salary,
       max(salary)           as max_salary
from employees
group by department_id
having count(*) > 5
order by avg_salary desc;
```

- Правило `GROUP BY`: в `SELECT` можно указывать **только** колонки из `GROUP BY` и агрегаты. `select department_id, name, count(*) ... group by department_id` — ошибка: какое из имён в группе показать? (Исключение PostgreSQL: можно, если группируете по первичному ключу таблицы.)
- `WHERE` фильтрует строки **до** группировки, `HAVING` — группы **после**. Фильтр, не связанный с агрегатом, ставьте в `WHERE`: так меньше строк уйдёт в группировку.
- Сотрудники с `department_id = NULL` попадут в **одну общую группу** `NULL`.
- Условный подсчёт (очень частый приём):

```sql
select customer_id,
       count(*)                                    as all_orders,
       count(*) filter (where status = 'PAID')     as paid,        -- PostgreSQL
       sum(case when status = 'CANCELLED' then 1 else 0 end) as cancelled  -- в любой СУБД
from orders
group by customer_id;
```

---

## 6. Подзапросы, CTE, UNION

### Подзапросы

```sql
-- Скалярный (одно значение): сотрудники с зарплатой выше средней по компании
select * from employees where salary > (select avg(salary) from employees);

-- Коррелированный (ссылается на внешнюю строку, логически выполняется для каждой строки):
-- сотрудники с зарплатой выше средней ПО СВОЕМУ отделу
select * from employees e
where salary > (select avg(salary) from employees x where x.department_id = e.department_id);

-- В FROM (derived table) — обязательно алиас
select dept, avg_s from (
    select department_id as dept, avg(salary) as avg_s from employees group by department_id
) t where avg_s > 200000;
```

**`IN` vs `EXISTS`:** по смыслу `EXISTS` отвечает «есть ли хоть одна строка» и останавливается на первой найденной. Современный планировщик PostgreSQL обычно превращает оба варианта в одинаковый semi-join, так что разница в скорости — миф. Реальная разница — в поведении с `NULL` у `NOT IN` (см. раздел 3).

### CTE (`WITH`)

CTE — именованный подзапрос. Делает сложный запрос читаемым: «сначала посчитай это, потом то».

```sql
with dept_avg as (
    select department_id, avg(salary) as avg_salary
    from employees
    group by department_id
)
select e.name, e.salary, d.avg_salary
from employees e
join dept_avg d on d.department_id = e.department_id
where e.salary > d.avg_salary;
```

С PostgreSQL 12 CTE по умолчанию **встраивается** в запрос (оптимизируется как обычный подзапрос). Раньше он всегда материализовался — это был «забор оптимизации». Управлять можно: `with x as materialized (...)`.

**Рекурсивный CTE** — для иерархий (оргструктура, дерево категорий):

```sql
-- Все подчинённые (прямые и косвенные) сотрудника с id = 1
with recursive subordinates as (
    select id, name, manager_id, 1 as level
    from employees where id = 1                          -- стартовая строка (якорь)
    union all
    select e.id, e.name, e.manager_id, s.level + 1
    from employees e
    join subordinates s on e.manager_id = s.id           -- шаг рекурсии
)
select * from subordinates;
```

### UNION

- `UNION` — склеить результаты двух запросов **и убрать дубликаты** (дорого: нужна сортировка или хэш).
- `UNION ALL` — склеить как есть. Быстрее; используйте, если дубликатов быть не может или они нужны.
- `INTERSECT` — пересечение, `EXCEPT` — разность.
- Количество и типы колонок в обоих запросах должны совпадать.

---

## 7. Оконные функции — то, что отличает «знаю SQL» от «писал 30 запросов»

**Идея:** агрегат с `GROUP BY` схлопывает строки группы в одну. Оконная функция считает то же самое, **но оставляет все строки**: к каждой строке добавляется значение, посчитанное по её «окну».

```sql
select name, department_id, salary,
       avg(salary) over (partition by department_id) as dept_avg   -- среднее по отделу рядом с каждым
from employees;
```

Синтаксис: `функция() over (partition by ... order by ... [рамка])`
- `partition by` — на какие группы делить (как `GROUP BY`, но без схлопывания). Без него окно — вся таблица.
- `order by` — порядок внутри окна (нужен для нумерации, нарастающих итогов, `lag`/`lead`).

### Нумерация: ROW_NUMBER, RANK, DENSE_RANK

Зарплаты в отделе: 300, 200, 200, 100.

| salary | `row_number()` | `rank()` | `dense_rank()` |
|---|---|---|---|
| 300 | 1 | 1 | 1 |
| 200 | 2 | 2 | 2 |
| 200 | 3 | 2 | 2 |
| 100 | 4 | **4** | **3** |

- `row_number` — всегда уникальный номер (при равенстве порядок случайный, если не добавить ещё поле в `order by`).
- `rank` — одинаковым одинаковый номер, потом **пропуск**.
- `dense_rank` — одинаковым одинаковый номер, **без пропуска**. Его берут для «N-я по величине зарплата».

### Соседние строки и нарастающие итоги

```sql
select created_at::date as day,
       amount,
       lag(amount)  over (order by created_at) as prev_amount,     -- значение из предыдущей строки
       lead(amount) over (order by created_at) as next_amount,     -- из следующей
       sum(amount)  over (order by created_at) as running_total    -- нарастающий итог
from orders;
```

Тонкость: при `order by` внутри `over` рамка по умолчанию — «от начала окна до текущей строки **включая всех с таким же значением сортировки**» (`RANGE`). Если у двух заказов одинаковый `created_at`, нарастающий итог у них будет одинаковый. Чтобы считать построчно: `rows between unbounded preceding and current row`.

Скользящее среднее за 7 строк: `avg(amount) over (order by day rows between 6 preceding and current row)`.

### Фильтр по оконной функции — только снаружи

```sql
select * from (
    select e.*, dense_rank() over (partition by department_id order by salary desc) as rnk
    from employees e
) t
where rnk <= 3;
```

---

## 8. Задачи с собеседований

Сначала попробуйте написать сами.

### Задача 1. Вторая по величине зарплата в компании

<details><summary>Решение</summary>

```sql
-- Вариант 1: максимум среди тех, кто меньше максимума
select max(salary) from employees
where salary < (select max(salary) from employees);

-- Вариант 2: dense_rank — легко обобщается до N-й
select distinct salary from (
    select salary, dense_rank() over (order by salary desc) as rnk from employees
) t where rnk = 2;

-- Вариант 3: offset (distinct обязателен, иначе при двух одинаковых максимумах вернёт снова максимум)
select distinct salary from employees order by salary desc offset 1 limit 1;
```
Что спросят дальше: «а если второй зарплаты нет?» — вариант 1 вернёт `NULL` (одна строка), варианты 2–3 вернут пустой результат.
</details>

### Задача 2. Сотрудники, которые получают больше своего начальника

<details><summary>Решение</summary>

```sql
select e.name, e.salary, m.name as manager, m.salary as manager_salary
from employees e
join employees m on m.id = e.manager_id
where e.salary > m.salary;
```
</details>

### Задача 3. Топ-3 самых высокооплачиваемых в каждом отделе

<details><summary>Решение</summary>

```sql
select department_id, name, salary from (
    select e.*, dense_rank() over (partition by department_id order by salary desc) as rnk
    from employees e
) t
where rnk <= 3
order by department_id, salary desc;
```
Уточнить у интервьюера: «топ-3 зарплаты» (`dense_rank`, людей может быть больше 3) или «ровно 3 человека» (`row_number`).
</details>

### Задача 4. Найти дубликаты email у клиентов

<details><summary>Решение</summary>

```sql
select email, count(*)
from customers
where email is not null
group by email
having count(*) > 1;

-- Без учёта регистра
select lower(email), count(*) from customers group by lower(email) having count(*) > 1;
```
</details>

### Задача 5. Удалить дубликаты, оставив запись с минимальным id

<details><summary>Решение</summary>

```sql
delete from customers c
where exists (
    select 1 from customers d
    where d.email = c.email and d.id < c.id      -- есть такой же email с меньшим id → c лишний
);

-- Через row_number
delete from customers
where id in (
    select id from (
        select id, row_number() over (partition by email order by id) as rn from customers
    ) t where rn > 1
);
```
На проде: сначала `select` тем же условием, проверить количество, и только потом `delete` — в транзакции.
</details>

### Задача 6. Сколько заказов у каждого клиента, включая клиентов без заказов

<details><summary>Решение</summary>

```sql
select c.id, c.name, count(o.id) as orders_cnt     -- count(o.id), а НЕ count(*)!
from customers c
left join orders o on o.customer_id = c.id
group by c.id, c.name
order by orders_cnt desc;
```
Подвох: `count(*)` посчитает строку с `NULL`-заказом и даст клиенту без заказов **1** вместо 0.
</details>

### Задача 7. Отделы, где средняя зарплата выше средней по компании

<details><summary>Решение</summary>

```sql
select d.name, avg(e.salary) as avg_salary
from departments d
join employees e on e.department_id = d.id
group by d.id, d.name
having avg(e.salary) > (select avg(salary) from employees);
```
</details>

### Задача 8. Выручка по месяцам и рост к прошлому месяцу в %

<details><summary>Решение</summary>

```sql
with monthly as (
    select date_trunc('month', created_at) as month, sum(amount) as revenue
    from orders
    where status = 'PAID'
    group by 1
)
select month, revenue,
       lag(revenue) over (order by month) as prev,
       round(100.0 * (revenue - lag(revenue) over (order by month))
             / nullif(lag(revenue) over (order by month), 0), 1) as growth_pct
from monthly
order by month;
```
`nullif(x, 0)` — защита от деления на ноль: вернёт `NULL` вместо ошибки.
</details>

### Задача 9. Последний заказ каждого клиента

<details><summary>Решение</summary>

```sql
-- PostgreSQL: DISTINCT ON — коротко и быстро
select distinct on (customer_id) *
from orders
order by customer_id, created_at desc;

-- Универсально: row_number
select * from (
    select o.*, row_number() over (partition by customer_id order by created_at desc) as rn
    from orders o
) t where rn = 1;
```
</details>

### Задача 10. Клиенты, у которых есть и оплаченные, и отменённые заказы

<details><summary>Решение</summary>

```sql
select customer_id
from orders
where status in ('PAID', 'CANCELLED')
group by customer_id
having count(distinct status) = 2;
```
</details>

### Задача 11. Перевод денег между счетами (банковская классика)

Таблица `accounts(id, balance)`. Перевести 100 со счёта 1 на счёт 2 так, чтобы баланс не ушёл в минус и не было гонки.

<details><summary>Решение</summary>

```sql
begin;
-- Блокируем ОБА счёта в одном порядке (по id), чтобы два встречных перевода не попали в deadlock
select id, balance from accounts where id in (1, 2) order by id for update;

update accounts set balance = balance - 100 where id = 1 and balance >= 100;
-- если обновилась 0 строк — денег не хватает → rollback
update accounts set balance = balance + 100 where id = 2;
commit;
```
Ещё лучше — ограничение в схеме: `check (balance >= 0)`, тогда БД сама не даст уйти в минус. Подробнее про блокировки — [databases.md](databases.md#7-блокировки).
</details>

### Задача 12. Дни подряд (gaps and islands) — задача «со звёздочкой»

Найти периоды, когда клиент делал заказы несколько дней подряд.

<details><summary>Решение</summary>

Идея: если из даты вычесть её порядковый номер, у дней, идущих подряд, получится одинаковое значение — это и есть «остров».

```sql
with days as (
    select distinct customer_id, created_at::date as day from orders
),
grp as (
    select customer_id, day,
           day - (row_number() over (partition by customer_id order by day))::int as island
    from days
)
select customer_id, min(day) as from_day, max(day) as to_day, count(*) as days_in_row
from grp
group by customer_id, island
having count(*) >= 2
order by customer_id, from_day;
```
</details>

### Задача 13. «Что вернёт запрос?» — проверка на понимание

<details><summary>Таблица t(x): 1, 2, NULL. Что вернут count(*), count(x), sum(x), avg(x)?</summary>

`count(*) = 3`, `count(x) = 2`, `sum(x) = 3`, `avg(x) = 1.5` (среднее по двум не-NULL, а не 3/3 = 1).
</details>

<details><summary>select * from t where x <> 1 — сколько строк?</summary>

Одну (`2`). Строка с `NULL` не попадёт: `NULL <> 1` → `NULL`, а не `true`.
</details>

<details><summary>Таблица a: 3 строки, b: 4 строки. Сколько строк вернёт a cross join b? А a left join b on false?</summary>

`cross join` — 12. `left join ... on false` — 3 (все строки `a`, справа `NULL`).
</details>

---

## 9. Изменение данных (DML)

```sql
insert into departments (id, name) values (1, 'IT'), (2, 'HR');

-- Вставка результата запроса
insert into archive_orders select * from orders where created_at < now() - interval '1 year';

update employees set salary = salary * 1.1 where department_id = 1;

-- UPDATE с JOIN (PostgreSQL)
update employees e
set salary = salary * 1.1
from departments d
where d.id = e.department_id and d.name = 'IT';

delete from orders where status = 'CANCELLED';

-- UPSERT: вставить, а если запись уже есть — обновить (PostgreSQL)
insert into customers (id, name, email) values (1, 'Иван', 'ivan@mail.ru')
on conflict (id) do update set email = excluded.email;   -- excluded — строка, которую пытались вставить

-- Вернуть то, что изменилось (PostgreSQL) — удобно, чтобы не делать второй select
update orders set status = 'PAID' where id = 10 returning *;
```

**`DELETE` vs `TRUNCATE` vs `DROP`:**
- `DELETE` — удаляет строки по условию, построчно, пишет каждую в журнал, срабатывают триггеры. Можно откатить.
- `TRUNCATE` — очищает всю таблицу разом, очень быстро, без условия. В PostgreSQL тоже транзакционный (можно откатить), но берёт эксклюзивную блокировку на таблицу.
- `DROP` — удаляет саму таблицу вместе со структурой.

---

## 10. DDL: таблицы, типы, ограничения

```sql
create table accounts (
    id         bigint generated always as identity primary key,  -- автоинкремент (современный вариант serial)
    number     varchar(20) not null unique,
    owner_id   bigint not null references customers (id) on delete restrict,
    balance    numeric(19, 2) not null default 0 check (balance >= 0),
    currency   char(3) not null,
    created_at timestamptz not null default now()
);
```

| Ограничение | Смысл |
|---|---|
| `PRIMARY KEY` | уникальный и не NULL идентификатор строки; автоматически создаёт индекс |
| `UNIQUE` | значения не повторяются (NULL-ов может быть много — они «не равны» друг другу); создаёт индекс |
| `FOREIGN KEY` (`REFERENCES`) | значение должно существовать в другой таблице. **Индекс на колонку FK PostgreSQL сам не создаёт** — его почти всегда стоит добавить |
| `NOT NULL`, `CHECK`, `DEFAULT` | понятно из названий |

`ON DELETE`: `RESTRICT`/`NO ACTION` (запретить удаление родителя), `CASCADE` (удалить детей), `SET NULL`.

Типы, о которых спрашивают:
- **Деньги — только `numeric`/`decimal`**, никогда `float`/`double` (`0.1 + 0.2 <> 0.3`). В Java — `BigDecimal`.
- Время — `timestamptz` (хранит момент в UTC и переводит в пояс сессии). `timestamp` без пояса — источник багов при переходе через пояса.
- `text` и `varchar(n)` в PostgreSQL по скорости одинаковы; `varchar(n)` — просто проверка длины.
- `uuid` — для id, которые генерирует приложение; в PostgreSQL 18 появилась `uuidv7()` — UUID, упорядоченный по времени, он гораздо дружелюбнее к B-tree индексу, чем случайный v4.
- `jsonb` — JSON в бинарном виде, с индексами GIN.

**Представление (VIEW)** — сохранённый `SELECT` с именем; данных не хранит, при каждом обращении выполняется заново. **Материализованное представление** (`materialized view`) хранит результат, его обновляют командой `refresh materialized view` — для тяжёлых отчётов.

**Триггер** — функция, которую СУБД сама вызывает при `INSERT`/`UPDATE`/`DELETE` (до или после). Применяют для аудита и историчности. Минусы: скрытая логика, которую не видно из кода приложения, сложнее отлаживать.

---

## 11. Шпаргалка «как ответить на вопрос»

- **Разница `WHERE` и `HAVING`?** `WHERE` фильтрует строки до группировки, `HAVING` — группы после. Агрегаты — только в `HAVING`.
- **Разница `UNION` и `UNION ALL`?** `UNION` убирает дубликаты (дороже), `UNION ALL` — нет.
- **`COUNT(*)` vs `COUNT(col)`?** Все строки против строк, где `col` не NULL.
- **Виды JOIN?** INNER, LEFT, RIGHT, FULL, CROSS + self join. Как найти «то, чего нет» — `LEFT JOIN ... IS NULL` или `NOT EXISTS`.
- **Почему `NOT IN` опасен?** Один `NULL` в подзапросе — и результат пустой.
- **Чем `rank` отличается от `dense_rank`?** `rank` после одинаковых делает пропуск номера, `dense_rank` — нет.
- **Оконная функция vs `GROUP BY`?** Окно не схлопывает строки.
- **Как писать запросы из Java безопасно?** Только параметры (`PreparedStatement`, `:param` в JPQL/Spring Data), никакой склейки строк — см. [SQL-инъекции](databases.md#13-sql-инъекции).

## Где тренироваться

- [sql-ex.ru](https://sql-ex.ru) — классический русскоязычный задачник.
- [pgexercises.com](https://pgexercises.com) — задачи именно на PostgreSQL, с разбором.
- LeetCode → раздел Database (вкладка SQL 50).
