# Simulation du Vol des Étourneaux (Modèle Boids)

Ce projet propose deux simulations du comportement collectif des étourneaux en utilisant le modèle **Boids** de Craig Reynolds.

* **2D avec Pygame** : Boids représentés par des triangles, interaction avec un obstacle fixe et un prédateur contrôlé au clavier.
* **3D avec VPython** : Boids représentés par des sphères orange dans un cube transparent, rebondissant sur les parois.

---

## Fichiers

* `boids_simulation_2D.py` : Simulation en 2D avec Pygame.
* `boids_simulation_3D.py` : Simulation en 3D avec VPython.

---

## Dépendances

### Simulation 2D

* Python 3.x
* Pygame

  ```bash
  pip install pygame
  ```

### Simulation 3D

* Python 3.x
* VPython

  ```bash
  pip install vpython
  ```

---

## Lancer les simulations

### 2D

```bash
python boids_simulation_2D.py
```

* Contrôlez le prédateur avec les flèches du clavier ou `ZQSD`.

### 3D

```bash
python boids_simulation_3D.py
```

* La caméra peut être orientée à la souris.

---

## Auteur

* **Lucas MOUSSAOUI**
* TP dirigé par **M. TORRES** – 2025

---

*Le rapport PDF et le code commenté sont disponibles avec ce projet.*
