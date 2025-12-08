# Kafka course
## Sample commands
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