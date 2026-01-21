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
### Module 4 : demo 1
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
### Module 4 : demo 2
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

## Kafka distributed connector
### Module 6 : demo 2

```
$ cd demos/module6/demo2
$ docker-compose up -d
```

### First solution: Install directly a kafka connect on your machine
This is not working on windows => abandonate

### Second Solution: Using docker-compose service for kafka connect
#### 1. Add Kafka connect service to docker-compose.yml file

#### 2. Install needed libs into kafka connect container
```
$ docker exec -it kafka-connect confluent-hub install confluentinc/kafka-connect-avro-converter:7.5.0
$ docker exec -it kafka-connect confluent-hub install mongodb/kafka-connect-mongodb:1.11.0 
# $ docker exec -it kafka-connect confluent-hub install mongodb/kafka-connect-mongodb:latest

# Restart kafka-connect service
$ docker-compose restart kafka-connect

# Check installed libs
$ curl http://localhost:8083/connector-plugins
[
  {
    "class": "com.mongodb.kafka.connect.MongoSinkConnector",
    "type": "sink",
    "version": "1.11.0"
  },
  {
    "class": "com.mongodb.kafka.connect.MongoSourceConnector",
    "type": "source",
    "version": "1.11.0"
  },
  {
    "class": "org.apache.kafka.connect.mirror.MirrorCheckpointConnector",
    "type": "source",
    "version": "7.4.1-ccs"
  },
  {
    "class": "org.apache.kafka.connect.mirror.MirrorHeartbeatConnector",
    "type": "source",
    "version": "7.4.1-ccs"
  },
  {
    "class": "org.apache.kafka.connect.mirror.MirrorSourceConnector",
    "type": "source",
    "version": "7.4.1-ccs"
  }
]

```

#### 3. Create topic: connect-distributed
```
$ kafka-topics.bat --create --bootstrap-server 127.0.0.1:9092 --replication-factor 2 --partitions 4 --topic connect-distributed
```

#### 4. Create a connector for mango db
It will be better to use Postman
```
curl -X POST http://localhost:8083/connectors -H "Content-Type: application/json" -d '{
    "name": "mongo-sink",
    "config": {
      "connector.class": "com.mongodb.kafka.connect.MongoSinkConnector",
      "tasks.max": "1",
      "topics": "connect-distributed",
      "connection.uri": "mongodb://mongo:27017",
      "database": "quickstart",
      "collection": "topicData"
    }
  }'

# If it does not worked use this:
curl -X POST http://localhost:8083/connectors -H "Content-Type: application/json" -d '{
    "name": "mongo-sink",
    "config": {
      "connector.class": "com.mongodb.kafka.connect.MongoSinkConnector",
      "tasks.max": "1",
      "topics": "connect-distributed",
      "connection.uri": "mongodb://mongo:27017",
      "database": "quickstart",
      "collection": "topicData",
      "key.converter": "org.apache.kafka.connect.storage.StringConverter",
      "value.converter": "io.confluent.connect.avro.AvroConverter",
      "value.converter.schemas.enable": "false",
	  "value.converter.schema.registry.url": "http://schema-registry:8081"
    }
  }'

# Display created connector
$ curl http://localhost:8083/connectors
['mongo-sink']

# We can delete it by name if we want
$ curl -X DELETE http://localhost:8083/connectors/mongo-sink

# check connector status
$ curl http://localhost:8083/connectors/mongo-sink/status
```

#### 5. Run Java Kafka Producer

```
# Open project with IntelliJ
# Generate resources
$ mvn generate-sources

# Run class AlbumSender.java
```

#### 6. Connect to mongo to check exported data
```
$ docker exec -it mongo mongosh

test> show dbs
admin       40.00 KiB
config      92.00 KiB
local       40.00 KiB
quickstart   8.00 KiB

test> use quickstart
switched to db quickstart
quickstart> db.topicData.find()
[
  {
    _id: ObjectId('696a33d88bc3952fc2520a90'),
    name: 'Use Your Illusion',
    year: 1991
  },
  {
    _id: ObjectId('696a33d88bc3952fc2520a91'),
    name: 'Use Your Illusion',
    year: 1991
  },
  {
    _id: ObjectId('696a33d88bc3952fc2520a92'),
    name: 'Use Your Illusion',
    year: 1991
  },
  {
    _id: ObjectId('696a33d88bc3952fc2520a93'),
    name: 'Use Your Illusion',
    year: 1991
  },
  {
    _id: ObjectId('696a33e68bc3952fc2520a94'),
    name: 'Use Your Illusion',
    year: 1991
  }
]
```

