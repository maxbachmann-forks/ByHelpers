# -*- coding: utf-8 -*-
import logging
import pika
import os
import json
import sys
import uuid

APP_NAME = os.getenv('APP_NAME', '__name__')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')

LOGGER = logging.getLogger(APP_NAME)
LOGGER.setLevel(LOG_LEVEL)

pika_logger = logging.getLogger('pika')
pika_logger.setLevel("ERROR")

STREAMER_ROUTING_KEY = os.getenv('STREAMER_ROUTING_KEY', 'routing')
SMONITOR_KEY = os.getenv('SMONITOR','smonitor')

if os.getenv('ENV', 'LOCAL').lower() == 'dev':
    if not '_dev' in STREAMER_ROUTING_KEY:
        STREAMER_ROUTING_KEY += '_dev'
    if not '_dev' in SMONITOR_KEY:
        SMONITOR_KEY += '_dev'

RETAILER_KEY = os.getenv('RETAILER_KEY')
SCRAPER_TYPE = os.getenv('SCRAPER_TYPE')


class RabbitEngine(object):
    """This is a consumer/producer that can handle unexpected interactions
    with RabbitMQ such as channel and connection closures.

    If RabbitMQ closes the connection, it will reopen it. You should
    look at the output, as there are limited reasons why the connection may
    be closed, which usually are tied to permission related issues or
    socket timeouts.

    If the channel is closed, it will indicate a problem with one of the
    commands that were issued and that should surface in the output as well.

    """

    def __init__(self, config, blocking=False, purge=False):
        """Setup the example publisher object, passing in the URL we will use
        to connect to RabbitMQ.
        :param str amqp_url: The URL for connecting to RabbitMQ
        """

        self._connection = None
        self._channel = None
        self._deliveries = []
        self._acked = 0
        self._nacked = 0
        self._message_number = 0
        self._stopping = False
        self._closing = False
        self._callback = self.on_message
        self._async = not blocking
        self._purge = purge

        self.USER = config['user'] if 'user' in config.keys() else os.getenv('STREAMER_USER','guest')
        self.PWD = config['password'] if 'password' in config.keys() else os.getenv('STREAMER_PASS','guest')
        self.HOST = config['host'] if 'host' in config.keys() else os.getenv('STREAMER_HOST','localhost')
        self.VHOST = config['vhost'] if 'vhost' in config.keys() else os.getenv('STREAMER_VIRTUAL_HOST','')
        self.PORT = config['port'] if 'port' in config.keys() else os.getenv('STREAMER_PORT','5672')
        self.CONN_ATTEMPTS = str(config['connection_attempts']) if 'connection_attempts' in config.keys() else '3'
        self.HEARTBEAT = config['heartbeat_interval'] if 'heartbeat_interval' in config.keys() else '0'

        self.EXCHANGE = config['exchange'] if 'exchange' in config.keys() else os.getenv('STREAMER_EXCHANGE','data')
        self.EXCHANGE_TYPE = config['exchange_type'] if 'exchange_type' in config.keys() else os.getenv('STREAMER_EXCHANGE_TYPE','direct')
        self.ROUTING_KEY = config['routing_key'] if 'routing_key' in config.keys() else os.getenv('STREAMER_ROUTING_KEY','')
        self.QUEUE = config['queue'] if 'queue' in config.keys() else os.getenv('STREAMER_QUEUE','')
        
        self._prefetch = config.get('prefetch', None)

    def set_callback(self,callback):
        self._callback = callback

    def connect(self):
        """This method connects to RabbitMQ, returning the connection handle.
        When the connection is established, the on_connection_open method
        will be invoked by pika.
        :rtype: pika.SelectConnection
        """
        if self._async:
            self._url = 'amqp://%s:%s@%s:%s/%s?connection_attempts=%s&heartbeat_interval=%s' % \
                        (self.USER,self.PWD,self.HOST,self.PORT, self.VHOST,self.CONN_ATTEMPTS,self.HEARTBEAT)
            
            LOGGER.debug('Connecting to %s', self._url)
            self._connection = pika.SelectConnection(pika.URLParameters(self._url),
                                    self.on_connection_open,
                                    stop_ioloop_on_close=False)
        else:
            self._connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                                        host=self.HOST,
                                        port=int(self.PORT),
                                        credentials=pika.credentials.PlainCredentials(self.USER, self.PWD),
                                        virtual_host=self.VHOST,
                                        heartbeat_interval=0
                                        )
                                    )
            self._channel = self._connection.channel()
            self._channel.exchange_declare(exchange=self.EXCHANGE,exchange_type=self.EXCHANGE_TYPE, durable=True)
            self._channel.queue_declare(queue=self.QUEUE, durable=True)
            if self._purge:
                self._channel.queue_purge(queue=self.QUEUE)

    def on_blocked_connection_closed(self):
        """ Method to apply reconnection when a Blocking connection 
            has been lost, it applies the same reconnection code.
        """
        if not self._connection:
            self.connect()
        elif self._connection.is_closed:
            self.connect()

    def on_connection_open(self, unused_connection):
        """This method is called by pika once the connection to RabbitMQ has
        been established. It passes the handle to the connection object in
        case we need it, but in this case, we'll just mark it unused.
        :type unused_connection: pika.SelectConnection
        """
        LOGGER.debug('Connection opened')
        self.add_on_connection_close_callback()
        self.open_channel()

    def add_on_connection_close_callback(self):
        """This method adds an on close callback that will be invoked by pika
        when RabbitMQ closes the connection to the publisher unexpectedly.

        """
        LOGGER.debug('Adding connection close callback')
        self._connection.add_on_close_callback(self.on_connection_closed)

    def on_connection_closed(self, connection, reply_code, reply_text):
        """This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.

        :param pika.connection.Connection connection: The closed connection obj
        :param int reply_code: The server provided reply_code if given
        :param str reply_text: The server provided reply_text if given

        """
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            LOGGER.debug('Connection closed, reopening in 5 seconds: (%s) %s',
                           reply_code, reply_text)
            self._connection.add_timeout(5, self.reconnect)

    def reconnect(self):
        """Will be invoked by the IOLoop timer if the connection is
        closed. See the on_connection_closed method.

        """
        # This is the old connection IOLoop instance, stop its ioloop
        self._connection.ioloop.stop()

        if not self._closing:

            # Create a new connection
            self.connect()

            # There is now a new connection, needs a new ioloop to run
            self._connection.ioloop.start()

    def open_channel(self):
        """Open a new channel with RabbitMQ by issuing the Channel.Open RPC
        command. When RabbitMQ responds that the channel is open, the
        on_channel_open callback will be invoked by pika.

        """
        LOGGER.debug('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        """This method is invoked by pika when the channel has been opened.
        The channel object is passed in so we can make use of it.

        Since the channel is now open, we'll declare the exchange to use.

        :param pika.channel.Channel channel: The channel object

        """
        LOGGER.debug('Channel opened')
        self._channel = channel
        if self._prefetch:
                LOGGER.debug('Prefetch count %s', self._prefetch)
                self._channel.basic_qos(prefetch_count=int(self._prefetch))
        self.add_on_channel_close_callback()
        self.setup_exchange(self.EXCHANGE)

    def add_on_channel_close_callback(self):
        """This method tells pika to call the on_channel_closed method if
        RabbitMQ unexpectedly closes the channel.

        """
        LOGGER.debug('Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reply_code, reply_text):
        """Invoked by pika when RabbitMQ unexpectedly closes the channel.
        Channels are usually closed if you attempt to do something that
        violates the protocol, such as re-declare an exchange or queue with
        different parameters. In this case, we'll close the connection
        to shutdown the object.

        :param pika.channel.Channel: The closed channel
        :param int reply_code: The numeric reason the channel was closed
        :param str reply_text: The text reason the channel was closed

        """
        LOGGER.debug('Channel %i was closed: (%s) %s',
                       channel, reply_code, reply_text)
        self._connection.close()

    def setup_exchange(self, exchange_name):
        """Setup the exchange on RabbitMQ by invoking the Exchange.Declare RPC
        command. When it is complete, the on_exchange_declareok method will
        be invoked by pika.

        :param str|unicode exchange_name: The name of the exchange to declare

        """
        LOGGER.debug('Declaring exchange %s', exchange_name)
        self._channel.exchange_declare(self.on_exchange_declareok,
                                       exchange_name,
                                       self.EXCHANGE_TYPE)

    def on_exchange_declareok(self, unused_frame):
        """Invoked by pika when RabbitMQ has finished the Exchange.Declare RPC
        command.

        :param pika.Frame.Method unused_frame: Exchange.DeclareOk response frame

        """
        LOGGER.debug('Exchange declared')
        self.setup_queue(self.QUEUE)

    def setup_queue(self, queue_name):
        """Setup the queue on RabbitMQ by invoking the Queue.Declare RPC
        command. When it is complete, the on_queue_declareok method will
        be invoked by pika.

        :param str|unicode queue_name: The name of the queue to declare.

        """
        LOGGER.debug('Declaring queue %s', queue_name)
        self._channel.queue_declare(callback=self.on_queue_declareok, queue=queue_name, auto_delete=False)

    def on_queue_declareok(self, method_frame):
        """Method invoked by pika when the Queue.Declare RPC call made in
        setup_queue has completed. In this method we will bind the queue
        and exchange together with the routing key by issuing the Queue.Bind
        RPC command. When this command is complete, the on_bindok method will
        be invoked by pika.

        :param pika.frame.Method method_frame: The Queue.DeclareOk frame

        """
        LOGGER.debug('Binding %s to %s with %s',
                    self.EXCHANGE, self.QUEUE, self.ROUTING_KEY)
        self._channel.queue_bind(self.on_bindok, self.QUEUE,
                                 self.EXCHANGE, self.ROUTING_KEY)

    def on_bindok(self, unused_frame):
        """Invoked by pika when the Queue.Bind method has completed. At this
        point we will start consuming messages by calling start_consuming
        which will invoke the needed RPC commands to start the process.

        :param pika.frame.Method unused_frame: The Queue.BindOk response frame

        """
        LOGGER.debug('Queue bound')
        self.start_consuming()

    def start_consuming(self):
        """This method sets up the consumer by first calling
        add_on_cancel_callback so that the object is notified if RabbitMQ
        cancels the consumer. It then issues the Basic.Consume RPC command
        which returns the consumer tag that is used to uniquely identify the
        consumer with RabbitMQ. We keep the value to use it when we want to
        cancel consuming. The on_message method is passed in as a callback pika
        will invoke when a message is fully received.

        """
        LOGGER.debug('Issuing consumer related RPC commands')
        self.add_on_cancel_callback()
        self._consumer_tag = self._channel.basic_consume(self._callback,
                                                         self.QUEUE)

    def start_publishing(self):
        """This method will enable delivery confirmations and schedule the
        first message to be sent to RabbitMQ
        """
        LOGGER.debug('Issuing consumer related RPC commands')
        self.enable_delivery_confirmations()
        #self.schedule_next_message()

    def enable_delivery_confirmations(self):
        """Send the Confirm.Select RPC method to RabbitMQ to enable delivery
        confirmations on the channel. The only way to turn this off is to close
        the channel and create a new one.

        When the message is confirmed from RabbitMQ, the
        on_delivery_confirmation method will be invoked passing in a Basic.Ack
        or Basic.Nack method from RabbitMQ that will indicate which messages it
        is confirming or rejecting.
        """
        LOGGER.debug('Issuing Confirm.Select RPC command')
        self._channel.confirm_delivery(self.on_delivery_confirmation)

    def on_delivery_confirmation(self, method_frame):
        """Invoked by pika when RabbitMQ responds to a Basic.Publish RPC
        command, passing in either a Basic.Ack or Basic.Nack frame with
        the delivery tag of the message that was published. The delivery tag
        is an integer counter indicating the message number that was sent
        on the channel via Basic.Publish. Here we're just doing house keeping
        to keep track of stats and remove message numbers that we expect
        a delivery confirmation of from the list used to keep track of messages
        that are pending confirmation.

        :param pika.frame.Method method_frame: Basic.Ack or Basic.Nack frame

        """
        confirmation_type = method_frame.method.NAME.split('.')[1].lower()
        LOGGER.debug('Received %s for delivery tag: %i',
                    confirmation_type,
                    method_frame.method.delivery_tag)
        if confirmation_type == 'ack':
            self._acked += 1
        elif confirmation_type == 'nack':
            self._nacked += 1
        self._deliveries.remove(method_frame.method.delivery_tag)
        LOGGER.debug('Published %i messages, %i have yet to be confirmed, '
                    '%i were acked and %i were nacked',
                    self._message_number, len(self._deliveries),
                    self._acked, self._nacked)

    def send(self,message):
        self._message = message
        self.publish_message(message)

    def publish_message(self,message):
        if self._stopping:
            return
        properties = pika.BasicProperties(app_id="byprice",content_type='application/json', delivery_mode=2)
        # Add reconnection when is disconnected
        self.on_blocked_connection_closed()
        self._channel.basic_publish(exchange=self.EXCHANGE,
                                    routing_key=self.ROUTING_KEY,
                                    body=json.dumps(message, ensure_ascii=False),
                                    properties=properties)
        self._message_number += 1
        LOGGER.debug('Published message # %i', self._message_number)

    def add_on_cancel_callback(self):
        """Add a callback that will be invoked if RabbitMQ cancels the consumer
        for some reason. If RabbitMQ does cancel the consumer,
        on_consumer_cancelled will be invoked by pika.

        """
        LOGGER.debug('Adding consumer cancellation callback')
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

    def on_consumer_cancelled(self, method_frame):
        """Invoked by pika when RabbitMQ sends a Basic.Cancel for a consumer
        receiving messages.

        :param pika.frame.Method method_frame: The Basic.Cancel frame

        """
        LOGGER.debug('Consumer was cancelled remotely, shutting down: %r',
                    method_frame)
        if self._channel:
            self._channel.close()

    def on_message(self, unused_channel, basic_deliver, properties, body):
        """Invoked by pika when a message is delivered from RabbitMQ. The
        channel is passed for your convenience. The basic_deliver object that
        is passed in carries the exchange, routing key, delivery tag and
        a redelivered flag for the message. The properties passed in is an
        instance of BasicProperties with the message properties and the body
        is the message that was sent.

        :param pika.channel.Channel unused_channel: The channel object
        :param pika.Spec.Basic.Deliver: basic_deliver method
        :param pika.Spec.BasicProperties: properties
        :param str|unicode body: The message body
        """
        LOGGER.debug('Received message # %s from %s: %s',
                    basic_deliver.delivery_tag, properties.app_id, body)
        self.acknowledge_message(basic_deliver.delivery_tag)

    def acknowledge_message(self, delivery_tag):
        """Acknowledge the message delivery from RabbitMQ by sending a
        Basic.Ack RPC method for the delivery tag.

        :param int delivery_tag: The delivery tag from the Basic.Deliver frame

        """
        LOGGER.debug('Acknowledging message %s', delivery_tag)
        self._channel.basic_ack(delivery_tag)

    def stop_consuming(self):
        """Tell RabbitMQ that you would like to stop consuming by sending the
        Basic.Cancel RPC command.

        """
        if self._channel:
            LOGGER.debug('Sending a Basic.Cancel RPC command to RabbitMQ')
            self._channel.basic_cancel(self.on_cancelok, self._consumer_tag)

    def on_cancelok(self, unused_frame):
        """This method is invoked by pika when RabbitMQ acknowledges the
        cancellation of a consumer. At this point we will close the channel.
        This will invoke the on_channel_closed method once the channel has been
        closed, which will in-turn close the connection.

        :param pika.frame.Method unused_frame: The Basic.CancelOk frame

        """
        LOGGER.debug('RabbitMQ acknowledged the cancellation of the consumer')
        self.close_channel()

    def close_channel(self):
        """Call to close the channel with RabbitMQ cleanly by issuing the
        Channel.Close RPC command.

        """
        LOGGER.debug('Closing the channel')
        self._channel.close()

    def run(self):
        """Run the example consumer by connecting to RabbitMQ and then
        starting the IOLoop to block and allow the SelectConnection to operate.
        """
        self.connect()
        self._connection.ioloop.start()

    def stop(self):
        """Cleanly shutdown the connection to RabbitMQ by stopping the consumer
        with RabbitMQ. When RabbitMQ confirms the cancellation, on_cancelok
        will be invoked by pika, which will then closing the channel and
        connection. The IOLoop is started again because this method is invoked
        when CTRL-C is pressed raising a KeyboardInterrupt exception. This
        exception stops the IOLoop which needs to be running for pika to
        communicate with RabbitMQ. All of the commands issued prior to starting
        the IOLoop will be buffered but not processed.

        """
        LOGGER.debug('Stopping')
        self._closing = True
        self.stop_consuming()
        self._connection.ioloop.start()
        LOGGER.debug('Stopped')

    def close_connection(self):
        """This method closes the connection to RabbitMQ."""
        LOGGER.debug('Closing connection')
        self._connection.close()


class Streamers(object):
    stream_info = RabbitEngine({
        'queue': STREAMER_ROUTING_KEY,
        'routing_key': STREAMER_ROUTING_KEY
    }, blocking=True)

    stream_monitor = RabbitEngine({
            'queue': SMONITOR_KEY,
            'routing_key': SMONITOR_KEY
        }, blocking=True)

    def __init__(self):
        pass


    @staticmethod
    def send_stream_info(elem, param='id', first_attempt=True):

        try:
            LOGGER.debug("Streaming [{}]".format(elem.get(param, '')))
            Streamers.stream_info.send(elem)
            return True
        except Exception as e:
            LOGGER.error("Error while streaming: {}".format(e))
        if first_attempt:
            try:
                if Streamers.stream_info:
                    LOGGER.debug("Closing possible channel in stream_info")
                    Streamers.stream_info.close_channel()
                    LOGGER.debug("Closing possible connection in stream_info")
                    Streamers.stream_info.close_connection()
                else:
                    raise Exception("stream_info does not exist anymore")
            except Exception as e:
                LOGGER.error("Error while closing stream_info: {}".format(e))

            try:
                Streamers.stream_info = RabbitEngine({
                    'queue': STREAMER_ROUTING_KEY,
                    'routing_key': STREAMER_ROUTING_KEY
                }, blocking=True)
                Streamers.send_stream_info(elem, param=param, first_attempt=False)
            except Exception as e:
                LOGGER.error("Error while reconnecting streamer_info: {}".format(e))
                return False
        return False


    @staticmethod
    def send_stream_monitor(elem, param='id', first_attempt=True):
        try:
            LOGGER.debug("Streaming [{}]".format(elem.get(param, '')))
            Streamers.stream_monitor.send(elem)
            return True
        except Exception as e:
            LOGGER.error("Error while streaming: {}".format(e))

        if first_attempt:
            try:
                if Streamers.stream_monitor:
                    LOGGER.debug("Closing possible channel in stream_monitor")
                    Streamers.stream_monitor.close_channel()
                    LOGGER.debug("Closing possible connection in stream_monitor")
                    Streamers.stream_monitor.close_connection()
                else:
                    raise Exception("stream_monitor does not exist anymore")
            except Exception as e:
                LOGGER.error("Error while closing stream_monitor: {}".format(e))

            try:
                Streamers.stream_monitor = RabbitEngine({
                    'queue': SMONITOR_KEY,
                    'routing_key': SMONITOR_KEY
                }, blocking=True)
                Streamers.send_stream_monitor(elem, param=param, first_attempt=False)
            except Exception as e:
                LOGGER.error("Error while reconnecting stream_monitor: {}".format(e))
                return False
        return False


    @staticmethod
    def close_stream_info():
        Streamers.stream_info.close_channel()
        Streamers.stream_info.close_connection()


    @staticmethod
    def close_stream_monitor():
        Streamers.stream_monitor.close_channel()
        Streamers.stream_monitor.close_connection()


def stream_info(elem, param='id'):
    return Streamers.send_stream_info(elem, param)


def close_stream_info():
    Streamers.close_stream_info()


def close_stream_monitor():
    Streamers.close_stream_monitor()


def stream_monitor(signal_type, **params):
    try:
        if signal_type.lower()=='master':
            if SCRAPER_TYPE == 'item' or SCRAPER_TYPE == 'price':
                required_params = ['params', 'num_stores']
            elif SCRAPER_TYPE == 'store':
                required_params = []
            else:
                raise Exception("SCRAPER_TYPE {} is not defined for master".format(str(SCRAPER_TYPE)))
            for param in required_params:
                if params.get(param, False) is False:
                    raise Exception('{} not defined in master signal'.format(param))
            ms_id = str(uuid.uuid1())
            elem = {
                'signal': 'master',
                'ms_id': ms_id,
                'retailer_key': RETAILER_KEY,
                'params': params.get('params'),
                'num_stores': params.get('num_stores'),
                'type_': SCRAPER_TYPE
            }
            if __sm(elem):
                return ms_id
            else:
                return False

        elif signal_type.lower()=='worker':
            required_params = ['ms_id', 'step', 'store_id']
            for param in required_params:
                if params.get(param, False) is False:
                    raise Exception('{} not defined in worker signal'.format(param))
            ws_id = str(uuid.uuid1())
            elem = {
                'signal': 'worker',
                'retailer_key': RETAILER_KEY,
                'type_': SCRAPER_TYPE,
                'ms_id': params.get('ms_id'),
                'step': params.get('step'),
                'store_id': params.get('store_id'),
                'value': params.get('value'),
                'ws_id': ws_id,
                'br_stats': params.get('br_stats', {})
            }
            if __sm(elem):
                return ws_id
            else:
                return False
        elif signal_type.lower()=='error':
            if params.get('ws_id'):
                required_params = ['ws_id', 'store_id', 'code', 'reason']
                for param in required_params:
                    if params.get(param, False) is False:
                        raise Exception('{} param not defined in error signal'.format(param))
            elif params.get('ms_id'):
                required_params = ['code', 'reason']
                for param in required_params:
                    if not params.get(param):
                        raise Exception('{} not defined in error signal'.format(param))
            es_id = str(uuid.uuid1())
            elem = {
                'signal': 'error',
                'retailer_key': RETAILER_KEY,
                'type_': SCRAPER_TYPE,
                'ws_id': params.get('ws_id'),
                'ms_id': params.get('ms_id'),
                'store_id': params.get('store_id'),
                'code': params.get('code'),
                'reason': params.get('reason'),
                'es_id': es_id
            }
            if __sm(elem):
                return es_id
            else:
                return False

        else:
            raise Exception('Wrong signal_type')
    except Exception as e:
        LOGGER.error("Error parsing smonitor signal: {}".format(e))
        return False


def __sm(elem, param='signal'):
    """
    Stream the elem to smonitor queue RabbitMQ
    :param elem: dict
    :param param: str
    :return: Boolean
    """
    return Streamers.send_stream_monitor(elem, param)


class MonitorException(Exception):
    """
    Error class with attributes code and reason
    """
    def __init__(self, code=2, reason=''):
        self.code = code
        self.reason = reason

