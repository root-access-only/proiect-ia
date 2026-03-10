import pandas as pd
import seaborn as sns


tips = sns.load_dataset('tips')

print("=== Informatii generale ===")
print(f"Dimensiune: {tips.shape[0]} linii x {tips.shape[1]} coloane")
print(f"\nTipuri de date:\n{tips.dtypes}")
print(f"\nValori lipsa:\n{tips.isnull().sum()}")
print("\n=== Statistici descriptive ===")
print(tips.describe().round(2))

print("\n=== Bacsisul mediu per zi ===")
mediu_per_zi = tips.groupby('day', observed=True).mean(numeric_only=True)['tip'].round(2)
print(mediu_per_zi)

print("\n=== Bacsisul mediu per sex ===")
mediu_per_sex = tips.groupby('sex', observed=True).mean(numeric_only=True)['tip'].round(2)
print(mediu_per_sex)

tips_copie = tips.copy()
tips_copie['procent_bacsis'] = (tips_copie['tip'] / tips_copie['total_bill'] * 100).round(2)

print("\n=== Cele mai generoase 5 mese ===")
top5 = tips_copie.nlargest(5, 'procent_bacsis')
print(top5[['total_bill', 'tip', 'procent_bacsis', 'day', 'sex']])

print("\n=== Numar mese per zi si fumator ===")
mese_per_zi_fumator = tips.groupby(['day', 'smoker'], observed=True).size()
print(mese_per_zi_fumator)
