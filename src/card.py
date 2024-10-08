from os.path import exists
from data.oracle_cards.oracle_cards_to_csv import update_oracle_cards
import csv, re
import numpy as np
from sklearn.preprocessing import OneHotEncoder
from enum import Enum, unique
from typing import Callable, TypeVar

class Rarity(Enum):
    common = 0
    uncommon = 1
    rare = 2
    mythic = 3
    special = 4


class Type(Enum):
    Artifact = 0
    Battle = 1
    Conspiracy = 2
    Creature = 3
    Dungeon = 4
    Enchantment = 5
    Kindred = 6
    Land = 7
    Instant = 8
    Phenomenon = 9
    Plane = 10
    Planeswalker = 11
    Scheme = 12
    Sorcery = 13
    Vanguard = 14
    Card = 15
    Emblem = 16

class Format(Enum):
    commander = 0
    oathbreaker = 1
    standardbrawl = 2
    brawl = 3
    paupercommander = 4
    duel = 5
    predh = 6

class Color(Enum):
    white = 'W'
    blue = 'U'
    red = 'R'
    black = 'B'
    green = 'G'

class SuperType(Enum):
    Legendary = 0
    Basic = 1
    Token = 2


@unique
class Filters(Enum):
    isColorless = lambda card: all(not v for v in card.colors.values())
    #Placeholders
    # isCreature = None
    # isLegalInCommander = None
    # isRare = None

    @classmethod
    def _generate_filters(cls):
        cls._generate_rarity_filters()
        cls._generate_legality_filters()
        cls._generate_type_filters()
        cls._generate_color_filters()

    @classmethod
    def _generate_color_filters(cls):
        for color_member in Color:
            name = f'is{color_member.name.capitalize()}'
            value = lambda card, color = color_member: card.color_identity[color.value]
            setattr(cls, name, value)

    @classmethod
    def _generate_rarity_filters(cls):
        for rarity_member in Rarity:
            name = f'is{rarity_member.name.capitalize()}'
            value = lambda card, rarity = rarity_member: card.rarity == rarity.value
            setattr(cls, name, value)

    @classmethod
    def _generate_type_filters(cls):
        for type_member in Type:
            name = f'is{type_member.name}'  
            value = lambda card, type_name = type_member.name: type_name in card.types
            setattr(cls, name, value)

        for type_member in SuperType:
            name = f'is{type_member.name}'  
            value = lambda card, type_name = type_member.name: type_name in card.super_types
            setattr(cls, name, value)

    @classmethod
    def _generate_legality_filters(cls):
        for format_member in Format:
            name = f'isLegalIn{format_member.name.capitalize()}'
            value = lambda card, format_name = format_member: card.is_legal(format_name)
            setattr(cls, name, value)

    def __new__(cls, *args):
        obj = object.__new__(cls)
        cls._generate_filters()
        return obj
    
Filters._generate_filters()

