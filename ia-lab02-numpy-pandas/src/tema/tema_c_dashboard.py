import matplotlib.pyplot as plt
import seaborn as sns


sns.set_theme(style='whitegrid', palette='muted')
tips = sns.load_dataset('tips')

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Dashboard — Dataset Tips', fontsize=16, fontweight='bold')

culori = {'Male': '#3498db', 'Female': '#e74c3c'}
for sex, culoare in culori.items():
    subset = tips[tips['sex'] == sex]
    axes[0, 0].scatter(subset['total_bill'], subset['tip'],
                       label=sex, color=culoare, alpha=0.7, s=40)
axes[0, 0].set_title('Total bill vs. Tip (per sex)')
axes[0, 0].set_xlabel('Total bill ($)')
axes[0, 0].set_ylabel('Tip ($)')
axes[0, 0].legend()

sns.boxplot(data=tips, x='day', y='total_bill',
            order=['Thur', 'Fri', 'Sat', 'Sun'], ax=axes[0, 1])
axes[0, 1].set_title('Distributia total bill per zi')
axes[0, 1].set_xlabel('Zi')
axes[0, 1].set_ylabel('Total bill ($)')

sns.histplot(data=tips, x='tip', hue='time', kde=True,
             bins=15, ax=axes[1, 0])
axes[1, 0].set_title('Distributia bacsisului (Lunch vs Dinner)')
axes[1, 0].set_xlabel('Tip ($)')

sns.barplot(data=tips, x='day', y='tip', hue='day',
            order=['Thur', 'Fri', 'Sat', 'Sun'],
            errorbar='ci', ax=axes[1, 1], legend=False)
axes[1, 1].set_title('Bacsisul mediu per zi')
axes[1, 1].set_xlabel('Zi')
axes[1, 1].set_ylabel('Tip mediu ($)')

plt.tight_layout()
plt.savefig('dashboard_tips.png', dpi=150, bbox_inches='tight')
plt.show()
print("Graficul a fost salvat in fisierul 'dashboard_tips.png'.")
