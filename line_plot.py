import pandas
import matplotlib.pyplot as plt
df = pandas.read_csv('jul/01_erp.csv')
df = dd.loc[df['veh_category_name'] == 2]
df = df.loc[df['Rhum'] == 2]
df = df.loc[df['pol_id'] == 2]
df = df.loc[df['process_id'] == 2]
df = df.loc[df['cat_id'] == 2]
df = df.loc[df['speed_time'] == 2]
df.plot(x=None, y='ER', kind='line')
plt.show()
