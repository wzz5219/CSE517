import numpy as np
import matplotlib.pyplot as plt
from collections import deque
from scipy.stats import t
import os,sys

def plot(values, num_simulations, metric_name):
	mean = np.mean(values)
	std_dev = np.std(values, ddof=1)
	confidence_level = 0.95
	z_score = 1.96  # for 95% confidence interval
	margin_of_error = z_score * (std_dev / np.sqrt(num_simulations))  # Margin of error
	ci_lower = mean - margin_of_error
	ci_upper = mean + margin_of_error

	# Plotting the results with confidence interval
	plt.figure(figsize=(10, 6))
	plt.hist(values, bins=10, alpha=0.7, color='lightblue', edgecolor='black')
	plt.axvline(mean, color='red', linestyle='--', label=f"Mean = {mean:.2f}")
	plt.axvline(ci_lower, color='green', linestyle='--', label=f"95% CI Lower = {ci_lower:.2f}")
	plt.axvline(ci_upper, color='green', linestyle='--', label=f"95% CI Upper = {ci_upper:.2f}")
	plt.xlabel(metric_name)
	plt.ylabel('Frequency')
	plt.title(f'{metric_name} with 95% Confidence Interval')
	plt.legend()
	#plt.show()
	plt.savefig(f"plot_{metric_name}.png")

	# Print the statistics
	print(f"{metric_name}: {mean:.2f}")
	print(f"95% Confidence Interval: ({ci_lower:.2f}, {ci_upper:.2f})")