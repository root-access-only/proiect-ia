# Tema A - Evitare cu recuperare

Am implementat o masina de stari cu 3 stari:

- FORWARD
- BACKWARD
- TURNING

Robotul merge inainte pana cand detecteaza un obstacol frontal la o distanta mai mica decat pragul STOP_DISTANCE. In acel moment intra in starea BACKWARD, unde merge inapoi timp de 1 secunda. Dupa aceea alege aleatoriu un viraj la stanga sau la dreapta si intra in starea TURNING. La finalul virajului revine in starea FORWARD.

Observatii:
- robotul nu ramane blocat permanent in fata obstacolelor
- alegerea aleatoare a directiei de viraj ajuta la iesirea din configuratii repetitive
- parametrii BACKWARD_TIME, TURN_TIME si STOP_DISTANCE au fost ajustati experimental
# Tema B - Braitenberg cu inregistrare de date

Am extins comportamentul Braitenberg de evitare a obstacolelor prin salvarea datelor de simulare intr-un fisier CSV.

## Date salvate
La fiecare iteratie sunt salvate:
- timestamp
- v_left
- v_right
- s0..s7
- pos_x
- pos_y

## Grafice generate
1. Traiectoria robotului in planul XY
2. Vitezele rotilor in functie de timp
3. Heatmap pentru activarea senzorilor s0-s7

## Observatii
- Cand robotul se apropie de obstacole, diferentele dintre v_left si v_right cresc.
- Traiectoria rezulta din reactia continua la senzorii frontali.
- Heatmap-ul arata clar momentele in care obstacolele au fost detectate de senzorii din fata.

## Tema C - Robot Explorer

### Descriere

În această temă am implementat un comportament de **explorare autonomă** pentru robotul Pioneer P3-DX, combinând:

- wall-following (urmărirea peretelui din dreapta)
- evitare obstacole frontale
- mecanism de recuperare la blocaj

Robotul este capabil să se deplaseze continuu într-o arenă cu obstacole, fără coliziuni, timp de cel puțin 60 de secunde.

---

### Stări implementate

Am folosit o mașină de stări cu următoarele stări:

- `SEARCH_WALL` – robotul caută un perete în dreapta
- `FOLLOW_WALL` – robotul urmărește peretele la o distanță constantă
- `AVOID_FRONT` – evită obstacolele frontale prin viraj
- `RECOVERY` – mecanism de ieșire din blocaj

---

### Strategie de control

- Robotul folosește un **controller proporțional (P)** pentru menținerea distanței față de perete:
  
- Dacă detectează un obstacol frontal:
- execută un viraj pe loc pentru evitare

- Dacă nu mai avansează suficient într-un interval de timp:
- este considerat blocat
- execută o secvență de recuperare:
  - mers înapoi
  - viraj aleator (stânga/dreapta)

---

### Parametri utilizați

- `TARGET_DIST = 0.4 m`
- `K_P = 3.0`
- `FRONT_STOP = 0.4 m`
- `RUN_TIME = 60 s`
- `RECOVERY_BACK_TIME ≈ 1.0 s`
- `RECOVERY_TURN_TIME ≈ 1.3 s`

Parametrii au fost ajustați experimental pentru stabilitate.

---

### Date salvate

Pe durata rulării se salvează:

- `timestamp`
- `pos_x`, `pos_y`
- starea curentă
- distanța frontală
- distanța laterală dreapta

---

### Rezultate

- robotul explorează arena fără coliziuni majore
- nu rămâne blocat permanent
- traiectoria este salvată în fișier CSV
- este generat graficul traiectoriei în planul XY
- a fost realizată o captură video de minimum 60 secunde

---

### Observații

- fără mecanism de recovery, robotul rămâne blocat în colțuri
- alegerea aleatoare a direcției de viraj ajută la ieșirea din situații repetitive
- valorile prea mari pentru `K_P` duc la oscilații
- valorile prea mici duc la reacții lente

---

## Tema D - Braitenberg "Iubire"

### Descriere

În această temă am implementat un vehicul Braitenberg de tip **„Iubire”**, bazat pe conexiuni:

- **ipsilaterale** (senzorul influențează motorul de pe aceeași parte)
- **inhibitorii** (reduc viteza)

---

### Principiu de funcționare

- senzorii din stânga reduc viteza roții stângi
- senzorii din dreapta reduc viteza roții drepte

Efect:

- robotul se orientează către stimul
- pe măsură ce se apropie, încetinește
- foarte aproape de obstacol, viteza devine foarte mică

---

### Comportament emergent

Robotul:

- se apropie de obstacole
- își reduce viteza gradual
- nu se lovește agresiv de ele

Acest comportament este interpretat ca o formă de **„atracție blândă”**, de unde denumirea de „Iubire”.

---

### Diferență față de alte comportamente

| Tip comportament | Efect |
|-----------------|------|
| Frică           | evită obstacolele |
| Agresivitate    | merge direct spre obstacole |
| Iubire          | se apropie și încetinește |

---

### Parametri utilizați

- `V_BASE ≈ 4.0`
- `K_SENSOR ≈ 4.5`

Acești parametri controlează:
- viteza inițială
- intensitatea reacției la senzori

---

### Observații

- dacă `K_SENSOR` este prea mare → robotul se oprește prea devreme
- dacă este prea mic → nu reacționează suficient
- comportamentul este complet reactiv, fără memorie sau planificare

---

## Concluzie

Prin implementarea temelor C și D:

- am explorat comportamente reactive complexe
- am combinat controlul bazat pe reguli simple cu rezultate emergente
- am demonstrat cum comportamente aparent inteligente pot apărea din reguli simple de tip senzor → motor