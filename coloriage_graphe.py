import csv
import matplotlib.pyplot as plt
import networkx as nx

# ============================================
# 1. DÉFINITION DES CLASSES
# ============================================

class UE:
    """Classe représentant une Unité d'Enseignement"""
    def __init__(self, code, niveau, effectif, type_salle="standard"):
        self.code = code
        self.niveau = niveau
        self.effectif = effectif
        self.type_salle = type_salle  # "standard" ou "labo"
    
    def __repr__(self):
        return f"UE({self.code}, {self.effectif} étudiants, {self.type_salle})"

class Salle:
    """Classe représentant une salle d'examen"""
    def __init__(self, nom, capacite, type_salle="standard"):
        self.nom = nom
        self.capacite = capacite
        self.type_salle = type_salle  # "standard" ou "labo"
    
    def __repr__(self):
        return f"Salle({self.nom}, {self.capacite} places, {self.type_salle})"

# ============================================
# 2. ALGORITHMES DE COLORATION
# ============================================

def dsatur(ues, list_adj):
    """Algorithme DSATUR pour la coloration de graphe"""
    n = len(ues)
    coloration = {}
    
    def get_dsat(u):
        couleurs_voisines = {coloration[v] for v in list_adj[u] if v in coloration}
        return len(couleurs_voisines)

    while len(coloration) < n:
        non_colores = [i for i in range(n) if i not in coloration]
        u_choisi = max(non_colores, key=lambda i: (get_dsat(i), len(list_adj[i])))
        
        couleurs_voisins = {coloration[v] for v in list_adj[u_choisi] if v in coloration}
        couleur = 1
        while couleur in couleurs_voisins:
            couleur += 1
            
        coloration[u_choisi] = couleur
        
    return coloration

def welsh_powell(ues, list_adj):
    """Algorithme de Welsh-Powell pour la coloration de graphe"""
    n = len(ues)
    degres = [(i, len(list_adj[i])) for i in range(n)]
    degres.sort(key=lambda x: x[1], reverse=True)
    ordre = [i for i, _ in degres]
    
    coloration = {}
    for u in ordre:
        couleurs_voisins = {coloration[v] for v in list_adj[u] if v in coloration}
        couleur = 1
        while couleur in couleurs_voisins:
            couleur += 1
        coloration[u] = couleur
    
    return coloration

# ============================================
# 3. ATTRIBUTION DES SALLES
# ============================================

def attribuer_salles(coloration, ues, salles):
    """Attribue une salle à chaque UE en vérifiant les capacités et types"""
    planning_salles = {}
    if not coloration:
        return planning_salles
        
    nb_creneaux = max(coloration.values())
    
    for creneau in range(1, nb_creneaux + 1):
        ues_du_creneau = [i for i, col in coloration.items() if col == creneau]
        salles_libres = salles.copy()
        ues_du_creneau.sort(key=lambda u: ues[u].effectif, reverse=True)
        
        for u in ues_du_creneau:
            ue = ues[u]
            meilleure_salle = None
            for salle in salles_libres:
                if salle.type_salle == ue.type_salle and salle.capacite >= ue.effectif:
                    if meilleure_salle is None or salle.capacite < meilleure_salle.capacite:
                        meilleure_salle = salle
            
            if meilleure_salle:
                planning_salles[u] = meilleure_salle.nom
                salles_libres.remove(meilleure_salle)
            else:
                planning_salles[u] = "⚠️ AUCUNE SALLE"
    
    return planning_salles

# ============================================
# 4. VISUALISATION DU GRAPHES
# ============================================

