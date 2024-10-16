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

    def __iter__(self)->list[Card]: return iter(self.cards)
    def __len__(self)->list[Card]:  return len(self.cards)
    def __getitem__(self, key): return self.cards[key]
    def __delitem__(self, card): del self.cards[card]
    def __contains__(self, card): return card in self.cards
    def keys(self):             return self.cards.keys()
    def values(self):           return self.cards.values()
    def items(self):            return self.cards.items()

    def __repr__(self) -> str:
        s = ''
        for card in self.keys():
            s= s + f'{card}\n'
        return s
    
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
    

    def vectorize(self) -> dict[int, list[bool]]:
        vector: dict[int, list[bool]] = {}

        deck_ids = [deck_id for deck_list in self.values() for deck_id in deck_list]
        for deck_id in deck_ids:
            vector[deck_id] = [0] * len(self)

        for i, card in enumerate(self):
            for deck_id in self[card]:
                vector[deck_id][i] = 1
        
        return vector

    # def vectorize(self, do_types=True, do_subtypes=False, do_keywords=False):
    #     from collections import Counter as C
    #     vector = {}
    #     total_len = 0
    #     for card, ids in self.items():
    #         freq = len(ids)
    #         if do_types: vector = C(vector) + C(count(self, card.types, freq))
    #         if do_subtypes:  vector = C(vector) + C(count(self, card.sub_types, freq))
    #         if do_keywords:  vector = C(vector) + C(count(self, card.keywords, freq))
    #         total_len += freq

    #     return vector

    def similarity_matrix(self) -> np.ndarray:
        if len(self.split()) == 1:
            raise ValueError
        return similarity_matrix(self.split())

    
    def split(self) -> dict:
        """_summary_
        Returns:
            grimoires (dict[int,Grimoire]): grimori separati per deck_id
        """

        grimoires = {}
        for deck_id in self.get_all_deck_ids():
            grimoires[deck_id] = Grimoire()
            for card, associated_deck_ids in grimoire.items():
                if  deck_id in associated_deck_ids:
                    grimoires[deck_id].append(card,deck_id)
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
        """
        summary: cancella da tutte le carte di un grimorio un deck_id, 
        poi rimuove carte senza deck_id
        """
        removed = False
        for card in list(self):
            if deck_id in self[card]:
                self[card].remove(deck_id)
                removed = True
            
            if not self[card]:
                del self[card]

        return removed


def count(grim:Grimoire, dict, freq):
    vector = {}
    for type in dict:
        vector[type] = freq
    return vector

def cosine_similarity(self, grim:Grimoire)->float:
    return cosine_similarity(self, grim)



# Metodi Statici
def merge(g_A:Grimoire, g_B:Grimoire):
    for card, deck_ids in g_B.items():
        g_A.append(card, deck_ids)
    return g_A


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
    
    # ### Chiediti cosa è sta roba sotto
    # decks.load(filename)
    # if os.path.exists(filename):
    #     print(f"Sono presenti mazzi da sfogliare per {filename}")
    #     while ask:
    #         user_input = input(f"Vuoi salvare il grimorio? S/n").lower()
    #         if user_input == 'n':
    #             return
    #         ask = not(user_input == 's'|user_input == '')
    #     return fetch(filename)
    return None






#### ----- Fetching ----- ####
from queue import Queue
from threading import Thread, Lock
import time, requests
import src.decks as decks
from src.decks import Deck
from src.by import By

def fetch(by:By, decks_filename:str, check_if_playable=False, n_thread=5, do_load=True, do_save=True):
    global queue, deck_num, errori, grimoire, decks_to_fetch, seen, lock
    
    if do_load:
        grimoire= load(decks_filename)
        if grimoire is not None:
            return grimoire
    
    deck_num = 0
    errori = 0
    grimoire = Grimoire()
    seen = {}
    decks_to_fetch = decks.load(decks_filename)
    print(f'trovati {len(decks_to_fetch)} mazzi da fetchare per {decks_filename}')
    
    # Threads di richiesta e gestione
    queue = Queue()
    lock = Lock()
    threads = [Thread(target=fetch_cards, args=(decks_to_fetch,)) for _ in range(n_thread)]
    threads.append(Thread(target=handle_cards, args=(check_if_playable,)))
    
    for t in threads:
        t.start()
        time.sleep(0.2)          
    
    for t in threads:
        t.join(timeout=3)
    
    if do_save and len(grimoire)>0:
        decks.save(decks_to_fetch, decks_filename, by)
        file_dim = grimoire.save(decks_filename)
        print(f"Salvate {len(grimoire)} carte in {by.value}/{decks_filename}.pkl da Archidekt - {file_dim} kB")
    return grimoire


