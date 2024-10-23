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
        o = object.__new__(cls)
        cls._generate_filters()
        return o
    
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
    legalities : dict[str:bool]                 # ['commander': True, 'oathbreaker':True ...]



    def __repr__(self) -> str:     return f"{self.name}"
    def __eq__(self,other):        return self.oracle_id == other.oracle_id
    def __hash__(self):        return hash(self.oracle_id)
    def __init__(self) -> None: pass


    def load(self, source:dict|csv.DictReader):
        """
        Loads data from a given source into the current object, mapping values based on a predefined key-to-attribute mapping.

        This method takes a source of type `dict` or `csv.DictReader`, and uses the `LOAD_MAPPING` attribute of the class
        to assign values to the corresponding object attributes.

        Args:
            source (dict or csv.DictReader): 
                The data source containing attribute values to load. 
                - If `source` is a `dict`, it is expected to contain key-value pairs corresponding to object attributes.
                - If `source` is a `csv.DictReader`, the values are extracted from the appropriate column in the CSV.

        Raises:
            ValueError: If `source` is not of type `dict` or `csv.DictReader`.

        Mapping Logic:
            - The method iterates over `self.LOAD_MAPPING`, where each entry is a tuple containing:
                - `keys`: A tuple of possible keys for `dict` and `csv.DictReader` sources.
                - `transform`: A transformation function applied to the value if not `None`.
            - For each attribute, the corresponding value is extracted from the `source` using the appropriate key based on the source type.
            - If a `transform` function is provided, the value is transformed before being assigned to the attribute.

        Returns:
            self: The instance of the class, with attributes populated from the source.

        Example:
            card_instance.load({'name': 'Black Lotus', 'mana_cost': '0'})

        """
        if    isinstance(source, dict):           k = 1
        elif  isinstance(source, csv.DictReader): k = 0
        else: raise ValueError("source deve essere di tipo dict o csv.DictReader")

        for attribute,  (keys, transform) in self.LOAD_MAPPING.items():
            value = source[keys[k]] if keys[k] in source else source['oracleCard'][keys[k]]
            if transform:
                value = transform(value)
            setattr(self, attribute, value)


        return self


    def search(self, oracle_id:str=None, name:str=None):
        """
        Searches for a card in the oracle_cards CSV file by `oracle_id` or `name`.
        If a match is found, it loads the card details using `self.load_csv`.

        Args:
            oracle_id (str, optional): The oracle ID of the card to search for. Defaults to None.
            name (str, optional): The name of the card to search for. Defaults to None.

        Raises:
            ValueError: Raised if neither `oracle_id` nor `name` is provided, or if no match is found.

        Notes:
            - If the CSV file does not exist, it recreates it by calling `update_oracle_cards`.
            - Only one of `oracle_id` or `name` needs to be provided for the search.

        Example:
            instance.search(oracle_id="abc123")
            instance.search(name="Black Lotus")
        """
        if oracle_id == None and name == None:
            raise ValueError("Specifica almeno uno tra oracle_id o name")
        CSV_PATH = "./data/oracle_cards/oracle_cards.csv"
        if not exists(CSV_PATH):
            print("Ricreo il file csv")
            CSV_PATH = update_oracle_cards()
        
        with open(CSV_PATH, 'r',encoding="UTF-8", errors="ignore") as infile:
            reader = csv.reader(infile,delimiter=',')

            for row in reader:
                if (oracle_id is not None and row[0] == oracle_id) or (name is not None and row[1] == name):
                    print(row)
                    self.load(row)
                    break
        raise ValueError(f"Non è stata trovata alcuna carta per {(oracle_id or name)}")
        



    def vectorize(self, all_subtypes:list):
        """
        Converts card attributes into a numerical vector representation.

        This method generates a vector that encodes various aspects of the card, such as its color identity, 
        mana costs, rarity, types, subtypes, power, toughness, and other relevant properties.

        Args:
            all_subtypes (list): A list of all possible subtypes available in the dataset, used for one-hot encoding.

        Returns:
            np.array: A concatenated NumPy array representing the card in a numerical format, suitable for machine learning tasks.

        Vector Components:
            - **color_identity_vec**: One-hot encoding for the card's color identity ("W", "U", "R", "B", "G", "C").
            - **colors_vec**: One-hot encoding for the card's actual colors.
            - **mana_cost_vec**: A list containing the card's total mana cost.
            - **mana_value_vec**: Values representing the converted mana cost of each element in the mana cost.
            - **mana_production_vec**: A vector representing the mana produced by the card.
            - **rarity_vec**: Numerical encoding of the card's rarity.
            - **subtypes_vec**: One-hot encoding of the card's subtypes using a fitted `OneHotEncoder`.
            - **types_vec**: One-hot encoding for the card's primary types (e.g., Creature, Sorcery).
            - **supertypes_vec**: One-hot encoding for the card's super types (e.g., Legendary).
            - **power_vec**: Integer representation of the card's power (if applicable).
            - **toughness_vec**: Integer representation of the card's toughness (if applicable).

        Example:
            card_vector = card_instance.vectorize(all_subtypes=subtypes_list)

        Notes:
            - The method uses OneHotEncoder to encode subtypes dynamically, based on the list of all possible subtypes provided.
            - Handles empty subtype lists by returning a zero vector for subtypes.
            - Power and toughness are converted to integers, with non-numeric values defaulting to 0.
        """
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

    # def line(self, predicate, values=None):
    #     name = self.name.replace("'","''").replace('//', '')
    #     line = f"{predicate}('{name}'"
    #     if values is not None:
    #         line += ','.join(f"'{value.replace('\'', '\'\'').replace('//', '-').replace('!', '')}'" 
    #             for value in values if isinstance(value, str))

    #     return line+')'

    fact_mapping = {
        'mana_cost':      lambda o, v: o.line('cost', [v]),
        'mana_value':     lambda o, v: [o.line('mana_value', [color, value]) for color, value in v.items() if value > 0],
        'color_identity': lambda o, v: [o.line('color_identity', [color]) for color, has_color in v.items() if has_color],
        'colors':         lambda o, v: [o.line('color', [color]) for color, is_color in v.items() if is_color],
        'rarity':         lambda o, v: o.line('rarity', [v]),
        'power':          lambda o, v: o.line('power', [v]) if v.isdigit() else None,
        'toughness':      lambda o, v: o.line('toughness', [v]) if v.isdigit() else None,
        'text':           lambda o, v: o.line('text', [v]) if len(v) > 0 else None,
        'types':          lambda o, v: [o.line('type', [t]) for t in v],
        'super_types':    lambda o, v: [o.line('super_type', [sup]) for sup in v],
        'sub_types':      lambda o, v: [o.line('sub_type', [sub]) for sub in v],
        'keywords':       lambda o, v: [o.line('keyword', [kw]) for kw in v if len(kw) > 0],
        'mana_production': lambda o, v: [o.line('mana_production', [key, value]) for key, value in v.items() if (value.isdigit() and int(value) > 0) or key == "Or"]
    }

    # def to_facts(self) -> str:
    #     facts = []
    #     facts.append(self.line('card'))
    #     facts.append(self.line('cost', [self.mana_cost]))
    #     for color, value in self.mana_value.items():
    #         if value > 0:
    #             facts.append(self.line('mana_value', [color,value]))
        
    #     for color, has_color in self.color_identity.items():
    #         if has_color:
    #             facts.append(self.line('color_identity', [color,value]))

    #     for color, is_color in self.colors.items():
    #         if is_color:
    #             facts.append(self.line('color', [color,value]))

    #     facts.append(self.line('rarity', [self.rarity]))
    #     if self.power.isdigit() :
    #         facts.append(self.line('power', [self.power]))
    #         facts.append(self.line('toughness', [self.toughness]))

    #     if len(self.text)>0:
    #         facts.append(self.line('text', [self.text]))

    #     for t in self.types:
    #         facts.append(self.line('type', [t]))

    #     for sup in self.super_types:
    #         facts.append(self.line('super_type', [sup]))
        
    #     for sub in self.sub_types:
    #         facts.append(self.line('sub_type', [sub]))

    #     for kw in self.keywords:
    #         if len(kw)>0:
    #             facts.append(self.line('keyword', [kw]))

    #     for key, value in self.mana_production.items():
    #         if self.mana_production['Cost'] == "":
    #             break
    #         elif (value.isdigit() and value>0) or key == "Or":
    #             facts.append(self.line('mana_production',[key,value]))

    #     return facts
    def to_facts(self) -> str:
        facts = []
        for key, transform in self.fact_mapping.items():
            value = getattr(self, key)
            if value is not None:
                result = transform(self, value)
                if isinstance(result, list):
                    facts.extend(result)
                elif result:
                    facts.append(result)

        return facts

    def to_dict(self):
        return {attr: getattr(self, attr) for attr in self.LOAD_MAPPING}
    
    def flatten(self, 
                positive_filters: list[Filters] = None,
                negative_filters: list[Filters] = None,
                additional_data: dict[str, Callable['Card', int]] = None # type: ignore
            ) -> dict:
        """Flatten the attributes of the Card object based on provided filters and additional data.

    Args:
        positive_filters (list[Filters], optional): A list of filter functions that must all return True for 
            the Card to be included in the flattened output.
        negative_filters (list[Filters], optional): A list of filter functions that must all return False for 
            the Card to be included in the flattened output. 
        additional_data (dict[str, Callable['Card', int]], optional): A dictionary of additional data to 
            include in the flattened output. The keys are the names of the fields, and the values are functions 
            that take a Card instance as input and return an integer.

    Returns:
        dict: A dictionary containing the flattened attributes of the Card. The dictionary includes:
            - 'mana_cost': The mana cost of the Card.
            - 'rarity': The rarity of the Card.
            - 'toughness': (if Filters.isCreature in positive_filters) The toughness of the Creature.
            - 'power': (if Filters.isCreature in positive_filters) The power of the Creature.
            - Any additional fields specified in the `additional_data` argument, with their corresponding values calculated using the provided functions.

    Example:
        >>> card = Card().load('Kodama of the West Tree)  # Assume Card is properly defined
        >>> card.flatten(additional_data={f"mana_value_{k}": [v] for k, v in self.mana_value.items()})
        {'mana_cost': [3], 
        'rarity': ['mythic'], 
        'mana_value_G': 1,
        'mana_value_C': 2}
    """
        if not all(f(self) for f in positive_filters) or any(f(self) for f in negative_filters):
            return {}
            
        flat = {
            "mana_cost": self.mana_cost,
            "rarity": rarity_mapping[self.rarity],
            # **{f"mana_value_{k}": v for k, v in self.mana_value.items()},
            # **{f"color_identity_{k}": int(v)]for k, v in self.color_identity.items()},
            # **{f"color_identity_none": int(all(v is False for v in self.color_identity.values()))},
            # **{f"colors_{k}": int(v) for k, v in self.colors.items()},
        }
        
        if Filters.isCreature in positive_filters:
            flat = { **flat,
                **{"toughness": self.toughness},
                **{"power": self.power}
                }
        if additional_data:
            for key, func in additional_data.items():
                flat[key] = func(self)

        flat = {key: [value] for key, value in flat.items()}

        
        return flat
    
    #MOLTO WIP, non usare #To-Do
    def get_mana_production(self)->dict: 
        """
        Extracts and interprets the mana production information from the card's text.

        This method parses the card's text to identify mana production capabilities, extracting both the mana
        symbols produced and any additional notes such as conditions (e.g., "for each" clause) or variable amounts
        of mana (e.g., "Add X mana of any color").

        Returns:
            dict: A dictionary representing the mana production, with the following structure:
                - **W, U, R, B, G, C**: Count of each respective mana symbol produced.
                - **Or**: A boolean flag indicating whether the mana production is flexible
                - **Note**: Any additional notes or conditions (e.g., "for each creature").
                - **cost**: The activation cost.

        Mana Parsing Logic:
            - Searches the card's text for "Add" followed by mana symbols enclosed in `{}`.
            - Handles cases where mana is produced "for each" of a particular quality (e.g., creature or land).
            - Identifies generic mana production (e.g., "Add X mana of any color") and maps words like "one", "two", "three", etc. to their numeric equivalents.
            - Extracts the activation cost, if present, which appears before a colon `:` in the card's text.

        Example:
            mana_dict = card_instance.get_mana_production()

        Notes:
            - If the card does not contain mana production information, the method returns `None`.
            - The method accounts for variable mana amounts (X) and specific conditions tied to mana production.
        """
        match = re.search(r'\.?\s*(.*?)\s*Add\s+(.*)\.', self.text)
        if not match:
            return None
        
        #suppongo ci sia un costo di attivazione
        try:
            cost, mana_produced = self.text.split(':',1)
        except Exception as e:
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


    @staticmethod
    def _pot(pot:str)-> int:
        if pot is None or pot == '': return 0
        if not pot[0].isdigit(): return 0
        if '*' in pot: 
            pot = pot.replace('*', '0').replace('+', '')
        try:
            return int(pot)
        except:
            return 0

    @staticmethod 
    def _keywords(kw:str) -> list:
        return kw[1:-1].replace("'", '').replace(" ", '').split(',')
    
    @staticmethod
    def _text(t:str, keywords:list=None) -> str:
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

    @staticmethod
    def _mana_value(mv:str) -> dict:
        mana_value = {color:mv.count(color)  for color in "WURBGC"}
        if len(mv)>0 and mv[1].isdigit():
            mana_value['C']+= int(mv[1])
        return mana_value


    @staticmethod
    def _colors(ci:list) -> dict:
        translator = {'W':'White','U':'Blue','B':'Black','R':'Red','G':'Green'}
        return {k: k in ci for k,v in translator.items()}
    

    # def _split_typeline(typeline:str) -> tuple: 
    #     supertypes = [type.name for type in SuperType if type.name in typeline]
    #     types = [type.name for type in Type if type.name in typeline]

        
    #     return (supertypes, types, subtypes)

    def _types(typeline:str) -> list[str]:
        return [type.name for type in Type if type.name in typeline]

    def _supertypes(typeline:str) -> list[str]:
        return [type.name for type in SuperType if type.name in typeline]

    def _subtypes(typeline:str|list) -> list[str]:
        if isinstance(typeline, list):
            return typeline
        if '—' in typeline:
            return typeline.split('—')[1].strip().split()
        return []
        # if Type.Plane.name in _types(typeline) and Type.Planeswalker.name not in types:
        #     subtypes = [typeline.split('—')[1][1:]]
        # else:
        #     try:
        #         subtypes = typeline.split('//')[1].split(" ")[1:]
        #     except:
        #         try:
        #             subtypes = typeline.split('—')[1].split(" ")[1:]
        #         except:
        #             subtypes = []
        # return subtypes

    @staticmethod
    def _legalities(line:str|list)->dict:
        if isinstance(line, dict):
            return line
        import json
        return json.loads(line[11].replace( "'",'"').lower())
        
    LOAD_MAPPING = {
        'oracle_id':    ([0, 'id'],         None),
        'name':         ([1, 'name'],       None),
        'rarity':       ([16, 'rarity'],    None),
        'power':        ([26, 'power'],     _pot),
        'toughness':    ([27, 'toughness'], _pot),
        'keywords':     ([10, 'text'],      _keywords),
        'text':         ([7, 'text'],       _text),  
        'super_types':  ([6, 'superTypes'], _supertypes),
        'types':        ([6, 'types'],      _types),
        'sub_types':    ([6, 'subTypes'],   _subtypes),
        'mana_value':   ([4, 'manaCost'],   _mana_value),
        'colors':       ([8, 'colors'],     _colors),
        'color_identity':([9,'colorIdentity'], _colors),
        'mana_cost':    ([5, 'cmc'],        int),  
        # 'set':          ([12, 'set'],       None),  
        'legalities':   ([None,'legalities'], _legalities),  
        'mana_production': ([None, 'manaProduction'], None),  
        'default_category': ([None, 'defaultCategory'], None),
    }

supertypes_mapping = {'': 0, 'Token':1, 'Basic':2, 'Legendary':3}  
rarity_mapping = {'':0, 'common':0, 'uncommon':1, 'rare':2, 'mythic':3, 'special':4, 'bonus':4}
def opt(dict, condition, result={}):
    return dict if condition else result

def vld(dict:dict, alt={}):
    return opt(dict, list(dict.values())[0] is not None and  list(dict.values())[0] != '', {list(dict.keys())[0]:0})


    









