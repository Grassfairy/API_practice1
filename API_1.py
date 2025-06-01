from sanic import Sanic, Blueprint, Request, json as sanic_json, exceptions
from sanic_ext import validate

from sanic.response import json as sanic_json

from pydantic import BaseModel
from typing import List, Dict, Any

import json
import requests
import pandas as pd

app = Sanic("Backend")

global DATA
global COUNTRIES
global PERSONS
with open('./test.json', 'r') as file:
    DATA = json.load(file)
    COUNTRIES:list = DATA.get("countries", [])
    PERSONS:list = DATA.get("persons", [])

@app.route("/get_api", methods=["GET"])
async def getApi(req: Request):

    # token = "ea1d8333-c1fd-48e7-89e8-bda65ae6a413"
    # dataset = 'O-A0001-001'
    # url =  fr"""https://data.moenv.gov.tw/api/v2/aqx_p_07?api_key={token}"""
    # response = requests.get(url)

    # if response.status_code == 200:
    #     data = response.json()
    # else:
    #     print("Error:", response.status_code)
    
    # # json to dataframe
    # df = pd.DataFrame(data['records'])
    # print(df.head(3))
    # return df
    return sanic_json({"country": 'CSL', "person": 'person'})

class persontype(BaseModel):
    country: str

@app.route("/get_person", methods=["GET"])
@validate(query=persontype)
async def getPerson(requ: Request, query:persontype):
    for i in range(0,len(COUNTRIES)):
        if query.country == COUNTRIES[i]:
            return sanic_json({"persons": PERSONS[i]})
    return sanic_json({"persons":"not found"})


# ============================================

class AddItem(BaseModel):
    new_persons: List[str]
    new_countries: List[str]

@app.route("/add_item", methods=["POST"])
@validate(json=AddItem) #因為是用 json format 傳入資料 所以這邊要用 json
async def add_item(request: Request, body: AddItem):
    
    new_persons = body.new_persons 
    new_countries = body.new_countries

    duplicates = []
    for person in new_persons:
        if person in PERSONS:
            # PERSONS 裡面已經存在 重複的 value 了
            duplicates.append(person)
        else:
            # PERSONS 裡面沒有這個 value 所以 append 到 PERSONS
            PERSONS.append(person)
    
    # 概念如上
    for country in new_countries:
        if country in COUNTRIES:
            duplicates.append(country)
        else:
            COUNTRIES.append(country)

    write()

    return sanic_json({"duplicate": duplicates})

#寫回test.json
def write():
    DATA["countries"] = COUNTRIES
    DATA["persons"] = PERSONS

    with open('./test.json', 'w', encoding='utf-8') as file:
        json.dump(DATA, file, indent=4, ensure_ascii=False)

# ============================================
class DeleteItem(BaseModel):
    del_item: Dict[str, Any] = None

@app.route("/delete_item", methods=["DELETE"])
@validate(json=DeleteItem) #因為是用 json format 傳入資料 所以這邊要用 json
async def delete_item(request: Request, body: DeleteItem):
    person_to_delete = body.del_item.get("person")
    country_to_delete = body.del_item.get("countries")

    removed_person = False
    removed_country = False

    if person_to_delete and person_to_delete in PERSONS:
        PERSONS.remove(person_to_delete)
        removed_person = True
    elif person_to_delete: # Only if person_to_delete was provided but not found
        print(f"Person '{person_to_delete}' not found in PERSONS list.")
        

    if country_to_delete and country_to_delete in COUNTRIES:
        COUNTRIES.remove(country_to_delete)
        removed_country = True
    elif country_to_delete: # Only if country_to_delete was provided but not found
        print(f"Country '{country_to_delete}' not found in COUNTRIES list.")
        

    if removed_person or removed_country:
        write()
        return sanic_json({"msg": "success"})
    else:
        if not person_to_delete and not country_to_delete:
            return sanic_json({"msg": "failure", "detail": "No person or country provided for deletion."}, status=400)
        else:
            return sanic_json({"msg": "failure", "detail": "Neither specified person nor country was found to delete."}, status=404)


if __name__  == "__main__":
    app.run(host='0.0.0.0', port=2020, auto_reload=True, debug=True)