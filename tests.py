from unittest import mock
import simulation
from utils import MessageQueue, MonitorThread
import unittest
import time

class MessageQueueTest(unittest.TestCase):
    def setUp(self):
        self.mq = MessageQueue()

    def test_sentinel(self):
        self.mq.put_message(None)
        self.assertIsNone(self.mq.get_message())
    
    def test_message(self):
        self.mq.put_message("Test","12345678")
        msg, pno = self.mq.get_message()
        self.assertEqual(msg, "Test")
        self.assertEqual(pno, "12345678")

    def test_msg_with_sentinel(self):
        self.mq.put_message("Test","12345678")
        self.mq.put_message(None)
        msg, pno = self.mq.get_message()
        self.assertEqual(msg, "Test")
        self.assertEqual(pno, "12345678")
        self.assertIsNone(self.mq.get_message())


class MonitorThreadTest(unittest.TestCase):
    def setUp(self):
        self.monitor = mock.Mock()
        self.mock_lock = mock.Mock()
        self.total_msgs = 100
        self.stats = [0,0,0]
        self.mt = MonitorThread(2, self.monitor, self.total_msgs, self.stats, self.mock_lock)

    # @unittest.skip("Time save")
    # test that timer is calling monitor method by mocking monitor method
    def test_timer(self):
        time.sleep(3)
        self.monitor.assert_called_once_with(self.mt, self.total_msgs, self.stats, self.mock_lock)
        self.assertEqual(self.monitor.call_count, 1)

    def tearDown(self) -> None:
        self.mt.stop()

class ProducerSenderTest(unittest.TestCase):
    def setUp(self):
        self.num_msgs = 100
        self.sentinel = 1
        self.mq = MessageQueue(self.num_msgs + self.sentinel)
        self.stats = [0,0,0]
        self.stats_lock = simulation.threading.Lock()
    
    def __fill_q(self):
        rn_p = simulation.random.Random()
        prod = simulation.threading.Thread(target=simulation.producer, args=(self.mq, rn_p, self.num_msgs))
        prod.start()
        prod.join()

    # @unittest.skip("Time save")
    def test_producer(self):
        self.__fill_q()
        self.assertEqual(self.mq.qsize(), self.num_msgs + self.sentinel)
    
    def test_sender(self):
        self.__fill_q()
        rnd = simulation.np.random.default_rng()

        consumer = simulation.threading.Thread(target=simulation.sender, args=(self.mq, rnd, self.stats, self.stats_lock, 0.1, 0.03))
        consumer.start()
        consumer.join()
        self.assertEqual(self.num_msgs, self.stats[0]+self.stats[1])
        self.assertEqual(self.mq.qsize(), 1)

    def test_multiple_senders(self):
        self.__fill_q()
        senders_n = 7
        with simulation.concurrent.futures.ThreadPoolExecutor(max_workers=senders_n) as executor:
            for i in range(senders_n):
                rnd = simulation.np.random.default_rng()
                executor.submit(simulation.sender, self.mq, rnd, self.stats, self.stats_lock, 0.1, 0.03)
        
        self.assertEqual(self.num_msgs, self.stats[0]+self.stats[1])
        self.assertEqual(self.mq.qsize(), 1)
    
    def test_monitor_stop(self):
        self.test_sender()
        MonitorThread.stop = mock.Mock()
        mt = MonitorThread(2, simulation.monitor, self.num_msgs, self.stats, self.stats_lock)
        time.sleep(3)
        mt._MonitorThread__timer.cancel()
        MonitorThread.stop.assert_called_once()

if __name__ == "__main__":
    unittest.main(buffer=True)