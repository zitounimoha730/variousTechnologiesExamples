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