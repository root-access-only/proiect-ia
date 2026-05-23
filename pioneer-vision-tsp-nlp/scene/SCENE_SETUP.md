# Ghid scenă CoppeliaSim - Pioneer P3-DX cu vision sensor

Acest document explică **exact** ce trebuie adăugat în scena CoppeliaSim pentru
ca proiectul de navigație să funcționeze. Documentul presupune CoppeliaSim 4.6+
și fișierul de pornire `pioneer_lab06.ttt` din laboratorul #06 (sau o scenă
similară cu un Pioneer P3-DX deja prezent).

## 0. Cerințe preliminare

- CoppeliaSim instalat și pornit.
- Scena conține un Pioneer P3-DX la calea `/PioneerP3DX` cu motoarele
  `leftMotor` și `rightMotor` și 16 senzori `ultrasonicSensor[0..15]`.
- ZMQ Remote API activ (este activ implicit pe port 23000).

---

## 1. Adăugarea senzorului de viziune pe robot

Robotul Pioneer P3-DX *nu* are camera implicit - trebuie adăugată manual.

1. În *Scene Hierarchy*, dă click dreapta pe `/PioneerP3DX` și alege
   **Add → Vision sensor → Perspective type**.
2. Va apărea un obiect numit `/Vision_sensor`. Mută-l ca **child** al lui
   `/PioneerP3DX` (drag & drop în Scene Hierarchy).
3. Redenumește-l în `visionSensor` (click dreapta → *Rename*).
4. Cu el selectat, deschide **Object Common Properties** și verifică
   "*Visible*" și "*Renderable*".
5. Deschide **Vision Sensor Properties** și setează:
   - Near clipping plane: **0.02 m**
   - Far clipping plane: **5.0 m**
   - View angle / orthographic size: **60°** (perspectivă largă, similar GoPro)
   - Resolution X / Y: **512 / 384** (raport 4:3, suficient pentru detector)
6. Plasează senzorul **în fața robotului, la înălțime mijloc**:
   - Position: `x = 0.20, y = 0.0, z = 0.20` *relativ la PioneerP3DX*.
   - Orientation: `alpha = -90°, beta = 0°, gamma = -90°` (sau ajustat astfel
     încât săgeata roșie locală să indice înainte pe robot).
7. Verifică în panoul *Camera View* că senzorul vede înaintea robotului.

> **Notă:** Codul așteaptă calea `/PioneerP3DX/visionSensor`. Dacă alegi alt
> nume, schimbă parametrul `vision_path` la inițializarea
> `CoppeliaSimDriver` (sau din GUI - vezi sursa în
> `src/robot/simulator.py`).

---

## 2. Generarea texturilor pentru semne și semafoare

Aplicația Tkinter conține un buton **"Genereaza texturi semne"** care apelează
`src/robot/sign_generator.py` și produce 12 fișiere PNG (512x512) în
directorul `data/signs/`:

```
stop.png, yield.png, no_entry.png,
speed_limit_30.png, speed_limit_50.png, speed_limit_80.png,
mandatory_forward.png, mandatory_left.png, mandatory_right.png,
traffic_light_red.png, traffic_light_yellow.png, traffic_light_green.png
```

Le poți regenera și manual:

```bash
python -m src.robot.sign_generator
```

---

## 3. Adăugarea unui semn în scenă (procedeu repetabil)

Pentru fiecare semn pe care vrei să-l plasezi în arenă:

1. **Add → Primitive shape → Cuboid** cu dimensiuni:
   - X = 0.50 m, Y = 0.02 m, Z = 0.50 m (placa subțire, vertical)
2. **Object Common Properties** → debifează *Respondable* și *Dynamic*; lasă
   *Renderable* și *Detectable* activate (ca să poată fi văzut de camera și să
   nu interfereze cu fizica).
3. **Apply texture**: cu cuboidul selectat, deschide
   **Object Common Properties → Adjust texture...**, click *Load texture* și
   selectează PNG-ul dorit din `data/signs/`.
4. Setează *Texture coordinates → mode = Plane (X+Y)* (sau cube depending on
   orientation) și ajustează *Size U / V* la 0.5 / 0.5.
5. Mută placa în arenă pe **lateralul drumului** robotului, cu fața normalei
   către traseul pe care se va deplasa Pioneer-ul. Înălțime recomandată:
   centrul plăcii la `z = 0.30 m` (la nivelul camerei robotului).

**Sfaturi de plasare:**
- Pune semnele la cel puțin 1 m distanță una de alta pe lateralul drumului.
- Asigură-te că placa este **paralelă cu drumul**, nu perpendiculară.
- Iluminarea ambientală implicită este suficientă - nu este nevoie de surse
  suplimentare.

---

## 4. Construirea unui semafor (3 lămpi)

Cea mai simplă variantă este o singură placă cu textura
`traffic_light_*.png`, dar pentru un efect mai realist poți construi un
semafor cu trei lămpi separate:

