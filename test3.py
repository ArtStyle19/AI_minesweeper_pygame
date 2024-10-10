import pygame
import random



# Generate a 10x10 board with mines and a safe area at the start
def generar_tablero(tamano=30, num_minas=240):
    tablero = [[0 for _ in range(tamano)] for _ in range(tamano)]
    
    # Define a safe area of 2x2 in the top-left corner
    zona_segura = [(i, j) for i in range(2) for j in range(2)]
    
    # Place mines ensuring a unique solution
    mina_posiciones = set()
    while len(mina_posiciones) < num_minas:
        x = random.randint(0, tamano - 1)
        y = random.randint(0, tamano - 1)
        
        # Ensure mines are not placed in the safe zone
        if (x, y) not in zona_segura:
            mina_posiciones.add((x, y))
    
    for mina in mina_posiciones:
        x, y = mina
        tablero[x][y] = -1  # -1 represents a mine

    # Calculate the numbers around the mines
    for i in range(tamano):
        for j in range(tamano):
            if tablero[i][j] == -1:
                continue
            tablero[i][j] = contar_minas(tablero, i, j)
    
    return tablero

def contar_minas(tablero, x, y):
    tamano = len(tablero)
    minas_cercanas = 0
    for i in range(max(0, x-1), min(tamano, x+2)):
        for j in range(max(0, y-1), min(tamano, y+2)):
            if tablero[i][j] == -1:
                minas_cercanas += 1
    return minas_cercanas

def obtener_adyacentes(x, y, tamano=30):
    adyacentes = []
    for i in range(max(0, x-1), min(tamano, x+2)):
        for j in range(max(0, y-1), min(tamano, y+2)):
            if (i, j) != (x, y):
                adyacentes.append((i, j))
    return adyacentes

# IA_Buscaminas class remains unchanged
class IA_Buscaminas:
    def __init__(self, tablero, pantalla,mines):
        self.mines= mines
        self.tablero = tablero
        self.pantalla = pantalla
        tamano = len(tablero)
        self.conocido = [[False for _ in range(tamano)] for _ in range(tamano)]
        self.kb = []
        self.minas_marcadas = []
        self.seguros = []
        self.tamano_celda = 30

    def descubrir_celda(self, x, y):
        if self.conocido[x][y]:
            return
        
        valor = self.tablero[x][y]
        self.conocido[x][y] = True
        
        if valor == -1:
            print(f"Inferencia: ({x}, {y}) es mina")
            self.minas_marcadas.append((x, y))
            self.kb.append(('mina', x, y))
        else:
            print(f"Descubierta celda segura en ({x}, {y}) con número {valor}")
            self.kb.append(('numero', x, y, valor))
            self.seguros.append((x, y))
            
            # If it's a 0, expand into limited adjacent cells
            if valor == 0:
                self.expandir_zona_segura_alrededor(x, y)

    def expandir_zona_segura_alrededor(self, x, y):
        cola = [(x, y)]
        visitado = set()
        while cola:
            cx, cy = cola.pop(0)
            if (cx, cy) in visitado:
                continue
            visitado.add((cx, cy))
            
            if not self.conocido[cx][cy]:
                self.descubrir_celda(cx, cy)
            
            self.inferir()
            if any(inf for inf in self.kb if inf[0] == 'numero' and not self.conocido[inf[1]][inf[2]]):
                print(f"Inferencia segura encontrada después de expandir zona alrededor de ({x}, {y})")
                return
            
            if self.tablero[cx][cy] == 0:
                for nx, ny in obtener_adyacentes(cx, cy, len(self.tablero)):
                    if (nx, ny) not in visitado and not self.conocido[nx][ny]:
                        cola.append((nx, ny))
            
            self.mostrar_tablero_visual()

    def inferir(self):
        cambios = True
        while cambios:
            cambios = False
            for tipo, x, y, *resto in self.kb:
                if tipo == 'numero':
                    valor = resto[0]
                    desconocidas = []
                    minas_cerca = 0
                    for i, j in obtener_adyacentes(x, y, len(self.tablero)):
                        if (i, j) in self.minas_marcadas:
                            minas_cerca += 1
                        elif not self.conocido[i][j]:
                            desconocidas.append((i, j))
                    
                    if valor == minas_cerca and desconocidas:
                        for dx, dy in desconocidas:
                            print(f"Inferencia: ({dx}, {dy}) es seguro")
                            self.descubrir_celda(dx, dy)
                            self.mostrar_tablero_visual()
                            cambios = True
                    elif len(desconocidas) + minas_cerca == valor and desconocidas:
                        for dx, dy in desconocidas:
                            if (dx, dy) not in self.minas_marcadas:
                                print(f"Inferencia: ({dx}, {dy}) es mina")
                                self.minas_marcadas.append((dx, dy))
                                self.kb.append(('mina', dx, dy))
                                self.mostrar_tablero_visual()
                                cambios = True

    def hacer_conjetura(self):
        celdas_no_conocidas = [(i, j) for i in range(len(self.tablero))
                               for j in range(len(self.tablero[i]))
                               if not self.conocido[i][j] and (i, j) not in self.minas_marcadas]
        if celdas_no_conocidas:
            x, y = random.choice(celdas_no_conocidas)
            print(f"Haciendo conjetura en la celda ({x}, {y})")
            self.descubrir_celda(x, y)
            self.expandir_zona_segura_alrededor(x, y)
            self.mostrar_tablero_visual()

    def resolver(self):
        print("Comenzando con una parte del tablero descubierta:")
        for i in range(2):
            for j in range(2):
                self.descubrir_celda(i, j)
                self.mostrar_tablero_visual()
        
        while len(self.minas_marcadas) < self.mines:
            self.manejar_eventos()
            antes = len(self.seguros)
            self.inferir()
            despues = len(self.seguros)
            if antes == despues:
                print("No hay más inferencias seguras que realizar. Se procede a hacer una conjetura.")
                self.hacer_conjetura()
        
        if self.juego_resuelto():
            print("¡Juego resuelto correctamente!")
        else:
            print("Juego terminado, pero aún quedan celdas sin descubrir.")
        self.mostrar_tablero_visual()

    def juego_resuelto(self):
        for i in range(len(self.tablero)):
            for j in range(len(self.tablero[i])):
                if self.tablero[i][j] != -1 and not self.conocido[i][j]:
                    return False
        return True

    def mostrar_tablero_visual(self):
        tamano = len(self.tablero)
        for i in range(tamano):
            for j in range(tamano):
                rect = pygame.Rect(j * self.tamano_celda, i * self.tamano_celda, self.tamano_celda, self.tamano_celda)
                if self.conocido[i][j]:
                    pygame.draw.rect(self.pantalla, (200, 200, 200), rect)
                    if self.tablero[i][j] == -1:
                        pygame.draw.rect(self.pantalla, (255, 255, 0), rect)  
                    elif self.tablero[i][j] > 0:
                        font = pygame.font.SysFont(None, 24)
                        num_text = font.render(str(self.tablero[i][j]), True, (0, 0, 0))
                        self.pantalla.blit(num_text, rect.center)
                else:
                    if (i, j) in self.minas_marcadas:
                        pygame.draw.rect(self.pantalla, (255, 255, 0), rect)  # Yellow for marked mines
                    else:
                        pygame.draw.rect(self.pantalla, (100, 100, 100), rect)
        pygame.display.flip()

    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()

