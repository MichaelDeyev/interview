# Kotlin

[← Оглавление](README.md) · Многопоточность в Java — [concurrency.md](concurrency.md) · Spring — [spring.md](spring.md)

## Чем Kotlin отличается от Java (вопрос «на разогрев»)

**Коротко:** null-безопасность в системе типов, лаконичность (data-классы, свойства, вывод типов, именованные и дефолтные параметры), функции-расширения, корутины на уровне языка, неизменяемость по умолчанию в коллекциях, нет проверяемых исключений. Полностью совместим с Java в обе стороны и компилируется в тот же байткод.

- Классы и методы по умолчанию **`final`** (в Java — наоборот). Открыть — `open`.
- `val` — неизменяемая ссылка (как `final`), `var` — изменяемая.
- Нет примитивов на уровне языка: `Int`, `Long` компилируются в `int`/`long`, где возможно, и в `Integer`, где нужен объект (nullable-тип, generics).
- Нет `static` — вместо него `companion object`, функции верхнего уровня и `object`.
- `==` в Kotlin — это `equals()`, `===` — сравнение ссылок.
- `when` вместо `switch` — выражение, работает с типами, диапазонами и любыми условиями.
- Строковые шаблоны: `"Hello, $name, сумма ${order.total}"`.
- Компилятор **K2** (Kotlin 2.0, 2024) — новый фронтенд компилятора, заметно быстрее компиляция.

## Null-безопасность

```kotlin
var name: String = "a"     // не может быть null — компилятор не даст присвоить null
var email: String? = null  // nullable-тип

email.length               // ошибка компиляции
email?.length              // safe call: null, если email == null
email?.length ?: 0         // Elvis: значение по умолчанию
email!!.length             // «я уверен»: NPE, если null — использовать как можно реже
if (email != null) email.length   // smart cast: внутри if компилятор знает, что не null

email?.let { send(it) }    // выполнить блок, только если не null
```

- **Platform types (`String!`)** — значения из Java-кода: Kotlin не знает, может ли там быть null, и не проверяет. Здесь NPE возможен. Помогают аннотации `@Nullable`/`@NonNull` в Java-коде (Spring Framework 7 / Boot 4 перешли на аннотации **JSpecify**, и Kotlin видит null-безопасность Spring API).
- `lateinit var` — «проинициализирую позже, не null» (для DI в поле, тестов). Обращение до инициализации — `UninitializedPropertyAccessException`. Только для `var` и не-примитивов.
- `by lazy { }` — ленивое вычисление при первом обращении, по умолчанию потокобезопасно (synchronized).

## Классы

```kotlin
data class Money(val amount: BigDecimal, val currency: String)   // equals/hashCode/toString/copy/componentN

val m2 = m1.copy(amount = BigDecimal.TEN)    // копия с изменённым полем
val (amount, currency) = m1                  // деструктуризация

sealed interface PaymentResult {
    data class Success(val id: String) : PaymentResult
    data class Failure(val reason: String) : PaymentResult
    data object Pending : PaymentResult
}

fun render(r: PaymentResult) = when (r) {     // без else: компилятор проверяет, что все варианты учтены
    is PaymentResult.Success -> "ok ${r.id}"  // smart cast
    is PaymentResult.Failure -> "fail ${r.reason}"
    PaymentResult.Pending    -> "wait"
}

object Config { val timeout = 30 }            // синглтон

class User private constructor(val name: String) {
    companion object {                         // «статические» члены
        fun of(name: String) = User(name.trim())
    }
}

@JvmInline value class UserId(val value: Long)   // обёртка-тип без накладных расходов (в рантайме — просто long)
```

- **`data class`**: `equals`, `hashCode`, `toString`, `copy`, `componentN` — только по свойствам **основного конструктора**. Не может быть `open`/`abstract`.
- **`sealed`** — закрытая иерархия, все наследники известны компилятору → исчерпывающий `when`. Идеально для результатов операций, состояний, событий.
- **`object`** — синглтон, создаётся лениво и потокобезопасно. `companion object` — объект внутри класса.
- **`value class`** — типобезопасная обёртка (`UserId` вместо голого `Long`), компилятор по возможности разворачивает её до примитива.
- Свойства: `val name: String` — поле + геттер (+ сеттер для `var`). Можно свой `get()`/`set()`.
- Делегирование: `class Repo(private val delegate: List<X>) : List<X> by delegate` — реализация интерфейса через делегат (композиция без шаблонного кода).

## Функции

