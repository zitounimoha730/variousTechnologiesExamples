# Exporting Data to a File with Kafka Connect
## Introduction
In this hands-on lab, we will implement a basic connector to copy Kafka data to a file on the local disk.

## Additional Resources
Your supermarket company is using Kafka to manage some data. They want to export data from a topic to a data file on the disk for analysis. You have been asked to set up a connector to automatically export records from the inventory_purchases topic to a file located at /home/cloud_user/output/output.txt.

Use the following information as you implement a solution:

The connector class org.apache.kafka.connect.file.FileStreamSinkConnector can be used to export data to a file.
Set the number of tasks to 1.
The data in the topic is string data, so use org.apache.kafka.connect.storage.StringConverter for key.converter and value.converter.
Here is an example of a connector configuration for a FileStream Sink Connector:
```
"connector.class": "org.apache.kafka.connect.file.FileStreamSinkConnector",
"tasks.max": "1",
"file": "<file path>",
"topics": "<topic>",
"key.converter": "<key converter>",
"value.converter": "<value converter>"
```
Once you have set up the connector, publish a new record to the topic for a purchase of plums:
```
kafka-console-producer --broker-list localhost:9092 --topic inventory_purchases
```
plums:5
Check the file to verify that the new record appears:
```
cat /home/cloud_user/output/output.txt
```

## Solution
Begin by logging in to the lab servers using the credentials provided on the hands-on lab page:
```
ssh cloud_user@PUBLIC_IP_ADDRESS
```

### Create a Connector to Export Data from the inventory_purchases Topic to a File
Create a FileStreamSinkConnector:
```
curl -X POST http://localhost:8083/connectors -H "Content-Type: application/json" -d '{
  "name": "file_sink",
  "config": {
    "connector.class": "org.apache.kafka.connect.file.FileStreamSinkConnector",
    "tasks.max": "1",
    "file": "/home/cloud_user/output/output.txt",
    "topics": "inventory_purchases",
    "key.converter": "org.apache.kafka.connect.storage.StringConverter",
    "value.converter": "org.apache.kafka.connect.storage.StringConverter"
  }
}'
```
We should see data from the topic appearing in the output file:
```
cat /home/cloud_user/output/output.txt
```
### Publish a New Purchase of Plums to the inventory_purchases Topic
Start up a console producer:
```
kafka-console-producer --broker-list localhost:9092 --topic inventory_purchases
```
Publish some data representing a purchase of plums:
plums:5
Close the producer with the keyboard shortcut (e.g. Ctrl + C).
Check the file and verify that the purchase of plums shows up in the file data:
```
cat /home/cloud_user/output/output.txt
```
Note: It may take a few moments for the connector to process the new data.



