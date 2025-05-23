from vpython import vector, sphere, rate, color, canvas, mag, norm, box
import random

# --- Paramètres de simulation ---
NUM_BOIDS = 50       # nombre de boids simulés
WIDTH = 200          # demi-largeur du cube
HEIGHT = 200         # demi-hauteur
DEPTH = 200          # demi-profondeur
MAX_SPEED = 2        # vitesse maximale autorisée
MAX_FORCE = 0.05     # force maximale de correction (accélération)
RADIUS = 40          # rayon d’influence de chaque boid

# --- Initialisation de la scène 3D ---
scene = canvas(
        title="Simulation 3D du vol des étourneaux",
        width=800,
        height=600,
        center=vector(0, 0, 0),
        background=vector(0.6, 0.8, 1) # bleu clair
    )

border = box(               # Cube de repère transparent (limites de vol)
    pos=vector(0, 0, 0),
    length=WIDTH * 2,
    height=HEIGHT * 2,
    width=DEPTH * 2,
    opacity=0.2,
    color=color.white
)
scene.forward = vector(-1, -1, -1) # Donne à la caméra une vue isométrique

# --- Classe Boid 3D ---
class Boid3D:
    def __init__(self):
        # position initiale aléatoire dans le cube
        self.position = vector(
            random.uniform(-WIDTH, WIDTH),
            random.uniform(-HEIGHT, HEIGHT),
            random.uniform(-DEPTH, DEPTH)
        )
        # vitesse initiale aléatoire normalisée
        velocity = vector(
            random.uniform(-1, 1),
            random.uniform(-1, 1),
            random.uniform(-1, 1)
        )
        self.velocity = norm(velocity) * MAX_SPEED  # vitesse initiale normalisée avec la vitesse maximale
        self.acceleration = vector(0, 0, 0)         # accélération initiale
        self.body = sphere(pos=self.position, radius=1.5, color=vector(1, 0.5, 0))  # sphère orange qui représente le boid

    def update(self):
        # Met à jour la position du boid en fonction de sa vitesse et de son accélération
        self.velocity += self.acceleration                  # applique les forces
        if mag(self.velocity) > MAX_SPEED:                  # limite la vitesse
            self.velocity = norm(self.velocity) * MAX_SPEED
        self.position += self.velocity                      # met à jour la position
        self.edges()                                        # permet de rebondir sur les bords du cube
        self.body.pos = self.position                       # met à jour la position de la sphère
        self.acceleration = vector(0, 0, 0)                 # réinitialise l'accélération

    def edges(self):
        # Inverse la direction si on dépasse les limites du cube
        if self.position.x > WIDTH or self.position.x < -WIDTH:
            self.velocity.x *= -1
        if self.position.y > HEIGHT or self.position.y < -HEIGHT:
            self.velocity.y *= -1
        if self.position.z > DEPTH or self.position.z < -DEPTH:
            self.velocity.z *= -1


    def apply_force(self, force):
        # accumule les forces
        self.acceleration += force

    # --- Les 3 comportements de base : alignement, cohésion et séparation ---
    # Ces comportement sont les mêmes que dans le code 2D, mais adaptés pour la 3D
    # Avec :
    # pygame.Vector2(x, y) --> vpython.vector(x, y, z)
    # .distance_to()       --> mag()
    # .normalize()        --> norm()
    # .rotate()           --> pas nécessaire
    # .angle_to()         --> pas nécessaire
    # Les commentaire detaillés sont dans le code 2D

    def align(self, boids):
        # Aligne la direction du boid avec celle de ses voisins
        steering = vector(0, 0, 0)
        total = 0
        for other in boids:
            if other != self and mag(other.position - self.position) < RADIUS:
                steering += other.velocity
                total += 1
        if total > 0:
            steering /= total
            steering = norm(steering) * MAX_SPEED
            steering -= self.velocity
            if mag(steering) > MAX_FORCE:
                steering = norm(steering) * MAX_FORCE
        return steering

    def cohesion(self, boids):
        # Fait en sorte que le boid se rapproche du centre de ses voisins
        steering = vector(0, 0, 0)
        total = 0
        center = vector(0, 0, 0)
        for other in boids:
            if other != self and mag(other.position - self.position) < RADIUS:
                center += other.position
                total += 1
        if total > 0:
            center /= total
            direction = center - self.position
            direction = norm(direction) * MAX_SPEED
            steering = direction - self.velocity
            if mag(steering) > MAX_FORCE:
                steering = norm(steering) * MAX_FORCE
        return steering

    def separation(self, boids):
        # Évite que le boid ne se rapproche trop de ses voisins
        steering = vector(0, 0, 0)
        total = 0
        for other in boids:
            distance = mag(self.position - other.position)
            if other != self and distance < RADIUS / 2:
                diff = self.position - other.position
                if distance > 0:
                    diff /= distance
                steering += diff
                total += 1
        if total > 0:
            steering /= total
            if mag(steering) > 0:
                steering = norm(steering) * MAX_SPEED
                steering -= self.velocity
                if mag(steering) > MAX_FORCE:
                    steering = norm(steering) * MAX_FORCE
        return steering

    def flock(self, boids):
        # Applique les forces d'alignement, de cohésion et de séparation
        alignment = self.align(boids)
        cohesion = self.cohesion(boids)
        separation = self.separation(boids)
        self.apply_force(alignment * 1.0)
        self.apply_force(cohesion * 0.8)
        self.apply_force(separation * 1.5)

# --- Création de la liste des boids ---
boids = [Boid3D() for _ in range(NUM_BOIDS)]

# --- Boucle principale de simulation ---
while True:
    rate(60)  # 60 FPS
    for boid in boids:
        boid.flock(boids)   # applique les forces de vol
        boid.update()       # met à jour la position
