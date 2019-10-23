class ValitorException(Exception):

    def __init__(self, number, message, log_id):
        print(number, message, log_id)
        self.number = number
        self.message = message
        self.log_id = log_id


class ValitorPayException(Exception):

    def __init__(self, message):
        print(message)
        self.message = message
