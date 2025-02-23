class Oracle:
    def __init__(self, constraints, top_k_fraction=0.3):
        """
        Initialize a multi–attribute fairness oracle.

        Parameters:
          constraints (dict): A dictionary mapping attribute names to a dictionary
                              of group constraints. For example:
                              {
                                  'race': {
                                      'African-American': (0.3, 0.6),
                                      'Caucasian': (0.4, 0.7)
                                  },
                                  'sex': {
                                      'Female': (0.4, 0.6),
                                      'Male': (0.4, 0.6)
                                  }
                              }
                              Each tuple (min_frac, max_frac) represents the minimum and maximum
                              allowed fraction for that group in the top–k.
          top_k_fraction (float): The fraction (e.g., 0.3 for the top 30%) of the ranking to evaluate.
        """
        self.constraints = constraints
        self.types = list(constraints.keys())
        self.top_k_fraction = top_k_fraction

    def __call__(self, ranking):
        """
        Evaluate if the given ranking satisfies the fairness criteria across multiple attributes.

        Parameters:
          ranking (list): A list of items (dictionaries) representing the ranked order.
                          Each item must contain keys for the protected attributes defined in constraints.

        Returns:
          bool: True if the ranking satisfies all fairness constraints; False otherwise.
        """
        if not ranking:
            return True  # No items means no fairness violation.

        # Determine the number of items in the top-k portion.
        top_k = int(len(ranking) * self.top_k_fraction)
        top_k = max(top_k, 1)  # Ensure at least one item is evaluated.

        # For each protected attribute, count the occurrences of each group in the top-k.
        index = 2
        for attr in self.types:
            counts = {}
            for item in ranking[-top_k:]:
                group = item[index]
                counts[group] = counts.get(group, 0) + 1

            for group, (min_frac, max_frac) in self.constraints[attr].items():
                frac = counts.get(group, 0) / top_k
                # Debug print (optional): print(f"For attribute '{attr}', group '{group}': fraction = {frac}")
                if frac < min_frac or frac > max_frac:
                    return False
            index += 1
        # If all attribute constraints are satisfied, return True.
        return True