def citeste_matrice(cale_fisier):
    with open(cale_fisier, 'r') as f:
        linii = [linie.strip() for linie in f if linie.strip()]
    n = int(linii[0])
    matrice = [[int(x) for x in linii[i + 1].split()] for i in range(n)]
    return n, matrice