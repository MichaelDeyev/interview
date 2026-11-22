# Подготовка к собеседованию: Java / Kotlin backend

База знаний для подготовки к техническим собеседованиям на позицию Senior Java/Kotlin backend-разработчика: Java, Kotlin, Spring, базы данных, Kafka, многопоточность, микросервисы. Актуализировано в ноябре 2026: Java 21/25, Kotlin 2, Spring Boot 3/4, Kafka 4, PostgreSQL 18, AI в backend (RAG, агенты).

**Всё одним файлом:** [README-full.md](README-full.md) — все темы подряд в порядке исходного README. Он собирается из тематических файлов скриптом: правки вносить в тематические файлы, затем выполнить `python tools/build_full_readme.py` из корня репозитория. Схемы в `img/` — SVG с тёмным фоном, рисуются скриптом `python tools/build_images.py` (правки — в описании схем в скрипте).

**Формат:** вопрос → **«Коротко»** (что сказать за 20–30 секунд) → подробности, примеры кода и подвохи. В разделах с задачами ответы спрятаны под спойлер «Решение» — сначала попробуйте ответить сами.

## Оглавление

| Тема | Что внутри |
|---|---|
| [Java Core](java-core.md) | `Object`, equals/hashCode, String, обёртки, исключения, интерфейсы, generics, Stream API, Optional, Java 17–25, records |
| [Коллекции и структуры данных](collections.md) | иерархия, сложность операций, устройство HashMap, TreeMap, WeakHashMap, fail-fast, деревья |
| [JVM](jvm.md) | области памяти, сборщики мусора (G1, ZGC), GC roots, загрузчики классов, JIT, JVM в контейнере |
| [**Многопоточность**](concurrency.md) | JMM и happens-before, volatile, synchronized, локи, CAS, ConcurrentHashMap, пулы, CompletableFuture, виртуальные потоки, задачи |
| [Kotlin](kotlin.md) | null-безопасность, data/sealed-классы, расширения, scope-функции, корутины и Flow, Kotlin + Spring/JPA |
| [Spring и Spring Boot](spring.md) | IoC/DI, бины и жизненный цикл, прокси и AOP, `@Transactional`, автоконфигурация, MVC, WebFlux, Security |
| [JPA, Hibernate, Spring Data](hibernate.md) | состояния сущности, dirty checking, N+1, LazyInitializationException, кэши, batch, блокировки |
| [**SQL**](sql.md) | порядок выполнения, NULL, JOIN, группировка, оконные функции, 13 задач с решениями |
| [**Базы данных (PostgreSQL)**](databases.md) | ACID, аномалии и уровни изоляции, MVCC, индексы, EXPLAIN, блокировки, пагинация, масштабирование |
| [**Kafka**](kafka.md) | партиции, репликация, продюсер и acks, consumer group, гарантии доставки, DLT, Spring Kafka, вопросы |
| [Микросервисы](microservices.md) | CAP, синхронное и асинхронное общение, Resilience4j, outbox, saga, идемпотентность, кэш, наблюдаемость |
| [Сети и безопасность](web.md) | HTTP, методы и коды, REST, TLS, cookies и сессии, JWT, OAuth2, OWASP |
| [Паттерны и принципы](patterns.md) | SOLID, GoF, Strategy и Chain of Responsibility на Spring, архитектура, антипаттерны |
| [Тестирование](testing.md) | пирамида, JUnit 5, Mockito, Spring-тесты, Testcontainers, нагрузочное тестирование |
| [Сборка и DevOps](devops.md) | Maven/Gradle, Git, Docker, Kubernetes, CI/CD |
| [Алгоритмы](algorithms.md) | Big O, сортировки, приёмы, 12 задач на live coding |
| [System design](system-design.md) | план ответа, сервис уведомлений, переводы, rate limiter |
| [**AI в backend**](ai.md) | LLM и токены, эмбеддинги и pgvector, RAG, tool calling, агенты и harness, MCP, Spring AI, evals, prompt injection |
| [Нетехнические вопросы](behavioral.md) | рассказ о себе, STAR, вопросы техлиду, вопросы работодателю |
| [Вопросы для интервьюера](my-questions/my-interview-questions.md) | набор вопросов для проведения собеседования с кандидатом |

## Как готовиться

