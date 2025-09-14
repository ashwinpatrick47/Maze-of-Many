# -------------------------------------------------
# DON'T CHANGE THIS FILE.
# Master file for running all maze generation/solving functions.
#
# __author__ = 'Edward Small'
# __copyright__ = 'Copyright 2025, RMIT University'
# -------------------------------------------------

import sys
from graph.coordinate import Coordinate
from helpers.helpers import (
    load_config, build_maze, start_timer, stop_timer,
    save_maze_to_txt, load_maze_from_txt,
    validate_full_coverage, validate_clone_origins,
    validate_path_connectivity
)
from maze.dfs_generator import generateMazeDFS
from MST.prims import primMST
from MST.kruskals import kruskalMST
from maze.maze import Maze
from solvers.no_clone import no_clone_solver
from solvers.always_clone import always_clone_solver
from solvers.task_d_solver import task_d_solver

# enforce python version >= 3.13
if sys.version_info < (3, 13):
    print("Error: Python 3.13 or higher is required to run Maze of Many.")
    sys.exit(1)

def main():
    print("--------------- Maze of Many ---------------")
    # ─── Load Configuration ───────────────────────────────────
    if len(sys.argv) != 2:
        print("Usage: python mazeRunner.py config.json")
        sys.exit(1)

    config_path = sys.argv[1]
    config = load_config(config_path)

    rows = config.get("rows")
    cols = config.get("cols")
    graph_type = config.get("graph_type", "matrix").lower()
    maze_name = config.get("maze_name", "test")
    entrance_data = config.get("entrance", {})
    entrance = Coordinate(entrance_data.get("row", 0), entrance_data.get("col", 0))

    # ─── Maze Construction ────────────────────────────────────
    if config.get("load_maze", False):
        file_path = f"mazes/{maze_name}.txt"
        print(f"Loading maze from file: {file_path}")
        graph = load_maze_from_txt(file_path, graph_type)
        maze = Maze(graph)
        maze.setStart(entrance)
    else:
        print(f"Creating new maze of size {rows}x{cols}")
        maze = build_maze(rows, cols, graph_type)
        maze.setStart(entrance)
        print(f"Entrance set at: {entrance}")

        gen_type = config.get("maze_generator", "dfs").lower()
        rem_perc = config.get("wall_removal_perc", 0)
        max_weight = config.get("max_weight", 1)

        print(f"Generating maze using: {gen_type}")
        if gen_type == "dfs":
            generateMazeDFS(maze.graph, rem_perc, max_weight)
        else:
            print(f"Unknown maze generation type: '{gen_type}'. Only 'dfs' is supported.")
            sys.exit(1)

    # ─── MST Generation ───────────────────────────────────────
    mst_type = config.get("mst_generator", "prims").lower()
    print(f"Generating MST using: {mst_type}")

    if mst_type == "prims":
        mst = primMST(maze.graph)
    elif mst_type == "kruskals":
        mst = kruskalMST(maze.graph)
    else:
        print("Invalid MST generation method. Use 'prims' or 'kruskals'.")
        sys.exit(1)

    # ─── Solve Maze using MST ──────────────────────────────────
    maze_solver = config.get("maze_solver", "no_clone").lower()
    clone_cost = config.get("clone_cost", 0)
    print(f"Solving maze using {maze_solver} with a clone cost of {clone_cost}")
    if maze_solver == "always_clone":
        path, cost, num_clones = always_clone_solver(mst, entrance, clone_cost)
    elif maze_solver == "no_clone":
        path, cost, num_clones = no_clone_solver(mst, entrance, clone_cost)
    elif maze_solver == "task_d":
        path, cost, num_clones = task_d_solver(mst, entrance, clone_cost)
    else:
        print("Invalid maze solver method. Use 'always_clone', 'no_clone', or 'task_d.")
        sys.exit(1)

    # Check we visit all nodes
    if not validate_full_coverage(mst, path):
        print("Solver failed to visit all nodes in the maze.")
        sys.exit(1)

    if not validate_clone_origins(path):
        print("Clone does not spawn in a previously visited cell.")
        sys.exit(1)

    if not validate_path_connectivity(maze.graph, path):
        print("A path is not valid.")
        sys.exit(1)

    print(f"Cost of traversal (max cost of (1) inheritance + (2) clone creation + (3) travel for single entity): {cost}")
    print(f"Number of clones: {num_clones}")

    # ─── Optional Debug Output ────────────────────────────────
    if config.get("print_struct", False):
        print("\nMaze Graph Structure:")
        maze.graph.print()
        print("\nMST Graph Structure:")
        mst.print()

    # ─── Save Maze ────────────────────────────────────────────
    if config.get("save_maze", False):
        file_path = f"mazes/{maze_name}.txt"
        print(f"Saving maze to file: {file_path}")
        save_maze_to_txt(maze.graph, file_path)

    # ─── Visualisation ────────────────────────────────────────
    if config.get("visualise", False):
        try:
            from viz.visualiser import draw_maze
            print("Launching visualisation...")
            draw_maze(maze, mst, path)
        except ImportError:
            print("Visualization skipped: matplotlib is not installed.")

    print("--------------- Run Complete ---------------")


if __name__ == "__main__":
    main()
