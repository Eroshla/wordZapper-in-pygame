import pygame
import random
import os
import sys
import string
from pygame.locals import *

# Initialize Pygame
pygame.init()
pygame.font.init()
pygame.mixer.pre_init(44100, 32, 2, 4096)

screen_height = 546
screen_width = 448

pixel_size = 30
white = (255, 255, 255)

font_name = pygame.font.get_default_font()
game_font = pygame.font.SysFont(font_name, 72)
info_font = pygame.font.SysFont(font_name, 24)
menu_font = pygame.font.SysFont(font_name, 36)

# Initialize the display/screen
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Your Game Title")

# Get the current working directory
current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

file_path = os.path.join(current_dir, "wordzapper.txt")
with open(file_path, "r") as file:
    words = file.read().splitlines()


def choose_word():
    word = random.choice(words).lower().strip()
    print(word)
    return word


# Navigate to the folder where the images are located
images_dir = os.path.join(current_dir, "images")

# Navigate to the folder where the sounds are located
sounds_dir = os.path.join(current_dir, "sounds")

# Navigate to the folder where the letters are located
letters_dir = os.path.join(current_dir, "letters")

# Complete paths for the images
background_filename = os.path.join(images_dir, 'bg.png')
zap_filename = os.path.join(images_dir, 'zap_up.png')
meteor_filename = os.path.join(images_dir, 'meteor.png')
fireball_filename = os.path.join(images_dir, 'fireball.png')

# Complete paths for the sound effects
hit_sound_filename = os.path.join(sounds_dir, 'boom.wav')
success_sound_filename = os.path.join(sounds_dir, 'success.wav')
music_sound_filename = os.path.join(sounds_dir, 'MUSIC.mp3')

# Load the images
background = pygame.image.load(background_filename).convert()
zap_sprite = pygame.image.load(zap_filename).convert_alpha()
meteor_sprite = pygame.image.load(meteor_filename).convert_alpha()
fireball_sprite = pygame.image.load(fireball_filename).convert_alpha()

# load the sounds 
pygame.mixer.init()
hit_sound = pygame.mixer.Sound(hit_sound_filename)
trilha_sound = pygame.mixer.Sound(music_sound_filename)

