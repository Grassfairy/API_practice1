#在本地主機載入和儲存 dataframe
import pandas as pd

df = pd.read_json ('test.json')
print(df.to_markdown())

with open('test.json', encoding='utf-8') as inputfile:
    df = pd.read_json(inputfile)

#轉換成csv格式,index是有沒有流水號
df.to_csv('csvtest.csv', encoding='utf-8', index=False)
print(pd.read_csv('csvtest.csv'))
df.to_csv('csvtest2.csv', encoding='utf-8', index=True)
print(pd.read_csv('csvtest2.csv'))