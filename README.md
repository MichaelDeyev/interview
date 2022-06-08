## JAVA CORE

### 1. Методы Object.class
`toString()`,
`equals()`,
`hashcode()`,
`wait()`,
`notify()`,
`notifyAll()`,
`getClass()`.
### 2. equals() & hashcode()
- `equals()` гарантирует: если `o1.equals(o2)` вернул `true`, то объекты равны. Если `false`, то элементы точно _не равны_ друг другу.

- `hasCode()` гарантирует что если у 2х объектов разные хэшкоды - эти объекты точно разные, а если хэшкоды равны то либо объекты равны, либо произошла коллизия.

_Прим.:_ При вызове o1.equals(o2) сначала сравниваются их хэшкоды, если хеши не равны, выдаётся `false`, если равны, то вызывается метод `equals()`, который работает долго, но выдаёт точный ответ. (сравнивая объекты по ссылкам)

_Стоит отметить, что для корректной работы, при создании собственного класса, всегда нужно переопределять методы `equals()` и `hasCode()`._
- Рефлексивность. для любого заданного значения x, выражение x.equals(x) должно возвращать true. (Заданного — имеется в виду такого, что x != null)
- Симметричность. для любых заданных значений x и y, x.equals(y) должно возвращать true только в том случае, когда y.equals(x) возвращает true.
- Транзитивность. для любых заданных значений x, y и z, если x.equals(y) возвращает true и y.equals(z) возвращает true, x.equals(z) должно вернуть значение true.
- Согласованность. для любых заданных значений x и y повторный вызов x.equals(y) будет возвращать значение предыдущего вызова этого метода при условии, что поля, используемые для сравнения этих двух объектов, не изменялись между вызовами.
- Сравнение null. для любого заданного значения x вызов x.equals(null) должен возвращать false

### 3. public static void main(String[] args)
psvm - это точка входа Java-программы для виртуальной машины Java (JVM).
- `public`- чтобы JVM имела к нему доступ
- `static`- потому что JVM не умеет создавать экземпляры классов. JVM вызывает <ClassName>.<mainMethod>
- `void` - JVM не ожидает значения от main(). Если другой тип возвращаемого значения, то RunTimeError i.e., NoSuchMethodFoundError.
- `(String[] args)`. JVM вызывает main() передавая аргументы (типа String) командной строкой

### 4. Exceptions (Исключения)
#### Иерархия
![](img/exception hieracy.png)

_Прим:_
При создании собственного исключения, если мы хотим сделать его проверяемым мы должны наследовать его, например, от I/O Exception

#### Обработка исключений
1. try/catch
2. try/catch+finally. finally{} выполнится всегда, кроме случаев когда:
- самом блоке finally вылетает ошибка
- вызывается метод System.exit()
- операционная система завершит работу JVM
- Если блок finally будет выполняться потоком демона, а все остальные потоки не демоны завершат свое выполнение

3. try with resources. В try создаем некие сущности, которые должны поддерживать интерфейс AutoClosable. По окончанию блока try,
   не зависимо от того было ли исключение или нет, эти сущности закроются. (исп. для чтения потоков или соединения с БД)
#### Можно ли поймать Runtime exception?
Да, можно
#### Когда следует ловить Error?
В общем случае его не стоит ловить, но в частном случае OutOfMemoryErr иногда полезно отлавливать.

### 5. Абстрактный класс vs Интерфейс
1. Интерфейс описывает только поведение. У него нет состояния. А у абстрактного класса состояние есть: он описывает и то и другое. (в абс. классе можно создавать переменные и сеттеры\геттеры для них, в интерфейсе – нет).
2. Абстрактный класс связывает между собой и объединяет классы, имеющие очень близкую связь (абстр. Класс Птица и Класс наследник Соловей).
 В то же время, один и тот же интерфейс могут реализовать классы, у которых вообще нет ничего общего (инт. Летающий и реализующие его классы Птица и Самолёт).
3. Разрешена множественная реализация интерфейсов (множественное наследование классов запрещено)

