def generar_combinaciones_pin_a_otros(pines_utilizados):
    combinaciones = []
    cantidad = len(pines_utilizados)
    for i in range(cantidad):
        for j in range(i + 1, cantidad):
            combinaciones.append((pines_utilizados[i], pines_utilizados[j]))
    return combinaciones

pines = [1, 2, 3, 6, 7, 8, 12, 13, 14]
pares_a_medir = generar_combinaciones_pin_a_otros(pines)

for par in pares_a_medir:
    print(f"Medir pin {par[0]} contra pin {par[1]}")