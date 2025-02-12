import pygame
import os
import random
import csv
pygame.init()
SCREEN_WIDTH = 700
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('GAME BẮN SÚNG')

#set framerate
clock = pygame.time.Clock()
FPS = 60

#xac dinh bien
GRAVITY = 0.75	
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
screen_scroll = 0
bg_scroll = 0
level = 1
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

font30=pygame.font.SysFont('Constantia',30)
font40=pygame.font.SysFont('Constantia',40)
countdown=3
last_count=pygame.time.get_ticks()
def draw_text(text,font,text_col,x,y):
	img=font.render(text,True,text_col)
	screen.blit(img,(x,y))

#Music
pygame.mixer.init()
pygame.mixer.music.load("nhạc.mp3")  # Đường dẫn đến file nhạc
pygame.mixer.music.set_volume(0.5)  # Thiết lập âm lượng (0.0 - 1.0)
pygame.mixer.music.play(-1)

#load hinh anh
sky_img = pygame.image.load('img/Background/sky_cloud.png').convert_alpha()

#luu tiles trong mot list
img_list = []
for x in range(TILE_TYPES):
	img = pygame.image.load(f'img/Tile/{x}.png')
	img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
	img_list.append(img)
#dan
bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha()
#bom
grenade_img = pygame.image.load('img/icons/grenade.png').convert_alpha()

#mau
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)


def draw_bg():
	screen.fill(BG)
	width = sky_img.get_width()
	for x in range(5):
		screen.blit(sky_img, ((x * width) - bg_scroll * 0.5, 0))
		


class Soldier(pygame.sprite.Sprite):
	def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
		pygame.sprite.Sprite.__init__(self)
		self.alive = True
		self.char_type = char_type
		self.speed = speed
		self.ammo = ammo
		self.start_ammo = ammo
		self.shoot_cooldown = 0
		self.grenades = grenades
		self.health = 100
		self.max_health = self.health
		self.direction = 1
		self.vel_y = 0
		self.jump = False
		self.in_air = True
		self.flip = False
		self.animation_list = []
		self.frame_index = 0
		self.action = 0
		self.update_time = pygame.time.get_ticks()
		#bien cho AI
		self.move_counter = 0
		self.vision = pygame.Rect(0, 0, 150, 20)
		self.idling = False
		self.idling_counter = 0
		
		#load anh player
		animation_types = ['Idle', 'Run', 'Jump', 'Death']
		for animation in animation_types:
			#cap nhat lai danh sach hinh anh
			temp_list = []
			#dem so anh co trong file
			num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
			for i in range(num_of_frames):
				img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
				img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
				temp_list.append(img)
			self.animation_list.append(temp_list)

		self.image = self.animation_list[self.action][self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.width = self.image.get_width()
		self.height = self.image.get_height()


	def update(self):
		self.update_animation()
		self.check_alive()
		#update cooldown
		if self.shoot_cooldown > 0:
			self.shoot_cooldown -= 1


	def move(self, moving_left, moving_right):
		#cap nhat lai bien di chuyen
		screen_scroll = 0
		dx = 0
		dy = 0

		#di chuyen
		if moving_left:
			dx = -self.speed
			self.flip = True
			self.direction = -1
		if moving_right:
			dx = self.speed
			self.flip = False
			self.direction = 1

		#nhay
		if self.jump == True and self.in_air == False:
			self.vel_y = -13
			self.jump = False
			self.in_air = True

		#trong luc
		self.vel_y += GRAVITY
		if self.vel_y > 10:
			self.vel_y
		dy += self.vel_y

		#kiem tra va cham
		for tile in world.obstacle_list:
			#kiem tra va cham voi truc x
			if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
				dx = 0
				#if the ai has hit a wall then make it turn around
				if self.char_type == 'enemy':
					self.direction *= -1
					self.move_counter = 0
			#kiem tra va cham voi truc y
			if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
				#check if below the ground, i.e. jumping
				if self.vel_y < 0:
					self.vel_y = 0
					dy = tile[1].bottom - self.rect.top
				#check if above the ground, i.e. falling
				elif self.vel_y >= 0:
					self.vel_y = 0
					self.in_air = False
					dy = tile[1].top - self.rect.bottom

		#dieu kien scroll man hinh
		if self.char_type == 'player':
			if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
				dx = 0

		#cap nhat vi tri rectangle cua player
		self.rect.x += dx
		self.rect.y += dy

		#update scroll based on player position
		if self.char_type == 'player':
			if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH)\
				or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
				self.rect.x -= dx
				screen_scroll = -dx
		return screen_scroll

	def shoot(self):
		if self.shoot_cooldown == 0 and self.ammo > 0:
			self.shoot_cooldown = 20
			bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
			bullet_group.add(bullet)
			#giam dan
			self.ammo -= 1

	def ai(self):
		if self.alive and player.alive:
			if self.idling == False and random.randint(1, 200) == 1:
				self.update_action(0)#0: idle
				self.idling = True
				self.idling_counter = 50
			#kiem tra AI o gan nguoi choi
			if self.vision.colliderect(player.rect):
				#AI dung lai
				self.update_action(0)#0: dung yen
				#ban
				self.shoot()
			else:
				if self.idling == False:
					if self.direction == 1:
						ai_moving_right = True
					else:
						ai_moving_right = False
					ai_moving_left = not ai_moving_right
					self.move(ai_moving_left, ai_moving_right)
					self.update_action(1)#1: chay
					self.move_counter += 1
					#cap nhat tam nhin cho AI de ban player
					self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

					if self.move_counter > TILE_SIZE:
						self.direction *= -1
						self.move_counter *= -1
				else:
					self.idling_counter -= 1
					if self.idling_counter <= 0:
						self.idling = False

		#lan man hinh
		self.rect.x += screen_scroll

	def update_animation(self):
		#cap nhat hoat hoa
		ANIMATION_COOLDOWN = 100
		self.image = self.animation_list[self.action][self.frame_index]
		if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
			self.update_time = pygame.time.get_ticks()
			self.frame_index += 1
		if self.frame_index >= len(self.animation_list[self.action]):
			if self.action == 3:
				self.frame_index = len(self.animation_list[self.action]) - 1
			else:
				self.frame_index = 0

	def update_action(self, new_action):
		#cap nhat hanh dong
		if new_action != self.action:
			self.action = new_action
			#cap nhat cai dat lai hoat hoa
			self.frame_index = 0
			self.update_time = pygame.time.get_ticks()

	def check_alive(self):
		if self.health <= 0:
			self.health = 0
			self.speed = 0
			self.alive = False
			self.update_action(3)

	def draw(self):
		screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

