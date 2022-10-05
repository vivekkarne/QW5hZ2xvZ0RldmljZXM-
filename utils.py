import queue
import threading

"""
Subclass of thread-safe queue.Queue class, wraps put and get message
by handling sentinel character insertion and removal. Sentinel character
None is used to indicate to the sender threads that the producer has stopped sending
"""
class MessageQueue(queue.Queue):
    def __init__(self, maxsize: int = 1001) -> None:
        super().__init__(maxsize)
    
    #Setter - Takes two arguments, message and phone number to store in a queue
    def put_message(self, message, phone = None):
        if message is None:
            self.put(None)
            return
        self.put({"msg": message, "pno": phone})
    
    #Getter - returns None, if sentinel character, else returns the message and phone_number
    def get_message(self):
        message_dic = self.get()
        if message_dic is None:
            return message_dic
        return message_dic['msg'], message_dic['pno']

"""
Wrapper class for threading.Timer object, used for the monitoring thread.
A new timer is created every "interval" seconds, and the old one is garbage collected.
Instance Variables:
__timer - timer variable
interval - N seconds for a new timer to spin up
function - function that is to run every N seconds
total_msgs - total msgs sent from the producer, used as stop condition for the timer, ie. to cancel it 
stats - input to the function, shared variable for sender and monitor timer
stats_lock - lock for accessing the stats variable
"""   
class MonitorThread():
    def __init__(self, interval, function, total_msgs, stats, stats_lock) -> None:
        self.__timer = None
        self.interval = interval
        self.function = function
        self.stats = stats
        self.stats_lock = stats_lock
        self.total_msgs = total_msgs
        self.running= False
        self.start()

    # Prepares for the next timer, and executes the function supplied with params
    def __run(self):
        self.running = False
        self.start()
        self.function(self, self.total_msgs, self.stats, self.stats_lock)
    
    # New timer is created and is started
    def start(self):
        if not self.running:
            self.__timer = threading.Timer(self.interval, self.__run)
            self.__timer.start()
            self.running = True
    
    # Cancels the timer and resets running, so a new Timer can be started
    def stop(self):
        self.__timer.cancel()
        self.running = False