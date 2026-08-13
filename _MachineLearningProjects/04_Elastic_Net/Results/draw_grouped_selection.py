import os
import numpy as np
import matplotlib.pyplot as plt

def draw_bracket(ax, x_start, x_end, y_val, label, offset=0.05):
    # Draw bracket line
    ax.plot([x_start, x_end], [y_val - offset, y_val - offset], color='#555555', lw=1.2)
    # Ticks upward at the edges
    ax.plot([x_start, x_start], [y_val - offset, y_val - offset + 0.02], color='#555555', lw=1.2)
    ax.plot([x_end, x_end], [y_val - offset, y_val - offset + 0.02], color='#555555', lw=1.2)
    # Center tick downward pointing to label
    x_mid = (x_start + x_end) / 2.0
    ax.plot([x_mid, x_mid], [y_val - offset, y_val - offset - 0.02], color='#555555', lw=1.2)
    # Add label text
    ax.text(x_mid, y_val - offset - 0.04, label, ha='center', va='top', fontsize=11, color='#e65100', weight='bold')

def main():
    # Set light theme parameters
    plt.rcParams['text.color'] = '#1e1e1e'
    plt.rcParams['axes.labelcolor'] = '#1e1e1e'
    plt.rcParams['xtick.color'] = '#555555'
    plt.rcParams['ytick.color'] = '#555555'
    plt.rcParams['font.family'] = 'sans-serif'
    
    # Feature indices
    indices = np.arange(9)
    
    # True coefficients
    true_coefs = np.zeros(9)
    true_coefs[1:4] = [0.70, 0.65, 0.60]  # Group A
    true_coefs[5:8] = [0.48, 0.44, 0.40]  # Group B
    
    # Lasso coefficients (selects only one per group)
    lasso_coefs = np.zeros(9)
    lasso_coefs[1] = 0.72  # Active from Group A
    lasso_coefs[5] = 0.50  # Active from Group B
    
    # Elastic Net coefficients (retains group structure with shrinkage)
    en_coefs = np.zeros(9)
    en_coefs[1:4] = [0.52, 0.48, 0.45]  # Group A retained
    en_coefs[5:8] = [0.36, 0.33, 0.30]  # Group B retained
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), facecolor='#ffffff')
    
    # Common configurations
    titles = ["True coefficients", "Lasso picks one per group", "Elastic Net keeps the group"]
    data_sets = [true_coefs, lasso_coefs, en_coefs]
    colors = ['#0288d1', '#2e7d32', '#8e24aa']  # Blue, Green, Purple
    
    for idx, (ax, title, data, color) in enumerate(zip(axes, titles, data_sets, colors)):
        ax.set_facecolor('#ffffff')
        
        # Plot bars
        ax.bar(indices, data, color=color, width=0.7, edgecolor=color, alpha=0.85, zorder=3)
        
        # Grid and axes
        ax.grid(axis='y', linestyle='--', linewidth=0.5, color='#e0e0e0')
        ax.set_xlim(-0.5, 8.5)
        ax.set_ylim(-0.25, 0.9)
        
        # Customize spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#555555')
        ax.spines['bottom'].set_color('#555555')
        
        # Labels and ticks
        ax.set_ylabel(r"$\beta_j$", fontsize=14, rotation=0, labelpad=15)
        ax.set_xlabel("Features", fontsize=12, labelpad=10)
        ax.set_title(title, fontsize=14, pad=15, weight='bold')
        
        # Set ticks
        ax.set_xticks(indices)
        ax.set_xticklabels([f"F{i+1}" for i in range(9)])
        ax.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8])
        
        # Draw group brackets on the first panel (True coefficients)
        if idx == 0:
            draw_bracket(ax, 0.7, 3.3, 0.0, "Group A")
            draw_bracket(ax, 4.7, 7.3, 0.0, "Group B")
            
    plt.suptitle("The Grouped Selection: Lasso vs Elastic Net", fontsize=18, color='#1e1e1e', weight='bold', y=0.96)
    plt.tight_layout(rect=[0, 0, 1, 0.92])
    
    # Save image
    os.makedirs('Results', exist_ok=True)
    save_path = os.path.join('Results', 'grouped_selection.png')
    plt.savefig(save_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    print(f"Saved successfully to: {os.path.abspath(save_path)}")

if __name__ == '__main__':
    main()
