import os
import numpy as np
import matplotlib.pyplot as plt

def main():
    # Setup styles for dark theme
    plt.rcParams['text.color'] = '#f0f0f0'
    plt.rcParams['axes.labelcolor'] = '#f0f0f0'
    plt.rcParams['xtick.color'] = '#a0a0a0'
    plt.rcParams['ytick.color'] = '#a0a0a0'
    plt.rcParams['font.family'] = 'sans-serif'
    
    # Create grid for contour calculation
    delta = 0.002
    x = np.arange(-1.6, 1.6, delta)
    y = np.arange(-1.6, 1.6, delta)
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
    colors = ['#00e5ff', '#d500f9', '#ff3d00']
    fill_colors = ['rgba(0, 229, 255, 0.2)', 'rgba(213, 0, 249, 0.2)', 'rgba(255, 61, 0, 0.2)']
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), facecolor='#121212')
    
    for idx, (rho, title, color) in enumerate(zip(rhos, titles, colors)):
        ax = axes[idx]
        ax.set_facecolor('#121212')
        
        # Grid and design
        ax.grid(True, which='both', color='#2d2d2d', linestyle='--', linewidth=0.5)
        ax.set_xlim(-1.6, 1.6)
        ax.set_ylim(-1.6, 1.6)
        ax.set_aspect('equal')
        
        # Draw axes lines with arrows
        ax.annotate('', xy=(1.5, 0), xytext=(-1.5, 0),
                    arrowprops=dict(arrowstyle="->", color="#e0e0e0", lw=1.2))
        ax.annotate('', xy=(0, 1.5), xytext=(0, -1.5),
                    arrowprops=dict(arrowstyle="->", color="#e0e0e0", lw=1.2))
        
        # Draw references in dashed format for comparisons
        # Circle (Ridge)
        ax.contour(X, Y, L2, levels=[1.0], colors='#00e5ff', linestyles='dashed', linewidths=0.8, alpha=0.3)
        # Diamond (Lasso)
        ax.contour(X, Y, L1, levels=[1.0], colors='#ff3d00', linestyles='dashed', linewidths=0.8, alpha=0.3)
        
        # Draw target Elastic Net constraint region boundary
        Z = rho * L1 + (1.0 - rho) * L2
        
        # Fill the region
        ax.contourf(X, Y, Z, levels=[0.0, 1.0], colors=[color], alpha=0.15)
        # Draw contour edge
        ax.contour(X, Y, Z, levels=[1.0], colors=[color], linewidths=2.5)
        
        # Label coordinates
        ax.set_title(title, fontsize=14, pad=15, color='#ffffff', weight='bold')
        ax.text(1.55, -0.12, r"$\beta_1$", fontsize=13, color='#e0e0e0')
        ax.text(-0.12, 1.55, r"$\beta_2$", fontsize=13, color='#e0e0e0')
        
        # Add labels to intercept points on the axes
        ax.plot([1, -1, 0, 0], [0, 0, 1, -1], 'o', color='#ffffff', markersize=4, zorder=5)
        ax.text(1.05, 0.05, '1', color='#ffffff', fontsize=9)
        ax.text(0.05, 1.05, '1', color='#ffffff', fontsize=9)
        
        # Adjust spines
        for spine in ax.spines.values():
            spine.set_color('#2d2d2d')
            
    plt.suptitle("Elastic Net Constraint Geometry", fontsize=18, color='#ffffff', weight='bold', y=0.96)
    plt.tight_layout(rect=[0, 0, 1, 0.92])
    
    # Save folder
    os.makedirs('Results', exist_ok=True)
    save_path = os.path.join('Results', 'elastic_net_geometry.png')
    plt.savefig(save_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    print(f"Saved successfully to: {os.path.abspath(save_path)}")

if __name__ == '__main__':
    main()