### Playing with kafka commands to discover the cluster
```
# Vérifier que Kafka est UP (brokers)
# Version & brokers visibles
# Si Kafka est UP, on verra la liste des brokers et leurs API supportées.
cloud_user@ip-10-0-1-101:~$ kafka-broker-api-versions --bootstrap-server localhost:9092
zoo1:9092 (id: 1 rack: null) -> (
        Produce(0): 0 to 7 [usable: 7],
        Fetch(1): 0 to 10 [usable: 10],
        ListOffsets(2): 0 to 5 [usable: 5],
        Metadata(3): 0 to 7 [usable: 7],
        LeaderAndIsr(4): 0 to 2 [usable: 2],
        StopReplica(5): 0 to 1 [usable: 1],
        UpdateMetadata(6): 0 to 5 [usable: 5],
        ControlledShutdown(7): 0 to 2 [usable: 2],
        OffsetCommit(8): 0 to 6 [usable: 6],
        OffsetFetch(9): 0 to 5 [usable: 5],
        FindCoordinator(10): 0 to 2 [usable: 2],
        JoinGroup(11): 0 to 4 [usable: 4],
        Heartbeat(12): 0 to 2 [usable: 2],
        LeaveGroup(13): 0 to 2 [usable: 2],
        SyncGroup(14): 0 to 2 [usable: 2],
        DescribeGroups(15): 0 to 2 [usable: 2],
        ListGroups(16): 0 to 2 [usable: 2],
        SaslHandshake(17): 0 to 1 [usable: 1],
        ApiVersions(18): 0 to 2 [usable: 2],
        CreateTopics(19): 0 to 3 [usable: 3],
        DeleteTopics(20): 0 to 3 [usable: 3],
        DeleteRecords(21): 0 to 1 [usable: 1],
        InitProducerId(22): 0 to 1 [usable: 1],
        OffsetForLeaderEpoch(23): 0 to 2 [usable: 2],
        AddPartitionsToTxn(24): 0 to 1 [usable: 1],
        AddOffsetsToTxn(25): 0 to 1 [usable: 1],
        EndTxn(26): 0 to 1 [usable: 1],
        WriteTxnMarkers(27): 0 [usable: 0],
        TxnOffsetCommit(28): 0 to 2 [usable: 2],
        DescribeAcls(29): 0 to 1 [usable: 1],
        CreateAcls(30): 0 to 1 [usable: 1],
        DeleteAcls(31): 0 to 1 [usable: 1],
        DescribeConfigs(32): 0 to 2 [usable: 2],
        AlterConfigs(33): 0 to 1 [usable: 1],
        AlterReplicaLogDirs(34): 0 to 1 [usable: 1],
        DescribeLogDirs(35): 0 to 1 [usable: 1],
        SaslAuthenticate(36): 0 to 1 [usable: 1],
        CreatePartitions(37): 0 to 1 [usable: 1],
        CreateDelegationToken(38): 0 to 1 [usable: 1],
        RenewDelegationToken(39): 0 to 1 [usable: 1],
        ExpireDelegationToken(40): 0 to 1 [usable: 1],
        DescribeDelegationToken(41): 0 to 1 [usable: 1],
        DeleteGroups(42): 0 to 1 [usable: 1],
        ElectPreferredLeaders(43): 0 [usable: 0]
)

# Vérifier les brokers via ZooKeeper (si présent)
cloud_user@ip-10-0-1-101:~$ zookeeper-shell localhost:2181
Connecting to localhost:2181
Welcome to ZooKeeper!
JLine support is enabled

WATCHER::

WatchedEvent state:SyncConnected type:None path:null
[zk: localhost:2181(CONNECTED) 0] ls /brokers/ids

# Lister les topics
cloud_user@ip-10-0-1-101:~$ kafka-topics --bootstrap-server localhost:9092 --list

__confluent.support.metrics
__consumer_offsets
connect-configs
connect-offsets
connect-status
inventory_purchases

# Décrire un topic (partitions, leaders, replicas)
cloud_user@ip-10-0-1-101:~$ kafka-topics \
>   --bootstrap-server localhost:9092 \
>   --describe \
>   --topic inventory_purchases

Topic:inventory_purchases       PartitionCount:1        ReplicationFactor:1     Configs:segment.bytes=1073741824
        Topic: inventory_purchases      Partition: 0    Leader: 1       Replicas: 1     Isr: 1

# Produire et consommer (sanity check)
cloud_user@ip-10-0-1-101:~$kafka-console-producer \
  --broker-list localhost:9092 \
  --topic inventory_purchases
> ...

cloud_user@ip-10-0-1-101:~$ kafka-console-consumer \
>   --bootstrap-server localhost:9092 \
>   --topic inventory_purchases \
>   --from-beginning

apples:10
oranges:5
tangerines:11
limes:2
lemons:6
apples:8
apples:14
oranges:13
grapes:160
starfruit:1
durian:2
apples:2
limes:6
apples:2
grapes:540
lemons:4
apricots:15
pears:9
oranges:4
apples:23
pplums:5

# Vérifier que Kafka Connect est UP
cloud_user@ip-10-0-1-101:~$ curl http://localhost:8083/
{"version":"2.2.1-cp1","commit":"7ff42411baaba1ae","kafka_cluster_id":"AI8Tqab-S8aPofFfXejB6Q"}
cloud_user@ip-10-0-1-101:~$

# Lister les connectors
cloud_user@ip-10-0-1-101:~$ curl http://localhost:8083/connectors
["file_sink"]cloud_user@ip-10-0-1-101:~$

# Voir la config d’un connector
cloud_user@ip-10-0-1-101:~$ curl http://localhost:8083/connectors/file_sink
{"name":"file_sink","config":{"connector.class":"org.apache.kafka.connect.file.FileStreamSinkConnector","file":"/home/cloud_user/output/output.txt","tasks.max":"1","topics":"inventory_purchases","name":"file_sink","value.converter":"org.apache.kafka.connect.storage.StringConverter","key.converter":"org.apache.kafka.connect.storage.StringConverter"},"tasks":[{"connector":"file_sink","task":0}],"type":"sink"}cloud_user@ip-10-0-1-101:~$

# Voir le statut du connector
cloud_user@ip-10-0-1-101:~$ curl http://localhost:8083/connectors/file_sink/status
{"name":"file_sink","connector":{"state":"RUNNING","worker_id":"10.0.1.101:8083"},"tasks":[{"id":0,"state":"RUNNING","worker_id":"10.0.1.101:8083"}],"type":"sink"}

# Vérifier les consumer groups (Connect = un consumer)
cloud_user@ip-10-0-1-101:~$ kafka-consumer-groups \
>   --bootstrap-server localhost:9092 \
>   --list
console-consumer-74003
connect-file_sink

# Décrire ce group
kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --describe \
  --group connect-file_sink
```

### Resume util commands
```
# Brokers
kafka-broker-api-versions --bootstrap-server localhost:9092

# Topics
kafka-topics --bootstrap-server localhost:9092 --list
kafka-topics --bootstrap-server localhost:9092 --describe --topic inventory_purchases

# Connect
curl http://localhost:8083/
curl http://localhost:8083/connectors
curl http://localhost:8083/connectors/file_sink/status

# Consumer groups
kafka-consumer-groups --bootstrap-server localhost:9092 --list

# Ping REST Proxy
curl http://localhost:8082/

# Lister topics via REST Proxy
curl http://localhost:8082/topics
curl http://localhost:8082/brokers
```