# Improvement Ideas:
# - Fire flickers randomly. Both in brightness and direction of the flames.


import random

import pygame

from src import base
from src.helpers import linear_map, EventTimer


BACKGROUND_COLOR = pygame.Color(0, 0, 32)
TRANSPARENT_BLACK = pygame.Color(0, 0, 0, 0)
PARTICLE_COLOR = pygame.Color(226, 88, 34)
PARTICLE_DIAMETER = 51
PARTICLES_PER_SECOND = 250
LIFETIME_MEAN = 1  # seconds
LIFETIME_SD = 0.1
# Time in seconds it takes for a particle to vanish. The particles start
# vanishing at lifetime - vanish_duration and die when time >= lifetime.
VANISH_DURATION = 0.5
SPEED_MEAN = 100  # pixels per second
SPEED_SD = 25
# Strictly speaking those are not forces but accelerations. Here it
# doesn't matter because all particles have the same mass.
FORCES = (
    pygame.Vector2(0, -400),  # updraft
)
TOTAL_FORCE = sum(FORCES, pygame.Vector2())
EMISSION_EVENT_ID = pygame.event.custom_type()


class Emitter(base.Emitter):
    def __init__(self):
        self.particles = []
        self.position = pygame.Vector2()
        self.time_since_last_emission = 0
        self.is_emitting = False
        self.emission_timer = EventTimer(EMISSION_EVENT_ID, 1 / PARTICLES_PER_SECOND)
        self.fire_surface = pygame.Surface(pygame.display.get_window_size(), flags=pygame.SRCALPHA)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.is_emitting = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_emitting = False
        elif event.type == EMISSION_EVENT_ID and self.is_emitting:
            self.particles.append(Particle(self.position))

    def update(self, dt):
        self.emission_timer.update(dt)
        self.position.update(pygame.mouse.get_pos())
        force_dt = TOTAL_FORCE * dt
        force_dt_half = force_dt / 2
        alive_particles = []
        for p in self.particles:
            if p.alive:
                alive_particles.append(p)
                p.update(dt, force_dt, force_dt_half)
        self.particles = alive_particles

    def draw(self, target_surace):
        self.fire_surface.fill(TRANSPARENT_BLACK)
        for p in self.particles:
            self.fire_surface.blit(p.image, p.position, special_flags=pygame.BLEND_RGBA_ADD)
        target_surace.fill(BACKGROUND_COLOR)
        if not self.is_emitting:
            pygame.draw.circle(target_surace, PARTICLE_COLOR, self.position, 3, 1)
        target_surace.blit(self.fire_surface, (0, 0))


def make_particle_images():
    base_image = pygame.Surface((PARTICLE_DIAMETER, PARTICLE_DIAMETER), flags=pygame.SRCALPHA)
    max_distance = (PARTICLE_DIAMETER - 1) / 2
    center = pygame.Vector2(max_distance)
    for x in range(PARTICLE_DIAMETER):
        for y in range(PARTICLE_DIAMETER):
            # linear interpolation (not how real light behaves)
            position = (x, y)
            distance = center.distance_to(position)
            ratio = min(distance / max_distance, 1)
            color = PARTICLE_COLOR.lerp(TRANSPARENT_BLACK, ratio)
            base_image.set_at(position, color)

    # Generate a list of images with varying transparency. Pygame doesn't let me mix
    # per pixel alpha and surface alpha so I have to blit a semitransparent layer
    # on the base image to achieve this effect.
    # The index corresponsds to the transparency where 0 is transparent and 255 is opaque.
    images = []
    transparent_layer = pygame.Surface(base_image.get_size(), flags=pygame.SRCALPHA)
    for alpha in range(255, -1, -1):
        image = base_image.copy()
        transparent_layer.fill((0, 0, 0, alpha))
        image.blit(transparent_layer, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
        images.append(image)

    return images


class Particle(base.Particle):
    images = make_particle_images()

    def __init__(self, position):
        self.position = pygame.Vector2(position)
        self.position = self.position.elementwise() - PARTICLE_DIAMETER // 2  # center the image
        self.velocity = pygame.Vector2(random.gauss(SPEED_MEAN, SPEED_SD), 0)
        self.velocity.rotate_ip(random.uniform(0, 360))
        self.image = Particle.images[-1]
        self.time = 0
        self.lifetime_limit = random.gauss(LIFETIME_MEAN, LIFETIME_SD)
        self.vanish_start_time = self.lifetime_limit - VANISH_DURATION
        self.alive = True

    def update(self, dt, force_dt, force_dt_half):
        self.time += dt
        if self.time >= self.vanish_start_time:
            if self.time >= self.lifetime_limit:
                self.alive = False
                return
            alpha = linear_map(
                self.time,
                self.vanish_start_time, self.lifetime_limit,
                255, 0
            )
            self.image = Particle.images[int(alpha)]
        self.velocity += force_dt
        self.position += (self.velocity - force_dt_half) * dt
