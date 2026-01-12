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

## Demo: module4/demo1
```
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