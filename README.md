# QW5hZ2xvZ0RldmljZXM-
## Abstract
We are dealing with a producer consumer problem, where in the producer generates many messages which are to be sent to multiple mobile numbers, multiple senders simulate sending of these messages and, a monitor then displays the progress at regular intervals. We can use a multi-threaded approach, with threads for producer, senders and the monitor. The producer and sender threads use a thread-safe Queue for communication, and the consumer threads update to a shared location which the monitor thread uses to display the statistics.  

The consumer simulates sending using wait times which are modeled as an exponential distribution and, the consumer failure rates are modeled using a uniform distribution. Both successful and failed messages incur wait times and the statistics display the average wait time per message.

## Run Steps (Python 3.6+)
### Simulation
1) Create a virtual env using `python3 -m venv env`
2) Activate the source `source env/bin/activate`
3) Install the requirements `pip3 install -r requirements.txt`
4) Run the simulation `python3 simulation.py`
5) Enter 'd' for default configurations when prompted

### Unit Tests
1) Run steps 1 & 2 from Simulation
2) Run tests.py `python3 tests.py`