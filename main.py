import numpy as np
import matplotlib.pyplot as plt
from collections import deque
from scipy.stats import t
import os,sys
from eventstack import Event, EventStack, Job
from tandemqueuesimulator import TandemQueueSimulator
import simulationplot

# Simulation Parameters
print("simulations with poisson 1.0")
arrival_rates = [1.0]
service_rates = [1.5, 1.2]
num_jobs = 50000
num_queues = 2

# Run the Simulation first to verify jackson and little's formula for basic tandem queue pair
sim = TandemQueueSimulator(arrival_rates, service_rates, num_jobs, False, 2)
sim.run_simulation()
sim.calculate_statistics()

simulations = []
num_simulations = 20
for i in range(0, num_simulations):
	sim_i = TandemQueueSimulator(arrival_rates, service_rates, num_jobs, False, 2)
	simulations.append(sim_i)
	simulations[i].run_simulation()
	simulations[i].calculate_statistics()

for i in range (num_queues):
	#plot mean_sojourntime
	values = [simulation.mean_soujorntime_perqueue[i] for simulation in simulations]
	metric_name = f"Mean sojourn time at Queue {i} for poisson-arrival(1.0), service_rate(1.5, 1.2)"
	simulationplot.plot(values, num_simulations, metric_name)

	#plot mean_number of jobs
	values = [simulation.mean_jobcounts[i] for simulation in simulations]
	metric_name = f"Mean number of jobs at Queue {i} for poisson-arrival(1.0), service_rate(1.5, 1.2)"
	simulationplot.plot(values, num_simulations, metric_name)

	#plot queue_utilization
	values = [simulation.queue_utilizations[i] for simulation in simulations]
	metric_name = f"Utilization at Queue {i} for poisson-arrival(1.0), service_rate(1.5, 1.2)"
	simulationplot.plot(values, num_simulations, metric_name)

#now, do the experiment with non-poisson arrival rate
simulations = []
for i in range(0, num_simulations):
	sim_i = TandemQueueSimulator(arrival_rates, service_rates, num_jobs, True, 2)
	simulations.append(sim_i)
	simulations[i].run_simulation()
	simulations[i].calculate_statistics()

for i in range (num_queues):
	#plot mean_sojourntime
	values = [simulation.mean_soujorntime_perqueue[i] for simulation in simulations]
	metric_name = f"Mean sojourn time at Queue {i} for non-poisson-arrival, service_rate(1.5, 1.2)"
	simulationplot.plot(values, num_simulations, metric_name)

	#plot mean_number of jobs
	values = [simulation.mean_jobcounts[i] for simulation in simulations]
	metric_name = f"Mean number of jobs at Queue {i} for non-poisson-arrival, service_rate(1.5, 1.2)"
	simulationplot.plot(values, num_simulations, metric_name)

	#plot queue_utilization
	values = [simulation.queue_utilizations[i] for simulation in simulations]
	metric_name = f"Utilization at Queue {i} for non-poisson-arrival, service_rate(1.5, 1.2)"
	simulationplot.plot(values, num_simulations, metric_name)


# Experiment with new simulation Parameters
print("simulations with poisson 2.0")
arrival_rates = [2.0]
service_rates = [2.5, 2.2]


# Run the Simulation first to verify jackson and little's formula for basic tandem queue pair
sim = TandemQueueSimulator(arrival_rates, service_rates, num_jobs, False, 2)
sim.run_simulation()
sim.calculate_statistics()

simulations = []
for i in range(0, num_simulations):
	sim_i = TandemQueueSimulator(arrival_rates, service_rates, num_jobs, False, 2)
	simulations.append(sim_i)
	simulations[i].run_simulation()
	simulations[i].calculate_statistics()

for i in range (num_queues):
	#plot mean_sojourntime
	values = [simulation.mean_soujorntime_perqueue[i] for simulation in simulations]
	metric_name = f"Mean sojourn time at Queue {i} for poisson-arrival(2.0), service_rate(2.5, 2.2)"
	simulationplot.plot(values, num_simulations, metric_name)

	#plot mean_number of jobs
	values = [simulation.mean_jobcounts[i] for simulation in simulations]
	metric_name = f"Mean number of jobs at Queue {i} for poisson-arrival(2.0), service_rate(2.5, 2.2)"
	simulationplot.plot(values, num_simulations, metric_name)

	#plot queue_utilization
	values = [simulation.queue_utilizations[i] for simulation in simulations]
	metric_name = f"Utilization at Queue {i} for poisson-arrival(2.0), service_rate(2.5, 2.2)"
	simulationplot.plot(values, num_simulations, metric_name)

#now, do the experiment with non-poisson arrival rate
simulations = []
for i in range(0, num_simulations):
	sim_i = TandemQueueSimulator(arrival_rates, service_rates, num_jobs, True, 2)
	simulations.append(sim_i)
	simulations[i].run_simulation()
	simulations[i].calculate_statistics()

for i in range (num_queues):
	#plot mean_sojourntime
	values = [simulation.mean_soujorntime_perqueue[i] for simulation in simulations]
	metric_name = f"Mean sojourn time at Queue {i} for non-poisson-arrival, service_rate(2.5, 2.2)"
	simulationplot.plot(values, num_simulations, metric_name)

	#plot mean_number of jobs
	values = [simulation.mean_jobcounts[i] for simulation in simulations]
	metric_name = f"Mean number of jobs at Queue {i} for non-poisson-arrival, service_rate(2.5, 2.2)"
	simulationplot.plot(values, num_simulations, metric_name)

	#plot queue_utilization
	values = [simulation.queue_utilizations[i] for simulation in simulations]
	metric_name = f"Utilization at Queue {i} for non-poisson-arrival, service_rate(2.5, 2.2)"
	simulationplot.plot(values, num_simulations, metric_name)


	