1. Пройти «Быструю самопроверку» ниже: на что не ответили уверенно за 30 секунд, то прочитать по ссылке.
2. Задачи по SQL и алгоритмам — **решать руками**: SQL — в локальном PostgreSQL (`docker run -d --name pg -e POSTGRES_PASSWORD=pg -p 5433:5432 postgres`, подключение: localhost:5433, пользователь `postgres`, пароль `pg`; порт 5433 — чтобы не конфликтовать с локально установленным PostgreSQL; таблицы и данные — [sql/seed.sql](sql/seed.sql)), код — в IDE.
3. Перед собеседованием — пройти по разделам «Коротко» и «Короткие ответы» в конце файлов.
4. Подготовить 5–7 историй из своего опыта по схеме STAR ([behavioral.md](behavioral.md)).

## Быстрая самопроверка

### Java
- Методы класса `Object`? Как работает `equals`, если его не переопределять? → [java-core](java-core.md#1-методы-класса-object)
- Контракт `equals` и `hashCode`. Какие поля использовать для `hashCode`? → [java-core](java-core.md#2-equals-и-hashcode)
- Примитивы и обёртки: отличия, где хранятся, кэш `Integer`? → [java-core](java-core.md#3-примитивы-и-обёртки)
- String: неизменяемость, пул строк? → [java-core](java-core.md#4-string)
- Checked и unchecked исключения, когда не выполнится `finally`? → [java-core](java-core.md#5-исключения)
- Интерфейс или абстрактный класс? → [java-core](java-core.md#6-интерфейс-и-абстрактный-класс)
- Можно ли перегрузить `static`-метод? А переопределить? Можно ли при переопределении сузить модификатор доступа? → [java-core](java-core.md#7-перегрузка-и-переопределение)
- Type erasure, PECS? → [java-core](java-core.md#8-generics)
- Stream API: зачем `map`, `flatMap`, чем плох `filter`, что такое ленивость? → [java-core](java-core.md#11-stream-api)
- Что нового в Java 17, 21 и 25? → [java-core](java-core.md#13-современная-java-17--21--25)

### Коллекции и JVM
- Почему `Map` не наследует `Collection`? → [collections](collections.md#1-иерархия)
- `ArrayList` или `LinkedList`? Уменьшится ли ёмкость `ArrayList` при удалении? → [collections](collections.md#3-arraylist-vs-linkedlist)
- Как устроена `HashMap`, параметры конструктора, что будет при одинаковых хэшкодах, можно ли не найти значение по ключу? → [collections](collections.md#4-как-устроена-hashmap)
- Стек и куча, что где хранится? → [jvm](jvm.md#1-области-памяти-jvm)
- Как GC находит мусор, какие сборщики есть, какой по умолчанию? → [jvm](jvm.md#2-сборка-мусора-gc)

### Многопоточность
- Атомарность, видимость, упорядоченность — что это? → [concurrency](concurrency.md#1-зачем-вообще-всё-это-и-в-чём-проблема)
- Что такое happens-before? Что даёт `volatile` и чего не даёт? → [concurrency](concurrency.md#2-java-memory-model-jmm-и-happens-before)
- `synchronized` vs `ReentrantLock`? `sleep` vs `wait`? → [concurrency](concurrency.md#4-synchronized-и-мониторы)
- Что такое CAS и проблема ABA? → [concurrency](concurrency.md#6-cas-и-атомарные-классы)
- Как устроен `ConcurrentHashMap`? → [concurrency](concurrency.md#как-устроен-concurrenthashmap-java-8)
- Как работает `ThreadPoolExecutor`, чем опасен `newFixedThreadPool`? → [concurrency](concurrency.md#8-executor-пулы-потоков-future)
- Виртуальные потоки: когда помогают, что такое pinning? → [concurrency](concurrency.md#10-виртуальные-потоки-java-21)
- Deadlock: как возникает, как избежать? → [concurrency](concurrency.md#11-deadlock-livelock-starvation-race-condition)

### Spring и Hibernate
- Способы создать бин и внедрить зависимость, какой лучше? → [spring](spring.md#3-внедрение-зависимостей)
- `@RequiredArgsConstructor` — чья аннотация? → [spring](spring.md#3-внедрение-зависимостей)
- `@Component`, `@Service`, `@Repository`, `@Controller`: в чём разница? Можно ли заменить `@RestController` на `@Component`? → [spring](spring.md#стереотипы)
- Зачем профили? → [spring](spring.md#конфигурация)
- Жизненный цикл бина, `BeanPostProcessor`? → [spring](spring.md#5-жизненный-цикл-бина)
- JDK Proxy vs CGLIB? → [spring](spring.md#jdk-dynamic-proxy-vs-cglib)
- `@Transactional` на private-методе? Вызов одного транзакционного метода из другого в том же классе? Propagation? → [spring](spring.md#7-transactional)
- JPA vs Hibernate? → [hibernate](hibernate.md#1-jpa-vs-hibernate-vs-spring-data)
- Lazy и Eager, проблема N+1? → [hibernate](hibernate.md#4-проблема-n1)
- Как обойти `LazyInitializationException`? → [hibernate](hibernate.md#5-lazyinitializationexception)
- Specification, Criteria API? → [hibernate](hibernate.md#10-spring-data)

### SQL и БД
- Порядок выполнения `SELECT`, `WHERE` vs `HAVING`? → [sql](sql.md#1-порядок-выполнения-запроса--главное-что-нужно-понять)
- Чем опасен `NOT IN`? → [sql](sql.md#3-null--источник-половины-подвохов)
- Виды JOIN, как найти «то, чего нет»? → [sql](sql.md#4-join--соединения-таблиц)
- Оконные функции, `rank` vs `dense_rank`? → [sql](sql.md#7-оконные-функции--то-что-отличает-знаю-sql-от-писал-30-запросов)
- ACID, аномалии, уровни изоляции, что по умолчанию в PostgreSQL? → [databases](databases.md#3-уровни-изоляции)
- Индексы: когда применяем, когда избегаем, почему индекс не используется? → [databases](databases.md#5-индексы)
- Оптимистичная и пессимистичная блокировка? → [databases](databases.md#lost-update-в-read-committed--частый-вопрос)
- Пагинация offset и keyset? → [databases](databases.md#8-пагинация-offset-vs-keyset-seek)
- Партиционирование, шардирование, репликация? → [databases](databases.md#9-масштабирование)

### Kafka и микросервисы
- Партиции и консьюмеры: что будет, если консьюмеров больше? → [kafka](kafka.md#5-консьюмер-и-consumer-group)
- `acks`, ISR, `min.insync.replicas`? → [kafka](kafka.md#3-репликация-и-отказоустойчивость)
- At-least-once, exactly-once, идемпотентный консьюмер? → [kafka](kafka.md#6-гарантии-доставки)
- Kafka vs RabbitMQ? → [kafka](kafka.md#1-что-такое-kafka-одной-фразой)
- Синхронное и асинхронное общение сервисов? → [microservices](microservices.md#как-сервисы-общаются)
- Transactional outbox, Saga, circuit breaker? → [microservices](microservices.md#transactional-outbox)
- CAP? → [microservices](microservices.md#cap-и-pacelc)
- Какие паттерны знаешь и использовал? Антипаттерны? → [patterns](patterns.md#3-основные-паттерны--суть-и-где-встречаются)

### AI
- Что такое RAG, из каких шагов состоит, где чаще всего ломается? → [ai](ai.md#4-rag--retrieval-augmented-generation)
- Эмбеддинги, векторный поиск, HNSW vs IVFFlat, зачем гибридный поиск? → [ai](ai.md#3-эмбеддинги-и-векторный-поиск)
- Как работает tool calling, кто выполняет функцию? → [ai](ai.md#6-tool-calling-function-calling)
- Что такое агент и harness, workflow или агент? → [ai](ai.md#7-агенты-и-harness)
- Что такое MCP? → [ai](ai.md#8-mcp--model-context-protocol)
- Как тестировать LLM-фичу, что такое evals? → [ai](ai.md#10-качество-как-проверять-llm-систему)
- Prompt injection и защита? → [ai](ai.md#prompt-injection--главная-уязвимость)

### Сети
- Идемпотентные методы HTTP? GET vs POST? → [web](web.md#2-http-методы)
- Принципы REST? → [web](web.md#4-rest)
- Как работает TLS? → [web](web.md#6-https-и-tls)
- JWT и OAuth2? → [web](web.md#8-аутентификация-jwt-oauth2)
