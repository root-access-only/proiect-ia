# Proiect Inteligenta Artificiala - Pioneer P3-DX + TSP + NLP

Proiect integrat care reuneste, intr-o singura aplicatie **Tkinter desktop**,
cele trei mari teme parcurse pe parcursul laboratoarelor de IA:

1. **Sistem de navigatie autonoma** pentru robotul **Pioneer P3-DX** simulat
   in **CoppeliaSim**, cu detectie de **semne de circulatie si semafoare**
   in timp real folosind **OpenCV**. Robotul opreste la STOP, incetineste
   la galben, vireaza la dreapta/stanga la semne obligatorii, asteapta verdele
   la semafor, evita obstacole reactiv (Braitenberg) s.a.m.d.

2. **Cinci algoritmi de TSP** parametrizabili - Backtracking (BKT),
   Nearest Neighbor (NN), Hill Climbing (HC), Simulated Annealing (SA) si
   Algoritm Genetic (GA) - cu grafice de convergenta, comparatie cost/timp
   si experiment de scalabilitate.

3. **Pipeline NLP** parametrizabil pentru clasificarea textelor cu trei
   dataset-uri in limba engleza (20 Newsgroups, IMDB reviews, AG News) si
   patru clasificatori (Naive Bayes, SVM liniar, Regresie Logistica,
   Random Forest).

---

## Pornire rapida (TL;DR)

```bash
# 1. Cloneaza repo-ul
git clone https://github.com/root-access-only/proiect-ia.git
cd proiect-ia/pioneer-vision-tsp-nlp

# 2. Instaleaza dependentele Python
python -m pip install -r requirements.txt

# 3. Porneste CoppeliaSim si deschide scena
#    File -> Open Scene -> scene/scena_proiect.ttt
#    Apasa Play

# 4. Configureaza scena automat (creeaza semne, dezactiveaza script default)
python setup_scene.py

# 5. Porneste interfata grafica principala
python run_gui.py
```

In GUI: tab **Robot Pioneer + Vision** -> **Conecteaza** -> **Start navigatie**.

---

## Cerinte sistem

| Software         | Versiune minima | Nota                                    |
| ---------------- | --------------- | --------------------------------------- |
| **Python**       | 3.10+           | Testat pe 3.12 / 3.14                   |
| **CoppeliaSim**  | 4.6+            | Edu sau Pro                             |
| **Sistem**       | Windows / Linux / macOS | Tkinter inclus in Python standard |
| **RAM**          | 4 GB+           | 8 GB recomandat pentru NLP              |
| **Disk**         | 2 GB liber      | Include CoppeliaSim, datasets           |

---

## Structura proiectului

```
pioneer-vision-tsp-nlp/
├── README.md                          # acest fisier
├── requirements.txt                   # dependente Python
├── .gitignore
│
├── run_gui.py                         # punctul de intrare in GUI
├── run_tsp_cli.py                     # runner CLI pentru TSP (rapoarte)
├── setup_scene.py                     # configurare automata scena CoppeliaSim
│
├── data/
│   ├── tsp/                           # instante TSP (.txt)
│   │   ├── orase4.txt
│   │   ├── orase5.txt
│   │   └── orase10.txt
│   ├── nlp/                           # CSV-uri NLP (optional)
│   └── signs/                         # texturi PNG generate pt CoppeliaSim
│       ├── stop.png
│       ├── yield.png
│       ├── no_entry.png
│       ├── speed_limit_30.png  /  50.png  /  80.png
│       ├── mandatory_forward.png  /  left.png  /  right.png
│       └── traffic_light_red.png  /  yellow.png  /  green.png
│
├── output/                            # grafice si rapoarte salvate la rulare
│
├── scene/
│   ├── SCENE_SETUP.md                 # ghid pas-cu-pas scena CoppeliaSim
│   └── scena_proiect.ttt              # scena pregatita (drum + case + robot)
│
└── src/
    ├── tsp/                           # BKT, NN, HC, SA, GA + comparator
    ├── nlp/                           # dataset-uri, pipeline, plot-uri
    ├── robot/                         # driver CoppeliaSim, OpenCV vision,
    │                                  # controller FSM, generator texturi
    └── gui/                           # aplicatia Tkinter cu 3 tab-uri
```

