import queue
import threading

class MessageQueue(queue.Queue):
    def __init__(self, maxsize: int = 1001) -> None:
        super().__init__(maxsize)
    
    def put_message(self, message, phone = None):
        if message is None:
            self.put(None)
            return
        self.put({"msg": message, "pno": phone})
    
    def get_message(self):
        message_dic = self.get()
        if message_dic is None:
            return message_dic
        return message_dic['msg'], message_dic['pno']
    
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

    def __run(self):
        self.running = False
        self.start()
        self.function(self, self.total_msgs, self.stats, self.stats_lock)
    
    def start(self):
        if not self.running:
            self.__timer = threading.Timer(self.interval, self.__run)
            self.__timer.start()
            self.running = True

    def stop(self):
        self.__timer.cancel()
        self.running = False