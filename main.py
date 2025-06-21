#Importation des données

import random
import numpy as np
import pygame
import random
import matplotlib.pyplot as plt
import pygame

########################################################################################
# Définition des fonctions et classes 

# Création de la classe des corps célestes
class Corps:
    def __init__(self,masse,distance,rayon,couleur,nom):
        self.masse = masse
        self.distance = distance
        self.nom = nom
        self.rayon = rayon
        self.couleur = couleur
    def caracteristiques(corps):
        return(corps.masse,corps.distance,corps.rayon,corps.nom,corps.couleur)
    
# Force Renvoie le vecteur force subit par le corps k 2 array
def Force(rk,rj,k,j,liste_corps):#Calcule la force exercée par tous les corps j sur le cors k
    
    G=6.67430E-11 #constante gravitationnelle
    rayon_k, _, masse_k = liste_corps[k].caracteristiques()
    rayon_j, _, masse_j = liste_corps[j].caracteristiques()
    rkj_vec = rj-rk
    rkj = np.linalg.norm(rkj_vec)
    if rkj < (rayon_k + rayon_j): # évite les divergences
        return(np.array([0.0,0.0]))
      
    ukj=rkj_vec/rkj

    return(np.array((G*masse_k*masse_j/(rkj**2))*ukj)) #retourne le vecteur force

# calc_acc_k : Calcule l'accélération du corps k   
def calc_acc_k(tab_r,k,liste_corps):

    masse_k ,_ ,_ ,_= liste_corps[k].caracteristiques()
    n,d=np.shape(tab_r) # n nombres corps et d la dimenion x,y,z... 
    rk=tab_r[k,:]  #vecteur position du corps k
    Ftot=np.array([0.0,0.0]) #on initialise le vecteur force total des corps j sur k 
        
    for j in range(n):#toutes les autres j planetes    
        if j != k and liste_masse[k]/liste_masse[j] < 1E6 :  #conditions pour optimiser à verifier    
            masse_j ,_ ,_ ,_= liste_corps[j].caracteristiques()    
            rj = tab_r[j,:] #vecteur position du corps j
            Fkj = Force(rk,rj,k,j,liste_corps)
            Ftot += Fkj #on ajoute ttes les contributions des corps j      
            
    ak=Ftot/liste_masse[k]#on récupère l'accélération du corps ak cf PFD

    return(ak)

#Partie jeu 
#controles : récupère les inputs du joueur
def controles():

    # Contrôles
    
    dx=0
    dy=0
    ds=0
    
    pressed = pygame.key.get_pressed()

    # haut bas gauche droite
    if pressed[pygame.K_z]:
        dy -= 1  # vers le haut
    if pressed[pygame.K_s]:
        dy += 1  # vers le bas
    if pressed[pygame.K_q]:
        dx -= 1  # gauche
    if pressed[pygame.K_d]:
        dx += 1  # droite

    # Gestion du zoom/dezoom
    if pressed[pygame.K_a]:
        ds -= 0.01
    if pressed[pygame.K_e]:
        ds += 0.01

    return(dx,dy,ds)

# rebond : calcul du rebond élastique
def rebond(v1,m1,v2,m2):
    
    new_v1 = (2*m2/(m1+m2))*v2 + ((m1-m2)/(m1+m2))*v1
    new_v2 = (2*m2/(m1+m2))*v1 + ((m1-m2)/(m1+m2))*v2

    return(new_v1, new_v2)


# Définition des constantes
MASS = 1E3  # masse du vaisseau en kg (1 tonne)
dF = 1E4 # Newton (force appliquée par l'utilisateur)
dt = 3
color = (255, 0, 255)  # couleur du vaisseau

#on initialise nos tableaux

n = 2 # nombre de corps 
tab_r=np.zeros((2,n)) #tableau des positions
tab_v=np.zeros((2,n)) #tableau des vitesses

