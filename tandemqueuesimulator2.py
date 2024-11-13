import numpy as np
import matplotlib.pyplot as plt
from collections import deque
from scipy.stats import t
import os,sys
from eventstack import Event, EventStack, Job, EventType
import time


def generate_times_from_distribution(num_samples, distribution):
    distribution_type = distribution['type']
    params = distribution['params']

    if distribution_type == 'uniform':
        times = np.random.uniform(0, 1, num_samples)
    
    elif distribution_type == 'exponential':
        rate = params.get('rate', 1.0)
        uniform_samples = np.random.uniform(0, 1, num_samples)
        times = -np.log(uniform_samples) / rate

    elif distribution_type == 'erlang':
        # Erlang Distribution (sum of k exponential phases)
        rate = params.get('rate', 1.0)
        k = params.get('k', 1)
        uniform_samples = np.random.uniform(0, 1, (num_samples, k))
        times = np.sum(-np.log(uniform_samples) / rate, axis=1)

    elif distribution_type == 'hyperexponential':
        # Hyperexponential Distribution (mixture of different rates)
        rates = np.array(params.get('rates', [1.0, 2.0]))
        probs = np.array(params.get('probs', [0.5, 0.5]))
        chosen_rates = np.random.choice(rates, size=num_samples, p=probs)
        uniform_samples = np.random.uniform(0, 1, num_samples)
        times = -np.log(uniform_samples) / chosen_rates

    elif distribution_type == 'hypoexponential':
        # Hypoexponential Distribution (sequential phases with different rates)
        rates = np.array(params.get('rates', [1.0, 2.0]))
        num_phases = len(rates)
        uniform_samples = np.random.uniform(0, 1, (num_samples, num_phases))
        times = np.sum(-np.log(uniform_samples) / rates, axis=1)

    else:
        raise ValueError("Unsupported distribution type.")

    return times