def fetch_deck(filename:str, deck:Deck, check_if_playable=False, n_thread=2, try_load=True, do_save=True):
    global queue, deck_num, errori, grimoire, decks_to_fetch, seen, lock
    
    if try_load:
        grimoire = load(filename)
        if grimoire is not None:
            return grimoire
    
    deck_num = 0
    errori = 0
    grimoire = Grimoire()
    seen = {}
    decks_to_fetch = [deck]

    # Threads di richiesta e gestione
    queue = Queue()
    lock = Lock()
    threads = [Thread(target=fetch_cards, args=(decks_to_fetch,)) for _ in range(n_thread)]
    threads.append(Thread(target=handle_cards, args=(check_if_playable,)))
    
    for t in threads:
        t.start()
        time.sleep(0.2)               
    
    for t in threads:
        t.join(timeout=2)
    
    if do_save and len(grimoire)>0:
        file_dim = grimoire.save(filename)
        print(f"Salvate {len(grimoire)} carte in {filename}.pkl da Archidekt - {file_dim} kB")
    
    return grimoire


def fetch_decklist(decklist:list[Deck], check_if_playable=False, n_thread=3, try_load=True, do_save=True):
    grimoire = Grimoire()
    for deck in decklist:
        deck.grimoire = fetch_deck(deck.name, deck, check_if_playable, n_thread, try_load, do_save)
        merge(grimoire, deck.grimoire)
    return grimoire


# gestire le risposte
def handle_cards(check_if_playable):
    from _queue import Empty
    global grimoire, decks_to_fetch
    handled_decks = {}
    while len(handled_decks) < len(decks_to_fetch):
        try:
            response, deck_id = queue.get(timeout=10)
        except Empty:
            print("Non riesco ad aggiungere altre carte, procedo oltre                \n")
            break
        except Exception as e:
            raise(e)
        
        handled_decks[deck_id] = True
        
        # Se la lunghezza del mazzo non è esatta, continua
        if check_if_playable and response.json()["cards"] != 100:
            continue

        #Per ogni carta nella risposta GET
        for card_dict in response.json()["cards"]:
            card = Card().load_dict(card_dict['card'])
            grimoire.append(card,deck_id)
            
            if card_dict['categories'] is not None and 'Commander' in card_dict['categories']:
                # Se è uno dei commander del mazzo, aggiungilo nell'header del deck
                decks.find(decks_to_fetch, deck_id).add_commander(card)
        
        print(f'Ho raccolto {len(grimoire)} carte finora', end='\r')
            



# effettuare richieste GET
def fetch_cards(decks_to_fetch:list):
    global seen, lock
    try:
        for deck in decks_to_fetch:
            # Permette di condividere la lista di mazzi tra più thread
            with lock:
                if deck.id in seen.keys():
                    continue
                seen[deck.id] = True

            response = wait_valid_response(cards_url(deck.id))
            queue.put((response, deck.id))
            time.sleep(0.4) # per non sovraccaricare la API
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
    #vettorizzali e scarta i deck_id
    # se sono più di due darà errore

    vectors = list(g.vectorize().values()) #[:2]
    if len(vectors) == 1:
        return 1.0

    v1, v2 = vectors[:2]
    dot_product = np.dot(v1, v2)
    
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    
    if 0 in [norm1,norm2]:
        return 0.0
    
    return dot_product / (norm1 * norm2)

def similarity_matrix(grims:dict[str:Grimoire]) -> np.ndarray:
    n = len(grims)
    grims = list(grims.values())
    matrix = np.zeros((n,n))

    for i in range(n):
        for j in range(i, n):
            sim = cosine_similarity(grims[i], grims[j])
            matrix[i][j] = matrix[j][i]  = sim
            
    return matrix