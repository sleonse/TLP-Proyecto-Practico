# En el siguiente ejecutador
import json
import random
import time
import msvcrt
import os

class Juego:
    def __init__(self, file_ast, game_name):
        self.rules = {}
        self.figures = {}
        self.file_ast = file_ast
        self.game_name = game_name

    #Cargar el AST - Este es el segundo paso
    def load_ast(self):
        self.status = 'Se ejecuto: cargar_ast'
        try:
            with open(self.file_ast, 'r', encoding= 'utf-8') as f:
                self.loaded_ast = json.load(f)
            
            for key, value in self.loaded_ast.items():
                if key.startswith("regla_"):
                    self.rules[key] = value
                elif key.startswith("figura_"):
                    self.figures[key] = value
            self.status = 'cargar_ast exitoso'
            print(f'ast cargado correctamente')
        except FileNotFoundError:
            print(f'error: archivo no encontrado')
        except Exception as e:
            print(f'error: {e}')



        print(f"\nResumen del Juego {self.game_name}")
        print(f"Numero de reglas cargadas: {len(list(self.rules.keys()))}")
        print(f"Numero de figuras cargadas: {len(list(self.figures.keys()))}")

    # esto depsues de cargar_ast
    def starter(self):
        self.ancho = self.rules.get('regla_general', {}).get('tablero_ancho')
        self.largo = self.rules.get('regla_general', {}).get('tablero_largo')
        self.tabla_puntuacion_largo = self.largo
        self.tabla_puntuacion_ancho = 3
        self.grid = [[0 for i in range(self.ancho)] for i in range(self.largo)]
        self.status = 'grid creado'
        self.juego_terminado = False
        # separacion por juegos
        if self.game_name == 'tetris':
            self.aparecion_aleatoria = self.rules.get('regla_aparicion_fichas', {}).get('aparicion_aleatoria')
            self.pieza_actual = None
            self.rotacion_actual = 0
            self.velocidad_gravedad = self.rules.get('regla_niveles_velocidad').get('velocidad_inicial')
            self.evento_finalizar_juego = self.rules.get('regla_fin_juego').get('evento')
            self.fichas_disponibles = list(self.figures.keys())
            self.game_puntuacion = 0
        elif self.game_name == 'snake':
            # Configuración específica de Snake
            serpiente_config = self.figures.get('figura_serpiente', {})
            self.longitud_inicial = serpiente_config.get('longitud', 4)
            self.velocidad = self.rules.get('regla_velocidad', {}).get('velocidad', 0.5)
            self.game_puntuacion = 0

            centro_x = self.ancho // 2
            centro_y = self.largo // 2
            self.serpiente = []
            for i in range(self.longitud_inicial):
                self.serpiente.append([centro_y, centro_x - i])
            
            self.direccion = [0, 1] 
            self.direccion_pendiente = None  
            
            # Colocar manzana
            self.manzana = None
            self.generar_manzana()