1. Adaugă un Cuboid orizontal mare (0.30 × 0.05 × 0.90) - corpul semaforului,
   colorat negru (*Object Color → diffuse = (0.1, 0.1, 0.1)*).
2. Adaugă trei sfere (sau discuri subțiri) cu diametru 0.18 m, montate
   pe față, una sub alta. Setează diffuse:
   - Top: roșu strălucitor `(1, 0.1, 0.1)` ON sau `(0.1, 0.04, 0.04)` OFF
   - Middle: galben `(1, 0.85, 0.2)` / `(0.1, 0.09, 0.05)`
   - Bottom: verde `(0.15, 0.85, 0.2)` / `(0.04, 0.1, 0.04)`
3. Pentru a face semaforul **dinamic** (alternează roșu/galben/verde),
   adaugă un *Threaded child script* pe corpul semaforului cu:

```lua
function sysCall_threadmain()
    local red    = sim.getObject('./light_red')
    local yellow = sim.getObject('./light_yellow')
    local green  = sim.getObject('./light_green')

    local off_red    = {0.1, 0.04, 0.04, 0, 0, 0, 0, 0, 0}
    local on_red     = {1.0, 0.1,  0.1,  0, 0, 0, 0, 0, 0}
    local off_yellow = {0.1, 0.09, 0.05, 0, 0, 0, 0, 0, 0}
    local on_yellow  = {1.0, 0.85, 0.2,  0, 0, 0, 0, 0, 0}
    local off_green  = {0.04, 0.1, 0.04, 0, 0, 0, 0, 0, 0}
    local on_green   = {0.15, 0.85, 0.2, 0, 0, 0, 0, 0, 0}

    while true do
        sim.setShapeColor(red,    nil, sim.colorcomponent_ambient_diffuse, on_red)
        sim.setShapeColor(yellow, nil, sim.colorcomponent_ambient_diffuse, off_yellow)
        sim.setShapeColor(green,  nil, sim.colorcomponent_ambient_diffuse, off_green)
        sim.wait(6.0)

        sim.setShapeColor(red,    nil, sim.colorcomponent_ambient_diffuse, off_red)
        sim.setShapeColor(yellow, nil, sim.colorcomponent_ambient_diffuse, on_yellow)
        sim.wait(2.0)

        sim.setShapeColor(yellow, nil, sim.colorcomponent_ambient_diffuse, off_yellow)
        sim.setShapeColor(green,  nil, sim.colorcomponent_ambient_diffuse, on_green)
        sim.wait(6.0)
    end
end
```

Asigură-te că lămpile sunt copii ai corpului semaforului și numite
`light_red`, `light_yellow`, `light_green`.

---

## 5. Recomandări pentru scenă (impact vizual la notare)

- **Arena**: un dreptunghi 8×8 m cu un drum desenat pe podea (Floor Pattern
  Editor sau pur și simplu o textură personalizată).
- **Obstacole**: 4-6 cuburi sau cilindri răspândiți, pentru a forța
  comportamentul Braitenberg să se activeze.
- **Trafic**: 6-10 semne distribuite pe traseu (un STOP, un YIELD, două
  speed limits, un semafor, două săgeți obligatorii).
- **Iluminare**: lasă lumina implicită; adaugă o sursă suplimentară doar
  dacă apare zgomot HSV.
- **Ferestre / structuri**: zero - reduc FPS-ul fără valoare adăugată.

Salvează scena ca `scene/lab_navigation.ttt` (sau direct peste
`pioneer_lab06.ttt`) și pornește simularea cu butonul ▶ înainte să apeși
"Conecteaza" în aplicația Tkinter.

---

## 6. Troubleshooting

| Simptom                                  | Cauză probabilă                                            | Rezolvare                                                                 |
| ---------------------------------------- | ---------------------------------------------------------- | ------------------------------------------------------------------------- |
| `ConnectionRefusedError` la conectare    | CoppeliaSim nu rulează sau ZMQ pe alt port                 | Pornește simulatorul; verifică portul 23000 în *Add-ons → ZMQ Remote API* |
| `Object not found: /PioneerP3DX`         | Numele robotului diferă în scenă                           | Redenumește robotul sau ajustează `robot_path` în GUI / cod               |
| Camera label rămâne "(camera offline)"   | `visionSensor` nu există sau e la altă cale                | Verifică ierarhia; rute alternative: `/PioneerP3DX/Vision_sensor`         |
| Detectorul nu prinde semafoarele         | Lămpile sunt prea închise în material                      | Mărește diffuse pe lampa "aprinsă" (RGB > 0.8)                            |
| Detector confundă STOP cu speed limit    | Textura semnului e mătuită / paletă greșită                | Regenerează texturile cu `python -m src.robot.sign_generator`             |
| Robotul nu se mișcă                      | Simularea nu a fost pornită cu ▶                           | Apasă Play înainte de "Start navigatie" în GUI                            |
