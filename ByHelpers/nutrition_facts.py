#-*- coding: utf-8-*-

import unicodedata
import string
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import re


NUTRIMENTS = [
    {
        "key": "calories",
        "match": ["calories", "calorias", "cals", "calorie", "caloria", "cal", "calory", "kilocalories", "ener", "energy", "energia", 'kcal'],
        "name": "Calories",
        "name_es": "Calorias"
    },
    {

        "key": "niacin",
        "match": ["nia", "niacin", "niacina"],
        "name": "Niacin",
        "name_es": "Niacina"
    },
    {
        "name": "Docosahexaenoic Acid",
        "name_es": "Ácido Docosahexaenoico",
        "key": "dha",
        "match": ["docosahexaenoic", "docosahexaenoico", "dha"]
    },
    {
        "name": "Riboflavin",
        "name_es": "Riboflavina",
        "key": "riboflavin",
        "match": ["riboflavin", "riboflavina", "ribf"]
    },
    {
        "name": "Potassium",
        "name_es": "Potasio",
        "key": "k",
        "match": ["potassium", "potasio", "k"],
        "description": "Potasio"
    },
    {
        "name": "Vitamin E",
        "name_es": "Vitamina E",
        "key": "vite",
        "match": ["vite", "vitamin e", 'vitamina e'],
    },
    {
        "name": "Iodized Salt",
        "name_es": "Yodo",
        "key": "iodine",
        "match": ["iodized_salt", "yodo", 'sal iodada']
    },
    {
        "name": "Sodium",
        "name_es": "Sodio",
        "key": "sodium",
        "match": ["sodio", "sodium", "na"],
    },
    {
        "name": "Carnitine",
        "name_es": "Carnitina",
        "key": "carnitine",
        "match": ["carnitine", "l carnitine", "carnitina"],
        "description": "Carnitina"
    },
    {
        "name": "Thiamin",
        "name_es": "Tiamina",
        "key": "tiamin",
        "match": ["thia", "thiamin", "thiamine","tiamina", "vitb1", "vitb1", "vitamina b1", "vitamine b1"]
    },
    {
        "name": "Fat",
        "name_es": "Grasas",
        "key": "fat",
        "match": ["fat", "grasa", "grasas", "acidos grasos"],
    },
    {
        "name": "Saccharose",
        "name_es": "Sacarosa",
        "key": "saccharose",
        "match": ["saccharose", "sacarosa"]
    },
    {
        "name": "Vitamin C",
        "name_es": "Vitamina C",
        "key": "vitc",
        "match": ["vitc", "vitc", "vitamina c", "vitamin c"],
    },
    {
        "name": "Erythritol",
        "name_es": "Eritritol",
        "key": "eritritol",
        "match": ["eritritol", "erythritol"]
    },
    {
        "name": "Carbohydrate",
        "name_es": "Carbohidratos",
        "key": "carbohydrate",
        "match": ["carbohydrate", "carbohidrato", "choavl"]
    },
    {
        "name": "Lactose",
        "name_es": "Lactosa",
        "key": "lactose",
        "match": ["lactose", "lactosa"]
    },
    {
        "name": "Zinc",
        "name_es": "Zinc",
        "key": "zinc",
        "match": ["zinc", "zn"]
    },
    {
        "name": "Folic Acid",
        "name_es": "Ácido Fólico",
        "key": "folic_acid",
        "match": ["folic acid", "acido folico", "acid folico", "acido folic", "acid folic", "foldfe"]
    },
    {
        "name": "Vitamin A",
        "name_es": "Vitamina A",
        "key": "vita",
        "match": ["vita", "vita", "vitamina a", "vitamin a"]
    },
    {
        "name": "Vitamin D",
        "name_es": "Vitamina D",
        "key": "vitd",
        "match": ["vitd", "vitd", "vitamina d", "vitamin d"]
    },
    {
        "name": "Polyunsaturated Fat",
        "name_es": "Grasas Poliinsaturadas",
        "key": "poly_fat",
        "match": ["fapucis", "polyunsaturated fat", "grasas poliinsaturadas", "grasa poliinsaturada"]
    },
    {
        "name": "Monounsaturated Fat",
        "name_es": "Grasas Monoinsaturadas",
        "key": "mono_fat",
        "match": ["famscis", "monounsaturated fat", "grasas monoinsaturadas", "grasa monoinsaturada"]
    },
    {
        "name": "Cholesterol",
        "name_es": "Colesterol",
        "key": "cholesterol",
        "match": ["cholesterol", "colesterol"]
    },
    {
        "name": "Sugar",
        "name_es": "Azúcares",
        "key": "sugar",
        "match": ["sugar", "sugares", "azucar", "azucares"]
    },
    {
        "name": "Calcium",
        "name_es": "Calcio",
        "key": "calcium",
        "match": ["calcium", "ca", "calcio"]
    },
    {
        "name": "Selenium",
        "name_es": "Selenio",
        "key": "selenium",
        "match": ["selenium", "se", "selenio"]
    },
    {
        "name": "Pantothenic Acid",
        "name_es": "Ácido Pantoténico",
        "key": "pantothenic_acid",
        "match": ["pantothenic acid", "pantac", "acido pantotenico"]
    },
    {
        "name": "Vitamin B12",
        "name_es": "Vitamina B12",
        "key": "vitb12",
        "match": ["vitb12", "vitamina b12", "vitamin b12"]
    },
    {
        "name": "Vitamin B2",
        "name_es": "Vitamina B2",
        "key": "vitb2",
        "match": ["vitb2", "vitamina b2", "vitamin b2"],
        "description": "Vitamina B2"
    },
    {
        "name": "Vitamin B6",
        "name_es":"Vitamina B6",
        "key": "vitb6",
        "match": ["vitb6", "vitb6", "vitamina b6", "vitamin b6"],
        "description": "Vitamina B6"
    },
    {
        "name": "Vitamin K",
        "name_es":"Vitamina K",
        "key": "vitk",
        "match": ["vitk",  "vitamina k", "vitamin k"]
    },
    {
        "name": "Fibre",
        "name_es": "Fibra",
        "key": "fibre",
        "match": ["fibtg", "fibre", "fibra"]
    },
    {
        "name": "Magnesium",
        "name_es": "Magnesio",
        "key": "magnesium",
        "match": ["magnessium", "magnesio", "mg"]
    },
    {
        "name": "Net Content",
        "name_es": "Contenido Neto",
        "key": "net_content",
        "match": ["net content", "netcontent", "contenido neto"]
    },
    {
        "name": "Iodide",
        "name_es": "Yoduro",
        "key": "iodide",
        "match": ["id", "iodide", "yoduro"]
    },
    {
        "name": "Serving Quantity Information",
        "name_es": "Tamaño de porción",
        "key": "serving_quantity",
        "match": ["serving quantity", "serving quantity information", "tamano de porcion", "serv size", "serving size",
                  "serv quantity",  "serv qty"]
    },
    {
        "name": "Polyols",
        "name_es": "Polioles",
        "key": "polyols",
        "match": ["polyols", "polioles", "polyl"]
    },
    {
        "name": "Sodium Chloryde",
        "name_es": "Cloruro de Sodio",
        "key": "sodium_chloryde",
        "match": ["sodium chloryde", "cloruro de sodio", "nacl", "sales"]
    },
    {
        "name": "Saturated Fat",
        "name_es": "Grasas Saturadas",
        "key": "sat_fat",
        "match": ["fasat", "saturated_fat", "grasas_saturadas", "grasa_saturada"],
        "description": "Grasas Saturadas"
    },
    {
        "name": "Protein",
        "name_es": "Proteína",
        "key": "protein",
        "match": ["pro-", "protein", "proteina"],
        "description": "Proteína"
    },
    {
        "name": "Galactose",
        "name_es": "Galactosa",
        "key": "galactose",
        "match": ["galactose", "galactosa"],
        "description": "Galactosa"
    },
    {
        "name": "Bicarbonate",
        "name_es": "Bicarbonato",
        "key": "bicarbonate",
        "match": ["bicarbonate", "bicarbonato", "g_hc"],
        "description": "Bicarbonato"
    },
    {
        "name": "Iron",
        "name_es": "Hierro",
        "key": "iron",
        "match": ["hierro", "fe", "iron"],
        "description": "Hierro"
    },
    {
        "name": "Biotin",
        "name_es": "Biotina",
        "key": "biotin",
        "match": ["biotin", "biot", "biotina"],
        "description": "Biotina"
    },
    {
        "name": "Oleic Acid",
        "name_es": "Ácido Oleico",
        "key": "oleic_acid",
        "match": ["oleic_acid", "omega_9", "acido_oleico", "acid_oleico", "acido_oleic", "oleic_acido"],
        "description": "Ácido Oleico"
    },
    {
        "name": "Phosphorus",
        "name_es": "Fósforo",
        "key": "phosphorus",
        "match": ["phosphorus", "p", "fosforo"],
        "description": "Fósforo"
    },
    {
        "name": "Copper",
        "name_es": "Cobre",
        "key": "copper",
        "match": ["copper", "cu", "cobre"],
        "description": "Cobre"
    }
]


