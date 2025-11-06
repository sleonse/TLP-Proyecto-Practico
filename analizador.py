import json
import re
import os
class Tokenizer:
    # ... (El código de la clase Tokenizer no cambia) ...
    def __init__(self, source_code):
        self.source = source_code
        self.tokens = []

    def tokenize(self):
        lines = self.source.splitlines()
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            regex_tokens = re.findall(r'(\bregla\b)|(\bfigura\b)|"(\w*)"|(\d+\.?\d*)|(=)|(,)|(\[)|(\])|(\{)|(\})|(\w+)', line)
                                    #0          #1         #2     #3         #4   #5 #6   #7   #8  #9   #10
            for group in regex_tokens:
                if group[0]: # es regla
                    self.tokens.append(('REGLA', group[0]))
                elif group[1]: # es figura
                    self.tokens.append(('FIGURA', group[1]))
                elif group[2]:  # Es una cadena de texto
                    self.tokens.append(('STRING', group[2]))
                elif group[3]:  # Es un numero
                    if '.' in group[3]:
                        self.tokens.append(('NUMBER', float(group[3])))
                    else:
                        self.tokens.append(('NUMBER', int(group[3])))
                elif group[4]:  # para el igual
                    self.tokens.append(('ASSIGN', group[4]))
                elif group[5]:  # para el comma
                    self.tokens.append(('COMMA', group[5]))
                elif group[6]:  # para el corchete abrir
                    self.tokens.append(('LBRACKET', group[6]))
                elif group[7]:  # para el corchete cerrar
                    self.tokens.append(('RBRACKET', group[7]))
                elif group[8]:  # para el llave abierto
                    self.tokens.append(('LBRACE', group[8]))
                elif group[9]:  # para el llave cerrar
                    self.tokens.append(('RBRACE', group[9]))
                elif group[10]:  # Es un identificador
                    self.tokens.append(('IDENTIFIER', group[10]))
        
        return self.tokens

#Hasta aqui lexer

#empieza parser

class Parser:
    def __init__(self, tokens):     #clase iniciadora
        self.tokens = tokens        # lista con todos los tokens
        self.current_token_index = 0        # entero, es el indice del token actual empezando en 0
        self.symbol_table = {}      # diccionario,esta es la tabla de simbolos       


    def get_token(self):        #esta funcion devuelve el token y aumenta el indice
        if self.current_token_index < len(self.tokens):     # condicional que verifica que hayan tokens.
            token = self.tokens[self.current_token_index]       # devuelve el token actual en la variable token
            self.current_token_index += 1       # suma uno al indice del token (esto lo hace para poder analizar el siguiente token)
            return token        # si hay tokens, lo devuelve
        return None     # si no hay tokens, no devuelve nada


    def peek_token(self):       # esta funcion devuelve el token que sigue sin hacerle nada
        if self.current_token_index < len(self.tokens):     # verifica que todavia hayan tokens
            return self.tokens[self.current_token_index]
        return None
    

    def expect(self, expected_value, expected_type, error_context=""):      # esta funcion es la que verifica el proximo token esperado
                # esta funcion, trae el expect value, es el token esperado, al igual que su valor, str, int, lbrace.. etc
                # estos expected_value y expected_type son generados por el token anterior
        token = self.get_token()     # Trae el token a evaluar
        if token is None:       # si no hay token, significa que termino repentinamente, por lo que lanza un error
            raise SyntaxError(f"Error de sintaxis, se esperaba {expected_value}'{error_context} y el codigo termino")
        if token[0] != expected_type:    # el token es una dupla, en 0 es donde esta su tipo, lo compara con el expected que dejo el token anterior
            raise SyntaxError(f"Error de sintaxis: se esperaba {expected_type}{error_context}, se encontro tipo {token[0]}")        # si no es el tipo esperado: error
        if token[1] != expected_value:      
            raise SyntaxError(f"Error de sintaxis: se esperaba {expected_value}{error_context}, se encontro {token[1]}")        # si no es el valor esperado: error
        
        return token
    


    def parse(self):   #raiz del programa

        # empieza el bluce que lee 
        while self.current_token_index < len(self.tokens):

            if self.peek_token() is None:       # si no hay proximo token se rompe el bucle, y se acaba el codigo porque no hay mas q ver para adelante#
                break
            
            self.parse_statement()    # ni idea que es esa funcion, no la hemos definido#
        
        return self.symbol_table    # retorna la tabla de simbolos, 
        
    # a continuacion la funcion que hace todo

    def parse_statement(self):          #aqui construimos el diccionario
        
        token = self.peek_token() #mira como empieza la sentencia
        if token is None: return


        token_type, token_value = token         #token es una dupla
        final_key = None

        ##ruta A, empieza con regla o figura
        if token_type == 'REGLA' or token_type == 'FIGURA':        #Si empieza con regla o figura.
           
            keyword_token = self.get_token()            #consume regla o figura para seguir analizando

            key_token = self.get_token()        # esto consumiria, tipo de regla o figura, osea seria un identificador

            if key_token is None or key_token[0] != 'IDENTIFIER':       #aqui, se expresa que key_token que es lo que sigue despues de regla/figura, y tiene que ser un identificador

                raise SyntaxError(f"Error: se esperaba un indetificador despues de '{keyword_token[1]}") #si no es identificador, lanza error

            final_key = f"{keyword_token[1]}_{key_token[1]}"
        #ruta b empieza con un identificador
        elif token_type == 'IDENTIFIER':
            key_token = self.get_token() #consume ese identifier que se detecto
            final_key = key_token[1]

        else:
            raise SyntaxError(f"Error: Sentencia inesperada al inicio: {token_value}")
        
        #como se leyo algo que despues de el si o si debe ir un igual, entonces

        self.expect('=', expected_type='ASSIGN', error_context=f"en la asignacion de '{final_key}'")
        
        #Ahora lo que sigue despues de esto

        value = self.parse_value()  # esto maneja la sentencias despues de el =
        #en value se almacena lo que sigue despues del igual

        self.symbol_table[final_key] = value
        #guarda el valor en la tabla de simbolos


    def parse_value(self):
        #aqui es lo que seguiria despues de 
        token = self.peek_token() #toma la siguiente token
        if token is None:
            raise SyntaxError("Error de sintaxis: Se esperaba un valor despues de '='.")
            
        token_type, token_value = token

        #Aqui analizamos el proximo token desoues del =
        if token_type == 'STRING' or token_type == 'NUMBER':
            self.get_token()
            return token_value
            
        elif token_type == 'LBRACE': #recursivooo para cuando es un bloque osea con {}
            return self.parse_block()  # estas se definen mas adelante
            

        elif token_type == 'LBRACKET':
            return self.parse_list()  #estas se definen mas adelante
        
        elif token_type == 'IDENTIFIER':

            raise SyntaxError(f"Error de sintaxis: Valor inesperado '{token_value}'")

        raise SyntaxError(f"Error de sintaxis: valor inesperado '{token_value}', despues de asignacion")
    

    def parse_block(self): #este identifica los bloques {}

        self.expect('{', expected_type = 'LBRACE') 
        block_content = {} #hasta aqui voy
        #mientras que no se cierre el bloque

        while self.peek_token() and self.peek_token()[0] != 'RBRACE':
        
            key_token = self.get_token()
            #Obtiene el token

            if key_token is None or key_token[0] != 'IDENTIFIER':
                
                raise SyntaxError(f"Error de sintaxis en el bloque, se esperaba un identificador (clave), se encontro {key_token[1]}.")
            
            self.expect('=', expected_type='ASSIGN', error_context=f"en la clave '{key_token[1]}'")

            value = self.parse_value()

            block_content[key_token[1]] = value

            if self.peek_token() and self.peek_token()[0] == 'COMMA':
                self.expect(',', expected_type ='COMMA') # se traga la comma

        self.expect('}', expected_type='RBRACE')

        return block_content
    

    def parse_list(self): # para []

        # Primero el de apertura
        self.expect('[', expected_type='LBRACKET')
        list_content = []

        while self.peek_token() and self.peek_token()[0] != 'RBRACKET':

            value = self.parse_value()


            list_content.append(value)

            # para la conma
            if self.peek_token() and self.peek_token()[0] == 'COMMA':
                self.expect(',', expected_type= 'COMMA')


            elif self.peek_token() and self.peek_token()[0] != 'RBRACKET':
                raise SyntaxError(f"Error de sintaxis en la lista: se esperaba ',' o ']', se encontro {self.peek_token()[1]}")
            

        self.expect(']', expected_type='RBRACKET')


        return list_content




