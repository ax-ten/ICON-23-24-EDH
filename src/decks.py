import os, pickle
from src.by import By
from src.card import Card
filename_translator = {ord(i):None for i in '".?/:;><'}


class Deck():
    def __init__(self, deck:dict, grimoire=None) -> None:
        self.id = deck['id']
        self.name = deck['name']
        self.owner = deck['owner']['username']
        self.colors = deck['colors']
        self.tags = deck['tags']
        self.last_update = deck['updatedAt']
        self.commanders = []
        self.grimoire = grimoire 
    
    def add_commander(self, commander:Card):
        self.commanders.append(commander)
    
    def set(self, grimoire):
        self.grimoire = grimoire
    
    def __repr__(self) -> str:
        if self.commanders != []:
            return f"Commander: {self.commanders[0]}{' '*(30-len(self.commanders[0]))}{self.name}"
        return f"{self.name}"
    
    def save(self, ask=False) -> str:
        import re
        TRANSLATE = {
            By.COMMANDER:self.commanders[0],
            By.OWNER:self.owner,
            By.DECKNAME:self.name
        }
        PATH = f"./data/fetched/{by.value}/{TRANSLATE[by]}.pkl"
        
        re.sub(r'[^\w_. -]', '-', PATH)
        while ask:
            user_input = input(f"Vuoi salvare {PATH}? S/n").lower()
            if user_input == 'n': return
            ask = not(user_input == 's'|user_input == '')
        
        with open(PATH, "wb") as outfile:
            pickle.dump(self, outfile)
        return round(os.stat(PATH).st_size / 1024,2)
    
    def vector(self, read_grimoire=False) -> list :
        v=self.colors.values()
        if read_grimoire:
            if self.grimoire == None:
                raise ValueError(f"Il mazzo {self.name} non ha alcun grimorio associato")
            
            # v = [colori, power, toughness, tipi, sottotipi, keyword]
            for card in self.grimoire:
                v[6] += card.power
                v[7] += card.toughness
                v += card.types + card.sub_types #+card.keywords 
        
        [' '.join(self.tags)]
        # v = [colori, tags]
        for tag in self.tags:
            v.append(tag)
        return v


def save(decks, filename, by:By, ask=False) -> str:
    filename = filename.translate(filename_translator)

    PATH = rf"./data/fetched/{by.value}/{filename}.pkl"
    
    while ask:
        user_input = input(f"Vuoi salvare {PATH}? S/n").lower()
        if user_input == 'n': return
        ask = not(user_input == 's'|user_input == '')
    
    with open(PATH, "wb") as outfile:
        pickle.dump(decks, outfile)
    return round(os.stat(PATH).st_size / 1024,2)
#    print(f'Ho salvato {len(decks)} mazzi in "{PATH}" - {round(os.stat(PATH).st_size / 1024,2)} kB')


from src.by import By
def load(filename:str, by:By=None):
    filename = filename.translate(filename_translator)
    paths = [f'./data/fetched/{(by or b).value}/{filename}.pkl' for b in By]
    
    for path in paths:
        if os.path.exists(path):
            with open(path, "rb") as infile:
                return pickle.load(infile)
    return None


def find(my_decks:list, deck_id: int):
    for deck in my_decks:
        if deck.id == deck_id:
            return deck
    return None

def get_commanders(my_decks:list) -> set:
    commanders = []
    for deck in my_decks:
        for commander in deck.commanders:
            commanders.append(commander)
    return set(commanders)


#### ----- DECK FETCHER ----- ####
import requests, time, src.by as by
from queue import Queue
from threading import Thread, Lock
from urllib.parse import quote


def fetch(by:By, query_arg:str, n_thread=3, do_load=True, do_save=True, upper_limit=600) -> list[Deck]:
    """Ottieni una lista di oggetti Deck cercandoli per nome del commander, per username del loro owner, 
        o per nome del mazzo. 
    
    Args:
        by (By): tipologia di ricerca, una tra By.COMMANDER, By.OWNER, By.DECKNAME
        query_arg (str): parametro di ricerca, elemento in comune ai mazzi da cercare
        n_thread (int, optional): Numero di Thread da applicare alla ricerca. Defaults to 3.
        do_load (bool, optional): Se Vera, prova a caricare il mazzo dai dati gia' salvati. Defaults to True.
        do_save (bool, optional): Se Vera, salva i mazzi dopo averli ottenuti. Defaults to False.
        upper_limit (int, optional): Limite massimo alla lista di mazzi ottenibile. Defaults to 300.

    Returns:
        list[Deck]: lista di mazzi conformanti a by e query_arg
    """    
    global decks, page, queue, errori, deck_count, lock
    
    if do_load:
        decks= load(query_arg, by)
        if decks is not None and len(decks)!=0:
            print(f"Carico {len(decks)} mazzi per {query_arg}")
            return decks
    
    page = 0
    decks = []
    errori = 0
    
    queue = Queue()
    threads = [Thread(target=fetch_data, args=(by,query_arg)) for _ in range(n_thread)]
    threads.append(Thread(target=handle_response))
    deck_count = min(wait_valid_response(url_by(by,query_arg,page=1)).json()["count"],upper_limit)

    while deck_count <1:
        print(f"Non riesco a trovare mazzi per {query_arg}???", end='\r')
        time.sleep(0.5)
        deck_count = min(wait_valid_response(url_by(by,query_arg,page=1)).json()["count"],upper_limit)
    
    print(f"Ho trovato {deck_count}{'+' if deck_count==600 else ''} mazzi per {query_arg} da Archidekt", end='\r')
    
    lock = Lock()
    for t in threads:
        time.sleep(0.1)
        t.start()
        
    for t in threads:
        t.join(timeout=5)

    if do_save and deck_count>0:
        file_dim = save(decks,query_arg,by)
        print(f"Salvati {deck_count} mazzi in {by.value}/{query_arg}.pkl da Archidekt - {file_dim} kB")
    return decks


# effettuare richieste GET
def fetch_data(by:by, query_arg:str):
    global page, queue, deck_count, lock
    while page*50 < deck_count:
        with lock:
            page = page + 1    
            local_page = page 
        response = wait_valid_response(url_by(by,query_arg,page=local_page))
        
        queue.put(response)
        time.sleep(0.2) # non sovraccaricare l'API


def handle_response():
    global page, decks, queue, deck_count
    while len(decks) < deck_count:
        try:
            response = queue.get(timeout=4)
        except:
            print("Non riesco ad aggiungere altri mazzi, procedo oltre                ")
            break
        data = response.json()["results"]
        
        for deck_info in data:
            decks.append(Deck(deck_info))
        print(f'Ho raccolto {len(decks)} mazzi su', end='\r')


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


def url_by(by:by, arg:str, page:int, format=3):
    archidekt_url = 'https://archidekt.com/api/decks/cards/'
    if " " in arg:
        arg = f'"{quote(arg)}"'
    return archidekt_url + f'?{by.value}={arg}&formats={format}&page={page}&pageSize=50'