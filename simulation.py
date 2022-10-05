import concurrent.futures
import threading
import random
import string
import numpy as np
from time import sleep
import datetime

from utils import MessageQueue, MonitorThread

"""
Startup method for producer thread, generates messages/pno's and puts them into the queue.
Terminates with a sentinel character after all the messages are put.
message_q - MessageQueue object
rn_p - Random generator for producer
num_msgs - Number of msgs to be produced
"""
def producer(message_q, rn_p, num_msgs = 1000):
    for _ in range(num_msgs):
        message = ''.join(rn_p.choices(string.ascii_uppercase + string.digits, k=rn_p.randint(1,100)))
        pno = '{}-{}-{}'.format(str(rn_p.randint(100,999)),str(rn_p.randint(1,888)).zfill(3), str(rn_p.randint(1,9998)).zfill(4))
        message_q.put_message(message,pno)
    message_q.put_message(None)


"""
Sender startup function parses messages from the message queue, simulates sending by waiting, and determines if the
send was successful or not. Also, terminates on encountering a sentinel value (None) and reinserts it for the next 
sender to terminate.
Also updates the stats variable with successful messages, failed messages, and total time waited until now.
message_q - MessageQueue object
rnd - Random generator for each consumer
stats - list to store statistics for monitor to read later
stats_lock - lock for stats list
failure_rate [0-1] - probability that a message will fail to be sent x% of the time
mean - average waiting time specified by the user
"""
def sender(message_q, rnd, stats, stats_lock, failure_rate =  0.1, mean = 0.3):
    while True:
        message_tuple = message_q.get_message()

        # exit from infinite loop when senntinel is encountered 
        if message_tuple is None:
            message_q.put_message(None)
            break

        fail = False

        # get wait time from exponential distribution, as they are best modeled by this distribution
        rn_wt = rnd.exponential(mean)
        sleep(rn_wt)

        # Uniform distribution models failure rate
        if rnd.uniform(0,1) <= failure_rate:
            fail=True

        #Update stats using the lock
        stats_lock.acquire()
        if fail:
            stats[1] += 1
        else:
            stats[0] += 1
        stats[2] += rn_wt
        stats_lock.release()

        
"""
Function passed to the Timer in MonitorThread object, run every "interval" seconds
mon - MonitorThread object which calls monitor function
total_msgs - total messages produced, used to stop the MonitorThread object timer
stats - stats object to get the stats from
stats_lock - lock for the stats object
"""
def monitor(mon, total_msgs, stats, stats_lock):
    stats_lock.acquire()
    if stats[0]+stats[1] > 0:
        print("********")
        print("Timestamp", datetime.datetime.now())
        print("Number of messages sent so far:", stats[0])
        print("Number of messages Failed so far:", stats[1])
        print("Average time per message so far:", stats[2]/(stats[0] + stats[1]))
        print("********")
        if stats[0] + stats[1] == total_msgs:
            mon.stop()
    else:
        print("Stats waiting for atleast one message to be picked up by sender")
    stats_lock.release()


if __name__ == "__main__":
    
    # Params
    x = input("Enter the number of messages to be sent [d - default(1000)]: ")
    total_msgs = 1000 if x == 'd' else int(x)

    s_x = input("Enter the number of senders to be started [d - default(10), mean(0.3 seconds), failure_rate(0.1)]: ")
    senders = 10 if s_x == 'd' else int(s_x)

    sender_config = [dict({"mean": 0.3, "failure_rate": 0.1}) for _ in range(senders)]

    if s_x != 'd':
        for i in range(senders):
            sender_config[i]["mean"] = float(input("Enter average wait time for sender {} (seconds): ".format(i+1)))
            sender_config[i]["failure_rate"] = float(input("Enter failure rate [0-1] for sender {}: ".format(i+1)))

    m_x = input("Enter the interval(seconds) for monitor thread [d - default(5 seconds)]: ")
    interval = 5.0 if m_x == 'd' else float(m_x)

    # stats, 0-total sent, 1-total failed, 2-total time
    stats = [0,0,0.0]

    stats_lock = threading.Lock()

    message_q = MessageQueue(1001)

    # Spawn and submit threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=senders+1) as executor:
        MonitorThread(interval, monitor, total_msgs, stats, stats_lock)
        rn_p = random.Random()
        executor.submit(producer, message_q, rn_p,total_msgs)
        for i in range(senders):
            # Each sender should have its own random object
            rnd = np.random.default_rng()
            executor.submit(sender, message_q, rnd, stats, stats_lock ,sender_config[i]["failure_rate"], sender_config[i]["mean"])