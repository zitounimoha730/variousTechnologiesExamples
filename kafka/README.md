# Kafka course
## Publish and consume some messages
```
# Publish some messages
$ kafka-console-producer.bat --bootstrap-server 127.0.0.1:8082 --topic first_topic
> Hello
> From
> Me!

# Receiving messages
$ kafka-console-consumer.bat --bootstrap-server 127.0.0.1:8082 --topic first_topic --from-beginning
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