class World():
	def __init__(self):
		self.obstacle_list = []

	def process_data(self, data):
		self.level_length = len(data[0])
		#iterate through each value in level data file
		for y, row in enumerate(data):
			for x, tile in enumerate(row):
				if tile >= 0:
					img = img_list[tile]
					img_rect = img.get_rect()
					img_rect.x = x * TILE_SIZE
					img_rect.y = y * TILE_SIZE
					tile_data = (img, img_rect)
					if tile >= 0 and tile <= 8:
						self.obstacle_list.append(tile_data)
					elif tile >= 9 and tile <= 10:
						water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
						water_group.add(water)
					elif tile >= 11 and tile <= 14:
						decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
						decoration_group.add(decoration)
					elif tile == 15:#create player
						player = Soldier('player', x * TILE_SIZE, y * TILE_SIZE, 1.65, 5, 20, 5)
						health_bar = HealthBar(10, 10, player.health, player.health)
					elif tile == 16:#create enemies
						enemy = Soldier('enemy', x * TILE_SIZE, y * TILE_SIZE, 1.65, 2, 20, 0)
						enemy_group.add(enemy)
					
						
					elif tile == 20:#create exit
						exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
						exit_group.add(exit)
		return player, health_bar

	def draw(self):
		for tile in self.obstacle_list:
			tile[1][0] += screen_scroll
			screen.blit(tile[0], tile[1])

class Decoration(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self):
		self.rect.x += screen_scroll

class Water(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self):
		self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self):
		self.rect.x += screen_scroll








	

class HealthBar():
	def __init__(self, x, y, health, max_health):
		self.x = x
		self.y = y
		self.health = health
		self.max_health = max_health

	def draw(self, health):
		#cap nhat mau 
		self.health = health
		#tinh phan tram mau
		ratio = self.health / self.max_health
		pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
		pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
		pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))

class Bullet(pygame.sprite.Sprite):
	def __init__(self, x, y, direction):
		pygame.sprite.Sprite.__init__(self)
		self.speed = 10
		self.image = bullet_img
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.direction = direction

	def update(self):
		#di chuyen dan
		self.rect.x += (self.direction * self.speed) + screen_scroll
		#xoa dan neu dan ra khoi man hinh
		if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
			self.kill()
		#kiem tra va cham 
		for tile in world.obstacle_list:
			if tile[1].colliderect(self.rect):
				self.kill()

		#kiem tra va cham voi dan
		if pygame.sprite.spritecollide(player, bullet_group, False):
			if player.alive:
				player.health -= 5
				self.kill()
		for enemy in enemy_group:
			if pygame.sprite.spritecollide(enemy, bullet_group, False):
				if enemy.alive:
					enemy.health -= 25
					self.kill()

