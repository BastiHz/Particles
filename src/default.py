import random

import pygame

from src import base
from src.helpers import EventTimer


BACKGROUND_COLOR = pygame.Color(0, 0, 32)
PARTICLE_COLOR = pygame.Color("#e25822")
PARTICLE_RADIUS = 5
PARTICLES_PER_SECOND = 1000
LIFETIME_MEAN = 1  # seconds
LIFETIME_SD = 0.25
SPEED_MEAN = 100  # pixels per second
SPEED_SD = 25
# Strictly speaking those are not forces but accelerations. Here it
# doesn't matter because all particles have the same mass.
FORCES = (
    pygame.Vector2(0, 500),  # gravity
    pygame.Vector2(300, 0),  # wind
)
# No need to iterate over all forces every frame if I can just use the sum.
TOTAL_FORCE = sum(FORCES, pygame.Vector2())
EMISSION_EVENT_ID = pygame.event.custom_type()


class Emitter(base.Emitter):
    def __init__(self):
        self.particles = []
        self.position = pygame.Vector2()
        self.time_since_last_emission = 0
        self.is_emitting = False
        self.emission_timer = EventTimer(EMISSION_EVENT_ID, 1 / PARTICLES_PER_SECOND)

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
        # Remove old particles before updating the rest, otherwise they live
        # one frame less than intended.
        self.particles = [p for p in self.particles if p.lifetime < p.lifetime_limit]
        force_dt = TOTAL_FORCE * dt
        for p in self.particles:
            p.update(dt, force_dt)

    def draw(self, target_surace):
        target_surace.fill(BACKGROUND_COLOR)
        if not self.is_emitting:
            pygame.draw.circle(target_surace, PARTICLE_COLOR, self.position, 3, 1)
        for p in self.particles:
            pygame.draw.circle(target_surace, PARTICLE_COLOR, p.position, PARTICLE_RADIUS)


class Particle(base.Particle):
    def __init__(self, position):
        self.position = pygame.Vector2(position)
        self.velocity = pygame.Vector2(random.gauss(SPEED_MEAN, SPEED_SD), 0)
        self.velocity.rotate_ip(random.uniform(0, 360))
        self.lifetime = 0
        self.lifetime_limit = random.gauss(LIFETIME_MEAN, LIFETIME_SD)

    def update(self, dt, force_dt):
        self.lifetime += dt
        self.velocity += force_dt
        self.position += self.velocity * dt
