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
    if rkj < (rayon_k + rayon_j)/20: # évite les divergences
        return(np.array([0.0,0.0]))
      
    ukj=rkj_vec/rkj

    return(np.array((G*masse_k*masse_j/(rkj**2))*ukj)) #retourne le vecteur force

## calc_acc_k : Calcule l'accélération du corps k   
def calc_acc_k(tab_r,k,liste_corps):

    masse_k ,_ ,_ ,_,_= liste_corps[k].caracteristiques()
    d,n = np.shape(tab_r) # n nombres corps et d la dimenion x,y,z... 
    rk=tab_r[:,k]  #vecteur position du corps k
    Ftot=np.array([0.0,0.0]) #on initialise le vecteur force total des corps j sur k 
        
    for j in range(n):#toutes les autres j planetes    
        masse_j ,_ ,_ ,_,_= liste_corps[j].caracteristiques()
        if j != k  and masse_j > 1E-6*masse_k :  # le corps j doit être suffisament massif 
                
            rj = tab_r[:,j] #vecteur position du corps j
            Fkj = Force(rk,rj,k,j,liste_corps)
            Ftot += Fkj #on ajoute ttes les contributions des corps j      
            
    ak=Ftot/masse_k#on récupère l'accélération du corps ak cf PFD

    return(ak)
## Permet de tracer un triangle
def coord_triangle(theta,tab_r):
    e_r = np.array([np.cos(theta),np.sin(theta)])
    e_theta = np.array([-np.sin(theta),np.cos(theta)])
    #longueur totale 
    L = 10000E6
    #largeur
    l = 4000E6
    point_haut = tab_r[:,2] + L/2*e_r
    # = -L/2 e_r - a /2 e_theta
    point_gauche = tab_r[:,2] - L/2*e_r - l/2*e_theta
    point_droite = tab_r[:,2] - L/2*e_r + l/2*e_theta
    points = [(point_gauche[0],point_gauche[1]),(point_droite[0],point_droite[1]),(point_haut[0],point_haut[1])]
    return(points)

def nearest_planet(x,y,scale,tab_r,referential,n): #isclicked booléen ,x,y, position en pixels, referentiel corps k sur lequel la cam est basée

    near_planets = []
    near_planets_index = []
    
    
        
    for k in range(n):

        x_corps_k = (tab_r[0,k] - tab_r[0,referential])*scale + CENTER[0] # en pixels
        y_corps_k = (tab_r[1,k] - tab_r[1,referential])*scale + + CENTER[1] # en pixels
        dx = np.abs(x_corps_k-x)
        dy = np.abs(y_corps_k-y)
        if dx + dy < 2000 :
            near_planets.append(dx+dy)
            near_planets_index.append(k)
    
    planet = near_planets_index[near_planets.index(min(near_planets))]
    print(max(near_planets))

    return(planet)         
    
#Partie jeu 
#controles : récupère les inputs du joueur
def controles():

    # Contrôles
    dtheta = 0
    dy=0
    ds=0
    dF=0
    cam_input = -1 # pas d'info !!
    pressed = pygame.key.get_pressed()
    # avant arriere
    if pressed[pygame.K_z]:
        dy += 1  # vers le haut
    if pressed[pygame.K_s]:
        dy -= 1  # vers le bas
    # Orientation du vaisseau
    if pressed[pygame.K_q]:
        dtheta -= 0.0001  # gauche

    if pressed[pygame.K_d]:
        dtheta += 0.0001  # droite
    # Gestion du zoom/dezoom
    if pressed[pygame.K_a]:
        ds -= 0.01

    if pressed[pygame.K_e]:
        ds += 0.01

    if pressed[pygame.K_c]:
        cam_input =1

    if pressed[pygame.K_v]:
        cam_input = 0

    if pressed[pygame.K_x]:
        cam_input = 2

    if pressed[pygame.K_f]:
       dF -= 0.1

    if pressed[pygame.K_g]:
       dF += 0.1

    return(dtheta,dy,ds,cam_input,dF)

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
# Options
F = 1E4 # Newton (force appliquée par l'utilisateur)
dt = 300
dt_predic = dt*2000 #moins précis pour calculer plus vite !
nb_frame = 100
color = (255, 0, 255)  # couleur du vaisseau
cpt_frame = 60  # lance le calcul ttes les cpt_frame
tickrate = 144

