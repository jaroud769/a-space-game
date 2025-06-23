#Importation des modules

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
    def caracteristiques(self):
        return(self.masse,self.distance,self.rayon,self.nom,self.couleur)
    
# Force Renvoie le vecteur force subit par le corps k 2 array
def Force(rk,rj,k,j,liste_corps):#Calcule la force exercée par tous les corps j sur le cors k
    
    G=6.67430E-11 #constante gravitationnelle
    masse_k, _, rayon_k,_,_ = liste_corps[k].caracteristiques()
    masse_j, _, rayon_j,_,_ = liste_corps[j].caracteristiques()
    rkj_vec = rj-rk
    rkj = np.linalg.norm(rkj_vec)
    if rkj < (rayon_k + rayon_j): # évite les divergences
        return(np.array([0.0,0.0]))
      
    ukj=rkj_vec/rkj

    return(np.array((G*masse_k*masse_j/(rkj**2))*ukj)) #retourne le vecteur force

# calc_acc_k : Calcule l'accélération du corps k   
def calc_acc_k(tab_r,k,liste_corps):

    masse_k ,_ ,_ ,_,_= liste_corps[k].caracteristiques()
    d,n = np.shape(tab_r) # n nombres corps et d la dimenion x,y,z... 
    rk=tab_r[:,k]  #vecteur position du corps k
    Ftot=np.array([0.0,0.0]) #on initialise le vecteur force total des corps j sur k 
        
    for j in range(n):#toutes les autres j planetes    
        
        if j != k : #and liste_masse[k]/liste_masse[j] < 1E6 :  #conditions pour optimiser à verifier    
            masse_j ,_ ,_ ,_,_= liste_corps[j].caracteristiques()    
            rj = tab_r[:,j] #vecteur position du corps j
            Fkj = Force(rk,rj,k,j,liste_corps)
            Ftot += Fkj #on ajoute ttes les contributions des corps j      
            
    ak=Ftot/masse_k#on récupère l'accélération du corps ak cf PFD

    return(ak)


#Partie jeu 
#controles : récupère les inputs du joueur
def controles():

    # Contrôles
    dx=0
    dy=0
    ds=0
    cam_input = 2 # pas d'info !!
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

    if pressed[pygame.K_c]:
        cam_input =1

    if pressed[pygame.K_v]:
        cam_input =0
    return(dx,dy,ds,cam_input)

# rebond : calcul du rebond élastique
def rebond(v1,m1,v2,m2):
    
    new_v1 = (2*m2/(m1+m2))*v2 + ((m1-m2)/(m1+m2))*v1
    new_v2 = (2*m2/(m1+m2))*v1 + ((m1-m2)/(m1+m2))*v2
    return(new_v1, new_v2)

def CI_corps_k(liste_corps,k):

    G=6.67430E-11 #constante gravitationnelle
    theta = random.random()*2*np.pi
    _,distance,_,_,_ = liste_corps[k].caracteristiques()
    if distance == 0 : #ie si on est le Soleil
        return([[0,0],[0,0]])
    #SOleil
    masse_soleil ,_ ,_ ,_,_= liste_corps[0].caracteristiques()    
    x = distance * np.cos(theta)
    y = distance * np.sin(theta) 
    v_abs = np.sqrt(G *masse_soleil/distance) 
    vx = -np.sin(theta)*v_abs
    vy = np.cos(theta)*v_abs

    return( [x,y],[vx,vy])
    
#########################################################################################

# Définition des constantes
dF = 1E4 # Newton (force appliquée par l'utilisateur)
dt = 300
dt_predic = dt*100 #moins précis pour calculer plus vite !
color = (255, 0, 255)  # couleur du vaisseau
nb_frame = 600
#on initialise nos tableaux

n = 3 # nombre de corps 
tab_r=np.zeros((2,n)) #tableau des positions
tab_v=np.zeros((2,n)) #tableau des vitesses        
tab_a=np.zeros((2,n)) #tableau des accélérations

# on définit les corps ici :

terre = Corps(5.9722E24,149_597_870.7E3,7_000E3,"Terre",(0,0,255))
dist_vaisseau = 149_598_970.7E3 + 160E5 #on commence proche de la terre
vaisseau = Corps(1E3,dist_vaisseau,10,"Vaisseau",(255,255,255))
soleil = Corps(1.9884E30,0,700_000E3,"Soleil",(255,0,0))

#Rmars=227_944_000E3
#Vmars=0.1*24.080E3
#Vterre=29.7E3

dmin = 7000 #rayon du soleil taille limite (un peu arbitraire mais on s'en fout question d'ODG) car les corps ne sont pas ponctuels dans la vraie vie -> évite les divisions par 0

