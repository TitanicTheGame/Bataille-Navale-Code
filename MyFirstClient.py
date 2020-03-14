import sys
from time import sleep
from sys import stdin, exit

from PodSixNet.Connection import connection, ConnectionListener

from tkinter import *
from PIL import Image,ImageTk

X=Y=300

SensBateaux={'B1':'vertical','B2':'vertical','B3':'vertical'}
L=[] #Liste contenant les positions des bateaux
E=0 #Etat du jeu : Phase placement ou phase jeu
R=5

INITIAL=0
ACTIVE=1
DEAD=-1


class Client(ConnectionListener):

    def __init__(self, host, port):
        self.Connect((host, port))
        self.state=INITIAL
        print("Client started")
        print("Ctrl-C to exit")
        print("Enter your nickname: ")
        nickname=stdin.readline().rstrip("\n")
        self.nickname=nickname
        connection.Send({"action": "nickname", "nickname": nickname})
        # a single loop to send to the server my nickname
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
        global E
        E+=1
        if E==2:
            Bombes.bind("<Button-1>",poserBombe)
                
    def Network_BombDropped(self, data):
        n=0
        for i in L:
            (x,y)=i
            if (x,y)==data["bomb"]:
                c.Send({"action":"Touched","touched":"yes"})
                Bateaux.create_image(x,y,image=explosion)
                n=1
        if n==0:
            c.Send({"action":"Touched","touched":"no"})
        
    def Network_Touched(self, data):
        if data["touched"]=="yes":
            print('Touché !')
        else:
            print('Raté')
    
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

def plateau(Canvas):
    global X,Y
    x=y=0
    for i in range(4):
        x+=X/5
        y+=Y/5
        Canvas.create_line(x,0,x,Y,fill='black')
        Canvas.create_line(0,y,X,y,fill='black')

def poserBombe(evt):
    x=evt.x//(X/5)*X/5+X/10
    y=evt.y//(Y/5)*Y/5+Y/10
    Bombes.create_line(x-X/10,y-Y/10,x+X/10,y+Y/10,fill='black')
    Bombes.create_line(x-X/10,y+Y/10,x+X/10,y-Y/10,fill='black')
    c.Send({"action":"BombDropped","bomb":(x,y)})

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

def validerpositions(evt): #Replace le bateau sur les cases
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
    (X1,Y1)=validerpositions2(X1,Y1,'B1')
    (X2,Y2)=validerpositions2(X2,Y2,'B2')
    (X3,Y3)=validerpositions2(X3,Y3,'B3')
    Bateaux.coords(B1,(X1,Y1))
    Bateaux.coords(B2,(X2,Y2))
    Bateaux.coords(B3,(X3,Y3))
   
   
def validerpositions2(x,y,B): #Regarde si le bateau ne dépasse pas du cadre
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
    if X>Y:
        (X1,Y1)=(X,X)
    else:
        (X1,Y1)=(Y,Y)
    img=img.resize((X1,Y1))
    img=img.rotate(90)
    img=img.resize((Y,X))
    return(img)

def valider():
    global E
    E+=1
    if E==2:
        Bombes.bind("<Button-1>",poserBombe)
    Bateaux.unbind("<B1-Motion>")
    Valider.destroy()
    (x1,y1)=Bateaux.coords(B1)
    (x2,y2)=Bateaux.coords(B2)
    (x3,y3)=Bateaux.coords(B3)
    valider2(x1,y1,'B1')
    valider2(x2,y2,'B2')
    valider2(x3,y3,'B3')
    c.Send({"action":"ReadyToPlay","ready":"yes"})

def valider2(x,y,B):
    if SensBateaux[B]=='vertical':
        L.append((x,y-Y/10))
        L.append((x,y+Y/10))
    else:
        L.append((x-X/10,y))
        L.append((x+X/10,y))
        
    
    
#CARTE BATEAU

Plateau=Tk()
Plateau.title('Titanic the game')

Valider=Button(Plateau,text='Valider',command=valider) #Valider les positions des bateaux et passer à la phase de jeu
Valider.pack(side=TOP)


Bateaux=Canvas(Plateau,width=X, height = Y,bg='white')
Bateaux.pack(side=LEFT)
Bateaux.bind("<B1-Motion>",poserbateau)
Bateaux.bind("<ButtonRelease-1>",validerpositions)
Bateaux.bind('<Double-Button-1>',tournerbateau)

img=Image.open('bateau.png') #L'image de départ doit être verticale
img=img.resize((X//5,2*Y//5))
img2=tournerimage(img)
img3=Image.open('explosion.png')
img3=img3.resize((X//5,Y//5))
bateauv=ImageTk.PhotoImage(img)
bateauh=ImageTk.PhotoImage(img2)
fond=PhotoImage(file='fondmer.png')
explosion=ImageTk.PhotoImage(img3)
Bateaux.create_image(X//2,Y//2,image=fond)
B1=Bateaux.create_image(X/10,Y/5,image=bateauv)
B2=Bateaux.create_image(3*X/10,Y/5,image=bateauv)
B3=Bateaux.create_image(5*X/10,Y/5,image=bateauv)

plateau(Bateaux)


#CARTE BOMBE

Bombes=Canvas(Plateau,width=X, height = Y,bg='white')
Bombes.pack(side=RIGHT)
plateau(Bombes)

#POSER BOMBE



# first loop to say to the server that I exist
c.Loop()

