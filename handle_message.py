class handle_message:
    def put_in_struct(message,op):
        
        
        message={"op":op,"data":message}
        return message
    def send_regular(message):
        message=handle_message.put_in_struct(message,"regular_message")
        return message
    def ping():
        message=handle_message.put_in_struct("","ping")
        return message
    def return_ping():
        message=handle_message.put_in_struct("","return_ping")
        return message
    def accept_message(id):
        return handle_message.put_in_struct(id,"accept_message")
    def ping_comm():
        return handle_message.put_in_struct("","ping_comm")
    def can_be_server():
        return handle_message.put_in_struct("","can_be_server")
 