- Параметры по умолчанию и именованные аргументы — вместо перегрузок и билдеров: `createUser(name = "Иван", active = false)`. Для вызова из Java — `@JvmOverloads`.
- **Функции-расширения:** `fun String.isEmail(): Boolean = contains("@")` → `"a@b".isEmail()`. Разрешаются **статически** (по объявленному типу, а не реальному), не имеют доступа к `private` членам. Это синтаксический сахар над статической функцией.
- Функции высшего порядка и лямбды: `fun retry(times: Int, block: () -> Unit)`; если лямбда — последний аргумент, её выносят за скобки: `retry(3) { call() }`.
- **`inline`-функции** — тело функции и лямбды встраиваются в место вызова: нет объекта лямбды, можно `return` из внешней функции внутри лямбды. **`reified`** параметр типа (только в `inline`) — тип доступен во время выполнения: `inline fun <reified T> parse(json: String): T = mapper.readValue(json, T::class.java)`.
- Infix и operator-функции: `1 to "one"`, перегрузка `+`, `[]`.

### Scope-функции — частый вопрос

| Функция | Объект внутри как | Возвращает | Типичное применение |
|---|---|---|---|
| `let` | `it` | результат лямбды | действие над nullable: `x?.let { }`, преобразование |
| `run` | `this` | результат лямбды | вычислить что-то с объектом |
| `with(obj)` | `this` | результат лямбды | несколько вызовов на одном объекте |
| `apply` | `this` | **сам объект** | настройка объекта: `User().apply { name = "a"; age = 3 }` |
| `also` | `it` | **сам объект** | побочное действие: `.also { log.info("создан $it") }` |

## Коллекции

- Интерфейсы разделены: `List`/`Set`/`Map` — **только чтение**, `MutableList`/... — изменяемые. Это ограничение интерфейса, а не неизменяемость объекта: под `List` может лежать `ArrayList`.
- `listOf`, `mutableListOf`, `mapOf("a" to 1)`, `buildList { add(1) }`.
- Богатое API прямо на коллекциях: `filter`, `map`, `groupBy`, `associateBy`, `partition`, `chunked`, `windowed`, `sumOf`, `firstOrNull`. Эти операции **жадные**: каждая создаёт новый список.
- **`Sequence`** (`asSequence()`) — ленивые операции, как Java Stream: для длинных цепочек и больших коллекций без промежуточных списков.

## Корутины

**Коротко:** корутина — приостанавливаемое вычисление. `suspend`-функция может приостановиться (ожидая сеть или БД), **не блокируя поток**; поток в это время выполняет другие корутины. Код при этом пишется последовательно, без колбэков. Корутины очень лёгкие — можно запустить сотни тысяч.

```kotlin
suspend fun loadProfile(id: Long): Profile = coroutineScope {
    val user   = async { userClient.get(id) }        // запускаются параллельно
    val orders = async { orderClient.list(id) }
    Profile(user.await(), orders.await())            // если одна упадёт — вторая отменится
}
```

### Основные понятия

- **`suspend`** — функция, которая может приостановиться. Вызывается только из другой `suspend`-функции или из корутины. Компилятор превращает её в конечный автомат с объектом `Continuation` (CPS-преобразование): точки приостановки — состояния автомата.
- **Билдеры:** `launch` — запустить и не ждать результата (возвращает `Job`); `async` — запустить и получить результат позже (`Deferred<T>`, `await()`); `runBlocking` — блокирует текущий поток до завершения (только для `main` и тестов, **не в продакшн-коде** внутри сервиса).
- **`CoroutineScope`** — область жизни корутин. **Структурная конкурентность (structured concurrency):** корутина-родитель ждёт всех детей; ошибка ребёнка отменяет родителя и остальных детей; отмена родителя отменяет детей. Корутины не «утекают».
- `coroutineScope { }` — дочерняя область: ждёт всех, ошибка одного отменяет всех. `supervisorScope { }` — ошибка одного ребёнка **не** отменяет остальных.
- **`GlobalScope`** — без родителя и без отмены; почти всегда ошибка (утечки).
- **`Job`** — ручка корутины: `cancel()`, `join()`. **`SupervisorJob`** — ошибки детей не распространяются вверх.

### Диспетчеры — на каких потоках выполняется

| Диспетчер | Потоки | Для чего |
|---|---|---|
| `Dispatchers.Default` | по числу ядер | вычисления, нагрузка на CPU |
| `Dispatchers.IO` | большой пул (до 64 или числа ядер, если больше), общий с Default | **блокирующие** вызовы: JDBC, файлы, старые клиенты |
| `Dispatchers.Main` | UI-поток | Android/десктоп |
| `Dispatchers.Unconfined` | где придётся | редко, тесты |

```kotlin
val rows = withContext(Dispatchers.IO) { jdbcTemplate.query(...) }   // блокирующий код — на IO
```

**Главная ошибка:** вызвать блокирующий код (JDBC, `Thread.sleep`, синхронный HTTP-клиент) в корутине на `Default` или на event loop WebFlux. Поток заблокирован, корутины на нём стоят. Блокирующее — в `withContext(Dispatchers.IO)`; для ожидания — `delay()`, а не `Thread.sleep()`.

### Отмена и исключения