---

## Instalare detaliata

### 1. Clonare repo

```bash
git clone https://github.com/root-access-only/proiect-ia.git
cd proiect-ia/pioneer-vision-tsp-nlp
```

### 2. Mediu virtual Python (recomandat)

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Dependente

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Dependentele acopera:
- **TSP**: `numpy`, `matplotlib`, `simpleai`, `simanneal`, `pygad`
- **NLP**: `scikit-learn`, `nltk`, `pandas`, `seaborn`
- **Robot**: `opencv-python`, `coppeliasim-zmqremoteapi-client`, `Pillow`
- **GUI**: `tkinter` (vine cu Python)

### 4. CoppeliaSim

Descarca **CoppeliaSim Edu 4.6+** de la [coppeliarobotics.com](https://www.coppeliarobotics.com/downloads).
Instaleaza normal, lanseaza aplicatia, deschide scena:

```
File -> Open Scene -> <calea_ta>/pioneer-vision-tsp-nlp/scene/scena_proiect.ttt
```

Apasa **Play** (sau Simulation -> Start simulation).

> Important: **trebuie sa fie deschis CoppeliaSim cu simularea pornita**
> inainte sa rulezi orice script Python care foloseste robotul.

### 5. Setup scena (UNA singura data per scena noua)

```bash
python setup_scene.py
```

Acesta:
- Dezactiveaza scriptul Lua default al lui Pioneer (Braitenberg-ul propriu
  care intra in conflict cu controller-ul Python)
- Genereaza texturile semnelor daca lipsesc
- Creeaza 12 cuboizi-semne si le aplica texturile
- Le plaseaza in fata robotului, alternativ stanga/dreapta, la 5 m unul de altul
- Repozitioneaza corect vision sensor-ul pe robot

### 6. Porneste GUI-ul

```bash
python run_gui.py
```

---

## Tab 1 - Robot Pioneer + Vision

Foloseste modulele din [src/robot/](src/robot/):

- [simulator.py](src/robot/simulator.py) - wrapper ZMQ peste API-ul CoppeliaSim
- [vision.py](src/robot/vision.py) - detector OpenCV (HSV + contururi + topologie)
- [controller.py](src/robot/controller.py) - controller cu **masina de stari (FSM)**
- [sign_generator.py](src/robot/sign_generator.py) - generator PNG-uri texturi

### Masina de stari implementata

| Stare              | Descriere                                                            |
| ------------------ | -------------------------------------------------------------------- |
| `IDLE`             | inactiv                                                              |
| `CRUISE`           | navigare normala                                                     |
| `SLOW`             | viteza redusa (galben sau speed limit)                               |
| `STOPPED_AT_SIGN`  | oprire temporizata (STOP, YIELD, NO ENTRY)                           |
| `WAIT_FOR_GREEN`   | oprire la semafor rosu, repornire la verde                           |
| `AVOIDING`         | evitare obstacole Braitenberg                                        |
| `EMERGENCY_STOP`   | obstacol foarte aproape                                              |
| `TURNING_LEFT`     | viraj 90 grade stanga (declansat de mandatory_left)                  |
| `TURNING_RIGHT`    | viraj 90 grade dreapta (declansat de mandatory_right)                |

### Semne si semafoare recunoscute

| Eticheta                       | Forma                | Actiune robot              |
| ------------------------------ | -------------------- | -------------------------- |
| `stop`                         | Octogon rosu         | Oprire 2.5s, apoi continua |
| `yield`                        | Triunghi rosu        | Oprire scurta (1.2s)       |
| `no_entry`                     | Cerc rosu + bara     | Oprire prelungita          |
| `speed_limit_30/50/80`         | Cerc + cifra         | Limita viteza              |
| `mandatory_forward`            | Cerc albastru + sus  | Informativ                 |
| `mandatory_left`               | Cerc albastru + stanga | Viraj 90 grade stanga    |
| `mandatory_right`              | Cerc albastru + dreapta | Viraj 90 grade dreapta  |
| `traffic_light_red`            | Lampa rosie aprinsa  | Oprire pana la verde       |
| `traffic_light_yellow`         | Lampa galbena        | Viteza redusa              |
| `traffic_light_green`          | Lampa verde          | Reluare cruise             |

### Parametri configurabili in GUI

Tab Robot -> sectiunea **Parametri navigatie**:

- `v_cruise`, `v_slow`, `v_max` - viteze (rad/s)
- `stop pauza` - durata opririi la STOP
- `emergency dist`, `avoid dist` - praguri sonari
- `Braitenberg gain` - sensibilitate la obstacole
- `Min confidence` - prag detectie OpenCV

---

## Tab 2 - TSP (BKT / NN / HC / SA / GA)

Toti algoritmii returneaza un `TSPResult` standardizat (cost, timp,
numar iteratii, istoric pentru convergenta, parametri).

### Parametrizare (configurabila in GUI)

- **BKT**: mod oprire (`toate` / `prima` / `timp` / `y_solutii`), limita timp
- **NN**: varianta single sau multistart
- **HC**: varianta (steepest / stochastic / random_restart), numar reporniri,
  initializare (random / NN warm-start)
- **SA**: T_max, T_min, alpha, schedule (geometric / linear / logarithmic),
  iteratii, initializare
- **GA**: dimensiune populatie, generatii, rata mutatie, rata crossover,
  elitism, selectie (tournament / roulette)

### Vizualizari

- `output/convergence.png` - curbe de convergenta suprapuse
- `output/cost_time.png` - bar chart cost final + curba timp per algoritm
- `output/scalability.png` - experiment pe mai multe N

### Rulare headless

```bash
python run_tsp_cli.py --n 10 --bkt-mode toate
python run_tsp_cli.py --file data/tsp/orase10.txt
```

---

## Tab 3 - NLP

Pipeline scikit-learn:
- **3 dataset-uri engleza**: 20 Newsgroups (20 clase), IMDB sentiment (binar),
  AG News (4 topicuri)
- **2 vectorizers**: TF-IDF (sublinear + L2) sau BoW
- **4 clasificatori**: Multinomial NB, Linear SVM, Logistic Regression,
  Random Forest
- **Parametri reglabili**: ngram range, max_features, min_df / max_df,
  stop words, test fraction, sample size

### Vizualizari

- `output/nlp_confusion.png` - confusion matrix
- `output/nlp_compare.png` - bar chart accuracy/precision/recall/F1

### Predictie text liber

Campul "Predictie text liber" din tab antreneaza pipeline-ul ales pe tot
dataset-ul si clasifica textul introdus.

---

## Cum rulezi un experiment complet

### Demo robot autonom

1. Deschide CoppeliaSim cu `scene/scena_proiect.ttt`, apasa Play
2. Ruleaza `python setup_scene.py` - apar 12 semne in fata robotului
3. Ruleaza `python run_gui.py`
4. Tab Robot -> **Conecteaza** -> **Start navigatie**
5. Vei vedea in log:
   ```
   12:30:01 [cruise] Navigation started
   12:30:03 [stopped_at_sign] STOP detectat (conf=0.92)
   12:30:06 [cruise] Repornire dupa stop/yield
   12:30:09 [turning_right] Mandatory RIGHT - virez dreapta
   12:30:11 [cruise] Viraj terminat - reiau cruise
   12:30:15 [wait_for_green] Semafor rosu - opresc
   12:30:18 [cruise] Semafor verde - repornesc
   ```

### Demo TSP

1. Tab TSP -> N=10, seed=42 -> **Genereaza aleator**
2. **Ruleaza toti algoritmii**
3. Vezi tabel cu cost / timp / iters, click "Convergenta" pentru grafic

### Demo NLP

1. Tab NLP -> dataset = `imdb_reviews`, classifier = `logreg`
2. **Antreneaza & evalueaza**
3. Raport + confusion matrix
4. Textbox: scrie o recenzie de film -> **Classify** -> predictie

---

## Troubleshooting

| Simptom                                   | Cauza probabila                         | Rezolvare                                       |
| ----------------------------------------- | --------------------------------------- | ----------------------------------------------- |
| `ConnectionRefusedError`                  | CoppeliaSim nu ruleaza                  | Porneste CoppeliaSim cu Play                    |
| `ModuleNotFoundError: cv2`                | OpenCV nu e instalat                    | `pip install opencv-python`                     |
| Camera label ramane `(camera offline)`    | visionSensor lipseste sau e cu alta cale | Ruleaza `python setup_scene.py`                |
| Robotul nu se misca dupa Start navigatie  | Script Pioneer default activ            | Ruleaza `python setup_scene.py`                 |
| Imagine camera inversata                  | Diferenta flip intre versiuni           | Editeaza `simulator.py` linia cu `np.flipud`    |
| Detectorul nu prinde semafoarele          | Lampile prea inchise in material        | Regenereaza: `python -m src.robot.sign_generator` |
| Semnele dispar la deschiderea scenei      | Texturile nu sunt embeded               | Salveaza scena DUPA `setup_scene.py`            |
| `mandatory_right` detectat dar nu vireaza | Cod vechi                               | Pull ultima versiune; restart GUI               |
| GUI crapa imediat                         | Lipseste o dependenta                   | `pip install -r requirements.txt`               |

---

## Pentru colegii care preiau proiectul

1. **Citeste acest README integral.** Toate trucurile sunt aici.
2. **Pasul de aur**: dupa ce deschizi scena, **intotdeauna** ruleaza
   `python setup_scene.py` o singura data. Acesta dezactiveaza scriptul
   default al lui Pioneer, fara de care **nimic nu va merge** - robotul isi va
   face propria treaba ignorand Python-ul.
3. **Pentru a salva munca**: dupa ce ai configurat scena si ai mutat semnele
   unde iti place, fa `File -> Save scene` in CoppeliaSim. Texturile se
   incorporeaza automat in fisierul `.ttt`.
4. **Modificari la cod**: orice editare in `src/` se reflecta imediat;
   restart GUI prin `python run_gui.py` si gata.
5. **Modificari la parametri navigatie**: tot din GUI prin slider-e - nu
   trebuie sa editezi cod.

---

## Note de implementare

- **Detector OpenCV**: HSV + analiza contur - discrimineaza octogon vs cerc
  prin **raport arie / cerc minim inconjurator** (~0.9 pentru octogon, >0.93
  pentru cerc).
- **Recunoastere cifra** (30/50/80): topologia contururilor: "8" are 2 gauri,
  "0" are 1, "3" si "5" nu au; "3" vs "5" prin distributia cerneala in
  jumatatea superioara.
- **Directia sagetii obligatorii**: centroidul pixelilor albi din interiorul
  discului albastru.
- **FSM-ul de navigatie**: evita declansarea repetata a aceluiasi STOP/turn
  folosind o "amprenta" coarsa a bounding-box-ului semnului.
- **Threading**: controller-ul ruleaza intr-un thread daemon separat. GUI-ul
  primeste evenimente prin `tkinter.after(0, ...)` pentru thread-safety.

---

## Licenta & atribuiri

Proiect academic pentru cursul de Inteligenta Artificiala.
- Bibliotecile externe folosite isi pastreaza licentele lor.
- Texturile semnelor sunt generate procedural cu PIL.
- Scena CoppeliaSim e construita manual peste modelul standard Pioneer P3-DX.

Autori: vezi commit history.
