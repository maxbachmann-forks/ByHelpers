import unicodedata
import string
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import re

ATTRIBUTES = [
    {
        "key": "presentation",
        "match": ["presentation", "presentacion"],

    },
    {

        "key": "measure_units",
        "match": ["units", "measure", "measurement", "medida", "unidades"],

    },
    {

        "key": "size",
        "match": ["size", "talla", "tamano", 'siz'],

    },
    {
        "key": "material",
        "match": ["material", "mtrl"],
    },
    {
        "key": "ingredient",
        "match": ["ingredient", "ingrediente", "ingredients", "ingredientes"]
    },
    {
        "key": "category",
        "match": ["category", "categories", "categoria", "categorias"]
    },
    {
        "key": "laboratory",
        "match": ["laboratorio", "laboratory", "lab"]
    },
    {
        "key": "model",
        "match": ["model", "modelo"]
    },
    {
        "key": "brand",
        "match": ["brand", "marca"]
    },
    {
        "key": "provider",
        "match": ["proveedor", "provider"]
    },
    {
        "key": "flavour",
        "match": ["flavour", "taste", "savor", "sabor"]
    },
    {
        "key": "color",
        "match": ["color"]
    },
    {
        "key": "genre",
        "match": ["genre", "gender", "kind", "genero", "sex", "sexo"]
    },
    {
        "key": "age",
        "match": ["age", "ages", "edad", "edades"]
    },
    {
        "key": "condition",
        "match": ["condition", "condicion", "status", "estado"]
    },
    {
        "key": "height",
        "match": ["height", "alto", "hgt"]
    },
    {
        "key": "width",
        "match": ["width", "ancho", "wdth"]
    },
    {
        "key": "length",
        "match": ["length", "long", "largo"]
    },
    {
        "key": "weight",
        "match": ["weight", "peso"]
    }
]

