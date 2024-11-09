import numpy as np
import matplotlib.pyplot as plt
from collections import deque
from scipy.stats import t
import os,sys

class Job:
    def __init__(self, job_id):
        self.job_id = job_id
        #we can put various properties of a job (that may be useful for statistical purpose)
        self.queueids = []
        self.arrival_times = []
        self.depurture_times = []
        self.service_times=[]
        self.wait_times = []
        self.sojourn_times = []
        self.overall_sojourntime = 0

    def calulate_jobstats(self):
        self.wait_times = [0] * len(self.queueids)
        self.sojourn_times = [0] * len(self.queueids)

        for i in range(len(self.queueids)):
            self.wait_times[i] = max(0, self.depurture_times[i] - self.service_times[i] - self.arrival_times[i])
            self.sojourn_times[i] = self.depurture_times[i] - self.arrival_times[i]
            self.overall_sojourntime += self.sojourn_times[i]

    def print_jobstats(self):
        print(self.queueids)
        print(f"Arrival: {self.arrival_times}")
        print(f"Wait: {self.wait_times}")
        print(f"service: {self.service_times}")
        print(f"departure: {self.depurture_times}")
        print(f"sojourn: {self.sojourn_times}")
        print(f"total sojourn: {self.overall_sojourntime}")
        

class EventType:
    def __init__(self, event_type, queueid):
        self.queueid = queueid
        self.type = event_type  # 'arrival', 'departure'
        
class Event:
    def __init__(self, time, event_type, job_id):
        self.event_time = time
        self.event_type = event_type  # 'arrival_q1', 'departure_q1', 'departure_q2'
        self.job_id = job_id # one particular job may have many events
        self.next = None
        self.prev = None

class EventStack:
    def __init__(self):
        self.head = None

    def insert_event(self, event):
        # Insert event in the event stack in sorted order by time
        if not self.head:
            self.head = event
        else:
            current = self.head
            if current.event_time > event.event_time:
                # insert at the head
                event.next = current
                current.prev = event
                self.head = event
                return
            
            while current.next and current.next.event_time <= event.event_time:
                current = current.next

            event.next = current.next
            event.prev = current
            if current.next: #not tail case
                current.next.prev = event
            current.next = event

    def pop_event(self):
        if not self.head:
            return None
        event = self.head
        self.head = self.head.next
        if self.head:
            self.head.prev = None
        return event


