# Kafka course
## Publish and consume some messages
```
# Publish some messages
$ kafka-console-producer.bat --bootstrap-server 127.0.0.1:9092 --topic first_topic
> Hello
> From
> Me!

# Receiving messages
$ kafka-console-consumer.bat --bootstrap-server 127.0.0.1:9092 --topic first_topic --from-beginning
Hello
From
Me!
```

## Create a topic with some partitions

```
$ kafka-topics.bat --create --bootstrap-server 127.0.0.1:9092 --replication-factor 1 --partitions 3 --topic myorders

```

## Reassign partitions

```
kafka-reassign-partitions.bat --bootstrap-server 127.0.0.1:9092 --reassignment-json-file increase_replication.json --execute

```

We can now drop a broker and see what's happining:
```
$ docker stop broker-3
```

## Kafka Groups and use of message key:value
```
$ cd demos/module4/demo1
$ docker-compose up -d
$ kafka-topics.bat --create --bootstrap-server 127.0.0.1:9092 --replication-factor 3 --partitions 3 --topic myorders

$ kafka-console-consumer.bat --bootstrap-server 127.0.0.1:9092 --topic myorders --group 1
hello
from
zitouni

$ kafka-console-consumer.bat --bootstrap-server 127.0.0.1:9092 --topic myorders --group 1
hi
from
mohamed

$ kafka-console-producer.bat --bootstrap-server 127.0.0.1:9092 --topic myorders --property="parse.key=true" --property "key.separator=:"
>>zit:hello
>>zit:from
>>zit:zitouni
>>med:hi
>>med:from
>>med:mohamed

$ kafka-consumer-groups.bat --bootstrap-server 127.0.0.1:9092 --all-groups --all-topics --describe

GROUP    TOPIC           PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG  CONSUMER-ID    HOST    CLIENT-ID        
1        myorders        1          3               3               0     <id1>      /172.19.0.1     console-consumer 
1        myorders        0          0               0               0     <id1>      /172.19.0.1     console-consumer 
1        myorders        2          3               3               0     <id2>      /172.19.0.1     console-consumer

```

## Kafka Java client example
```
$ cd modules/module4/demo2
$ kafka-topics.bat --create --bootstrap-server 127.0.0.1:9092 --replication-factor 3 --partitions 3 --topic myorders

$ kafka-console-consumer.bat `
    --bootstrap-server 127.0.0.1:9092 `
    --topic myorders `
    --from-beginning `
    --key-deserializer org.apache.kafka.common.serialization.StringDeserializer `
    --value-deserializer org.apache.kafka.common.serialization.DoubleDeserializer `
    --property print.key=true `
    --property key-separator=, `
    --group 1

TX      1532.0
CA      2634.0
HI      5373.0
WY      6877.0
OK      1935.0
CA      4348.0
...

$ mvn clean install
$ java -jar ./kafka-client-1.0-SNAPSHOT.jar
...
NH
2313.0
myorders-1@72
[main] INFO com.globomantics.Main - Sending message with key TN to Kafka
TN
9862.0
myorders-1@73
[main] INFO com.globomantics.Main - Sending message with key TN to Kafka
...
```

## Kafka Groups
### Module 5 : demo 1
Kafka cluster:
* 3 brokers 
* 3 zookeepers

Topic: myorders
- 2 partitions
- 2 replications

```
$ cd demos/module5/demo1
$ docker-compose up -d
$ kafka-topics.bat --create --bootstrap-server 127.0.0.1:9092 --replication-factor 2 --partitions 2 --topic myorders
```

Run consumers

```
$ kafka-console-consumer.bat `
    --bootstrap-server 127.0.0.1:9092 `
    --topic myorders `
    --from-beginning `
    --key-deserializer org.apache.kafka.common.serialization.StringDeserializer `
    --value-deserializer org.apache.kafka.common.serialization.DoubleDeserializer `
    --property print.key=true `
    --property key-separator=, `
    --group 1

$ kafka-console-consumer.bat `
    --bootstrap-server 127.0.0.1:9092 `
    --topic myorders `
    --from-beginning `
    --key-deserializer org.apache.kafka.common.serialization.StringDeserializer `
    --value-deserializer org.apache.kafka.common.serialization.DoubleDeserializer `
    --property print.key=true `
    --property key-separator=, `
    --group 1

$ kafka-console-consumer.bat `
    --bootstrap-server 127.0.0.1:9092 `
    --topic myorders `
    --from-beginning `
    --key-deserializer org.apache.kafka.common.serialization.StringDeserializer `
    --value-deserializer org.apache.kafka.common.serialization.DoubleDeserializer `
    --property print.key=true `
    --property key-separator=, `
    --group 2

$ kafka-console-consumer.bat `
    --bootstrap-server 127.0.0.1:9092 `
    --topic myorders `
    --from-beginning `
    --key-deserializer org.apache.kafka.common.serialization.StringDeserializer `
    --value-deserializer org.apache.kafka.common.serialization.DoubleDeserializer `
    --property print.key=true `
    --property key-separator=, `
    --group 1

$ docker logs broker-1 | Select-String "Coordinator"
```