ATTRIBUTES_FIXED = {
    "presentation": {
        "values": [
            {
                "match" : ["dose","dosis","e27"],
                "name": 'dose',
                "name_es": "dosis"
            },
            {
                "name" : "tablet",
                "name_es" : "tabletas",
                "match" : ["tableta","tabletas","tab","tabs","grajeas","grageas","tabl"]
            },
            {
                "name" : "capsule",
                "name_es" : "cápsulas",
                "match" : ["capsula","capsulas","comprimidos","caps","cap"]
            },
            {
                "name" : "cream",
                "name_es" : "crema",
                "match" : ["crema","cream"]
            },
            {
                "name" : "unit",
                "name_es" : "unidades",
                "match" : ["unidades","unidad","units","pieza","piezas","pz","pzs","pzas", "u" , "h87", "1n", "counts"]
            },
            {
                "name" : "kit",
                "name_es" : "kit",
                "match" : ["set", "sets", "kt", "kit", "kits", "pack", "paquete", "combo"]
            },
            {
                "name" : "ointment",
                "name_es" : "ungüento",
                "match" : ["unguento", "ung", "ointment"]
            },
            {
                "name" : "suspension",
                "name_es" : "suspensión",
                "match" : ["susp","suspension"]
            },
            {
                "name" : "suppository",
                "name_es" : "supositorio",
                "match" : ["supositorio","suppository"]
            },
            {
                "name" : "env",
                "name_es" : "sobres",
                "match" : ["sobre","sobres","envelopes"]
            },
            {
                "name" : "gel",
                "name_es" : "gel",
                "match" : ["gel"]
            },
            {
                "name" : "solution",
                "name_es" : "solución",
                "match" :["sol","solucion","solution","solución"]
            },
            {
                "name" : "drops",
                "name_es" : "gotas",
                "match" :["gotas","gota","drops"]
            },
            {
                "name" : "tube",
                "name" : "name_es",
                "match" : ["tubo","tub","tube"]
            },
            {
                "name" : "ampoule",
                "name_es" : "ampolletas",
                "match" : ["ampolletas","ampoules","ampolleta"]
            }
        ],
        "fixed": ['value'],
        "must": ["value"],
        "type": "str",
        "name": "Presentation",
        "name_es": "Presentación"
    },
    "measure_units": {
        "values": [
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
                "match" : ["miligrams","miligramos","mg","miligramo","mgs", "mc"]
            },
            {
                "name" : "ug",
                "name_es" : "microgramo(s)",
                "match" : ["micrograms","ug","miligramo","mgs"]
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
                "name" : "bar",
                "name_es" : "bar(es)",
                "match" : ["bar","bares","bars"]
            },
            {
                "name" : "kg",
                "name_es" : "kilogramo(s)",
                "match" : ["kg","kgs","kilogramos","kilogramo","kilograms","kilogram","kilos", "kilo", "kgm"]
            },
            {
                "name" : "mm",
                "name_es" : "milimetro(s)",
                "match" : ["mm","mms","milimetros","milimetro","millimeters","millimeter", "mmt"]
            },
            {
                "name" : "cm",
                "name_es" : "centimetro(s)",
                "match" : ["cm","cms","centimetros","centimetro","centimeters","centimeter"]
            },
            {
                "name": "in",
                "name_es": "pulgada(s)",
                "match": ["inch", '"', "pulgada", "in", "pulgadas"]
            },
            {
                "name" : "m",
                "name_es" : "metro(s)",
                "match" : ["m","ms","mtr"]
            },
            {
                "name" : "km",
                "name_es" : "kilometro(s)",
                "match" : ["km","kms","kilometros","kilometro","kilometers","kilometer", "kmt"]
            },
            {
                "name" : "par",
                "name_es" : "par(es)",
                "match" : ["par", "pares", "pair", "pairs", "pr"]
            }
        ],
        "fixed_values": ['value'],
        "must": ["value"],
        "type": "str",
        "name": "Measure Units",
        "name_es": "Unidades de Medida"
    },
    "size": {
        "values": [
            {
                "name" : "sm",
                "name_es" : "chico",
                "match" : ["ch","chico","pequeno","pequeño","small","sm","chicos","petite", 's']
            },
            {
                "name" : "md",
                "name_es" : "mediano",
                "match" : ["md","mediano","medium","medianos", 'm']
            },
            {
                "name" : "lg",
                "name_es" : "grande",
                "match" : ["lg","large","grande","grandes", 'l']
            },
            {
                "name" : "xl",
                "name_es" : "extra grande",
                "match" : ["extragrande","extra grande","extra large","xl","xxl","xxxl","extralarge"]
            }
        ],
        "fixed": ['value'],
        "must": ["value"],
        "type": "str",
        "name": "Size",
        "name_es": "Tamaño"
    },
    "material": {
       "name": "Material",
       "name_es": "Material",
       "must": ["value"],
       "type": "str"
    },
    "ingredient": {
        "name": "Ingredient",
        "name_es": "Ingrediente",
        "must": ["value"],
        "type": "str"
    },
    "category":   {
        "name": "Category",
        "name_es": "Categoría",
        "must": ["value", "order"],
        "type": "str"
    },
    "laboratory": {
        "name": "Laboratory",
        "name_es": "Laboratorio",
        "must": ["value"],
        "type": "str"
    },
    "model": {
       "name": "Model",
       "name_es": "Modelo",
       "must": ["value"],
       "type": "str"
    },
    "brand": {
        "name": "Brand",
        "name_es": "Marca",
        "must": ["value"],
        "type": "str"
    },
    "provider": {
        "name": "Provider",
        "name_es": "Proveedor",
        "must": ["value"],
        "type": "str"
    },
    "flavour": {
        "name": "Flavour",
        "name_es": "Sabos",
        "must": ["value"],
        "type": "str"
    },
    "color": {
        "name": "Color",
        "name_es": "Color",
        "must": ["value"],
        "type": "str"
    },
    "genre": {
        "name": "Genre",
        "name_es": "Género",
        "must": ["value"],
        "type": "str"
    },
    "age": {
        "name": "Age",
        "name_es": "Edad",
        "must": ["value"],
        "type": "str"
    },
    "condition": {
        "name": "Condition",
        "name_es": "Condición",
        "must": ["value"],
        "type": "str"
    },
    "height": {
        "name": "Height",
        "name_es": "Alto",
        "must": ["value", "unit"],
        "type": "int"
    },
    "width": {
       "name": "Width",
       "name_es": "Ancho",
       "must": ["value", "unit"],
       "type": "int"
    },
    "length": {
        "name": "Length",
        "name_es": "Largo",
        "must": ["value", "unit"],
        "type": "int"
    },
    "weight": {
        "name": "Weight",
        "name_es": "Peso",
        "must": ["value", "unit"],
        "type": "int"
    }
}


