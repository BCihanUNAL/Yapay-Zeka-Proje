import pygame, sys
import random

class Ball():

    def __init__(self,left,top,width,height,speed_x = 0,speed_y = 0,x = -1,y = -1):
        self.obj = pygame.Rect(left, top, width, height)
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.left = left
        self.top = top
        self.width = width
        self.height = height

        if x != -1:
            self.obj.x = x

        if y != -1 :
            self.obj.y = y

    def animation(self, player, opponent, screen_width, screen_height):
        self.obj.x += self.speed_x
        self.obj.y += self.speed_y

        if self.obj.top <= 0 or self.obj.bottom >= screen_height:
            self.speed_y *= -1
        if self.obj.left <= 0 or self.obj.right >= screen_width:
            self.restart(screen_width,screen_height)

        if self.obj.colliderect(player):
            self.speed_x = abs(self.speed_x)
        if self.obj.colliderect(opponent):
            self.speed_x = -abs(self.speed_x)

    def restart(self, screen_height, screen_width):
        self.obj.centerx = screen_width/2
        self.obj.centery = screen_height/2
        self.speed_y *= random.choice((1, -1))
        self.speed_x *= random.choice((1, -1))

    def get(self):
        return self.obj

    def get_x(self):
        return self.obj.x

    def get_y(self):
        return self.obj.y

def calculate_state_value(ball_y,stick_y_down,stick_y_up):
    if int(ball_y + 15) < stick_y_down and (ball_y - 15) > stick_y_up:
        return 1.0
    else:
        return -1.0

def calculate_prize(ball_x,ball_y,stick_x,stick_y_down,stick_y_up):
    if ball_x + 15 >= stick_x:
        if int(ball_y + 15) < stick_y_down and (ball_y - 15) > stick_y_up:#ball_y in [stick_y_up - 15,stick_y_down + 15]:
            return 5.0
        else:
            return -5.0
    else:
        if int(ball_y + 15) < stick_y_down and (ball_y - 15) > stick_y_up:
            return 2.0
        else:
            return -1.0



def calculate(ball_x,ball_y,stick_x,stick_y_down,stick_y_up,alpha,decay_greedy,depth,speed_x,speed_y,depth_limit=2):
    if depth > depth_limit or ball_x >= screen_width - 25:
        return calculate_state_value(ball_y,stick_y_down,stick_y_up) + alpha * calculate_prize(ball_x,ball_y,stick_x,stick_y_down,stick_y_up)
    else:
        s_x = speed_x
        s_y = speed_y
        if ball_y+speed_y+15 >= screen_height or ball_y+speed_y-15 <= 0:
            speed_y *= -1
        if ball_x+speed_x-15 <= 15: # oyuncu cubugunun sag tarafi
            speed_x *= -1
        if stick_y_up - 7 < 0:
            up_move_value = calculate(ball_x+s_x,ball_y+s_y,stick_x,stick_y_down-stick_y_up, 0, alpha, decay_greedy, depth + 1, speed_x, speed_y)
        else:
            up_move_value = calculate(ball_x + s_x, ball_y + s_y, stick_x, stick_y_down - 7, stick_y_up - 7, alpha, decay_greedy, depth + 1, speed_x, speed_y)
        if stick_y_down + 7 > screen_height:
            down_move_value = calculate(ball_x + s_x, ball_y + s_y, stick_x, screen_height, screen_height - (stick_y_down-stick_y_up), alpha, decay_greedy, depth + 1, speed_x, speed_y)
        else:
            down_move_value = calculate(ball_x+s_x,ball_y+s_y,stick_x,stick_y_down + 7, stick_y_up + 7, alpha, decay_greedy, depth + 1, speed_x, speed_y)

        return calculate_state_value(ball_y,stick_y_down,stick_y_up) + alpha * (decay_greedy * max(up_move_value,down_move_value) - calculate_state_value(ball_y,stick_y_down,stick_y_up))



def player_animation():
    player.y += player_speed
    if player.top < 0:
        player.top = 0
    if player.bottom >= screen_height:
        player.bottom = screen_height

def opponent_animation():
    opponent.y += opponent_speed
    if opponent.top < 0:
        opponent.top = 0
    if opponent.bottom >= screen_height:
        opponent.bottom = screen_height


pygame.init()
clock = pygame.time.Clock()

screen_width = 1360
screen_height = 768
screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption('Pong')

ball = Ball(screen_width/2 - 15, screen_height/2 - 15, 30, 30, 7, 7)
player = pygame.Rect(10, screen_height/2 - 70, 10, 140)
opponent = pygame.Rect(screen_width - 20, screen_height/2 - 70, 10, 140)


bg_color = pygame.Color('grey12')
light_grey = (200, 200, 200)
player_speed = 0
opponent_speed = 0
alpha = 0.5
decay_greedy = 0.9

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                player_speed += 7
            if event.key == pygame.K_UP:
                player_speed -= 7
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                player_speed -= 7
            if event.key == pygame.K_UP:
                player_speed += 7

    ball.animation(player,opponent,screen_width,screen_height)
    player_animation()

    up_move = calculate(ball.obj.left + (ball.obj.width / 2),ball.obj.top + (ball.obj.height / 2),opponent.left,opponent.bottom - 7,opponent.top - 7,alpha,decay_greedy,ball.speed_x,ball.speed_y,0)
    down_move = calculate(ball.obj.left + (ball.obj.width / 2),ball.obj.top + (ball.obj.height / 2), opponent.left, opponent.bottom + 7, opponent.top + 7, alpha, decay_greedy,ball.speed_x,ball.speed_y,0)

    print(up_move)
    print(down_move)
    print("--------------")

    if up_move >= down_move:
        opponent_speed = -7
    else:
        opponent_speed = 7

    opponent_animation()

    screen.fill(bg_color)
    pygame.draw.rect(screen, light_grey, player)
    pygame.draw.rect(screen, light_grey, opponent)
    pygame.draw.ellipse(screen, light_grey, ball.get())
    pygame.draw.aaline(screen, light_grey, (screen_width/2,0), (screen_width/2, screen_height))

    pygame.display.flip()
    clock.tick(60)
