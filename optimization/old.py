# from ortools.sat.python import cp_model

# model = cp_model.CpModel()

# # x[c] = 1 if color c is selected
# x = {c: model.NewBoolVar(f'select_color_{c}') for c in range(num_colors)}

# # Constraint: Select exactly n colors
# model.Add(sum(x[c] for c in range(num_colors)) == num_colors_to_select)

# # Find the maximum possible distance for upper bound
# max_distance = max(distance_matrix.values())

# # min_dist is the minimum distance we want to maximize
# min_dist = model.NewIntVar(0, max_distance, 'min_dist')

# # For each pair of colors, if both are selected, their distance must be >= min_dist
# for i in range(num_colors):
#     for j in range(i + 1, num_colors):
#         if (i, j) in distance_matrix:
#             dist = distance_matrix[(i, j)]
#         elif (j, i) in distance_matrix:
#             dist = distance_matrix[(j, i)]
#         else:
#             continue
        
#         # If both colors are selected, min_dist <= dist
#         # Equivalent to: NOT(x[i] AND x[j]) OR (min_dist <= dist)
#         # Which is: x[i]=0 OR x[j]=0 OR min_dist <= dist
#         both_selected = model.NewBoolVar(f'both_{i}_{j}')
#         model.AddBoolAnd([x[i], x[j]]).OnlyEnforceIf(both_selected)
#         model.AddBoolOr([x[i].Not(), x[j].Not()]).OnlyEnforceIf(both_selected.Not())
        
#         # If both are selected, min_dist must be <= the distance between them
#         model.Add(min_dist <= dist).OnlyEnforceIf(both_selected)

# model.Maximize(min_dist)

# # Solve
# solver = cp_model.CpSolver()
# solver.parameters.max_time_in_seconds = 240 # May need more time for this formulation
# solver.parameters.log_search_progress = False
# status = solver.Solve(model)

# # Extract results
# if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
#     selected_colors = [c for c in range(num_colors) if solver.Value(x[c]) == 1]
    
#     # Calculate minimum and average distance
#     min_found = float('inf')
#     total_dist = 0
#     count = 0
#     for i in selected_colors:
#         for j in selected_colors:
#             if i < j:
#                 dist = distance_matrix.get((i, j)) or distance_matrix.get((j, i), 0)
#                 min_found = min(min_found, dist)
#                 total_dist += dist
#                 count += 1
    
#     avg_dist = total_dist / count if count > 0 else 0
#     print(f"Selected colors: {selected_colors}")
#     print(f"Minimum distance: {min_found}")
#     print(f"Average distance: {avg_dist}")
#     print(f"Status: {'OPTIMAL' if status == cp_model.OPTIMAL else 'FEASIBLE'}")
# else:
#     print(f"Solver failed with status: {solver.StatusName(status)}")