import numpy as np
import matplotlib.pyplot as plt
from collections import deque
from scipy.stats import t
import os,sys
from eventstack import Event, EventStack, Job
from tandemqueuesimulator2 import TandemQueueSimulator
import simulationplot

arrival_distributions = [{'type': 'exponential', 'params': {'rate': 2}}]
arrival_distributions_uniform = [{'type': 'uniform', 'params': {}}]

different_service_distributions = [[{'type': 'exponential', 'params': {'rate': 4}}, {'type': 'exponential', 'params': {'rate': 3.5}}],
		[{'type': 'exponential', 'params': {'rate': 3.5}}, {'type': 'exponential', 'params': {'rate': 4}}],
		[{'type': 'exponential', 'params': {'rate': 4.5}}, {'type': 'exponential', 'params': {'rate': 4.5}}]]

num_jobs = 500000
num_queues = 2
num_simulations = 20


jackson_values_avg_num_jobs_system = []
poisson_means_avg_num_jobs_system = []
poisson_errors_avg_num_jobs_system = []
uniform_means_avg_num_jobs_system = []
uniform_errors_avg_num_jobs_system = []

jackson_values_mean_sojourntime_system = []
poisson_means_mean_sojourntime_system = []
poisson_errors_mean_sojourntime_system = []
uniform_means_mean_sojourntime_system = []
uniform_errors_mean_sojourntime_system = []


jackson_values_throughput = []
poisson_means_throughput = []
poisson_errors_throughput = []
uniform_means_throughput = []
uniform_errors_throughput = []

#per queue checks

jackson_values_utilization = [[] for _ in range(0, num_queues)]
poisson_means_utilization = [[] for _ in range(0, num_queues)]
poisson_errors_utilization = [[] for _ in range(0, num_queues)]
uniform_means_utilization = [[] for _ in range(0, num_queues)]
uniform_errors_utilization = [[] for _ in range(0, num_queues)]

jackson_values_mean_jobs_per_queue = [[] for _ in range(0, num_queues)]
poisson_means_mean_jobs_per_queue = [[] for _ in range(0, num_queues)]
poisson_errors_mean_jobs_per_queue = [[] for _ in range(0, num_queues)]
uniform_means_mean_jobs_per_queue = [[] for _ in range(0, num_queues)]
uniform_errors_mean_jobs_per_queue = [[] for _ in range(0, num_queues)]

for i in range(len(different_service_distributions)): 
	sim = TandemQueueSimulator(arrival_distributions, different_service_distributions[i], num_jobs, True, num_queues)
	sim.run_simulation()
	sim.calculate_statistics()
	sim.determin_stats_with_jackson()
	jackson_values_avg_num_jobs_system.append(sim.jackson_avg_jobs_in_system)
	jackson_values_mean_sojourntime_system.append(sim.jackson_mean_sojourn_time_in_system)
	jackson_values_throughput.append(sim.jackson_system_throughput)

	for k in range(sim.num_queues):
		jackson_values_utilization[k].append(sim.jackson_utilization[k])
		jackson_values_mean_jobs_per_queue[k].append(sim.jackson_avg_queue_length[k])


for i in range(len(different_service_distributions)): 
	poisson_values_simulations_avg_num_jobs_system = []
	poisson_values_simulations_mean_sojourntime_system = []
	poisson_values_simulations_throughput = []
	poisson_values_simulations_utilization = [[] for _ in range(0, num_queues)]
	poisson_values_simulations_mean_jobs_per_queue = [[] for _ in range(0, num_queues)]

	for j in range(0, num_simulations):
		sim = TandemQueueSimulator(arrival_distributions, different_service_distributions[i], num_jobs, True, num_queues)
		sim.run_simulation()
		sim.calculate_statistics()
		poisson_values_simulations_avg_num_jobs_system.append(sim.overall_mean_jobcount)
		poisson_values_simulations_mean_sojourntime_system.append(sim.overall_mean_soujorntime)
		poisson_values_simulations_throughput.append(sim.throughput)

		for k in range(sim.num_queues):
			poisson_values_simulations_utilization[k].append(sim.queue_utilizations[k])
			poisson_values_simulations_mean_jobs_per_queue[k].append(sim.mean_jobcounts[k])			

	mean, error = simulationplot.compute_ci(poisson_values_simulations_avg_num_jobs_system, 0.95)
	poisson_means_avg_num_jobs_system.append(mean)
	poisson_errors_avg_num_jobs_system.append(error)

	mean, error = simulationplot.compute_ci(poisson_values_simulations_mean_sojourntime_system, 0.95)
	poisson_means_mean_sojourntime_system.append(mean)
	poisson_errors_mean_sojourntime_system.append(error)

	mean, error = simulationplot.compute_ci(poisson_values_simulations_throughput, 0.95)
	poisson_means_throughput.append(mean)
	poisson_errors_throughput.append(error)

	for k in range(sim.num_queues):
		mean, error = simulationplot.compute_ci(poisson_values_simulations_utilization[k], 0.95)
		poisson_means_utilization[k].append(mean)
		poisson_errors_utilization[k].append(error)

		mean, error = simulationplot.compute_ci(poisson_values_simulations_mean_jobs_per_queue[k], 0.95)
		poisson_means_mean_jobs_per_queue[k].append(mean)
		poisson_errors_mean_jobs_per_queue[k].append(error)
	
