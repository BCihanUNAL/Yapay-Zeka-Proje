import pygame, sys
import random
import math
import pickle

speed_ball = 11
speed_player = 7
#oyunun durum degiskenlerine gore hesaplanacak Q fonksiyonu degerleri, asagidaki dict yapisinda tutuluyor.
#durum = (top_x, top_y ajan_y, top_hiz_x, top_hiz_y)
Q_values = {}
epsilon = 0.1
is_training = False

#oyundaki top asagidaki sinif ile kontrol edilmektedir.
class Ball():
    def __init__(self,left,top,width,height,speed_x = 0,speed_y = 0,x = -1,y = -1):
        self.obj = pygame.Rect(left, top, width, height)
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.counter = 0
        self.player_score = 0
        self.opponent_score = 0

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
            if self.obj.left <= 0:
                self.player_score += 1
            else:
                self.opponent_score += 1
            self.restart()

        if self.obj.colliderect(player) or self.obj.left <= 20 and is_training: # ajan egitiliyorsa, ajanin karsisindaki oyuncu asla kaybetmez.
            self.speed_x = abs(self.speed_x)

        if self.obj.colliderect(opponent):
            self.speed_x = -abs(self.speed_x)
            if is_training:
                self.counter += 1
                if self.counter >= 1000: #ajani kac tur boyunca egitecegiz?
                    save_obj(Q_values,'Qmodel')

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

