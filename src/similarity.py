from enum import Enum
import numpy as np

class SimilarityMethod(Enum):
    COSINE = lambda v1, v2: cosine(v1, v2)
    EUCLIDEAN = lambda v1, v2: np.linalg.norm(np.array(v1) - np.array(v2))
    MANHATTAN = lambda v1, v2: np.sum(np.abs(np.array(v1) - np.array(v2)))
    CHEBYSHEV = lambda v1, v2: np.max(np.abs(np.array(v1) - np.array(v2)))
    JACCARD = lambda v1, v2: np.sum(np.minimum(v1, v2)) / np.sum(np.maximum(v1, v2)) if np.sum(np.maximum(v1, v2)) != 0 else 0
    COSINE_DISTANCE = lambda v1, v2: 1 - cosine(v1, v2)
    PEARSON_CORRELATION = lambda v1, v2: np.corrcoef(v1, v2)[0, 1]
    BRAY_CURTIS = lambda v1, v2: np.sum(np.abs(np.array(v1) - np.array(v2))) / np.sum(np.abs(np.array(v1) + np.array(v2)))
    
    def calculate(self, v1, v2):
        return self.value(v1, v2)

def cosine(v1: list, v2: list) -> float:
    dot_product = np.dot(v1, v2)
    n1, n2 = [np.linalg.norm(n) for n in [v1, v2]]
    if 0 in [n1, n2]:
        return 0.0
    return max(-1.0, min(1.0, dot_product / (n1 * n2)))