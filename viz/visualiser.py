# -------------------------------------------------
# DON'T CHANGE THIS FILE.
# Basic visualiser function (draws plots).
#
# __author__ = 'Edward Small'
# __copyright__ = 'Copyright 2025, RMIT University'
# -------------------------------------------------

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from scipy.interpolate import splprep, splev
from graph.coordinate import Coordinate
from maze.maze import Maze


def draw_maze(maze: Maze, mst: Maze, path=None, cell_size: float = 1.0):
    """
    Visualizes the MST graph and the maze side by side.

    @param maze: Maze object with full graph.
    @param mst: Maze object with MST graph.
    @param cell_size: Size of each cell in the maze grid.
    """
    fig, (ax_maze, ax_mst) = plt.subplots(1, 2, figsize=(14, 7))
    ax_maze.set_facecolor('#f0f0f0')  # light grey

    fig.suptitle("Maze vs Minimum Spanning Tree", fontsize=16)

    for ax in [ax_maze, ax_mst]:
        ax.set_aspect('equal')
        ax.axis('off')

    rows, cols = maze.graph.rows, maze.graph.cols
    vertices = maze.graph.getVertices()

    # ----------------------------------------
    # LEFT: Maze Grid View
    # ----------------------------------------
    ax_maze.set_title("Maze Grid")

    neis = {u: set(maze.graph.neighbours(u)) for u in vertices}

    for coord in vertices:
        x = coord.getCol()
        y = coord.getRow()

        for dx, dy, side in [(0, -1, 'top'), (0, 1, 'bottom'), (-1, 0, 'left'), (1, 0, 'right')]:
            nr, nc = y + dy, x + dx
            ncoord = Coordinate(nr, nc)
            out = not (0 <= nr < rows and 0 <= nc < cols)
            connected = (not out) and (ncoord in neis[coord])

            if out or not connected:
                draw_wall(ax_maze, x, y, side, cell_size)

    maze_width = cols * cell_size
    maze_height = rows * cell_size
    border = patches.Rectangle((0, 0), maze_width, maze_height,
                               linewidth=2, edgecolor='black', facecolor='none')
    ax_maze.add_patch(border)

    edge_weights = []
    for u in vertices:
        for v in neis[u]:
            if u.getRow() > v.getRow() or (u.getRow() == v.getRow() and u.getCol() > v.getCol()):
                continue
            weight = maze.graph.getWeight(u, v)
            edge_weights.append((u, v, weight))

    if edge_weights:
        # Collect all edge weights
        weights = sorted(set(w for _, _, w in edge_weights))  # Unique weights only
        cmap = cm.get_cmap('Blues', len(weights))  # Discrete colormap with N colors

        # Map each weight to a distinct color
        weight_to_color = {w: cmap(i / max(len(weights) - 1, 1)) for i, w in enumerate(weights)}

        # Draw colored squares at edge midpoints
        for u, v, w in edge_weights:
            x = (u.getCol() + v.getCol()) / 2
            y = (u.getRow() + v.getRow()) / 2
            color = weight_to_color.get(w, cmap(0.0))  # fallback to lowest color

            square = patches.Rectangle(
                ((x + 0.25) * cell_size, (y + 0.25) * cell_size),
                cell_size * 0.5, cell_size * 0.5,
                facecolor=color, edgecolor='none'
            )
            ax_maze.add_patch(square)

        # Create a ListedColormap from the mapped colors
        color_list = [weight_to_color[w] for w in weights]
        listed_cmap = mcolors.ListedColormap(color_list)

        # Create boundaries between weights
        boundaries = [w - 0.5 for w in weights] + [weights[-1] + 0.5]
        norm = mcolors.BoundaryNorm(boundaries, listed_cmap.N)

        # Create colorbar
        sm = cm.ScalarMappable(cmap=listed_cmap, norm=norm)
        sm.set_array([])

        num_ticks = max(2, max(weights) // 10)
        tick_indices = [round(i * (len(weights) - 1) / (num_ticks - 1)) for i in range(num_ticks)]
        tick_weights = [weights[i] for i in tick_indices]

        cbar = plt.colorbar(sm, ax=ax_maze, fraction=0.03, pad=0.04, ticks=tick_weights)
        cbar.set_label('Edge Weight', rotation=270, labelpad=15)
        cbar.ax.set_yticklabels([str(w) for w in tick_weights])

    for coord in vertices:
        x = coord.getCol()
        y = coord.getRow()

        if coord == maze.start:
            cx = (x + 0.5) * cell_size
            cy = (y + 0.5) * cell_size
            circle = patches.Circle((cx, cy), radius=cell_size * 0.15,
                                    facecolor='green', edgecolor='black', linewidth=1.5)
            ax_maze.add_patch(circle)

            ax_maze.text(cx, cy, "Start", fontsize=8, ha='center', va='center', color='white')

        for dx, dy, side in [(0, -1, 'top'), (0, 1, 'bottom'), (-1, 0, 'left'), (1, 0, 'right')]:
            nr, nc = y + dy, x + dx
            ncoord = Coordinate(nr, nc)
            out = not (0 <= nr < rows and 0 <= nc < cols)
            connected = (not out) and (ncoord in neis[coord])

            if connected:
                draw_dotted_divider(ax_maze, x, y, side, cell_size)

    # draw the path
    paths = path if isinstance(path[0], list) else [path]
    cmap = cm.get_cmap('autumn')
    num_paths = len(paths)

    for i, p in enumerate(paths):
        if p:
            color = '#006400' if i == 0 else cmap(i / max(num_paths - 1, 1))  # dark green for original
            if i == 0:
                ax_maze.plot([], [], color='#006400', label='Sorcerer')
            else:
                ax_maze.plot([], [], color=color, label=f'Clone {i}')

            offset_x = []
            offset_y = []

            OFFSET_MAG = 0.05

            for i in range(len(p)):
                coord = p[i]
                x = coord.getCol() + 0.5
                y = coord.getRow() + 0.5

                # Compute direction vector (forward or backward)
                if i < len(p) - 1:
                    next_coord = p[i + 1]
                else:
                    next_coord = p[i - 1]

                dx = next_coord.getCol() - coord.getCol()
                dy = next_coord.getRow() - coord.getRow()

                # Rotate 90 degrees clockwise: (dx, dy) → (dy, -dx)
                perp_dx = dy
                perp_dy = -dx

                # Normalize
                length = (perp_dx ** 2 + perp_dy ** 2) ** 0.5 or 1
                perp_dx /= length
                perp_dy /= length

                # Apply offset
                offset_x.append(x + perp_dx * OFFSET_MAG)
                offset_y.append(y + perp_dy * OFFSET_MAG)

            if len(offset_x) > 3:  # splprep requires at least 3 points
                tck, _ = splprep([offset_x, offset_y], s=0)
                u_fine = [i / (len(p) * 10) for i in range(len(p) * 10)]
                x_spline, y_spline = splev(u_fine, tck)

                ax_maze.plot(x_spline, y_spline, color=color, linewidth=2)
            else:
                # fallback to straight lines if path is too short
                ax_maze.plot(offset_x, offset_y, color=color, linewidth=2)

    ax_maze.legend(
        loc='center left',
        bbox_to_anchor=(-0.2, 0.5),
        fontsize='small',
        frameon=False
    )

    # ----------------------------------------
    # RIGHT: MST Graph View
    # ----------------------------------------
    ax_mst.set_title("Weighted MST Graph")

    edge_weights = []
    for u in mst.getVertices():
        for v in mst.neighbours(u):
            if u.getRow() > v.getRow() or (u.getRow() == v.getRow() and u.getCol() > v.getCol()):
                continue
            w = mst.getWeight(u, v)
            edge_weights.append((u, v, w))

    radius = cell_size * 0.2

    for u, v, w in edge_weights:
        x1, y1 = u.getCol() + 0.5, u.getRow() + 0.5
        x2, y2 = v.getCol() + 0.5, v.getRow() + 0.5

        dx, dy = x2 - x1, y2 - y1
        dist = (dx ** 2 + dy ** 2) ** 0.5
        if dist == 0:
            continue

        ux, uy = dx / dist, dy / dist

        start_x = (x1 + ux * radius) * cell_size
        start_y = (y1 + uy * radius) * cell_size
        end_x = (x2 - ux * radius) * cell_size
        end_y = (y2 - uy * radius) * cell_size

        ax_mst.plot([start_x, end_x], [start_y, end_y], color='black', linewidth=1.5)

        # Offset label perpendicular to the edge direction
        offset_scale = cell_size * 0.15  # tweak this for spacing
        perp_x = -uy  # perpendicular to (ux, uy)
        perp_y = ux

        label_x = (start_x + end_x) / 2 + perp_x * offset_scale
        label_y = (start_y + end_y) / 2 + perp_y * offset_scale

        ax_mst.text(label_x, label_y, str(w), fontsize=8, ha='center', va='center', color='black')

    for coord in mst.getVertices():
        x = coord.getCol()
        y = coord.getRow()
        cx = (x + 0.5) * cell_size
        cy = (y + 0.5) * cell_size

        circle = patches.Circle((cx, cy), radius=radius,
                                facecolor='white', edgecolor='black', linewidth=1.5)
        ax_mst.add_patch(circle)

        label = f"({x}, {y})"
        ax_mst.text(cy, cx, label, fontsize=8, ha='center', va='center', color='black')

    plt.tight_layout()
    plt.show()


def draw_wall(ax, x: int, y: int, side: str, cell_size: float):
    """
    Draws a wall on one side of a cell.

    @param ax: Matplotlib axis.
    @param x: Column index.
    @param y: Row index (flipped).
    @param side: 'top', 'bottom', 'left', or 'right'.
    @param cell_size: Size of the cell.
    """
    if side == 'top':
        ax.plot([x * cell_size, (x + 1) * cell_size], [y * cell_size, y * cell_size], color='black')
    elif side == 'bottom':
        ax.plot([x * cell_size, (x + 1) * cell_size], [(y + 1) * cell_size, (y + 1) * cell_size], color='black')
    elif side == 'left':
        ax.plot([x * cell_size, x * cell_size], [y * cell_size, (y + 1) * cell_size], color='black')
    elif side == 'right':
        ax.plot([(x + 1) * cell_size, (x + 1) * cell_size], [y * cell_size, (y + 1) * cell_size], color='black')


def draw_dotted_divider(ax, x: int, y: int, side: str, cell_size: float):
    """
    Draws a faint dotted line between connected cells to indicate separation.

    @param ax: Matplotlib axis.
    @param x: Column index.
    @param y: Row index (flipped).
    @param side: 'top', 'bottom', 'left', or 'right'.
    @param cell_size: Size of the cell.
    """
    kwargs = dict(color='gray', linestyle=':', linewidth=0.5)
    if side == 'top':
        ax.plot([x * cell_size, (x + 1) * cell_size], [y * cell_size, y * cell_size], **kwargs)
    elif side == 'bottom':
        ax.plot([x * cell_size, (x + 1) * cell_size], [(y + 1) * cell_size, (y + 1) * cell_size], **kwargs)
    elif side == 'left':
        ax.plot([x * cell_size, x * cell_size], [y * cell_size, (y + 1) * cell_size], **kwargs)
    elif side == 'right':
        ax.plot([(x + 1) * cell_size, (x + 1) * cell_size], [y * cell_size, (y + 1) * cell_size], **kwargs)
