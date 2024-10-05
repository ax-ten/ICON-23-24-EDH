from enum import Enum
import numpy as np
class Pooling(Enum):
    MAX = lambda deck_vs:       np.max(deck_vs, axis=0) # Ottiene le caratteristiche dominanti
    SUM = lambda deck_vs:       np.sum(deck_vs, axis=0) # Accumulo totale delle caratteristiche
    MIN = lambda deck_vs:       np.min(deck_vs, axis=0) # Indica le caratteristiche recessive
    AVERAGE = lambda deck_vs:   np.mean(deck_vs, axis=0) # Indica le caratteristiche medie
    MEDIAN = lambda deck_vs:    np.median(deck_vs, axis=0) # Riduce l'impatto degli outlier
    VARIANCE = lambda deck_vs:  np.var(deck_vs, axis=0) # Misura la diversità all'interno del deck
    GEO_MEAN = lambda deck_vs:  np.exp(np.mean(np.log(deck_vs + 1e-9), axis=0)) # Riduce impatto di valori agli estremi