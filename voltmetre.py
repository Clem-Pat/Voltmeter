import tkinter as tk  #module d'interface graphique
import pyfirmata    #module de communication avec la carte Arduino
from matplotlib.figure import Figure    #importer le module Figure dans Matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg     #pour afficher le graphique DANS la fenêtre Tkinter (matplotlib ~ Pyplot et CanvasTk renvoie à Tkinter)
import time
import keyboard #module de contrôle du clavier



"""voltmeter 2 values, A0 and A1"""
#

def definir_board():
    try:
        board=pyfirmata.Arduino('COM7') #On définit la carte Arduino qui est branchée sur le port COM8
        iter8 = pyfirmata.util.Iterator(board)  #On accepte de soutirer des infos à la carte
        iter8.start()   #On démarre la lecture des données (itérative cad qu'on actualise la lecture des données)
        # board.analog[0].enable_reporting()  #On accepte la lecture des données de la pin analogue 0
        board.analog[0].enable_reporting()  #On accepte la lecture des données de la pin analogue 5
        board.analog[1].enable_reporting()  #On accepte la lecture des données de la pin analogue 5
        time.sleep(1)   #On attend un peu pour laisser le temps à la carte de charger

        a0 = board.analog[0]  #on donne un nom à la pin 5
        a1 = board.analog[1]  #on donne un nom à la pin 5
    except:
        board, a0, a1 = None, None, None

    return board, a0, a1

def definir_application():
    def destroy(*args):
        app.destroy()

    posx, posy = 450, 0 #positions de la fenetre
    longueur, hauteur = 800, 800

    app = tk.Tk()
    app.minsize(longueur, hauteur)
    app.geometry("820x645+{}+{}".format(str(posx), str(posy))) #placer la fenêtre #"bonjour {}".format("Vio et Alex") renvoie la chaine de caractère "bonjour Vio et Alex"
    app.configure(bg="light blue") #background = bleu ciel.

    title = tk.Label(app, text='Voltmètre', bg='light blue', fg='navy', font='Impact 30 bold') #Le label (venant de Tkinter) Titre
    title.place(x=550, y=40)
    app.bind('<Escape>', destroy)
    app.state('zoomed')


    return app

def plot(app, time_x_axis, y_axis_lists, name=None, color=None):

    figure = Figure(figsize=(6, 4), dpi=96) #Définir la figure
    ax = figure.add_subplot(111)        #ajouter un plan orthonormé dans la figure

    if name == None: names = ['a0', 'a1']
    else: names = [name]

    if color == None: colors = ['orange', 'blue']
    else: colors = [color]

    for i in range(len(y_axis_lists)):
        ax.plot(time_x_axis, y_axis_lists[i], color=colors[i], label=names[i], marker="+", ls='-')   #sur l'axe, on plot la courbe servo moteur (idem)
    ax.legend(loc='best', shadow=True, fontsize='small', markerscale=0.4)   #Ajouter une légende qui s'affiche au mieux sur le graphe
    ax.set(xlabel='temps (s)')  #Ajouter un titre à l'axe des abscisses
    graph = FigureCanvasTkAgg(figure, master=app)   #greffer la figure 'figure' dans la fenêtre 'app'
    canvas = graph.get_tk_widget()  #Récupérer tout le canvas graphique pour le renvoyer.

    return canvas



def main():

    app = definir_application()
    text = tk.Label(app, text = 'valeur mesurée a0 : {}'.format(0), fg='black', bg='light blue')
    text2 = tk.Label(app, text = 'valeur mesurée a1 : {}'.format(0), fg='black', bg='light blue')
    text.place(x=100, y=550)
    text2.place(x=700, y=550)

    board, a0, a1 = definir_board() #Définir la carte arduino et les 3 pins avec lesquelles on communique.

    t0 = time.time() #instant initial
    if board != None :
        time_x_axis, y_axis = [t0], [[a0.read()], [a1.read()]]    #listes des valeurs à afficher (moins grandes que les vraies listes de valeurs)
    else:
        time_x_axis, y_axis = [0], [[0], [0]]

    while not keyboard.is_pressed('ctrl'): #tant que la fenêtre est ouverte :
        try:
            if board != None:
                a0_value, a1_value = a0.read(), a1.read()    #on lit la valeur en sortie du servo
                ti = time.time()    #on lit l'instant

                text.config(text = 'valeur mesurée a0: {}'.format(a0_value))
                text2.config(text = 'valeur mesurée a1: {}'.format(a1_value))
                # text.place(x=100, y=550)
                # text2.place(x=100, y=570)

                tdernier = time_x_axis[-1]  #on note l'instant tdernier = t(i-1) le dernier instant pour lequel on a lu et affiché les valeurs
                if ti - tdernier >= 0.05: #si ti - t(i-1) est supérieur à 0.2, on ajoute les valeurs lues à l'instant ti aux listes des valeurs à afficher. (Permet de ne pas afficher des listes immenses)
                    time_x_axis.append(ti)
                    y_axis[0].append(a0_value)
                    y_axis[1].append(a1_value)

                graph0 = plot(app, time_x_axis, [y_axis[0]], 'a0', 'orange') #on affiche les nouvelles valeurs lues (cad on affiche à nouveau toutes les listes qui sont un peu plus grosses)
                graph1 = plot(app, time_x_axis, [y_axis[1]], 'a1', 'blue') #on affiche les nouvelles valeurs lues (cad on affiche à nouveau toutes les listes qui sont un peu plus grosses)
                graph0.place(x=50, y=150)
                graph1.place(x=650, y=150)

                if len(time_x_axis)>=30: #si on affiche trop de valeurs, on enlève les premières valeurs des listes (impression d'avancée dans le temps)
                    time_x_axis.pop(0)
                    y_axis[0].pop(0)
                    y_axis[1].pop(0)

            else:
                graph0 = plot(app, [0], [[0]], 'a0', 'orange')
                graph1 = plot(app, [0], [[0]], 'a1', 'blue')
                graph0.place(x=50, y=150)
                graph1.place(x=650, y=150)

            app.update()
        except: #si on n'y arrive pas, on sort de la boucle while parce que la fenêtre a été détruite.
            break


if __name__ == '__main__':
    main()  #on rentre dans le programme.