#### Дефолтная реализация интерфейсов
1. Сохранение обратной совместимости. Чтобы не было нужды переопределять новый метод интерфейса всех его реализациях,
   пишешь `default` перед названием метода в интерфейсе и всё.
2. Реализация по-дефолту

_Прим.:_ Если класс реализует 2 интерфейса, в каждом из которых есть одинаково названные дефолтные методы, неообходимо будет в явном виде переопредлить
этот метод в классе и указать, чью именно реализацию использовать.

```java
public class Car implements Vehicle, Alarm {

    @Override
    public String turnAlarmOn() {
        return Vehicle.super.turnAlarmOn();
    }
    
    @Override
    public String turnAlarmOff() {
        return Vehicle.super.turnAlarmOff();
    }
}
``` 

#### Functional interface
Интерфейс с одним абстрактным методом @FunctionalInterface. Например: consumer, supplier, function, predicate, operator и их биформы. 
Кол-во `default` методов не ограничено.

_Прим.:_ Их не было до java 8. Нужны же они для обратной совместимости, а также это позволяют избежать 
создания служебных классов, так как все необходимые методы могут быть представлены в самих интерфейсах

### 6. Collections
#### Иерархия
![](img/collections-hierarchy.png)
#### Как внутри устроена HashMap?
HashMap состоит из массива односвязных списков - бакетов, размером 16.
При добавлении пары K-V в HashMap высчитывается hashcode ключа `key.hashcode()` и побитово умножается на (n-1), где n - длинна внутреннего массива.
Получается число от 0 до n-1. Данная пара K-V помещается в ячейку соответствующей, числу, полученному в предыдущей операции.
Со всеми следующими парами K-V работа аналогичная.
Если элементов становится слишком много, в HashMap выделяется еще один массив размерностью 16 (_Или каждый бакет становится красно-черным деревом_)
#### Как внутри устроена TreeMap?
Красно-черное дерево

#### Можно ли положить в HashMap объекты, у которых не переопределены методы `equals()` и `hasCode()`?
Можно, но тогда теряется эффективность и скорость работы HashMap

#### Как по другому можно заимплементить Map?
Как простой массив []

### 7. Multithreading (Многопоточность)
#### Способы создания потока:
1. `Clazz extends Thread`. В таком случае клас будет _являться_ потоком.
   Для запуска вызываем метод `start()`
2. `Clazz implements Runnable` переопределить единственный метод `run()`, внутри которого указать, что конкретно будет выполняться данным потоком

_Эти способы не используются на реальных проектах. У разработчика не должно быть возможности самому создавать треды, иначе может начать вылетать ошибки.
Например, Разработчик создал много тредов и, так как под каждый новый тред выделяется фиксированное количество мегабайт (например, 1Мб), то программа начинает уходить в своп при переполнении оперативной памяти._
3. `concurrent.ExecutorService` - фреймворк для работы с потоками. Также в этом фреймворке есть классы для работы с ассинхронностью.

#### Как сделать метод потокобезопасным?
`synchronized` Можно сделать синхронизацию либо по объекту, либо по методу.

#### Какие есть методы для работы с потоками?
`wait(), notify(), notifyAll()`

_Их можно использовать только в synchronized блоках_


#### Deadlock 
Deadlock, или взаимная блокировка, возникает, когда есть несколько потоков и каждый ожидает ресурс, 
принадлежащий другому потоку, так что формируется цикл из ресурсов и ожидающих их потоков. 
Наиболее очевидным видом ресурса является монитор объекта, но любой ресурс, который вызывает блокировку (например,`wait/notify`), также подходит.

Взаимная блокировка происходит, если в одно и то же время:

- Один поток пытается перенести данные с одного аккаунта на другой и уже наложил блокировку на первый аккаунт.
- Другой поток пытается перенести данные со второго аккаунта на первый, и уже наложил блокировку на второй аккаунт.

_Предотвращение deadlock_:
- Порядок блокировок — всегда накладывайте блокировки в одном и том же порядке.
- Блокировка с тайм-аутом — не блокируйте бессрочно при наложении блокировки, 
лучше как можно быстрее снимите все блокировки и попробуйте снова.

