import seaborn as sns
import matplotlib.pyplot as plt


sns.set_theme(style='whitegrid', palette='Set2')
iris = sns.load_dataset('iris')
tips = sns.load_dataset('tips')

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Vizualizarea distribuțiilor cu Seaborn', fontsize=16,
fontweight='bold')
# --- Subplot 1: Histogramă cu KDE per specie (Iris) ---
sns.histplot(data=iris, x='petal_length', hue='species',
kde=True, bins=15, ax=axes[0, 0])
axes[0, 0].set_title('Distribuția lungimii petalei pe specii')
axes[0, 0].set_xlabel('Lungime petală (cm)')
# --- Subplot 2: Boxplot — lungimea sepalei per specie (Iris) ---
sns.boxplot(data=iris, x='species', y='sepal_length', ax=axes[0, 1])
axes[0, 1].set_title('Boxplot — lungimea sepalei pe specii')
axes[0, 1].set_xlabel('Specie')
axes[0, 1].set_ylabel('Lungime sepală (cm)')
# --- Subplot 3: Violinplot — lățimea petalei per specie (Iris) ---
sns.violinplot(data=iris, x='species', y='petal_width',
inner='quart', ax=axes[1, 0])
axes[1, 0].set_title('Violinplot — lățimea petalei pe specii')
axes[1, 0].set_xlabel('Specie')
axes[1, 0].set_ylabel('Lățime petală (cm)')


#Subplot 4: Boxplot bacșișuri per zi (Tips) ---
# Dataset-ul Tips ne permite să comparăm variabilitatea bacșișurilor
# în funcție de ziua săptămânii.
sns.boxplot(data=tips, x='day', y='tip',
order=['Thur', 'Fri', 'Sat', 'Sun'], ax=axes[1, 1])
axes[1, 1].set_title('Distribuția bacșișurilor per zi (Tips)')
axes[1, 1].set_xlabel('Zi')
axes[1, 1].set_ylabel('Bacșiș ($)')
plt.tight_layout()
plt.savefig('distributii_seaborn.png', dpi=150, bbox_inches='tight')
plt.show()
