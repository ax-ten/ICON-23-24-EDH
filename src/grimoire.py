import os, pickle
from src.card import Card
from src.decks import Deck
import csv
    
import numpy as np
from src.pooling import Pooling
filename_translator = {ord(i):None for i in '".?/:;><'}
PATH = "./data/fetched/grimoire/"

class Grimoire():
    def __init__(self):
        self.cards = {} # = {card:[deck_id:int]}

    def __iter__(self)->list[Card]: return iter(self.cards)
    def __len__(self)->list[Card]:  return len(self.cards)
    def __getitem__(self, key): return self.cards[key]
    def __delitem__(self, card): del self.cards[card]
    def __contains__(self, card): return card in self.cards
    def keys(self):             return self.cards.keys()
    def values(self):           return self.cards.values()
    def items(self):            return self.cards.items()
    def get(self, key, default=None):  return self.cards.get(key, default)

    def __repr__(self) -> str:
        s = ''
        for card in self.keys():
            s= s + f'{card}\n'
        return s
    
    def make_omni(self):
        OMNI = 'OMNI'
        if load(OMNI) is None:
            CSV_PATH = "./data/oracle_cards/oracle_cards.csv"
    
            with open(CSV_PATH, 'r',encoding="UTF-8", errors="ignore") as infile:
                reader = csv.reader(infile,delimiter=',')
                head = next(reader)
                for row in reader:
                    card=Card()
                    card.load_csv(row)
                    self.append(card)
                    
                    # self.append(Card().load_csv(row),deck_id=0)
            
            self.save(OMNI)
        else:
            self.cards = load(OMNI,display=False).cards
    

    def append(self, card: Card, deck_id: str | list[str]):
        if isinstance(deck_id, list):
            self.cards.setdefault(card, []).extend(deck_id)
        else:
            self.cards.setdefault(card, []).append(deck_id)
    

    def save(self, filename:str) -> str:
        filename = filename.translate(filename_translator)
        grimoire_path = rf"{PATH}{filename.replace('?','-')}.pkl"
        with open(grimoire_path, "wb") as outfile:
            pickle.dump(self, outfile)
        return round(os.stat(grimoire_path).st_size / 1024,2)


    def all_subtypes(self) -> list:
        subtypes = set()
        for card in self:
    
            subtypes.update(card.sub_types)
        return list(subtypes)


    def analyze(self, pooling:Pooling):
        subtypes = self.all_subtypes()  # ottieni tutti i sottotipi delle carte
        deck_aggregates = {}
        deck_grimoires = self.split() # ottieni un dict[deck_id,grimoire]
        
        for deck_id, grimoire in deck_grimoires.items():
            card_vectors = [card.vectorize(subtypes) for card in grimoire]
            deck_vector = pooling(card_vectors)
            deck_aggregates[deck_id] = deck_vector
        
        return (deck_aggregates.keys(), np.unique(deck_aggregates.values()))


    from typing import Callable
    def dataframe(self, 
                positive_filters: list[Callable[[Card], bool]] = None, 
                negative_filters: list[Callable[[Card], bool]] = None, 
                additional_data=None):
        import pandas as pd
        flattened_cards = [card.flatten(positive_filters, negative_filters, additional_data) for card in self]
        df = pd.concat([pd.DataFrame(card) for card in flattened_cards], ignore_index=True)
        return df


    def vectorize(self) -> dict[str, list[bool]]:
        """
        Restituisce un dict di vettori booleani (0 o 1) di lunghezza pari a quella del grimorio
        """
        vector: dict[str, list[bool]] = {}

        deck_ids = [deck_id for deck_list in self.values() for deck_id in deck_list]
        for deck_id in deck_ids:
            vector[deck_id] = [0] * len(self)

        for i, card in enumerate(self):
            for deck_id in self[card]:
                vector[deck_id][i] = 1
        
        return vector


    def similarity_matrix(self) -> np.ndarray:
        if len(self.split()) == 1:
            raise ValueError
        return similarity_matrix(self)


    def split(self) -> dict:
        """
        Returns:
            list[Grimoire]: grimori separati per deck_id
        """
        grimoires = []
        for deck_id in self.get_all_deck_ids():
            grimoire = Grimoire()
            for card, associated_deck_ids in self.items():
                if deck_id in associated_deck_ids:
                    grimoire.append(card,deck_id)
            grimoires.append(grimoire)
        return grimoires


    def get_all_deck_ids(self) -> set:
        return set(deck_id for deck_list in self.values() for deck_id in deck_list)
    

    def extract(self, deck_id:str) -> 'Grimoire':
        g = Grimoire()
        for card, deckids in self.items():
            if deck_id in deckids:
                g.append(card, deck_id)
        return g
    

    def remove(self, deck_id:str) -> bool:
        """_summary_ cancella da tutte le carte di un grimorio un deck_id, 
        poi rimuove carte senza deck_id
        Returns:
            True se almeno un deck_id è stato rimosso
        """
        removed = False
        for card in list(self):
            if deck_id in self[card]:
                self[card].remove(deck_id)
                removed = True
            
            if not self[card]:
                del self[card]

        return removed


