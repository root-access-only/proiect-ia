# Proiect IA - Pioneer P3-DX + TSP + NLP

Aplicatie desktop Tkinter cu trei module:

1. Robot Pioneer P3-DX simulat in CoppeliaSim, cu navigatie autonoma si recunoastere de semne de circulatie prin OpenCV.
2. Cinci algoritmi de TSP: Backtracking, Nearest Neighbor, Hill Climbing, Simulated Annealing, Algoritm Genetic.
3. Pipeline NLP pentru clasificare de texte cu trei dataset-uri (20 Newsgroups, IMDB, AG News) si patru clasificatori (Naive Bayes, SVM, Logistic Regression, Random Forest).

## Pornire rapida

```
python -m pip install -r requirements.txt
python setup_scene.py
python run_gui.py
```

In GUI: tab Robot Pioneer + Vision -> Conecteaza -> Start navigatie.

## Cerinte

- Python 3.10+
- CoppeliaSim Edu 4.6+
- 4 GB RAM
- 2 GB liber pe disc

## Structura

```
proiect/
  run_gui.py          punct de intrare GUI
  run_tsp_cli.py      runner CLI pentru TSP
  setup_scene.py      configurare automata scena CoppeliaSim
  requirements.txt
  data/
    tsp/              instante TSP
    nlp/              CSV-uri NLP
    signs/            texturi semne
  scene/
    scena_proiect.ttt scena CoppeliaSim
  output/             grafice si rapoarte
  src/
    tsp/              algoritmi TSP
    nlp/              pipeline NLP
    robot/            driver, vision, controller
    gui/              aplicatia Tkinter
```

## Instalare

```
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Descarca CoppeliaSim Edu de la coppeliarobotics.com, deschide scena `scene/scena_proiect.ttt` si apasa Play.

Apoi ruleaza o singura data:

```
python setup_scene.py
```

Acesta dezactiveaza scriptul Lua default al robotului, genereaza texturile semnelor, plaseaza 12 semne in fata robotului si repozitioneaza vision sensor-ul.

## Tab 1 - Robot Pioneer + Vision

Folosit pentru navigatie autonoma. Mașina cu stari:

| Stare              | Descriere                              |
| ------------------ | -------------------------------------- |
| IDLE               | inactiv                                |
| CRUISE             | navigare normala                       |
| SLOW               | viteza redusa                          |
| STOPPED_AT_SIGN    | oprire la stop/yield                   |
| WAIT_FOR_GREEN     | oprire la semafor rosu                 |
| AVOIDING           | evitare obstacole Braitenberg          |
| EMERGENCY_STOP     | obstacol foarte aproape                |
| TURNING_LEFT       | viraj 90 grade stanga                  |
| TURNING_RIGHT      | viraj 90 grade dreapta                 |

Semne recunoscute:

| Eticheta              | Actiune robot              |
| --------------------- | -------------------------- |
| stop                  | Oprire 2.5s                |
| yield                 | Oprire scurta              |
| no_entry              | Oprire prelungita          |
| speed_limit_30/50/80  | Limita viteza              |
| mandatory_forward     | Informativ                 |
| mandatory_left        | Viraj 90 grade stanga      |
| mandatory_right       | Viraj 90 grade dreapta     |
| traffic_light_red     | Oprire pana la verde       |
| traffic_light_yellow  | Viteza redusa              |
| traffic_light_green   | Reluare cruise             |

Parametri configurabili din GUI:

- v_cruise, v_slow, v_max - viteze
- stop pauza - durata opririi la STOP
- emergency dist, avoid dist - praguri sonari
- Braitenberg gain - sensibilitate la obstacole
- Min confidence - prag detectie OpenCV

## Tab 2 - TSP

Cinci algoritmi configurabili. Fiecare returneaza cost, timp, iteratii, istoric pentru convergenta.

Parametri:

- BKT: mod oprire (toate / prima / timp / y_solutii), limita timp
- NN: single sau multistart
- HC: variant (steepest / stochastic / random_restart), reporniri, init (random / NN)
- SA: T_max, T_min, alpha, schedule (geometric / linear / logarithmic), iteratii
- GA: populatie, generatii, mutatie, crossover, elitism, selectie (tournament / roulette)

Vizualizari salvate in `output/`:

- convergence.png - curbe de convergenta
- cost_time.png - cost final si timp per algoritm
- scalability.png - experiment pe mai multe N

Rulare CLI:

```
python run_tsp_cli.py --n 10 --bkt-mode toate
python run_tsp_cli.py --file data/tsp/orase10.txt
```

## Tab 3 - NLP

Pipeline scikit-learn:

- Dataset-uri: 20 Newsgroups (20 clase), IMDB (binar), AG News (4 topicuri)
- Vectorizers: TF-IDF sau BoW
- Clasificatori: Multinomial NB, Linear SVM, Logistic Regression, Random Forest
- Parametri: ngram range, max_features, min_df, max_df, stop words, test fraction, sample size

Vizualizari:

- nlp_confusion.png - confusion matrix
- nlp_compare.png - comparare 4 clasificatori

Predictie text liber: scrii un text, alegi dataset + clasificator, primesti categoria prezisa.

## Demo rapid

Robot autonom:

1. Deschide CoppeliaSim cu scena, apasa Play
2. `python setup_scene.py`
3. `python run_gui.py`
4. Tab Robot -> Conecteaza -> Start navigatie

TSP:

1. Tab TSP -> N=10, seed=42 -> Genereaza aleator
2. Ruleaza toti algoritmii
3. Vezi tabel + grafic de convergenta

NLP:

1. Tab NLP -> dataset = imdb_reviews, classifier = logreg
2. Antreneaza & evalueaza
3. Scrie o recenzie in textbox -> Classify

## Probleme frecvente

| Simptom                                   | Rezolvare                                 |
| ----------------------------------------- | ----------------------------------------- |
| ConnectionRefusedError                    | Porneste CoppeliaSim cu Play              |
| ModuleNotFoundError: cv2                  | pip install opencv-python                 |
| Camera label (camera offline)             | Ruleaza python setup_scene.py             |
| Robotul nu se misca dupa Start navigatie  | Ruleaza python setup_scene.py             |
| Imagine camera inversata                  | Editeaza simulator.py linia np.flipud     |
| Detectorul nu prinde semafoarele          | Regenereaza: python -m src.robot.sign_generator |
| Semnele dispar la deschiderea scenei      | Salveaza scena dupa setup_scene.py        |
| GUI crapa                                 | pip install -r requirements.txt           |

## Note de implementare

- Detector OpenCV: HSV + analiza contur. Discriminare prin raport arie / cerc minim inconjurator (~0.9 octogon, >0.93 cerc).
- Recunoastere cifra (30/50/80): topologia contururilor.
- Directia sagetii mandatory: centroid pixeli albi in interiorul discului.
- FSM evita declansarea repetata folosind o amprenta a bounding-box-ului.
- Controller-ul ruleaza intr-un thread separat. GUI primeste evenimente prin tkinter.after().
