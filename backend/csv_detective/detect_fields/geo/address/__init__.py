from csv_detective.process_text import _mini_process_text
import re
PROPORTION = 1

def _is(s):
    #Add by chokki
    s = _mini_process_text(s)
    reg1 = r"\d+\s+\w+\s+(?:st(?:\.|reet)?|ave(?:nue)?|lane|blvd|boulevard|dr(?:\.|ive)?)"
    #reg2 = r"^[\d]+[A-z\s,]+[\d]"
    #Addr# Street Name, City, State ZIP code
    reg3 = r"^(\\d{1,}) [a-zA-Z0-9\\s]+(\\,)? [a-zA-Z]+(\\,)? [A-Z]{2} [0-9]{5,6}$"

    # Original code is possibly wrong:
    # oldValue.length is out of range for charAt since the last index is at oldValue.length-1
    # !isNaN(parseInt(oldValue.charAt(oldValue.length), 10)))
    """try:
        int(s[len(s) - 1])
        last_char_is_int = True
    except ValueError:
        last_char_is_int = False"""

    voies = [
        'street',
        'road',
        'lane',
        'drive',
        'dr',
        'rd',
        'ln',
        'st',
        'st.',
        'blvd',
        'aire',
        'allee',
        'avenue',
        'ave',
        'district',
        'base',
        'boulevard',
        'cami',
        'carrefour',
        'chemin',
        'gare',
        'station',
        'cheminement',
        'chaussee',
        'cite',
        'city',
        'province',
        'clos',
        'coin',
        'corniche',
        'cote',
        'cour',
        'Cours',
        'Domaine',
        'Descente',
        'Ecart',
        'Esplanade',
        'Faubourg',
        'Gare',
        'Grande Rue',
        'Hameau',
        'Halle',
        'Ilot',
        'Impasse',
        'Lieu dit',
        'Lotissement',
        'Marche',
        'Montee',
        'Parc',
        'Passage',
        'Place',
        'Plan',
        'Plaine',
        'Plateau',
        'Pont',
        'Port',
        'Promenade',
        'Parvis',
        'Quartier',
        'Quai',
        'Residence',
        'Ruelle',
        'Rocade',
        'Rond Point',
        'Route',
        'Rue',
        'Sente - Sentier',
        'Square',
        'Tour',
        'Terre-plein',
        'Traverse',
        'Villa',
        'Village',
        'Voie',
        'Zone artisanale',
        'Zone d’amenagement concerte',
        'Zone d’amenagement differe',
        'Zone industrielle',
        'Zone',
        'r',
        'av',
        'pl',
        'bd',
        'cami',
        'che',
        'chs',
        'dom',
        'ham',
        'ld',
        'pro',
        'rte',
        'vlge',
        'za',
        'zac',
        'zad',
        'zi',
        'car',
        'fg',
        'lot',
        'imp',
        'qu',
        'mte'
    ]

    arrval = s.split(' ')
    match = False
    for val in arrval:
        a = any([val == x.lower() for x in voies])
        if a:
            match = True

    return (match or (re.search(reg1, s.lower()) is not None) or (re.search(reg3, s.lower()) is not None))
    #return (re.search(reg1, s) is not None) or match
