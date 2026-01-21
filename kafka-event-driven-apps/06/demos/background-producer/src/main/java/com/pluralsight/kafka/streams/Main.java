package com.pluralsight.kafka.streams;


import com.pluralsight.kafka.streams.model.Order;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.Producer;
import org.apache.kafka.clients.producer.ProducerRecord;

import java.util.Properties;

import static java.lang.Thread.sleep;

public class Main {

    public static void main(String[] args) throws InterruptedException {

        Properties props = new Properties();
        props.put("bootstrap.servers", "127.0.0.1:9093");
        props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
        props.put("value.serializer", "io.confluent.kafka.serializers.KafkaAvroSerializer");
        props.put("schema.registry.url", "http://localhost:8081");

        Producer<String, Order> producer = new KafkaProducer<>(props);


        String key;
        Order value;
        ProducerRecord<String, Order> producerRecord;

        for(int i = 1; i <= 5; i++) {
            key = String.valueOf(i);
            value = Order.newBuilder()
                    .setUserId("1234")
                    .setNbOfItems(1001 * i)
                    .setTotalAmount(100 * i)
                    .build();

            producerRecord = new ProducerRecord<>("payments", key, value);

            producer.send(producerRecord);

            sleep(1000);
        }

        producer.close();
    }
}
