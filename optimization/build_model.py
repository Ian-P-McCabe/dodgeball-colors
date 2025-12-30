from ortools.sat.python import cp_model

# def build_max_pairwise_model(num_colors: int, num_colors_to_select: int, distance_matrix) -> cp_model.CpModel:

#     model = cp_model.CpModel()

#     # x[c] = 1 if color c is selected
#     x = {c: model.NewBoolVar(f'select_color_{c}') for c in range(num_colors)}

#     # Constraint: Select exactly n colors
#     model.Add(sum(x[c] for c in range(num_colors)) == num_colors_to_select)

#     # Objective: Maximize total pairwise distance
#     objective_terms = []
#     for i in range(num_colors):
#         for j in range(i + 1, num_colors):
#             if (i, j) in distance_matrix:
#                 dist = distance_matrix[(i, j)]
#             elif (j, i) in distance_matrix:
#                 dist = distance_matrix[(j, i)]
#             else:
#                 continue
            
#             # pair_var = 1 if both x[i] and x[j] are selected
#             pair_var = model.NewBoolVar(f'pair_{i}_{j}')
#             model.AddBoolAnd([x[i], x[j]]).OnlyEnforceIf(pair_var)
#             model.AddBoolOr([x[i].Not(), x[j].Not()]).OnlyEnforceIf(pair_var.Not())
            
#             objective_terms.append(dist * pair_var)

#     model.Maximize(sum(objective_terms))

#     return model


class ColorSolver():

    def __init__(self, num_colors: int, num_colors_to_select: int, distance_matrix):
        self.num_colors = num_colors
        self.num_colors_to_select = num_colors_to_select
        self.distance_matrix = distance_matrix
        self.color_selection_vars = {}
        self.model = cp_model.CpModel()
    
    def build_max_pairwise_model(self):
        # x[c] = 1 if color c is selected
        color_selection_vars = {c: self.model.NewBoolVar(f'select_color_{c}') for c in range(self.num_colors)}

        # Constraint: Select exactly n colors
        self.model.Add(sum(color_selection_vars[c] for c in range(self.num_colors)) == self.num_colors_to_select)

        # Objective: Maximize total pairwise distance
        objective_terms = []
        for i in range(self.num_colors):
            for j in range(i + 1, self.num_colors):
                if (i, j) in self.distance_matrix:
                    dist = self.distance_matrix[(i, j)]
                elif (j, i) in self.distance_matrix:
                    dist = self.distance_matrix[(j, i)]
                else:
                    continue
                
                # pair_var = 1 if both x[i] and x[j] are selected
                pair_var = self.model.NewBoolVar(f'pair_{i}_{j}')
                self.model.AddBoolAnd([color_selection_vars[i], color_selection_vars[j]]).OnlyEnforceIf(pair_var)
                self.model.AddBoolOr([color_selection_vars[i].Not(), color_selection_vars[j].Not()]).OnlyEnforceIf(pair_var.Not())
                
                objective_terms.append(dist * pair_var)

        self.model.Maximize(sum(objective_terms))
    
    
    def analyze_solution(self, solver: cp_model.CpSolver):

        status = solver.status_name

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            selected_colors = [c for c in range(self.num_colors) if solver.Value(self.color_selection_vars[c]) == 1]
            
            # Calculate minimum and average distance
            min_found = float('inf')
            total_dist = 0
            count = 0
            for i in selected_colors:
                for j in selected_colors:
                    if i < j:
                        dist = self.distance_matrix.get((i, j)) or self.distance_matrix.get((j, i), 0)
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


# Solve
# solver = cp_model.CpSolver()
# solver.parameters.max_time_in_seconds = 30  # Optional time limit
# solver.parameters.log_search_progress = False 
# status = solver.Solve(model)

# Extract results
# if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
#     selected_colors = [c for c in range(num_colors) if solver.Value(color_selection_vars[c]) == 1]
    
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