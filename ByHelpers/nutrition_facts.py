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
        "name": "Grasas Trans",
        "name_es": "Trans Fat",
        "key": "trans_fat",
        "match": ["grasas trans", "trans fat", "acidos grasos trans", "trans fatty acids"],
        "description": "Cobre"
    },
    {
        "name": "Total Fat",
        "name_es": "Grasas Totales",
        "key": "fat",
        "match": ["fat", "grasa", "grasas", "acidos grasos", "grasa total", "total fat", ""],
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
        "match": ["carbohydrate", "carbohidrato", "choavl", "total carbohydrate", "carbohidratos totales"]
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
        "name": "Cholesterol",
        "name_es": "Colesterol",
        "key": "cholesterol",
        "match": ["cholesterol", "colesterol"]
    },
    {
        "name": "Sugar",
        "name_es": "Azúcares",
        "key": "sugar",
        "match": ["sugar", "sugares", "azucar", "azucares", "azucares totales", "total sugars", "sugars"]
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
        "match": ["fibtg", "fibre", "fibra", "dietary fiber", "fibra dietetica", "fda", "roughage"]
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
        "match": ["fasat", "saturated fat", "grasas saturadas", "grasa saturada"],
        "description": "Grasas Saturadas"
    },
    {
        "name": "Protein",
        "name_es": "Proteína",
        "key": "protein",
        "match": ["pro", "protein", "proteina"],
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
        "match": ["bicarbonate", "bicarbonato", "g hc"],
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
        "match": ["oleic acid", "omega 9", "acido oleico", "acid oleico", "acido oleic", "oleic acido"],
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


WEIGHT_UNITS = [
    {
        "name" : "ml",
        "name_es" : "mililitro(s)",
        "match" : ["ml","mililitros","mltrs","mls","militers", "mlt"]
    },
    {
        "name" : "l",
        "name_es" : "litro(s)",
        "match" : ["l","litros","ltrs","liters", "ltr"]
    },
    {
        "name" : "mg",
        "name_es" : "miligramo(s)",
        "match" : ["miligrams","miligramos","mg","miligramo","mgs"]
    },
    {
        "name" : "ug",
        "name_es" : "microgramo(s)",
        "match" : ["micrograms","ug","miligramo", "mcg"]
    },
    {
        "name" : "g",
        "name_es" : "gramo(s)",
        "match" : ["grams","gramos","g","gramo","gr", "grm"]
    },
    {
        "name" : "onz",
        "name_es" : "onza(s)",
        "match" : ["ounce","ounces","onza","onzas","onz"]
    },
    {
        "name" : "pnt",
        "name_es" : "pinta(s)",
        "match" : ["pint","pinta","ptd", "pti"]
    },
    {
        "name" : "kg",
        "name_es" : "kilogramo(s)",
        "match" : ["kg","kgs","kilogramos","kilogramo","kilograms","kilogram","kilos", "kilo", "kgm"]
    }
]


class Nutriments:
    def __init__(self, language='en'):
        self.langage=language
        self.raw_nutriments={}
        self.nutriments={}
        self.good_name = None


    @staticmethod
    def create_nutriment(key=None, name=None, daily=None, unit=None, qty=None):
        return {
            "key": key,
            "name": name,
            "unit": unit,
            "qty": qty,
            "daily": daily
        }


    def guess_nutr(self, text):
        name = self.get_name(text)
        print(name)
        if name is not False:
            self.add_nutriment(text, name=name, is_raw=True)
        else:
            self.add_nutriment(text, name='raw', is_raw=True)


    def add_nutriment(self, *args, **kargs):
        """
        This method helps you to add nutriments easily

        Individual nutriments:
            :param name: Type of nutriment. Ex: 'brand', 'ingredient', 'category'
            :param daily: The daily of the nutriment. Ex: 'Brand's Name', 'Ingredient's Name'
            :param unit: The units of the nutriment. Ex: 'Kg', 'Kilograms', 'Lt'
            :param qty: The quantity of the nutriment. Ex 1, 100, 150
            :param order: The order of the nutriment
            :return: Update the nutriments & raw_nutriments

        Batch nutriments:
            :param Dict of nutriments {'name': 'daily'}
        """
        if args:
            if len(args) == 1:
                if isinstance(args[0], dict):
                    if kargs.get('name', False) is not False:
                        for daily, qty in args[0].items():
                            self.add_nutriment(name=kargs.get('name'), qty=qty, daily=daily)
                    else:
                        for name, value in args[0].items():
                            self.add_nutriment(name=name, guess_values=value)
                elif isinstance(args[0], str):
                    if kargs.get('name', False) is not False:
                        self.add_nutriment(name=kargs.get('name'), guess_values=args[0])
                    else:
                       self.guess_nutr(args[0])
                elif isinstance(args[0], list) or isinstance(args[0], tuple) or isinstance(args[0], set):
                    if kargs.get('name', False) is not False:
                        if isinstance(args[0], list) or isinstance(args[0], tuple):
                            for value in args[0]:
                                if value:
                                    self.add_nutriment(name=kargs.get('name'), guess_values=value)
                    else:
                        for value in args[0]:
                            if value:
                                self.guess_nutr(value)
                else:
                    print("{} type is not supported ({})".format(str(args[0]), type(args[0])))
                    return False
        elif kargs:
            name = kargs.get('name', 'raw')
            nutr = self.get_name(name, return_dict=True)
            if nutr is not False:
                nutr_dict = {
                    'key': nutr.get('key'),
                    'name': nutr.get('name_es') if self.langage == 'es' else nutr.get('name')
                }
                is_raw = False
                nutr_dict.update(self.gess_values(nutr, daily=False, unit=False, qty=False, values=False))
            else:
                nutr_dict = {
                    'key': 'raw',
                    'name': name
                }
                is_raw = True
                nutr_dict.update(self.gess_values(None, daily=False, unit=False, qty=False, values=False))




            if kargs.get('is_raw', False) is True:
                is_raw = True




            self.update_nutr(nutr_dict, is_raw)
        else:
            print("You should pass at least 1 paramenter")


    def update_nutr(self, parsed_nutr, is_raw=True):
        if is_raw is True:
            name = parsed_nutr.get('name', 'raw')
            nutr = self.raw_nutriments.get(name, False)
            if nutr is False:
                self.raw_nutriments[name] = parsed_nutr
            elif isinstance(nutr, dict):
                self.raw_nutriments[name] = [nutr, parsed_nutr]
            elif isinstance(nutr, list):
                self.raw_nutriments[name].append(parsed_nutr)
        else:
            name = parsed_nutr.get('name', 'raw')
            nutr = self.nutriments.get(name, False)
            if nutr is False:
                self.nutriments[name] = parsed_nutr
            elif isinstance(nutr, dict):
                self.nutriments[name] = [nutr, parsed_nutr]
            elif isinstance(nutr, list):
                self.nutriments[name].append(parsed_nutr)


    @staticmethod
    def get_name(text, min_score=90, trusty_score=95, return_dict=False):
        text = ''.join(x for x in unicodedata.normalize('NFKD', text) if x in string.ascii_letters or x in [" "]).lower()
        text.strip()
        text = re.sub(r'\s+', ' ', text)
        max_score = float('-inf')
        closer_nutr = False
        for nutr in NUTRIMENTS:
            choices = nutr.get("match")
            result = process.extractOne(text, choices, scorer=fuzz.WRatio, score_cutoff=min_score)
            if result:
                print(text, result)
            if result and result[1] > max_score:
                print (result[1] > max_score, result[1], max_score)
                closer_nutr = nutr.get('key')
                closer_dict = nutr
                closer_dict['closer_match'] = result[0]
                max_score = result[1]
                print ("Max: ", max_score)
                if max_score >= trusty_score:
                    if return_dict is True:
                        return nutr
                    return closer_nutr
        if max_score >= min_score:
            if return_dict is True:
                return closer_dict
            return closer_nutr
        else:
            return False


    def gess_values(self, nutr, daily=False, unit=False, qty=False, values=False):
        guess_dict ={
            "qty": None,
            "daily": None,
            "unit": None
        }
        if qty is not False:
            if isinstance(qty, str):
                if unit is False:
                    unit = self.get_unit(qty)
                    if unit is not False:
                        guess_dict['unit'] = unit

                qty = self.str_to_float(qty)
                guess_dict['qty'] = qty if qty is not False else None

            elif isinstance(qty, float) or isinstance(qty, float):
                guess_dict['qty'] = float(qty)

        if daily is not False:
            if isinstance(daily, str):
                daily = self.str_to_float(daily)
                guess_dict['daily'] = daily if daily is not False else None

            elif isinstance(daily, float) or isinstance(daily, float):
                guess_dict['daily'] = float(daily)

        if unit is not False and isinstance(unit, str):
            unit, closer_unit = self.get_unit(unit, is_trusty=True)
            if unit is not False:
                guess_dict['unit'] = unit

        if values and isinstance(values, str):
            values = ''.join(
            x for x in unicodedata.normalize('NFKD', string) if x in string.ascii_letters or x in [" ", "%"]).lower()
            if nutr is not None:
                values = values.replace(nutr.get('closer_match'), '')
            if unit is not None:
                values = values.replace(unit, '')
            else:
                unit, closer_unit = self.get_unit(values)
                if unit is not False:
                    guess_dict['unit'] = unit
            if qty is None:
                qty_search = re.search(r'([\d\.]+) *{unit}'.format(unit=closer_unit), values)
                if qty_search:
                    try:
                        qty = float(qty_search)
                    except:
                        qty = None

                qty_search = re.findall(r'([\d\.]+)', values)
                if len(qty_search) == 1:
                    if '%' not in values:
                        try:
                            qty = float(qty_search[0])
                        except:
                            qty = None
                    else:
                        try:
                            daily = float(qty_search[0])
                        except:
                            daily = None
                elif len(qty_search) == 2:
                    if '%' in values:
                        daily_search = re.search(r'([\d\.]+) *%', values)
                        if daily_search:
                            try:
                                daily_str = daily_search.group(1)
                                qty = set(qty_search) - {daily_search}

                                if len(qty) == 1:
                                    try:
                                        qty = float(qty)
                                    except:
                                        qty = None
                                daily = float(daily_str)
                            except:
                                daily = None
            if daily is None and '%' in values:
                daily_search = re.findall(r'([\d\.]+)', values)
                if len(daily_search) == 1:
                    try:
                        daily = float(qty_search[0])
                    except:
                        daily = None
                else:
                    daily_search = re.search(r'([\d\.]+) *%', values)
                    if daily_search:
                        try:
                            daily = float(daily_search.group(1))
                        except:
                            daily = None

        if guess_dict["qty"] is None:
            guess_dict["qty"] = qty
        if guess_dict["daily"] is None:
            guess_dict["daily"] = daily
        if guess_dict["unit"] is None:
            guess_dict["unit"] = unit

        return guess_dict


    @staticmethod
    def get_unit(string, is_trusty=False, min_score=95, trusty_score=100):
        if not isinstance(string, str):
            return False
        text = ''.join(
            x for x in unicodedata.normalize('NFKD', string) if x in string.ascii_letters or x in [" "]).lower()
        text.strip()
        text = re.sub(r'[\d%]')
        text = re.sub(r'\s+', ' ', text)
        if is_trusty:
            trustier_text = re.search('[\d\.]+ *([\(\)a-z]+)')
            trustier_text = trustier_text.group(1) if trustier_text else False
        else:
            trustier_text = False

        max_score = float('-inf')
        closer_unit = False
        closer_match = False
        for unit in WEIGHT_UNITS:
            choices = unit.get("match")
            if trustier_text is not False:
                result = process.extractOne(text, choices, scorer=fuzz.partial_token_set_ratio, score_cutoff=min_score)
                if result:
                    return unit.get('key')
            result = process.extractOne(text, choices, scorer=fuzz.partial_token_set_ratio, score_cutoff=min_score)
            if result and result[1] > max_score:
                closer_unit = unit.get('key')
                closer_match = result[0]
                max_score = result[1]
            if is_trusty is True or max_score >= trusty_score:
                return closer_unit, closer_match
        if max_score > min_score:
            return closer_unit, closer_match
        else:
            return False, False


    @staticmethod
    def str_to_float(string):
        if not isinstance(string, str):
            return False
        text = re.sub(r'\s+', ' ', string)

        text = re.sub(r'[^\d\.]', '', text)
        text.strip()
        try:
            return float(text)
        except:
            return False


    def get_nutrs(self):
        return self.nutriments, self.raw_nutriments