#on initialise nos tableaux

n = 5 # nombre de corps 
tab_r=np.zeros((2,n)) #tableau des positions
tab_v=np.zeros((2,n)) #tableau des vitesses        
tab_a=np.zeros((2,n)) #tableau des accélérations

# on définit les corps ici :
dist_terre_lune = 370_00E3
dist_terre_soleil = 5.9722E24,149_597_870.7E3
terre = Corps(5.9722E24,149_597_870.7E3,7_000E3,"Terre",(0,0,255))
dist_vaisseau = 149_598_970.7E3 + 160E5 #on commence proche de la terre
vaisseau = Corps(1E3,dist_vaisseau,10,"Vaisseau",(255,255,255))
soleil = Corps(1.9884E30,0,700_000E3,"Soleil",(255,0,0))
corps_random1 = Corps(5.9722E26,149_597_870.7E3*1.5,2*7_000E3*1.5,"corps random1",(255,100,0))
corps_random2 = Corps(5.9722E27,149_597_870.7E3*3,2*7_000E3*3,"corps random2",(255,0,100))


#Rmars=227_944_000E3
#Vmars=0.1*24.080E3
#Vterre=29.7E3

#boucle du jeu
resolution=(2000, 1200)
SCALE = 1E-4# échelle : 1 pixel = 10E4 km de larges
CENTER = (resolution[0] // 2, resolution[1] // 2)
s = 0
pygame.init()
screen = pygame.display.set_mode(resolution)
clock = pygame.time.Clock()

liste_corps = (soleil,terre,vaisseau,corps_random1,corps_random2)
cam_input = 0 # referentiel du Soleil pour commencer

#initialisation : 1re itération
theta = 0 # angle du vaisseau
referential = 0 # soleil de base
w = 0 # vitesse de rotation
for k in range(n):
    
    tab_r[:,k],tab_v[:,k] = CI_corps_k(liste_corps,k)
    ak = calc_acc_k(tab_r,k,liste_corps)#instant initial cf pas encore dans la boucle
    tab_a[:,k] = ak #on a besoin de l'accélérations initiale pour calculer v2 par Verlet !


planet_k_locked = -1
# Boucle principale du jeu
running = True
locked_state = 0
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Permet de verrouiller une planète 

        if event.type == pygame.MOUSEBUTTONDOWN:
            x_click, y_click = event.pos
            
            if locked_state == 0 or planet_k_locked != nearest_planet(x_click,y_click,SCALE,tab_r,referential,n) : # si on est pas verrouillé ou si on est verrouillé sur une autre planète
                planet_k_locked = nearest_planet(x_click,y_click,SCALE,tab_r,referential,n)
                locked_state = 1
            else : 
                locked_state = 0
                planet_k_locked = -1 #aucune n'est locked

    
    
    # Calcul des trajectoires
    
    if cpt_frame == 60:# toutes les 10 secondes
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

             #on a toutes les nouvelles positions on peut calculer les accélérations   
            for k in range(n):
                tab_a_predict[:,k,i+1] = calc_acc_k(tab_r_predict[:,:,i+1],k,liste_corps)#on a la nouvelle accélération (avec la nouvelle position) pour calculer new_v 
                tab_v_predict[:,k,i+1] = tab_v_predict[:,k,i]+0.5*(tab_a_predict[:,k,i]+tab_a_predict[:,k,i+1])*dt_predic#on obtient la nouvelle vitesse

    cpt_frame += 1
    screen.fill((0, 0, 0))  # Efface l'écran à chaque frame

    # Contrôles: on récupère tous les inputs
    
    dw, dy, ds, cam_input,dF = controles()
    w += dw
    theta += w
    if cam_input != -1:
        referential = cam_input # prend les valeurs 0 1 ou 2 
    F = F+dF*F
    
    s += ds
    masse_vaisseau = 1E3
    # Calcul de l'accélération en fonction de la force et de la masse
    a_norme = F/masse_vaisseau*dy
    accel_vaisseau = a_norme*np.array([np.cos(theta),np.sin(theta)])
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
            if size < 4: # RAYON MINMAL
                size = 4
            couleur = liste_corps[k].caracteristiques()[3]
            # Camera suit le vaisseau ou referentiel Soleil
            offset_x = tab_r[0,referential]
            offset_y = tab_r[1,referential]
            if k != 2:
                pygame.draw.circle(screen,couleur , (int((tab_r[0,k]-offset_x)*SCALE+CENTER[0]), int((tab_r[1,k]-offset_y)*SCALE+CENTER[1])), size )#on enleve la position du vaisseau changement de repère O->O' vaisseau, +res/2 on se met au centreE1
                if k == planet_k_locked :
                    # Tracé du verrouillage
                    pygame.draw.circle(screen,couleur , (int((tab_r[0,k]-offset_x)*SCALE+CENTER[0]), int((tab_r[1,k]-offset_y)*SCALE+CENTER[1])), size*2,1 )#on enleve la position du vaisseau changement de repère O->O' vaisseau, +res/2 on se met au centreE1
                    # Tracé du différence de vitesse entre les deux corps !
                    diff_vitesse = (tab_v[:,2] - tab_v[:,k])
                    x_begin = int((tab_r[0,k]-offset_x)*SCALE+CENTER[0])
                    y_begin = int((tab_r[1,k]-offset_y)*SCALE+CENTER[1])
                    x_end = int((tab_r[0,k] + diff_vitesse[0]* dt * 1000 - offset_x)*SCALE+CENTER[0])
                    y_end = int((tab_r[1,k] + diff_vitesse[1] * dt * 1000 -offset_y)*SCALE+CENTER[1])
                    pygame.draw.line(screen,(255,255,255),(x_begin,y_begin),(x_end,y_begin),1)
                    pygame.draw.line(screen,(255,255,255),(x_begin,y_begin),(x_begin,y_end),1)
                    #pygame.draw.line(screen,(255,255,255) , (int((tab_r[0,k]-offset_x)*SCALE+CENTER[0]), int((tab_r[1,k]-offset_y)*SCALE+CENTER[1])),(int((tab_r[0,k]-offset_x)*SCALE+CENTER[0]), int((tab_r[1,k]-offset_y)*SCALE+CENTER[1])), size )#on enleve la position du vaisseau changement de repère O->O' vaisseau, +res/2 on se met au centreE1
                    
                                          
            if k == 2:
                points = coord_triangle(theta,tab_r)
                # pygame.draw.polygon(screen,couleur , (int((tab_r[0,k]-offset_x)*SCALE+CENTER[0]), int((tab_r[1,k]-offset_y)*SCALE+CENTER[1])), size )#on enleve la position du vaisseau changement de repère O->O' vaisseau, +res/2 on se met au centreE1
                point_gauche = points[0]
                point_droite = points[1]
                point_haut = points[2]
                pygame.draw.polygon(screen, couleur,[(int((point_gauche[0]-offset_x)*SCALE+CENTER[0]), int((point_gauche[1]-offset_y)*SCALE+CENTER[1])), (int((point_droite[0]-offset_x)*SCALE+CENTER[0]), int((point_droite[1]-offset_y)*SCALE+CENTER[1])), (int((point_haut[0]-offset_x)*SCALE+CENTER[0]), int((point_haut[1]-offset_y)*SCALE+CENTER[1]))] )#on enleve la position du vaisseau changement de repère O->O' vaisseau, +res/2 on se met au centreE1

           

            #Affichage trajectoire :
            size = int(size/10)
            if size <1 :
                size = 1
            cpt = 1
            for i in range(nb_frame-1):
                if cpt == 1:
                    #offset  bouge lui même a chaque pas de temps i !
                    offset_x_i = tab_r_predict[0,referential,i]
                    offset_y_i = tab_r_predict[1,referential,i]

                    pygame.draw.circle(screen,couleur , (int((tab_r_predict[0,k,i]-offset_x_i)*SCALE+CENTER[0]), int((tab_r_predict[1,k,i]-offset_y_i)*SCALE+CENTER[1])), 2 )#on enleve la position du vaisseau changement de repère O->O' vaisseau, +res/2 on se met au centreE1
                    cpt = 0
                cpt += 1

    pygame.display.flip()
    clock.tick(tickrate)
    
pygame.quit()
# IDEE : diviser toutes les distances par 10 : diviser G par 100 