for i in range(len(different_service_distributions)): 
	uniform_values_simulations_avg_num_jobs_system = []
	uniform_values_simulations_mean_sojourntime_system = []
	uniform_values_simulations_throughput = []
	uniform_values_simulations_utilization = [[] for _ in range(0, num_queues)]
	uniform_values_simulations_mean_jobs_per_queue = [[] for _ in range(0, num_queues)]

	for j in range(0, num_simulations):
		sim = TandemQueueSimulator(arrival_distributions_uniform, different_service_distributions[i], num_jobs, False, num_queues)
		sim.run_simulation()
		sim.calculate_statistics()
		uniform_values_simulations_avg_num_jobs_system.append(sim.overall_mean_jobcount)
		uniform_values_simulations_mean_sojourntime_system.append(sim.overall_mean_soujorntime)
		uniform_values_simulations_throughput.append(sim.throughput)

		for k in range(sim.num_queues):
			uniform_values_simulations_utilization[k].append(sim.queue_utilizations[k])	
			uniform_values_simulations_mean_jobs_per_queue[k].append(sim.mean_jobcounts[k])			

	mean, error = simulationplot.compute_ci(uniform_values_simulations_avg_num_jobs_system, 0.95)
	uniform_means_avg_num_jobs_system.append(mean)
	uniform_errors_avg_num_jobs_system.append(error)

	mean, error = simulationplot.compute_ci(uniform_values_simulations_mean_sojourntime_system, 0.95)
	uniform_means_mean_sojourntime_system.append(mean)
	uniform_errors_mean_sojourntime_system.append(error)

	mean, error = simulationplot.compute_ci(uniform_values_simulations_throughput, 0.95)
	uniform_means_throughput.append(mean)
	uniform_errors_throughput.append(error)

	for k in range(sim.num_queues):
		mean, error = simulationplot.compute_ci(uniform_values_simulations_utilization[k], 0.95)
		uniform_means_utilization[k].append(mean)
		uniform_errors_utilization[k].append(error)

		mean, error = simulationplot.compute_ci(uniform_values_simulations_mean_jobs_per_queue[k], 0.95)
		uniform_means_mean_jobs_per_queue[k].append(mean)
		uniform_errors_mean_jobs_per_queue[k].append(error)




configurations = ["ServiceRate(4, 3.5)", "ServiceRate(3.5,4)", "ServiceRate(4.5,4.5)"]
ylabel = "Avg number of jobs in the system"
simulationplot.plot(configurations, poisson_means_avg_num_jobs_system, poisson_errors_avg_num_jobs_system, uniform_means_avg_num_jobs_system, uniform_errors_avg_num_jobs_system, jackson_values_avg_num_jobs_system, ylabel)

ylabel = "Mean sojourn time in the system"
simulationplot.plot(configurations, poisson_means_mean_sojourntime_system, poisson_errors_mean_sojourntime_system, uniform_means_mean_sojourntime_system, uniform_errors_mean_sojourntime_system, jackson_values_mean_sojourntime_system, ylabel)

ylabel = "System throughput"
simulationplot.plot(configurations, poisson_means_throughput, poisson_errors_throughput, uniform_means_throughput, uniform_errors_throughput, jackson_values_throughput, ylabel)

for k in range(0, num_queues):
	ylabel = f"Mean job in Queue{k}"
	simulationplot.plot(configurations, poisson_means_mean_jobs_per_queue[k], poisson_errors_mean_jobs_per_queue[k], uniform_means_mean_jobs_per_queue[k], uniform_errors_mean_jobs_per_queue[k], jackson_values_mean_jobs_per_queue[k], ylabel)

	ylabel = f"Utilization of Queue{k}"
	simulationplot.plot(configurations, poisson_means_utilization[k], poisson_errors_utilization[k], uniform_means_utilization[k], uniform_errors_utilization[k], jackson_values_utilization[k], ylabel)
