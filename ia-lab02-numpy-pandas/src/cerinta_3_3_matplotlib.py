import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


iris = sns.load_dataset('iris')
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle('Tipuri de grafice Matplotlib — Dataset Iris', fontsize=16,
fontweight='bold')

# --- Subplot 1: Grafic linie — media lungimii sepalei per specie ---
medii = iris.groupby('species')['sepal_length'].mean()
axes[0, 0].plot(medii.index, medii.values, marker='o', linewidth=2,
markersize=8, color='steelblue')
axes[0, 0].set_title('Media lungimii sepalei per specie')
axes[0, 0].set_xlabel('Specie')
axes[0, 0].set_ylabel('Lungime sepală (cm)')
axes[0, 0].grid(True, alpha=0.3)

# --- Subplot 2: Scatter — lungime vs. lățime petală, colorat per specie ---
culori = {'setosa': '#e74c3c', 'versicolor': '#3498db', 'virginica': '#2ecc71'}
for specie, culoare in culori.items():
    subset = iris[iris['species'] == specie]
    axes[0, 1].scatter(subset['petal_length'], subset['petal_width'],
                    label=specie, color=culoare, alpha=0.7, s=50)
# Explicație: iterăm prin dicționarul de culori; pentru fiecare specie,
# filtrăm rândurile corespunzătoare și le reprezentăm cu o culoare proprie.
axes[0, 1].set_title('Lungime vs. lățime petală pe specii')
axes[0, 1].set_xlabel('Lungime petală (cm)')
axes[0, 1].set_ylabel('Lățime petală (cm)')
axes[0, 1].legend()
# --- Subplot 3: Grafic bare — număr flori per specie ---
numar_per_specie = iris['species'].value_counts()
axes[1, 0].bar(numar_per_specie.index, numar_per_specie.values,
color=['#e74c3c', '#3498db', '#2ecc71'], edgecolor='black',
alpha=0.8)
axes[1, 0].set_title('Număr de flori per specie')
axes[1, 0].set_xlabel('Specie')
axes[1, 0].set_ylabel('Număr de înregistrări')
# --- Subplot 4: Histogramă — distribuția lungimii sepalei ---
axes[1, 1].hist(iris['sepal_length'], bins=20, color='steelblue',
edgecolor='black', alpha=0.7)
axes[1, 1].set_title('Distribuția lungimii sepalei')
axes[1, 1].set_xlabel('Lungime sepală (cm)')
axes[1, 1].set_ylabel('Frecvență')
medie_sepala = iris['sepal_length'].mean()
axes[1, 1].axvline(medie_sepala, color='red', linestyle='--',
linewidth=2, label=f'Medie: {medie_sepala:.2f}')
axes[1, 1].legend()
plt.tight_layout()
plt.savefig('grafice_iris_matplotlib.png', dpi=150, bbox_inches='tight')
plt.show()
print("Graficul a fost salvat în fișierul 'grafice_iris_matplotlib.png'.")