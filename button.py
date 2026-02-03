import pygame.font

class Button:
    """A class to build buttons for the game"""
    
    def __init__(self, ai_game, msg):
        """Initialize the button attribute"""
        self.screen = ai_game.screen
        self.screen_rect = self.screen. get_rect()
        
        # Set the dimensions and properties of the button
        self.width, self.height = 200, 50
        self.button_color = (50, 150, 255)  # Bright blue
        self.hover_color = (100, 200, 255)  # Lighter blue on hover
        self.border_color = (255, 255, 255)  # White border
        self.text_color = (255, 255, 255)
        self.font = pygame.font.SysFont(None, 48)
        self.is_hovered = False
        
        # Build the button's rect object and center it
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = self.screen_rect.center
        
        # The button message needs to be prepped only once.
        self._prep_msg(msg)
    
    def _prep_msg(self, msg):
        """Turn msg into a rendered image and center text on the bottom."""
        self.msg_image = self.font.render(msg, True, self.text_color, 
                                          self.button_color)
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center
    
    def draw_button(self):
        """Draw button with hover effect and modern styling"""
        # Check if mouse is hovering
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        # Choose color based on hover state
        current_color = self.hover_color if self.is_hovered else self.button_color
        
        # Draw button (try rounded corners, fallback to regular if not supported)
        try:
            pygame.draw.rect(self.screen, current_color, self.rect, border_radius=10)
            # Draw border
            pygame.draw.rect(self.screen, self.border_color, self.rect, width=3, border_radius=10)
        except TypeError:
            # Fallback for older pygame versions
            pygame.draw.rect(self.screen, current_color, self.rect)
            # Draw border manually
            pygame.draw.rect(self.screen, self.border_color, self.rect, 3)
        
        # Draw text
        self.screen.blit(self.msg_image, self.msg_image_rect)