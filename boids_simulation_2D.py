import pygame
import random
import math
import sys

# Paramètres modifiables
WIDTH, HEIGHT = 800, 600 # Taille de la fenêtre
NUM_BOIDS = 50 # Nombre de boids
MAX_SPEED = 4 # Vitesse maximale qu’un boid peut atteindre
MAX_FORCE = 0.08 # Force maximale d’ajustement de trajectoire
RADIUS = 50  # Rayon d’influence (distance d’interaction)

# Initialiser pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulation du vol des étourneaux (Boids)")
clock = pygame.time.Clock()

# La classe Boid représente un oiseau dans la simulation
# Chaque boid a une position, une vitesse et une accélération
class Boid:
    def __init__(self):
        # Position aléatoire dans la fenêtre
        self.position = pygame.Vector2(random.uniform(0, WIDTH), random.uniform(0, HEIGHT))
        # Angle aléatoire
        angle = random.uniform(0, 2 * math.pi) 
        # Vitesse initiale aléatoire
        self.velocity = pygame.Vector2(math.cos(angle), math.sin(angle)) * MAX_SPEED
        # Avec accélération nulle
        self.acceleration = pygame.Vector2(0, 0)

    def update(self):
        self.velocity += self.acceleration          # On applique l’accélération à la vitesse
        if self.velocity.length() > MAX_SPEED:      # On limite la vitesse (évite que le boid "déraille")
            self.velocity.scale_to_length(MAX_SPEED)
        self.position += self.velocity              # On déplace le boid selon la vitesse. 
        self.acceleration *= 0                      #On remet l'accélération à zéro (elle est recalculée à chaque frame)
        self.edges()                                # On vérifie si le boid est sorti de l'écran et on le remet de l'autre côté

    def edges(self):
        # Quand un boid sort de l’écran, il réapparaît de l’autre côté (effet "wrap")
        if self.position.x > WIDTH:
            self.position.x = 0
        elif self.position.x < 0:
            self.position.x = WIDTH
        if self.position.y > HEIGHT:
            self.position.y = 0
        elif self.position.y < 0:
            self.position.y = HEIGHT

    def draw(self, screen):
        # Cela donne l’angle de rotation du boid en degrés, pour l’orienter dans la bonne direction
        angle = self.velocity.angle_to(pygame.Vector2(1, 0))
        points = [
            # On décale le triangle pour qu’il soit centré sur la position réelle du boid dans l’espace
            # +
            # Ces trois vecteurs définissent un triangle centré autour de (0,0), pointant vers la droite
            # .
            # On fait pivoter chaque point selon l’angle pour que le triangle pointe dans la direction du mouvement du boid
            self.position + pygame.Vector2(10, 0).rotate(-angle),
            self.position + pygame.Vector2(-5, 5).rotate(-angle),
            self.position + pygame.Vector2(-5, -5).rotate(-angle)
        ]
        # On dessine le triangle (blanc) à l’écran, en reliant les 3 points calculés
        pygame.draw.polygon(screen, (255, 255, 255), points)

    ### Les 3 règles du modèle Boids ###

    def align(self, boids):
        steering = pygame.Vector2()     #  le vecteur final à retourner (la "force" à appliquer)
        total = 0                       # combien de voisins on a trouvés    
        avg_vector = pygame.Vector2()   # cumul des vitesses des voisins

        for other in boids: # Pour chaque boid dans la liste
            # On ne prend en compte que les boids qui sont dans le rayon d’influence
            if other != self and self.position.distance_to(other.position) < RADIUS:
                avg_vector += other.velocity    # On additionne les vitesses des voisins
                total += 1                      # On incrémente le nombre de voisins

        if total > 0: # Si il y a au moins un voisin
            avg_vector /= total                             # On fait la moyenne des vitesses
            avg_vector = avg_vector.normalize() * MAX_SPEED # On recupere le vecteur de longueur MAX_SPEED (qui nous montre la direction moyenne du groupe et la meilleure vitesse à adopter)
            steering = avg_vector - self.velocity           # On compares où on veux aller (vitesse cible) avec où on vas déjà, et on obtiens un vecteur d’ajustement (une force de rotation douce)
            if steering.length() > MAX_FORCE:               # On empêches la flèche de correction (changement de direction) de faire tourner trop violemment le boid
                steering.scale_to_length(MAX_FORCE)
        return steering                                     # On retourne la force d’ajustement

    def cohesion(self, boids):
        steering = pygame.Vector2()
        total = 0
        center_mass = pygame.Vector2() # pour additionner les positions des voisins
        for other in boids:
            if other != self and self.position.distance_to(other.position) < RADIUS:
                center_mass += other.position   # On additionne les positions des voisins
                total += 1                      # On incrémente le nombre de voisins
        if total > 0:
            center_mass /= total                        # On fait la moyenne des positions
            desired = center_mass - self.position       # On calcule la direction vers le centre de masse
            desired = desired.normalize() * MAX_SPEED   # On recupere le vecteur de longueur MAX_SPEED (qui nous montre la direction du centre de masse et la meilleure vitesse à adopter)
            steering = desired - self.velocity          # On compares où on veux aller (vitesse cible) avec où on vas déjà, et on obtiens un vecteur d’ajustement (une force de rotation douce)
            if steering.length() > MAX_FORCE:          # On empêches la flèche de correction (changement de direction) de faire tourner trop violemment le boid
                steering.scale_to_length(MAX_FORCE)
        return steering

    def separation(self, boids):
        # Empêcher les boids de se rentrer dedans.
        # Si un voisin est trop proche, on applique une force de répulsion pour s’en éloigner
        steering = pygame.Vector2()
        total = 0
        for other in boids:                                         # Pour chaque boid dans la liste
            distance = self.position.distance_to(other.position)    # On calcule la distance entre le boid et son voisin
            if other != self and distance < RADIUS / 2:             # On ne prend en compte que les boids qui sont dans le rayon d’influence
                diff = self.position - other.position               # difference de position
                if distance > 0:
                    diff /= distance        # Plus la distance est courte, plus on renforce la répulsion (car on divise par une valeur petite)
                steering += diff            # On additionne les vecteurs de répulsion    
                total += 1                  # On incrémente le nombre de voisins
        if total > 0:                                       # Si il y a au moins un voisin    
            steering /= total                               # On fait la moyenne des vecteurs de répulsion
            if steering.length() > 0:                       # On évite le cas ou il se fait pousser symétriquement et produit donc un verteur nul
                steering = steering.normalize() * MAX_SPEED # même principe que pour l’alignement et la cohésion
                steering -= self.velocity
                if steering.length() > MAX_FORCE:
                    steering.scale_to_length(MAX_FORCE)
        return steering

    def flock(self, boids):
        # Calculer les trois forces fondamentales (séparation, alignement, cohésion),
        # les pondérer correctement, puis les appliquer au boid
        alignment = self.align(boids)
        cohesion = self.cohesion(boids)
        separation = self.separation(boids)

        # Pondérer les forces
        self.apply_force(alignment * 1.0) # On maintient le même poids pour l’alignement
        self.apply_force(cohesion * 0.8) # On donne un peu moins d'importance à la cohésion ( moins urgent )
        self.apply_force(separation * 1.5) # On donne plus d'importance à la séparation pour éviter les collisions
        # cela créé donc un seul vecteur d’accélération qui est la somme de toutes les forces appliquées

    def apply_force(self, force):
        # Ajouter une force au boid, en l’accumulant dans son accélération, 
        # qui sera utilisée au prochain update pour modifier la vitesse
        self.acceleration += force

    def avoid_obstacle(self, obstacle_pos, avoid_radius):
        # Éviter un obstacle en appliquant une force de répulsion
        # On mesure la distance entre le boid et le centre de l’obstacle (qui est un cercle)
        distance = self.position.distance_to(obstacle_pos)
        if distance < avoid_radius:
            # Crée un vecteur de répulsion loin de l'obstacle
            diff = self.position - obstacle_pos
            if distance > 0:
                diff /= distance  # plus on est proche, plus on est repoussé
            diff = diff.normalize() * MAX_SPEED # Même que pour les 3 regles de base
            steering = diff - self.velocity
            if steering.length() > MAX_FORCE:
                steering.scale_to_length(MAX_FORCE)
            self.apply_force(steering * 1.5) # On donne plus d'importance à l'évitement de l'obstacle