## Kafka Streams
### Creating a Kafka Streams Application - Module 7 : demo 1
#### 1. create kafka cluster
```
$ cd demos/module7/demo1
$ docker-compose up -d
```

#### 2. create topics
```
$ kafka-topics.bat --create --bootstrap-server 127.0.0.1:9092 --partitions 4 --topic RawTempReadings
$ kafka-topics.bat --create --bootstrap-server 127.0.0.1:9092 --partitions 4 --topic ValidatedTempReadings
```

#### 3. Create console consumer
```
$ kafka-console-consumer.bat `
    --bootstrap-server 127.0.0.1:9092 `
    --topic ValidatedTempReadings `
    --from-beginning `
    --key-deserializer org.apache.kafka.common.serialization.StringDeserializer `
    --value-deserializer org.apache.kafka.common.serialization.IntegerDeserializer `
    --property print.key=true `
    --property key-separator=, `
    --group 1

```

#### 4. Start App Stream & Producer
```
# Open project using IntellIj
# Start The Stream class: SimpleETL
# Start The producer class: Producer
```

Result: we are filtering tempiratures between -20 and 130 degree
```
# Our consumer on ValidatedTempReadings topic stats to receive these messages:
sensor_3        125
sensor_1        108
sensor_2        126
sensor_3        103
sensor_1        104
sensor_1        33
sensor_1        79
sensor_2        -19
sensor_1        -11
sensor_1        57
.....
```

### Quering a Stream with ksql part1 - Module 7 : demo 2
#### 1. create kafka cluster
```
$ cd demos/module7/demo2
$ docker-compose up -d
```

#### 2. connect to ksqldb command line interface
```
$ docker exec -it ksqldb-cli ksql http://ksqldb-server:8088

ksql> show all topics;

 Kafka Topic                            | Partitions | Partition Replicas
----------------------------------------------------------
 _confluent-ksql-default__command_topic | 1          | 1
 _schemas                               | 1          | 3
 default_ksql_processing_log            | 1          | 1
----------------------------------------------------------

```

#### 3. Configure ksql reading offset
We are going to see all of the changes of all topics from the biginning.
```
ksql> SET 'auto.offset.reset'='earliest';
Successfully changed local property 'auto.offset.reset' to 'earliest'. Use the UNSET command to revert your change.
```

#### 4. Create a stream
```
ksql> CREATE STREAM tempReadings (zipcode VARCHAR, sensortime BIGINT, temp DOUBLE) WITH (kafka_topic='readings', timestamp='sensortime', value_format='json', partitions=1);
 Message
----------------
 Stream created
----------------

ksql> show topics extended;

 Kafka Topic                 | Partitions | Partition Replicas | Consumers | ConsumerGroups
--------------------
 default_ksql_processing_log | 1          | 1                  | 0         | 0
 readings                    | 1          | 1                  | 0         | 0
--------------------

ksql> show streams extended;
Name                 : TEMPREADINGS
Type                 : STREAM
Timestamp field      : SENSORTIME
Key format           : KAFKA
Value format         : JSON
Kafka topic          : readings (partitions: 1, replication: 1)
...
 Field      | Type
------------------------------                                                                      &
 ZIPCODE    | VARCHAR(STRING)
 SENSORTIME | BIGINT
 TEMP       | DOUBLE
------------------------------
...
```

#### 5. insert data to the Stream
```
ksql> INSERT INTO tempReadings (zipcode, sensortime, temp) VALUES ('1234', UNIX_TIMESTAMP(), 100);
ksql> INSERT INTO tempReadings (zipcode, sensortime, temp) VALUES ('4321', UNIX_TIMESTAMP(), 90);
ksql> INSERT INTO tempReadings (zipcode, sensortime, temp) VALUES ('4321', UNIX_TIMESTAMP() + 60 * 60 * 1000, 80);
ksql> INSERT INTO tempReadings (zipcode, sensortime, temp) VALUES ('4321', UNIX_TIMESTAMP() + 30 * 60 * 1000, 80);
ksql> INSERT INTO tempReadings (zipcode, sensortime, temp) VALUES ('4321', UNIX_TIMESTAMP() + 2 * 60 * 60 * 1000, 70);
```

