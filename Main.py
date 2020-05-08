import pygame, sys
import random
import math
import pickle

speed_ball = 11
speed_player = 7
Q_values = {}
epsilon = 0.1
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

    def animation(self):
        self.obj.x += self.speed_x
        self.obj.y += self.speed_y

        if self.obj.top <= 0 or self.obj.bottom >= screen_height:
            self.speed_y *= -1
        if self.obj.left <= 0 or self.obj.right >= screen_width:
            self.restart()

        if self.obj.colliderect(player) or self.obj.left <= 20: # egitim icin bu satiri ekliyoruz.
            self.speed_x = abs(self.speed_x)
        if self.obj.colliderect(opponent):
            self.speed_x = -abs(self.speed_x)

    def restart(self):
        self.obj.left = screen_width/2 - 15
        self.obj.top = screen_height/2 - 15
        self.speed_y *= random.choice((1, -1))
        self.speed_x *= random.choice((1, -1))

    def get(self):
        return self.obj

    def get_x(self):
        return self.obj.x

    def get_y(self):
        return self.obj.y

def save_obj(obj, name ):
    with open('obj/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name ):
    with open('obj/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)

def calculate_state_value(ball_y,stick_y_down,stick_y_up):
    if int(ball_y + 15) < stick_y_down and (ball_y - 15) > stick_y_up:
        return 1.0
    else:
        return -1.0

def calculate_prize(ball_x,ball_y,stick_x,stick_y_down,stick_y_up,speed_y):
    if ball_x + 15 >= stick_x:
        if int(ball_y + 15) < stick_y_down and (ball_y - 15) > stick_y_up:#ball_y in [stick_y_up - 15,stick_y_down + 15]:
            return 5.0
        else:
            return -5.0
    else:
        dir_prize = 0
        if speed_y < 0 and (stick_y_down+stick_y_up)/2 - ball_y < 0 or speed_y > 0 and (stick_y_down+stick_y_up)/2 - ball_y > 0 :
            dir_prize = 0.5

        return -abs((stick_y_down+stick_y_up)/2 - ball_y)/(2 * screen_height) - abs(stick_x - ball_x)/(2 * screen_width)



def calculate(ball_x,ball_y,stick_x,stick_y_down,stick_y_up,alpha,decay_greedy,depth,speed_x,speed_y,depth_limit=9):
    dir_x = 1
    dir_y = 1
    if speed_x < 0:
        dir_x = -1
    if speed_y < 0:
        dir_y = -1
    
    if depth >= depth_limit or ball_x >= screen_width - 25:
        if Q_values.get((ball_x, ball_y, (stick_y_up + stick_y_down) / 2, dir_x, dir_y)) != None:
            print(Q_values[(ball_x, ball_y, (stick_y_up + stick_y_down) / 2, dir_x, dir_y)])
            return Q_values[(ball_x, ball_y, (stick_y_up + stick_y_down) / 2, dir_x, dir_y)]
        else:
            return calculate_prize(ball_x,ball_y,stick_x,stick_y_down,stick_y_up,speed_y)
    else:
        s_x = speed_x
        s_y = speed_y
        if ball_y+speed_y+15 >= screen_height or ball_y+speed_y-15 <= 0:
            speed_y *= -1
        if ball_x+speed_x-15 <= 20: # oyuncu cubugunun sag tarafi
            speed_x *= -1
        if stick_y_up - speed_player < 0:
            up_move_value = calculate(ball_x+s_x,ball_y+s_y,stick_x,stick_y_down-stick_y_up, 0, alpha, decay_greedy, depth + 1, speed_x, speed_y)
        else:
            up_move_value = calculate(ball_x + s_x, ball_y + s_y, stick_x, stick_y_down - speed_player, stick_y_up - speed_player, alpha, decay_greedy, depth + 1, speed_x, speed_y)

        if stick_y_down + speed_player > screen_height:
            down_move_value = calculate(ball_x + s_x, ball_y + s_y, stick_x, screen_height, screen_height - (stick_y_down-stick_y_up), alpha, decay_greedy, depth + 1, speed_x, speed_y)
        else:
            down_move_value = calculate(ball_x+s_x,ball_y+s_y,stick_x,stick_y_down + speed_player, stick_y_up + speed_player, alpha, decay_greedy, depth + 1, speed_x, speed_y)
        angle = math.atan(((stick_y_up + stick_y_down) / 2 - ball_y) / (stick_x - ball_x))
        mul = 2
        if Q_values.get((ball_x, ball_y, (stick_y_up + stick_y_down) / 2, dir_x, dir_y)) != None:
            return Q_values[(ball_x, ball_y, (stick_y_up + stick_y_down) / 2, dir_x, dir_y)] + alpha * (2*abs(math.sin(mul*angle)) -2*abs((stick_y_down+stick_y_up)/2 - ball_y)/(screen_height) - 2*abs(stick_x - ball_x)/(screen_width) + decay_greedy * max(up_move_value, down_move_value) - Q_values[(ball_x, ball_y, (stick_y_up + stick_y_down) / 2, dir_x, dir_y)])
        else:
            return calculate_prize(ball_x,ball_y,stick_x,stick_y_down,stick_y_up,speed_y) + alpha * (2*abs(math.sin(mul*angle)) -2*abs((stick_y_down+stick_y_up)/2 - ball_y)/(screen_height) - 2*abs(stick_x - ball_x)/(screen_width) + decay_greedy * max(up_move_value,down_move_value) - calculate_prize(ball_x,ball_y,stick_x,stick_y_down,stick_y_up,speed_y))



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

ball = Ball(screen_width/2 - 15, screen_height/2 - 15, 30, 30, speed_ball, speed_ball)
player = pygame.Rect(10, screen_height/2 - 70, 10, 140)
opponent = pygame.Rect(screen_width - 20, screen_height/2 - 70, 10, 140)


bg_color = pygame.Color('grey12')
light_grey = (200, 200, 200)
player_speed = 0
opponent_speed = 0
alpha = 0.5
decay_greedy = 0.9
counter = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                player_speed += speed_player
            if event.key == pygame.K_UP:
                player_speed -= speed_player
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                player_speed -= speed_player
            if event.key == pygame.K_UP:
                player_speed += speed_player

    ball.animation()
    player_animation()


    up_move = calculate(ball.obj.left + (ball.obj.width / 2),ball.obj.top + (ball.obj.height / 2),opponent.left,opponent.bottom - speed_player,opponent.top - speed_player,alpha,decay_greedy,0,ball.speed_x,ball.speed_y)
    down_move = calculate(ball.obj.left + (ball.obj.width / 2),ball.obj.top + (ball.obj.height / 2), opponent.left, opponent.bottom + speed_player, opponent.top + speed_player, alpha, decay_greedy,0,ball.speed_x,ball.speed_y)
    dir_x = 1
    dir_y = 1
    if ball.speed_x < 0:
        dir_x = -1
    if ball.speed_y < 0:
        dir_y = -1

    #print(up_move)
    #print(down_move)
    #print("--------------")
    if random.random() < epsilon:
        if random.random() < 0.5:
            opponent_speed = -speed_player
            Q_values[(ball.obj.centerx, ball.obj.centery, opponent.centery, dir_x, dir_y)] = up_move
            #print(Q_values[(ball.obj.centerx, ball.obj.centery, opponent.centery)])
        else:
            opponent_speed = speed_player
            Q_values[(ball.obj.centerx, ball.obj.centery, opponent.centery, dir_x, dir_y)] = down_move
            #print(Q_values[(ball.obj.centerx, ball.obj.centery, opponent.centery)])

    else:
        if up_move >= down_move:
            opponent_speed = -speed_player
            Q_values[(ball.obj.centerx, ball.obj.centery, opponent.centery, dir_x, dir_y)] = up_move
            #print(Q_values[(ball.obj.centerx, ball.obj.centery, opponent.centery)])
        else:
            opponent_speed = speed_player
            Q_values[(ball.obj.centerx, ball.obj.centery, opponent.centery, dir_x, dir_y)] = down_move
            #print(Q_values[(ball.obj.centerx, ball.obj.centery, opponent.centery)])

    opponent_animation()

    screen.fill(bg_color)
    pygame.draw.rect(screen, light_grey, player)
    pygame.draw.rect(screen, light_grey, opponent)
    pygame.draw.ellipse(screen, light_grey, ball.get())
    pygame.draw.aaline(screen, light_grey, (screen_width/2,0), (screen_width/2, screen_height))

    pygame.display.flip()
    if counter >= 30000:
        save_obj(Q_values, 'Qmodel')
        counter = -200000000
    counter += 1
    clock.tick(60)