- Отмена **кооперативная**: корутина отменяется в точках приостановки (`delay`, `await`, `withContext`, `yield`) — там бросается `CancellationException`. Долгий цикл вычислений без приостановок нужно проверять вручную: `ensureActive()` / `isActive`.
- **Нельзя глотать `CancellationException`** (`catch (e: Exception)` её ловит!) — ломает отмену. Пробрасывать дальше или ловить конкретные исключения.
- В `launch` необработанное исключение уходит родителю (и в `CoroutineExceptionHandler` у корня); в `async` — выбросится при `await()`.
- `withTimeout(1000) { }` — отменить блок по таймауту.

### Flow

- **`Flow<T>`** — холодный асинхронный поток значений (аналог `Flux` в Reactor и `Sequence` для suspend): ничего не происходит, пока не вызвали терминальный оператор `collect`.
- Операторы: `map`, `filter`, `flatMapMerge`, `buffer`, `catch`, `retry`, `flowOn(Dispatchers.IO)` (меняет диспетчер для операций **выше** по цепочке).
- `StateFlow` (хранит последнее значение) и `SharedFlow` — **горячие** потоки, рассылка нескольким подписчикам.
- Backpressure естественный: `emit` приостанавливается, пока `collect` не обработал значение.

### Корутины в Spring

- Spring WebFlux (и Spring MVC с версии 5.3) поддерживают `suspend`-методы контроллеров и `Flow` в ответе. Spring Data — `CoroutineCrudRepository` для R2DBC.
- `kotlinx-coroutines-reactor`: `mono { }`, `.awaitSingle()` — мост между Reactor и корутинами.
- `@Transactional` работает с `suspend`-функциями только с реактивным менеджером транзакций (R2DBC). С JDBC — блокирующий код и `Dispatchers.IO`.
- Корутины vs виртуальные потоки vs WebFlux — в [concurrency.md](concurrency.md#10-виртуальные-потоки-java-21).

## Kotlin и Spring / JPA — подводные камни

- **Классы `final` по умолчанию**, а Spring создаёт CGLIB-прокси наследованием (`@Transactional`, `@Configuration`, `@Cacheable`). Нужен плагин компилятора **`kotlin-spring`** (all-open) — он делает `open` классы с аннотациями Spring. Без него `@Transactional` на final-методах молча не работает.
- **JPA-сущности:** нужен плагин **`kotlin-jpa`** (no-arg) — генерирует конструктор без аргументов для Hibernate; классы и свойства сущностей должны быть `open` (all-open для `@Entity`), иначе не работают ленивые прокси.
- **Не делать сущности `data class`:** сгенерированные `equals`/`hashCode`/`toString` по всем полям тянут ленивые связи (лишние запросы, `LazyInitializationException`, бесконечная рекурсия в двунаправленных связях) и ломают контракт при смене id. Обычный класс + `equals`/`hashCode` по id или бизнес-ключу.
- Jackson — модуль `jackson-module-kotlin` (Spring Boot подключает сам), чтобы работали data-классы без пустого конструктора и параметры по умолчанию.
- Конфигурация — `@ConfigurationProperties` с data-классом и `val` (binding через конструктор).
- Внедрение зависимостей — через конструктор: `class OrderService(private val repo: OrderRepository)`.

## Совместимость с Java

- `@JvmStatic` — сделать метод `companion object` настоящим статическим для Java.
- `@JvmField` — открыть свойство как поле без геттера.
- `@JvmOverloads` — сгенерировать перегрузки для параметров по умолчанию.
- `@Throws(IOException::class)` — объявить проверяемое исключение для Java-кода.
- Kotlin-код из Java выглядит как обычные классы: свойства — геттеры/сеттеры, функции верхнего уровня — статические методы класса `ИмяФайлаKt`.

## Короткие ответы

- **`val` vs `var` vs `const val`?** Неизменяемая ссылка / изменяемая / константа времени компиляции (только примитивы и `String`, верхний уровень или `object`).
- **`lateinit` vs `by lazy`?** `lateinit var` — присвоим позже снаружи; `by lazy` — `val`, значение вычислится само при первом обращении.
- **Что такое `Unit`, `Nothing`, `Any`?** `Unit` — «нет значения» (как `void`, но это объект). `Nothing` — функция никогда не возвращает (всегда бросает исключение, `TODO()`), подтип всех типов. `Any` — корень иерархии (как `Object`), `Any?` — включая null.
- **Есть ли checked exceptions?** Нет. Для Java-вызывающих — `@Throws`.
- **Как работает extension-функция под капотом?** Статический метод, где получатель — первый параметр. Не переопределяется полиморфно.
- **Чем `launch` отличается от `async`?** `Job` без результата против `Deferred` с результатом; ошибка `launch` сразу идёт родителю, ошибка `async` — при `await`.
- **Корутина vs поток?** Корутина — объект в куче с состоянием автомата, приостанавливается без блокировки потока; потоков мало и они дорогие, корутин — сотни тысяч.
