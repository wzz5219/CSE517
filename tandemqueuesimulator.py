import numpy as np
import matplotlib.pyplot as plt
from collections import deque
from scipy.stats import t
import os,sys
from eventstack import Event, EventStack, Job, EventType

class TandemQueueSimulator:
    def __init__(self, arrival_rates, service_rates, num_jobs, non_poisson, num_queues=2):
        self.arrival_rates = arrival_rates
        self.service_rates = service_rates
        self.num_jobs = num_jobs
        self.num_queues = num_queues
        self.event_stack = EventStack()
        self.queues = [deque() for _ in range(num_queues)]
        self.current_time = 0
        self.next_job_id = 0
        self.jobs = []
        self.jobsdone = 0
        self.non_poisson = non_poisson

        #for statistical purpose
        self.queue_lengths = [0] * self.num_queues
        self.prev_event_time = 0;
        self.queue_idletimes = [0] * self.num_queues
        self.weighted_job_counts_in_queues = [0] * self.num_queues
        self.mean_jobcounts = [0] * self.num_queues
        self.overall_mean_jobcount = 0;
        self.overall_mean_soujorntime = 0
        self.queue_utilizations = [0] * self.num_queues
        self.queue_waittimes = [0] * self.num_queues
        self.mean_soujorntime_perqueue = [0] * self.num_queues
        self.throughput = 0;
        
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
        first_arrival = self.generate_interarrival_time(first_queueid);
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
            self.weighted_job_counts_in_queues[i] += time_spent * self.queue_lengths[i]

        if event.event_type.type == 'arrival':
            event_queueid = event.event_type.queueid
            self.queue_lengths[event_queueid] += 1
            
            #determine service time in this queue
            service_time = self.generate_service_time(event_queueid)
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
                next_arrival = self.generate_interarrival_time(event_queueid)
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

    def calculate_statistics(self):
        
        for i in range(self.num_queues):
            self.queue_utilizations[i] = self.queue_utilizations[i] / self.current_time 
            self.mean_jobcounts[i] = self.weighted_job_counts_in_queues[i] / self.current_time
            self.overall_mean_jobcount += self.mean_jobcounts[i]
            self.mean_soujorntime_perqueue[i] = np.mean([job.sojourn_times[i] for job in self.jobs])
        '''
        print("details of weighted_job_counts_in_queues")
        print(self.weighted_job_counts_in_queues)
        print("details of avg_job_counts_in_queues")
        print(self.mean_jobcounts)
        '''
        
        self.overall_mean_soujorntime = np.mean([job.overall_sojourntime for job in self.jobs])

        #verifying jackson formula
        print(f"Simulation time: {self.current_time}")

        if not self.non_poisson:
            print("jackson verification")
            for i in range(self.num_queues):
                print("queue", i)
                print("verifying utilization")
                jackson_utilization = self.arrival_rates[0]/ self.service_rates[i]
                print(self.queue_utilizations[i])
                print(jackson_utilization)

                print("verifying avg queue length/jobs")
                jackson_avg_queue_length_i = jackson_utilization / ( 1 - jackson_utilization)
                print(self.mean_jobcounts[i])
                print(jackson_avg_queue_length_i)

                print("verifying mean sojourn time")
                jackson_mean_sojourn_i = 1 / (self.service_rates[i] - self.arrival_rates[0])
                print(self.mean_soujorntime_perqueue[i])
                print(jackson_mean_sojourn_i)

                print("verifying little's formula")
                little_lhs_i = self.mean_jobcounts[i];
                little_rhs_i = self.mean_soujorntime_perqueue[i] * self.arrival_rates[0];
                print(little_lhs_i)
                print(little_rhs_i)
            
            #system  wide thoruhput should match initial arrival_rate
            print("\n\nsystem  wide thoruhput should match initial arrival_rate")
            self.throughput = self.current_time/self.num_jobs
            print(1/self.arrival_rates[0])
            print(self.throughput)