def afficher_graphe(ues, list_adj, coloration):
    """Génère et affiche le graphe coloré avec NetworkX et Matplotlib"""
    G = nx.Graph()
    
    # Ajouter les sommets avec leur code UE
    for i, ue in enumerate(ues):
        G.add_node(i, label=ue.code)
        
    # Ajouter les arêtes
    for u in list_adj:
        for v in list_adj[u]:
            if u < v:  # Éviter les doublons pour un graphe non-orienté
                G.add_edge(u, v)
                
    labels = nx.get_node_attributes(G, 'label')
    
    # Mapper les couleurs (générer une palette dynamique selon le nombre de couleurs)
    if coloration:
        nb_couleurs = max(coloration.values())
        palette = plt.cm.rainbow([i / nb_couleurs for i in range(nb_couleurs)])
        node_colors = [palette[coloration[node] - 1] for node in G.nodes()]
    else:
        node_colors = 'lightblue'
        
    plt.figure(figsize=(10, 7))
    plt.title("Graphe de Conflits des UE (Coloration représentant les Créneaux)")
    
    # Positionnement des sommets
    pos = nx.spring_layout(G, seed=42)
    
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=700, edgecolors='black')
    nx.draw_networkx_edges(G, pos, width=1.5, alpha=0.6)
    nx.draw_networkx_labels(G, pos, labels, font_size=10, font_weight='bold')
    
    plt.axis('off')
    print("\nVisualisation du graphe en cours de génération... (Ferme la fenêtre du graphe pour continuer)")
    plt.savefig("graphe_colorie.png")  # Sauvegarde demandée par le livrable
    plt.show()

# ============================================
# 5. EXPORTATION CSV
# ============================================

def exporter_planning_csv(ues, coloration, planning_salles, filename="planning_examens.csv"):
    """Exporte le planning sous forme Créneau/Salle/UE en fichier CSV"""
    if not coloration:
        print("Aucun planning à exporter.")
        return
        
    nb_creneaux = max(coloration.values())
    salles_utilisees = sorted(list(set(planning_salles.values())))
    if "⚠️ AUCUNE SALLE" in salles_utilisees:
        salles_utilisees.remove("⚠️ AUCUNE SALLE")
    salles_utilisees.append("Sans Salle") # Colonne pour les UE non affectées

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # En-tête : Créneau | Liste des salles
        header = ["Créneau / Horaire"] + salles_utilisees
        writer.writerow(header)
        
        # Remplissage ligne par ligne (chaque ligne correspond à un créneau)
        for creneau in range(1, nb_creneaux + 1):
            ligne = [f"Créneau {creneau}"]
            
            # Récupérer les UE de ce créneau
            ues_du_creneau = [u for u, col in coloration.items() if col == creneau]
            
            # Mapper chaque salle vers l'UE affectée dans ce créneau
            salle_to_ue = {}
            ue_sans_salle = []
            for u in ues_du_creneau:
                salle = planning_salles[u]
                if salle == "⚠️ AUCUNE SALLE":
                    ue_sans_salle.append(f"{ues[u].code} ({ues[u].effectif})")
                else:
                    salle_to_ue[salle] = f"{ues[u].code} ({ues[u].effectif})"
            
            # Construire la ligne de données pour le CSV
            for salle in salles_utilisees[:-1]:
                ligne.append(salle_to_ue.get(salle, "")) # Vide si la salle n'est pas occupée
                
            # Ajouter les UE sans salle à la fin
            ligne.append(", ".join(ue_sans_salle) if ue_sans_salle else "")
            writer.writerow(ligne)
            
    print(f"\n💾 Planning exporté avec succès dans le fichier : '{filename}'")

# ============================================
# 6. Saisie Dynamique des Données (Interface Utilisateur)
# ============================================

