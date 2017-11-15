# # In consumers.py
# from channels import Group

# # Connected to websocket.connect
# def ws_add(message):
#     # Accept the connection
#     print message
#     print "---------------"
#     print message.content["query_string"]
#     print "---------------"

#     message.reply_channel.send({"accept": True})
#     # Add to the chat group
#     Group("chat").add(message.reply_channel)

# # Connected to websocket.receive
# def ws_message(message):
#     print message
#     Group("chat").send({
#         "text": "[user] %s" % message.content['text'],
#     })

# # Connected to websocket.disconnect
# def ws_disconnect(message):
#     Group("chat").discard(message.reply_channel)





# In consumers.py
# import json
# from channels import Group
# from channels.sessions import channel_session
# # from urllib.parse import parse_qs

# # Connected to websocket.connect
# @channel_session
# def ws_connect(message, room_name):
#     print "-----------------ws_connect---------------"
#     # Accept connection
#     message.reply_channel.send({"accept": True})
#     # Parse the query string
#     # params = parse_qs(message.content["query_string"])
#     params = ""
#     if b"username" in params:
#         # Set the username in the session
#         message.channel_session["username"] = params[b"username"][0].decode("utf8")
#         # Add the user to the room_name group
#         Group("chat-%s" % room_name).add(message.reply_channel)
#     else:
#         # Close the connection.
#         message.reply_channel.send({"close": True})

# # Connected to websocket.receive
# @channel_session
# def ws_message(message, room_name):
#     print "-----------------ws_message---------------"
#     Group("chat-%s" % room_name).send({
#         "text": json.dumps({
#             "text": message["text"],
#             "username": message.channel_session["username"],
#         }),
#     })

# # Connected to websocket.disconnect
# @channel_session
# def ws_disconnect(message, room_name):
#     print "-----------------ws_disconnect---------------"
#     Group("chat-%s" % room_name).discard(message.reply_channel)


# In consumers.py
from channels import Channel, Group
from channels.sessions import channel_session
from channels.auth import channel_session_user, channel_session_user_from_http


room_name = "rbs"
# Connected to websocket.connect
@channel_session_user_from_http
def ws_add(message):
    # Accept connection
    print "ws_add"
    room_name = message.content['path'].strip("/")
    print room_name
    message.channel_session['room'] = room_name 
    message.reply_channel.send({"accept": True})
    # Add them to the right group
    Group("push-%s" % room_name).add(message.reply_channel)

# Connected to websocket.receive
@channel_session_user
def ws_message(message):
    Group("push-%s" % message.channel_session['room']).send({
        "text": message['text'],
    })

# Connected to websocket.disconnect
@channel_session_user
def ws_disconnect(message):
    Group("push-%s" % message.channel_session['room']).discard(message.reply_channel)