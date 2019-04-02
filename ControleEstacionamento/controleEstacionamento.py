# -*- coding: utf-8 -*-

import yaml
import numpy as np
import cv2


video = "datasets/video.mp4"
database = "datasets/coordenadas.yml"

cap = cv2.VideoCapture(video)
# Faz o video começar no frame 940
cap.set(cv2.CAP_PROP_POS_FRAMES, 940)
# Ler arquivo Yml
with open(database, 'r') as stream:
    dados_estacionamento = yaml.safe_load(stream)
    # Cria uma array para armazenar os contornos
    contornos_estacionamento = []
     # Cria uma array para armazenar a area do estacionamento
    area_estacionamento = []
  
    # Caso os dados retornados na variavel estacionamento esteja dentro das coordenadas de dados do estacionamento
    for estacionamento in dados_estacionamento:
        coordenadas = np.array(estacionamento['coordenadas'])
        
        # Desenha um retângulo aproximado
        retangulo = cv2.boundingRect(coordenadas)
        # Salva dentro da variavel coordenadas_alteradas as coordenadas especificadas que estão dentro o arquivo "estacionamento4.yml"
        coordenadas_alteradas = coordenadas.copy()
        # Pega todos os valores da coluna 0 e todas as linhas dessa coluna das coordenadas que estão no arquivo "estacionamento4.yml" e dimininui pelos valores gerados no retangulo na coluna 0        
        # [:,0] : Significa pega todos os valores da coluna zero (de todas as linhas)
        coluna0 = coordenadas[:,0] - retangulo[0] 

        # Pega todos os valores da coluna 1 e todas as linhas dessa coluna das coordenadas que estão no arquivo "estacionamento4.yml" e dimininui pelos valores gerados no retangulo na coluna 1        
        # [:,1] : Significa pega todos os valores da coluna 1 (de todas as linhas)        
        coluna1 = coordenadas[:,1] - retangulo[1]
        
        # Aparece os valores das coordenadas
        contornos_estacionamento.append(coordenadas)
        # Aparece os valores dos retangulos
        area_estacionamento.append(retangulo)


status_estacionamento= [False]*len(dados_estacionamento)
novos_dados = [None]*len(dados_estacionamento)

while(cap.isOpened()):   
    # Inicialização das variaveis de vagas livres e vagas ocupadas
    vagas_livres = 0
    vagas_ocupadas = 0 
    
    # Lê frame por frame    
    # Posição atual do arquivo de vídeo em milisegundos
    video_posicao_atual = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0 
    # Índice do quadro a ser capturado
    # video_cap_frame = cap.get(cv2.CAP_PROP_POS_FRAMES) 
    # Ler o vídeo 
    ret, frame = cap.read()    
    
    # Se ocorrer algum problema na exibição do video vai imprimir "Erro ao capturar o video"
    if ret == False:
        print("Erro ao capturar o video!")
        break
    # cv2.imwrite("estacionamento3.jpg", frame)
    
    # Tratamento da imagem
    desfoque = cv2.GaussianBlur(frame.copy(), (5,5), 3)
    cinza = cv2.cvtColor(desfoque, cv2.COLOR_BGR2GRAY)
    saida = frame.copy()

    # vai enumerar os dados que estão dentro da variavel "dados_estacionamento"
    for dados, estacionamento in enumerate(dados_estacionamento):
        
        # Salva os dados das coordenadas dentro da varialvel coordenadas
        coordenadas = np.array(estacionamento['coordenadas'])
        # Retangulo recebe uma array de dados referente a área do estacionamento
        retangulo = area_estacionamento[dados]
        roi_gray = cinza[retangulo[1]:(retangulo[1]+retangulo[3]), retangulo[0]:(retangulo[0]+retangulo[2])] # crop roi for faster calculation   
       
        # Pega todos os valores da coluna 0 e todas as linhas dessa coluna das coordenadas que estão no arquivo "estacionamento4.yml" e dimininui pelos valores gerados no retangulo na coluna 0        
        # [:,0] : Significa que pega todos os valores da coluna zero (de todas as linhas)
        coordenadas_coluna0 = coordenadas[:,0] - retangulo[0] 

        # Pega todos os valores da coluna 1 e todas as linhas dessa coluna das coordenadas que estão no arquivo "estacionamento4.yml" e dimininui pelos valores gerados no retangulo na coluna 1        
        # [:,1] : Significa pega todos os valores da coluna 1 (de todas as linhas)        
        coordenadas_coluna1 = coordenadas[:,1] - retangulo[1]
        # np.std = Calcula o desvio padrão aritmetico da array informada que nesse caso é a array da variavel "roi_gray"
        # np.mean = Calcula a media aritmetica da array "roi_gray"
        # após isso a variavel status recebe o valor do np.std da variavel roi_gray menor que 22 e o valor do np.mean maior que 53 
        status = np.std(roi_gray) < 22 and np.mean(roi_gray) > 53
        

        # Se detectou uma mudança no status de estacionamento, salve a hora atual
        # se o valor recebido da variavel status for diferente dos dados salvos na "status_estacionamento" e "novo_dados" for none
        if status != status_estacionamento[dados] and novos_dados[dados]==None:
                # novos_dados vai receber a posição atual do video
                novos_dados[dados] = video_posicao_atual
              
            
        # Se o status for diferente daquele que foi salvo e os novos_dados for diferente de None
        elif status != status_estacionamento[dados] and novos_dados[dados]!=None:

        # Essa condição faz com que se o carro passar rapido pela vaga o valor dela não altera
        # Com essa condição é possivel fazer com que o vaga só altere depois que o carro realmente estacionar na vaga
            if video_posicao_atual - novos_dados[dados] > 3:
        
                status_estacionamento[dados] = status
                novos_dados[dados] = None
            
            
        # Se o status for o mesmo que foi salvo no status_estacionamento[dados] e os novos_dados for diferente de None                   
        elif status == status_estacionamento[dados] and novos_dados[dados]!=None:
            novos_dados[dados] = None                    
   
   #condição para colocar as cores de ocupado e livre                        
    for dados, estacionamento in enumerate(dados_estacionamento):
        coordenadas = np.array(estacionamento['coordenadas'])
        # se status do estacionamento[dados] = true, quer dizer que está livre 
        if status_estacionamento[dados]: 
            # coloca na variavel color o cor verde
            color = (0,255,0)
            # coloca o total das vagas livres
            vagas_livres = vagas_livres+1
        else:
            # coloca na variavel color o cor vermelha
            color = (0,0,255)
            # coloca o total das vagas ocupadas
            vagas_ocupadas = vagas_ocupadas+1
        # desenha os contornos na telas das vagas livres e ocupadas
        cv2.drawContours(saida, [coordenadas], contourIdx=-1,
                        color=color, thickness=2, lineType=cv2.LINE_8)            
    
    texto = "Vagas Livres: {} | Vagas Ocupadas: {}" .format(vagas_livres, vagas_ocupadas)
    cv2.putText(saida, texto, (19,26), cv2.FONT_HERSHEY_COMPLEX,
                        0.7, (255,0,0), 2, cv2.LINE_AA)
            
    
    # Visualizando frame
    cv2.imshow('Detecção de Vagas de Estacionamento', saida)
    # Delay para o video não correr rápido demais
    cv2.waitKey(40)
    if cv2.waitKey(1) == 13:
        break
cap.release()
cv2.destroyAllWindows()    
