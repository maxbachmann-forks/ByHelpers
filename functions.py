import unicodedata
import string


def create_attribute(name='', clss_name='', value='', attr_key='', clss_key=''):
    return {
        "attr_name": name,
        "clss_name": clss_name,
        "value": value,
        "attr_key": attr_key,
        "clss_key": clss_key
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