Run Java producer
```
$ mvn clean install
$ run maven project to send messages from producer
```

Describe kafka cluster

```
kafka-consumer-groups.bat --bootstrap-server 127.0.0.1:9092 --all-groups --all-topics --describe
2026-01-13T13:23:56.441692700Z main ERROR Reconfiguration failed: No configuration found for '764c12b6' at 'null' in 'null'

GROUP           TOPIC           PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG             CONSUMER-ID                                           HOST            CLIENT-ID
1               myorders        1          9               10              1               consumer-id1 /172.19.0.1     console-consumer
1               myorders        0          12              12              0               consumer-id2 /172.19.0.1     console-consumer

GROUP           TOPIC           PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG             CONSUMER-ID                                           HOST            CLIENT-ID
2               myorders        1          9               10              1               consumer-id3 /172.19.0.1     console-consumer
2               myorders        0          12              12              0               consumer-id3 /172.19.0.1     console-consumer

```
* We have a topic with 2 partitions
* We added 2 groups (1 and 2)
* For group 1, we added 3 consumers => one of them became idle (not receiving any message) because relationship between partitions and consumer groups is many to one. Each other consumer is receiving messages only from one partition.
* For group 2, we added only one consumer => it is receiving all messages from both partitions.

## Rebalance
### Module 5 : demo 2
Kafka cluster:
* 3 brokers 
* 3 zookeepers

Topic: myorders
- 4 partitions
- 2 replications

```
$ cd demos/module5/demo2
$ docker-compose up -d
$ kafka-topics.bat --create --bootstrap-server 127.0.0.1:9092 --replication-factor 2 --partitions 4 --topic myorders
```

Run Java consumers:
```
$ cd demos/module5/demo2
# $ mvn clean install exec:java -Dexec.mainClass="com.globomantics.Consumer" -Dexec.args="1" => won't work
# Run Comsumer.main from intelliJ passing "1" as java argument => Consumer1.1
# Run Comsumer.main from intelliJ passing "1" as java argument => Consumer1.2
```

Run Java producer
```
# Run Producer.main from intelliJ => Producer
```

Describe kafka cluster

```
$ kafka-consumer-groups.bat --bootstrap-server 127.0.0.1:9092 --all-groups --all-topics --describe

GROUP           TOPIC           PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG             CONSUMER-ID          HOST            CLIENT-ID
1consumer       myorders        2          20              20              0               consumer-id1 /172.19.0.1     consumer-1consumer-1
1consumer       myorders        3          15              15              0               consumer-id2 /172.19.0.1     consumer-1consumer-1
1consumer       myorders        1          28              28              0               consumer-id2 /172.19.0.1     consumer-1consumer-1
1consumer       myorders        0          20              20              0               consumer-id2 /172.19.0.1     consumer-1consumer-1
```

Add consumer1.3
```
# Run Comsumer.main from intelliJ passing "1" as java argument => Consumer1.3

kafka-consumer-groups.bat --bootstrap-server 127.0.0.1:9092 --all-groups --all-topics --describe
2026-01-13T15:26:04.661136200Z main ERROR Reconfiguration failed: No configuration found for '764c12b6' at 'null' in 'null'

GROUP           TOPIC           PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG             CONSUMER-ID        HOST            CLIENT-ID
1consumer       myorders        1          57              57              0               consumer-id1 /172.19.0.1     consumer-1consumer-1
1consumer       myorders        0          46              46              0               consumer-id1 /172.19.0.1     consumer-1consumer-1
1consumer       myorders        3          35              35              0               consumer-id2 /172.19.0.1     consumer-1consumer-1
1consumer       myorders        2          36              36              0               consumer-id3 /172.19.0.1     consumer-1consumer-1
```

## Standalone Kafka Connector
### Module 6 : demo 1
Kafka cluster:
* 3 brokers 
* 3 zookeepers

Topic: connectlog
- 4 partitions
- 2 replications
```
$ cd demos/module6/demo1
$ docker-compose up -d
$ curl 'http://localhost:8082/brokers'
{"brokers": [1,2,3]}

$ kafka-topics.bat --create --bootstrap-server 127.0.0.1:9092 --replication-factor 2 --partitions 4 --topic connectlog

```

Start the standalone connector
```
$ connect-standalone.bat worker.properties filesink.properties
```

Start the java client producer
```
# Run the java class LogProducer from IntelliJ IDE
```

Check generated log file: file-log.txt
```
cat file-log.txt
Some logging info from Kafka with key45.0
Some logging info from Kafka with key48.0
Some logging info from Kafka with key28.0
Some logging info from Kafka with key47.0
Some logging info from Kafka with key28.0
....
```
