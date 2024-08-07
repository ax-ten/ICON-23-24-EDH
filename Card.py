class Card():
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)
    
    def __repr__(self) -> str:
        return f"{type(self).__name__}: {self.name}"


    def __init__(self, card_dict):
        oracle = card_dict['oracleCard']
        self.oracle_id = card_dict['uid']
        self.color_identity = oracle['colorIdentity']
        self.rarity = card_dict['rarity']
        self.colors = oracle['colors']
        self.name = oracle['name']
        self.power = oracle['power']
        self.toughness = oracle['toughness']
        self.text = oracle['text']
        self.types = oracle['types']
        self.super_types = oracle['superTypes']
        self.sub_types = oracle['subTypes']
        self.mana_value = oracle['manaCost']
        self.mana_cost = oracle['cmc']
        self.mana_production = oracle['manaProduction']
        self.default_category = oracle['defaultCategory']


