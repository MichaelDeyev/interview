# Вопросы к собесу:
## Общее:
### Расскажи про свой опыт?
___
## Java
### Объясни public static void main(String[] args)
psvm - это точка входа Java-программы для виртуальной машины Java (JVM).
- `public`- чтобы JVM имела к нему доступ
- `static`- потому что JVM не умеет создавать экземпляры классов. JVM вызывает <ClassName>.<mainMethod>
- `void` - JVM не ожидает значения от main(). Если другой тип возвращаемого значения, то RunTimeError i.e., NoSuchMethodFoundError.
- `(String[] args)`. JVM вызывает main() передавая аргументы (типа String) командной строкой

### В чем особенность Generics?
Они существуют только в compile-time для сохранения обратной совместимости. Во время runtime generic-тип сводится либо к Object,
если сам параметр (например `Т`) не наследуется ни от какого класса, либо к родительскому классу.

### Расскажи про отличия Абстрактного класса от интерфейса?

### Если бы в Java не было множественного наследования через интерфейсы, то к какой проблеме это бы привело?
Интерфейсы бы раздувались до больших размеров, и нарушался бы Interface segregation principal

### Обработка исключений
1. try/catch
2. try/catch+finally. finally{} выполнится всегда, кроме случаев когда:
- самом блоке finally вылетает ошибка
- вызывается метод System.exit()
- операционная система завершит работу JVM
- Если блок finally будет выполняться потоком демона, а все остальные потоки не демоны завершат свое выполнение

### GC в Java? Какой по дефолту? Какой общий принцип действия? roots?
GC roots: static, class, thread, объекты со стека

### Объясни стримы? Для чего можно использовать flatMap?
???
### Если в методе создам локальную int x=5 и на следующей строке буду использовать его в стриме в лямбде, что будет?

### Объясни Java record?
Он final
#### В чем минус?
—сложно использовать cо SpringData

## Multithreading

#### Deadlock
Deadlock, или взаимная блокировка, возникает, когда есть несколько потоков и каждый ожидает ресурс,
принадлежащий другому потоку, так что формируется цикл из ресурсов и ожидающих их потоков.
Наиболее очевидным видом ресурса является монитор объекта, но любой ресурс, который вызывает блокировку (например,`wait/notify`), также подходит.
#### Livelock и потоковое голодание
Livelock возникает, когда потоки тратят все свое время на переговоры о доступе к ресурсу или обнаруживают и избегают тупиковой ситуации так,
что поток фактически не продвигается вперед. Голодание возникает, когда потоки сохраняют блокировку в течение длительных периодов,
так что некоторые потоки «голодают» без прогресса.

#### RaceCondition
Состояние гонки возникает, когда один и тот же ресурс используется несколькими потоками одновременно,
и в зависимости от порядка действий каждого потока может быть несколько возможных результатов.
___
## Spring
### Что такое Бин?
### Какие знаешь контейнеры бинов? 
### Какие есть способы объявить бин?
### Отличие аннотаций `@Component` `@Controller` `@RestController` `@Service` `@Repository` ?
@Controller (@RestController) говорит спрингу исследовать данный класс на наличие аннотации @RequestMapping. Другие стереотипные аннотации такого не делают
#### А семантическая разница?

### `@Transactional` где нужно использовать?
Не на все методы. Например, на методы которые просто читают из базы нет необходимости вешать @Transactional

### Способы внедрить зависимость? В чем отличие?
1. на поле через @Autowired 
2. через конструктор 
3. через сеттер (над методом)
- Через конструктор мы можем поменять DI фреймворк и функционал останется
- через @Autowired будет задействована рефлексия
- Однако если через ломбоковский конструктор (@RequiredArgs) делать внедрение, то если бина нет в контексте мы этого просто не заметим. 
Это является преимуществом использования @Autowired

### Кто вызывает методы контроллера ?
Dispatcher Servlet
___
## Hibernate
### Как можно улучшить код:
`for(int i=0, i<objectList.size(), i++){
repository.save(objectList.get(i))
}`

`objectList.forEach(repository::save)` // хибернейт сам может циклический INSERT мержить в 1 запрос (batchSize)

`repository.saveAll(objectList)`

### Объясни N+1
### Уровни изолированности БД
### Какой уровень по умолчанию в postgres
Read Committed
### Если в транзакционном методе сначала вызвать repository.save(obj), а в след строке obj.setName == "newName", то что сохраниться в БД?
В Hibernate персистентность происходит при закрытии транзакции, так что сохранится obj с полем name = "newName"   
### SQL-инъекции?
Инъекции возможны при использовании старых технологий. Например, JDBC Statement где не происходило экранирования запроса.
#### Пример: 
запрос `"SELECT * FROM Users WHERE name='{name}'"`, где `name` принимается из запроса по REST в какой-нибудь форме поиска. 
Тогда, в поле `name` при поиске можно было вбить `'; DELETE FROM Users WHERE name != '` и этот запрос отработает в БД, удалив все записи из таблицы `User`, при условии, что у таблицы есть поле `name`  
В дальнейшем технологии (JDBC PreparedStatement, Hibernate) научились экранировать все запросы и получалось `\\' ; DELETE FROM Users WHERE name !='\\` или использовать свой API для работы с запросами
### Разница между GET и POST запросом? (вопрос про возможность наличия body у GET)
___
## Паттерны
### Паттерны: какие есть виды паттернов?
### Назови 3 паттерна которые чаще всего используешь?
### В чем преимущества и недостатки монолита и микросервисной архитектуры?
### Паттерны МСА?
___
## Ситуации
### Ситуация: ты приходишь на новый проект, тебе выдают все доступы, но при сборке проекта мавеном у тебя не проходит часть артефактов. Твои действия?
- Взять у коллег файл `setting.xml`
### Как при сборке заигнорить тесты?
- `mvn -Dskip.test`
### Можно ли использовать версию библиотеки latest?
### Ты ревьвишь ПР и видишь что коллега теструет логику валидатора создавая на каждый кейс новый тестовый метод. Твои предложения?
___
## Рефакторинг
### <Код с проблемой транзакшионала>. Как можно решить эту проблему?
(рассмотреть вариант с AspectJ)

### <Код который показывает нарушение Single Responsability, на примере со стейт машиной>
```java
@Service
@RequiredArgsConstructor
public class ConfirmDocServiceImpl implements ConfirmDocService {

    private final ConfirmDocMapper confirmDocMapper;
    private final ConfirmDocRepository confirmDocRepository;
    private final ConfirmDocStateMachineService confirmDocStateMachineService;
    private final StateMachineFactory<DocStatusState, DocStatusEvent> confirmDocStateMachineFactory;
    
    @Override
    @Transactional
    public ConfirmDocDto createConfirmDoc(ConfirmDocDto confirmDocDto) {
        ConfirmDoc confirmDoc = confirmDocMapper.toEntity(confirmDocDto);
        StateMachine<DocStatusState, DocStatusEvent> sm = confirmDocStateMachineFactory.getStateMachine();
        sm.getExtendedState().getVariables().put("CONFIRM_DOC_TO_BE_SAVED", confirmDoc);
        sm.start();
        confirmDoc.setDocStatusId(sm.getState().getId());
        ConfirmDoc savedConfirmDoc = confirmDocRepository.save(confirmDoc);
        return confirmDocMapper.toDto(savedConfirmDoc);
    }
}
```
