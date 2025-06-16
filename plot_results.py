import json
import matplotlib.pyplot as plt
import numpy as np

def plot_optimization_results(log_file="optimizer_results/optimization_log.json"):
    """
    Reads the optimization log and plots the success rate vs. intensity.
    """
    print(f"--- PLOTTING RESULTS FROM {log_file} ---")
    
    try:
        with open(log_file, 'r') as f:
            results = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Log file not found at '{log_file}'.")
        print("Please run the optimizer.py script first to generate the log.")
        return
    except json.JSONDecodeError:
        print(f"ERROR: Could not read the log file. It might be empty or corrupted.")
        return

    # Convert dictionary keys (str) to float for sorting and plotting
    intensities = sorted([float(k) for k in results.keys()])
    success_rates = [results[str(k)] for k in intensities]
    
    # Convert intensity to percentage for the x-axis labels
    intensity_percentages = [i * 100 for i in intensities]
    
    # --- Create the Plot ---
    plt.style.use('seaborn-v0_8-darkgrid') # Use a professional, dark-themed style
    fig, ax = plt.subplots(figsize=(12, 7)) # Create a figure and an axes object

    # Plot the main data line
    ax.plot(intensity_percentages, success_rates, marker='o', linestyle='-', color='cyan', label='Success Rate')

    # Find and highlight the optimal point
    best_rate = max(success_rates)
    best_intensity_pct = intensity_percentages[success_rates.index(best_rate)]
    ax.plot(best_intensity_pct, best_rate, 'o', markersize=12, color='magenta', label=f'Peak Performance ({best_rate:.2f}%)')
    
    # Add annotations and labels
    ax.set_title('ACE V2 Engine: Adversarial Success Rate vs. Mask Intensity', fontsize=16, fontweight='bold')
    ax.set_xlabel('Mask Intensity (%)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Dual Kill Success Rate (%)', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    
    # Set axis limits and ticks
    ax.set_xlim(min(intensity_percentages) - 5, max(intensity_percentages) + 5)
    ax.set_ylim(min(success_rates) - 5, 105) # Go up to 105 for better top margin
    ax.set_xticks(intensity_percentages)
    plt.xticks(rotation=45)

    # Add a horizontal line at our 90% goal
    ax.axhline(y=90, color='lime', linestyle='--', label='90% Dominance Threshold')
    ax.legend() # Redraw legend to include the new line

    # Add text to highlight the "Breaking Point"
    ax.text(45, 80, 'The "Breaking Point"\n(Catastrophic AI Failure)', 
            horizontalalignment='center', color='yellow', fontsize=11, style='italic')
    ax.annotate('', xy=(55, 95), xytext=(45, 85),
                arrowprops=dict(facecolor='yellow', shrink=0.05, width=1, headwidth=8))


    # Save and show the plot
    output_filename = "optimizer_results/performance_graph.png"
    plt.tight_layout()
    plt.savefig(output_filename, dpi=300)
    print(f"Graph saved to '{output_filename}'")
    
    plt.show()


if __name__ == '__main__':
    # You might need to install matplotlib if you haven't already:
    # pip install matplotlib
    plot_optimization_results()