NUTRIMENTS_FIXED = {

}

class Attributes:
    def __init__(self, language='en'):
        self.langage=language
        self.raw_attributes={}
        self.attributes={}

    @staticmethod
    def create_attribute(key=None, name=None, value=None, unit=None, qty=None, order=None):
        return {
            "key": key,
            "name": name,
            "value": value,
            "unit": unit,
            "qty": qty,
            "order": order
        }

    def guess_attr(self, text):
        name = self.get_name(text)
        if name is not False:
            self.add_attribute(text, name=name, is_raw=True)
        else:
            self.add_attribute(text, name='raw', is_raw=True)

    def add_attribute(self, *args, **kargs):
        """
        This method helps you to add attributes easily

        Individual attributes:
            :param name: Type of attribute. Ex: 'brand', 'ingredient', 'category'
            :param value: The value of the attribute. Ex: 'Brand's Name', 'Ingredient's Name'
            :param unit: The units of the attribute. Ex: 'Kg', 'Kilograms', 'Lt'
            :param qty: The quantity of the attribute. Ex 1, 100, 150
            :param order: The order of the attribute
            :return: Update the attributes & raw_attributes

        Batch attributes:
            :param Dict of attributes {'name': 'value'}
        """
        if args:
            if len(args) == 1:
                if isinstance(args[0], dict):
                    if kargs.get('name', False) is not False:
                        for value, qty in args[0].items():
                            self.add_attribute(name=kargs.get('name'), value=value, qty=qty)
                    else:
                        for name, value in args[0].items():
                            self.add_attribute(name=name, value=value)
                elif isinstance(args[0], str):
                    if kargs.get('name', False) is not False:
                        self.add_attribute(value=args[0], qty=args[0], unit=args[0], name=kargs.get('name'), is_raw=kargs.get('is_raw', False))
                    else:
                       self.guess_attr(args[0])
                elif isinstance(args[0], list) or isinstance(args[0], tuple) or isinstance(args[0], set):
                    if kargs.get('name', False) is not False:
                        if isinstance(args[0], list) or isinstance(args[0], tuple):
                            for index, value in enumerate(args[0]):
                                if value:
                                    self.add_attribute(value=value,  name=kargs.get('name'), order=index+1)
                        else:
                            for value in args[0]:
                                if value:
                                    self.add_attribute(value=value, qty=value, unit=value, name=kargs.get('name'))
                    else:
                        for value in args[0]:
                            if value:
                                self.guess_attr(value)
                else:
                    print("{} type is not supported ({})".format(str(args[0]), type(args[0])))
                    return False
        elif kargs:
            name = kargs.get('name', 'raw')
            good_name = self.get_name(name)
            if good_name is not False:
                name = good_name
                is_raw = False
            else:
                is_raw = True
            attributes = [('value', str), ('unit', str), ('qty', float), ('order', str)]
            attr = ATTRIBUTES_FIXED.get(name, {})
            if len(attr) == 0:
                print('IS RAW!!!!!')
                is_raw = True

            attr_dict = {
                            'key': name,
                            'name': attr.get('name_es', name) if self.langage == 'es' else attr.get('name', name)
                        }
            fixed = {attr_fixed[0]: attr_fixed[1] for attr_fixed in attr.get('fixed', [])}
            must = {attr_must[0]: attr_must[1] for attr_must in attr.get('must', [])}

            for attribute, default_type in attributes:
                if attribute in fixed.keys() and kargs.get(attribute, False) is not False:
                    for fixed_values in attr.get(attribute):
                        match = fixed_values.get('match')
                        match_found = fixed_values.get('name_es') if self.langage == 'es' else fixed_values.get('name')
                        result = self.get_attr(kargs.get(attribute, False), match, expected_type=fixed.get(attribute))
                        if result is True:
                            result = match_found
                            break
                    else:
                        result = kargs.get(attribute)
                        is_raw = True
                elif attribute in must.keys() and kargs.get(attribute, False) is not False:
                    result = self.check_attr(kargs.get(attribute), expected_type=must.get(attribute))
                    if result is None:
                        result = kargs.get(attribute)
                        is_raw = True
                else:
                    result = self.check_attr(kargs.get(attribute), expected_type=default_type)
                    if result is None:
                        result = kargs.get(attribute)

                attr_dict[attribute] = result

            if kargs.get('is_raw', False) is True:
                is_raw = True




            self.update_attr(attr_dict, is_raw)
        else:
            print("You should pass at least 1 paramenter")

    def update_attr(self, parsed_attr, is_raw=True):
        if is_raw is True:
            name = parsed_attr.get('name', 'raw')
            attr = self.raw_attributes.get(name, False)
            if attr is False:
                self.raw_attributes[name] = parsed_attr
            elif isinstance(attr, dict):
                self.raw_attributes[name] = [attr, parsed_attr]
            elif isinstance(attr, list):
                self.raw_attributes[name].append(parsed_attr)
        else:
            name = parsed_attr.get('name', 'raw')
            attr = self.attributes.get(name, False)
            if attr is False:
                self.attributes[name] = parsed_attr
            elif isinstance(attr, dict):
                self.attributes[name] = [attr, parsed_attr]
            elif isinstance(attr, list):
                self.attributes[name].append(parsed_attr)

    @staticmethod
    def get_name(text, min_score=80, trusty_score=90):
        text = ''.join(x for x in unicodedata.normalize('NFKD', text) if x in string.ascii_letters or x in [" ", '"', "'", '.', ',']).lower()
        text.strip()
        text = re.sub(r'\s+', ' ', text)
        max_score = float('-inf')
        closer_attr = False
        for attr in ATTRIBUTES:
            choices = attr.get("match")
            result = process.extractOne(text, choices, scorer=fuzz.partial_token_set_ratio, score_cutoff=min_score)
            if result and result[1] > max_score:
                closer_attr = attr.get('key')
                max_score = result[1]
            if max_score > trusty_score:
                return closer_attr
        if max_score > min_score:
            return closer_attr
        else:
            return False

    @staticmethod
    def get_attr(value, choices, min_score=90, expected_type=str):
        if isinstance(value, str):
            if expected_type is str:
                text = ''.join(x for x in unicodedata.normalize('NFKD', value) if x in string.ascii_letters or x in [" ", '"', "'", '.', ',']).lower()
                text.strip()
                text = re.sub(r'\s+', ' ', text)
                result = process.extractOne(text, choices, scorer=fuzz.partial_token_set_ratio, score_cutoff=min_score)
                if result and result[1] > min_score:
                    return True
                else:
                    return False
            elif expected_type is int or expected_type is float:
                value = re.sub(r'[^.,\s\d]', '', value)
                value = re.sub(r'\s+', ' ', value)
                value = value.strip()
                try:
                    return expected_type(value)
                except:
                    return False

        elif type(value) is expected_type:
            return value
        else:
            return False

    @staticmethod
    def check_attr(value, expected_type=str):
        if isinstance(value, str):
            if expected_type is str:
                text = ''.join(x for x in unicodedata.normalize('NFKD', value) if
                               x in string.ascii_letters or x in [" ", '"', "'", '.', ',']).lower()
                text.strip()
                text = re.sub(r'\s+', ' ', text)
                text = text.strip()
                if text:
                    return text
                else:
                    return None
            elif expected_type is int or expected_type is float:
                value = re.sub(r'[^.,\s\d]', '', value)
                value = re.sub(r'\s+', ' ', value)
                value = value.strip()
                try:
                    return expected_type(value)
                except:
                    return None

        elif type(value) is expected_type:
            return value
        else:
            return None

    def get_attrs(self):
        return self.attributes, self.raw_attributes