from ortools.sat.python import cp_model

class SolutionCollector(cp_model.CpSolverSolutionCallback):
    """Callback to collect multiple solutions."""
    
    def __init__(self, color_vars, num_colors, max_solutions=100):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.color_vars = color_vars
        self.num_colors = num_colors
        self.max_solutions = max_solutions
        self.solutions = []
    
    def on_solution_callback(self):
        selected = [c for c in range(self.num_colors) if self.Value(self.color_vars[c]) == 1]
        self.solutions.append(selected)
        if len(self.solutions) >= self.max_solutions:
            self.StopSearch()

class ColorModel():

    def __init__(self, num_colors: int, num_colors_to_select: int, distance_matrix):
        self.num_colors = num_colors
        self.num_colors_to_select = num_colors_to_select
        self.distance_matrix = distance_matrix
        self._reset_model()
    

    def _reset_model(self):
        """Reset model state for fresh build."""
        self.model = cp_model.CpModel()
        self.color_vars = {}


    def _create_color_variables(self):
        """Create binary variables for each color."""
        self.color_vars = {
            c: self.model.NewBoolVar(f'color_{c}') 
            for c in range(self.num_colors)
        }
        # Constraint: Select exactly n colors
        self.model.Add(sum(self.color_vars.values()) == self.num_colors_to_select)
    

    def build_max_pairwise_model(self):
        
        self._reset_model()
        self._create_color_variables()

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
                self.model.AddBoolAnd([self.color_vars[i], self.color_vars[j]]).OnlyEnforceIf(pair_var)
                self.model.AddBoolOr([self.color_vars[i].Not(), self.color_vars[j].Not()]).OnlyEnforceIf(pair_var.Not())
                
                objective_terms.append(dist * pair_var)

        self.model.Maximize(sum(objective_terms))
    

    def build_max_minimum_model(self):

        self._reset_model()
        self._create_color_variables()

        max_distance = max(self.distance_matrix.values())
        self.min_dist_var = self.model.NewIntVar(0, max_distance, 'min_dist')

        # For each pair of colors, if both are selected, their distance must be >= min_dist
        for i in range(self.num_colors):
            for j in range(i + 1, self.num_colors):
                if (i, j) in self.distance_matrix:
                    dist = self.distance_matrix[(i, j)]
                elif (j, i) in self.distance_matrix:
                    dist = self.distance_matrix[(j, i)]
                else:
                    continue
                
                # If both colors are selected, min_dist <= dist
                both_selected = self.model.NewBoolVar(f'both_{i}_{j}')

                self.model.AddMultiplicationEquality(both_selected, [self.color_vars[i], self.color_vars[j]])

                # If both are selected, min_dist must be <= the distance between them
                self.model.Add(self.min_dist_var <= dist).OnlyEnforceIf(both_selected)

        self.model.Maximize(self.min_dist_var)
    

    def build_hybrid_model(self, optimal_max_min: int):

        self._reset_model()
        self._create_color_variables()

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
                both_selected = self.model.NewBoolVar(f'pair_{i}_{j}')
                self.model.AddMultiplicationEquality(both_selected, [self.color_vars[i], self.color_vars[j]])

                # Hard constraint: if both selected, distance must be >= optimal_max_min
                if dist < optimal_max_min:
                    # Cannot select both colors if their distance is below threshold
                    self.model.Add(both_selected == 0)
                
                objective_terms.append(dist * both_selected)

        self.model.Maximize(sum(objective_terms))



    def max_min_solve_enumerate_optimal(self, time_limit: int = 300, max_solutions: int = 10, known_optimal: int = None):
        # First solve to find optimal
        if known_optimal is not None:
            optimal_value = known_optimal
            print(f"Using known optimal min_dist: {optimal_value}")
        else:
            # First solve to find optimal
            solver = cp_model.CpSolver()
            solver.parameters.max_time_in_seconds = time_limit
            status = solver.Solve(self.model)
            
            if status != cp_model.OPTIMAL:
                print("Could not prove optimality, returning single solution")
                return [self.extract_solution(status, solver)]
            
            optimal_value = int(solver.ObjectiveValue())
            print(f"Optimal min_dist: {optimal_value}")

        #Fix objective to optimal
        self.model.Add(self.min_dist_var == optimal_value)

        self.model.ClearObjective()
        
        # Fresh solver for enumeration
        enum_solver = cp_model.CpSolver()
        enum_solver.parameters.enumerate_all_solutions = True
        enum_solver.parameters.max_time_in_seconds = time_limit
        
        # Collect solutions with callback
        collector = SolutionCollector(self.color_vars, self.num_colors, max_solutions)
        
        enum_solver.Solve(self.model, collector)
        
        print(f"Found {len(collector.solutions)} optimal solutions")
        return collector.solutions

    
    def solve(self, time_limit: float = 300, log_progress: bool = False):
        """Solve the model and return results."""

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = time_limit
        solver.parameters.log_search_progress = log_progress

        status = solver.Solve(self.model)
        return self.extract_solution(status, solver)


    def extract_solution(self, status, solver):

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            selected_colors = [c for c in range(self.num_colors) if solver.Value(self.color_vars[c]) == 1]
            
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

            return selected_colors, min_found
        else:
            print(f"Solver failed with status: {solver.StatusName(status)}")
            return [], -1