_JVM способен обнаруживать взаимные блокировки мониторов и выводить информацию о них в дампах потоков_ 

#### Livelock и потоковое голодание
Livelock возникает, когда потоки тратят все свое время на переговоры о доступе к ресурсу или обнаруживают и избегают тупиковой ситуации так, 
что поток фактически не продвигается вперед. Голодание возникает, когда потоки сохраняют блокировку в течение длительных периодов, 
так что некоторые потоки «голодают» без прогресса.

#### RaceCondition
Состояние гонки возникает, когда один и тот же ресурс используется несколькими потоками одновременно, 
и в зависимости от порядка действий каждого потока может быть несколько возможных результатов. 
Код, приведенный ниже, не является потокобезопасным, и переменная value может быть инициализирована больше, 
чем один раз, так как `check-then-act` (проверка на `null`, а затем инициализация), которая лениво инициализирует поле, не является _атомарной_
```java
class Lazy <T> {
 private volatile T value;
 T get() {
   if (value == null)
     value = initialize();
   return value;
 }
}
```
#### CAS ????
#### Типы данных concurrency (Atomics, ConcurrentHashMap) ????
#### ExecutorService ????

### 8. JMM
Память процесса делится на Stack и Heap и включает 5 областей:
- **_Stack_**
1. Permanent Generation — используемая JVM память для хранения метаинформации; классы, методы и т.п. 
2. Code Cache — используемая JVM память при включенной JIT-компиляции; в этой области памяти кешируется скомпилированный платформенно-зависимый код.
- **_Heap_**
1. Eden Space — в этой области выделяется память под все создаваемые программой объекты. Жизненный цикл большей части объектов, к которым относятся итераторы, объекты внутри методов и т.п., недолгий. 
2. Survivor Space — здесь хранятся перемещенные из Eden Space объекты после первой сборки мусора. Объекты, пережившие несколько сборок мусора, перемещаются в следующую сборку Tenured Generation. 
3. Tenured Generation хранит долгоживущие объекты. Когда данная область памяти заполняется, выполняется полная сборка мусора (full, major collection).

#### Команды для управления размерами Heap
- `java –Xmx4G` - максимальны размер 4Gb
- `java –Xms4G` - начальный размер 4Gb

### 9. Garbage Collector
#### Задачи GC
1. Reference counting – учет ссылок. Каждый объект имеет счетчик (количество указывающих на него ссылок).
когда счетчик = 0 объект считается мусором. Из-за невозможности работы с циклическими зависимостями данный подход не используется.  
2. Tracing – трассировка. Идея: до «живого» объекта можно добраться из корневых точек (_GC Root_). 
Всё, что доступно из «живого» объекта, также является «живым». Если представить все объекты и ссылки между ними как дерево, 
то необходимо пройти от корневых узлов GC Roots по всем узлам. При этом узлы, до которых нельзя добраться, являются мусором.

![](img\garbage-collection1.png)

#### GC Root
- Основной Java поток - поток, который выполняет main
- Локальные переменные в основном методе - параметры main метода и локальные переменные внутри main метода
- Статические переменные основного класса - статические переменные основного класса, внутри которого находится main метод

#### Типы GC
- Serial Garbage Collector
- Parallel Garbage Collector
- CMS Garbage Collector
- G1 Garbage Collector (default)
- Shenandoah


### 10. ClassLoader
Загрузчик классов отвечает за поиск библиотек, чтение их содержимого и загрузку классов, содержащихся в библиотеках. 
Эта загрузка обычно выполняется «по требованию», поскольку она не происходит до тех пор, пока программа не вызовет класс. 
Класс с именем может быть загружен только один раз данным загрузчиком классов.

Сам загрузчик классов является частью JRE, которая динамически загружает Java классы в JVM. 
Система исполнения в Java не должна знать о файлах и файловых системах благодаря загрузчику классов. 
Делегирование является важной концепцией, которую выполняет загрузчик.

