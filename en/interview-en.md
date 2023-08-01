# Opening questions
### Introduce yourself
My name is Mike, and I am a Java developer. I started learning Java at university and have been working as a Java developer for over two years. I started working for a large retail company written on the SAP E-commerce platform, but I have been working in fintech for a year and a half. I managed to work on the "Security" and "Savings and Deposits" projects of the largest bank.
My main PL is Java, and I'm really Love it. I am also familiar with SpringBoot framework and with Hibernate ORM.
I always try to improve my skills and learning new technologies. For example, now I'm learning frontend to addition for main skills


# JAVA CORE
### What is an interface?
Interface - a contract between classes that must be implemented in classes

### What is the difference between an interface and an abstract class? Г. сказал что можно создать экземпляр абстрактного класса  
1. An interface describes only behavior. He has no state. An abstract class has a state: it describes both. In an abstract class, you can create variables and setters/getters for them, but not in an interface.
2. An abstract class connects classes that are very closely related.
At the same time, the same interface can be implemented by classes that have nothing in common except behavior.
3. Java forbids multiple inheritance of classes, but allows multiple implementation of interfaces

### What Collections do you know? 

### Say a few words about the Map? мапа не является коллекцией, мапа не выдаст исключение если туда положить существующий ключ

### Do you know about Garbage collection functional in Java? знает назначение но не знает реализаицию

### How can we convert `String array[]` to `ArrayList<String>` ?
We can call static method of Arrays class `asList()` that will return list of strings

# Data Base
### How can you explain the term ‘relational’ speaking about relational databases?
Relational databases are data structures in which rows relate to columns. Rows store data and columns store data-properties  
### What is the difference between partitioning and sharding?
- Partition is Dividing the table into parts according to some data (by rows). For example, by the date the entry was created. 
One partition can be deleted without harming other partitions.
- Sharding is dividing a table by columns (Some columns in one table, some in another).
- 
### ACID abbreviation
- _**Atomicity**_. Atomicity guarantees that each transaction will either complete completely or not at all. Intermediate states are not allowed.

- _**Consistency**_. As a result of the operation of the transaction, the data will be valid. This is not a question of technology, but of business logic: for example, if the amount of money in the account cannot be negative, the transaction logic should check if the result is negative values.

- _**Isolation**_. Guarantee that concurrent transactions will not affect the outcome of other transactions.

- _**Durability**_. Changes resulting from a transaction must remain persistent regardless of any failures. In other words, if the user received a signal about the completion of the transaction, he can be sure that the data has been saved.

# SPRING
### 1. What Spring is?
Spring Framework is framework which implement several concepts:
### How it helps us?
1. Dependency injection
2. Inversion of Control
3. give us convenient interfaces for web-developing.
### Which Spring annotations do you know?
### Maybe you know the difference between the @Component and the @Bean annotations? Не знает про @Components 

# Patterns. can you name me three patterns do you used more often?
### What objects in the MVC pattern could be used as a View in a classic REST API application?
We use `Data Transfer Object` as a View in REST API

### What is the difference between Monolithic, SOA and Microservices Architecture?
- _**Monolithic architecture**_ is a pattern that is implemented by writing the entire system in one application. As an advantage, one can note the ease of development in the initial stages of writing an application, as well as the ease of deployment to the environment. Disadvantages appear only when the application begins to grow: difficult scaling and the introduction of new functionality
- _**Service Oriented Architecture**_ is a pattern that describes the interaction between services through a SOA bus. The whole system is divided into services that communicate with each other through a common data-bus.
- _**Microservices Architecture**_ is an architectural pattern that is implemented by dividing the entire system into many small components (services). Each service is responsible only for its area and operates independently of other services providing the principle of loose coupling. The advantages are easy scaling, the ability to easily add new functionality at any stage of development, as well as fault tolerance. The disadvantage is the difficulty in deploying and in controlling the entire system.

### Which type of connectivity have you used in microservices? How Microservices can communicate with each other
# Common Computer Science
### What is a serialisation/deserialisation?
- Searialization is a process of saving object's state to DataBase, file or another type of interface
- Deserialisation is reverse Searialization process

# Network
### What are the methods of REST?
There are many REST-methods, but commonly we used several methods
- _GET_. The goal is to get data from the server. The URL can contain parameters. The request body is empty. Can only pass key-value pairs.
- _POST_. The goal is to change the data on the server. All parameters are stored in the request body. Data type (key-value, JSON, XML, etc.). The URL contains no data.
- _PUT_. The goal is to add or update data on the server. If there is nothing in this topic, then Put will create (Insert) a new entry, but if there is already something in it, then Put will update the data. 
The put request is idempotent, that is, the number of records in the database won't be incremented during subsequent operations.
- _DELETE_. The goal is to delete data

# DevOps

### How can you implement horizontal scaling in kubernetes?
We can increment the number of ReplicaSet in deployment.yaml file

# Closing questions:
### What do you find most satisfying about this type of work?
### What's your greatest strength as a developer?
### What are your favorite languages for writing code? What are the pros and cons of each language?

### What would you do to understand if your code has a bad design?
When I spend too much time on support and making changes in my code
### Tell me the 3 worst defects in/of your preferred language?
- Verbosity
- Unintuitive API for working with asynchronous interaction