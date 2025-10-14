import pandas as pd
from rich import print
import json


df = pd.read_csv('parts_prod_unique.csv')
df = df.to_dict(orient='records')

all_parts = pd.read_csv('all_parts.csv')
all_parts = all_parts.to_dict(orient='records')


for parts in all_parts:
    json_data = json.loads(parts['json_data'])
    parts['json_data'] = json_data
    print(parts)
    input('Next part: ')