# Initialize pygame
def inicializar_pygame(tamano_celda=30, tamano=30):
    pygame.init()
    pantalla = pygame.display.set_mode((tamano_celda * tamano, tamano_celda * tamano))
    pygame.display.set_caption("Buscaminas con IA")
    return pantalla

# Menu functions
def mostrar_menu(pantalla):
    fuente = pygame.font.SysFont(None, 48)
    menu_opciones = ["Facil", "Medio", "Dificil", "Instrucciones", "Salir"]
    seleccion = 0
    while True:
        pantalla.fill((0, 0, 0))
        for i, opcion in enumerate(menu_opciones):
            if i == seleccion:
                color = (255, 0, 0)  # Red for selected option
            else:
                color = (255, 255, 255)  # White for unselected option
            texto = fuente.render(opcion, True, color)
            pantalla.blit(texto, (pantalla.get_width() // 2 - texto.get_width() // 2, 100 + i * 60))
        
        pygame.display.flip()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_DOWN:
                    seleccion = (seleccion + 1) % len(menu_opciones)
                elif evento.key == pygame.K_UP:
                    seleccion = (seleccion - 1) % len(menu_opciones)
                elif evento.key == pygame.K_RETURN:
                    if seleccion == 0:  # Iniciar Juego

                        pantalla = pygame.display.set_mode((30*10, 30*10))
                        return generar_tablero(10, 30) , 30
                    elif seleccion == 1:  # Instrucciones
                        pantalla = pygame.display.set_mode((30*20, 30*20))
                        return generar_tablero(20, 120), 120
                    elif seleccion == 2:  # Instrucciones
                        pantalla = pygame.display.set_mode((30*30, 30*30))
                        return generar_tablero(30, 240), 240
                    elif seleccion == 3:  # Instrucciones
                        mostrar_instrucciones(pantalla)
                    elif seleccion == 4:  # Salir
                        pygame.quit()
                        exit()

def mostrar_instrucciones(pantalla):
    fuente = pygame.font.SysFont(None, 36)
    instrucciones = [
        "Instrucciones:",
        "1. Haz clic en una celda para descubrirla.",
        "2. Si descubres una mina, ¡perdiste!",
        "3. El número en una celda indica cuántas minas",
        "   hay en las celdas adyacentes.",
        "4. Usa las conjeturas para encontrar minas.",
        "Presiona Enter para volver al menú."
    ]
    
    while True:
        pantalla.fill((0, 0, 0))
        for i, linea in enumerate(instrucciones):
            texto = fuente.render(linea, True, (255, 255, 255))
            pantalla.blit(texto, (50, 50 + i * 30))
        
        pygame.display.flip()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    return



# Main Execution
pantalla = inicializar_pygame()
tablero = mostrar_menu(pantalla)
ia = IA_Buscaminas(tablero[0], pantalla,tablero[1])
ia.resolver()

pygame.time.wait(3000)
pygame.quit()
