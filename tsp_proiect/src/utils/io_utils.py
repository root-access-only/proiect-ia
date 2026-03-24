import random
import os


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
    if not os.path.exists(cale_fisier):
        raise FileNotFoundError(f"Fisierul '{cale_fisier}' nu a fost gasit.")

    try:
        with open(cale_fisier, 'r') as f:
            linii = [linie.strip() for linie in f if linie.strip()]

        if not linii:
            raise ValueError("Fisierul este gol.")

        n = int(linii[0])

        if n < 2:
            raise ValueError("Numarul de orase trebuie sa fie cel putin 2.")

        if len(linii) < n + 1:
            raise ValueError(f"Fisierul trebuie sa contina {n + 1} linii (1 pentru N si {n} pentru matrice).")

        matrice = []
        for i in range(n):
            rand = [int(x) for x in linii[i + 1].split()]

            if len(rand) != n:
                raise ValueError(f"Randul {i} contine {len(rand)} elemente, dar s-au asteptat {n}.")

            matrice.append(rand)

        return n, matrice

    except ValueError as e:
        raise ValueError(f"Eroare la citirea fisierului: {e}")


def genereaza_matrice_aleatorie(n, min_dist=1, max_dist=100, seed=None):
    """Genereaza o matrice de distante NxN simetrica cu valori aleatoare.

    Args:
        n: Dimensiunea matricei (numarul de orase) (int).
        min_dist: Distanta minima (implicit 1) (int).
        max_dist: Distanta maxima (implicit 100) (int).
        seed: Seed pentru generatorul aleatoriu; daca None, nu se seteaza (int sau None).

    Returns:
        Matrice NxN simetrica (lista de liste de intregi).
    """
    if n < 2:
        raise ValueError("Numarul de orase trebuie sa fie cel putin 2.")

    if seed is not None:
        random.seed(seed)

    matrice = [[0] * n for _ in range(n)]

    for i in range(n):
        for j in range(i + 1, n):
            dist = random.randint(min_dist, max_dist)
            matrice[i][j] = dist
            matrice[j][i] = dist

    return matrice


def salveaza_matrice(cale_fisier, matrice):
    """Salveaza matricea de distante intr-un fisier text.

    Args:
        cale_fisier: Calea catre fisierul de iesire (str).
        matrice: Matricea NxN (lista de liste).

    Raises:
        ValueError: Daca matricea nu este patrata.
        IOError: Daca nu se poate scrie in fisier.
    """
    if not matrice:
        raise ValueError("Matricea nu poate fi goala.")

    n = len(matrice)

    for i, rand in enumerate(matrice):
        if len(rand) != n:
            raise ValueError(f"Matricea nu este patrata: randul {i} contine {len(rand)} elemente, asteptate {n}.")

    try:
        with open(cale_fisier, 'w') as f:
            f.write(f"{n}\n")
            for rand in matrice:
                f.write(" ".join(str(val) for val in rand) + "\n")
    except IOError as e:
        raise IOError(f"Eroare la scrierea in fisierul '{cale_fisier}': {e}")


def genereaza_si_salveaza_tsp(n, cale_fisier=None, min_dist=1, max_dist=100, seed=None):
    """Genereaza o matrice TSP aleatoare si o salveaza intr-un fisier.

    Aceasta este o functie de convenience care combina genereaza_matrice_aleatorie
    si salveaza_matrice.

    Args:
        n: Numarul de orase (int).
        cale_fisier: Calea catre fisierul de iesire; daca None, se genereaza din N (str sau None).
        min_dist: Distanta minima (implicit 1) (int).
        max_dist: Distanta maxima (implicit 100) (int).
        seed: Seed pentru reproducibilitate (int sau None).

    Returns:
        Tuplu (n, matrice) si salveaza in fisier.
    """
    if cale_fisier is None:
        cale_fisier = f"tsp_{n}.txt"

    matrice = genereaza_matrice_aleatorie(n, min_dist, max_dist, seed)
    salveaza_matrice(cale_fisier, matrice)

    return n, matrice


def afisare_matrice(matrice, titlu="Matricea de distante"):
    """Afiseaza matricea intr-un format lizibil.

    Args:
        matrice: Matricea NxN (lista de liste).
        titlu: Titlul de afisare (str).
    """
    n = len(matrice)
    print(f"\n{titlu}:")
    print("  ", end="")
    for j in range(n):
        print(f"{j:4d}", end=" ")
    print()

    for i, rand in enumerate(matrice):
        print(f"{i} ", end="")
        for val in rand:
            print(f"{val:4d}", end=" ")
        print()
    print()


def creare_interactiva():
    """Interfata interactiva pentru generarea unei matrice TSP si salvarea in fisier.

    Utilizator-friendly wrapper pentru genereaza_si_salveaza_tsp.
    """
    print("=== Generator TSP Interactiv ===\n")

    # Citeste dimensiunea
    while True:
        try:
            n = int(input("Introduceti numarul de orase: ").strip())
            if n < 2:
                print("Numarul de orase trebuie sa fie cel putin 2.")
                continue
            break
        except ValueError:
            print("Introduceti un numar intreg valid.")

    # Citeste calea fisierului (optional)
    cale_fisier = input("Introduceti calea fisierului de iesire (nu obligatoriu): ").strip()
    if not cale_fisier:
        cale_fisier = f"tsp_{n}.txt"
    if not cale_fisier.endswith(".txt"):
        cale_fisier += ".txt"

    # Citeste min si max distante
    try:
        min_dist = int(input("Introduceti distanta minima (implicit 1): ").strip() or "1")
        max_dist = int(input("Introduceti distanta maxima (implicit 100): ").strip() or "100")

        if min_dist < 0 or max_dist < min_dist:
            print("Distantele trebuie sa fie valide (min >= 0, max >= min).")
            return

    except ValueError:
        print("Introduceti numere intregi valide.")
        return

    # Genereaza si salveaza
    try:
        genereaza_si_salveaza_tsp(n, cale_fisier, min_dist, max_dist)
        print(f"\nMatricea TSP de dimensiune {n}x{n} a fost salvata in '{cale_fisier}'.")

        # Optiune de afisare
        if input("Doriti sa vedeti matricea? (da/nu): ").strip().lower() in ['da', 'd', 'yes', 'y']:
            _, matrice = citeste_matrice(cale_fisier)
            afisare_matrice(matrice, "Matricea TSP generata")

    except (ValueError, IOError) as e:
        print(f"Eroare: {e}")


if __name__ == "__main__":
    criere_interactiva()