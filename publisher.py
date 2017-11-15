import pika
mq_creds  = pika.PlainCredentials(username = "guest", password = "guest")
mq_params = pika.ConnectionParameters(host= "localhost",credentials  = mq_creds,virtual_host = "/")
mq_exchange    = "amq.topic"
mq_routing_key = "mymessages1"
mq_conn = pika.BlockingConnection(mq_params)

# This is one channel inside the connection
mq_chan = mq_conn.channel()
                                                                                                                                        
import readline
print("Press Ctrl+C to quit.\n")

while True:
  text = raw_input("Enter your message: ")
  print("Sending '" + text + "'")
  mq_chan.basic_publish(exchange = mq_exchange, routing_key = mq_routing_key, body = text)

