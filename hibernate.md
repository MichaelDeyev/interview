# JPA, Hibernate и Spring Data

[← Оглавление](README.md) · Транзакции в Spring — [spring.md](spring.md#7-transactional) · Изоляция и блокировки в БД — [databases.md](databases.md)

## 1. JPA vs Hibernate vs Spring Data

- **JPA (Jakarta Persistence)** — **спецификация**: набор интерфейсов и аннотаций (`@Entity`, `EntityManager`, JPQL). Сама ничего не делает.
- **Hibernate** — самая популярная **реализация** JPA (плюс свои возможности сверх спецификации). Другие — EclipseLink.
- **Spring Data JPA** — надстройка над JPA: репозитории-интерфейсы, методы по имени (`findByEmail`), пагинация. Под капотом вызывает `EntityManager`, то есть Hibernate.
- Версии: Spring Boot 3 — Hibernate 6, Spring Boot 4 — Hibernate 7 (Jakarta Persistence 3.2).

## 2. Состояния сущности и persistence context

**Коротко:** persistence context (контекст постоянства, он же **кэш первого уровня**) — набор сущностей, которыми сейчас управляет `EntityManager` (`Session`). Обычно живёт столько же, сколько транзакция. Hibernate отслеживает изменения управляемых сущностей и сам пишет их в БД.

| Состояние | Что значит |
|---|---|
| **Transient / New** | создан через `new`, Hibernate о нём не знает |
| **Managed / Persistent** | в контексте постоянства: изменения отслеживаются и будут записаны |
| **Detached** | был управляемым, но контекст закрыт (транзакция завершилась) или объект отсоединён (`detach`, `clear`). Изменения не отслеживаются |
| **Removed** | помечен на удаление, `DELETE` выполнится при flush |

- **`persist(e)`** — new → managed. **`merge(e)`** — копирует состояние detached-объекта в управляемый (загружает из БД при необходимости) и **возвращает управляемую копию**; переданный объект остаётся detached. **`remove(e)`** — managed → removed. **`find`** — загрузить по id (сначала смотрит в контекст).
- **Spring Data `save(entity)`** — если сущность новая (`id == null` или `@Version == null`, либо `Persistable.isNew()`), вызывает `persist`, иначе `merge`. Поэтому `save` возвращает объект — **работать дальше надо с возвращённым**.
- Подвох: если id генерирует приложение (UUID задан заранее), `save` решит, что сущность не новая, и сделает `merge` → лишний `SELECT` перед `INSERT`. Лечится `Persistable` или `@Version`.

### Dirty checking и flush

```java
@Transactional
public void rename(Long id, String name) {
    User user = userRepository.findById(id).orElseThrow();   // managed
    user.setName(name);                                       // save() вызывать НЕ нужно
}   // при коммите Hibernate сравнит состояние со снимком и выполнит UPDATE
```

- **Dirty checking** — при загрузке Hibernate запоминает снимок полей; перед коммитом сравнивает и генерирует `UPDATE` для изменённых сущностей.
- **Flush** — отправка накопленных изменений в БД (SQL выполняется, но транзакция ещё не закоммичена). Происходит перед коммитом, перед JPQL-запросом, который может затронуть изменённые таблицы (`FlushMode.AUTO`), и при явном `flush()`.
- Вопрос: «в транзакционном методе `repository.save(obj)`, потом `obj.setName("new")` — что будет в БД?» Ответ: `"new"`, если `obj` — управляемый объект (новый после `persist` или загруженный в этой транзакции): при flush dirty checking увидит изменение. Если `obj` был detached и `save` сделал `merge`, то изменён detached-объект, а не возвращённая копия, — в БД останется старое значение.
- Ошибки ограничений (`unique`, `not null`) из-за отложенного flush могут вылететь не в строке `save`, а при коммите — после выхода из метода. Поэтому outbox-событие нельзя отправлять «сразу после save» в надежде, что запись уже прошла.

## 3. Связи и загрузка

- `@OneToOne`, `@OneToMany`, `@ManyToOne`, `@ManyToMany`.
- **По умолчанию:** `@ManyToOne` и `@OneToOne` — **EAGER**; `@OneToMany` и `@ManyToMany` — **LAZY**. Рекомендация — делать **все** связи LAZY (`@ManyToOne(fetch = FetchType.LAZY)`) и явно подгружать нужное в запросе.
- **LAZY** — вместо связанного объекта подставляется **прокси** (для коллекций — `PersistentBag`/`PersistentSet`); запрос в БД — при первом обращении к данным.
- **EAGER** — загрузить сразу. Опасен: тянет графы объектов везде, даже где не нужно, и сам по себе вызывает N+1 в JPQL-запросах.
- Владелец связи — сторона с внешним ключом (`@ManyToOne`). В `@OneToMany(mappedBy = "order")` — обратная сторона. Двунаправленную связь синхронизировать в обе стороны (методы `addItem`/`removeItem`).
- `cascade = CascadeType.ALL` — операции над родителем распространяются на детей (для агрегатов: заказ → позиции). `orphanRemoval = true` — убрали ребёнка из коллекции → удалить из БД. Не ставить каскады на `@ManyToOne` (удалить пользователя при удалении заказа — не то, что нужно).
- `@ManyToMany` с `List` при удалении элемента пересоздаёт всю связующую таблицу — лучше `Set` или явная сущность-связка.

## 4. Проблема N+1

**Коротко:** один запрос загружает N родителей, а потом для каждого выполняется ещё по запросу за связанными данными — итого N + 1 запросов вместо одного-двух.

```java
List<User> users = userRepository.findAll();            // 1 запрос
for (User u : users) {
    u.getRoles().size();                                // + по запросу на каждого пользователя
}
```

Возникает и с LAZY (при обходе в цикле, в маппере в DTO, при сериализации в JSON), и с EAGER (Hibernate грузит связь отдельным запросом для каждого результата JPQL).

### Как найти
- Логи SQL (`spring.jpa.show-sql`, а лучше `logging.level.org.hibernate.SQL=debug`), статистика Hibernate (`hibernate.generate_statistics`).
- Тесты на количество запросов (библиотеки вроде `datasource-proxy`, Hypersistence Utils).

### Как решить

```java
public interface UserRepository extends JpaRepository<User, Long> {

    // 1. JOIN FETCH — связь загружается в том же запросе
    @Query("select distinct u from User u left join fetch u.roles")
    List<User> findAllWithRoles();

    // 2. EntityGraph — то же декларативно
    @EntityGraph(attributePaths = "roles")
    List<User> findAll();

    // 3. Проекция в DTO — загрузить только нужные поля, без сущностей
    @Query("select new com.example.UserView(u.id, u.name) from User u")
    List<UserView> findAllViews();
}
```

4. **`@BatchSize(size = 50)`** на коллекции (или глобально `hibernate.default_batch_fetch_size`) — ленивые коллекции догружаются пачками `where user_id in (...)`: вместо N запросов — N/50.
5. `@Fetch(FetchMode.SUBSELECT)` — догрузить все коллекции одним подзапросом.

Подвохи:
- **`JOIN FETCH` + пагинация** (`Pageable`) по коллекции — Hibernate не может сделать `LIMIT` в SQL (строк больше, чем родителей) и пагинирует **в памяти** с предупреждением `HHH90003004` (`firstResult/maxResults specified with collection fetch`). Решение: сначала страница id, потом второй запрос с `join fetch ... where id in (:ids)`; или `@BatchSize`.
- **`MultipleBagFetchException`** — нельзя `join fetch` две коллекции-`List` одновременно. Решение: `Set`, или два запроса, или batch size. (Даже с `Set` две коллекции через join дают декартово произведение строк.)

## 5. `LazyInitializationException`

**Причина:** обращение к ленивой связи **после закрытия** persistence context (транзакция кончилась, объект detached) — прокси не может сходить в БД.

Типичное место — контроллер или JSON-сериализация сущности, которую вернул сервис.

Правильные решения:
1. Загрузить нужное **внутри транзакции**: `JOIN FETCH`, `@EntityGraph`.
2. Преобразовать в **DTO внутри сервисного `@Transactional`-метода** и наружу отдавать DTO, а не сущности.
3. Проекции Spring Data (интерфейсные или record).

Плохие решения (антипаттерны):
- **Open Session in View** (`spring.jpa.open-in-view=true` — **включено в Spring Boot по умолчанию**, при старте выводится предупреждение): контекст живёт весь HTTP-запрос, ленивые связи грузятся при рендеринге. Ошибки не будет, но соединение с БД занято весь запрос, а N+1 спрятан. Рекомендуется выключать: `spring.jpa.open-in-view=false`.
- `hibernate.enable_lazy_load_no_trans=true` — каждый ленивый доступ открывает новую транзакцию. Хуже всего.
- Перевести связь на EAGER «чтобы не падало».

## 6. Кэши Hibernate

- **Первого уровня** — persistence context. Включён всегда, живёт в рамках сессии/транзакции. Повторный `find(id)` в той же транзакции не идёт в БД. **Не** кэширует результаты JPQL-запросов (запрос всё равно выполнится, но для уже загруженных строк вернутся те же объекты).
- **Второго уровня** — общий для всех сессий приложения (на уровне `SessionFactory`). Выключен по умолчанию, нужен провайдер (Ehcache, Caffeine, Infinispan через JCache) и `@Cache` на сущностях. Подходит для справочников, которые редко меняются. Подвохи: при нескольких инстансах приложения локальный кэш устаревает (нужен распределённый или короткий TTL); изменения в обход Hibernate (SQL, другой сервис) кэш не видит.
- **Кэш запросов** — хранит id результатов запроса, работает вместе с L2. Инвалидируется при любом изменении таблицы — полезен редко.
- В микросервисах чаще кэшируют на уровне сервиса (Spring `@Cacheable` + Redis), а не L2 Hibernate.

## 7. Генерация id и пакетная вставка

| Стратегия | Как | Batch insert |
|---|---|---|
| `IDENTITY` | автоинкремент колонки (`identity`/`serial`) | **отключается**: Hibernate должен выполнить каждый `INSERT` сразу, чтобы узнать id |
| `SEQUENCE` | последовательность БД; с `allocationSize = 50` Hibernate берёт сразу диапазон id и почти не ходит за новыми | работает — **рекомендуется для PostgreSQL** |
| `UUID` | генерирует приложение | работает; UUIDv7 лучше для индекса, чем случайный v4 |
| `TABLE` | отдельная таблица-счётчик | медленно, не использовать |

Пакетная вставка (batch):

```yaml
spring.jpa.properties.hibernate:
  jdbc.batch_size: 50
  order_inserts: true      # группировать INSERT по таблицам
  order_updates: true
```

Вопрос «как улучшить код»:

```java
for (Item item : items) repository.save(item);   // каждый save — своя транзакция, если метод не @Transactional
```

Ответ: (1) выполнить всё в **одной транзакции** (`@Transactional` на сервисном методе) или `saveAll(items)` — он сам транзакционный; (2) включить `jdbc.batch_size` и использовать `SEQUENCE`, тогда Hibernate отправит вставки пачками; (3) для очень больших объёмов — периодически `flush()` и `clear()`, чтобы контекст не разрастался, или вообще `JdbcTemplate.batchUpdate` / `COPY` без ORM.

## 8. Блокировки в JPA

- **Оптимистичная** — поле `@Version` (число или timestamp). При `UPDATE` Hibernate добавляет `where version = ?`; если строку изменил кто-то другой — `OptimisticLockException` (в Spring — `ObjectOptimisticLockingFailureException`). Обработка: повторить операцию (Spring Retry / `@Retryable`) или вернуть пользователю 409 Conflict.
- **Пессимистичная** — `@Lock(LockModeType.PESSIMISTIC_WRITE)` на методе репозитория → `SELECT ... FOR UPDATE`. Таймаут: `@QueryHints(@QueryHint(name = "jakarta.persistence.lock.timeout", value = "3000"))`.
- Когда что — см. [databases.md](databases.md#lost-update-в-read-committed--частый-вопрос).

## 9. `equals()` и `hashCode()` для сущностей

Проблема: если id генерирует БД, у новой сущности `id == null`, после `persist` он появляется. Если `hashCode` зависит от id, объект, положенный в `HashSet` до сохранения, «потеряется» после.

Варианты:
1. **Бизнес-ключ** — неизменяемое уникальное поле (номер счёта, email, внешний UUID). Лучший вариант, если он есть.
2. **id, сгенерированный приложением** (UUID при создании объекта) — id известен сразу, проблемы нет.
3. **id из БД + константный `hashCode`** (рецепт Vlad Mihalcea / Thorben Janssen):

```java
@Override
public boolean equals(Object o) {
    if (this == o) return true;
    if (!(o instanceof Account other)) return false;     // instanceof, а не getClass(): Hibernate-прокси — подкласс
    return id != null && id.equals(other.getId());       // две новые сущности без id не равны
}

@Override
public int hashCode() {
    return getClass().hashCode();                        // константа: не меняется при присвоении id
}
```

Константный хэш корректен по контракту, но все сущности класса попадут в один бакет: `HashSet` из тысяч новых сущностей превращается по скорости в список (в Java 8+ в дерево, если ключи сравнимы). Обычно это не проблема — в одной коллекции-связи редко тысячи элементов.

Чего не делать: использовать все поля (изменяемые, ленивые связи → лишние запросы и рекурсия); `data class` в Kotlin и `@Data`/`@EqualsAndHashCode` Lombok на сущностях по той же причине.

## 10. Spring Data

- Иерархия: `Repository` → `CrudRepository` (`save`, `findById`, `delete`…) → `ListCrudRepository` (возвращает `List`, а не `Iterable`; с Spring Data 3). `PagingAndSortingRepository` (с Spring Data 3 **не наследует** `CrudRepository`) и `ListPagingAndSortingRepository`. **`JpaRepository`** — всё вместе плюс JPA-специфика (`flush`, `saveAllAndFlush`, `deleteAllInBatch`, `getReferenceById`).
- **Методы по имени:** `findByStatusAndCreatedAtAfterOrderByCreatedAtDesc(...)`. Длинные имена — сигнал перейти на `@Query`.
- **`@Query`** — JPQL или `nativeQuery = true`. Для изменения данных — плюс `@Modifying` (и `clearAutomatically = true`, иначе контекст будет хранить устаревшие объекты).
- **Проекции:** интерфейс с геттерами или record/DTO — выбираются только нужные колонки.
- **Specification / Criteria API** — динамические запросы из набора условий (фильтры в поиске): `repository.findAll(where(hasStatus(s)).and(createdAfter(d)), pageable)`. Criteria API — типобезопасный программный построитель запросов JPA, Specification — обёртка Spring Data над ним. Альтернатива — Querydsl, jOOQ.
- **Пагинация:** `Page<T>` (делает дополнительный `count`-запрос), `Slice<T>` (без `count`, знает только «есть ли следующая»), `Window<T>` + `ScrollPosition` (keyset, Spring Data 3.1+).
- `getReferenceById(id)` — прокси без запроса в БД: удобно, чтобы установить связь (`order.setCustomer(ref)`), не загружая клиента.
- `deleteAll()` / `deleteBy...` загружают сущности и удаляют по одной (с каскадами и колбэками). Массово — `deleteAllInBatch()` или `@Modifying @Query("delete ...")`.

## 11. Короткие ответы

- **Чем `persist` отличается от `merge`?** Делает переданный new-объект управляемым против копирования состояния в управляемую копию (переданный не становится managed).
- **Зачем `@Transactional(readOnly = true)` для чтения?** Hibernate не делает снимков для dirty checking и не делает flush — меньше памяти и CPU; можно направлять на реплику.
- **Почему `IDENTITY` плох для batch insert?** Нужно выполнить `INSERT`, чтобы узнать id, поэтому пачки не собираются.
- **Что такое прокси в Hibernate?** Сгенерированный подкласс сущности для ленивой загрузки. Отсюда требования: класс не `final`, есть конструктор без аргументов (protected/public).
- **`get` vs `load` / `find` vs `getReference`?** Сразу загрузить (или `null`) против ленивого прокси без запроса (исключение при первом доступе, если строки нет).
- **Hibernate или JDBC?** ORM удобен для CRUD и сложных моделей с изменениями; для отчётов, массовых операций и тонкой настройки SQL — `JdbcTemplate`/`JdbcClient`, jOOQ. В одном проекте их часто совмещают.
