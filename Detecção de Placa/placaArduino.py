# -*- coding: utf-8 -*-

import numpy as np
import cv2
from copy import deepcopy
from PIL import Image
import pytesseract as tess
import time
import serial

ser = serial.Serial('COM3', 9600, timeout=1)



def tratamentoImagem(frame):
    desfoque = cv2.GaussianBlur(frame, (3,3), 0)
    gray = cv2.cvtColor(desfoque, cv2.COLOR_BGR2GRAY)

    sobelx = cv2.Sobel(gray,cv2.CV_8U,1,0,ksize=1)
    binariza,threshold_img = cv2.threshold(sobelx,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    return threshold_img

def limpandoPlaca(plate):   
    gray = cv2.cvtColor(plate, cv2.COLOR_BGR2GRAY)
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (1, 1))
    thresh = cv2.dilate(gray, kernel, iterations = 1)
    # cv2.imshow("Placa detectada", thresh)
    # cv2.waitKey(1) == 27

    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(thresh.copy(),cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    if contours:
        areas = [cv2.contourArea(c) for c in contours]
        max_index = np.argmax(areas)

        max_cnt = contours[max_index]
        max_cntArea = areas[max_index]
        x,y,w,h = cv2.boundingRect(max_cnt)

        if not tamanhoPlaca(max_cntArea,w,h):
            return plate,None

        cleaned_final = thresh[y:y+h, x:x+w]
        return cleaned_final,[x,y,w,h]

    else:
        return plate, None

def extraindoContornos(threshold_img):
    element = cv2.getStructuringElement(shape=cv2.MORPH_RECT, ksize=(17, 3))
    morph_img_threshold = threshold_img.copy()
    cv2.morphologyEx(src=threshold_img, op=cv2.MORPH_CLOSE, kernel=element, dst=morph_img_threshold)

    contours, hierarchy= cv2.findContours(morph_img_threshold,mode=cv2.RETR_EXTERNAL,method=cv2.CHAIN_APPROX_NONE)
    return contours


def tamanhoPlaca(area, width, height):
    ratio = float(width) / float(height)
    if ratio < 1:
        ratio = 1 / ratio

    aspect = 4.7272
    min = 15 * aspect * 15  # area minima
    max = 125 *aspect * 125  # area maxima

    rmin = 3
    rmax = 6

    if (area < min or area > max) or (ratio < rmin or ratio > rmax):
        return False
    return True

def validateRotationAndRatio(rect):
    (x, y), (width, height), rect_angle = rect
    
    if(width>height):
        angulo = -rect_angle
    else:
        angulo = 90 + rect_angle

    if angulo>15:
        return False

    if height == 0 or width == 0:
        return False

    area = height*width
    if not tamanhoPlaca(area,width,height):
        return False
    else:
        return True
		
def identificandoPlaca(img,contornos):
    for i,cnt in enumerate(contornos):
        min_rect = cv2.minAreaRect(cnt)

        if validateRotationAndRatio(min_rect):

            x,y,w,h = cv2.boundingRect(cnt)
            plate_img = img[y:y+h,x:x+w]

            clean_plate, rect = limpandoPlaca(plate_img)
            
            if rect:
                x1,y1,w1,h1 = rect
                x,y,w,h = x+x1,y+y1,w1,h1
                #plate_im = Image.fromarray(clean_plate)
                cv2.imwrite("imagem/placa.jpg", clean_plate)                
                text = tess.image_to_string(clean_plate, lang='por', config= '--psm 10 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVXWYZ0123456789')
                char = removerChar(text)
                

                with open('placas.txt', 'r') as f:
                    for l_num, l in enumerate(f,1):
                        if char == l.strip():
                            ser.write(str.encode('L'))
                            print('Placa "{}" foi localizada! Veículo liberado'.format(char))
                            #valor = ser.readline()
                            #print(valor)
                            break    
                        # elif len(char) == 7:
                        #     print("A placa ", char ,"foi detectada, mas não está no sistema!")
                        #     break
                        elif len(char) <= 6:
                            ser.write(str.encode('D'))
                            #valor = ser.readline()
                            #print(valor)
                            #ser.close()
                            print("Não foi possivel fazer a leitura da placa") 
                            break
                        ser.write(str.encode('N'))
                        # valor = ser.readline()
                        # print(valor)
                        print("A placa ", char ,"foi detectada, mas não está no sistema!")
                
                    # else:
                    #     print("A placa ", char ,"foi detectada, mas não está no sistema!")             
                                                         
                img = cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),3)
def removerChar(text):
    str = "!@#%$*()-}°,"":|[]º'“«=+» "
    for x in str:
        text = text.replace(x,'')
    return text
                    
if __name__ == '__main__':
        print("DETECTANDO PLACA . . .")

stream = "http://192.168.27.47:8080/?action=stream"        
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
   

    video = cv2.imwrite('imagem/foto.jpg', frame)
    img = cv2.imread('imagem/foto.jpg')

    inicio=time.time()    

    imagemTratada = tratamentoImagem(frame)
    contornos = extraindoContornos(imagemTratada)
    identificandoPlaca(img,contornos)

    fim=time.time()

    cv2.imshow("Video",img)
   
    if img is ():
        print("TESTE")
    
    
    if cv2.waitKey(1) == 13 :
        break

# imagem = Image.open('imagem/placa.jpg')
# text = tess.image_to_string(imagem, lang='por', config= '--psm 10 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVXWYZ0123456789')
# char = removerChar(text)
# print("Placa detectada : ", char)
tempofinal = fim - inicio
print('{:.4f}s'.format(tempofinal))

#print("O tempo final foi de %d segundos" % (int(inicio)))

cap.release()
cv2.destroyAllWindows()