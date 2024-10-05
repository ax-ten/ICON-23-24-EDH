import owlready2
from prompt_toolkit import prompt
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
from enum import Enum

class OntologyCompleter(Completer):
    def __init__(self, ontology):
        self.classes = [cls.name for cls in ontology.classes()]
        self.object_properties = [prop.name for prop in ontology.object_properties()]
        self.individuals = [ind.name for ind in ontology.individuals()]

class OntologyClassCompleter(OntologyCompleter):
    def get_completions(self, document, complete_event):
        text = document.text
        for name in self.classes:
            if name.startswith(text):
                yield Completion(name, start_position=-len(text))

class OntologyIndividualCompleter(OntologyCompleter):
    def get_completions(self, document, complete_event):
        text = document.text
        for name in self.individuals:
            if name.startswith(text):
                yield Completion(name, start_position=-len(text))

class OntologyPropertyClassCompleter(OntologyCompleter):
    def get_completions(self, document, complete_event):
        text = document.text
        for name in self.object_properties:
            if name.startswith(text):
                yield Completion(name, start_position=-len(text))

class Completer(Enum):
    CLASS = (OntologyClassCompleter, 'la classe')
    INDIVIDUAL = (OntologyIndividualCompleter, 'l\'individuo')
    PROPERTY = (OntologyPropertyClassCompleter, 'la proprietà')

def get_onto():
    from rdflib import Graph
    from owlready2 import get_ontology
    # Percorso al file dell'ontologia in formato Turtle
    ontology_path = "data/Ontology/mtg_ontology_updated.owl.tll"

    # Crea un grafo RDF e carica il file Turtle usando rdflib
    g = Graph()
    g.parse(ontology_path, format="turtle")

    # Salva il grafo RDF in un formato supportato da owlready2 (come RDF/XML)
    converted_ontology_path = "data/Ontology/converted_mtg_ontology.owl"
    g.serialize(destination=converted_ontology_path, format="xml")

    # Carica l'ontologia convertita usando owlready2
    return get_ontology(converted_ontology_path).load()

def search_items(completer:Completer):
    onto = get_onto()
    item_searched = prompt(
        f"Inserisci il nome de{completer.value[1]} desiderata: ",
        completer=completer.value[0](onto),
        auto_suggest=AutoSuggestFromHistory()
    )

    try:
        item = onto.search(iri=f"*{item_searched}")[0]
        # Trova tutti gli oggetti di tipo 'item'
        items = onto.search(is_a=item)
        return items
    except Exception as e:
        print(e)
