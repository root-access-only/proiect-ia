# Proiect Inteligență Artificială — Pioneer P3-DX + TSP + NLP

Proiect integrat care reunește, într-o singură aplicație **Tkinter desktop**,
cele trei mari teme parcurse pe parcursul laboratoarelor de IA:

1. **Sistem de navigație autonomă** pentru robotul **Pioneer P3-DX** simulat
   în **CoppeliaSim**, cu detecție de **semne de circulație și semafoare**
   în timp real folosind **OpenCV**. Robotul oprește la STOP, încetinește
   la galben, virează la dreapta/stânga la semne obligatorii, așteaptă verdele
   la semafor, evită obstacole reactiv (Braitenberg) ș.a.m.d.

2. **Cinci algoritmi de TSP** parametrizabili — Backtracking (BKT),
   Nearest Neighbor (NN), Hill Climbing (HC), Simulated Annealing (SA) și
   Algoritm Genetic (GA) — cu grafice de convergență, comparație cost/timp
   și experiment de scalabilitate.

3. **Pipeline NLP** parametrizabil pentru clasificarea textelor cu trei
   dataset-uri în limba engleză (20 Newsgroups, IMDB reviews, AG News) și
   patru clasificatori (Naive Bayes, SVM liniar, Regresie Logistică,
   Random Forest).

---

## ⚡ Pornire rapidă (TL;DR)

```bash
# 1. Clonează repo-ul
git clone https://github.com/root-access-only/proiect-ia.git
cd proiect-ia/pioneer-vision-tsp-nlp

# 2. Instalează dependențele Python
python -m pip install -r requirements.txt

# 3. Pornește CoppeliaSim și deschide scena
#    File → Open Scene → scene/scena_proiect.ttt
#    Apasă ▶ Play

# 4. Configurează scena automat (creează semne, dezactivează script default)
python setup_scene.py

# 5. Pornește interfața grafică principală
python run_gui.py
```

În GUI: tab **Robot Pioneer + Vision** → **Conecteaza** → **Start navigatie**.

---

## 📋 Cerințe sistem

| Software         | Versiune minimă | Notă                                  |
| ---------------- | --------------- | ------------------------------------- |
| **Python**       | 3.10+           | Testat pe 3.12 / 3.14                 |
| **CoppeliaSim**  | 4.6+            | Edu sau Pro                           |
| **Sistem**       | Windows / Linux / macOS | Tkinter inclus în Python standard |
| **RAM**          | 4 GB+           | 8 GB recomandat pentru NLP            |
| **Disk**         | 2 GB liber      | Include CoppeliaSim, datasets         |

---

## 📁 Structura proiectului

```
pioneer-vision-tsp-nlp/
├── README.md                          # acest fișier
├── requirements.txt                   # dependențe Python
├── .gitignore
│
├── run_gui.py                         # punctul de intrare în GUI
├── run_tsp_cli.py                     # runner CLI pentru TSP (rapoarte)
├── setup_scene.py                     # configurare automată scenă CoppeliaSim
│
├── data/
│   ├── tsp/                           # instanțe TSP (.txt)
│   │   ├── orase4.txt
│   │   ├── orase5.txt
│   │   └── orase10.txt
│   ├── nlp/                           # CSV-uri NLP (opțional)
│   └── signs/                         # texturi PNG generate pt CoppeliaSim
│       ├── stop.png
│       ├── yield.png
│       ├── no_entry.png
│       ├── speed_limit_30.png  /  50.png  /  80.png
│       ├── mandatory_forward.png  /  left.png  /  right.png
│       └── traffic_light_red.png  /  yellow.png  /  green.png
│
├── output/                            # grafice și rapoarte salvate la rulare
│
├── scene/
│   ├── SCENE_SETUP.md                 # ghid pas-cu-pas scena CoppeliaSim
│   └── scena_proiect.ttt              # scena pregătită (drum + case + robot)
│
└── src/
    ├── tsp/                           # BKT, NN, HC, SA, GA + comparator
    ├── nlp/                           # dataset-uri, pipeline, plot-uri
    ├── robot/                         # driver CoppeliaSim, OpenCV vision,
    │                                  # controller FSM, generator texturi
    └── gui/                           # aplicația Tkinter cu 3 tab-uri
```

---

## 🔧 Instalare detaliată

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

### 3. Dependențe

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Dependențele acoperă:
- **TSP**: `numpy`, `matplotlib`, `simpleai`, `simanneal`, `pygad`
- **NLP**: `scikit-learn`, `nltk`, `pandas`, `seaborn`
- **Robot**: `opencv-python`, `coppeliasim-zmqremoteapi-client`, `Pillow`
- **GUI**: `tkinter` (vine cu Python)

### 4. CoppeliaSim

