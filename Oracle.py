class Oracle:
    def __init__(self, protected_val='AfricanAmerican', top_k_fraction=0.3, max_protected_fraction=0.6):
        """
        Initialize the fairness oracle using the FM1 fairness model.

        Parameters:
          protected_val (str): The value that identifies the protected group.
          top_k_fraction (float): The fraction (e.g., 0.3 for top 30%) of the ranking to evaluate.
          max_protected_fraction (float): The maximum allowed fraction of protected items in the top-k.
        """
        self.protected_val = protected_val
        self.top_k_fraction = top_k_fraction
        self.max_protected_fraction = max_protected_fraction

    def __call__(self, ranking):
        """
        Evaluate if the given ranking satisfies the FM1 fairness criteria.

        Parameters:
          ranking (list): A list of items (e.g., dictionaries) representing the ranked order.

        Returns:
          bool: True if the ranking is fair under FM1, False otherwise.
        """
        if not ranking:
            return True  # No items means no fairness violation.

        # Determine the number of items to consider in the top-k.
        top_k = int(len(ranking) * self.top_k_fraction)
        top_k = max(top_k, 1)  # Ensure at least one item is evaluated.

        # Count how many items in the top-k belong to the protected group.
        protected_count = sum(1 for item in ranking[:top_k] if item[2] == self.protected_val)

        # Calculate the fraction of protected items in the top-k.
        fraction = protected_count / top_k

        # The ranking is fair if the fraction does not exceed the threshold.
        return fraction <= self.max_protected_fraction