Всего их три вида:
1. Загрузчик класса bootstrap. Загружает основные библиотеки расположенные в папке <JAVA_HOME>/jre/lib. 
2. Загрузчик класса расширений. Загружает код в каталоги расширений (<JAVA_HOME>/jre/lib/ext, или любой другой каталог, указанный системным свойством java.ext.dirs).
3. Системный загрузчик. Загружает код, найденный в java.class.path, который сопоставляется с переменной среды CLASSPATH

## Структуры данных
### 1. Структуры данных
#### Динамический массив ????
#### Связный список ????
#### Бинарное(двоичное) дерево
Всё, что меньше корня идёт по левой ветке, всё что больше по правой. Корень - первый элемент, помещенный в дерево,
листья - последние элементы, ноды(узлы) - промежуточные. Каждая нода с его потомками отдельное дерево.

Бинарное дерево лучше использовать при неотсортированных данных.
Если в бинарное дерево подавать отсортированные данные, то оно вырождается в двусвязный список.
Сложность всех операций (bad way) такая же, как и у двусвязного списка `O(n)` (медленная)

#### Красно-черное дерево
Самобалансирующееся Бинарное дерево, такое что:
1. Количество черных нод в каждой ветке держится одинаковым.
2. Корень глобального дерева всегда черный (корни поддеревьев могут быть красными)
3. У каждой красной ноды дочки черные
4. Листья (последние элементы в ветке) всегда черные и null.

_Когда одна ветвь становится длиннее других, происходит перебалансировка_

Сложность по всем операциям - `O(log(n))`
#### Б-дерево ??? (каждая нода - массив)

### 2. Алгоритмическая сложность
![](img/algoryth-difficulty1.jpg)

### 3. Сортировки

#### Сортировка пузырьком

```java
class Scratch {
    public int[] bubbleSort(int[] arr) {
        for(int i = arr.length-1 ; i > 0 ; i--) {
            for(int j = 0 ; j < i ; j++){
                if( arr[j] > arr[j+1] ) {
                    int tmp = arr[j];
                    arr[j] = arr[j+1];
                    arr[j+1] = tmp;
                }
            }
        }
    }
}
```
## Паттерны
### 1. SOLID
- S _single responsibility principle_- принцип единственности ответственности.
У каждого класса должен быть только один мотив для изменений

- O _open/closed principle_ – принцип открытости\закрытости. Класс должен быть открыт для расширения и закрыт для изменения.
Нужно стараться расширять (extend) классы, а не изменять их (Не ломать уже существующий код)

- L _Принцип подстановки Лисков_. Подклассы должны дополнять, а не замещать поведение базового класса.
(Тип ПАРАМЕТРОВ МЕТОДА подкласса должен совпадать или быть более абстрактным, чем типы параметров базового класса,
и наоборот тип ВОЗВРАЩАЕМОГО ЗНАЧЕНИЯ метода подкласса должен совпадать или быть подтипом возвращаемого значения базового класса)

- I _interface segregation principle_. Принцип разделения интерфейса. Клиенты не должны зависеть от методов, которые они не используют.
(нужно стараться делать узкоспециализированные интерфейсы, чтобы не приходилось реализовывать избыточное поведение)

- D _Принцип инверсии зависимости_. Классы верхних уровней не должны зависеть от классов нижних уровней. Оба должны зависеть от абстракций.
Абстракции не должны зависеть от деталей. Детали должны зависеть от абстракций. (Зависимости должны быть не напрямую (сильными),
а через абстракции(слабыми)). _Прим.:_ Зависимости через интерфейсы, а не через наследование

### 2. GOF
- Декоратор - композиция. Один класс внедрён в другой класс как поле.
- Фасад - инкапсуляция. сложная реализация спрятана за удобными методами.
- Фабрика - очень похож на _Builder_. Специальный класс , которому делегируем создание экземпляра другого класса. Те же функции берет на себя и фабричный метод.
- Singleton. Разрешает создавать не более одного экземпляра класса.
- Strategy. В зависимости от состояния выполнить то или иное действие (switch/case, if/else)

## Базы данных
### 1. ACID
_Атомарность_ (atomicity). Атомарность гарантирует, что каждая транзакция будет выполнена полностью или не будет выполнена совсем.
Не допускаются промежуточные состояния.