class Card():
    oracle_id : int
    mana_value : dict[str:int]                  # {W:1, U:0, R:0, B:1, G:0, C:2}
    mana_cost : int                             # 4
    color_identity : dict[str:bool]             # {W:T, U:F, R:F, B:T, G:F} 
    colors : dict[str:bool]                     # {W:T, U:F, R:F, B:T, G:F} 
    rarity : Rarity                             # 'rare'
    name : str                                  # 'Teysa Karlov'
    power : None|int                            # 2
    toughness : None|int                        # 4
    text : None|str                             # If a creature dying causes a trig...
    types : list[Type]                          # ['Creature']
    super_types : list[SuperType]               # Supertype.LEGENDARY
    sub_types : list[str]                       # ['Human', 'Advisor']
    keywords : list[str]                        # []
    mana_production : dict[str:int|bool|str]    # {W:0, U:0, R:0, B:0, G:0, C:0, Or:True, Cost:""}
    default_category : list[str]                # []
    legalities : dict[str:bool]


    def __repr__(self) -> str:
        return f"{self.name}"


    def __eq__(self,other):
        return self.oracle_id == other.oracle_id


    def __hash__(self):
        return hash(self.oracle_id)

    def __init__(self) -> None:
        pass

    def load_csv(self, csv_line:dict) :
    # if csv_line.isinstance(str):
    #     csv_line = next(csv.reader([csv_line], delimiter=',', quotechar='"'))
        self.oracle_id = csv_line[0]
        self.name = csv_line[1]
        self.rarity = csv_line[16]
        self.power = pot(csv_line[26])
        self.toughness = pot(csv_line[27])
        self.keywords = keywords(csv_line[10])
        self.text = text(self.keywords, csv_line[7])
        self.super_types, self.types, self.sub_types = split_typeline(csv_line[6])
        self.mana_value = mana_value(csv_line[4])
        self.colors = colors(csv_line[8])
        self.color_identity = colors(csv_line[9])
        self.mana_cost = int(float(csv_line[5]))
        self.legalities = legalities(csv_line)
        self.set = csv_line[12]
        self.mana_production = {}
        self.default_category = []
        #card.mana_production = card.get_mana_production()
        #card.default_category = csv_line[0] # same come sopra

    def load_dict(self, card_dict:dict):
        oracle = card_dict['oracleCard']
        
        self.oracle_id = oracle['id']
        self.color_identity = colors(oracle['colorIdentity'])
        self.rarity = card_dict['rarity']
        self.colors = colors(oracle['colors'])
        self.name = oracle['name']
        self.power = pot(oracle['power'])
        self.toughness = pot(oracle['toughness'])
        self.legalities = oracle['legalities']
        self.text = oracle['text']
        self.types = oracle['types']
        self.super_types = oracle['superTypes']
        self.sub_types = oracle['subTypes']
        self.mana_value = mana_value(oracle['manaCost'])
        self.mana_cost = oracle['cmc']
        self.mana_production = oracle['manaProduction']
        self.default_category = oracle['defaultCategory']
        return self

    def search_in_csv(self, oracle_id:str=None, name:str=None):
        CSV_PATH = "./data/oracle_cards/oracle_cards.csv"
        if not exists(CSV_PATH):
            print("Ricreo il file csv")
            CSV_PATH = update_oracle_cards()
        
        with open(CSV_PATH, 'r',encoding="UTF-8", errors="ignore") as infile:
            reader = csv.reader(infile,delimiter=',')

            for row in reader:
                if (oracle_id is not None and row[0] == oracle_id) or (name is not None and row[1] == name):
                    print(row)
                    self.load_csv(row)

    def vectorize(self, all_subtypes:list):
        # Costi      
        color_identity_vec = [int(color in "".join(self.color_identity)) for color in "WURBGC"]
        colors_vec = [int(color in self.colors) for color in "WURBGC"]
        mana_cost_vec = [int(self.mana_cost)]

        mana_value_vec = [value for value in self.mana_value.values()]
        
        # Produzione
        mana_production_vec = ([int(value) for color, value in self.mana_production.items() if color in "WURBGC"]
            + [int(self.mana_production.get('Or', False))])
        
        # Rarità
        rarity_vec = [Rarity[self.rarity].value]
        
        # Tipi, Sottotipi, Supertipi
        subtype_encoder = OneHotEncoder()
        subtype_encoder.fit(np.array(all_subtypes).reshape(-1, 1))
        if self.sub_types != []:
            subtypes_vec = np.sum(subtype_encoder.transform(np.array(self.sub_types).reshape(-1, 1)).toarray(), axis=0)
        else:
            # Restituisce un vettore di zeri della stessa lunghezza delle categorie dei subtypes
            subtypes_vec = np.zeros(subtype_encoder.categories_[0].shape[0])
        
        types_vec = [int(t in self.types) for t in Type]
        supertypes_vec = [int(t in self.super_types) for t in SuperType]

        # Forza/Costituzione
        power_vec = [int(self.power) if self.power.isdigit() else 0]
        toughness_vec = [int(self.toughness) if self.toughness.isdigit() else 0]
        
        color_identity_vec = np.array(color_identity_vec)
        colors_vec = np.array(colors_vec)
        rarity_vec = np.array(rarity_vec)
        power_vec = np.array(power_vec)
        toughness_vec = np.array(toughness_vec)
        types_vec = np.array(types_vec)
        supertypes_vec = np.array(supertypes_vec)
        subtypes_vec = np.array(subtypes_vec)  # Convertire la lista in un array NumPy
        mana_value_vec = np.array(mana_value_vec)
        mana_cost_vec = np.array(mana_cost_vec)
        
        # Concatenazione di tutti i vettori
        card_vector = np.concatenate([
            color_identity_vec, 
            colors_vec, 
            rarity_vec, 
            power_vec, 
            toughness_vec, 
            types_vec, 
            supertypes_vec, 
            subtypes_vec.flatten(), 
            mana_value_vec, 
            mana_production_vec, 
            mana_cost_vec
        ])

        return card_vector
    
    def line(self, predicate, values=None):
        name = self.name.replace("'","''").replace('//', '')
        line = f"{predicate}('{name}'"
        if values is not None:
            for value in values:
                if isinstance(value,str):
                    if "'" in value:
                        value = value.replace("'","''")
                    if '//' in value:
                        value = value.replace('//', '-')
                    if "!" in value:
                        value = value.replace("!","")
                
                    value = f"'{value}'"
                line += f',{value}'
        return line+')'

    def to_facts(self) -> str:

        facts = []
        facts.append(self.line('card'))
        facts.append(self.line('cost', [self.mana_cost]))
        for color, value in self.mana_value.items():
            if value > 0:
                facts.append(self.line('mana_value', [color,value]))
        
        for color, has_color in self.color_identity.items():
            if has_color:
                facts.append(self.line('color_identity', [color,value]))

        for color, is_color in self.colors.items():
            if is_color:
                facts.append(self.line('color', [color,value]))

        facts.append(self.line('rarity', [self.rarity]))
        if self.power.isdigit() :
            facts.append(self.line('power', [self.power]))
            facts.append(self.line('toughness', [self.toughness]))

        if len(self.text)>0:
            facts.append(self.line('text', [self.text]))

        for t in self.types:
            facts.append(self.line('type', [t]))

        for sup in self.super_types:
            facts.append(self.line('super_type', [sup]))
        
        for sub in self.sub_types:
            facts.append(self.line('sub_type', [sub]))

        for kw in self.keywords:
            if len(kw)>0:
                facts.append(self.line('keyword', [kw]))

        for key, value in self.mana_production.items():
            if self.mana_production['Cost'] == "":
                break
            elif (value.isdigit() and value>0) or key == "Or":
                facts.append(self.line('mana_production',[key,value]))

        return facts

    def to_dict(self):
        return {
            'oracle_id' : self.oracle_id,
            'name': self.name,
            'types' : self.types,
            'super_types' : self.super_types,
            'sub_types' : self.sub_types,
            'colors' : self.colors,
            'color_identity' : self.color_identity,
            'mana_value' : self.mana_value,
            'mana_cost' : self.mana_cost,
            'mana_production' : self.mana_production,
            'rarity' : self.rarity,
            'text' : self.text,
            #'keywords' : self.keywords,
            'default_category' : self.default_category,
            'power' : self.power,
            'toughness' : self.toughness,
        }
    
    CardType = TypeVar('CardType', bound='Card')
    def flatten(self, 
                positive_filters: list[Filters] = None,
                negative_filters: list[Filters] = None,
                additional_data: dict[str, Callable[[CardType], int]] = None
            ) -> dict:
        for filter in positive_filters:
            if not filter(self): # questo sarebbe il filtro
                return {}
            
        for filter in negative_filters:
            if filter(self): # questo sarebbe il filtro
                return {}
            
        flat = {
            "mana_cost": [self.mana_cost],
            "rarity": [rarity_mapping[self.rarity]],
            # **{f"mana_value_{k}": [v] for k, v in self.mana_value.items()},
            # **{f"color_identity_{k}": [int(v)] for k, v in self.color_identity.items()},
            # **{f"color_identity_none": int(all(v is False for v in self.color_identity.values()))},
            # **{f"colors_{k}": [int(v)] for k, v in self.colors.items()},
        }
        

        if Filters.isCreature in filters:
            flat = { **flat,
                **{"toughness": [self.toughness]},
                **{"power": [self.power]}
                }
        if additional_data:
            for key, func in additional_data.items():
                flat[key] = func(self)
        
        return flat
    
    #MOLTO WIP, non usare #To-Do
    def get_mana_production(self)->dict: 
        match = re.search(r'\.?\s*(.*?)\s*Add\s+(.*)\.', self.text)
        if not match:
            return None
        
        #suppongo ci sia un costo di attivazione
        try:
            cost, mana_produced = self.text.split(':',1)
        except Exception as e:
            # print(e)
            # print(self)
            # print(self.text)
            cost, mana_produced = self.text.split('.',1)
        mana_dict = {"W": 0, "U": 0, "R": 0, "B": 0, "G": 0, "C":0, "Or": True, "Note": "", "cost":cost}

        # trova i simboli tra {}
        mana_symbols = re.findall(r'\{([WUBRGC])\}', mana_produced)

        if mana_symbols:
            # Add {*} for each [...]
            if "for each" in mana_produced:
                quality_match = re.search(r'for each (\w+)', mana_produced)
                if quality_match:
                    x = quality_match.group(1)
                    for symbol in mana_symbols:
                        mana_dict[symbol] = "X"
                    mana_dict["Note"] = f"for each {x}"
            else:
                for symbol in mana_symbols:
                    mana_dict[symbol] += 1
                    mana_dict["Or"] = False

        # Add X mana of any color
        QUANTITY = {"one":1, "two":2, "three":3, "four":4, "five":5, "X":"X"}
        quantity_match = re.search(r'Add (\w+) mana of any color', mana_produced)
        if quantity_match:
            x = quantity_match.group(1)
            for symbol in "WURBG":
                mana_dict[symbol] = QUANTITY[x]
        return  mana_dict
    
    def abs_mana_production(self) ->int:
        HIGH = 10
        prod = self.get_mana_production()
        if prod is None: return 0
        if 'for each' in prod['Note']: return HIGH
        if prod['Or']:
            return max([v for k,v in prod.items() if k in 'WURBGC'])
        else:
            return sum(v for k,v in prod.items() if k in 'WURBGC')
        
    
    def __len__(self) -> int :
        return len(self.name)
    
    
    def count_mana_production(self) -> int:
        return self.text.count('add ')
    
    def count_trigger_abilities(self) -> int:
        import re
        triggered_ability_pattern = r'\b(Whenever|When|At the beginning of|At the end of|If)\b'
        matches = re.findall(triggered_ability_pattern, self.text)
        return len(matches)
    
    def count_active_abilities(self) -> int:
        return self.text.count(':')
    

    def is_legal(self, format:Format=Format.commander) -> bool:
        return self.legalities[format.name]

