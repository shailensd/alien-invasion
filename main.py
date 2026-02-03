import sys
import pygame
import asyncio
from time import sleep

from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from game_stats import GameStats
from button import Button
from scoreboard import Scoreboard
from explosion import Explosion

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
        self.explosions = pygame.sprite.Group()
        
        self._create_fleet()
        
        # Start Alien Invasion in an inactive state.
        self.game_active = False
        
        # Make the Play Button
        self.play_button = Button(self, "Play") 
        # Create starfield for background
        self.stars = []
        self._create_starfield()
        
        # Fonts for title and game over screens
        self.title_font = pygame.font.SysFont(None, 72)
        self.subtitle_font = pygame.font.SysFont(None, 36)
        
    async def run_game(self):
        """Start the main loop for the game."""
        while True:
            # Watch for keyboard and mouse events.
            self._check_events()
            if self.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
                self._update_explosions()
            self._update_screen()
            self.clock.tick(60)
            await asyncio.sleep(0)

            
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
        
        if collisions:
            for aliens in collisions.values():
                for alien in aliens:
                    # Create explosion at alien position
                    explosion = Explosion(self, alien.rect.centerx, alien.rect.centery)
                    self.explosions.add(explosion)
                self.stats.score += self.settings.alien_points
            self.sb.prep_score()
            self.sb.check_high_score()
            
        if not self.aliens:
            # Destroy exiting bullets and create a new fleet.
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()
            
            # Increase level
            self.stats.level += 1
            self.sb.prep_level()
    
    def _update_explosions(self):
        """Update explosion particles"""
        for explosion in self.explosions.copy():
            explosion.update()
            if not explosion.is_alive():
                self.explosions.remove(explosion)
    
    def _update_aliens(self):
        """Check if the fleet is at an adge and Update the positions of 
        all aliens in the fleet."""
        self._check_fleet_edges()
        self.aliens.update()
        
        # Look for alien-ship collisions.
        if pygame.sprite.spritecollideany(self.ship, self.aliens): # type: ignore
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
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()
            
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
        if self.stats.ship_left > 0 :
            # Decrement ships left, and update scoreboard.
            self.stats.ship_left -= 1
            self.sb.prep_ships()
        
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
                # Treat this same as the ship got hit
                self._ship_hit()
                break
    
    def _create_starfield(self):
        """Create a starfield background"""
        import random
        for _ in range(self.settings.star_count):
            x = random.randint(0, self.settings.screen_width)
            y = random.randint(0, self.settings.screen_height)
            brightness = random.randint(100, 255)
            self.stars.append([x, y, brightness])
    
    def _draw_starfield(self):
        """Draw the starfield background"""
        for star in self.stars:
            pygame.draw.circle(self.screen, (star[2], star[2], star[2]), 
                             (star[0], star[1]), 1)
    
    def _draw_title_screen(self):
        """Draw title screen"""
        # Title
        title_text = self.title_font.render("ALIEN INVASION", True, (100, 255, 200))
        title_rect = title_text.get_rect(center=(self.settings.screen_width // 2, 
                                                 self.settings.screen_height // 2 - 100))
        self.screen.blit(title_text, title_rect)
        
        # High score if available
        if self.stats.high_score > 0:
            subtitle_text = self.subtitle_font.render(
                f"High Score: {self.stats.high_score:,}", 
                True, (255, 255, 255))
            subtitle_rect = subtitle_text.get_rect(
                center=(self.settings.screen_width // 2, 
                       self.settings.screen_height // 2 - 30))
            self.screen.blit(subtitle_text, subtitle_rect)
        
        # Instructions
        instruction_text = self.subtitle_font.render(
            "Use ARROWS to move, SPACE to shoot", 
            True, (200, 200, 200))
        instruction_rect = instruction_text.get_rect(
            center=(self.settings.screen_width // 2, 
                   self.settings.screen_height // 2 + 50))
        self.screen.blit(instruction_text, instruction_rect)
    
    def _draw_game_over(self):
        """Draw game over screen"""
        # Game Over text
        game_over_text = self.title_font.render("GAME OVER", True, (255, 100, 100))
        game_over_rect = game_over_text.get_rect(
            center=(self.settings.screen_width // 2, 
                   self.settings.screen_height // 2 - 100))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Final score
        final_score_text = self.subtitle_font.render(
            f"Final Score: {self.stats.score:,}", 
            True, (255, 255, 255))
        final_score_rect = final_score_text.get_rect(
            center=(self.settings.screen_width // 2, 
                   self.settings.screen_height // 2 - 30))
        self.screen.blit(final_score_text, final_score_rect)
        
        # High score if new
        if self.stats.score == self.stats.high_score:
            new_record_text = self.subtitle_font.render(
                "NEW HIGH SCORE!", 
                True, (100, 255, 100))
            new_record_rect = new_record_text.get_rect(
                center=(self.settings.screen_width // 2, 
                       self.settings.screen_height // 2 + 20))
            self.screen.blit(new_record_text, new_record_rect)
        
    def _update_screen(self):
        """Update images on the screen, and flip to the new screen"""
        # Redraw the screen during each pass through the loop.
        self.screen.fill(self.settings.bg_color)
        
        # Draw starfield background
        self._draw_starfield()
        
        # Draw game elements only when game is active
        if self.game_active:
            for bullet in self.bullets.sprites():
                bullet.draw_bullet()
            self.ship.blitme()
            self.aliens.draw(self.screen)
            # Draw explosions
            for explosion in self.explosions:
                explosion.draw()
        
        # Draw the score information
        self.sb.show_score()
        
        # Draw title screen or game over screen if game is inactive
        if not self.game_active:
            if self.stats.ship_left == 0 and self.stats.score > 0:
                # Game Over screen
                self._draw_game_over()
            else:
                # Title screen
                self._draw_title_screen()
            self.play_button.draw_button()
            
        # Make the most recently drawn screen visible.
        pygame.display.flip()

# Only run the following code, if file is being run directly
async def main():
    """Main function to run the game."""
    # Make a game instance and run the game.
    ai = AlienInvasion()
    await ai.run_game()

if __name__ == '__main__':
    # Make a game instance and run the game.
    asyncio.run(main())    
        