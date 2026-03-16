# Laborator \#03

## Căutare informată - algoritmul alpinistului

> 

---

## Cuprins

1. [Obiectivele lucrării de laborator](#1-obiectivele-lucrării-de-laborator)
2. [Algoritmul Alpinistului (Hill Climbing)](#2-algoritmul-alpinistului-hill-climbing)
   - 2.1 [Clasificare corectă: căutare locală, nu neinformată](#21-clasificare-corectă-căutare-locală-nu-neinformată)
   - 2.2 [Cum funcționează algoritmul](#22-cum-funcționează-algoritmul)
   - 2.3 [Variante ale algoritmului](#23-variante-ale-algoritmului)
   - 2.4 [Avantaje și limitări](#24-avantaje-și-limitări)
3. [Problema Comis-Voiajorului (TSP)](#3-problema-comis-voiajorului-tsp)
   - 3.1 [Descrierea problemei](#31-descrierea-problemei)
   - 3.2 [Matricea de distanțe — graful complet](#32-matricea-de-distanțe--graful-complet)
   - 3.3 [Formatul fișierului de intrare](#33-formatul-fișierului-de-intrare)
4. [Implementare de referință: Backtracking Recursiv (monolitic)](#4-implementare-de-referință-backtracking-recursiv-monolitic)
   - 4.1 [Descrierea algoritmului](#41-descrierea-algoritmului)
   - 4.2 [Cod Python](#42-cod-python)
5. [Rezolvarea TSP cu biblioteca simpleai](#5-rezolvarea-tsp-cu-biblioteca-simpleai)
   - 5.1 [Alegerea bibliotecii](#51-alegerea-bibliotecii)
   - 5.2 [Instalare și funcții disponibile](#52-instalare-și-funcții-disponibile)
   - 5.3 [Exemplu de utilizare](#53-exemplu-de-utilizare)
6. [Cerințele temei](#6-cerințele-temei)
7. [Bibliografie](#7-bibliografie)

---

## 1. Obiectivele lucrării de laborator

- Înțelegerea și implementarea algoritmului de **backtracking recursiv** pentru rezolvarea optimă a problemei comis-voiajorului (TSP).
- Cunoașterea principiilor **căutării locale** și a algoritmului alpinistului (*hill climbing*).
- Utilizarea bibliotecii Python `simpleai` pentru implementarea algoritmului alpinistului.
- Compararea experimentală a performanței celor două abordări prin grafice generate cu `matplotlib/seaborn`.

---

## 2. Algoritmul alpinistului (*hill climbing*)

### 2.1 Căutare locală informată

> Algoritmul alpinistului (*hill climbing* *algorithm*) nu este o strategie de căutare neinformată (BFS, DFS, cost uniform) ci un algoritm de **căutare locală informată**: el folosește o **funcție de evaluare euristică** specifică problemei pentru a ghida selecția stărilor următoare. Strategiile cu adevărat neinformate (neghidate) nu folosesc nicio informație despre calitatea stărilor - ele explorează spațiul de căutare fără a putea distinge o stare "mai bună" de una "mai slabă".
> 
> Clasificarea corectă, conform lucrării de referință *Artificial Intelligence: A Modern Approach* (Russell & Norvig, cap. 4 — *Search in Complex Environments*), plasează algoritmul alpinistului în categoria **algoritmilor de căutare locală**, o categorie distinctă atât de căutarea neinformată, cât și de cea informată clasică (A\*, greedy best-first).

Tabelul următor ilustrează diferențele esențiale:

| Criteriu                          | Strategii neinformate (ex. BFS, DFS) | Hill Climbing           |
| --------------------------------- | ------------------------------------ | ----------------------- |
| Folosește funcție euristică       | Nu                                   | **Da**                  |
| Explorează tot spațiul de căutare | Potențial da                         | Nu (doar local)         |
| Memorează stările anterioare      | Da (pentru revenire)                 | **Nu** (irevocabil)     |
| Garanție pentru optimul global    | BFS / cost uniform: da               | **Nu**                  |
| Complexitate spațială             | O(b^d) — exponențială                | **O(1)** — constantă    |
| Tip de strategie                  | Tentativă sau irevocabilă            | **Irevocabilă, locală** |

---

### 2.2 Cum funcționează algoritmul

Denumirea vine de la metafora unui **alpinist** care dorește să ajungă cât mai repede pe vârful unui munte: la fiecare pas, el privește împrejur și urcă în direcția cu panta cea mai abruptă, fără a ține minte drumul parcurs și fără a putea "vedea" dincolo de înălțimile din jur.

Formal, algoritmul operează cu:

- **Starea curentă** — configurația problemei la momentul dat.
- **Funcția de evaluare** `h(s)` — o valoare numerică asociată fiecărei stări, ce măsoară "cât de bună" este acea stare. Algoritmul **maximizează** această funcție (sau, echivalent, minimizează o funcție de cost `f(s) = -h(s)`).
- **Mulțimea de vecini** — setul stărilor accesibile dintr-o stare curentă printr-o singură "mișcare" (o transformare locală).

**Pseudocod (varianta Steepest Ascent):**

```
funcție HILL-CLIMBING(problema):
    stare_curentă ← stare_inițială(problema)    // de obicei aleasă aleatoriu

    repetă la nesfârșit:
        vecini ← GENEREAZĂ_VECINI(stare_curentă)
        cel_mai_bun_vecin ← argmax_{v ∈ vecini} h(v)

        dacă h(cel_mai_bun_vecin) ≤ h(stare_curentă):
            returnează stare_curentă    // optim local atins — algoritmul se oprește

        stare_curentă ← cel_mai_bun_vecin
```

**Observații cheie:**

1. Selecția este **irevocabilă**: odată ce se trece la o stare nouă, starea anterioară și toate alternativele sale sunt uitate definitiv.
2. Algoritmul se oprește când **niciun vecin nu îmbunătățește** starea curentă — aceasta este condiția de **optim local**. Nu există garanție că optimul local coincide cu cel global.
3. Funcția de evaluare `h(s)` este specifică problemei și constituie **cunoașterea euristică** (informată) pe care algoritmul o exploatează.

---

### 2.3 Variante ale algoritmului

#### 2.3.1 Algoritmul alpinistului cu cea mai abruptă pantă (*steepest ascent hill climbing*)

La fiecare pas se evaluează **toți** vecinii stării curente și se alege cel cu valoarea maximă a funcției de evaluare. Corespunde pseudocodului de mai sus. Această variantă este **deterministă** dacă starea inițială este fixă.

#### 2.3.2 Algoritmul alpinistului stocastic (*stochastic hill climbing*)

Nu alege neapărat **cel mai bun** vecin, ci selectează **aleatoriu** dintre vecinii mai buni decât starea curentă. Probabilitatea de selecție poate fi proporțională cu gradul de îmbunătățire adus. Avantaj față de steepest ascent: mai puțin predispus să se blocheze pe aceeași creastă; explorare mai diversă a vecinătății.

#### 2.3.3 Algoritmul alpinistului cu reporniri aleatorii (*random restart hill climbing*)

Rulează algoritmul de mai multe ori pornind din **stări inițiale alese aleatoriu** și păstrează cea mai bună soluție găsită. Dacă procentul din spațiul de stări care aparține "bazinului de atracție" al optimului global este `p`, atunci probabilitatea de a-l găsi după `k` reporniri independente este `1 − (1 − p)^k`. Cu suficiente reporniri, această variantă are **completitudine probabilistică** — îmbunătățire semnificativă față de varianta de bază.

#### Comparație tabelară

| Variantă        | Evaluare vecini               | Reporniri | Completitudine | Funcție în `simpleai`           |
| --------------- | ----------------------------- | --------- | -------------- | ------------------------------- |
| Steepest Ascent | Toți; alege maximul           | Nu        | Nu             | `hill_climbing`                 |
| Stocastic       | Aleatoriu dintre cei mai buni | Nu        | Nu             | —                               |
| Random Restart  | Steepest Ascent repetat       | Da        | Probabilistică | `hill_climbing_random_restarts` |

---

### 2.4 Avantaje și limitări

**Avantaje:**

- **Eficiență spațială O(1)** — memorează doar starea curentă, indiferent de dimensiunea problemei.
- **Convergență rapidă** pentru probleme cu structură "bine comportată" (puține optimi locale).
- **Scalabilitate** — aplicabil problemelor de dimensiuni mari unde explorarea exhaustivă (backtracking, BFS) este prohibitivă.
- **Simplitate de implementare** — necesită doar definirea funcției de evaluare și a vecinătății.

**Limitări:**

- **Optimi locali** — algoritmul se poate bloca într-o soluție suboptimă din care nu poate ieși.
- **Platouri** (*plateaux*) — zone ale spațiului de stări unde funcția de evaluare este constantă; nu există o direcție clară de îmbunătățire.
- **Creste** (*ridges*) — șiruri de optimi locali care formează un traseu spre optimul global, dar din care nici o mișcare individuală nu urca direct.
- **Fără garanție de optimalitate globală** — calitatea soluției depinde puternic de starea inițială și de structura vecinătății definite.

---

## 3. Problema comis-voiajorului (TSP)

### 3.1 Descrierea problemei

**Problema comis-voiajorului** (*Travelling Salesman Problem*, TSP) este una dintre cele mai studiate probleme de optimizare combinatorică din informatică și cercetarea operațională.

**Enunț:** Un comis-voiajor trebuie să viziteze un set de `N` orașe, fiecare **exact o singură dată**, și să se întoarcă la orașul de plecare. Costul deplasării între oricare două orașe este cunoscut. Se cere determinarea ordinii de vizitare a orașelor astfel încât **costul total al drumului să fie minim**.

**Importanță practică:** TSP apare în numeroase aplicații reale — optimizarea rutelor de livrare, planificarea traiectoriilor robotice, secvențierea genomică, proiectarea circuitelor integrate etc.

**Complexitate:** Numărul de tururi distincte pentru `N` orașe (fixând orașul de start pentru TSP simetric) este `(N − 1)! / 2`. Această creștere **factorială** face TSP o problemă **NP-hard** — niciun algoritm eficient (polinomial) nu este cunoscut pentru a găsi soluția optimă în cazul general. De exemplu:

| N (orașe) | Tururi posibile | Observație                       |
| --------- | --------------- | -------------------------------- |
| 5         | 12              | Rezolvabil imediat               |
| 10        | 181.440         | Rezolvabil rapid cu backtracking |
| 15        | ~43 miliarde    | Backtracking devine lent         |
| 20        | ~6 × 10^16      | Backtracking prohibitiv          |
| 50        | ~10^62          | Necesar algoritm euristic        |

---

### 3.2 Matricea de distanțe — graful complet

Datele de intrare ale problemei TSP sunt reprezentate printr-o **matrice de distanțe** (sau costuri) `D` de dimensiune `N × N`, unde `D[i][j]` reprezintă costul deplasării de la orașul `i` la orașul `j`.

**Recomandare:** Se va folosi un **graf complet** (fiecare oraș este direct conectat cu toate celelalte). Aceasta corespunde definiției clasice a TSP și prezintă mai multe avantaje:

- Simplifică implementarea (nu este necesară verificarea existenței unui drum).
- Garantează că orice permutare a orașelor constituie un tur valid.
- Corespunde scenariilor practice în care deplasarea între oricare două puncte este posibilă (eventual prin rute indirecte, distanța euclidiană etc.).

**Proprietăți ale matricei:**

- `D[i][i] = 0` pentru orice `i` (distanța unui oraș față de el însuși este zero).
- `D[i][j] > 0` pentru orice `i ≠ j` (toate drumurile au cost strict pozitiv).
- `D[i][j] = D[j][i]` pentru TSP **simetric** (costul drumului este același în ambele direcții) — cazul standard implementat în acest laborator.

**Exemplu vizual pentru N = 4 orașe (0, 1, 2, 3):**

```
        0    1    2    3
   0  [ 0   10   15   20 ]
   1  [10    0   35   25 ]
   2  [15   35    0   30 ]
   3  [20   25   30    0 ]
```

Turul optim pentru această instanță este: `0 → 1 → 3 → 2 → 0`, cu costul `10 + 25 + 30 + 15 = 80`.

---

### 3.3 Formatul fișierului de intrare

Fișierul de intrare este un fișier text simplu cu următoarea structură:

```
N
D[0][0]  D[0][1]  ...  D[0][N-1]
D[1][0]  D[1][1]  ...  D[1][N-1]
...
D[N-1][0]  D[N-1][1]  ...  D[N-1][N-1]
```

- **Prima linie:** un singur număr întreg `N` — numărul de orașe.
- **Următoarele `N` linii:** câte `N` numere întregi separate prin spații — rândul `i` conține costurile de la orașul `i` la toate celelalte orașe.
- Matricea este **simetrică**: `D[i][j] == D[j][i]`.
- Diagonala este **zero**: `D[i][i] == 0`.

**Exemplu complet (`orase.txt`):**

```text
4
0 10 15 20
10 0 35 25
15 35 0 30
20 25 30 0
```

---

## 4. Implementare de referință: backtracking recursiv (monolitic)

### 4.1 Descrierea algoritmului

**Backtracking-ul** explorează **sistematic și exhaustiv** spațiul de soluții prin construirea incrementală a unui traseu și abandonarea ("tăierea") ramurilor care nu pot conduce la o soluție mai bună decât cea deja găsită.

**Principii de funcționare:**

1. Se fixează **orașul de start** (orașul `0`) pentru a elimina soluțiile echivalente prin rotație (optimizare validă pentru TSP simetric).
2. La fiecare pas recursiv, se adaugă un **oraș nevizitat** la traseul curent, actualizând costul acumulat.
3. **Prunerea branch-and-bound:** dacă costul parțial curent depășește sau egalează cel mai bun cost complet găsit până acum, ramura este abandonată imediat. Condiția `cost_parțial >= cost_minim_cunoscut` este validă deoarece toate distanțele sunt strict pozitive — costul nu poate decât să crească.
4. Când toate `N` orașele au fost vizitate, se închide turul prin revenirea la orașul `0` și se actualizează soluția optimă dacă este cazul.

**Pseudocod:**

```
funcție BACKTRACKING(matrice, n, oraș_curent, vizitat[], traseu[], cost_curent):
    dacă lungime(traseu) == n:
        cost_total ← cost_curent + matrice[oraș_curent][traseu[0]]
        dacă cost_total < cost_minim_global:
            actualizează soluția optimă
        returnează

    pentru fiecare oraș_următor de la 0 la n-1:
        dacă vizitat[oraș_următor]:
            continuă

        cost_nou ← cost_curent + matrice[oraș_curent][oraș_următor]
        dacă cost_nou >= cost_minim_global:   // prunere
            continuă

        vizitat[oraș_următor] ← Adevărat
        adaugă oraș_următor la traseu
        BACKTRACKING(matrice, n, oraș_următor, vizitat, traseu, cost_nou)
        elimină ultimul element din traseu
        vizitat[oraș_următor] ← Fals
```

---

### 4.2 Implementare Python

Implementarea de referință este **monolitică** — conținută integral într-un singur fișier Python, cu funcții interne documentate în stil Google.

```python
"""Rezolvarea problemei comis-voiajorului prin backtracking recursiv.

Implementare de referinta monolitica: un singur fisier Python, fara module externe.
Algoritmul garanteaza gasirea traseului de cost minim (solutia optima globala).

Utilizare:
    python backtracking_ref.py <fisier_intrare>

Exemplu:
    python backtracking_ref.py orase.txt
"""

import sys
import time


def citeste_matrice(cale_fisier):
    """Citeste matricea de distante dintr-un fisier text.

    Formatul fisierului: prima linie contine N (numarul de orase),
    urmatoarele N linii contin cate N intregi separati prin spatii,
    reprezentand matricea de distante NxN.

    Args:
        cale_fisier: Calea catre fisierul de intrare (str).

    Returns:
        Un tuplu (n, matrice) unde n este numarul de orase (int) si matrice
        este o lista de liste de intregi de dimensiune NxN.

    Raises:
        FileNotFoundError: Daca fisierul nu exista la calea specificata.
        ValueError: Daca formatul fisierului este invalid.
    """
    with open(cale_fisier, 'r') as f:
        linii = [linie.strip() for linie in f if linie.strip()]
    n = int(linii[0])
    matrice = [[int(x) for x in linii[i + 1].split()] for i in range(n)]
    return n, matrice


# Variabile globale pentru solutia optima.
# Sunt resetate la inceputul fiecarei rulari in rezolva_tsp().
_cost_minim = sys.maxsize
_traseu_optim = []


def _backtracking(matrice, n, oras_curent, vizitat, traseu, cost):
    """Explorare recursiva a spatiului de solutii TSP prin backtracking.

    La fiecare apel recursiv se incearca extinderea traseului curent cu un
    oras nevizitat. Ramurile al caror cost partial depaseste minimul global
    cunoscut sunt abandonate imediat (prunere branch-and-bound).

    Args:
        matrice: Matricea de distante NxN (lista de liste de intregi).
        n: Numarul de orase (int).
        oras_curent: Indexul orasului in care ne aflam la pasul curent (int).
        vizitat: Lista de booleeni de lungime n; vizitat[i] este True daca
            orasul i a fost deja inclus in traseu.
        traseu: Lista cu orasele vizitate pana acum, in ordinea parcurgerii.
            Primul element este intotdeauna 0 (orasul de start).
        cost: Costul acumulat al traseului partial curent (int sau float).
    """
    global _cost_minim, _traseu_optim

    # Caz de baza: toate orasele au fost vizitate — inchidem turul.
    if len(traseu) == n:
        cost_total = cost + matrice[oras_curent][traseu[0]]
        if cost_total < _cost_minim:
            _cost_minim = cost_total
            _traseu_optim = traseu[:]  # copie a listei curente
        return

    # Pas recursiv: incercam extinderea traseului cu fiecare oras nevizitat.
    for urmator in range(n):
        if vizitat[urmator]:
            continue

        cost_nou = cost + matrice[oras_curent][urmator]

        # Prunere: abandonam ramura daca costul partial nu poate imbunatati
        # solutia optima cunoscuta (toate distantele sunt strict pozitive).
        if cost_nou >= _cost_minim:
            continue

        vizitat[urmator] = True
        traseu.append(urmator)

        _backtracking(matrice, n, urmator, vizitat, traseu, cost_nou)

        # Revenire (backtrack): restauram starea pentru a explora alte ramuri.
        traseu.pop()
        vizitat[urmator] = False


def rezolva_tsp(cale_fisier):
    """Rezolva TSP prin backtracking recursiv cu prunere branch-and-bound.

    Citeste datele din fisierul specificat, ruleaza algoritmul de backtracking
    si afiseaza traseul optim, costul minim si timpul de executie.

    Args:
        cale_fisier: Calea catre fisierul text cu matricea de distante (str).
    """
    global _cost_minim, _traseu_optim

    n, matrice = citeste_matrice(cale_fisier)
    print(f"Numar de orase: {n}")
    print("Matricea de distante:")
    for rand in matrice:
        print("  " + "  ".join(f"{val:4d}" for val in rand))
    print()

    # Resetam variabilele globale pentru a permite apeluri repetate.
    _cost_minim = sys.maxsize
    _traseu_optim = []

    # Fixam orasul de start la indexul 0 (optimizare pentru TSP simetric:
    # elimina N rotatii echivalente ale aceluiasi tur).
    vizitat = [False] * n
    vizitat[0] = True

    start = time.perf_counter()
    _backtracking(matrice, n, 0, vizitat, [0], 0)
    durata = time.perf_counter() - start

    if _traseu_optim:
        sir_traseu = " -> ".join(map(str, _traseu_optim))
        sir_traseu += f" -> {_traseu_optim[0]}"
        print(f"Traseu optim:   {sir_traseu}")
        print(f"Cost minim:     {_cost_minim}")
    else:
        print("Nu a fost gasit niciun traseu valid.")

    print(f"Timp de executie: {durata:.6f} secunde")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Utilizare: python backtracking_ref.py <fisier_intrare>")
        print("Exemplu:   python backtracking_ref.py orase.txt")
        sys.exit(1)
    rezolva_tsp(sys.argv[1])
```

**Ieșire așteptată pentru exemplul `orase.txt` (N = 4) de mai sus:**

```
Numar de orase: 4
Matricea de distante:
      0    10    15    20
     10     0    35    25
     15    35     0    30
     20    25    30     0

Traseu optim:   0 -> 1 -> 3 -> 2 -> 0
Cost minim:     80
Timp de executie: 0.000032 secunde
```

---

## 5. Rezolvarea TSP folosind biblioteca `simpleai`

### 5.1 Alegerea bibliotecii

Pentru implementarea algoritmului alpinistului se recomandă biblioteca **`simpleai`**, față de alternativa `aima-python`.

| Criteriu         | `simpleai`                                                              | `aima-python`                               |
| ---------------- | ----------------------------------------------------------------------- | ------------------------------------------- |
| Instalare        | `pip install simpleai`                                                  | Clonare manuală din GitHub                  |
| Versiuni PyPI    | Da                                                                      | Nu (pachet neoficial)                       |
| API              | Curat, stabil, orientat predare                                         | Mai complex, stâns legat de edițiile cărții |
| Documentație     | Dedicată, online                                                        | Cod sursă comentat                          |
| Algoritmi locali | `hill_climbing`, `hill_climbing_random_restarts`, `simulated_annealing` | Similari, dar API diferit                   |
| Recomandare      | **Da**                                                                  | Opțional, pentru aprofundare                |

`simpleai` urmează totuși structura conceptuală din *AIMA* (Russell & Norvig) și este conceput explicit pentru uz didactic, cu o interfață clară și ușor de extins.

---

### 5.2 Instalare și funcții disponibile

**Instalare:**

```bash
pip install simpleai
```

**Funcții disponibile pentru căutare locală** (`simpleai.search.local`):

| Funcție                                                                    | Descriere                                                                                |
| -------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| `hill_climbing(problem)`                                                   | Hill climbing steepest ascent de bază                                                    |
| `hill_climbing_random_restarts(problem, restarts_limit, iterations_limit)` | Cu reporniri aleatorii; returnează cea mai bună soluție din toate repornirile            |
| `simulated_annealing(problem, schedule_expr)`                              | Recoacere simulată — evită optimi locali prin acceptarea ocazională a stărilor mai slabe |

**Documentație oficială:** https://simpleai.readthedocs.io/

**Sursă GitHub:** https://github.com/simpleai-team/simpleai

---

### 5.3 Exemplu de utilizare

Pentru a folosi `simpleai`, problema TSP trebuie modelată ca o subclasă a `SearchProblem`, implementând metodele necesare căutării locale.

**Concepte cheie pentru modelarea TSP:**

- **Starea** este reprezentată ca un **tuplu** de indici de orașe, de exemplu `(0, 3, 1, 2)`, indicând ordinea de vizitare. Se folosește un tuplu (imutabil) deoarece `simpleai` poate utiliza stările drept chei de dicționar.
- **Vecinătatea 2-opt:** o operație clasică pentru TSP care inversează un segment al turului. Dintr-un tur de `N` orașe, aceasta generează O(N²) vecini și produce în practică soluții de calitate bună.
- **Funcția `value`:** `simpleai` **maximizează** această funcție. Deoarece TSP minimizează costul, `value` returnează **negativul costului** — maximizarea valorii corespunde minimizării costului.

## 6. Cerințele temei

Tema se predă ca un **proiect Python structurat** (nu ca fișier unic), organizat în mai multe module. Toate funcțiile vor fi documentate cu **comentarii în stil Google** (docstrings cu secțiunile `Args:`, `Returns:`, `Raises:` unde este cazul).

### 6.1 Sarcina A - backtracking ca proiect structurat

Reimplementați algoritmul de backtracking din implementarea de referință (Secțiunea 4) ca proiect cu module separate:

```
tsp_proiect/
├── requirements.txt
├── src/
├──── main.py
├──── utils/               # Punct de intrare: parsare argumente, apel functii, afisare rezultate
├────── io_utils.py        # citeste_matrice(cale_fisier), salveaza_rezultat(...)
├────── backtracking.py    # rezolva_tsp_backtracking(n, matrice) -> (traseu, cost)
└────── performance.py     # generare instante aleatorie, masurare timpi, grafice
```

**Cerințe specifice:**

- Eliminați variabilele globale din implementarea de referință. Funcția principală din `backtracking.py` va returna rezultatul prin **valoarea de retur** (tuplu `(traseu_optim, cost_minim)`).
- Funcțiile recursive interne pot fi implementate cu parametri suplimentari sau prin tehnica "wrapper cu lista mutabilă".
- Fiecare funcție publică va avea docstring complet în stil Google.

### 6.2 Sarcina B - hill climbing folosind`simpleai`, în același proiect

Adăugați în proiectul de la Sarcina A un modul suplimentar pentru rezolvarea TSP cu algoritmul alpinistului:

```
tsp_proiect/
└── hill_climbing_tsp.py  # TSPHillClimbing(SearchProblem), rezolva_tsp_hc(n, matrice, reporniri)
```

**Cerințe specifice:**

- Clasa `TSPHillClimbing` va fi documentată complet (docstring de clasă + docstring pentru fiecare metodă).
- Folosiți `hill_climbing_random_restarts` (nu varianta de bază) pentru rezultate mai bune.
- Funcția publică `rezolva_tsp_hc` va returna același format de tuplu `(traseu, cost)` ca funcția din `backtracking.py`, pentru a permite compararea directă.

### 6.3 Sarcina C - grafice de performanță

Implementați în `performance.py` un experiment comparativ între cele două algoritmi:

**Protocol experimental:**

1. Generați instanțe TSP aleatoare pentru valorile `N` (număr de orașe): `5, 7, 8, 10, 12` pentru ambii algoritmi; adăugați `15, 20, 30, 50` **exclusiv** pentru hill climbing (backtracking devine prohibitiv la N > 13–14).
2. Distanțele se generează aleatoriu ca întregi în intervalul `[1, 100]`, matrice simetrică. Folosiți un seed fix pentru reproductibilitate.
3. Măsurați timpul de execuție cu `time.perf_counter()`.
4. Generați un grafic cu **două subploturi** folosind `matplotlib`:
   - **Subplot stâng - scară liniară:** evidențiază comportamentul absolut al celor doi algoritmi.
   - **Subplot drept - scară logaritmică** (`semilogy`): relevă creșterea exponențială a backtracking-ului față de comportamentul cvasi-liniar al hill climbing-ului.
5. Salvați graficul ca fișier PNG (`comparare_performanta.png`).

**Exemplu de structură a funcției principale din `performance.py`:**

```python
def ruleaza_experiment():
    """Ruleaza experimentul comparativ si genereaza graficul de performanta."""
    valori_n_bt = [5, 7, 8, 10, 12]
    valori_n_hc = [5, 7, 8, 10, 12, 15, 20, 30, 50]
    # ... generare instante, masurare timpi, apel matplotlib ...
```

> **NOTA BENE**: limita "100" este aleasă ca referință. În realitate probabil nu aveți acces la un sistem suficient de puternic pentru a rezolva o problemă de complexitate N = 100. Probabil undeva pe la 20 -25 va fi limita atinsă! Pentru implementări non-exhaustive, puteți crește complexitatea peste limita de la algoritmul backtracking.

> **Notă:** La rularea backtracking-ului, se va nota în raport valoarea maximă a lui N pentru care timpul de execuție rămâne sub un prag acceptabil (ex. 30 de secunde). Această valoare va fi inclusa în analiza graficului.

---

## 7. Bibliografie

\[1\] Stuart Russell, Peter Norvig — *Artificial Intelligence: A Modern Approach*, ediția a 4-a, Pearson, 2020.
ISBN 978-0-13-468599-1. *(Capitolul 4: Search in Complex Environments — algoritmii de căutare locală, inclusiv hill climbing)*

\[2\] Documentație oficială `simpleai`:
https://simpleai.readthedocs.io/

\[3\] Sursă GitHub `simpleai`:
https://github.com/simpleai-team/simpleai
