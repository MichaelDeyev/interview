# Тестирование

[← Оглавление](README.md)

## Пирамида тестов

- **Unit** (много) — один класс без Spring и без БД, зависимости — моки. Быстрые, точно показывают место ошибки.
- **Интеграционные** (средне) — слой вместе с реальной инфраструктурой: репозиторий с настоящим PostgreSQL, листенер с настоящей Kafka (**Testcontainers**), контроллер с сериализацией (`@WebMvcTest`).
- **Компонентные / end-to-end** (мало) — сервис целиком (`@SpringBootTest`) с заглушками внешних систем (**WireMock**) или вся система на стенде. Медленные и хрупкие.
- **Контрактные тесты** (Spring Cloud Contract, Pact) — проверяют, что API провайдера соответствует ожиданиям потребителей, без поднятия всей системы.
- **Нагрузочные** (Gatling, JMeter, k6) — отдельный вид, см. ниже.

## JUnit 5 и Mockito

```java
@ExtendWith(MockitoExtension.class)
class PaymentServiceTest {
    @Mock PaymentRepository repository;
    @Mock FraudClient fraudClient;
    @InjectMocks PaymentService service;     // при внедрении через конструктор можно просто new PaymentService(repository, fraudClient)

    @Test
    void rejectsFraudPayment() {
        when(fraudClient.check(any())).thenReturn(FraudResult.BLOCKED);

        assertThatThrownBy(() -> service.pay(payment()))
                .isInstanceOf(PaymentRejectedException.class);
        verify(repository, never()).save(any());
    }

    @ParameterizedTest
    @CsvSource({"0, false", "100, true", "-1, false"})
    void validatesAmount(BigDecimal amount, boolean valid) {
        assertThat(validator.isValid(amount)).isEqualTo(valid);
    }
}
```

- `@Test`, `@BeforeEach`/`@AfterEach`, `@BeforeAll`, `@DisplayName`, `@Nested`, `@Disabled`, `@Timeout`.
- **Параметризованные тесты** (`@ParameterizedTest` + `@ValueSource`, `@CsvSource`, `@MethodSource`) — ответ на вопрос «коллега на каждый кейс валидатора пишет отдельный тестовый метод, что предложишь?».
- Mockito: `when(...).thenReturn/thenThrow`, `verify(mock, times(1))`, `ArgumentCaptor`, `@Spy` (частичный мок). Не мокать то, что вам не принадлежит, и value objects; не проверять через `verify` каждый вызов — тест станет хрупким.
- Ассерты — AssertJ (`assertThat(list).hasSize(3).extracting(User::name).contains("Иван")`).
- Kotlin — MockK, Kotest.
- Структура теста: **given / when / then** (arrange / act / assert). Один тест — одно поведение. Имя теста описывает поведение, а не метод.

## Spring-тесты

| Аннотация | Что поднимает | Для чего |
|---|---|---|
| `@SpringBootTest` | весь контекст | компонентные тесты |
| `@WebMvcTest(Controller.class)` | только веб-слой + `MockMvc` | маршруты, валидация, сериализация, обработка ошибок, security |
| `@DataJpaTest` | JPA, репозитории, транзакция с откатом после теста | запросы репозиториев |
| `@JsonTest`, `@RestClientTest` | соответствующий срез | — |

- `@MockitoBean` (Spring Framework 6.2+) — подменить бин моком; заменяет устаревший `@MockBean`. Каждая уникальная комбинация моков создаёт **новый контекст** — тесты замедляются; кэш контекстов работает только при одинаковой конфигурации.
- **Testcontainers** — настоящие PostgreSQL, Kafka, Redis в Docker на время тестов. В Boot 3.1+ — `@ServiceConnection`, параметры подключения подставляются автоматически. H2 вместо PostgreSQL — плохая идея: другой диалект, нет многих возможностей, тест проходит — прод падает.
- **WireMock** — HTTP-заглушка внешнего сервиса: проверить таймауты, ошибки 5xx, повторы, circuit breaker.
- `@Transactional` на тесте откатывает изменения после теста, но **скрывает проблемы**: не происходит коммит (не проверяются отложенные ограничения, `@TransactionalEventListener` не срабатывает), ленивые связи грузятся без `LazyInitializationException`.

## Нагрузочное тестирование

- Виды: **нагрузочный** (ожидаемый профиль), **стресс** (поиск предела), **на выносливость** (soak — часами, ищем утечки), **пиковый** (spike).
- Инструменты: **Gatling** (сценарии на Scala/Java/Kotlin, хорошие отчёты), JMeter, k6.
- Что фиксировать: RPS, **перцентили задержки** (p95, p99, а не среднее), долю ошибок, утилизацию CPU/памяти/пулов/соединений БД, lag Kafka, GC-паузы.
- Методика: профиль нагрузки с прода, стенд, близкий к проду по ресурсам и объёму данных, прогрев JVM перед замером, по одному изменению за итерацию, поиск узкого места (профайлер — async-profiler, JFR; `EXPLAIN` для БД; метрики пулов).
- Частые находки: N+1, отсутствие индекса, маленький пул соединений или потоков, синхронные вызовы внутри транзакции, логирование в горячем пути, неудачные настройки GC и памяти.

## Покрытие и качество

- Покрытие (JaCoCo) — индикатор непокрытого кода, а не цель. 100% покрытия с плохими проверками ничего не гарантирует.
- **Мутационное тестирование** (PIT) — показывает, ловят ли тесты изменения в коде.
- Статический анализ — SonarQube, проверки в CI.
