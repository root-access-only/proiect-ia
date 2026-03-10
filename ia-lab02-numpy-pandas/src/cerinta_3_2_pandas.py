import pandas as pd
import seaborn as sns
# Încărcare dataset
iris = sns.load_dataset('iris')
# --- Explorare generală ---
print("=== Primele 5 înregistrări ===")
print(iris.head())
print("\n=== Informații generale ===")
print(f"Dimensiune: {iris.shape[0]} linii × {iris.shape[1]} coloane")
print(f"Coloane: {iris.columns.tolist()}")
print(f"\nTipuri de date:\n{iris.dtypes}")
print(f"\nValori lipsă:\n{iris.isnull().sum()}")
print("\n=== Statistici descriptive ===")
print(iris.describe().round(2))
# --- Distribuția speciilor ---
print("\n=== Distribuția speciilor ===")
print(iris['species'].value_counts())
# --- Filtrare ---
print("\n=== Flori Setosa cu lungimea sepalei > 5 cm ===")
setosa_mare = iris.loc[(iris['species'] == 'setosa') & (iris['sepal_length'] >
5.0)]
print(f"Număr înregistrări: {len(setosa_mare)}")
print(setosa_mare.head())
# --- Agregare: medie per specie ---
print("\n=== Medie per specie ===")
medie_per_specie = iris.groupby('species').mean(numeric_only=True).round(2)
print(medie_per_specie)
# --- Adăugare coloană calculată ---
# Lucrăm pe o copie pentru a nu modifica dataset-ul original
iris_extins = iris.copy()
iris_extins['raport_petala'] = (iris_extins['petal_length'] /
iris_extins['petal_width']).round(2)
print("\n=== Raport lungime/lățime petală (primele 5) ===")
print(iris_extins[['species', 'petal_length', 'petal_width',
'raport_petala']].head())