def cosine_similarity(self, grim:Grimoire)->float:
    return cosine_similarity(self, grim)


# Metodi Statici
def merge(g1:Grimoire, g2:Grimoire) -> Grimoire:
    """Returns: 
        Grimoire: unione di g1 e g2
    """
    g = Grimoire()
    for card in {**g1, **g2}:
        g.append(card, g1.get(card, []) + g2.get(card, []))

    # g = Grimoire()
    # for card, deck_ids in g2.items():
    #     g.append(card, deck_ids)
    # for card, deck_ids in g1.items():
    #     g.append(card,deck_ids)
    return g


def load(filename:str, ask:bool=False, display:bool=True) -> Grimoire:
    """_summary_
    Args:
        filename (str): nome del file, senza percorso, ne` estensione
    Returns:
        Grimoire: il grimorio caricato
    """

    filename = filename.translate(filename_translator)
    grimoire_path = rf"{PATH}{filename}.pkl"

    if os.path.exists(grimoire_path):
        if display:
            print(f"Carico le carte dal grimorio di {filename}")    
        with open(grimoire_path, "rb") as infile:
            return pickle.load(infile)#grimoire
    return None




####################################
####    ____________________    ####
####    ----- Fetching -----    ####
####                            ####
####################################

from queue import Queue
from threading import Thread, Lock
import time, requests
import src.decks as decks
from src.decks import Deck
from src.by import By

def fetch(by:By, decks_filename:str, margin:int=0, n_thread:int=5, do_load:bool=True, do_save:bool=True):
    """
    Ottiene tutte le carte da mazzi già salvati.
    Args:
        by (By): tipo di ricerca usata per il mazzo (per commander, per nome, ...)
        decks_filename (str): nome del file mazzi
        margin (int): se un mazzo ha un numero di carte entro 100 ± margin, è accettato
        n_thread (int): thread applicati alle richieste API
        do_load (bool): verifica se è già presente un file grimorio, nel caso carica da quello
        do_save (bool): se True, salva il grimorio ottenuto

    Returns:
        Grimoire: la raccolta di carte e i mazzi in cui sono presenti

    Example:
        >>>fetch(By.COMMANDER, 'kodama', margin=10)
    """
    global queue, deck_num, errori, grimoire, decks_to_fetch, seen, lock
    
    if do_load:
        grimoire= load(decks_filename)
        if grimoire is not None:
            return grimoire
    
    deck_num = 0
    errori = 0
    grimoire = Grimoire()
    seen = []
    decks_to_fetch = decks.load(decks_filename)
    print(f'trovati {len(decks_to_fetch)} mazzi da fetchare per {decks_filename}')
    
    # Threads di richiesta e gestione
    queue = Queue()
    lock = Lock()
    threads = [Thread(target=fetch_cards, args=(decks_to_fetch,)) for _ in range(n_thread)]
    handle_thread = Thread(target=handle_cards, args=(margin,))
    
    for t in threads:
        t.start()
        time.sleep(0.2)          
    handle_thread.start()

    for t in threads:
        t.join()
    handle_thread.join(0.0)
    
    if do_save and len(grimoire)>0:
        decks.save(decks_to_fetch, decks_filename, by)
        file_dim = grimoire.save(decks_filename)
        print(f"Salvate {len(grimoire)} carte in {by.value}/{decks_filename}.pkl da Archidekt - {file_dim} kB")
    return grimoire



# def fetch_deck(filename:str, deck:Deck, check_if_playable=False, n_thread=2, try_load=True, do_save=True):
#     global queue, deck_num, errori, grimoire, decks_to_fetch, seen, lock
    