#olusturulan dict asagidaki fonksiyonlarla diske kaydedilip, diskten okunuyor
def save_obj(obj, name ):
    with open('obj/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name ):
    with open('obj/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)


#kullandigimiz Q fonksiyonuna gore eger ajan topu karsilamissa 5 puan, karsilayamamis ise -5 puan odul alir
#eger top ajanin x ekseninden daha uzakta ise top ile ajan arasindaki uzaklik kadar(0,1 arasi normallestirilmis) ceza alir.
def calculate_Q(ball_x,ball_y,stick_x,stick_y_down,stick_y_up,speed_y):
    if ball_x + 15 >= stick_x:
        if int(ball_y + 15) < stick_y_down and (ball_y - 15) > stick_y_up:#ball_y in [stick_y_up - 15,stick_y_down + 15]:
            return 5.0
        else:
            return -5.0
    else:
        return -abs((stick_y_down+stick_y_up)/2 - ball_y)/(2 * screen_height) - abs(stick_x - ball_x)/(2 * screen_width)

#asagida Q fonksiyonu, ajanin durum ve aksiyon bilgileri kullanilarak ajanin hareketlerine puan verilmektedir.
#eger belirli bir durum icin degerler hesaplanmissa, onceden hesaplanan degerler kullanilmaktadir.
#puani hesaplamak icin sinirli derinlikte arama yaparak ortaya cikan her durum icin Q degerlerini guncelliyoruz, ardindan ajan en yuksek puanli hareketi(yukari, asagi) seciyor
def calculate(ball_x,ball_y,stick_x,stick_y_down,stick_y_up,alpha,decay_greedy,depth,speed_x,speed_y,depth_limit=9):
    dir_x = 1
    dir_y = 1
    if speed_x < 0:
        dir_x = -1
    if speed_y < 0:
        dir_y = -1
    # belirlenen derinlige yada top ajanin karsilayabilecegi x noktasina gelene kadar inip Q degerlerini hesapla.
    if depth >= depth_limit or ball_x >= screen_width - 25:
        if Q_values.get((ball_x, ball_y, (stick_y_up + stick_y_down) / 2, dir_x, dir_y)) != None:
            return Q_values[(ball_x, ball_y, (stick_y_up + stick_y_down) / 2, dir_x, dir_y)]
        else:
            return calculate_Q(ball_x,ball_y,stick_x,stick_y_down,stick_y_up,speed_y)
    else:
        s_x = speed_x
        s_y = speed_y
        if ball_y+speed_y+15 >= screen_height or ball_y+speed_y-15 <= 0:
            speed_y *= -1
        if ball_x+speed_x-15 <= 20: # oyuncu cubugunun sag tarafi, ajan karsi tarafin oyunu en iyi duzeyde oynadigini kabul eder.
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
        #tum islemler tamamlandiktan sonra hesaplanan Q' degerleri kullanilarak sonuc dondurulur.
        #top ile ajan arasindaki acinin 45 dereceye yakin olmasi(topun ilerleme acisi) ve ajan ile topun birbirine yakin olmasi odullendirilmektedir.
        if Q_values.get((ball_x, ball_y, (stick_y_up + stick_y_down) / 2, dir_x, dir_y)) != None:
            return Q_values[(ball_x, ball_y, (stick_y_up + stick_y_down) / 2, dir_x, dir_y)] + alpha * (2*abs(math.sin(mul*angle)) -2*abs((stick_y_down+stick_y_up)/2 - ball_y)/(screen_height) - 2*abs(stick_x - ball_x)/(screen_width) + decay_greedy * max(up_move_value, down_move_value) - Q_values[(ball_x, ball_y, (stick_y_up + stick_y_down) / 2, dir_x, dir_y)])
        else:
            return calculate_Q(ball_x,ball_y,stick_x,stick_y_down,stick_y_up,speed_y) + alpha * (2*abs(math.sin(mul*angle)) -2*abs((stick_y_down+stick_y_up)/2 - ball_y)/(screen_height) - 2*abs(stick_x - ball_x)/(screen_width) + decay_greedy * max(up_move_value,down_move_value) - calculate_Q(ball_x,ball_y,stick_x,stick_y_down,stick_y_up,speed_y))



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

if is_training == False:
    Q_values = load_obj('Qmodel')

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

game_font = pygame.font.Font("freesansbold.ttf", 32)

while True:
    if ball.counter >= 1000:
        is_training = False
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

    if is_training:
        up_move = calculate(ball.obj.centerx, ball.obj.centery,opponent.left,opponent.bottom - speed_player,opponent.top - speed_player,alpha,decay_greedy,0,ball.speed_x,ball.speed_y)
        down_move = calculate(ball.obj.centerx, ball.obj.centery, opponent.left, opponent.bottom + speed_player, opponent.top + speed_player, alpha, decay_greedy,0,ball.speed_x,ball.speed_y)
        dir_x = 1
        dir_y = 1
        if ball.speed_x < 0:
            dir_x = -1
        if ball.speed_y < 0:
            dir_y = -1

        #belirlenen epsilon degeri kadar rastgele hareket edilmekte, bu sayede ajan etrafini kesfetmektedir.
        if random.random() < epsilon:
            if random.random() < 0.5:
                opponent_speed = -speed_player
                Q_values[(ball.obj.centerx, ball.obj.centery, opponent.centery - speed_player, dir_x, dir_y)] = up_move
            else:
                opponent_speed = speed_player
                Q_values[(ball.obj.centerx, ball.obj.centery, opponent.centery + speed_player, dir_x, dir_y)] = down_move

        else:
            if up_move >= down_move:
                opponent_speed = -speed_player
                Q_values[(ball.obj.centerx, ball.obj.centery, opponent.centery - speed_player, dir_x, dir_y)] = up_move
            else:
                opponent_speed = speed_player
                Q_values[(ball.obj.centerx, ball.obj.centery, opponent.centery + speed_player, dir_x, dir_y)] = down_move
    else:
        dir_x = 1
        dir_y = 1
        if ball.speed_x < 0:
            dir_x = -1
        if ball.speed_y < 0:
            dir_y = -1
        #Q fonksiyonunun degeri su anki state icin olusturulmamis ise hesaplanmaktadir
        #ajanin yapabilecegi hareketlerden sonra olusan durumlar icin Q degerleri tekrar hesaplanmakta, sonrasinda hangi hareketin yapilacagini karsilastirmak icin kullanilmaktadir.
        if Q_values.get((ball.obj.centerx, ball.obj.centery, opponent.centery - speed_player,dir_x, dir_y)) != None:
            up_move = Q_values[(ball.obj.centerx, ball.obj.centery, opponent.centery - speed_player,dir_x, dir_y)]
        else:
            up_move = calculate(ball.obj.centerx, ball.obj.centery,opponent.left,opponent.bottom - speed_player,opponent.top - speed_player,alpha,decay_greedy,0,ball.speed_x,ball.speed_y)
            Q_values[(ball.obj.centerx, ball.obj.centery, opponent.centery - speed_player, dir_x, dir_y)] = up_move
        if Q_values.get((ball.obj.centerx, ball.obj.centery, opponent.centery + speed_player,dir_x, dir_y)) != None:
            down_move = Q_values[(ball.obj.centerx, ball.obj.centery, opponent.centery + speed_player,dir_x, dir_y)]
        else:
            down_move = calculate(ball.obj.centerx, ball.obj.centery,opponent.left,opponent.bottom + speed_player,opponent.top + speed_player,alpha,decay_greedy,0,ball.speed_x,ball.speed_y)

        if random.random() < epsilon:
            if random.random() < 0.5:
                opponent_speed = -speed_player
            else:
                opponent_speed = speed_player

        else:
            if up_move >= down_move:
                opponent_speed = -speed_player
            else:
                opponent_speed = speed_player

    opponent_animation()

    screen.fill(bg_color)
    pygame.draw.rect(screen, light_grey, player)
    pygame.draw.rect(screen, light_grey, opponent)
    pygame.draw.ellipse(screen, light_grey, ball.get())
    pygame.draw.aaline(screen, light_grey, (screen_width/2,0), (screen_width/2, screen_height))

    player_text = game_font.render(f"{ball.player_score}", False, light_grey)
    screen.blit(player_text, (screen_width/2 + 25, screen_height/2))
    opponent_text = game_font.render(f"{ball.opponent_score}", False, light_grey)
    screen.blit(opponent_text, (screen_width/2 - 50, screen_height/2))

    pygame.display.flip()
    clock.tick(60)
