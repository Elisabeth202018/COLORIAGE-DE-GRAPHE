
#classe UE
class UE:
    def __init__(self,code, niveau, eff, type_salle, optionnel):
        self.code= code
        self.niveau=niveau
        self.effectif= eff
        self.salle = type_salle
        self.optionnel = optionnel

#Creation de la liste des UE des niveaux L1,L2,L3 et M1
ues = []
#niveau1
ues.append(UE("INF111","L1",1200,"standard",optionnel=False))
ues.append(UE("INF121","L1",1200,"standard",optionnel=False))
ues.append(UE("INF131","L1",1200,"standard",optionnel=False))
ues.append(UE("INF141","L1",1200,"standard",optionnel=True))
ues.append(UE("INF151","L1",1200,"standard",optionnel=True))

#niveau 2
ues.append(UE("INF211","L2",800,"standard",optionnel=False))
ues.append(UE("INF221","L2",800,"standard",optionnel=False))
ues.append(UE("INF231","L2",800,"standard",optionnel=False))
ues.append(UE("INF241","L2",800,"standard",optionnel=True))
ues.append(UE("INF251","L2",800,"standard",optionnel=True))
ues.append(UE("ENG211","L2",800,"standard",optionnel=False))

n = len(ues)

#MATRICE
matrice = [[0]*n for _ in range(n)]
for i in range(n):
    for j in range(i+1,n):
        if ues[i].niveau ==ues[j].niveau:
            matrice[i][j] = 1
            matrice[j][i] = 1

#LISTE D'ADJACENCE
list_adj = [[] for _ in range(n)]
for i in range(n):
    for j in range(i+1,n):
        if ues[i].niveau ==ues[j].niveau:
            if ues[i].optionnel and ues[j].optionnel:
                continue
            list_adj[i].append(j)
            list_adj[j].append(i)

#STATISTIQUES DE GRAPHE
print("=" * 35)
print(" STATISTIQUES DU GRAPHE")
print("=" * 35)
#nombre de sommets
print(f"\n Nombre de sommets:{n}")

#nombre d'aretes
nb_arete = sum(len(voisins) for voisins in list_adj)
print(f"\n Nombre de aretes(conflit):{nb_arete}")

#degre de chaque sommet
print("\n Degre de chaque sommet: ")
for i,ue in enumerate(ues):
    print(f" {ue.code:10} : {len(list_adj[i])} voisins")

print("====Matrice d'adjacence====:")
for i in range(n):
    print(f"{ues[i].code:10}" ," ".join(str(matrice[i][j])for j in range (n))) 
    
print("====Liste d'adjacence====:")
for i, ue in enumerate(ues):
    voisins_code = [ues[v].code for v in list_adj[i]]
    print(f"{ue.code:8} --> {voisins_code}")

import networkx as nx
import matplotlib.pyplot as plt

# Création du graphe
G = nx.Graph()

# Ajout des sommets
for ue in ues:
    G.add_node(ue.code)

# Ajout des arêtes
for i in range(n):
    for j in list_adj[i]:
        G.add_edge(ues[i].code, ues[j].code)

# Couleurs selon le niveau
couleurs = []
for ue in ues:
    if ue.niveau == "L1":
        couleurs.append("skyblue")
    elif ue.niveau == "L2":
        couleurs.append("lightgreen")
    elif ue.niveau == "L3":
        couleurs.append("orange")
    else:
        couleurs.append("pink")

# Taille de la fenêtre
plt.figure(figsize=(12, 8))

# Positionnement automatique des sommets
pos = nx.spring_layout(G, seed=42)

# Dessin du graphe
nx.draw_networkx_nodes(
    G,
    pos,
    node_color=couleurs,
    node_size=2500
)

nx.draw_networkx_edges(
    G,
    pos,
    width=2
)

nx.draw_networkx_labels(
    G,
    pos,
    font_size=9,
    font_weight="bold"
)

plt.title("GRAPHE DES CONFLITS ENTRE UE", fontsize=14)
plt.axis("off")

# Sauvegarde de l'image
plt.savefig("graphe_ue.png")

# Affichage
plt.show()