#     if try_load:
#         grimoire = load(filename)
#         if grimoire is not None:
#             return grimoire
    
#     deck_num = 0
#     errori = 0
#     grimoire = Grimoire()
#     seen = []
#     decks_to_fetch = [deck]

#     # Threads di richiesta e gestione
#     queue = Queue()
#     lock = Lock()
#     threads = [Thread(target=fetch_cards, args=(decks_to_fetch,)) for _ in range(n_thread)]
#     threads.append(Thread(target=handle_cards, args=(check_if_playable,)))
    
#     for t in threads:
#         t.start()
#         time.sleep(0.2)               
    
#     for t in threads:
#         t.join(timeout=2)
    
#     if do_save and len(grimoire)>0:
#         file_dim = grimoire.save(filename)
#         print(f"Salvate {len(grimoire)} carte in {filename}.pkl da Archidekt - {file_dim} kB")
    
#     return grimoire


# def fetch_decklist(decklist:list[Deck], check_if_playable=False, n_thread=3, try_load=True, do_save=True):
#     grimoire = Grimoire()
#     for deck in decklist:
#         deck.grimoire = fetch_deck(deck.name, deck, check_if_playable, n_thread, try_load, do_save)
#         grimoire = merge(grimoire, deck.grimoire)
#     return grimoire


# gestire le risposte
def handle_cards(margin):
    def sidesize(cards: list) -> int:
        return sum(1 for card in cards if isinstance(card.get('categories'), list) and any(cat in ['Sideboard', 'Maybeboard'] for cat in card.get('categories', [])))
    global grimoire, decks_to_fetch, seen
    handled_decks = {}
    while True:
        try:
            response, deck_id  = queue.get()
        except Exception as e:
            if queue.get() is None:
                raise(e)
            break
        
        handled_decks[deck_id] = True
        cards = response.json()["cards"]

        # Se la lunghezza del mazzo non è esatta, continua
        if 100-margin <= len(cards)-sidesize(cards) <= 100+margin:
            continue

        #Per ogni carta nella risposta GET
        for card_dict in cards:
            card = Card().load_dict(card_dict['card'])
            grimoire.append(card,deck_id)
            
            if card_dict['categories'] is not None and 'Commander' in card_dict['categories']:
                # Se è uno dei commander del mazzo, aggiungilo nell'header del deck
                decks.find(decks_to_fetch, deck_id).add_commander(card)
        
        print(f'Mazzi: {len(seen)}/{len(decks_to_fetch)}. {len(grimoire)} carte raccolte. {errori} errori', end='\r')



        
            



# effettuare richieste GET
def fetch_cards(decks_to_fetch:list):
    global seen, lock
    try:
        for deck in decks_to_fetch:
            # Permette di condividere la lista di mazzi tra più thread
            with lock:
                if deck.id in seen:
                    continue
                seen.append(deck.id)
            response = wait_valid_response(cards_url(deck.id))
            
            queue.put((response, deck.id))
            time.sleep(0.2) # per non sovraccaricare la API
    except Exception as e:
        print(f'{e}:  {deck}')


def cards_url(deck_id):
    return f'https://archidekt.com/api/decks/{deck_id}/'


def wait_valid_response(arg):
    global errori
    response = requests.get(arg)
    while response.status_code != 200:
        errori += 1
        if response.status_code == 429:
            time.sleep(4) # per non sovraccaricare la API
        response = requests.get(arg)
        time.sleep(0.4) # per non sovraccaricare la API
    return response


def cosine_similarity(grim1:Grimoire, grim2:Grimoire) -> float:
    ## Unisci i grimori
    g = merge(grim1,grim2)

    vectors = list(g.vectorize().values()) #[:2]
    if len(vectors) == 1:
        return 1.0

    v1, v2 = vectors[:2]
    dot_product = np.dot(v1, v2)
    
    n1, n2 = [np.linalg.norm(n) for n in [v1,v2]]
    
    if 0 in [n1,n2]:
        return 0.0
    
    return dot_product / (n1 * n2)

def similarity_matrix(splittable_grims:Grimoire) -> np.ndarray:
    
    grims = splittable_grims.split()
    n = len(grims)
    matrix = np.zeros((n,n))

    for i in range(n):
        for j in range(i, n):
            sim = cosine_similarity(grims[i], grims[j])
            matrix[i][j] = matrix[j][i]  = sim
            
    return matrix