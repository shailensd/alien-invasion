import pygame
from pygame.sprite import Sprite

class Bullet(Sprite):
    """A class to manage bullet fired from the ship"""
    
    def __init__(self, ai_game):
        """Create a bullet object at the ship's current position"""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.color = self.settings.bullet_color
        
        # Create a bullet rect at (0,0) and then set correct position.
        self.rect = pygame.Rect(0, 0, self.settings.bullet_width,
                                self.settings.bullet_height)
        self.rect.midtop = ai_game.ship.rect.midtop
        
        # Store the bullet's position as a float
        self.y = float(self.rect.y)    
    
    def update(self):
        """Move the bullet up the screen."""
        # Update the exact position of the bullet
        self.y -= self.settings.bullet_speed
        # Update the rect position
        self.rect.y = self.y
        
    def draw_bullet(self):
        """Draw bullet with glow effect."""
        # Draw outer glow (slightly larger, dimmer)
        glow_rect = pygame.Rect(
            self.rect.x - 1, self.rect.y - 1,
            self.rect.width + 2, self.rect.height + 2
        )
        glow_color = (0, 200, 150)  # Dimmer cyan
        pygame.draw.rect(self.screen, glow_color, glow_rect)
        
        # Draw main bullet
        pygame.draw.rect(self.screen, self.color, self.rect)
        
        # Draw bright tip (white highlight)
        tip_rect = pygame.Rect(
            self.rect.x, self.rect.y,
            self.rect.width, 4
        )
        pygame.draw.rect(self.screen, (255, 255, 255), tip_rect)
            
        