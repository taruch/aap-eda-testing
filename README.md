# rheda-testing

Documentation on Source Plugins here:
https://ansible.readthedocs.io/projects/rulebook/en/stable/rulebooks.html
https://github.com/ansible/event-driven-ansible/tree/main/extensions/eda/plugins/event_source
https://github.com/ansible/event-driven-ansible/tree/main/extensions/eda/rulebooks (a couple of examples here)

EDA source types examples in this repo:
- alertmanager
- url check
- kafka
- webhook
- aws cloudtrail
- aws sqs
- ibm instana


Url_Check (rulebooks/url_check-example.yml):
An ansible-rulebook event source plugin that polls a set of URLs and sends
events with their status.

Arguments:
---------
    urls - a list of urls to poll
    delay - the number of seconds to wait between polling
    verify_ssl - verify SSL certificate

Example:
-------
    - name: check web server
      ansible.eda.url_check:
        urls:
          - http://44.201.5.56:8000/docs
        delay: 10

Setup:
This is a very easy example with no additional setup required.  This is an outbound request so no firewall ports are required.  Give it a/multiple urls to check and it will go check them at the delay specified.



Webhook (rulebooks/webhook-example.yml)
An ansible-rulebook event source module for receiving events via a webhook.
The message must be a valid JSON object.

Arguments:
---------
    host:     The hostname to listen to. Set to 0.0.0.0 to listen on all
              interfaces. Defaults to 127.0.0.1
    port:     The TCP port to listen to.  Defaults to 5000
    token:    The optional authentication token expected from client
    certfile: The optional path to a certificate file to enable TLS support
    keyfile:  The optional path to a key file to be used together with certfile
    password: The optional password to be used when loading the certificate chain

Setup:
This rulebook adds a service on port 5000 on the EDA Controller, so you need to first run the webhook-deps.yml to set up firewall on the EDA host. 
  ansible-playbook webhook-deps.yml

You can then use curl to post a message to the EDA controller.\
curl -H 'Content-Type: application/json' -d '{"message":"fastapi"}' edacontroller.local:8000/endpoint



Alertmanager (rulebooks/alertmanager-example.yml):
An ansible-rulebook event source module for receiving events via a webhook from
alertmanager or alike system.

Arguments:
---------
    host: The webserver hostname to listen to. Set to 0.0.0.0 to listen on all
          interfaces. Defaults to 127.0.0.1
    port: The TCP port to listen to.  Defaults to 5000
    data_alerts_path: The json path to find alert data. Default to "alerts"
                      Use empty string "" to treat the whole payload data as
                      one alert.
    data_host_path: The json path inside the alert data to find alerting host.
                    Use empty string "" if there is no need to find host.
                    Default to  "labels.instance".
    data_path_separator: The separator to interpret data_host_path and
                         data_alerts_path. Default to "."
    skip_original_data: true/false. Default to false
                        true: put only alert data to the queue
                        false: put sequentially both the received original
                               data and each parsed alert item to the queue.

Example:
-------
    - ansible.eda.alertmanager:
        host: 0.0.0.0
        port: 8000
        data_alerts_path: alerts
        data_host_path: labels.instance
        data_path_separator: .


Setup:
This is a bit more complicated source plugin with more options/arguments but gives you more control over the incoming structured data.  The rulebook adds a service on port 8000 on the EDA Controller, so you need to first run the alertmanager-deps.yml to set up firewall on the EDA host. 
  ansible-playbook alertmanager-deps.yml

You can then use curl to post a message to the EDA controller.\
curl -H 'Content-Type: application/json' -d '{"message":"fastapi"}' edacontroller.local:8000/endpoint



Kafka (rulebooks/kafka-example.yml):
Requires a Kafka host, for which I used AMQ Streams 2.4.
- Download: https://access.redhat.com/jbossnetwork/restricted/softwareDetail.html?softwareId=105393&product=jboss.amq.streams&version=2.4.0&downloadType=distributions
- Documentation: https://access.redhat.com/documentation/en-us/red_hat_amq_streams/2.4

Configure Kakfa (here is what I did - I haven't ansiblized it yet):
yum update -y
yum install -y java-11-openjdk.x86_64 java-11-openjdk-devel
pip3 install kafka-python
sudo groupadd kafka
sudo useradd -g kafka kafka
sudo passwd kafka
mv /home/truch/kafka_2.13-3.4.0.redhat-00006 /opt/kafka
sudo mkdir /var/lib/zookeeper
sudo mkdir /var/lib/kafka
sudo chown -R kafka:kafka /opt/kafka
sudo chown -R kafka:kafka /var/lib/kafka
sudo chown -R kafka:kafka /var/lib/zookeeper
cat /opt/kafka/config/zookeeper.properties
firewall-cmd --add-port=9092/tcp --permanent

su - kafka
/opt/kafka/bin/zookeeper-server-start.sh -daemon /opt/kafka/config/zookeeper.properties

New Terminal:
/opt/kafka/bin/kafka-console-consumer.sh --broker-list amqstreams.local:9092 --topic eda-topic

New Terminal:
/opt/kafka/bin/kafka-console-producer.sh --broker-list amqstreams.local:9092 --topic eda-topic

In the producer terminal, you can now write out messages that will show up in the consumer terminal; they can also be picked
up by the EDA Controller if you are running the kafka-example.yml rulebook.

