# Принципы и паттерны проектирования

[← Оглавление](README.md) · Паттерны микросервисов (outbox, saga, circuit breaker) — [microservices.md](microservices.md)

## 1. SOLID

- **S — Single Responsibility (единственная ответственность).** У класса должна быть одна причина для изменения — он отвечает перед одной «заинтересованной стороной». Признак нарушения: сервис и валидирует, и сохраняет, и отправляет уведомления, и форматирует отчёт.
- **O — Open/Closed (открытость/закрытость).** Модуль открыт для расширения и закрыт для изменения: новое поведение добавляют **новым кодом** (новый класс-реализация), не переписывая проверенный старый. Типичный способ — полиморфизм вместо растущего `if/switch` по типу.
- **L — Liskov Substitution (подстановка Лисков).** Объект подкласса должен работать везде, где ожидается базовый класс, **не нарушая ожиданий** вызывающего кода: не усиливать предусловия, не ослаблять постусловия, не бросать неожиданных исключений. Классика: `Square extends Rectangle` — `setWidth` у квадрата меняет и высоту, код, рассчитывающий на независимые стороны, ломается.
- **I — Interface Segregation (разделение интерфейсов).** Клиенты не должны зависеть от методов, которые не используют. Лучше несколько узких интерфейсов, чем один «толстый».
- **D — Dependency Inversion (инверсия зависимостей).** Модули верхнего уровня (бизнес-логика) не зависят от модулей нижнего уровня (БД, HTTP-клиенты) — оба зависят от **абстракций**, и абстракции принадлежат верхнему уровню. Пример: `PaymentService` зависит от интерфейса `PaymentGateway`, а реализация для конкретного провайдера — деталь. (DIP — принцип; DI в Spring — механизм, который помогает его соблюдать.)

Ещё принципы: **DRY** (не дублировать знание), **KISS** (проще — лучше), **YAGNI** (не делать «на будущее» то, что не нужно сейчас), **композиция предпочтительнее наследования**, **закон Деметры** (не лезть через цепочку `a.getB().getC().doX()`).

## 2. Виды паттернов GoF

- **Порождающие** — как создавать объекты: Singleton, Factory Method, Abstract Factory, Builder, Prototype.
- **Структурные** — как компоновать объекты: Adapter, Decorator, Proxy, Facade, Composite, Bridge, Flyweight.
- **Поведенческие** — как объекты взаимодействуют: Strategy, Chain of Responsibility, Observer, Template Method, Command, State, Iterator, Visitor, Mediator.

(Архитектурные паттерны — MVC, слоистая и гексагональная архитектура, микросервисные паттерны — отдельная категория, не GoF.)

## 3. Основные паттерны — суть и где встречаются

| Паттерн | Суть | Где в Java/Spring |
|---|---|---|
| **Singleton** | один экземпляр на приложение с глобальной точкой доступа | бины Spring со scope singleton (один на контекст, а не на JVM); `Runtime` |
| **Factory Method / Factory** | создание объекта делегировано отдельному методу/классу, вызывающий не знает конкретного класса | `BeanFactory`, `List.of()`, `Executors.newFixedThreadPool()` |
| **Builder** | пошаговое создание сложного объекта с множеством необязательных параметров | `StringBuilder`, `HttpRequest.newBuilder()`, Lombok `@Builder`, `UriComponentsBuilder` |
| **Adapter** | приводит интерфейс одного класса к интерфейсу, который ждёт клиент | `Arrays.asList`, `HandlerAdapter` в Spring MVC |
| **Decorator** | оборачивает объект тем же интерфейсом и **добавляет поведение**, можно навешивать слоями | `BufferedInputStream(new FileInputStream(...))`, `Collections.unmodifiableList` |
| **Proxy** | объект-заместитель с тем же интерфейсом **контролирует доступ** (ленивость, транзакции, безопасность, кэш) | AOP-прокси Spring, ленивые прокси Hibernate |
| **Facade** | простой интерфейс к сложной подсистеме | `JdbcTemplate`, сервис-фасад над несколькими сервисами |
| **Composite** | дерево объектов, с которым работают как с одним объектом | — |
| **Strategy** | семейство взаимозаменяемых **алгоритмов** за одним интерфейсом, выбор во время выполнения | `Comparator`, разные `PasswordEncoder`, способы оплаты |
| **Chain of Responsibility** | запрос проходит по цепочке обработчиков | фильтры Servlet и Spring Security, `HandlerInterceptor` |
| **Observer** | подписчики получают уведомления об изменении | `ApplicationEventPublisher` + `@EventListener`, Kafka как «распределённый observer» |
| **Template Method** | скелет алгоритма в базовом классе, шаги переопределяют наследники | `JdbcTemplate`, `AbstractController`, `TransactionTemplate` |
| **Command** | действие как объект (можно поставить в очередь, отменить, залогировать) | `Runnable`, задачи в executor |
| **State** | поведение объекта зависит от его состояния; каждое состояние — отдельный класс | автоматы состояний (Spring State Machine) — статусы заказа, документа |

**Decorator vs Proxy:** устроены одинаково (обёртка с тем же интерфейсом), различаются целью: декоратор **добавляет функциональность** и обычно собирается клиентом слоями; прокси **управляет доступом** к объекту и обычно подставляется прозрачно для клиента.

**Strategy vs State:** в Strategy алгоритм выбирает клиент снаружи; в State объект сам переключает своё поведение при смене состояния.

## 4. Strategy на Spring — вместо `if/else` и `switch`