### solo tetris
    def random_piece_tetris(self):
        return  random.choice(self.fichas_disponibles)

        # hasta aqui voy melo
    def cargar_controles_tetris(self):
        controls = self.rules.get('regla_controles')
        self.control_izquierda = controls.get('izquierda')
        self.control_derecha = controls.get('derecha')
        self.control_rotar = controls.get('rotar')
        self.control_acelerar_caida = controls.get('acelerar_caida')
        self.control_terminar = controls.get('terminar')
        return self.control_izquierda, self.control_derecha, self.control_rotar, self.control_acelerar_caida
    
    def cargar_pieza(self):
        self.ficha_actual = self.random_piece_tetris()
        self.ficha_actual_settings = self.figures.get(self.ficha_actual)
        self.ficha_actual_color = self.ficha_actual_settings.get('color')
        self.ficha_actual_rotaciones = {}
        for i in [0, 90, 180, 270]:
            key = f'rotacion{i}'
            self.ficha_actual_rotaciones[i] = self.ficha_actual_settings[key]
        self.rotacion_actual = 0
        return 
    

    def colocar_pieza(self):
        self.matriz_pieza_actual = self.ficha_actual_rotaciones[self.rotacion_actual]

        self.alto_pieza_actual, self.ancho_pieza_actual = len(self.matriz_pieza_actual), len(self.matriz_pieza_actual[0])
        
        self.pieza_actual_posx, self.pieza_actual_posy = (self.ancho - self.ancho_pieza_actual) // 2, 0

    def colision(self):


        for y in range(self.alto_pieza_actual):
            for x in range(self.ancho_pieza_actual):
                if self.matriz_pieza_actual[y][x] == 1:
                    real_y = self.pieza_actual_posy + y
                    real_x = self.pieza_actual_posx + x
                    
                    if not (0 <= real_x < self.ancho):
                        return True 
                    
                    if real_y >= self.largo:
                        return True 
                    
                    if real_y >= 0 and self.grid[real_y][real_x] == 1:
                        return True
        return False

    def limpiar_pieza_actual(self):
        for y in range(self.alto_pieza_actual):
            for x in range(self.ancho_pieza_actual):
                if self.matriz_pieza_actual[y][x] == 1:
                    real_y = self.pieza_actual_posy + y
                    real_x = self.pieza_actual_posx + x
                    if 0 <= real_y < self.largo and 0 <= real_x < self.ancho:
                        self.grid[real_y][real_x] = 0



    def nueva_posicion(self):
        for y in range(self.alto_pieza_actual):
            for x in range(self.ancho_pieza_actual):
                if self.matriz_pieza_actual[y][x] == 1:
                    real_y = self.pieza_actual_posy + y
                    real_x = self.pieza_actual_posx + x
                    if 0 <= real_y < self.largo and 0 <= real_x < self.ancho:
                        self.grid[real_y][real_x] = 1


    def gravedad(self):
        self.limpiar_pieza_actual()
        self.pieza_actual_posy += 1
        if self.colision():
            self.pieza_actual_posy -= 1
            self.nueva_posicion()
            self.fijar_pieza()
        else:
            self.nueva_posicion()

    def fijar_pieza(self):
        self.eliminar_filas()
        self.cargar_pieza()
        self.colocar_pieza()  
            

        if self.colision():
            self.juego_terminado = True
            print("¡JUEGO TERMINADO!")
                
        self.nueva_posicion() 

        return


    


    def imprimir_tablero(self):
        """Imprime el tablero de Tetris"""
        print("+" + "-" * self.ancho + "+")
        
        for y in range(self.largo):
            linea_str = "|" 
            for x in range(self.ancho):
                if self.grid[y][x] == 1:
                    linea_str += "█"
                else:
                    linea_str += " "
            linea_str += "|"
            print(linea_str)
        
        print("+" + "-" * self.ancho + "+")

    def eliminar_filas(self):
        filas_completadas = []
        for i in range(self.largo):
            count = 0
            if all(cell == 1 for cell in self.grid[i]):
                filas_completadas.append(i)
        
        if len(filas_completadas) == 1:
            self.game_puntuacion += int(self.rules.get('regla_puntuacion').get('puntuacion_linea'))
        elif len(filas_completadas) == 2:
            self.game_puntuacion += int(self.rules.get('regla_puntuacion').get('puntuacion_dos_lineas'))        
        elif len(filas_completadas) == 3:
            self.game_puntuacion += int(self.rules.get('regla_puntuacion').get('puntuacion_tres_lineas'))
        elif len(filas_completadas) == 4:
            self.game_puntuacion += int(self.rules.get('regla_puntuacion').get('puntuacion_cuatro_lineas'))

        for index in filas_completadas:

            del self.grid[index]

            self.grid.insert(0, [0] * self.ancho)
            
    def mover_derecha(self):
        self.limpiar_pieza_actual()
        self.pieza_actual_posx += 1
        if self.colision():
            self.pieza_actual_posx -= 1
        self.nueva_posicion()

    def mover_izquierda(self):
        self.limpiar_pieza_actual()
        self.pieza_actual_posx -= 1
        if self.colision():
            self.pieza_actual_posx += 1
        self.nueva_posicion()

    def rotar_pieza(self):
        self.limpiar_pieza_actual()
        rotacion_anterior = self.rotacion_actual
        self.rotacion_actual = (self.rotacion_actual + 90) % 360
        self.matriz_pieza_actual = self.ficha_actual_rotaciones[self.rotacion_actual]
        self.alto_pieza_actual, self.ancho_pieza_actual = len(self.matriz_pieza_actual), len(self.matriz_pieza_actual[0])
        if self.colision():
            self.rotacion_actual = rotacion_anterior
            self.matriz_pieza_actual = self.ficha_actual_rotaciones[self.rotacion_actual]
            self.alto_pieza_actual, self.ancho_pieza_actual = len(self.matriz_pieza_actual), len(self.matriz_pieza_actual[0])
        self.nueva_posicion()






    def run_game_tetris(self):
            self.load_ast()
            self.starter()
            self.cargar_controles_tetris()
            self.cargar_pieza()
            self.colocar_pieza()
            self.nueva_posicion()

            ultimo_tiempo_gravedad = time.time()
            
    
            while not self.juego_terminado:
                
                if msvcrt.kbhit():
                    key_bytes = msvcrt.getch()
                    key = key_bytes.decode('utf-8', errors='ignore') 
                    

                    if key == self.control_izquierda:
                        self.mover_izquierda()
                    elif key == self.control_derecha:
                        self.mover_derecha()
                    elif key == self.control_rotar:
                        self.rotar_pieza()
                    elif key == self.control_acelerar_caida:

                        self.gravedad() 
                        ultimo_tiempo_gravedad = time.time()
                    elif key == 'q':
                        self.juego_terminado = True


                tiempo_actual = time.time()
                if tiempo_actual - ultimo_tiempo_gravedad > self.velocidad_gravedad:
                    self.gravedad()
                    ultimo_tiempo_gravedad = tiempo_actual


                os.system('cls' if os.name == 'nt' else 'clear')
                self.imprimir_tablero()
                print("\nJuego terminado")
                print(f"Puntuacion: {self.game_puntuacion}")


                time.sleep(0.01)


    ### Hasta aqui tetris
    def cargar_controles_snake(self):
        controls = self.rules.get('regla_controles')
        self.control_arriba = controls.get('rotar')
        self.control_abajo = controls.get('acelerar_caida')
        self.control_izquierda = controls.get('izquierda')
        self.control_derecha = controls.get('derecha') 
        self.control_terminar = controls.get('terminar')
        return self.control_arriba, self.control_abajo, self.control_izquierda, self.control_derecha

    def generar_manzana(self):

        posiciones_vacias = []
        for y in range(self.largo):
            for x in range(self.ancho):
                if [y, x] not in self.serpiente:
                    posiciones_vacias.append([y, x])
        
        if posiciones_vacias:
            self.manzana = random.choice(posiciones_vacias)

    def cambiar_direccion_snake(self, nueva_direccion):

        if nueva_direccion[0] == -self.direccion[0] and nueva_direccion[1] == -self.direccion[1]:
            return
        self.direccion_pendiente = nueva_direccion

    def mover_serpiente(self):
        """Mueve la serpiente en la dirección actual"""

        if self.direccion_pendiente:
            self.direccion = self.direccion_pendiente
            self.direccion_pendiente = None
        

        cabeza = self.serpiente[0]
        nueva_cabeza = [cabeza[0] + self.direccion[0], cabeza[1] + self.direccion[1]]
        

        if (nueva_cabeza[0] < 0 or nueva_cabeza[0] >= self.largo or
            nueva_cabeza[1] < 0 or nueva_cabeza[1] >= self.ancho):
            self.juego_terminado = True
            return
        

        if nueva_cabeza in self.serpiente:
            self.juego_terminado = True
            return
        

        self.serpiente.insert(0, nueva_cabeza)
        

        if nueva_cabeza == self.manzana:

            regla_puntuacion = self.rules.get('regla_puntuacion', {})
            self.game_puntuacion += regla_puntuacion.get('aumento_puntuacion', 1)

            self.generar_manzana()
        else:

            self.serpiente.pop()

    def imprimir_tablero_snake(self):
        """Imprime el tablero de Snake"""
        print("+" + "-" * self.ancho + "+")
        
        for y in range(self.largo):
            linea_str = "|"
            for x in range(self.ancho):
                if [y, x] == self.serpiente[0]:
                    linea_str += "O"
                elif [y, x] in self.serpiente:
                    linea_str += "o"
                elif self.manzana and [y, x] == self.manzana:
                    linea_str += "X" 
                else:
                    linea_str += " "
            linea_str += "|"
            print(linea_str)
        
        print("+" + "-" * self.ancho + "+")
        print(f"PUNTUACIÓN: {self.game_puntuacion}")

    def run_game_snake(self):
        self.load_ast()
        self.starter()
        self.cargar_controles_snake()

        ultimo_tiempo_movimiento = time.time()
        
        while not self.juego_terminado:
            
            if msvcrt.kbhit():
                key_bytes = msvcrt.getch()
                key = key_bytes.decode('utf-8', errors='ignore')
                
                if key == self.control_arriba:
                    self.cambiar_direccion_snake([-1, 0])
                elif key == self.control_abajo:
                    self.cambiar_direccion_snake([1, 0])
                elif key == self.control_izquierda:
                    self.cambiar_direccion_snake([0, -1])
                elif key == self.control_derecha:
                    self.cambiar_direccion_snake([0, 1])
                elif key == 'q':
                    self.juego_terminado = True

            tiempo_actual = time.time()
            if tiempo_actual - ultimo_tiempo_movimiento > self.velocidad:
                self.mover_serpiente()
                ultimo_tiempo_movimiento = tiempo_actual

            os.system('cls' if os.name == 'nt' else 'clear')
            self.imprimir_tablero_snake()
            time.sleep(0.01)

        print("\nJuego terminado")
        print(f"Puntuacion: {self.game_puntuacion}")




## EJECUTADOR
x = ""
while x != 1 and x !=2:
    print("\ningrese 1 para tetris o 2 para snake.")
    x = int(input())
    if x == 1 or x == 2:
        break
if x == 1:
    base_dir = os.path.dirname(os.path.abspath(__file__))


    ruta_ast = os.path.join(base_dir, "arbol_tetris.ast")

    try:
        juego_tetris = Juego(ruta_ast, "tetris")
        juego_tetris.run_game_tetris()

    except Exception as e:
        print(e)

if x == 2:
    base_dir = os.path.dirname(os.path.abspath(__file__))


    ruta_ast = os.path.join(base_dir, "arbol_snake.ast")

    try:
        juego_snake = Juego(ruta_ast, "snake")
        juego_snake.run_game_snake()
    except Exception as e:
        print(e)



input()
print("Juego terminado")
print("Presione enter para salir")

# Terminado
