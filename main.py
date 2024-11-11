import simpy
import random
import matplotlib.pyplot as plt

# Parameters
EXPECTED_EMPLOYEES = 1000  # Expected number of employees arriving in one hour
PEAK_ARRIVAL_RATE = 1 / 2  # Higher arrival rate during peak times (employees per second)
LOW_ARRIVAL_RATE = 1 / 20  # Lower arrival rate outside peak times (employees per second)
SERVICE_RATE = 1 / 12       # Average service time (6 seconds per employee)
SIMULATION_DURATION = 3600  # Simulate 1 hour (8:00 AM to 9:00 AM)

# Data collection
results = {
    'num_machines': [],
    'wait_times': [],
    'queue_lengths': [],
    'utilization': [],
    'throughput': []
}

def employee(env, name, machine, wait_times, queue_lengths, served_count):
    """ Simulate an employee entering and being processed by a machine. """
    arrival_time = env.now  # Time when the employee arrives
    with machine.request() as req:
        yield req  # Wait for access to a machine
        wait_time = env.now - arrival_time  # Calculate wait time in queue
        wait_times.append(wait_time)  # Record wait time
        queue_lengths.append(len(machine.queue))  # Record queue length
        # Variable service time with slight random variation
        yield env.timeout(random.expovariate(SERVICE_RATE) * random.uniform(0.8, 1.2))
        served_count[0] += 1  # Increment the count of served employees

def setup(env, num_machines, wait_times, queue_lengths, served_count):
    """ Set up the environment with a controlled number of arrivals. """
    machine = simpy.Resource(env, capacity=num_machines)
    employee_count = 0

    while employee_count < EXPECTED_EMPLOYEES:
        # Time-varying arrival rate with peak at the middle of the hour
        current_time = env.now
        if 0 <= current_time < 1200:  # First 20 minutes, low arrival rate
            arrival_rate = LOW_ARRIVAL_RATE
        elif 1200 <= current_time < 2400:  # Middle 20 minutes, peak arrival rate
            arrival_rate = PEAK_ARRIVAL_RATE
        else:  # Last 20 minutes, low arrival rate again
            arrival_rate = LOW_ARRIVAL_RATE

        # Time between arrivals
        yield env.timeout(random.expovariate(arrival_rate))
        employee_count += 1
        env.process(employee(env, f'Employee {employee_count}', machine, wait_times, queue_lengths, served_count))

# Run the simulation for different machine configurations
for num_machines in [1, 3, 5, 7, 10]:  # Testing with 3, 5, and 10 machines
    print(f"\n--- Simulation with {num_machines} machines ---")
    env = simpy.Environment()
    wait_times = []  # List to store wait times
    queue_lengths = []  # List to store queue lengths
    served_count = [0]  # List to hold the count of employees served

    # Set up the environment with the defined number of machines and controlled arrivals
    env.process(setup(env, num_machines, wait_times, queue_lengths, served_count))
    env.run(until=SIMULATION_DURATION)  # Run the simulation for 1 hour or until employees finish arriving

    # Calculate metrics
    avg_wait_time = sum(wait_times) / len(wait_times) if wait_times else 0
    avg_queue_length = sum(queue_lengths) / len(queue_lengths) if queue_lengths else 0
    utilization = len(wait_times) / (SIMULATION_DURATION * num_machines) * SERVICE_RATE
    throughput = served_count[0] / SIMULATION_DURATION  # Employees processed per second

    # Store results
    results['num_machines'].append(num_machines)
    results['wait_times'].append(avg_wait_time)
    results['queue_lengths'].append(avg_queue_length)
    results['utilization'].append(utilization)
    results['throughput'].append(throughput)

# Plot results
plt.figure(figsize=(12, 8))

# Plot Average Wait Time
plt.subplot(2, 2, 1)
plt.plot(results['num_machines'], results['wait_times'], marker='o', color='b')
plt.title('Average Wait Time vs Number of Machines')
plt.xlabel('Number of Machines')
plt.ylabel('Average Wait Time (seconds)')

# Plot Average Queue Length
plt.subplot(2, 2, 2)
plt.plot(results['num_machines'], results['queue_lengths'], marker='o', color='g')
plt.title('Average Queue Length vs Number of Machines')
plt.xlabel('Number of Machines')
plt.ylabel('Average Queue Length')

# Plot Utilization
plt.subplot(2, 2, 3)
plt.plot(results['num_machines'], results['utilization'], marker='o', color='r')
plt.title('Utilization vs Number of Machines')
plt.xlabel('Number of Machines')
plt.ylabel('Utilization (%)')

# Plot Throughput
plt.subplot(2, 2, 4)
plt.plot(results['num_machines'], results['throughput'], marker='o', color='purple')
plt.title('Throughput vs Number of Machines')
plt.xlabel('Number of Machines')
plt.ylabel('Throughput (employees per second)')

plt.tight_layout()
plt.show()
