import sys
import pygame
from time import sleep

from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from game_stats import GameStats
from button import Button
from scoreboard import Scoreboard

class AlienInvasion:
    """Overall class to manage game assets and behavior. """
    def __init__(self):
        """Initialize the game, and create game resources."""
        pygame.init()
        self.clock = pygame.time.Clock()
        self.settings = Settings()
        # self.screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
        self.screen = pygame.display.set_mode((self.settings.screen_width,
                                               self.settings.screen_height))
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion")
        
        # Create an instance to store game statistics,
        # and create a scoreboard
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        
        self._create_fleet()
        
        # Start Alien Invasion in an inactive state.
        self.game_active = False
        
        # Make the Play Button
        self.play_button = Button(self, "Play")
        
    def run_game(self):
        """Start the main loop for the game."""
        while True:
            # Watch for keyboard and mouse events.
            self._check_events()
            if self.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
            self._update_screen()
            self.clock.tick(60)
            
    def _update_bullets(self):
        """Update bullet positions and get rid of old bullets."""
        self.bullets.update()
            
        # Get rid of the bullets that have disappeared
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        # Verify the number of bullets being decreased
        # print(len(self.bullets))
        self._check_bullet_alien_collision()
        
    def _check_bullet_alien_collision(self):
        """Respond to the bullet-alien collisions."""
        # Remove any bullets and aliens that have collided.
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, True)
        if not self.aliens:
            # Destroy exiting bullets and create a new fleet.
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()
    
    def _update_aliens(self):
        """Check if the fleet is at an adge and Update the positions of 
        all aliens in the fleet."""
        self._check_fleet_edges()
        self.aliens.update()
        
        # Look for alien-ship collisions.
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
        # Look for aliens hitting the bottom of the screen
        self._check_alien_bottom()
            
    def _check_events(self):
        """Respond to keypresses and mouse events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
                
    def _check_play_button(self, mouse_pos):
        """Start a new game when the player clicks Play"""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            # Reset the game settings.
            self.settings.initialize_dynamic_settings()
            
            # Reset the game statistics
            self.stats.reset_stats()
            self.game_active = True
            
            # Get rid of any remaining bullets and aliens.
            self.bullets.empty()
            self.aliens.empty()
            
            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()
            
            # Hide the mouse cursor
            pygame.mouse.set_visible(False)
            
    
    def _check_keydown_events(self,event):
        """Respond to keypresses."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self.fire_bullet()
            
    def _check_keyup_events(self,event):
        """Respond to key releases"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
            
    def fire_bullet(self):
        """Create a new bullet and add it to the bullets group."""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _create_fleet(self):
        """Create the fleet of aliens"""
        # Create an alien and keep adding aliens until there is no room left.
        # Spacing between aliens is one alien width and one alien height
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        
        current_x, current_y = alien_width, alien_height
        while current_y < (self.settings.screen_height -3* alien_height):
            while current_x < (self.settings.screen_width- 2* alien_width):
                self._create_alien(current_x, current_y)
                current_x += 2*alien_width
            # Finished a row; reset x value and increment y value
            current_x = alien_width
            current_y += 2* alien_height
                        
    def _create_alien(self, x_position, y_position):
        """Create an alien and place it in the row."""
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)
        
    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break
            
    def _change_fleet_direction(self):
        """Drop the entire fleet and change the direction of the fleet."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1
        
    def _ship_hit(self):
        """Respond to the ship being hit by an alien."""
        if self.stats.ship_left > 0:
            # Decrement ships left.
            self.stats.ship_left -=1
        
            # Get rid of any remaining bullets and aliens.
            self.bullets.empty()
            self.aliens.empty()
        
            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()
        
            # Pause
            sleep(0.5)
        else: 
            self.game_active = False
            pygame.mouse.set_visible(True)
            
    def _check_alien_bottom(self):
        """Check if any aliens have reached the bottom of the screen"""
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                # Treat this same as the ship got hiy
                self.ship_hit()
                break
                    
        
    def _update_screen(self):
        """Update images on the screen, and flip to the new screen"""
        # Redraw the screen during each pass through the loop.
        self.screen.fill(self.settings.bg_color)
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.ship.blitme()
        self.aliens.draw(self.screen)
        
        # Draw the score information
        self.sb.show_score()
        
        #Draw the play button if the game is inactive
        if not self.game_active:
            self.play_button.draw_button()
            
        # Make the most recently drawn screen visible.
        pygame.display.flip()

# Only run the following code, if file is being run directly
if __name__ == '__main__':
    # Make a game instance and run the game.
    ai = AlienInvasion()
    ai.run_game()    
        