#boucle du jeu
resolution=(2000, 1200)
SCALE = 1E-4# échelle : 1 pixel = 10E4 km de larges
CENTER = (resolution[0] // 2, resolution[1] // 2)
s = 0
pygame.init()
screen = pygame.display.set_mode(resolution)
clock = pygame.time.Clock()
tickrate = 60
liste_corps = (soleil,terre,vaisseau)
cam_input = 0 # referentiel du Soleil pour commencer
#initialisation : 1re itération
for k in range(n):
    
    tab_r[:,k],tab_v[:,k] = CI_corps_k(liste_corps,k)
    ak = calc_acc_k(tab_r,k,liste_corps)#instant initial cf pas encore dans la boucle
    tab_a[:,k] = ak #on a besoin de l'accélérations initiale pour calculer v2 par Verlet !

# Boucle principale du jeu
running = True
cpt_frame = 600 # Compteur pour lancer le calcul
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Calcul des trajectoires
    if cpt_frame == 600:# toutes les 10 secondes
        cpt_frame = 0
        # CALCUL DE LA TRAJECTOIRE de k corps

        # Tableaux prédictions trajectoires
        tab_r_predict = np.zeros((2,n,nb_frame))
        tab_v_predict = np.zeros((2,n,nb_frame))
        tab_a_predict = np.zeros((2,n,nb_frame))
        # Conditions initiales :
        for k in range(n):
            tab_r_predict[:,k,0] = tab_r[:,k]
            tab_v_predict[:,k,0] = tab_v[:,k]
            tab_a_predict[:,k,0] = tab_a[:,k]
        # Boucle sur le temps
        for i in range(nb_frame-1):
            for k in range(n):
                r_corps_k_temps_i = tab_r_predict[:,k,i]
                v_corps_k_temps_i = tab_v_predict[:,k,i]
                a_corps_k_temps_i = tab_a_predict[:,k,i]
                # Obtention de la position au pas dt suivant
                tab_r_predict[:,k,i+1] = r_corps_k_temps_i+dt_predic*v_corps_k_temps_i+0.5*(dt_predic)**2*a_corps_k_temps_i #on obtient toutes les nouvelles positions ce qui permet de calculer a_n+1
    
                tab_a_predict[:,k,i+1] = calc_acc_k(tab_r_predict[:,:,i+1],k,liste_corps)#on a la nouvelle accélération (avec la nouvelle position) pour calculer new_v 
                tab_v_predict[:,k,i+1] = tab_v_predict[:,k,i]+0.5*(tab_a_predict[:,k,i]+tab_a_predict[:,k,i+1])*dt_predic#on obtient la nouvelle vitesse

    cpt_frame += 1
    screen.fill((0, 0, 0))  # Efface l'écran à chaque frame

    # Contrôles
    dx, dy, ds, cam_input_test = controles()
    if cam_input_test != 2: # si on change de caméra
        cam_input = cam_input_test
    s += ds
    masse_vaisseau = 1E3
    # Calcul de l'accélération en fonction de la force et de la masse
    ax = dx * dF / masse_vaisseau  # a = F / m
    ay = dy * dF / masse_vaisseau  # a = F / m
    accel_vaisseau = [ax, ay]
    SCALE = 1E-8*10**s# échelle : 1 pixel = 10E4 km de larges
   ############################################################################################
   # Retour au temps réel 
    # Calculs des nouvelles positions des n corps !

    for k in range(n):
        
            rk = tab_r[:,k] #vecteur position du corps k
            vk = tab_v[:,k]
            ak = tab_a[:,k]
            tab_r[:,k] = rk+dt*vk+0.5*(dt)**2*ak #on obtient toutes les nouvelles positions ce qui permet de calculer a_n+1
            new_ak = calc_acc_k(tab_r,k,liste_corps)#on a la nouvelle accélération (avec la nouvelle position) pour calculer new_v 

            if k == 2: #si on est le vaisseau on doit rajouter la propulsion !!
                new_ak += accel_vaisseau
        
            tab_v[:,k] = tab_v[:,k]+0.5*(ak+new_ak)*dt#on obtient la nouvelle vitesse
            tab_a[:,k] = new_ak #on a besoin que de ak et new_aik pour calculer new_v on ne garde qu'une seule accélération en arrière
            rayon_k = liste_corps[k].caracteristiques()[2]
            #liste_corps[k].caracteristiques()[-1]
            #tab_r[0,k]  x_corps_k ; #tab_r[1,k] = y_corps_k 
            size = rayon_k*SCALE*1E2
            if size < 1: # RAYON MINMAL
                size = 1
            couleur = liste_corps[k].caracteristiques()[3]
            # Camera suit le vaisseau ou referentiel Soleil
            offset_x = cam_input*tab_r[0,2]
            offset_y = cam_input*tab_r[1,2]

            pygame.draw.circle(screen,couleur , (int((tab_r[0,k]-offset_x)*SCALE+CENTER[0]), int((tab_r[1,k]-offset_y)*SCALE+CENTER[1])), size )#on enleve la position du vaisseau changement de repère O->O' vaisseau, +res/2 on se met au centreE1
            #pygame.draw.circle(screen, color, (int(1E6*SCALE+CENTER[0]), int(1E6*SCALE+CENTER[1])), 5)# on veut que a SCALE = 1E-4 diameter = 100 d'ou diameter = 100 *

            #Affichage trajectoire :
            size = size/10
            if size <1 :
                size = 1
            offset_x = cam_input*tab_r_predict[0,2,0]
            offset_y = cam_input*tab_r_predict[1,2,0]
            for i in range(nb_frame-1):
                
                pygame.draw.circle(screen,couleur , (int((tab_r_predict[0,k,i]-offset_x)*SCALE+CENTER[0]), int((tab_r_predict[1,k,i]-offset_y)*SCALE+CENTER[1])), size )#on enleve la position du vaisseau changement de repère O->O' vaisseau, +res/2 on se met au centreE1
                

    pygame.display.flip()
    clock.tick(tickrate)
    
pygame.quit()
