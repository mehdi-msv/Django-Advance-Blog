import threading

class EmailThread(threading.Thread):
  # overriding constructor
  def __init__(self, message):
    # calling parent class constructor
    threading.Thread.__init__(self)
    self.message = message
  def run(self):
    self.message.send()