# Créer les boids
boids = [Boid() for _ in range(NUM_BOIDS)]
# Position de l'obstacle et son rayon
OBSTACLE_POS = pygame.Vector2(WIDTH // 2, HEIGHT // 2)  # position de l'obstacle
OBSTACLE_RADIUS = 40                                    # rayon de l'obstacle
AVOID_RADIUS = 120                                      # distance de sécurité autour de l'obstacle

# Boucle principale
running = True
while running:
    clock.tick(60)          # Limite la boucle à 60 images par seconde (FPS)
    screen.fill((0, 0, 0))  # Fond noir

    for event in pygame.event.get():    # Si l’utilisateur ferme la fenêtre, on arrête la boucle
        if event.type == pygame.QUIT:
            running = False

    for boid in boids:      # Pour chaque boid
        boid.flock(boids)   # On applique les forces de séparation, d’alignement et de cohésion
        boid.avoid_obstacle(OBSTACLE_POS, AVOID_RADIUS) # On applique la force d’évitement de l’obstacle
        boid.update()       # On met à jour la position et la vitesse du boid ( Grace a l'accélération récupérée )
        boid.draw(screen)   # On dessine le boid à l’écran

    pygame.draw.circle(screen, (200, 0, 0), OBSTACLE_POS, OBSTACLE_RADIUS)  # Dessine l'obstacle (rouge)
    pygame.display.flip()   # Affiche à l'écran tout ce qui a été dessiné pendant cette frame (double buffering)

pygame.quit()   # On ferme proprement Pygame
sys.exit()      # On quitte le programme Python