def legalities(csv_line):
    import json
    return json.loads(csv_line[11].replace( "'",'"').lower())

supertypes_mapping = {'': 0, 'Token':1, 'Basic':2, 'Legendary':3}  
rarity_mapping = {'':0, 'common':0, 'uncommon':1, 'rare':2, 'mythic':3, 'special':4, 'bonus':4}
def opt(dict, condition, result={}):
    return dict if condition else result

def vld(dict:dict, alt={}):
    return opt(dict, list(dict.values())[0] is not None and  list(dict.values())[0] != '', {list(dict.keys())[0]:0})

def keywords(kw:str) -> list:
    return kw[1:-1].replace("'", '').replace(" ", '').split(',')

def text(keywords:list, t:str) -> str:
    return t.strip().replace("'", "''")
#   si è rivelato troppo complicato, abort
    # if len(keywords) == 1:
    #     return t.strip().replace("'", "''")
    # caps = 0
    # i=0
    # while caps<len(keywords)+1 and len(t)>i:
    #     if t[i].isupper():
    #         caps +=1
    #     i+=1
    # return t[i-1:].strip().replace("'", "''")

def mana_value(mv:str) ->dict:
    mana_value = {color:mv.count(color)  for color in "WURBGC"}
    if len(mv)>0 and mv[1].isdigit():
        mana_value['C']+= int(mv[1])
    return mana_value

def pot(pot:str)-> int:
    if pot is None or pot == '': return 0
    if not pot[0].isdigit(): return 0
    if '*' in pot: 
        pot = pot.replace('*', '0').replace('+', '')
    try:
        return int(pot)
    except:
        return 0

def colors(ci:list) -> dict:
    translator = {'W':'White','U':'Blue','B':'Black','R':'Red','G':'Green'}
    return {k: k in ci for k,v in translator.items()}



def split_typeline(typeline:str) -> tuple: 
    supertypes = [type.name for type in SuperType if type.name in typeline]
    types = [type.name for type in Type if type.name in typeline]

    if Type.Plane.name in types and Type.Planeswalker.name not in types:
        subtypes = [typeline.split('—')[1][1:]]
    else:
        try:
            subtypes = typeline.split('//')[1].split(" ")[1:]
        except:
            try:
                subtypes = typeline.split('—')[1].split(" ")[1:]
            except:
                subtypes = []


    return (supertypes, types, subtypes)


    









