class Oracle:
    def __init__(self, top_k_fraction=0.3, max_AA_ratio=0.6, type_attr='African-American'):
        """
        Fairness oracle for FM1 on the COMPAS dataset.
        """
        self.top_k_fraction = top_k_fraction
        self.max_AA_ratio = max_AA_ratio
        self.type_attr = type_attr
        self.top_k = None

    def __call__(self, ranking):
        if not self.top_k:
            self.top_k = int(len(ranking) * self.top_k_fraction)

        # If there are no items in the top segment, the ranking is satisfactory.
        if self.top_k == 0:
            return True

        max_allowed = self.top_k * self.max_AA_ratio
        aa_count = 0
        for i in range(self.top_k):
            if ranking[i][2] == self.type_attr:
                aa_count += 1
                # Early exit if we exceed the allowed ratio.
                if aa_count > max_allowed:
                    return False

        return True

    def reset(self):
        self.top_k = None