class Grenade(pygame.sprite.Sprite):
	def __init__(self, x, y, direction):
		pygame.sprite.Sprite.__init__(self)
		self.timer = 100
		self.vel_y = -11
		self.speed = 7
		self.image = grenade_img
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		self.direction = direction

	def update(self):
		self.vel_y += GRAVITY
		dx = self.direction * self.speed
		dy = self.vel_y

		#kiem tra va cham voi cac doi tuong
		for tile in world.obstacle_list:
			#va cham voi dat
			if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
				self.direction *= -1
				dx = self.direction * self.speed
			#va cham theo truc y
			if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
				self.speed = 0
				#neu duoi chan la dat
				if self.vel_y < 0:
					self.vel_y = 0
					dy = tile[1].bottom - self.rect.top
				#neu tren dau la dat
				elif self.vel_y >= 0:
					self.vel_y = 0
					dy = tile[1].top - self.rect.bottom	

		#cap nhat vi tri bom
		self.rect.x += dx + screen_scroll
		self.rect.y += dy

		#dem nguoc thoi gian no
		self.timer -= 1
		if self.timer <= 0:
			self.kill()
			explosion = Explosion(self.rect.x, self.rect.y, 0.5)
			explosion_group.add(explosion)
			#bom gay sat thuong
			if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
				abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
				player.health -= 50
			for enemy in enemy_group:
				if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
					abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
					enemy.health -= 50

class Explosion(pygame.sprite.Sprite):
	def __init__(self, x, y, scale):
		pygame.sprite.Sprite.__init__(self)
		self.images = []
		for num in range(1, 6):
			img = pygame.image.load(f'img/explosion/exp{num}.png').convert_alpha()
			img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
			self.images.append(img)
		self.frame_index = 0
		self.image = self.images[self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.counter = 0

	def update(self):
		#lan man hinh
		self.rect.x += screen_scroll

		EXPLOSION_SPEED = 4
		#cap nhat hoat hoa cua vu no
		self.counter += 1
		if self.counter >= EXPLOSION_SPEED:
			self.counter = 0
			self.frame_index += 1
			#if the animation is complete then delete the explosion
			if self.frame_index >= len(self.images):
				self.kill()
			else:
				self.image = self.images[self.frame_index]

#create sprite groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

#ctao danh sach trong
world_data = []
for row in range(ROWS):
	r = [-1] * COLS
	world_data.append(r)
#load thong tin trong file level data va tao map
with open(f'img/level{level}_data.csv', newline='') as csvfile:
	reader = csv.reader(csvfile, delimiter=',')
	for x, row in enumerate(reader):
		for y, tile in enumerate(row):
			world_data[x][y] = int(tile)
world = World()
player, health_bar = world.process_data(world_data)

run = True
while run:
	clock.tick(FPS)
	#cap nhat bg
	draw_bg()
	#ve map
	world.draw()
	#hien thi mau nguoi choi
	health_bar.draw(player.health)

	player.update()
	player.draw()

	for enemy in enemy_group:
		enemy.ai()
		enemy.update()
		enemy.draw()

	#cap nhat nhom va ve nhom
	bullet_group.update()
	grenade_group.update()
	explosion_group.update()
	
	decoration_group.update()
	water_group.update()
	exit_group.update()
	bullet_group.draw(screen)
	grenade_group.draw(screen)
	explosion_group.draw(screen)
	
	decoration_group.draw(screen)
	water_group.draw(screen)
	exit_group.draw(screen)


	if countdown==0:
		#cap nhat hanh dong nguoi choi
		if player.alive:
			#ban dan
			if shoot:
				player.shoot()
			#nem bom
			elif grenade and grenade_thrown == False and player.grenades > 0:
				grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),\
							player.rect.top, player.direction)
				grenade_group.add(grenade)
				#giam so luong bom
				player.grenades -= 1
				grenade_thrown = True
			if player.in_air:
				player.update_action(2)#2: nhay
			elif moving_left or moving_right:
				player.update_action(1)#1: chay
			else:
				player.update_action(0)#0: dung yen
			screen_scroll = player.move(moving_left, moving_right)
			bg_scroll -= screen_scroll
		if player.rect.centery>int(SCREEN_HEIGHT):
			run=False
	if countdown>0:
		draw_text('GET READY!',font40, (0,0,0),int(SCREEN_WIDTH/2-100),int(SCREEN_HEIGHT/2-250))
		draw_text(str(countdown),font40,(0,0,0),int(SCREEN_HEIGHT/2+75),int(SCREEN_HEIGHT/2-200))
		count_timer=pygame.time.get_ticks()
		if count_timer-last_count>1000:
			countdown-=1
			last_count=count_timer
	
	for event in pygame.event.get():
		#out game
		if event.type == pygame.QUIT:
			run = False
		
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_a:
				moving_left = True
			if event.key == pygame.K_d:
				moving_right = True
			if event.key == pygame.K_SPACE:
				shoot = True
			if event.key == pygame.K_q:
				grenade = True
			if event.key == pygame.K_w and player.alive:
				player.jump = True
			if event.key == pygame.K_ESCAPE:
				run = False

		if event.type == pygame.KEYUP:
			if event.key == pygame.K_a:
				moving_left = False
			if event.key == pygame.K_d:
				moving_right = False
			if event.key == pygame.K_SPACE:
				shoot = False
			if event.key == pygame.K_q:
				grenade = False
				grenade_thrown = False

	pygame.display.update()
pygame.quit()