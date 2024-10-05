import json, csv
FILENAME = "oracle-cards-20241005090218.json"


def read_cards(path = f"./data/oracle_cards/{FILENAME}")-> dict:#of dicts
    with open(path, "rb") as infile:
        return json.load(infile)


def fixed_cards(cards = read_cards()) -> list:#of dicts
    delenda = ["object", "lang", "id", "multiverse_ids", "mtgo_id", "mtgo_foil_id", "tcgplayer_id", "cardmarket_id", "released_at", "scryfall_uri" ,"highres_image", "games", "variation",
            "image_status", "image_uris", "reserved", "oversized", "promo", "foil", "nonfoil", "set_id", "set_type", "collector_number", "textless", "illustration_id",
            "story_spotlight", "finishes", "reprint", "set_search_uri", "scryfall_set_uri", "full_art", "textless", "booster", "prices", "purchase_uris", "related_uris", "digital", "prints_search_uri"]

    cleaned = []
    for card in cards:
        for term in delenda:
            if term in card.keys():
                del card[term]
        fix_legalities(card)
        fix_newlines(card)
        cleaned.append(card)
    return cleaned

MULTILINE_FIELDS = ["oracle_text", "flavor_text"]
def fix_newlines(card):
    for k,v in card.items():
        if k in MULTILINE_FIELDS:
            card[k] = "".join(v.split("\n"))


LEGAL_FORMATS = ["commander","oathbreaker","standardbrawl","brawl","paupercommander","duel","predh"]
TRANSLATOR = {"not_legal":False, "banned":False, "restricted":False, "legal":True}
def fix_legalities(card) -> dict:#of strings:strings/bool
    is_legal = False
    for format in list(card['legalities'].keys()):
        if format not in LEGAL_FORMATS:
            del card["legalities"][format]
        else:
            card["legalities"][format] = TRANSLATOR[card["legalities"][format]]
            if card["legalities"][format] == True:
                is_legal = True

    if not is_legal:
        card = None
    return card

def get_fieldnames(cards)->list:#of strings
    fields = []
    for card in cards:
        for field in card.keys():
            fields.append(field)
    return list(dict.fromkeys(fields))

def update_oracle_cards(path = 'oracle_cards.csv'):
    cards = fixed_cards()
    fieldnames = get_fieldnames(cards)
    with open(path, 'w') as csvfile:
        csvfile.truncate()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for card in cards:
            writer.writerow(card)
    return path

if __name__ == "__main__":
    update_oracle_cards()