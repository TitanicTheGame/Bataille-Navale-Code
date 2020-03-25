import sys
from time import sleep
from sys import stdin, exit
from math import *

from PodSixNet.Connection import connection, ConnectionListener

from tkinter import *
from PIL import Image,ImageTk

chemin='/Users/quentinblanchet/Documents/Etudes/CPBx2/Semestre 4/Informatique/Bataille Navale/'

SensBateaux={'B1':'vertical','B2':'vertical','B3':'vertical'}
PosBateaux={'B1':[],'B2':[],'B3':[]} #Liste contenant les positions des bateaux
BateauxTireur={'B1':[],'B2':[],'B3':[]}
PosBateauxTouchés={'B1':[],'B2':[],'B3':[]} #Liste contenant les positions des bateaux touchés
BateauxCoulés={'B1':[],'B2':[],'B3':[]} #Liste contenant les positions des bateaux coulés

ListPoints=[]
def MakeListPoints():
    global X
    x=-X/10
    for i in range(5):
        x+=X/5
        y=-X/10
        for j in range(5):
            y+=X/5
            ListPoints.append((x,y))
    return ListPoints

E=0 #Etat du jeu : Phase placement ou phase jeu
score=3 #Nb de bateaux de l'adversaire
BR=3 #Nb de bateaux restants
T=0 #Variable d'état sur la main du jeu, 0=Pas moi; 1=Moi

R=5

INITIAL=0
ACTIVE=1
DEAD=-1