#### 6. Use ksql to query the Stream
```
ksql> SELECT zipcode, TIMESTAMPTOSTRING(WINDOWSTART, 'HH:mm:ss') as windowtime, 
COUNT(*) AS rowcount, AVG(temp) as tempAvg 
FROM tempReadings
WINDOW TUMBLING (SIZE 1 HOURS)
GROUP BY zipcode EMIT CHANGES;

+-----------------------------+-----------------------------+-----------------------------+-----------------------------+
|ZIPCODE                              |WINDOWTIME                           |ROWCOUNT                         |TEMPAVG
+-----------------------------+-----------------------------+-----------------------------+-----------------------------+
|1234                                 |17:00:00                             |1                                |100.0
|4321                                 |18:00:00                             |1                                |80.0 
|4321                                 |19:00:00                             |1                                |70.0   
|4321                                 |17:00:00                             |2                                |85.0 

```

#### 7. Consuming directly from topic used by the Stream
```
$ kafka-console-consumer.bat --bootstrap-server 127.0.0.1:9092 --topic readings --from-beginning
{"ZIPCODE":"1234","SENSORTIME":1768635270096,"TEMP":100.0}
{"ZIPCODE":"4321","SENSORTIME":1768635277748,"TEMP":90.0}
{"ZIPCODE":"4321","SENSORTIME":1768638891431,"TEMP":80.0}
{"ZIPCODE":"4321","SENSORTIME":1768637105743,"TEMP":80.0}
{"ZIPCODE":"4321","SENSORTIME":1768642514844,"TEMP":70.0}
```

#### 8. Creating a table from the Stream
Tables don't alive. They are just queries (like views in sql).
```
ksql> CREATE TABLE highsandlows WITH (kafka_topic='readings') AS 
SELECT MIN(temp) as min_temp, MAX(temp) as max_temp, zipcode
FROM tempReadings GROUP BY zipcode;

 Message
-------------------------------------------
 Created query with ID CTAS_HIGHSANDLOWS_3
-------------------------------------------

ksql> SELECT min_temp, max_temp
>FROM highsandlows WHERE zipcode='4321';
+--------------------+--------------------+
|MIN_TEMP             |MAX_TEMP            
+--------------------+--------------------+
|70.0                 |90.0             

```

## Kafka Administration
### Generate certifications for components in the cluster : module8/demo1
* First we need a CA (Certification authority)
* Zookeeper: 
  - keyStore: it is a server for krokers
  - trustStore: it is client for other zookepers
* Broker:
  - keyStore: it is server for producers
  - trustStore: it is client for zookeper and other brokers
* producer:
  - trustStore: it is client for brokers
  - keyStore: no need
* consumer:
  - trustStore: it is client for brokers
  - keyStore: no need

```
$ cd demos/module8/demo1
$ cd security
$ ./generate-ca.sh

# Generate keystore for 3 brokers
$ ./generate-keystore.sh broker-1
$ ./generate-keystore.sh broker-2
$ ./generate-keystore.sh broker-3

# Generate keystore for 3 Zookepers
$ ./generate-keystore.sh zookeper-1
$ ./generate-keystore.sh zookeper-2
$ ./generate-keystore.sh zookeper-3

# Generate Truststore for 3 brockers
$ ./generate-truststore.sh broker-1
$ ./generate-truststore.sh broker-2
$ ./generate-truststore.sh broker-3

# Generate Truststore for 3 zookepers
$ ./generate-truststore.sh zookeper-1
$ ./generate-truststore.sh zookeper-2
$ ./generate-truststore.sh zookeper-3
```

### Encrypting Zookeper (Offline): module8/demo2
Can be done in two ways:
- Online Fashion
- Offline Fashion
#### 1. Use keystore & truststore files to secure zookeepers & brokers
See demos/module8/demo2/docker-compose.yml file
#### 2. Start Kafka cluster
```
$ cd demos/module8/demo2
$ docker-compose.yml
$ curl localhost:8082
{brokers:[1,2,3]}
```
#### 3. Create a topic
```
$ kafka-topics.bat --create --bootstrap-server 127.0.0.1:9092 --partitions 4 --topic myorders
```

#### 4. Produce and receive messages
```
# Open project using IntelliJ IDE
# Run Consumer.java file => success receiving from myorders topic
# Run Producer.java file => Success sending messages to myorders topic
```
=> Data are encrypted between :
- zookepers - zookepers
- brokers - brokers
- zookepers - brokers

But not yet encrypted with producers or consumers and the communication until now between producers/consumers and brokers is in plaintext. In next demo we will make it communication in ssl => we change the protocol from PLAINTEXT to SSL

### Encrypt Producers and Consumers : module8/demo3
#### 1. Generate truststore files for a producer and a consumer
```
$ ./generate-truststore.sh producer
$ ./generate-truststore.sh consumer
```

#### 2. Run Java Producer and Consumer
- Open the project with IntelliJ
- Fix the path and password of jks files
- Run java classes