import seaborn as sns
import matplotlib.pyplot as plt


sns.set_theme(style='whitegrid', palette='Set2')
iris = sns.load_dataset('iris')

g = sns.pairplot(iris, hue='species', diag_kind='kde')
g.figure.suptitle('Pairplot — Dataset Iris', fontsize=16, y=1.02)
g.figure.savefig('pairplot_iris.png', dpi=150, bbox_inches='tight')
plt.show()
print("Pairplot salvat in 'pairplot_iris.png'.")

variabile = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']
etichete = ['Lungime sepala (cm)', 'Latime sepala (cm)',
            'Lungime petala (cm)', 'Latime petala (cm)']

fig, axes = plt.subplots(1, 4, figsize=(18, 5))
fig.suptitle('Violinplot per variabila — Dataset Iris', fontsize=16,
             fontweight='bold')

for i, (var, eticheta) in enumerate(zip(variabile, etichete)):
    sns.violinplot(data=iris, x='species', y=var, hue='species',
                   ax=axes[i])
    axes[i].set_title(eticheta)
    axes[i].set_xlabel('Specie')
    axes[i].set_ylabel(eticheta)

plt.tight_layout()
plt.savefig('violinplot_iris.png', dpi=150, bbox_inches='tight')
plt.show()
print("Violinplot salvat in 'violinplot_iris.png'.")