def saisir_donnees():
    """Permet à l'utilisateur d'entrer dynamiquement ses propres UE et salles"""
    ues = []
    salles = []
    list_adj = {}
    
    print("\n--- ÉTAPE 1 : ENREGISTREMENT DES UNITÉS D'ENSEIGNEMENT (UE) ---")
    nb_ues = int(input("Combien d'UE voulez-vous planifier ? : "))
    for i in range(nb_ues):
        print(f"\nSaisie de l'UE n°{i+1}:")
        code = input("Code de l'UE (ex: INF211) : ").strip().upper()
        niveau = input("Niveau (ex: L2) : ").strip()
        effectif = int(input("Effectif des étudiants inscrits : "))
        type_salle = input("Type de salle requis (standard/labo) [Défaut: standard] : ").strip().lower()
        if type_salle != "labo":
            type_salle = "standard"
        ues.append(UE(code, niveau, effectif, type_salle))
        list_adj[i] = []

    print("\n--- ÉTAPE 2 : ENREGISTREMENT DES SALLES DISPONIBLES ---")
    nb_salles = int(input("Combien de salles sont disponibles ? : "))
    for i in range(nb_salles):
        print(f"\nSaisie de la Salle n°{i+1}:")
        nom = input("Nom/Numéro de la salle (ex: Amphi A, Salle 102) : ").strip()
        capacite = int(input("Capacité maximale de la salle : "))
        type_salle = input("Type de la salle (standard/labo) [Défaut: standard] : ").strip().lower()
        if type_salle != "labo":
            type_salle = "standard"
        salles.append(Salle(nom, capacite, type_salle))

    print("\n--- ÉTAPE 3 : DÉFINITION DES CONFLITS (Étudiants en commun) ---")
    print("Pour chaque paire d'UE, indiquez s'il y a un conflit (des étudiants inscrits aux deux matières).")
    for i in range(nb_ues):
        for j in range(i + 1, nb_ues):
            reponse = input(f"Est-ce que des étudiants suivent à la fois {ues[i].code} et {ues[j].code} ? (o/n) : ").strip().lower()
            if reponse == 'o':
                list_adj[i].append(j)
                list_adj[j].append(i)
                
    return ues, salles, list_adj

# ============================================
# 7. PROGRAMME PRINCIPAL
# ============================================

if __name__ == "__main__":
    print("🎓 BIENVENUE DANS LE SYSTÈME DE PLANIFICATION D'EXAMENS PAR GRAPHES")
    print("=" * 70)
    
    # 1. Saisie des données par l'utilisateur
    ues, salles_disponibles, list_adj = saisir_donnees()
    
    # 2. Statistiques de base sur le graphe créé
    print("\n📊 STATISTIQUES DU GRAPHE DE CONFLITS :")
    print(f"   • Nombre total de sommets (UE) : {len(ues)}")
    nb_aretes = sum(len(voisins) for voisins in list_adj.values()) // 2
    print(f"   • Nombre total d'arêtes (Conflits) : {nb_aretes}")
    for i, ue in enumerate(ues):
        print(f"     - Degré de {ue.code} : {len(list_adj[i])}")
        
    # 3. Choix et Exécution de l'algorithme de coloration
    print("\n🔍 Quel algorithme de coloration souhaitez-vous appliquer ?")
    print("   1. DSATUR")
    print("   2. Welsh-Powell")
    choix = input("Votre choix (1 ou 2) : ").strip()
    
    if choix == "2":
        print("\n⚡ Exécution de l'algorithme Welsh-Powell...")
        coloration = welsh_powell(ues, list_adj)
    else:
        print("\n⚡ Exécution de l'algorithme DSATUR...")
        coloration = dsatur(ues, list_adj)
        
    # 4. Attribution des salles
    planning_salles = attribuer_salles(coloration, ues, salles_disponibles)
    
    # 5. Affichage du planning final textuel
    print("\n" + "="*80)
    print("📋 PLANNING DES ÉVALUATIONS GÉNÉRÉ".center(80))
    print("="*80)
    print(f"{'Code UE':<12} | {'Niveau':<8} | {'Effectif':<10} | {'Type':<10} | {'Créneau':<10} | {'Salle Affectée':<20}")
    print("-" * 80)
    
    planning_trie = sorted(coloration.items(), key=lambda x: x[1])
    for u, creneau in planning_trie:
        ue = ues[u]
        salle = planning_salles[u]
        print(f"{ue.code:<12} | {ue.niveau:<8} | {ue.effectif:<10} | {ue.type_salle:<10} | Créneau {creneau:<2} | {salle:<20}")
    print("="*80)
    
    # 6. Exportation automatique en CSV
    exporter_planning_csv(ues, coloration, planning_salles)
    
    # 7. Affichage visuel du Graphe
    afficher_graphe(ues, list_adj, coloration)