import pandas as pd
import numpy as np
dataFile = 'data/mammals_WORKING.csv'
df = pd.read_csv(dataFile)
df['DEFF'] = np.zeros(len(df), dtype=np.int16)
nullCounter = 0
for counter in range(0, len(df)):
    if not np.count_nonzero(df.iloc[counter, 3:-7].to_numpy()):
        df.loc[counter, 'DEFF'] = 1
        nullCounter+=1
print(nullCounter)
df.to_csv('mammals_WITHDEFF.csv', index=False)