class Zap(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = zap_sprite  # Set the player's image to the zap sprite
        self.rect = self.image.get_rect()
        self.lifes = 3

    def update(self, dx, dy):
        # Calculate the new position of the player
        new_x = self.rect.x + dx
        new_y = self.rect.y + dy

        # Check if the position is within the screen boundaries
        if new_x < 0:
            new_x = 0
        elif new_x > screen_width:
            new_x = screen_width

        # Restrict the player's movement to the top of the screen
        if new_y < 200:
            new_y = 200
        elif new_y > screen_height:
            new_y = screen_height

        # Update the player's position
        self.rect.x = new_x
        self.rect.y = new_y

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        pygame.sprite.Sprite.__init__(self)
        self.image = meteor_sprite  # Set the enemy's image to the meteor sprite
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = speed

    def update(self):
        # Move the enemy left or right
        self.rect.x += self.speed

        # Check if the enemy has left the screen
        if self.rect.right < 0 or self.rect.left > screen_width:
            self.kill()  # Delete the enemy when it goes off the screen


class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = fireball_sprite  # Set the projectile's image to the fireball sprite
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = -15

    def update(self):
        self.rect.y += self.speed

        # Check if the projectile has left the screen
        if self.rect.bottom <= 0:
            self.kill()  # Delete the projectile when it goes out of the screen


class CensoredWord:
    def __init__(self, word):
        self.original_word = word
        self.word = word
        self.censored = "_" * len(word)

    def censor_word(self):
        self.censored = "_" * len(self.word)

    def guess_letter(self, letter):
        censored_list = list(self.censored)
        for i in range(len(self.word)):
            if self.word[i] == letter or self.original_word[i] == letter:
                censored_list[i] = self.word[i]
                print("test")
        self.censored = "".join(censored_list)

    def is_word_guessed(self):
        return "_" not in self.censored




class Alphabet(pygame.sprite.Sprite):
    def __init__(self, x, speed, letter, censored_word):
        pygame.sprite.Sprite.__init__(self)
        self.letter = letter
        self.censored_word = censored_word
        self.image = pygame.Surface((100, 100))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = 90
        self.speed = speed

    def update(self):
        self.rect.x += self.speed
        if self.rect.right < 0:
            self.kill()

    def hit_letter(self):
        self.censored_word.guess_letter(self.letter)


censored_word = CensoredWord(choose_word())

pygame.init()

# Game screen setup
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Zap")

# Create the player
zap = Zap()

# Create a sprite group for enemies
enemy_group = pygame.sprite.Group()

# Create a sprite group for projectiles
projectile_group = pygame.sprite.Group()

# Create a sprite group for the alphabet
alphabet_group = pygame.sprite.Group()

# Main game loop
running = True
clock = pygame.time.Clock()
remaining_time = 99  # Initial time in seconds
font = pygame.font.Font(None, 100)  # Font for the time text

def decrement_time():
    global remaining_time
    remaining_time -= 1

# Create an event every 1 second to decrement the time
pygame.time.set_timer(pygame.USEREVENT, 1000)

# List with the letters of the alphabet in alphabetical order
alphabet_letters = list(string.ascii_uppercase)

# Variables to control the generation of alphabet letters
generated_letters = 0
max_letters = 26
letter_generation_time = 200  # 1 second in milliseconds
last_generation_time = 0

trilha_sound.play(-1)
text_info = menu_font.render(('Press any button to start!'),1,(255,255,255))
text_info2 = menu_font.render(('Press Space button to shoot'),1,(255,255,255))

gameInit = 0
while gameInit == 0:
    for event in pygame.event.get():
        if event.type == QUIT:
            exit()
        if event.type == KEYDOWN:
            gameInit = 1

    screen.blit(background, (0, 0))
    screen.blit(text_info,(80,250))
    screen.blit(text_info2,(50,300))
    pygame.display.update()

while True:
    gameInit = 1
    while remaining_time > 0 and (zap.lifes > 0 and "_" in censored_word.censored):
            # Event handling
            for event in pygame.event.get():
                if event.type == QUIT:
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        projectile = Projectile(zap.rect.centerx, zap.rect.top)
                        projectile_group.add(projectile)
                elif event.type == pygame.USEREVENT:
                    decrement_time()

            # Zap movement
            keys = pygame.key.get_pressed()
            dx = 0
            dy = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx -= 5
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx += 5
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy -= 5
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy += 5

            # Update zap position
            zap.update(dx, dy)

            # Prevent zap from going off the screen edges
            if zap.rect.left < 0:
                zap.rect.left = 0
            elif zap.rect.right > screen_width:
                zap.rect.right = screen_width
            if zap.rect.top < 200:  # Restrict zap movement at the top of the screen
                zap.rect.top = 200
            elif zap.rect.bottom > screen_height:
                zap.rect.bottom = screen_height

            # Create new enemies on the screen
            if len(enemy_group) < 10:
                if random.random() < 0.01:
                    x = random.choice([0, screen_width])
                    y = random.randint(200, screen_height)
                    if x == 0:  # Enemy on the left side
                        speed = random.uniform(1.0, 5.0)
                    else:  # Enemy on the right side
                        speed = random.uniform(-5.0, -1.0)
                    enemy = Enemy(x, y, speed)
                    enemy_group.add(enemy)

            # Generate new alphabet letters on the screen
            current_time = pygame.time.get_ticks()
            if generated_letters < max_letters and current_time - last_generation_time >= letter_generation_time:
                x = screen_width
                speed = -7.0
                letter = alphabet_letters[generated_letters % len(alphabet_letters)]  # Get the letter based on the number of generated letters using the modulo operator
                alphabet_object = Alphabet(x, speed, letter, censored_word)
                alphabet_group.add(alphabet_object)
                generated_letters += 1
                last_generation_time = current_time


            if generated_letters < max_letters and current_time - last_generation_time >= letter_generation_time:
                x = screen_width
                speed = -7.0
                letter = alphabet_letters[generated_letters % len(alphabet_letters)]
                alphabet_object = Alphabet(x, speed, letter, censored_word)
                alphabet_group.add(alphabet_object)
                generated_letters += 1
                last_generation_time = current_time
            # Check if all letters have been generated and reset the count
            if generated_letters == max_letters:
                generated_letters = 0

            # Check collision between zap and enemies
            if pygame.sprite.spritecollide(zap, enemy_group, True):
                zap.lifes -= 1  # Reduce remaining life by 1 upon collision

            # Check collision between projectiles and enemies
            projectile_enemy_collisions = pygame.sprite.groupcollide(projectile_group, enemy_group, True, True)

            # Check collision between projectiles and alphabet objects
            projectile_alphabet_collisions = pygame.sprite.groupcollide(projectile_group, alphabet_group, True, True)
            for projectile, hit_letters in projectile_alphabet_collisions.items():
                for letter in hit_letters:
                    letter_value = letter.letter.lower()
                    censored_word.guess_letter(letter_value)
                    print("Collided with the letter", letter_value)

            # Update projectiles
            projectile_group.update()

            # Update enemies
            enemy_group.update()

            # Update alphabet objects
            alphabet_group.update()

            # Draw the background on the screen
            screen.blit(background, (0, 0))

            # Draw the zap on the screen
            screen.blit(zap.image, zap.rect)

            # Draw the enemies on the screen
            for enemy in enemy_group:
                screen.blit(enemy.image, enemy.rect)

            for projectile in projectile_group:
                screen.blit(projectile.image, projectile.rect)

            # Draw the alphabet objects on the screen
            for alphabet_object in alphabet_group:
                letter_text = font.render(alphabet_object.letter, True, white)
                screen.blit(letter_text, alphabet_object.rect)

            # Draw the life and time on the screen
            text_info = info_font.render(('Time: {0}           Lifes: {1}'.format(remaining_time,zap.lifes)),1,(255,255,255))
            screen.blit(text_info, (10, 10))

            if remaining_time >= 95:
                censored_word_text = game_font.render(censored_word.original_word, True, white)
                screen.blit(censored_word_text, (255, 500))

            censored_word_text = font.render(censored_word.censored, True, white)
            screen.blit(censored_word_text, (225, 15))

                
            # Update the screen
            pygame.display.update()

            # Inside the main game loop, after updating the screen
            censored_word_text = font.render(censored_word.censored, True, white)
            screen.blit(censored_word_text, (10, 150))

            life_text = font.render(('Lifes: {0}'.format(zap.lifes)), 1, (255, 255, 255))
            screen.blit(life_text, (10, 15))

            # Limit the frame rate of the game
            clock.tick(60)
        
    while gameInit == 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            if event.type == KEYDOWN:
                gameInit = 0
                censored_word.censor_word()
                Zap.lifes = 3
                remaining_time = 99
                censored_word = CensoredWord(choose_word())
        screen.blit(background, (0, 0))
        text = game_font.render('GAME OVER', 1, (255, 0, 0))
        text_reiniciar = info_font.render('Press any button to restart!',1,(255,255,255))
        screen.blit(text, (75, 120))
        screen.blit(text_reiniciar,(70,250))
        pygame.display.update() 