class TandemQueueSimulator:
    def __init__(self, arrival_distributions, service_distributions, num_jobs, jackson, num_queues=2):
        self.arrival_rates = []
        self.service_rates = []
        
        if jackson:
            self.arrival_rates = [arrival_distribution['params'].get('rate') for arrival_distribution in arrival_distributions]
            self.service_rates = [service_distribution['params'].get('rate') for service_distribution in service_distributions]

        self.num_jobs = num_jobs
        self.num_queues = num_queues
        self.event_stack = EventStack()
        self.current_time = 0
        self.next_job_id = 0
        self.jobs = []
        self.jobsdone = 0
        self.jackson = jackson

        #for statistical purpose
        self.queue_lengths = [0] * self.num_queues
        self.prev_event_time = 0;
        self.queue_idletimes = [0] * self.num_queues
        self.time_weighted_job_counts_in_queues = [0] * self.num_queues
        self.mean_jobcounts = [0] * self.num_queues
        self.overall_mean_jobcount = 0;
        self.overall_mean_soujorntime = 0
        self.queue_utilizations = [0] * self.num_queues
        self.queue_waittimes = [0] * self.num_queues
        self.mean_soujorntime_perqueue = [0] * self.num_queues
        self.throughput = 0;

        #in tandem queues, only the first queue has external arrival
        self.inter_arrivaltimes = generate_times_from_distribution(num_jobs, arrival_distributions[0])
        self.servicetimes = [[] for _ in range(self.num_queues)]
        for i in range(self.num_queues):
            self.servicetimes[i] = generate_times_from_distribution(num_jobs, service_distributions[i])

        #jackson formulated values
        self.jackson_system_throughput = np.sum(self.arrival_rates)
        self.jackson_utilization = [0] * self.num_queues
        self.jackson_avg_queue_length = [0] * self.num_queues
        self.jackson_mean_sojourn_time_perqueue = [0] * self.num_queues
        self.jackson_avg_jobs_in_system = 0
        self.jackson_mean_sojourn_time_in_system = 0

        
    #arrival rate
    def generate_interarrival_time(self, queueid = 0):
        if self.non_poisson:
            # Non-Poisson arrival: using uniform distribution for non-Poisson arrivals
            return np.random.uniform(3.4, 5.5)  # Uniformly distributed inter-arrival times

        # Poisson arrival: Exponential inter-arrival times
        return np.random.exponential(1 / self.arrival_rates[queueid])

    #service rate
    def generate_service_time(self, queueid):
        return np.random.exponential(1 / self.service_rates[queueid])

    #simulation start
    def run_simulation(self, first_queueid=0):
        #first_arrival = self.generate_interarrival_time(first_queueid);
        first_arrival = self.inter_arrivaltimes[0]
        job = Job(self.next_job_id)
        job.queueids.append(first_queueid)
        job.arrival_times.append(first_arrival);
        self.jobs.append(job)
        
        self.event_stack.insert_event(Event(first_arrival, EventType('arrival', first_queueid), self.next_job_id))
        self.next_job_id += 1


        # we run this simulation until certain number of jobs are done
        while self.jobsdone < self.num_jobs:
            event = self.event_stack.pop_event()
            if event:
                self.current_time = event.event_time
                time_spent = self.current_time - self.prev_event_time
                self.prev_event_time = self.current_time
                self.process_event(event, time_spent)

        print(f"Simulation time: {self.current_time}")
        #calculate other stats
        for job in self.jobs:
            job.calulate_jobstats()
            #print(f"details of job {job.job_id}")
            #job.print_jobstats()
    
    def process_event(self, event, time_spent):
        #arrival case: for each arrival, schedule its deperture event. if its inital queue, then create next arrival event in the queue.
        for i in range(self.num_queues):
            self.time_weighted_job_counts_in_queues[i] += time_spent * self.queue_lengths[i]

        if event.event_type.type == 'arrival':
            event_queueid = event.event_type.queueid
            self.queue_lengths[event_queueid] += 1
            
            #determine service time in this queue
            #service_time = self.generate_service_time(event_queueid)
            service_time = self.servicetimes[event_queueid][event.job_id]
            
            self.jobs[event.job_id].service_times.append(service_time)
            self.queue_utilizations[event_queueid] += service_time

            depurture_time = self.current_time + service_time
            
            if self.queue_idletimes[event_queueid] > self.current_time:
                depurture_time = self.queue_idletimes[event_queueid] + service_time
                self.queue_waittimes[event_queueid] += (self.queue_idletimes[event_queueid] - self.current_time)

            self.queue_idletimes[event_queueid] = depurture_time

            #put deperture event of this job in this queue
            self.event_stack.insert_event(Event(depurture_time, EventType('departure', event_queueid), event.job_id))

            
            #next_arrival of job if this is the first queue
            if event_queueid == 0 and self.next_job_id < self.num_jobs:
                #next_arrival = self.generate_interarrival_time(event_queueid)
                next_arrival = self.inter_arrivaltimes[self.next_job_id]
                job = Job(self.next_job_id)
                job.queueids.append(event_queueid)
                job.arrival_times.append(self.current_time + next_arrival);
                self.jobs.append(job)
                self.event_stack.insert_event(Event(self.current_time + next_arrival, EventType('arrival', event_queueid), self.next_job_id))
                self.next_job_id += 1


        #depurture case: for each deputure, schedule a arrival time for next queue in chain unless its the end_queue=num_queue-1
        #
        elif event.event_type.type == 'departure':
            event_queueid = event.event_type.queueid
            self.queue_lengths[event_queueid] -= 1

            self.jobs[event.job_id].depurture_times.append(self.current_time)

            if event_queueid != (self.num_queues - 1):
                next_queueid = event_queueid + 1
                #put arrival event of this job in next queue
                self.event_stack.insert_event(Event(self.current_time, EventType('arrival', next_queueid), event.job_id))
                self.jobs[event.job_id].queueids.append(next_queueid)
                self.jobs[event.job_id].arrival_times.append(self.current_time)

            if event_queueid == (self.num_queues - 1):
                self.jobsdone += 1
                #print(self.jobsdone)


    def get_total_simulationtime(self):
        return self.current_time

    def calculate_statistics(self):        
        for i in range(self.num_queues):
            self.queue_utilizations[i] = self.queue_utilizations[i] / self.current_time 
            self.mean_jobcounts[i] = self.time_weighted_job_counts_in_queues[i] / self.current_time
            self.overall_mean_jobcount += self.mean_jobcounts[i]
            self.mean_soujorntime_perqueue[i] = np.mean([job.sojourn_times[i] for job in self.jobs])
       
        self.overall_mean_soujorntime = np.mean([job.overall_sojourntime for job in self.jobs])
        self.throughput = self.num_jobs/self.current_time

    def print_stats(self):
        print(f"simulation system throughput:{self.throughput}")
        for i in range(self.num_queues):
            print("simulation results: queue", i)
            print(f'Utilization: {self.queue_utilizations[i]}')
            print(f'Avg number of jobs: {self.mean_jobcounts[i]}')
            print(f'Mean sojourn_time here: {self.mean_soujorntime_perqueue[i]}')

        print(f'Avg number of jobs in the system: {self.overall_mean_jobcount}')
        print(f'Mean sojourn time in system: {self.overall_mean_soujorntime}')

    def determin_stats_with_jackson(self):
        print("\n\n\nStats using jackson formula:")
        
        print(f"system throughput:{self.jackson_system_throughput}")

        for i in range(self.num_queues):
            print("queue", i)
            #for tandem queue
            self.jackson_utilization[i] = self.arrival_rates[0]/ self.service_rates[i]
            print(f'Utilization: {self.jackson_utilization[i]}')

            self.jackson_avg_queue_length[i] = self.jackson_utilization[i] / ( 1 - self.jackson_utilization[i])
            self.jackson_avg_jobs_in_system += self.jackson_avg_queue_length[i]
            print(f'Avg number of jobs: {self.jackson_avg_queue_length[i]}')

            self.jackson_mean_sojourn_time_perqueue[i] = self.jackson_avg_queue_length[i]/self.arrival_rates[0]
            print(f'Mean sojourn_time here: {self.jackson_mean_sojourn_time_perqueue[i]}')

        self.jackson_mean_sojourn_time_in_system = self.jackson_avg_jobs_in_system/self.arrival_rates[0]
        print(f'Avg number of jobs in the system: {self.jackson_avg_jobs_in_system}')
        print(f'Mean sojourn time in system: {self.jackson_mean_sojourn_time_in_system}')


arrival_rates = [1.3]
service_rates = [2.5, 3.5]
arrival_distributions = [{'type': 'exponential', 'params': {'rate': 1.3}}]
arrival_distributions_uniform = [{'type': 'uniform', 'params': {}}]

service_distributions = [{'type': 'exponential', 'params': {'rate': 2.5}}, {'type': 'exponential', 'params': {'rate': 3.5}}]
num_jobs = 500000
num_queues = 2
# Start time
start_time = time.time()
# Run the Simulation first to verify jackson and little's formula for basic tandem queue pair
sim = TandemQueueSimulator(arrival_distributions, service_distributions, num_jobs, True, 2)
sim.run_simulation()
sim.calculate_statistics()

sim.print_stats()
sim.determin_stats_with_jackson()

# Start time
end_time = time.time()

# Duration in seconds
duration = end_time - start_time
print("\n\n\nExecution time:", duration, "seconds")