_Согласованность_ (consistency). В результате работы транзакции данные будут допустимыми.
Это вопрос не технологии, а бизнес-логики: например, если количество денег на счете не может быть отрицательным, логика транзакции должна проверять, не выйдет ли в результате отрицательных значений.

_Изолированность_ (isolation). Гарантия того, что параллельные транзакции не будут оказывать влияния на результат других транзакций.

_Долговечность_ (durability). Изменения, получившиеся в результате транзакции, должны оставаться сохраненными вне зависимости от каких-либо сбоев.
Иначе говоря, если пользователь получил сигнал о завершении транзакции, он может быть уверен, что данные сохранены.

### 2. Изолированность БД (TODO refactor)
- _Версионирование_ (snapshot) означает, что транзакции будут работать со своей копией данных, не влияя друг на друга,
но впоследствии несколько изменённых копий надо будет как-то слить в одну. Строгость версионирования регулирует моменты (когда) и размеры (сколько данных копировать) этих копий.
- _Блокирование_ (lock) означает, что одна транзакция будет ждать другую, чтобы избежать побочных эффектов,
в зависимости от строгости уровней изоляции этих транзакций. Различные виды блокировок обеспечивают более гранулярное блокирование,
например, только по строкам, или только на небольшой кусочек транзакции, а не на всю.

### 3. Уровни изолированность БД (TODO refactor)
- _Read Uncommitted_. Ничего не происходит в режиме read uncomitted. То есть ничего не блокируется и не создаются снэпшоты, транзакция просто читает всё что хочет.
По смыслу, этот режим можно отнести к (очень) оптимистичному — блокировки редки и коротки.
- _Read committed_ (то есть отсутсвие dirty reads) обеспечивается блокировкой на запись данных (строк), которые мы пытаемся прочитать.
Эта блокировка гарантирует, что мы подождём завершения транзакций, которые уже меняют наши данные, или заставим их подождать, пока мы будем читать.
В итоге, мы точно прочитаем только данные, которые были закоммичены, избежав тем самым грязное чтение. Этот режим — типичный пример пессимистичной блокировки, так как мы блокируем данные на запись, даже если в них никто реально не пишет.
- _Read commited_ snapshot (второй способ избежать dirty reads) обеспечивается версионированием блока данных, который мы читаем.
Любое его параллельное изменение на затронет нашу версию, и нам достанутся данные на момент начала чтения. Таким образом грязное чтение отсутствует, и ещё отсутствуют какие-либо блокировки*. Этот режим скорее оптимистичный, так как заранее ничего не блокируется, и тут как раз может быть конфликт обновления.
- _Repeatable read_ (то есть отсутствие всего, кроме фантомных чтений) обеспечивается почти как read commited, за тем исключением,
что блокировка на запись работает до конца транзакции, а не отдельной операции. Единожды “коснувшись” блока данных, транзакция блокирует его изменение до конца работы, что обеспечивает отсутствиуе dirty reads и non-repeatable reads.
Это более пессимистичный вид блокировки, чем read committed, так как блокировка держится ещё дольше.
- _Serializable_ (нет никаких побочных эффектов) обеспечивается блокировкой и на запись, и на чтение любого блока данных, с которым мы работаем.
Блокируется даже вставка данных, которые могут попасть в блок, который мы прочитали. Таким образом, за счёт низкой конкурентности, обеспечивается отсутствие даже фантомных чтений. Это более пессимистичный вид блокировки, чем repeatable read, так как блокировка держится ещё дольше.
- _Snapshot_ обеспечивается созданием нашей отдельной версии данных, с которыми мы работаем, без блокировок*.
Другие транзакции не будут иметь доступ к нашей версии, чем и обеспечивается отсутствие всего вплоть до фантомных чтений. Это оптимистичный вид блокировки, но менее оптимистичный, чем read committed snapshot, так как больше шансов получить конфликт обновления.

### 4. Нормализация БД ???
Нормализация БД – устранение избыточности

## SPRING
### 1. В чем идея Spring?
1. Внедрение и управление зависимостями (Dependency injection).
2. Инверсия управления (IoC)
3. Предоставление удобных интерфейсов для взаимодействия с Вебом.

