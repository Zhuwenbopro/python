import pandas as pd

url = 'demo.html'
with open(url, encoding='utf-8') as f:
    df = pd.read_html(f.read())

bb = pd.ExcelWriter('out.xlsx')
df[0].to_excel(bb)
bb.close()
