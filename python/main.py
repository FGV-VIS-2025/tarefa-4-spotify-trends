import pandas as pd

df = pd.read_csv('python/charts.csv', low_memory=False)

# Para criar o charts_global:
df = df[df["region"]=="Global"]
df = df[df['chart'] != 'viral50']
df = df.drop(columns=['chart'])
df = df.drop(columns=['trend'])
df['url'] = df['url'].str.replace('https://open.spotify.com/track/', '', regex=False)

df.to_csv('charts_global.csv', index=False)

# Para criar o charts_top:
# Tira os virais e deleta a coluna chart e trend
#df = df[df['chart'] != 'viral50']
#df = df.drop(columns=['chart'])
#df = df.drop(columns=['trend'])

# Ajusta a coluna url
#df['url'] = df['url'].str.replace('https://open.spotify.com/track/', '', regex=False)

#df.to_csv('python/charts_top.csv', index=False)