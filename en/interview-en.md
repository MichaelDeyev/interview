# JAVA CORE
### What is an interface?
Interface - a contract between classes that must be implemented in classes

### What is the difference between an interface and an abstract class?
1. An interface describes only behavior. He has no state. An abstract class has a state: it describes both. In an abstract class, you can create variables and setters/getters for them, but not in an interface.
2. An abstract class connects classes that are very closely related.
At the same time, the same interface can be implemented by classes that have nothing in common except behavior.
3. Java forbids multiple inheritance of classes, but allows multiple implementation of interfaces

### How can we convert `String array[]` to `ArrayList<String>` ?
We can call static method of Arrays class `asList()` that will return list of strings

# Data Base
### How can you explain the term ‘relational’ speaking about relational databases?
Relational databases are data structures in which rows relate to columns. Rows store data and columns store data-properties  
### What is the difference between partitioning and sharding?
- Partition is Dividing the table into parts according to some data (by rows). For example, by the date the entry was created. 
One partition can be deleted without harming other partitions.
- Sharding is dividing a table by columns (Some columns in one table, some in another).

# SPRING
### 1. What Spring is?
Spring Framework is framework which implement several concepts:
1. Dependency injection
2. Inversion of Control
3. give us convenient interfaces for web-developing.

# Patterns
### What objects in the MVC pattern could be used as a View in a classic REST API application?
We use `Data Transfer Object` as a View in REST API

# Common
### What is a serialisation/deserialisation?
- Searialization is a process of saving object's state to DataBase, file or another type of interface
- Deserialisation is reverse Searialization process

### What would you do to understand if your code has a bad design?
When I spend too much time on support and making changes in my code
### Tell me the 3 worst defects in/of your preferred language? 
- Verbosity
- Unintuitive API for working with asynchronous interaction
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
