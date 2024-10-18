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
        """
        Creates and loads the 'OMNI' dataset containing all available Magic: The Gathering cards.

        This method checks if the 'OMNI' dataset has already been loaded. If not, it reads the `oracle_cards.csv` file
        to load card data, creates `Card` objects for each entry, and appends them to the current object. Once all cards
        are loaded, it saves the dataset for future use. If the 'OMNI' dataset is already available, it loads the 
        existing data instead of recreating it.

        Returns:
            self: The current instance with the loaded card data.

        Raises:
            FileNotFoundError: If the `oracle_cards.csv` file cannot be found or opened.

        Example:
            omni = Grimoire().make_omni()
        """
        if load('OMNI') is None:
            CSV_PATH = "./data/oracle_cards/oracle_cards.csv"
    
            with open(CSV_PATH, 'r',encoding="UTF-8", errors="ignore") as infile:
                reader = csv.reader(infile,delimiter=',')
                head = next(reader)
                for row in reader:
                    card = Card().load(row)
                    self.append(card)
            
            self.save('OMNI')
        else:
            self.cards = load('OMNI',display=False).cards
        return self
    

    def append(self, card: Card, deck_id: str | list[str]):
        """
        Adds a deck ID or a list of deck IDs associated with a given card to the `cards` dictionary.

        This method appends a deck ID (or multiple deck IDs) to the list of deck IDs for the provided `card` 
        in the `cards` dictionary. If the card is not already present in the dictionary, it creates a new entry.

        Args:
            card (Card): The card object for which the deck ID(s) will be appended.
            deck_id (str | list[str]): A single deck ID (str) or a list of deck IDs (list[str]) to be associated 
            with the card.

        Example:
            card_manager.append(some_card, "deck_123")  # Adds deck_123 to the card's entry.
            card_manager.append(some_card, ["deck_123", "deck_456"])  # Adds both deck IDs to the card's entry.
        """
        if isinstance(deck_id, list):
            self.cards.setdefault(card, []).extend(deck_id)
        else:
            self.cards.setdefault(card, []).append(deck_id)
    

    def save(self, filename:str) -> str:
        """
        Saves the current object to a pickle file with the given filename.

        This method serializes the current object and stores it as a `.pkl` file in the specified path.
        The filename is cleaned up by replacing certain characters (like `?`), and the file size is returned in kilobytes.

        Args:
            filename (str): The name of the file where the object will be saved. 
                            Special characters are translated based on `filename_translator`.

        Returns:
            str: The size of the saved file in kilobytes (rounded to two decimal places).

        Example:
            file_size_kb = grimoire.save("my_grimoire_file")  
            # Saves the current object as "my_grimoire_file.pkl" and returns the file size.
        """
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
        """
        Analyzes the cards in the grimoire and aggregates their data by deck.

        This function splits the grimoire into individual decks and converts the cards in each deck into vectors. 
        These vectors are then pooled together using the provided pooling function (e.g., mean, sum) to create a single aggregated vector for each deck.
        Finally, it returns the deck IDs and unique aggregated vectors.

        Args:
            pooling (Pooling): A function used to aggregate the card vectors in each deck (e.g., averaging the vectors).

        Returns:
            tuple: A tuple containing:
                - A list of deck IDs (keys of `deck_aggregates`).
                - A NumPy array of unique aggregated vectors for all decks.

        Example:
            deck_ids, unique_vectors = grimoire.analyze(mean_pooling_function)
        """
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
        """
        Creates a pandas DataFrame from the cards in the current object, applying optional filters.

        This method flattens each card in the current object using the provided positive and negative filters,
        and then concatenates the resulting data into a single pandas DataFrame. 
        Positive filters are functions that determine whether a card meets certain criteria, while negative filters
        are used to exclude cards that do not meet specified conditions. 

        Args:
            `positive_filters (list[Callable[[Card], bool]], optional)`: A list of functions that return True for 
            cards that should be included in the DataFrame.
            
            `negative_filters (list[Callable[[Card], bool]], optional)`: A list of functions that return True for 
            cards that should be excluded from the DataFrame.
            
            `additional_data (optional)`: Any extra data to be included in the flattening process of the cards.

        Returns:
            `pd.DataFrame`: A pandas DataFrame containing the flattened data of the cards after applying filters.

        Example:
            df = grimoire.dataframe(positive_filters=[Filters.isLegalInCommander], negative_filters=[Filters.isColorless])
            # Creates a DataFrame of playable cards that are not banned.
        """
        import pandas as pd
        flattened_cards = [card.flatten(positive_filters, negative_filters, additional_data) for card in self]
        df = pd.concat([pd.DataFrame(card) for card in flattened_cards], ignore_index=True)
        return df


    def vectorize(self) -> dict[str, list[bool]]:
        """
        Creates a binary vector representation for each deck based on the cards it contains.

        This method generates a dictionary where each `key` is a deck ID and the corresponding `value`
        is a list of booleans indicating the presence (1) or absence (0) of each card in the current object. 
        The length of the boolean list corresponds to the number of cards in the object.

        Returns:
            vector(dict[str, list[bool]]): A dictionary mapping deck IDs to their respective binary vectors.
            Each vector has a length equal to the number of cards, with a 1 at index i indicating 
            that the card at index i is included in the deck.

        Example:
            vector_representation = grimoire.vectorize()
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
        Splits the current collection of cards into separate Grimoires based on their associated deck IDs.

        This method iterates over all deck IDs and creates a separate Grimoire for each deck,
        appending the cards associated with that deck to the respective Grimoire.

        Returns:
            dict(str, list[Grimoire]): A dictionary mapping each deck ID to its corresponding Grimoire object.

        Example:
            grimoires_by_deckid = grimoires.split()
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
        """
        Estrae un sottogruppo di carte associate a un dato deck_id.

        Questa funzione crea un nuovo oggetto Grimoire contenente solo le carte 
        associate a un determinato deck_id presente nel grimorio corrente.

        Args:
            deck_id (str): L'identificativo del mazzo di cui si desidera estrarre le carte.

        Returns:
            Grimoire: Un nuovo grimorio che contiene solo le carte associate al deck_id specificato.
        """
        g = Grimoire()
        for card, deckids in self.items():
            if deck_id in deckids:
                g.append(card, deck_id)
        return g
    

    def remove(self, deck_id:str) -> bool:
        """
        Removes a specified deck ID from all cards in the Grimoire.

        This method iterates through each card in the Grimoire and removes the provided 
        deck ID from the list of associated deck IDs for that card. If a card no longer 
        has any associated deck IDs after the removal, it will be deleted from the Grimoire.

        Args:
            deck_id (str): The ID of the deck to be removed from each card.

        Returns:
            bool: True if at least one deck ID was removed from any card; False otherwise.
        
        Example:
            success = grimoire.remove('deck123')
        will remove 'deck123' from all cards in the Grimoire and return True if any removals occurred.
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
    """
    Merges two Grimoires into a single Grimoire.

    This function combines the contents of two Grimoire objects, g1 and g2. 
    For each unique card in either Grimoire, it appends the card to the 
    resulting Grimoire and associates it with all deck IDs from both 
    g1 and g2.

    Args:
        g1 (Grimoire): The first Grimoire to merge.
        g2 (Grimoire): The second Grimoire to merge.

    Returns:
        Grimoire: A new Grimoire containing the union of cards and their 
        associated deck IDs from both g1 and g2.

    Example:
        merged_grimoire = merge(grimoire1, grimoire2)
    This will create a new Grimoire containing all cards from both grimoire1 and grimoire2.
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
    """
    Loads a Grimoire from a specified file.

    This function attempts to load a Grimoire object from a pickle file 
    located in the specified path. The filename should not include the 
    file extension.

    Args:
        filename (str): The name of the file, without the path or extension.
        ask (bool, optional): If set to True, the user will be prompted before loading. Defaults to False.
        display (bool, optional): If set to True, a message will be displayed when loading the Grimoire. Defaults to True.

    Returns:
        Grimoire: The loaded Grimoire object, or None if the file does not exist.

    Example:
        grimorio = load('Kodama of the West Tree')
    This will load the Grimoire from '{PATH}/Kodama of the West Tree.pkl' if it exists.
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
    Fetches all cards from already saved decks.

    This function retrieves cards from decks specified in the given filename. 
    It can load existing decks, save the fetched cards, and allows for multithreaded 
    fetching of cards from an API based on the specified search type.

    Args:
        by (By): The type of search used for the deck (e.g., by commander, by name, etc.).
        decks_filename (str): The name of the file containing the decks.
        margin (int): Acceptable range for the number of cards in a deck (within ±margin of 100).
        n_thread (int): The number of threads to be applied to API requests.
        do_load (bool): If True, checks for an existing Grimoire file and loads it if present.
        do_save (bool): If True, saves the fetched Grimoire to a file.

    Returns:
        Grimoire: A collection of cards and the decks in which they are present.

    Example:
        >>> fetch(By.COMMANDER, 'kodama', margin=10)
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
    """
    Handles the processing of cards fetched from the API.

    This function retrieves cards for each deck from a queue and processes them,
    adding valid cards to the global Grimoire. It checks the total card count against
    a specified margin and handles sideboards.

    Args:
        margin (int): Acceptable range for the number of cards in a deck (within ±margin of 100).
    """
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
    """
    Fetches card data for a list of decks from the API.

    This function iterates over a list of decks, retrieves their card data,
    and puts the responses in a queue for further processing. It ensures
    that each deck is only fetched once using a thread-safe approach.

    Args:
        decks_to_fetch (list): List of deck objects to fetch cards for.
    """
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
    """
    Waits for a valid HTTP response from a GET request.

    This function continuously sends a GET request to the specified URL
    until a successful response (status code 200) is received. It handles
    rate limiting by waiting when a 429 status code is encountered.

    Args:
        arg (str): The URL to send the GET request to.

    Returns:
        Response: The valid response object from the GET request.

    Increments:
        errori (int): A global counter for tracking the number of errors 
                    encountered during the requests.
    """
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
    """
    Calcola la similarità coseno tra due grimori.

    Questa funzione unisce due oggetti Grimoire e calcola la similarità coseno 
    tra i loro vettori. La similarità coseno misura l'angolo tra due vettori 
    in uno spazio n-dimensionale, producendo un valore compreso tra -1 e 1, 
    dove 1 indica che i vettori sono identici, 0 indica che sono ortogonali, 
    e -1 indica che sono opposti.

    Args:
        grim1 (Grimoire): Il primo grimorio da confrontare.
        grim2 (Grimoire): Il secondo grimorio da confrontare.

    Returns:
        float: Il valore di similarità coseno tra i due grimori. 
                Se uno dei grimori è vuoto, restituisce 0.0.
    """
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
    """
    Calcola una matrice di similarità coseno tra i grimori contenuti in un oggetto Grimoire.

    Questa funzione suddivide un grimorio in più grimori, calcola la similarità coseno 
    tra ogni coppia di grimori e restituisce una matrice quadrata che rappresenta 
    le similarità tra tutti i grimori.

    Args:
        splittable_grims (Grimoire): Il grimorio da suddividere e analizzare.

    Returns:
        np.ndarray: Una matrice di similarità coseno, dove l'elemento (i, j) 
                    rappresenta la similarità tra l'i-esimo il j-esimo grimorio .
    """
    grims = splittable_grims.split()
    n = len(grims)
    matrix = np.zeros((n,n))

    for i in range(n):
        for j in range(i, n):
            sim = cosine_similarity(grims[i], grims[j])
            matrix[i][j] = matrix[j][i]  = sim
            
    return matrix