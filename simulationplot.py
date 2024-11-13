import numpy as np
import matplotlib.pyplot as plt
from collections import deque
from scipy.stats import t
import os,sys
from scipy import stats

def compute_ci(sample, confidence=0.95):
    n = len(sample)
    mean = np.mean(sample)
    std_dev = np.std(sample, ddof=1)  # Sample standard deviation
    t_value = stats.t.ppf((1 + confidence) / 2, df=n - 1)  # t-value for 95% CI
    
    # Calculate the margin of error
    margin_of_error = t_value * (std_dev / np.sqrt(n))
    
    return mean, margin_of_error

def plot(configurations, poisson_means, poisson_errors, uniform_means, uniform_errors, jackson_values, ylabel):
	# Plotting
	plt.figure(figsize=(10, 6))

	plt.errorbar(configurations, poisson_means, yerr=poisson_errors, fmt='o', label='poisson(arrival=2)_simulation(95%CI)', color='blue', capsize=5)

	plt.errorbar(configurations, uniform_means, yerr=uniform_errors, fmt='^', label='uniform(arrival)_simulation(95%CI)', color='green', capsize=5)

	# Plot jackson formula values as a point for each configuration
	plt.scatter(configurations, jackson_values, color='red', marker='s', label='Jackson formulaValue', zorder=5)

	# Customizing the plot
	plt.xlabel('simulation-params')
	plt.ylabel(ylabel)
	plt.xticks(rotation=45)  # Rotate labels for better visibility
	plt.legend()
	plt.grid(True)
	plt.tight_layout()

	plt.savefig(f"plot_{ylabel}.png")
