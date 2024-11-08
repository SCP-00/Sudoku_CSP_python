import os
import itertools as it
from collections import deque

def leer_tablero(ruta_archivo):
    """Leer el archivo de texto y crear el diccionario del tablero."""
    tablero = {}
    with open(ruta_archivo, 'r') as archivo:
        lineas = archivo.readlines()
        if len(lineas) != 81:
            raise ValueError("El archivo debe contener exactamente 81 líneas.")
        filas = 'ABCDEFGHI'
        columnas = '123456789'
        for i, linea in enumerate(lineas):
            fila = filas[i // 9]
            columna = columnas[i % 9]
            casilla = fila + columna
            opciones = linea.strip()
            tablero[casilla] = set(opciones) if len(opciones) > 1 else {opciones}
    return tablero

def imprimir_tablero(tablero):
    """Imprimir el tablero de Sudoku."""
    filas = 'ABCDEFGHI'
    columnas = '123456789'
    for fila in filas:
        for columna in columnas:
            casilla = fila + columna
            print(''.join(tablero[casilla]) if len(tablero[casilla]) == 1 else '.', end=' ')
        print()

def unico_desnudo(tablero, constraints):
    """Aplicar la técnica de únicos desnudos."""
    for const in constraints:
        for KeyVar in const:
            if len(tablero[KeyVar]) == 1:
                for KeyXDelete in const:
                    if KeyXDelete != KeyVar:
                        tablero[KeyXDelete].discard(next(iter(tablero[KeyVar])))

def unico_oculto(tablero, constraints):
    """Aplicar la técnica de únicos ocultos."""
    for const in constraints:
        for digit in '123456789':
            count = 0
            last_key = None
            for KeyVar in const:
                if digit in tablero[KeyVar]:
                    count += 1
                    last_key = KeyVar
            if count == 1:
                tablero[last_key] = {digit}

def ac3(tablero, constraints):
    """Implementar el algoritmo AC3 para reducir los dominios."""
    queue = deque([(Xi, Xj) for const in constraints for Xi in const for Xj in const if Xi != Xj])
    
    while queue:
        Xi, Xj = queue.popleft()
        if revisar_consistencia_arco(Xi, Xj, tablero):
            if len(tablero[Xi]) == 0:
                return False
            # Cambiamos el conjunto de listas a simplemente iterar sobre las restricciones
            for const in constraints:
                if Xi in const:
                    for Xk in const:
                        if Xk != Xi and Xk != Xj:
                            queue.append((Xk, Xi))
    return True

def revisar_consistencia_arco(Xi, Xj, tablero):
    """Revisar si se puede reducir el dominio de Xi eliminando valores inconsisentes con Xj."""
    eliminado = False
    for x in tablero[Xi].copy():
        if not any(x != y for y in tablero[Xj]):
            tablero[Xi].discard(x)
            eliminado = True
    return eliminado

def mrv(tablero):
    """Heurístico de MRV (mínimos valores restantes)."""
    return min((v for v in tablero if len(tablero[v]) > 1), key=lambda x: len(tablero[x]), default=None)

def degree_heuristic(tablero, constraints):
    """Heurística de grado: Selecciona la variable que participa in más restricciones."""
    return max((v for v in tablero if len(tablero[v]) > 1), key=lambda x: sum(1 for c in constraints if x in c), default=None)

def es_tablero_completo(tablero):
    """Verifica si el tablero está completo."""
    return all(len(tablero[var]) == 1 for var in tablero)

def buscar_solucion(tablero, constraints, verbose=False):
    """Buscar una solución al tablero de Sudoku utilizando backtracking y heurísticos."""
    if es_tablero_completo(tablero):
        return tablero
    
    var = mrv(tablero) or degree_heuristic(tablero, constraints)
    
    if not var:
        return None

    for valor in tablero[var].copy():
        tablero_copia = {v: tablero[v].copy() for v in tablero}
        tablero_copia[var] = {valor}

        if ac3(tablero_copia, constraints):
            if verbose:
                print(f"Asignando {valor} a la variable {var}")
            solucion = buscar_solucion(tablero_copia, constraints, verbose)
            if solucion:
                return solucion
    
    return None

def generar_restricciones():
    """Genera las restricciones del Sudoku."""
    filas = 'ABCDEFGHI'
    columnas = '123456789'
    
    def agrupar(cajas):
        return [tuple(caja) for caja in cajas]

    # Filas
    filas_grupo = agrupar([[fila + columna for columna in columnas] for fila in filas])
    # Columnas
    columnas_grupo = agrupar([[fila + columna for fila in filas] for columna in columnas])
    # Cajas 3x3
    cajas_grupo = agrupar([[fila + columna for fila in filas[i:i+3] for columna in columnas[j:j+3]] for i in range(0, 9, 3) for j in range(0, 9, 3)])
    
    return filas_grupo + columnas_grupo + cajas_grupo

def main():
    ruta_default = r'Board_impossible_SD9BJKIA.txt'
    ruta_archivo = input("Ingrese la ruta del archivo de Sudoku (o presione Enter para usar la ruta por defecto): ")
    if not ruta_archivo:
        ruta_archivo = ruta_default

    if not os.path.exists(ruta_archivo):
        print(f"El archivo {ruta_archivo} no existe.")
        return

    tablero = leer_tablero(ruta_archivo)
    constraints = generar_restricciones()
    
    print("Tablero inicial:")
    imprimir_tablero(tablero)
    
    solucion = buscar_solucion(tablero, constraints, verbose=True)
    
    if solucion:
        print("\n¡Solución encontrada!")
        imprimir_tablero(solucion)
    else:
        print("\nNo se encontró solución.")

if __name__ == "__main__":
    main()