### 2. Что такое Bean?
Т.н. "Спринговский класс", то есть это обычный java-класс, который внесли в контекст спринга (SpringApplicationContext) - контейнер бинов.
#### Способы создать бин
1. Через XML
```xml
<beans>
   <!-- A simple bean definition -->
   <bean id = "fromBeanMessage" class = "com.example.Message">
       <property name="message" value="This is message from simple bean"/>
      <!-- collaborators and configuration for this bean go here -->
   </bean>
   <!-- A bean definition with lazy init set on -->
   <bean id = "lazy" class = "com.example.Lazy" lazy-init = "true">
      <!-- collaborators and configuration for this bean go here -->
   </bean>
   <!-- A bean definition with initialization method -->
   <bean id = "init" class = "com.example.Message" init-method = "getMessage">
      <!-- collaborators and configuration for this bean go here -->
   </bean>
   <!-- A bean definition with destruction method -->
   <bean id = "destroyBean" class = "com.example.Message" destroy-method = "getMessage">
      <!-- collaborators and configuration for this bean go here -->
   </bean>
</beans>
```
2. Через java-код
3. Через аннотации
`@Component` - вешается над классом, говоря спрингу, что от данного класса нужно создать бин
`@Bean` - вешается над методом, возвращаемое значение которого будет являться бином.
Используется в классах помеченных `@Configuration`

#### Жизненный цикл бина
![](img\bean-lifecycle.png)

#### Init/destroy - методы
- init-метод вызывается сразу после внедрения в бин всех необходимых зависимостей.
- destroy-метод вызывается после остановки контекста

_Прим.:_ post-destroy у прототипов не вызывается

#### BeanDefiniton ???
#### BeanPostProcessor ???

#### Bean scope (область видимости бина)
- _Singleton_ (по умолчанию). Бин с данным именем создаётся 1 раз в Spring Application Context и каждый раз при вызове getBean() вызывается тот самый бин. Используется, когда у бина нет изменяемых состояний (stateless)
- _Prototype_. При вызове getBean() каждый раз будет создаваться новый бин в Spring Application Context. Используется, когда у бина есть изменяемые состояния (statefull)
- _Request_. Создаётся один экземпляр бина на каждый HTTP запрос. Касается исключительно ApplicationContext.
- _Session_. Создаётся один экземпляр бина на каждую HTTP сессию. Касается исключительно ApplicationContext.
- _Global-session_. Создаётся один экземпляр бина на каждую глобальную HTTP сессию. Используется только с портлетами. Касается исключительно ApplicationContext.

### 2. Виды контейнеров бинов.
В Spring имеется 2 различных вида контейнеров:
1. Spring BeanFactory Container. Реализации: XmlBeanFactory
2. Spring ApplicationContext Container. Реализации: FileSystemXmlApplicationContext, ClassPathXmlApplicationContext, WebXmlApplicationContext

