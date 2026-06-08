# Песочница к открытому уроку. RabbitMQ и Kafka

Поднимаешь оба брокера одной командой и можешь повторить всё, что было на
вебинаре. Своих приложений писать не надо.

## Что понадобится

Docker и Python 3. Оба обычно уже стоят на маке и линуксе. На винде нужен Docker
Desktop.

## Старт

В папке с этим файлом и docker-compose.yml:

```bash
docker compose up -d
docker compose ps
```

Когда контейнеры в статусе up, открываются адреса:

- RabbitMQ, веб-панель: http://localhost:15672 логин guest пароль guest
- Kafka, веб-панель kafka-ui: http://localhost:8090

Остановить и убрать всё в конце:

```bash
docker compose down
```

## Часть 1. RabbitMQ

Сначала посмотри панель на localhost:15672. Вкладки Queues и Exchanges это твоё
всё.

Очереди, привязку к fanout и отправку можно сделать прямо из панели или
командами:

```bash
docker exec rabbitmq rabbitmqadmin declare queue name=queue-any durable=true
docker exec rabbitmq rabbitmqadmin declare queue name=queue-map durable=true
docker exec rabbitmq rabbitmqadmin declare binding source=amq.fanout destination=queue-any
docker exec rabbitmq rabbitmqadmin declare binding source=amq.fanout destination=queue-map

# одно сообщение в одну очередь
docker exec rabbitmq rabbitmqadmin publish exchange=amq.default routing_key=queue-any payload="hello"

# одно сообщение в fanout, прилетит сразу в обе очереди
docker exec rabbitmq rabbitmqadmin publish exchange=amq.fanout routing_key="" payload="broadcast"
```

Обнови панель и посмотри счётчики сообщений в очередях.

Теперь живые потребители. Установи библиотеку и запусти скрипты:

```bash
pip3 install pika
```

Если pip ругается на системный питон:

```bash
python3 -m venv venv && source venv/bin/activate && pip install pika
```

Отправить 10 сообщений:

```bash
python3 rabbit_producer.py 10
```

Запустить двух потребителей в двух разных окнах терминала:

```bash
python3 rabbit_consumer.py C1
python3 rabbit_consumer.py C2
```

Что посмотреть. Сообщения делятся между C1 и C2 по очереди, это round robin.
Останови C1, и C2 разгребает один. Останови обоих, отправь сообщения, в панели
очередь копит, потребителей ноль. Подними обратно, всё подхватится. Так видно,
что сообщения в очереди не теряются.

## Часть 2. Kafka

Открой kafka-ui на localhost:8090, там видны топики, партиции, группы и offset.

Создай топик с тремя партициями:

```bash
docker compose exec kafka kafka-topics --bootstrap-server localhost:9092 \
  --create --topic topic1 --partitions 3 --replication-factor 1
```

В двух окнах запусти потребителей одной группы:

```bash
docker compose exec kafka kafka-console-consumer --bootstrap-server localhost:9092 \
  --topic topic1 --group group1 --property print.partition=true
```

В отдельном окне продьюсер, каждая строка это сообщение, выход Ctrl C:

```bash
docker compose exec kafka kafka-console-producer --bootstrap-server localhost:9092 --topic topic1
```

Посмотреть, кому какие партиции достались и какой лаг:

```bash
docker compose exec kafka kafka-consumer-groups --bootstrap-server localhost:9092 \
  --describe --group group1
```

Что посмотреть. Партиции делятся между потребителями группы. Запусти третьего
потребителя и снова выполни describe, увидишь перебалансировку. Запусти
потребителя с другой группой group2, и он получит все те же сообщения, потому
что каждая группа читает лог независимо:

```bash
docker compose exec kafka kafka-console-consumer --bootstrap-server localhost:9092 \
  --topic topic1 --group group2 --property print.partition=true
```

Чтобы убедиться, что Kafka ничего не удаляет, останови всех потребителей,
отправь сообщения, потом снова подними потребителя. Он вычитает всё, что
накопилось.

## Если что-то занято

Порты 5672, 15672, 9092, 8090 должны быть свободны. Если заняты, останови старые
контейнеры через docker ps и docker stop, либо поменяй левую цифру в портах в
docker-compose.yml.
