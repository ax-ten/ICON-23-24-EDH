import src.decks as decks, src.grimoire as grimoire
import re, os, pickle, sys
from src.by import By
from src.card import Card
from simple_term_menu import TerminalMenu

def advice_cards():
    options = [
        "[1] Cerca il commander per nome (potrebbero volerci alcuni minuti)", 
        "[2] Seleziona file già scaricati"
    ]

    print("Consigliami delle carte per il mio commander")
    terminal_menu = TerminalMenu(options)
    menu_entry_index = terminal_menu.show()
    
    match(menu_entry_index):
        case 0: #cerca per nome
            commander = input("Inserisci il nome del commander:  ")
            while not commander_exists(commander):
                commander = input("Non lo trovo, inserisci nuovamente rispettando le maiuscole:  ")

            fetched_decks = decks.load(commander)
            if fetched_decks is None:
                fetched_decks = decks.fetch(By.COMMANDER, commander)
                
            while fetched_decks is None:
                commander = input("Riproviamo, Inserisci il nome del commander:  ")
                fetched_decks = decks.load(commander)
            fetched_grimoire = grimoire.fetch(By.COMMANDER, commander)
            
        case 1: #grimorio da file
            PATH = "./data/fetched/"
            file_list = list_files()
            print("Scegli uno tra i seguenti file")
            file_entry_index = TerminalMenu(file_list)
            with open(PATH + file_list[file_entry_index], "rb") as infile:
                fetched_grimoire =  pickle.load(infile)
            
    #consiglia carte


def commander_exists(commander_name) -> bool:
    try:
        c = Card(name=commander_name)
        return "Legendary" in c.super_types and "Creature" in c.types
    except Exception as e:
        return False


def list_files(directory="./data/fetched", pattern=""):
    return [file for file in os.listdir(directory) if os.path.isfile(os.path.join(directory, file)) and file.endswith("_grimoire.pickle")]


def advice_commander():
    #in base al mio profilo
    #in base ad un tema particolare
    # Aggiungi altri siti di deckbuilding oltre archidekt
    
    PATH = "./data/fetched/"
    owner = input("Inserisci il tuo nome utente su Archidekt:  ") #STUBBARONI ne ha 111
    decks.fetch(By.OWNER, owner)
    fetched_grimoire = grimoire.from_decks(owner)
    with open(PATH + owner + "_decks.pickle", "rb") as infile:
        fetched_decks = pickle.load(infile)

    #ottieni lista di commander di ownerA 
    owner_commanders = decks.get_commanders(fetched_decks)
    similar_owners = []
    for commander in owner_commanders:
        fetched_decks = decks.fetch(By.COMMANDER,commander.name)
        for deck in fetched_decks:
            similar_owners.append(deck['owner'])

    #similar_owners.sort()
    for owner in similar_owners[:40]:
        similar_decks = decks.fetch(By.OWNER, owner['username'])
    
    #sort similar_decks per similarita` ai decks del primo owner`




def info_onto():
    import webbrowser
    from src.ontology import search_items, Completer
    options = [
        "[1] Visualizzala su WebOwl",
        "[2] Cerca una Classe", 
        "[3] Cerca un Individuo",
        "[4] Cerca una Proprietà"
    ]
    print("Info sull'ontologia")
    terminal_menu = TerminalMenu(options)
    menu_entry_index = terminal_menu.show()
    completer = []
    
    match(menu_entry_index):
        case 0:
            print("Assicurati di caricare il file corretto")
            webbrowser.open("https://service.tib.eu/webvowl/")
        case 1:
            completer = Completer.CLASS
        case 2:
            completer = Completer.INDIVIDUAL
        case 3:
            completer = Completer.PROPERTY
    
    if completer:
        for item in search_items(completer):
            print(f" - {item}")


def info_KB():
    pass


def main():
    os.system('clear')
    while True:
        options = [
            "[1] Consigliami delle carte per il mio commander", 
            "[2] Consigliami dei Commander", 
            "[3] Info sull'ontologia",
            "[4] Info sulla Knowledge Base",
            "[q] Termina esecuzione"
        ]
        print("Benvenut!")
        terminal_menu = TerminalMenu(options)
        menu_entry_index = terminal_menu.show()
        
        match(menu_entry_index):
            case 0:
                advice_cards()
            case 1:
                advice_commander()
            case 2:
                info_onto()
            case 3:
                info_KB()
            case 4:
                sys.exit(1)



if __name__ == "__main__":
    main()