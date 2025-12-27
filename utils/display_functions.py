import matplotlib.pyplot as plt
import matplotlib.patches as patches

def display_palette(selected_colors: list[int], color_df, cols=None):

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
    plt.savefig("assets/testgrid.svg")
    plt.show()