Descarcă **CoppeliaSim Edu 4.6+** de la [coppeliarobotics.com](https://www.coppeliarobotics.com/downloads).
Instalează normal, lansează aplicația, deschide scena:

```
File → Open Scene → <calea_ta>/pioneer-vision-tsp-nlp/scene/scena_proiect.ttt
```

Apasă **▶ Play** (sau Simulation → Start simulation).

> Important: **trebuie să fie deschis CoppeliaSim cu simularea pornită**
> înainte să rulezi orice script Python care folosește robotul.

### 5. Setup scenă (UNA singură dată per scenă nouă)

```bash
python setup_scene.py
```

Acesta:
- Dezactivează scriptul Lua default al lui Pioneer (Braitenberg-ul propriu
  care intră în conflict cu controller-ul Python)
- Generează texturile semnelor dacă lipsesc
- Creează 12 cuboizi-semne și le aplică texturile
- Le plasează în fața robotului, alternativ stânga/dreapta, la 5 m unul de altul
- Repoziționează corect vision sensor-ul pe robot

### 6. Pornește GUI-ul

```bash
python run_gui.py
```

---

## 🤖 Tab 1 — Robot Pioneer + Vision

Folosește modulele din [src/robot/](src/robot/):

- [simulator.py](src/robot/simulator.py) — wrapper ZMQ peste API-ul CoppeliaSim
- [vision.py](src/robot/vision.py) — detector OpenCV (HSV + contururi + topologie)
- [controller.py](src/robot/controller.py) — controller cu **mașină de stări (FSM)**
- [sign_generator.py](src/robot/sign_generator.py) — generator PNG-uri texturi

### Mașina de stări implementată

| Stare              | Descriere                                                            |
| ------------------ | -------------------------------------------------------------------- |
| `IDLE`             | inactiv                                                              |
| `CRUISE`           | navigare normală                                                     |
| `SLOW`             | viteză redusă (galben sau speed limit)                               |
| `STOPPED_AT_SIGN`  | oprire temporizată (STOP, YIELD, NO ENTRY)                           |
| `WAIT_FOR_GREEN`   | oprire la semafor roșu, repornire la verde                           |
| `AVOIDING`         | evitare obstacole Braitenberg                                        |
| `EMERGENCY_STOP`   | obstacol foarte aproape                                              |
| `TURNING_LEFT`     | viraj 90° stânga (declanșat de mandatory_left)                       |
| `TURNING_RIGHT`    | viraj 90° dreapta (declanșat de mandatory_right)                     |

### Semne și semafoare recunoscute

| Etichetă                       | Formă                | Acțiune robot              |
| ------------------------------ | -------------------- | -------------------------- |
| `stop`                         | Octogon roșu         | Oprire 2.5s, apoi continuă |
| `yield`                        | Triunghi roșu        | Oprire scurtă (1.2s)       |
| `no_entry`                     | Cerc roșu + bară     | Oprire prelungită          |
| `speed_limit_30/50/80`         | Cerc + cifră         | Limită viteză              |
| `mandatory_forward`            | Cerc albastru + ↑    | Informativ                 |
| `mandatory_left`               | Cerc albastru + ←    | Viraj 90° stânga           |
| `mandatory_right`              | Cerc albastru + →    | Viraj 90° dreapta          |
| `traffic_light_red`            | Lampă roșie aprinsă  | Oprire până la verde       |
| `traffic_light_yellow`         | Lampă galbenă        | Viteză redusă              |
| `traffic_light_green`          | Lampă verde          | Reluare cruise             |

### Parametri configurabili în GUI

Tab Robot → secțiunea **Parametri navigație**:

- `v_cruise`, `v_slow`, `v_max` — viteze (rad/s)
- `stop pauza` — durata opririi la STOP
- `emergency dist`, `avoid dist` — praguri sonari
- `Braitenberg gain` — sensibilitate la obstacole
- `Min confidence` — prag detecție OpenCV

---

## 🧮 Tab 2 — TSP (BKT / NN / HC / SA / GA)

Toți algoritmii returnează un `TSPResult` standardizat (cost, timp,
număr iterații, istoric pentru convergență, parametri).

### Parametrizare (configurabilă în GUI)

- **BKT**: mod oprire (`toate` / `prima` / `timp` / `y_solutii`), limită timp
- **NN**: variantă single sau multistart
- **HC**: variantă (steepest / stochastic / random_restart), număr reporniri,
  inițializare (random / NN warm-start)
- **SA**: T_max, T_min, alpha, schedule (geometric / linear / logarithmic),
  iterații, inițializare
- **GA**: dimensiune populație, generații, rata mutație, rata crossover,
  elitism, selecție (tournament / roulette)

### Vizualizări

- `output/convergence.png` — curbe de convergență suprapuse
- `output/cost_time.png` — bar chart cost final + curbă timp per algoritm
- `output/scalability.png` — experiment pe mai multe N

### Rulare headless

```bash
python run_tsp_cli.py --n 10 --bkt-mode toate
python run_tsp_cli.py --file data/tsp/orase10.txt
```

---

## 📚 Tab 3 — NLP

Pipeline scikit-learn:
- **3 dataset-uri Engleză**: 20 Newsgroups (20 clase), IMDB sentiment (binar),
  AG News (4 topicuri)
- **2 vectorizers**: TF-IDF (sublinear + L2) sau BoW
- **4 clasificatori**: Multinomial NB, Linear SVM, Logistic Regression,
  Random Forest
- **Parametri reglabili**: ngram range, max_features, min_df / max_df,
  stop words, test fraction, sample size

### Vizualizări

- `output/nlp_confusion.png` — confusion matrix
- `output/nlp_compare.png` — bar chart accuracy/precision/recall/F1

### Predicție text liber

Câmpul "Predictie text liber" din tab antrenează pipeline-ul ales pe tot
dataset-ul și clasifică textul introdus.

---

## 🧪 Cum rulează un experiment complet

### Demo robot autonom

1. Deschide CoppeliaSim cu `scene/scena_proiect.ttt`, apasă ▶
2. Rulează `python setup_scene.py` — apar 12 semne în fața robotului
3. Rulează `python run_gui.py`
4. Tab Robot → **Conecteaza** → **Start navigatie**
5. Vei vedea în log:
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

1. Tab TSP → N=10, seed=42 → **Genereaza aleator**
2. **Ruleaza toti algoritmii**
3. Vezi tabel cu cost / timp / iters, click "Convergenta" pentru grafic

### Demo NLP

1. Tab NLP → dataset = `imdb_reviews`, classifier = `logreg`
2. **Antreneaza & evalueaza**
3. Raport + confusion matrix
4. Textbox: scrie o recenzie de film → **Classify** → predicție

---

## 🛠️ Troubleshooting

| Simptom                                   | Cauză probabilă                         | Rezolvare                                       |
| ----------------------------------------- | --------------------------------------- | ----------------------------------------------- |
| `ConnectionRefusedError`                  | CoppeliaSim nu rulează                  | Pornește CoppeliaSim cu ▶ Play                  |
| `ModuleNotFoundError: cv2`                | OpenCV nu e instalat                    | `pip install opencv-python`                     |
| Camera label rămâne `(camera offline)`    | visionSensor lipsește sau e cu altă cale | Rulează `python setup_scene.py`                 |
| Robotul nu se mișcă după Start navigatie  | Script Pioneer default activ            | Rulează `python setup_scene.py`                 |
| Imagine cameră inversată                  | Diferență flip între versiuni           | Editează `simulator.py` linia cu `np.flipud`    |
| Detectorul nu prinde semafoarele          | Lămpile prea închise în material        | Regenerează: `python -m src.robot.sign_generator` |
| Semnele dispar la deschiderea scenei      | Texturile nu sunt embeded               | Salvează scena DUPĂ `setup_scene.py`            |
| `mandatory_right` detectat dar nu virează | Cod vechi                               | Pull ultima versiune; restart GUI               |
| GUI crapă imediat                         | Lipsește o dependență                   | `pip install -r requirements.txt`               |

---

## 🤝 Pentru colegii care preiau proiectul

1. **Citește acest README integral.** Toate trucurile sunt aici.
2. **Pasul de aur**: după ce deschizi scena, **întotdeauna** rulează
   `python setup_scene.py` o singură dată. Acesta dezactivează scriptul
   default al lui Pioneer, fără de care **nimic nu va merge** — robotul își va
   face propria treabă ignorând Python-ul.
3. **Pentru a salva munca**: după ce ai configurat scena și ai mutat semnele
   unde îți place, fă `File → Save scene` în CoppeliaSim. Texturile se
   încorporează automat în fișierul `.ttt`.
4. **Modificări la cod**: orice editare în `src/` se reflectă imediat;
   restart GUI prin `python run_gui.py` și gata.
5. **Modificări la parametri navigație**: tot din GUI prin slider-e — nu
   trebuie să editezi cod.

---

## 📐 Note de implementare

- **Detector OpenCV**: HSV + analiză contur — discriminează octogon vs cerc
  prin **raport arie / cerc minim înconjurător** (~0.9 pentru octogon, >0.93
  pentru cerc).
- **Recunoaștere cifră** (30/50/80) — topologia contururilor: "8" are 2 găuri,
  "0" are 1, "3" și "5" nu au; "3" vs "5" prin distribuția cernelii în
  jumătatea superioară.
- **Direcția săgeții obligatorii** — centroidul pixelilor albi din interiorul
  discului albastru.
- **FSM-ul de navigație** — evită declanșarea repetată a aceluiași STOP/turn
  folosind o "amprentă" coarsă a bounding-box-ului semnului.
- **Threading**: controller-ul rulează într-un thread daemon separat. GUI-ul
  primește evenimente prin `tkinter.after(0, ...)` pentru thread-safety.

---

## 📝 Licență & atribuiri

Proiect academic pentru cursul de Inteligență Artificială.
- Bibliotecile externe folosite își păstrează licențele lor.
- Texturile semnelor sunt generate procedural cu PIL.
- Scena CoppeliaSim e construită manual peste modelul standard Pioneer P3-DX.

Autori: vezi commit history.