def load_file_content(filepath):
    """
    Carga el contenido de un archivo de texto.
    Maneja el error si el archivo no existe.
    """
    if not os.path.exists(filepath):
        print(f"Error: El archivo '{filepath}' no se encontro. Asegurate de que el archivo exista en la misma carpeta que el script.")
        return None
    
    with open(filepath, 'r', encoding='utf-8') as file:
        return file.read()

def save_ast_to_file(ast, filepath):
    """
    Guarda el AST en un archivo de texto en formato JSON.
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(ast, file, indent=4)
        print(f"AST guardado exitosamente en '{filepath}'")
    except Exception as e:
        print(f"Error al guardar el archivo: {e}")

current_script_dir = os.path.dirname(os.path.abspath(__file__))     #Devuelve la ruta del archivo actual


file_path_tetris = os.path.join(current_script_dir, "tetris.brik")      #lee la ruta de los 2 .brik, que deben estar en la misma carpeta del script
file_path_snake = os.path.join(current_script_dir, "snake.brik")

ast_file_path_tetris = os.path.join(current_script_dir, "arbol_tetris.ast")
ast_file_path_snake = os.path.join(current_script_dir, "arbol_snake.ast")

source_code_tetris = load_file_content(file_path_tetris)
source_code_snake = load_file_content(file_path_snake)

def main(source_code, ast_file_path):
    try:
        tokenizer = Tokenizer(source_code)
        tokens = tokenizer.tokenize() # Obtiene la lista de tokens

    except Exception as e:
        print(f" Error lexico (Tokenizador): {e}")
        return
    

    #despues el parser
    try:
        parser = Parser(tokens)

        symbol_table = parser.parse()

        print("Analisis exitoso")
        import pprint
        pprint.pprint(symbol_table)
        save_ast_to_file(symbol_table, ast_file_path)

    except SyntaxError as e:
        print("Error de sintaxis")
        print(f"El codigo no cumple con las reglas gramaticales: {e}")
    except Exception as e:
        print(f"Error inesperado durante el parsing: {e}")


 
if __name__ == "__main__":
    
        #tetris
    print("tetris:")
    main(source_code_tetris, ast_file_path_tetris)
        #snake  
    print("snake:")
    main(source_code_snake, ast_file_path_snake)
    input()