def key_format(data):
    '''
    Normaliza textos a formatos sin acentos o con formato
    para keys a base de datos
    '''
    if not isinstance(data, str):
        return None
    return ''.join(x for x in unicodedata.normalize('NFKD', data) if x in string.ascii_letters or x == " ").lower().replace(" ","_").replace("_y_","_").replace("_e_","_")


def clean_list(list_, remove_duplicates=True):
    if list_:
        output = [elem.strip() for elem in list_ if elem.strip()]
        if remove_duplicates is True:
            return list(set(output))
        else:
            return output
    else:
        return []


class Attributes:
    def __init__(self):
        self.raw_attributes={}
        self.attributes={}

    @staticmethod
    def create_attribute(name=None, value=None, unit=None, qty=None, order=None):
        return {
            "name": name,
            "value": value,
            "unit": unit,
            "qty": qty,
            "order": order
        }

    def guess_attr(self, text):
        name = get_name(text)
        if name is not False:
            self.add_attribute(text, name=name)
        else:
            self.add_attribute(text, name='raw')

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
                        self.add_attribute(value=args[0], name=kargs.get('name'))
                    else:
                       self.guess_attr(args[0])
                elif isinstance(args[0], list) or isinstance(args[0], tuple) or isinstance(args[0], set):
                    if kargs.get('name', False) is not False:
                        if isinstance(args[0], list) or isinstance(args[0], tuple):
                            for index, value in enumerate(args[0]):
                                if value:
                                    self.add_attribute(value=value, name=kargs.get('name'), order=index+1 )
                        else:
                            for value in args[0]:
                                if value:
                                    self.add_attribute(value=value, name=kargs.get('name'))
                    else:
                        for value in args[0]:
                            if value:
                                self.guess_attr(value)
                else:
                    print("{} type is not supported ({})".format(str(args[0]), type(args[0])))
                    return False
        elif kargs:
            is_raw = False

            value = kargs.get('value', False)
            unit = kargs.get('unit', False)
            qty = kargs.get('qty', False)
            order = kargs.get('oder', False)
            name = kargs.get('name', False)


            if name is not False:
                good_name = get_name(name)
                if good_name is not False:
                    name = good_name
                    for attr_fixed  in ATTRIBUTES_FIXED.get(name).get('fixed', []):

                else:
                    is_raw = True
            else:
                is_raw = True



            parsed_attr = self.create_attribute(name, value, unit, qty, order)
            self.update_attr(parsed_attr, is_raw)
        else:
            print "You should pass at least 1 paramenter"

    def update_attr(self, parsed_attr, is_raw=True):
        if is_raw is True:
            name = parsed_attr.get('name')
            attr = self.raw_attributes.get(name, False)
            if attr is False:
                self.raw_attributes[name] = parsed_attr
            elif isinstance(attr, dict):
                self.raw_attributes[name] = [attr, parsed_attr]
            elif isinstance(attr, list):
                self.raw_attributes += [parsed_attr]
        else:
            name = parsed_attr.get('name')
            attr = self.attributes.get(name, False)
            if attr is False:
                self.attributes[name] = parsed_attr
            elif isinstance(attr, dict):
                self.attributes[name] = [attr, parsed_attr]
            elif isinstance(attr, list):
                self.attributes += [parsed_attr]

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
            if result and  result[1] > max_score:
                closer_attr = attr.get('key')
                max_score = result[1]
            if max_score > trusty_score:
                return closer_attr
        if max_score > min_score:
            return closer_attr
        else:
            return False





