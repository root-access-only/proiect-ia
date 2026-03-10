import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
sns.set_theme(style='white')
iris = sns.load_dataset('iris')
# Eliminăm coloana categorică 'species' — corelația Pearson se calculează
# doar pe variabile numerice
iris_numeric = iris.drop(columns='species')
# Calculăm matricea de corelație Pearson
corelatie = iris_numeric.corr(method='pearson')
print("=== Matricea de corelație Pearson ===")
print(corelatie.round(3))
# Mascăm triunghiul superior pentru a evita duplicarea informației
# (matricea de corelație este simetrică: corr(A, B) == corr(B, A))
mask = np.triu(np.ones(corelatie.shape, dtype=bool), k=1)
fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(corelatie,
mask=mask, # afișăm doar triunghiul inferior + diagonala
annot=True, # afișăm valorile în celule
fmt='.2f', # format cu 2 zecimale
cmap='RdYlGn', # roșu (negativ) → galben (zero) → verde (pozitiv)
vmin=-1, vmax=1, # fixăm scala la [-1, +1]
square=True, # celule pătrate
linewidths=0.8,
cbar_kws={'label': 'Coeficient Pearson'},
ax=ax)
ax.set_title('Matricea de corelație — Dataset Iris\n(coeficient Pearson)',
fontsize=13)
plt.tight_layout()
plt.savefig('heatmap_corelatie_iris.png', dpi=150, bbox_inches='tight')
plt.show()
# Identificăm automat corelațiile puternice
print("\n=== Interpretare automată ===")
prag_puternic = 0.8
for col1 in corelatie.columns:
    for col2 in corelatie.columns:
        if col1 < col2: # evităm dubluri și diagonala
            val = corelatie.loc[col1, col2]
            if abs(val) >= prag_puternic:
                tip = "pozitivă" if val > 0 else "negativă"
                print(f"Corelație puternică {tip} ({val:.2f}): {col1} ↔ {col2}")