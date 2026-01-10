"""
Algorithm type enumeration for quantitative trading algorithms.
"""

from enum import Enum


class AlgorithmType(Enum):
    """Enumeration of all supported algorithm types."""

    # Classification Algorithms
    SVM = "svm"
    DECISION_TREE = "decision_tree"
    NAIVE_BAYES = "naive_bayes"

    # Pattern Matching Algorithms
    BRUTE_FORCE = "brute_force"
    KNUTH_MORRIS_PRATT = "knuth_morris_pratt"
    BOYER_MOORE_HORSPOOL = "boyer_moore_horspool"
    AHO_CORASICK = "aho_corasick"

    # Advanced Algorithms
    HIDDEN_MARKOV_MODEL = "hidden_markov_model"
    BAYESIAN_NETWORK = "bayesian_network"
    N_GRAM = "n_gram"
    NEURAL_NETWORK = "neural_network"

    @classmethod
    def get_classification_algorithms(cls):
        """Get all classification algorithm types."""
        return [cls.SVM, cls.DECISION_TREE, cls.NAIVE_BAYES]

    @classmethod
    def get_pattern_matching_algorithms(cls):
        """Get all pattern matching algorithm types."""
        return [cls.BRUTE_FORCE, cls.KNUTH_MORRIS_PRATT, cls.BOYER_MOORE_HORSPOOL, cls.AHO_CORASICK]

    @classmethod
    def get_advanced_algorithms(cls):
        """Get all advanced algorithm types."""
        return [cls.HIDDEN_MARKOV_MODEL, cls.BAYESIAN_NETWORK, cls.N_GRAM, cls.NEURAL_NETWORK]

    @classmethod
    def get_all_algorithms(cls):
        """Get all algorithm types."""
        return (
            cls.get_classification_algorithms() + cls.get_pattern_matching_algorithms() + cls.get_advanced_algorithms()
        )

    def get_category(self) -> str:
        """Get the category this algorithm belongs to."""
        if self in self.get_classification_algorithms():
            return "classification"
        elif self in self.get_pattern_matching_algorithms():
            return "pattern_matching"
        elif self in self.get_advanced_algorithms():
            return "advanced"
        else:
            return "unknown"