```java
public interface PaymentProcessor {
    PaymentMethod method();                      // за какой способ оплаты отвечает
    PaymentResult process(Payment payment);
}

@Component class CardProcessor implements PaymentProcessor { ... }
@Component class SbpProcessor  implements PaymentProcessor { ... }

@Service
public class PaymentService {
    private final Map<PaymentMethod, PaymentProcessor> processors;

    public PaymentService(List<PaymentProcessor> all) {          // Spring внедрит все реализации
        this.processors = all.stream()
                .collect(Collectors.toMap(PaymentProcessor::method, p -> p));   // дубль ключа → ошибка при старте
    }

    public PaymentResult pay(Payment payment) {
        PaymentProcessor p = processors.get(payment.method());
        if (p == null) throw new IllegalArgumentException("Не поддерживается: " + payment.method());
        return p.process(payment);
    }
}
```

Новый способ оплаты — новый класс-бин, `PaymentService` не меняется (Open/Closed). Почему не `switch`: каждое новое значение требует правки общего класса, растёт метод, связанность и риск забыть ветку. (В современной Java `switch` по `sealed`-иерархии с проверкой полноты компилятором — тоже нормальный вариант, если набор вариантов закрыт и логика небольшая.)

## 5. Chain of Responsibility на Spring

Задача с собеседования: перед сохранением документа его нужно провалидировать. Проверок может быть сколько угодно, они разные (вплоть до вызова другого сервиса), их будет становиться больше.

```java
public interface DocumentValidator {
    void validate(Document doc);                 // бросает ValidationException при ошибке
}

@Component @Order(1) class FormatValidator    implements DocumentValidator { ... }
@Component @Order(2) class LimitsValidator    implements DocumentValidator { ... }
@Component @Order(3) class AntiFraudValidator implements DocumentValidator { ... }   // ходит в другой сервис

@Service
@RequiredArgsConstructor
public class DocumentService {
    private final List<DocumentValidator> validators;   // в порядке @Order

    public void save(Document doc) {
        validators.forEach(v -> v.validate(doc));
        repository.save(doc);
    }
}
```

Варианты: остановиться на первой ошибке или собрать все ошибки в список; «классическая» цепочка, где каждый обработчик решает, передавать ли дальше (`next.handle()`), — как фильтры Spring Security.

## 6. Архитектура приложения

- **Слоистая (layered):** контроллер → сервис → репозиторий. Просто и привычно; риск — бизнес-логика «размазывается» по сервисам, а доменные объекты становятся пустыми структурами данных (anemic domain model).
- **Гексагональная (ports & adapters) / Clean Architecture:** в центре — доменная модель и сценарии использования, они не зависят ни от Spring, ни от БД. Наружу смотрят **порты** (интерфейсы), а адаптеры (REST-контроллер, JPA-репозиторий, Kafka-листенер, HTTP-клиент) их реализуют. Плюсы — бизнес-логику легко тестировать, инфраструктуру — менять. Цена — больше кода и маппингов.
- **DDD (Domain-Driven Design), основные понятия:** ubiquitous language (общий язык с бизнесом), **bounded context** (границы модели — хороший кандидат на микросервис), **агрегат** (кластер объектов с одним корнем, который охраняет инварианты; транзакция — в пределах одного агрегата), value object (неизменяемое значение без идентичности — `Money`), доменные события.
- **MVC** — Model (данные), View (представление), Controller (обработка ввода). В REST API роль View играет JSON-представление ответа (DTO, сериализованный `HttpMessageConverter`).

## 7. Антипаттерны

- **God Object** — класс, который знает и делает всё.
- **Spaghetti code**, **copy-paste programming**.
- **Magic numbers / strings** — непонятные литералы вместо констант и enum.
- **Anemic domain model** — сущности без поведения, вся логика в «сервисах-процедурах» (спорно: для простых CRUD-систем это нормально).
- **Распределённый монолит** — микросервисы, которые нельзя выпускать независимо (общая БД, синхронные цепочки вызовов, общие библиотеки с моделью).
- **Golden hammer** — одно решение на все задачи («всё через Kafka»).
- **Premature optimization** — оптимизация без замеров.
- **Глотание исключений**, `catch (Exception e) {}`.
- **Синглтон как глобальное изменяемое состояние** — затрудняет тестирование и многопоточность.
- Для JPA: open-session-in-view, EAGER везде, сущности наружу из API.

## 8. Задача на ревью кода

```java
@Service
@RequiredArgsConstructor
public class DocumentServiceImpl implements DocumentService {
    private final DocumentMapper mapper;
    private final DocumentRepository repository;
    private final StateMachineFactory<DocState, DocEvent> stateMachineFactory;

    @Override
    @Transactional
    public DocumentDto create(DocumentDto dto) {
        Document doc = mapper.toEntity(dto);
        StateMachine<DocState, DocEvent> sm = stateMachineFactory.getStateMachine();
        sm.getExtendedState().getVariables().put("DOC_TO_BE_SAVED", doc);
        sm.start();
        doc.setStatus(sm.getState().getId());
        return mapper.toDto(repository.save(doc));
    }
}
```

На что обратить внимание:
- **SRP:** сервис одновременно маппит, управляет автоматом состояний и сохраняет. Работу с автоматом — в отдельный компонент (`DocumentLifecycle.initialState(doc)`).
- Автомат создаётся и запускается на каждый вызов и не останавливается — лишняя работа, возможна утечка ресурсов; передача объекта через «магическую строку» `"DOC_TO_BE_SAVED"` — вынести в константу или избавиться.
- Начальный статус документа — по сути константа; запуск всего автомата ради него избыточен.
- Не видно валидации (→ chain of responsibility, раздел 5) и обработки ошибок.
- Если после сохранения нужно уведомить другие сервисы — outbox, а не прямой вызов внутри транзакции.
