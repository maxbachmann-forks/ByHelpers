# ByHelpers
Repository created to be used by ByPrice's Scrapers as a library

#### Installation
```shell
$ pip install ByHelpers
```

## APPLOGGER
Create a logger instance to send the scrapers logs


#### Variables from enviroment
```bash
APP_NAME = os.getenv('APP_NAME', '__name__')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
LOG_HOST = os.getenv('LOG_HOST', 'logs5.papertrailapp.com')
LOG_PORT = os.getenv('LOG_PORT', 27971)
ENV = os.getenv('ENV', 'LOCAL')
```

#### HOW TO USE
```python
# Import
from ByHelpers import applogger

# Create logger
applogger.create_logger()

# Instance logger
logger = applogger.get_logger()

# Examples
logger.info("Use this log every time you start a step")
logger.debug("Use this log to track important information for debugging")
logger.warning("Use this log to alert bad behaviors in the scaper")
logger.error("Use this log to declare errors that affect the scraper flow")

```


## RABBIT_ENGINE
Allow you to import two different streamers to send messages to rabbitMQ


#### Variables from enviroment
```bash
APP_NAME = os.getenv('APP_NAME', '__name__')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
STREAMER_ROUTING_KEY = os.getenv('STREAMER_ROUTING_KEY', 'routing')
SMONITOR_KEY = os.getenv('SMONITOR','smonitor')
ENV = os.getenv('ENV', 'LOCAL')

# Required!!
RETAILER_KEY = os.getenv('RETAILER_KEY')
SCRAPER_TYPE = os.getenv('SCRAPER_TYPE')
```

#### HOW TO USE
```python
# Import
from ByHelpers.rabbit_engine import stream_monitor, stream_info
from ByRequests.ByRequests import ByRequest

# MASTER ITEM OR PRICE
# required params:
#  - params (dict)
#  - num_stores (integer)

ms_id = stream_monitor('master', params={"dict": "with params"}, num_stores=1)



# MASTER STORE
ms_id = stream_monitor('master')



# WORKER
# required params:
#  - store_id (str)
#  - ms_id (str)
#  - step (str)
### Possible steps
### "start", "category", "pagination", "price", "item", "store"
### "price_details", "item_details", "store_details", "cookies"

# optional params
#  - value (integer)
#  - br_stats (ByRequest().stats)



br = ByRequests()
ws_id = stream_monitor('worker', store_id='123', ms_id=ms_id, step='category', value=0, br.stats)

# ERROR
# required params:
#  - ws_id (str) # IF THE ERROR OCCURS IN THE WORKER
#  - ms_id (str) # IF THE ERROR OCCURS IN THE MASTER
#  - code (integer)
#  - reason (str)
### Possible codes
### 0 -> No response from ByRequest
### 1 -> Empty
### 2 -> Undefined

# Error in master
es_id = stream_monitor('error', ms_id=ms_id, code=1, reason='The list was empty')

# Error in worker
es_id = stream_monitor('error', ws_id=ws_id, code=0, reason='Cannot get soup')

# Error before master
es_id = stream_monitor('error', code=2, reason='Unknown')

```


## FUNCTIONS
Some functions that will help you with the scrapers

#### create_attribute(name='', clss_name='', value='', attr_key='', clss_key='')
This function helps you with the format of the attributes


```python
# INGREDIENT
create_attribute(
    name='SOME INGREDIENT,
    clss_name='Ingrediente',
    value=None,
    attr_key='ingrediente',
    clss_key='ingredient'
)

# CATEGORY
create_attribute(
name='SOME CATEGORY',
clss_name='Categoría',
value=1, # DEPTH (index + 1)
attr_key='categoria',
clss_key='category')

# UNIT
create_attribute(
name="SOME UNIT", # Ex. (L, MG, G)
clss_name='Unidad',
value=100, # QUANTITY
attr_key='unidad',
clss_key='unit')

# LABORATORY
create_attribute(
name="SOME LABORATORY",
clss_name='Laboratorio',
value=None,
attr_key='laboratorio',
clss_key='laboratory')


# PRESETNATION
create_attribute(
name="SOME PRESENTATION",
clss_name='Presentación',
value="SOME VALUE", # EX. pastillas/piezas
attr_key='presentacion',
clss_key='presentation')


# CONTAINER TYPE
create_attribute(
name = "SOME CONTAINER", (bolsa, caja, atomizador)
clss_name='Contenedor',
value=None,
attr_key='contenedor',
clss_key='container')

```

### key_format(data)
This function convert an string into a key (without accents and special chars)

``` python
key_format("This is an Increíble example in Español!!! :D")
```

### clean_list(list_, remove_duplicates=True)
This function remove the empty string from a list and can drop duplicates

``` python
clean_list(["This", "", "\n", "is", "an", "example", "example", "!"])
```