def CI_corps_k(liste_corps,k):

    G=6.67430E-11 #constante gravitationnelle
    theta = random.random()*2*np.pi
    _,distance,_,_ = liste_corps[k].caracteristiques
    if distance == 0 :
        return()
    x = distance * np.cos(theta)
    y = distance * np.sin(theta) 
    v_abs = np.sqrt( G * )
    
    
#########################################################################################

#Définitions des n corps !!!
terre = Corps(5.9722E24,149_597_870.7E3,7_000E3,"Terre",(255,0,0))
dist_vaisseau = 149_598_970.7E3 + 160E5 #on commence proche de la terre
vaisseau = Corps(1E3,dist_vaisseau,10,"Vaisseau",(255,255,255))
soleil = Corps(1.9884E30,0,700_000E3,"Soleil",(0,0,255))
#Rmars=227_944_000E3
#Vmars=0.1*24.080E3
#Vterre=29.7E3
        
liste_ac=[]#liste des accélérations pour chaque corps 
dmin = 7000 #rayon du soleil taille limite (un peu arbitraire mais on s'en fout question d'ODG) car les corps ne sont pas ponctuels dans la vraie vie -> évite les divisions par 0

#boucle du jeu
resolution=(2000, 1200)
SCALE = 1E-4# échelle : 1 pixel = 10E4 km de larges
CENTER = (resolution[0] // 2, resolution[1] // 2)
s = 0
import pygame

pygame.init()
screen = pygame.display.set_mode(resolution)
clock = pygame.time.Clock()
tickrate = 60


for k in range(n):
    
    tab_r[k]=CI[k][0]
    tab_v[k]=CI[k][1]
        
    ak = calc_acc_k(tab_r,k,liste_masse)#instant initial cf pas encore dans la boucle
    liste_ac.append(ak) #on a besoin de l'accélérations initiale pour calculer v2 par Verlet !

# Boucle principale du jeu
running = True

while running:
    
    screen.fill((0, 0, 0))  # Efface l'écran à chaque frame

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Contrôles
    dx, dy, ds = controles()
    s += ds
    
    # Calcul de l'accélération en fonction de la force et de la masse
    ax = dx * dF / MASS  # a = F / m
    ay = dy * dF / MASS  # a = F / m
    a = [ax, ay]
    SCALE = 1E-4*10**s# échelle : 1 pixel = 10E4 km de larges
    
    # Calculs des nouvelles positions des n corps !
    for k in range(n):
        
            rk=tab_r[k,:] #vecteur position du corps k
            vk=tab_v[k,:]
            ak=liste_ac[k,:]
            tab_r[k,:]=rk+dt*vk+0.5*(dt)**2*ak #on obtient toutes les nouvelles positions ce qui permet de calculer a_n+1
            new_ak = calc_acc_k(tab_r,k,liste_masse)#on a la nouvelle accélération pour calculer new_v 

            if k == 1: #si on est le vaisseau on doit rajouter la propulsion !!
                new_ak += a 
        
            tab_v[k,:]=tab_v[k,:]+0.5*(ak+new_ak)*dt#on obtient la nouvelle vitesse
            liste_ac[k,:]=new_ak #on a besoin que de aik et new_aik pour calculer new_v on ne garde qu'une seule accélération en arrière
        
    
            pygame.draw.circle(screen, couleurs[k], (int((tab_r[k,:][0]-tab_r[1,0])*SCALE+CENTER[0]), int((tab_r[k,1]-tab_r[1,1])*SCALE+CENTER[1])), diameter_list[k]*SCALE*1E4)#on enleve la position du vaisseau changement de repère O->O' vaisseau, +res/2 on se met au centreE1
            #pygame.draw.circle(screen, color, (int(1E6*SCALE+CENTER[0]), int(1E6*SCALE+CENTER[1])), 5)# on veut que a SCALE = 1E-4 diameter = 100 d'ou diameter = 100 *
            
    pygame.display.flip()
    clock.tick(tickrate)
    
pygame.quit()

#A rajouter faire des classes et des fonctions pour definir taille , masse , CI de chaque corps, donner une taille pour chaque corps.