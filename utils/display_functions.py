import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
import pandas as pd 

def display_palette(selected_colors: list[int], color_df: pd.DataFrame, filepath: str, cols=None):

    hex_colors = [color_df.iloc[c]['Hex'] for c in selected_colors]
    color_names = [color_df.iloc[c]['Color Name'] for c in selected_colors]

    n = len(hex_colors)
    # Default to square-ish grid
    if cols is None:
        cols = int(n ** 0.5) + (1 if n % int(n ** 0.5) else 0)
    rows = (n + cols - 1) // cols
    
    fig, ax = plt.subplots(rows, cols, figsize=(cols * 1.5, rows * 1.5))
    
    # Handle case where we only have 1 subplot
    if rows == 1 and cols == 1:
        ax = [[ax]]
    elif rows == 1 or cols == 1:
        ax = ax.reshape(rows, cols)
    
    for idx, hex_color in enumerate(hex_colors):
        row = idx // cols
        col = idx % cols
        subplot_ax = ax[row, col]
        
        rect = patches.Rectangle((0, 0), 1, 1, facecolor='#'+hex_color)
        subplot_ax.add_patch(rect)
        
        if color_names:
            subplot_ax.text(0.5, -0.1, color_names[idx], ha='center', va='top', 
                           fontsize=8, fontweight='bold')
        
        subplot_ax.set_xlim(0, 1)
        subplot_ax.set_ylim(-0.2 if color_names else 0, 1)
        subplot_ax.set_aspect('equal')
        subplot_ax.axis('off')
    
    # Hide empty subplots
    for idx in range(n, rows * cols):
        row = idx // cols
        col = idx % cols
        ax[row, col].axis('off')
    
    plt.tight_layout()
    plt.savefig(filepath)


def plot_distance_heatmap(selected_colors: list[int], distance_matrix, color_df: pd.DataFrame, filepath: str):
    n = len(selected_colors)
    names = [color_df.iloc[c]['Color Name'] + " "*7 for c in selected_colors]
    hex_colors = [color_df.iloc[c]['Hex'] for c in selected_colors]
    
    # Build distance matrix for selected colors
    matrix = []
    for i in selected_colors:
        row = []
        for j in selected_colors:
            if i == j:
                row.append(0)
            else:
                dist = distance_matrix.get((i, j)) or distance_matrix.get((j, i), 0)
                row.append(dist)
        matrix.append(row)
    
    fig, ax = plt.subplots(figsize=(14, 12))
    sns.heatmap(matrix, xticklabels=names, yticklabels=names, 
                annot=True, fmt='.1f', cmap='RdYlGn', 
                vmin=0, vmax=60, cbar_kws={'label': 'Color Difference (ΔE)'},
                ax=ax)
    
    # Add color swatches to y-axis (left side)
    for i, hex_color in enumerate(hex_colors):
        rect = patches.Rectangle((-0.04, (n - i - 1) / n), 0.03, 1 / n, 
                                  facecolor='#' + hex_color, edgecolor='black', linewidth=0.5,
                                  transform=ax.transAxes, clip_on=False)
        ax.add_patch(rect)
    
    # Add color swatches to x-axis (top side) - using figure coordinates
    for i, hex_color in enumerate(hex_colors):
        rect = patches.Rectangle((i / n, -0.04), 1 / n, 0.03,
                                  facecolor='#' + hex_color, edgecolor='black', linewidth=0.5,
                                  transform=ax.transAxes, clip_on=False)
        ax.add_patch(rect)
    
    ax.set_title('Color Distinguishability (higher = more different)', pad=20)
    plt.tight_layout()

    plt.savefig(filepath)