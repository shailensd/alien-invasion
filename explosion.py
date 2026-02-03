import pygame
from pygame.sprite import Sprite
import random
import math

class Explosion(Sprite):
    """A class to create explosion particle effects"""
    
    def __init__(self, ai_game, x, y):
        """Create an explosion at the given position"""
        super().__init__()
        self.screen = ai_game.screen
        self.particles = []
        
        # Create particles radiating outward
        particle_count = 8
        for _ in range(particle_count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            self.particles.append({
                'x': float(x),
                'y': float(y),
                'vx': speed * math.cos(angle),
                'vy': speed * math.sin(angle),
                'life': random.randint(8, 15),
                'max_life': random.randint(8, 15),
                'size': random.randint(3, 6)
            })
    
    def update(self):
        """Update particle positions and lifetimes"""
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            
            # Remove dead particles
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def draw(self):
        """Draw all particles"""
        for particle in self.particles:
            if particle['life'] > 0:
                # Fade out as particle dies
                life_ratio = particle['life'] / particle['max_life']
                
                # Color transitions from yellow/orange to red
                if life_ratio > 0.6:
                    color = (255, 200, 0)  # Yellow
                elif life_ratio > 0.3:
                    color = (255, 150, 0)  # Orange
                else:
                    color = (255, 100, 0)  # Red-orange
                
                # Size decreases as particle dies
                size = int(particle['size'] * life_ratio)
                if size > 0:
                    pygame.draw.circle(self.screen, color, 
                                     (int(particle['x']), int(particle['y'])), size)
    
    def is_alive(self):
        """Check if explosion still has particles"""
        return len(self.particles) > 0
