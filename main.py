import argparse
import os
import sys

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame.freetype  # imports also pygame

from src.bounce import BounceSimulation
from src.default import DefaultSimulation
from src.fire import FireSimulation
from src.fireballs import FireballSimulation


parser = argparse.ArgumentParser()
parser.add_argument(
    "name",
    nargs="?",
    default="default",
    help="Name of the particle simulation."
)
parser.add_argument(
    "-w",
    "--window-size",
    metavar=("<width>", "<height>"),
    nargs=2,
    type=int,
    default=(1200, 800),
    help="Specify the window width and height in pixels."
)
args = parser.parse_args()

sims = {
    "bounce": BounceSimulation,
    "default": DefaultSimulation,
    "fire": FireSimulation,
    "fireballs": FireballSimulation
}
if args.name not in sims:
    parser.error(f"name must be one of {list(sims.keys())}")
sim_names = sorted(list(sims.keys()))
sim_index = sim_names.index(args.name)

pygame.init()
window = pygame.display.set_mode(args.window_size)
pygame.display.set_caption("Particles")
pygame.mouse.set_visible(False)
clock = pygame.time.Clock()
sim = sims[args.name]()

show_info = True
font = pygame.freetype.SysFont("inconsolate, consolas, monospace", 16)
# invert background color but not the alpha value
font.fgcolor = pygame.Color("white")
line_spacing = pygame.Vector2(0, font.get_sized_height())
text_margin = pygame.Vector2(5, 5)

paused = False

while True:
    dt = clock.tick(60) / 1000  # in seconds

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                sys.exit()
            elif event.key == pygame.K_F1:
                show_info = not show_info
            elif event.key == pygame.K_SPACE:
                paused = not paused
                pygame.mouse.set_visible(paused)
            elif event.key == pygame.K_DELETE:
                sim.clear()
            elif event.key == pygame.K_n:
                # Cycle through the simulations
                sim_index = (sim_index + 1) % len(sim_names)
                sim = sims[sim_names[sim_index]]()

        sim.handle_event(event)

    if not paused:
        sim.update(dt, pygame.mouse.get_pos())

    sim.draw(window)
    if show_info:
        font.render_to(
            window,
            text_margin,
            sim_names[sim_index]
        )
        font.render_to(
            window,
            text_margin + line_spacing,
            f"updates per second: {clock.get_fps():.0f}"
        )
        font.render_to(
            window,
            text_margin + line_spacing * 2,
            f"number of particles: {len(sim.particles)}"
        )
    pygame.display.flip()
