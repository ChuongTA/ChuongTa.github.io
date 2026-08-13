import os
import numpy as np
import matplotlib.pyplot as plt

def draw_geometry_plots():
    # Setup styles for light theme (white background)
    plt.rcParams['text.color'] = '#1e1e1e'
    plt.rcParams['axes.labelcolor'] = '#1e1e1e'
    plt.rcParams['xtick.color'] = '#555555'
    plt.rcParams['ytick.color'] = '#555555'
    plt.rcParams['font.family'] = 'sans-serif'
    
    # Create grid for contour calculation (increased range to prevent clipping)
    delta = 0.002
    x = np.arange(-1.8, 1.8, delta)
    y = np.arange(-1.8, 1.8, delta)
    X, Y = np.meshgrid(x, y)
    
    # Compute standard functions
    L1 = np.abs(X) + np.abs(Y)
    L2 = X**2 + Y**2
    
    rhos = [0.0, 0.3, 1.0]
    titles = [
        r"$\rho = 0$ (Ridge / $L_2$)",
        r"$\rho = 0.3$ (Elastic Net)",
        r"$\rho = 1$ (Lasso / $L_1$)"
    ]
    colors = ['#0288d1', '#8e24aa', '#d32f2f']
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), facecolor='#ffffff')
    
    for idx, (rho, title, color) in enumerate(zip(rhos, titles, colors)):
        ax = axes[idx]
        ax.set_facecolor('#ffffff')
        
        # Grid and design
        ax.grid(True, which='both', color='#e0e0e0', linestyle='--', linewidth=0.5)
        # Shift limits outwards to give margins breathing room
        ax.set_xlim(-1.8, 1.8)
        ax.set_ylim(-1.8, 1.8)
        ax.set_aspect('equal')
        
        # Draw axes lines with arrows (slightly scaled back from limits to look natural)
        ax.annotate('', xy=(1.7, 0), xytext=(-1.7, 0),
                    arrowprops=dict(arrowstyle="->", color="#2d2d2d", lw=1.2))
        ax.annotate('', xy=(0, 1.7), xytext=(0, -1.7),
                    arrowprops=dict(arrowstyle="->", color="#2d2d2d", lw=1.2))
        
        # Draw references in dashed format for comparisons
        ax.contour(X, Y, L2, levels=[1.0], colors='#0288d1', linestyles='dashed', linewidths=0.8, alpha=0.3)
        ax.contour(X, Y, L1, levels=[1.0], colors='#d32f2f', linestyles='dashed', linewidths=0.8, alpha=0.3)
        
        # Draw target Elastic Net constraint region boundary
        Z = rho * L1 + (1.0 - rho) * L2
        
        # Fill the region
        ax.contourf(X, Y, Z, levels=[0.0, 1.0], colors=[color], alpha=0.12)
        ax.contour(X, Y, Z, levels=[1.0], colors=[color], linewidths=2.5)
        
        # Label coordinates (shifted to avoid overlap with margins/arrows)
        ax.set_title(title, fontsize=14, pad=15, color='#1e1e1e', weight='bold')
        ax.text(1.72, -0.15, r"$\beta_1$", fontsize=13, color='#1e1e1e')
        ax.text(-0.15, 1.72, r"$\beta_2$", fontsize=13, color='#1e1e1e')
        
        # Add labels to intercept points on the axes
        ax.plot([1, -1, 0, 0], [0, 0, 1, -1], 'o', color='#1e1e1e', markersize=4, zorder=5)
        ax.text(1.05, 0.05, '1', color='#1e1e1e', fontsize=9)
        ax.text(0.05, 1.05, '1', color='#1e1e1e', fontsize=9)
        
        # Adjust spines
        for spine in ax.spines.values():
            spine.set_color('#cccccc')
            
    plt.suptitle("Elastic Net Constraint Geometry", fontsize=18, color='#1e1e1e', weight='bold', y=0.96)
    plt.tight_layout(rect=[0, 0, 1, 0.92])
    
    os.makedirs('Results', exist_ok=True)
    save_path = os.path.join('Results', 'elastic_net_geometry.png')
    plt.savefig(save_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)
    print(f"Geometry plot saved successfully to: {os.path.abspath(save_path)}")

def draw_bracket(ax, x_start, x_end, y_val, label, offset=0.05):
    ax.plot([x_start, x_end], [y_val - offset, y_val - offset], color='#555555', lw=1.2)
    ax.plot([x_start, x_start], [y_val - offset, y_val - offset + 0.02], color='#555555', lw=1.2)
    ax.plot([x_end, x_end], [y_val - offset, y_val - offset + 0.02], color='#555555', lw=1.2)
    x_mid = (x_start + x_end) / 2.0
    ax.plot([x_mid, x_mid], [y_val - offset, y_val - offset - 0.02], color='#555555', lw=1.2)
    ax.text(x_mid, y_val - offset - 0.04, label, ha='center', va='top', fontsize=11, color='#e65100', weight='bold')

def draw_grouped_selection_plots():
    indices = np.arange(9)
    
    true_coefs = np.zeros(9)
    true_coefs[1:4] = [0.70, 0.65, 0.60]
    true_coefs[5:8] = [0.48, 0.44, 0.40]
    
    lasso_coefs = np.zeros(9)
    lasso_coefs[1] = 0.72
    lasso_coefs[5] = 0.50
    
    en_coefs = np.zeros(9)
    en_coefs[1:4] = [0.52, 0.48, 0.45]
    en_coefs[5:8] = [0.36, 0.33, 0.30]
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), facecolor='#ffffff')
    
    titles = ["True coefficients", "Lasso picks one per group", "Elastic Net keeps the group"]
    data_sets = [true_coefs, lasso_coefs, en_coefs]
    colors = ['#0288d1', '#2e7d32', '#8e24aa']
    
    for idx, (ax, title, data, color) in enumerate(zip(axes, titles, data_sets, colors)):
        ax.set_facecolor('#ffffff')
        ax.bar(indices, data, color=color, width=0.7, edgecolor=color, alpha=0.85, zorder=3)
        ax.grid(axis='y', linestyle='--', linewidth=0.5, color='#e0e0e0')
        ax.set_xlim(-0.5, 8.5)
        ax.set_ylim(-0.25, 0.9)
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#555555')
        ax.spines['bottom'].set_color('#555555')
        
        ax.set_ylabel(r"$\beta_j$", fontsize=14, rotation=0, labelpad=15)
        ax.set_xlabel("Features", fontsize=12, labelpad=10)
        ax.set_title(title, fontsize=14, pad=15, weight='bold')
        
        ax.set_xticks(indices)
        ax.set_xticklabels([f"F{i+1}" for i in range(9)])
        ax.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8])
        
        if idx == 0:
            draw_bracket(ax, 0.7, 3.3, 0.0, "Group A")
            draw_bracket(ax, 4.7, 7.3, 0.0, "Group B")
            
    plt.suptitle("The Grouped Selection: Lasso vs Elastic Net", fontsize=18, color='#1e1e1e', weight='bold', y=0.96)
    plt.tight_layout(rect=[0, 0, 1, 0.92])
    
    os.makedirs('Results', exist_ok=True)
    save_path = os.path.join('Results', 'grouped_selection.png')
    plt.savefig(save_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)
    print(f"Grouped selection plot saved successfully to: {os.path.abspath(save_path)}")

def main():
    draw_geometry_plots()
    draw_grouped_selection_plots()

if __name__ == '__main__':
    main()
