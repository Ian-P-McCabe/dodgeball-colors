from ortools.sat.python import cp_model

def analyze_model(solver: cp_model.CpSolver, num_colors: int, distance_matrix):
    status = solver.status_name
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        selected_colors = [c for c in range(num_colors) if solver.Value(x[c]) == 1]
        
        # Calculate minimum and average distance
        min_found = float('inf')
        total_dist = 0
        count = 0
        for i in selected_colors:
            for j in selected_colors:
                if i < j:
                    dist = distance_matrix.get((i, j)) or distance_matrix.get((j, i), 0)
                    min_found = min(min_found, dist)
                    total_dist += dist
                    count += 1
        
        avg_dist = total_dist / count if count > 0 else 0
        print(f"Selected colors: {selected_colors}")
        print(f"Minimum distance: {min_found}")
        print(f"Average distance: {avg_dist}")
        print(f"Status: {'OPTIMAL' if status == cp_model.OPTIMAL else 'FEASIBLE'}")
    else:
        print(f"Solver failed with status: {solver.StatusName(status)}")