### 3. Аннотации
- `@ComponentScan` вместе с аннотацией `@Configuration`, чтобы указать пакеты, которые мы хотим сканировать.
`@ComponentScan` без аргументов указывает Spring сканировать текущий пакет и все его подпакеты.
- `@Autowired`. В `SpringApplicationContext` хранятся все бины (Классы, на которых висит `@Component` или их бин создан в явном виде в xml или через `@Bean`).
`@Autowired` внедряет ссылку на существующий бин в поле, над которым висит `@Autowired`.
Если scope бина “prototype”, то при `@Autowired` полю присваивается ссылка на новый бин.
_Прим.: Внедрять зависимости через `@Autowired` следует через конструктор, тк через конструктор зависимости могут быть final,
а значит потокобезопасными. Также, можно не писать @InjectMocks при написании юнит-тестов._
- `@Service`, `@Controller`, `@Repository` - аналоги `@Component` (синтаксический сахар)
- `@RestController` = `@Component` + `@ResponceBody`
- `@Qualifier`. Используется для указания конкретного бина для внедрения в другой бин при условии, что есть несколько бинов одного типа
- `@Primary`. Определяет предпочтение, когда присутствует несколько bean-компонентов одного типа.
Компонент, связанный с аннотацией @Primary, будет использоваться, если не указано иное.
- `@Transactional`. Делает методы над которыми висит транзакционными (обладающими свойствами транзакции)
[https://habr.com/ru/post/532000/]()

### 4. @Transactional
#### Будет ли при вызове method2 из метода method1 создана новая транзакция?
```java
public class MyServiceImpl {

    @Transactional
    public void method1() {
        //do something
        method2();
    }

    @Transactional (propagation=Propagation.REQUIRES_NEW)
    public void method2() {
        //do something
    }
}
```
_Ответ:_ Для поддержки транзакций через аннотации используется Spring AOP, в момент вызова method1() на самом деле вызывается метод прокси объекта.
Создается новая транзакция и далее происходит вызов method1() класса MyServiceImpl.
А когда из method1() вызовем method2(), обращения к прокси нет, вызывается уже сразу метод нашего класса и, соответственно, никаких новых транзакций создаваться не будет
_Решение:_:
1. Рефакторинг. Создание новой абстракции (например `Facade`), которая будет атомарно вызывать методы сервиса, помеченные `@Transactional`.
Таким образом избегается перекрестный вызов транзакционных методов друг-другом
2. Self-inject класса и вызов метода через него. _Прим.:_ Работает только для бинов со scope `singleton`,
для `prototype` при старте приложения упадёт ошибка циклического внедрения бина самого в себя
```java
@Service
@Transactional
class Clazz {
    
@Autowired
Clazz clazz;

  void method1(){//транзакция создается
    clazz.method2();//транзакция создается
  }
  void method2(){
  }
}
```
3. Использовать TransactionTemplate

_Пример:_
```java
transactionTemplate.execute(new TransactionCallback()
   {
    // код в этом методе выполняется в транзакционном контексте         
    public Object doInTransaction(TransactionStatus status)
    {               
    updateOperation1();    
       return resultOfUpdateOperation2();   
    }
  });  
```

### 5. Spring AOP
[https://habr.com/ru/post/347752/]()

#### Создание прокси
Проксирование происходит на этапе создания бинов. Реализуется паттерн Proxy. Для того чтобы
#### (CGLib VS JDK Dynamic proxy)
- JDK Dynamic proxy может проксировать только по интерфейсу (целевой класс должен имплементить интерфейс, который потом заимплементит проксирующий класс).
- CGLib может создать прокси по подклассу (наследованием). CGLib по факту создаёт наследника нашего класса, поэтому при использовании CGLib не получится делать `final`-классы

_Прим1:_ поскольку javassist и CGLIB используют прокси путем создания подклассов, по этой причине вы не можете объявлять `final`
методы или делать класс `final` при использовании фреймворков, которые полагаются на это. Это помешает этим библиотекам создавать подклассы вашего класса и переопределять ваши методы

_Прим2:_ CGLib быстрее на 15%, чем DynamicProxy.

_Прим3:_ По умолчанию, если класс реализует хотя бы один (_не пустой, как Serializable_) интерфейс, то будет использоваться JDK dynamic proxy для создания прокси.
Изменить поведение по умолчанию можно настройкой `proxy-target-class=true`. _Это в старых версиях SpringBoot.
С версии SpringBoot 2.0 - наоборот, по умолчанию используется CGLib (проксирование через наследование)_

### 6. SpringData
#### Интерфейсы SpringData
- CrudRepository
- PagingAndSortingRepository
- JpaRepository

### 7. Замена switch/case с использованием спринга (полиморфизма)


## Hibernate
### Ошибка N+1
[https://yannbriancon.com/blog/eliminate-hibernate-n-plus-one-queries/](https://yannbriancon.com/blog/eliminate-hibernate-n-plus-one-queries/)

Проблема N+1 это при `fetch.Type.EAGER` подгружается вся структура сущности + ее наследники (которых N штук).
Каждая из дочерних сущностей подгружается отдельным запросом. Итого идут запросы на получение N (всех связанных элементов)+ 1(основной элемент).
#### Решение N+1
Подход Spring Data:

`@Fetch.Type.Lazy`

_User one2many Role_
```java
public interface UserRepository extends CrudRepository<User, Long> {
// Проблема
    List<User> findAllBy(); // происходит проблема N+1

// Решение 1
    @Query("SELECT p FROM User p LEFT JOIN FETCH p.roles")  
    List<User> findWithoutNPlusOne(); // используя LEFT JOIN, мы решаем проблему N + 1

// Решение 2
    @EntityGraph(attributePaths = {"roles"})                
    List<User> findAll(); //используя attributePaths, Spring Data JPA позволяет избежать проблемы N + 1

}
```


## Сети
### 1. Как работает HTTP ???
### 2. Коды ответов на HTTP-запрос
200 ок, 300 перенаправление, 400 ошибки клиента, 500 ошибки сервера

### 2. Виды HTTP-запросов
- _GET_. Цель – получение данных с сервера. URL может содержать параметры.
Тело запроса пустое. Может передавать только пары ключ-значение.
- _POST_. Цель – изменить данные на сервере. Все параметры хранятся в теле запроса.
Тип данных (ключ-значение, JSON, XML, и т.д.). URL не содержит данные.
- _PUT_. Цель – добавить или обновить данные на сервере. Если в данной теме ничего нет, то Put создаст (Insert) новую запись,
но если в ней уже что-то есть, то Put обновит данные. Put-запрос идемпотентен, то есть при последующих операциях количество записей в БД не изменяется
- _DELETE_. Цель – удалить данные

### 3. Идемпотентные методы
Метод HTTP является идемпотентным, если повторный идентичный запрос, сделанный один или несколько раз подряд, имеет один и тот же эффект, _не изменяющий состояние сервера_.
Другими словами, идемпотентный метод _не должен иметь никаких побочных эффектов_ (side-effects), кроме сбора статистики или подобных операций.
Корректно реализованные методы GET, HEAD, PUT и DELETE идемпотентны, но не метод POST.
Также все безопасные методы (GET, HEAD или OPTIONS) являются идемпотентными

### 3. Cookies
### 4. REST
REST - representative state transfer
1) _client-server_. Отделение потребности интерфейса клиента от потребностей сервера, хранящего данные, повышает переносимость кода клиентского интерфейса на другие платформы, а упрощение серверной части улучшает масштабируемость.
2) _stateless_. в период между запросами клиента никакая информация о состоянии клиента на сервере не хранится
3) _cacheability_. Возможеость сервера кешировать ответы (при этом клиент должен знать, какой ответ был отправлен сервером из кеша)
4) _layerd-system_. Клиент не способен определить, взаимодействует он напрямую с сервером или же с промежуточным узлом, в связи с иерархической структурой сетей. Применение промежуточных серверов способно повысить масштабируемость за счёт балансировки нагрузки и распределённого кэширования
5) _Код по требованию_. REST может позволить расширить функциональность клиента за счёт загрузки кода с сервера
6) _Единообразие интерфейсов_. Унифицированные интерфейсы позволяют каждому из сервисов развиваться независимо

### 5. HATEOS


## Микросервисная архитектура
### 1. CAP
В любой реализации распределённых вычислений возможно обеспечить не более двух из трёх следующих свойств:
- согласованность данных (англ. consistency) — во всех вычислительных узлах в один момент времени данные не противоречат друг другу;
- доступность (англ. availability) — любой запрос к распределённой системе завершается корректным откликом, однако без гарантии, что ответы всех узлов системы совпадают;
- устойчивость к разделению (англ. partition tolerance) — расщепление распределённой системы на несколько изолированных секций не приводит к некорректности отклика от каждой из секций.
### 2. Виды масштабирования
- Вертикальное масштабирование – Пример: наращивание мощности компьютера
- Горизонтальное масштабирование – Пример: увеличение количества компьютеров

_Прим.:_ Предпочтительнее - горизонтальное, из-за невозможности бесконечного вертикального наращивания,
а также из-за отказоустойчивости (если один из нескольких компьютеров выйдет из строя, это скажется только на сервисах, запущенных на данном компьютере).
### 3. Паттерны МСА