class Client(ConnectionListener):

    def __init__(self, host, port):
        def clear_entry(event, entry):
            entry.delete(0, END)
        def sendPseudo(self):
            nickname=pseudo.get()
            if nickname!='' and nickname!='Inserez votre pseudo et appuyer sur Entrer':
                self.nickname=nickname
                connection.Send({"action": "nickname", "nickname": nickname})
                Accueil.destroy()
        self.Connect((host, port))
        self.state=INITIAL
        Accueil=Tk()
        Accueil.title('Titanic The Game')
        X=int(Accueil.winfo_screenwidth()*0.75)
        Y=X//2
        positionRight = int(Accueil.winfo_screenwidth()/2-X/2)  #Positioner la fenetre au milieu de l'écran
        positionDown = int(Accueil.winfo_screenheight()/2-Y/2)
        Accueil.geometry("+{}+{}".format(positionRight, positionDown))
        Wallpaper=Canvas(Accueil,width=X,height=Y,bd=0,highlightthickness=0)
        Wallpaper.pack()
        imgW=Image.open(chemin + 'wallpaper.png')
        imgW=imgW.resize((X,Y))
        wallpaper=ImageTk.PhotoImage(imgW)
        Wallpaper.create_image(Y,Y//2,image=wallpaper)

        F=Frame(Accueil,highlightbackground="firebrick",highlightthickness=3)
        F.place(relx=0.5,rely=0.5,anchor=CENTER)
        pseudo=Entry(F,width=40)
        pseudo.pack(side=LEFT)
        pseudo.insert(0, 'Inserez votre pseudo')
        B=Button(F,text="Entrer")
        B.pack(side=RIGHT)
        
        pseudo.bind("<Button-1>", lambda event: clear_entry(event, pseudo))
        pseudo.bind("<Return>",sendPseudo)
        B.bind("<Button-1>",sendPseudo)
        Accueil.mainloop()
        self.Loop()
        
    def Network_connected(self, data):
        print("You are now connected to the server")
    
    def Loop(self):
        connection.Pump()
        self.Pump()

    def quit(self):
        Plateau.destroy()
        self.state=DEAD
   
    def Network_start(self,data):
        self.state=ACTIVE
        while self.state!=DEAD:   
            Plateau.update()
            self.Loop()
            sleep(0.001)
        exit()
        
    def Network_ReadyToPlay(self,data):
        global E,FVALIDER
        global Score
        E+=1
        if E==2:
            Bombes.bind("<Button-1>",poserBombe)
            FVALIDER.pack_forget()
            Wait.destroy()
            Bateauxrestants.set("Bateaux adverses restants : {}".format(score))
            Score=Label(INFOS,textvariable=Bateauxrestants,fg="white")
            Score.pack(fill='both', expand=True)

    def Network_PlayerNumberOne(self,data):
        global T,FLIGHT,LIGHT
        if data["listPlayers"][data["P1"]-1]==data["nickname"]:
            T=1
        FLIGHT=Frame(INFOS)#Voyant vert ou rouge en fonction de la main sur le jeu
        LIGHT=Label(FLIGHT,text="",bg="firebrick")
        LIGHT.pack(side=BOTTOM,fill='both', expand=True)
        FLIGHT.pack(side=BOTTOM,fill='both', expand=True)
        lightTour()
                
    def Network_BombDropped(self, data):
        global BR,Score,T,LIGHT
        n=0
        for i in PosBateaux:
            for j in PosBateaux[i]:
                bomb=[k*(X//data["screensize"]) for k in data["bomb"]]
                if j==bomb:
                    PosBateaux[i].remove(j)
                    PosBateauxTouchés[i].append(j)
                    if len(PosBateaux[i])==0:
                        c.Send({"action":"Touched","touched":"Coulé","bomb":data["bomb"],"B":i})
                        del BateauxTireur[i]
                        BR-=1
                        if BR==0:
                            Score.destroy()
                            LIGHT.destroy()
                            LIGHT=Label(FLIGHT,text="",bg="firebrick")
                            LIGHT.pack(side=BOTTOM,fill='both', expand=True)
                            END=Label(INFOS,text="Vous avez perdu",bg="firebrick",fg="white")
                            END.pack(side=BOTTOM,fill='both', expand=True)
                    else:
                        c.Send({"action":"Touched","touched":"Touché","bomb":data["bomb"],"B":i})
                    Bateaux.create_image(data["bomb"],image=explosion)
                    n=1
        (x,y)=data['bomb']
        if n==0 and verifierExplosion(x,y)==False:
            c.Send({"action":"Touched","touched":"Raté","bomb":data["bomb"],"B":"0"})
            Bateaux.create_line(x-X/10,y-Y/10,x+X/10,y+Y/10,fill='firebrick')
            Bateaux.create_line(x-X/10,y+Y/10,x+X/10,y-Y/10,fill='firebrick')
            T=1
            lightTour()
        
    def Network_Touched(self, data):
        global score,BateauxCoulés,T,LIGHT
        (x,y)=data["bomb"]
        i=data["B"]
        if data["touched"]=="Coulé":
            BateauxCoulés[i].append((x,y))
            afficherBateauCoulé(i)
            score-=1
            if score==0:
                Score.destroy()
                LIGHT.destroy()
                LIGHT=Label(FLIGHT,text="",bg="green")
                LIGHT.pack(side=BOTTOM,fill='both', expand=True)
                END=Label(INFOS,text="Vous avez gagné",bg="green",fg="white")
                END.pack(side=BOTTOM,fill='both', expand=True)
                T=0
            Bateauxrestants.set("Bateaux adverses restants : {}".format(score))
        if data['touched']=='Raté':
            Bombes.create_line(x-X/10,y-Y/10,x+X/10,y+Y/10,fill='firebrick')
            Bombes.create_line(x-X/10,y+Y/10,x+X/10,y-Y/10,fill='firebrick')
            T=0
            lightTour()
        if data['touched']=='Touché':
            Bombes.create_image(x,y,image=explosion)
            BateauxCoulés[i].append((x,y))
            
        
    
    def Network_error(self, data):
        print('error:', data['error'][1])
        connection.Close()
    
    def Network_disconnected(self, data):
        print('Server disconnected')
        exit()
    
#########################################################

if len(sys.argv) != 2:
    print("Please use: python3", sys.argv[0], "host:port")
    print("e.g., python3", sys.argv[0], "localhost:31425")
    exit()

host, port = sys.argv[1].split(":")
c = Client(host, int(port))

#FONCTIONS

def lightTour():
    global T,LIGHT,Score
    if T==1:
        LIGHT.destroy()
        LIGHT=Label(FLIGHT,text="C'est votre tour",bg="green",fg="white")
        LIGHT.pack(side=BOTTOM,fill='both', expand=True)
        Score.config(bg="green")
    if T==0:
        LIGHT.destroy()
        LIGHT=Label(FLIGHT,text="Attendez votre tour",bg="firebrick",fg="white")
        LIGHT.pack(side=BOTTOM,fill='both', expand=True)
        Score.config(bg="firebrick")

def plateau(Canvas):
    global X,Y
    x=y=0
    for i in range(4):
        x+=X/5
        y+=Y/5
        Canvas.create_line(x,0,x,Y,fill='black')
        Canvas.create_line(0,y,X,y,fill='black')

def verifierExplosion(x,y):
    for i in PosBateauxTouchés:
            for j in PosBateauxTouchés[i]:
                if j==(x,y):
                    return True
    return False

def afficherBateauCoulé(i):
    global BateauxCoulés
    X=(BateauxCoulés[i][0][0]+BateauxCoulés[i][1][0])//2
    Y=(BateauxCoulés[i][0][1]+BateauxCoulés[i][1][1])//2
    if X==BateauxCoulés[i][0][0] and X==BateauxCoulés[i][1][0]: #Bateau Coulé est Vertical
        Bombes.create_image(X,Y,image=bateauv)
        Bombes.create_image(BateauxCoulés[i][0][0],BateauxCoulés[i][0][1],image=explosion)
        Bombes.create_image(BateauxCoulés[i][1][0],BateauxCoulés[i][1][1],image=explosion)
    if Y==BateauxCoulés[i][0][1] and Y==BateauxCoulés[i][1][1]: #Bateau Coulé est Horizontal
        Bombes.create_image(X,Y,image=bateauh)
        Bombes.create_image(BateauxCoulés[i][0][0],BateauxCoulés[i][0][1],image=explosion)
        Bombes.create_image(BateauxCoulés[i][1][0],BateauxCoulés[i][1][1],image=explosion)

def poserBombe(evt):
    global T,ListPoints
    n=0
    x=evt.x//(X/5)*X/5+X/10
    y=evt.y//(Y/5)*Y/5+Y/10
    for i in ListPoints:
        if i==(x,y):
            n=1
    if T==1 and n==1:
        animationMissile(x,y)
        ListPoints.remove((x,y))

def poserbateau(evt):
    (x1,y1)=Bateaux.coords(B1)
    (x2,y2)=Bateaux.coords(B2)
    (x3,y3)=Bateaux.coords(B3)
    if evt.x>x1-X/10 and evt.x<x1+X/10 and evt.y>y1-Y/5 and evt.y<y1+Y/5:
        Bateaux.coords(B1,(evt.x,evt.y))
    elif evt.x>x2-X/10 and evt.x<x2+X/10 and evt.y>y2-Y/5 and evt.y<y2+Y/5:
        Bateaux.coords(B2,(evt.x,evt.y))
    elif evt.x>x3-X/10 and evt.x<x3+X/10 and evt.y>y3-Y/5 and evt.y<y3+Y/5:
        Bateaux.coords(B3,(evt.x,evt.y))

def corrigerpositions(evt): #Replace le bateau sur les cases
    (x1,y1)=Bateaux.coords(B1)
    (x2,y2)=Bateaux.coords(B2)
    (x3,y3)=Bateaux.coords(B3)
    if SensBateaux['B1']=='vertical':
        (X1,Y1)=(round(x1//(X/5))*X/5+X/10,round(y1//(Y/5))*(Y/5))
    elif SensBateaux['B1']=='horizontal':
        (X1,Y1)=(round(x1//(X/5))*X/5,round(y1//(Y/5))*Y/5+Y/10)
    if SensBateaux['B2']=='vertical':
        (X2,Y2)=(round(x2//(X/5))*X/5+X/10,round(y2//(Y/5))*(Y/5))
    elif SensBateaux['B2']=='horizontal':
        (X2,Y2)=(round(x2//(X/5))*X/5,round(y2//(Y/5))*Y/5+Y/10)
    if SensBateaux['B3']=='vertical':
        (X3,Y3)=(round(x3//(X/5))*X/5+X/10,round(y3//(Y/5))*Y/5)
    elif SensBateaux['B3']=='horizontal':
        (X3,Y3)=(round(x3//(X/5))*X/5,round(y3//(Y/5))*Y/5+Y/10)
    (X1,Y1)=corrigerpositions2(X1,Y1,'B1')
    (X2,Y2)=corrigerpositions2(X2,Y2,'B2')
    (X3,Y3)=corrigerpositions2(X3,Y3,'B3')
    Bateaux.coords(B1,(X1,Y1))
    Bateaux.coords(B2,(X2,Y2))
    Bateaux.coords(B3,(X3,Y3))
   
   
def corrigerpositions2(x,y,B): #Regarde si le bateau ne dépasse pas du cadre
    if SensBateaux[B]=='vertical':
        if x<=0:
            x=X/10
        if x>=X:
            x=X-X/10
        if y<=0:
            y=Y/5
        if y>=Y:
            y=Y-Y/5
    else:
        if x<=0:
            x=X/5
        if x>=X:
            x=X-X/5
        if y<=0:
            y=Y/10
        if y>=Y:
            y=Y-Y/10
    return(x,y)

def tournerbateau(evt): #Tourne le bateau de 90°
    (x1,y1)=Bateaux.coords(B1)
    (x2,y2)=Bateaux.coords(B2)
    (x3,y3)=Bateaux.coords(B3)
    if evt.x>x1-X/10 and evt.x<x1+X/10 and evt.y>y1-Y/5 and evt.y<y1+Y/5:
        B='B1'
        (x,y)=(x1,y1)
    if evt.x>x2-X/10 and evt.x<x2+X/10 and evt.y>y2-Y/5 and evt.y<y2+Y/5:
        B='B2'
        (x,y)=(x2,y2)
    if evt.x>x3-X/10 and evt.x<x3+X/10 and evt.y>y3-Y/5 and evt.y<y3+Y/5:
        B='B3'
        (x,y)=(x3,y3)
    tournerbateau2(x,y,B)

def tournerbateau2(x,y,B):
    global B1,B2,B3
    if SensBateaux[B]=='vertical':
        if B=='B1':
            Bateaux.delete(B1)
            B1=Bateaux.create_image(x+X/10,y+Y/10,image=bateauh)
        if B=='B2':
            Bateaux.delete(B2)
            B2=Bateaux.create_image(x+X/10,y+Y/10,image=bateauh)
        if B=='B3':
            Bateaux.delete(B3)
            B3=Bateaux.create_image(x+X/10,y+Y/10,image=bateauh)
        SensBateaux[B]='horizontal'
    elif SensBateaux[B]=='horizontal':
        if B=='B1':
            Bateaux.delete(B1)
            B1=Bateaux.create_image(x+X/10,y+Y/10,image=bateauv)
        if B=='B2':
            Bateaux.delete(B2)
            B2=Bateaux.create_image(x+X/10,y+Y/10,image=bateauv)
        if B=='B3':
            Bateaux.delete(B3)
            B3=Bateaux.create_image(x+X/10,y+Y/10,image=bateauv)
        SensBateaux[B]='vertical'
    
def tournerimage(img): #Tourne une image à 90°
    (X,Y)=img.size
    if X>=Y:
        (X1,Y1)=(X,X)
    else:
        (X1,Y1)=(Y,Y)
    img=img.resize((X1,Y1))
    img=img.rotate(270)
    img=img.resize((Y,X))
    return(img)

def valider():
    global E,FVALIDER
    global Wait,Score,Quit
    Valider.destroy()
    TextValider.destroy()
    FVALIDER.pack_forget()
    E+=1
    if E==2:
        Bombes.bind("<Button-1>",poserBombe)
        Bateauxrestants.set("Bateaux adverses restants : {}".format(score))
        Score=Label(INFOS,textvariable=Bateauxrestants,fg="white")
        Score.pack(fill='both', expand=True)
    else:
        FVALIDER=Frame(INFOS)
        Wait=Label(FVALIDER,text="En attente de l'adversaire...",bg="gold",fg="white")
        Wait.pack(side=TOP,fill='both', expand=True)
        FVALIDER.pack(side=TOP,fill='both', expand=True)
    Bateaux.unbind("<B1-Motion>")
    (x1,y1)=Bateaux.coords(B1)
    (x2,y2)=Bateaux.coords(B2)
    (x3,y3)=Bateaux.coords(B3)
    valider2(x1,y1,'B1')
    valider2(x2,y2,'B2')
    valider2(x3,y3,'B3')
    c.Send({"action":"ReadyToPlay","ready":"yes"})

def valider2(x,y,B):
    if SensBateaux[B]=='vertical':
        PosBateaux[B].append([x,y-Y/10])
        PosBateaux[B].append([x,y+Y/10])
    else:
        PosBateaux[B].append([x-X/10,y])
        PosBateaux[B].append([x+X/10,y])
    BateauxTireur[B].append((x,y))

def bateauProcheMilieu():
    X=Y=0
    for i in BateauxTireur:
        if BateauxTireur[i][0][0]>X:
            X=BateauxTireur[i][0][0]
            Y=BateauxTireur[i][0][1]
    return(X,Y)

def tournerMissile(angle):
    imgM=Image.open(chemin+'missile.png')
    imgM=imgM.resize((int(X*0.1),int(X*0.1)))
    imgM=imgM.rotate(angle)
    missile=ImageTk.PhotoImage(imgM)
    return missile

def animationMissile(x2,y2):
    global dx,dy,n
    x2+=X
    (x1,y1)=bateauProcheMilieu()
    dx=x2-x1
    dy=y2-y1
    missile=tournerMissile(-(atan(dy/dx)*180/pi))
    M=Bateaux.create_image(x1,y1,image=missile)
    Bateaux.image=missile
    def animate(Canvas,M,xf):
        l=sqrt(2*11**2)/sqrt(dx**2+dy**2)
        DX=l*dx
        DY=l*dy
        x0,y0=Canvas.coords(M)
        Canvas.move(M,DX,DY)
        if x0>=xf:
            Canvas.delete(M)
            if xf==x2-X:
                Canvas.delete(M)
                c.Send({"action":"BombDropped","bomb":[x2-X,y2],"screensize":X})
            else:
                M=Bombes.create_image(0,y0,image=missile)
                Bombes.image=missile
                animate(Bombes,M,x2-X)
        else:
            Canvas.after(15, animate, Canvas,M,xf)
    animate(Bateaux,M,Bateaux.winfo_width())

 
#PLATEAU#############################################

Plateau=Tk()
Plateau.title('Titanic the game')
X=int(Plateau.winfo_screenwidth()*0.75)//2
Y=X
positionRight = int(Plateau.winfo_screenwidth()/2-X)  #Positioner la fenetre au milieu de l'écran
positionDown = int(Plateau.winfo_screenheight()/2-Y/2)
Plateau.geometry("+{}+{}".format(positionRight, positionDown))

MakeListPoints()

#INFORMATIONS

Bateauxrestants=StringVar()

INFOS=Frame(Plateau)

FVALIDER=Frame(INFOS,bg="gold")
TextValider=Label(FVALIDER,text="Placez vos bateaux, puis valider",bg="gold",fg="white")
TextValider.pack()
Valider=Button(FVALIDER,text='Valider',command=valider) #Valider les positions des bateaux et passer à la phase de jeu
Valider.pack()
FVALIDER.pack(side=TOP,fill='both', expand=True)


INFOS.pack(side=TOP,fill='both', expand=True)



#CARTE BATEAU
P=Frame(Plateau)
P.pack()
Bateaux=Canvas(P,width=X, height=Y,bd=0,highlightthickness=0)
Bateaux.pack(side=LEFT)

Bateaux.bind("<B1-Motion>",poserbateau)
Bateaux.bind("<ButtonRelease-1>",corrigerpositions)
Bateaux.bind('<Double-Button-1>',tournerbateau)

img=Image.open(chemin+'bateau.png') #L'image de départ doit être verticale
img=img.resize((int((img.size[0]*((14*X)/45))/img.size[1]),int(((14*X)/40))))
img2=tournerimage(img)
img3=Image.open(chemin+'explosion.png')
img3=img3.resize((X//5,Y//5))
bateauv=ImageTk.PhotoImage(img)
bateauh=ImageTk.PhotoImage(img2)
explosion=ImageTk.PhotoImage(img3)

imgFG=Image.open(chemin+'oceanG.gif')
imgFG=imgFG.resize((Y,Y))
oceanG=ImageTk.PhotoImage(imgFG)
Bateaux.create_image(X/2,Y/2,image=oceanG)

B1=Bateaux.create_image(X/10,Y/5,image=bateauv)
B2=Bateaux.create_image(3*X/10,Y/5,image=bateauv)
B3=Bateaux.create_image(5*X/10,Y/5,image=bateauv)

plateau(Bateaux)


#CARTE BOMBE

Bombes=Canvas(P,width=X, height=Y,bd=0,highlightthickness=0)
Bombes.pack(side=RIGHT)
imgFD=Image.open(chemin+'oceanD.gif')
imgFD=imgFD.resize((Y,Y))
oceanD=ImageTk.PhotoImage(imgFD)
Bombes.create_image(X/2,Y/2,image=oceanD)

plateau(Bombes)


#NUAGES
imgC1=Image.open(chemin+'cloud1.png')
imgC2=Image.open(chemin+'cloud2.png')
imgC1=imgC1.resize((int((imgC1.size[0]*(Y//5)/imgC1.size[1])),Y//5))
imgC2=imgC2.resize((int((imgC2.size[0]*(Y//4)/imgC2.size[1])),Y//4))
nuage1=ImageTk.PhotoImage(imgC1)
nuage2=ImageTk.PhotoImage(imgC2)
Bombes.create_image(X*0.4,Y*0.65,image=nuage1)
Bombes.create_image(X*0.2,Y*0.4,image=nuage1)
Bombes.create_image(X*0.8,Y*0.75,image=nuage1)
Bombes.create_image(X*0.8,Y*0.2,image=nuage1)
Bombes.create_image(X*0.7,Y*0.45,image=nuage2)
Bombes.create_image(X//3,Y*0.85,image=nuage2)
Bombes.create_image(X*0.3,Y*0.15,image=nuage2)

#FILLET - MUR DU MILIEUR
Bombes.create_line(0,0,0,Y,fill='firebrick',width=5)
Bateaux.create_line(Y,0,Y,Y,fill='firebrick',width=5)

#QUITTER
Quitter=Frame(Plateau)
Quit=Button(Quitter,text='Quitter la partie', command=c.quit)
Quit.pack()
Quitter.pack(side=BOTTOM,fill='both', expand=True)

# first loop to say to the server that I exist
c.Loop()
