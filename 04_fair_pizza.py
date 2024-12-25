import pyxel
import math
import random

# ゲームの設定
SCREEN_WIDTH = 160
SCREEN_HEIGHT = 120
PIZZA_RADIUS = 50
CUT_ANGLE = math.pi / 3  # 60度の角度
MAX_HEALTH = 3
START_X = SCREEN_WIDTH // 2
START_Y = SCREEN_HEIGHT // 2
MIN_CUTS = 4  # 最小のカット数

class PizzaGame:
    def __init__(self):
        self.score = 0
        self.level = 1
        self.health = MAX_HEALTH
        self.cuts = 0
        self.cut_angles = []  # カットの角度を保存するリスト
        self.game_over = False
        self.cut_line_angle = 0  # 回転中の直線の角度
        self.target_cuts = random.randint(MIN_CUTS, 4 + self.level * 2)  # レベルに基づいた最大カット数
        self.target_cuts_remaining = self.target_cuts
        self.is_paused = False  # ゲームが一時停止しているかどうか

        # 基準となる回転速度
        self.speed = 0.05
        self.rotation_speed = self.speed  # 初期回転速度
        self.speed_rand = 1

        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT)  # ウィンドウの初期化
        pyxel.run(self.update, self.draw)

    def update(self):
        if self.game_over:
            return

        # ゲームが一時停止していない場合のみ更新
        if not self.is_paused:
            # スコアに基づいてレベルを決定し、回転速度を調整
            self.level = min(self.score // 10 + 1, 5)
            self.rotation_speed = self.speed * ( (self.level + 5) / 5 ) * self.speed_rand
            
            # 回転する直線の角度を更新
            self.cut_line_angle += self.rotation_speed  # この値で回転速度を調整

            # スペースキーでカット
            if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) or pyxel.btnp(pyxel.KEY_SPACE):  
                self.make_cut()

            # 目標のカット数が達成されたらスコア更新とヘルス計算
            if self.target_cuts_remaining == 0:
                self.calculate_health()
                self.is_paused = True  # ゲーム一時停止

        # ゲームが一時停止している場合
        elif pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) or pyxel.btnp(pyxel.KEY_SPACE):
            # 一時停止後、再開時にカット数と最大カット数を更新
            self.target_cuts = random.randint(MIN_CUTS, 4 + self.level * 2)  # レベルに基づいた新しい最大カット数]
            self.speed_rand = random.randint(0, 7) / 10 + 0.7
            self.target_cuts_remaining = self.target_cuts  # 残りカット数をリセット
            self.cut_angles.clear()  # カットの角度もリセット
            self.is_paused = False  # スペースキーでゲーム再開
            if self.health <= 0:
                self.game_over = True

    def draw(self):
        pyxel.cls(0)

        if self.game_over:
            pyxel.text(SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2, "GAME OVER", pyxel.COLOR_RED)
            pyxel.text(SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2 + 10, f"Score: {self.score}", pyxel.COLOR_WHITE)
            return

        # ゲームが一時停止していない場合の描画
        if not self.is_paused:
            # ピザの描画
            pyxel.circ(START_X, START_Y, PIZZA_RADIUS, pyxel.COLOR_YELLOW)

            # 回転中の直線の描画
            x1 = START_X + PIZZA_RADIUS * math.cos(self.cut_line_angle)
            y1 = START_Y + PIZZA_RADIUS * math.sin(self.cut_line_angle)
            pyxel.line(START_X, START_Y, x1, y1, pyxel.COLOR_RED)

            # すでにカットした部分の描画
            for angle in self.cut_angles:
                x1 = START_X + PIZZA_RADIUS * math.cos(angle)
                y1 = START_Y + PIZZA_RADIUS * math.sin(angle)
                pyxel.line(START_X, START_Y, x1, y1, pyxel.COLOR_RED)

            # 体力とスコアの表示
            pyxel.text(5, 5, f"Health: {self.health}", pyxel.COLOR_WHITE)
            pyxel.text(5, 15, f"Score: {self.score}", pyxel.COLOR_WHITE)

            # 現在の目標のカット数表示
            if self.target_cuts < 7:
                pyxel.text(SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2 - 10, f"Cut: {self.target_cuts}", 7)
            elif self.target_cuts // 2 == self.target_cuts / 2:
                pyxel.text(SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2 - 10, f"Cut: {self.target_cuts}", 9)
            else:
                pyxel.text(SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2 - 10, f"Cut: {self.target_cuts}",(pyxel.frame_count) // 4 % 16)

        # ゲームが一時停止している場合
        if self.is_paused:
            # ピザの描画
            pyxel.circ(START_X, START_Y, PIZZA_RADIUS, pyxel.COLOR_YELLOW)

            slice_areas = self.calculate_areas()
            max_area = max(slice_areas)
            min_area = min(slice_areas)
            area_difference = max_area / min_area

            # すでにカットした部分の描画
            for angle in self.cut_angles:
                x1 = START_X + PIZZA_RADIUS * math.cos(angle)
                y1 = START_Y + PIZZA_RADIUS * math.sin(angle)
                pyxel.line(START_X, START_Y, x1, y1, pyxel.COLOR_RED)
            

            if (abs(area_difference-1)) < 0.01: 
                pyxel.text(SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 2 + 10, "Perfect!!", pyxel.COLOR_WHITE)
            elif (abs(area_difference-1)) < 0.1:
                pyxel.text(SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 2 + 10, "Great!", pyxel.COLOR_WHITE)          
            elif (abs(area_difference-1)) < (self.target_cuts/20):
                pyxel.text(SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 2 + 10, "Good!", pyxel.COLOR_WHITE)
            elif (abs(area_difference-1)) < (self.target_cuts/10):
                pyxel.text(SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 2 + 10, "Ok", pyxel.COLOR_WHITE)
            else:
                pyxel.text(SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 2 + 10, "Oops!", pyxel.COLOR_WHITE)
            pyxel.text(SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2 + 20, f"max/min : {int(abs(area_difference)*100)}%", pyxel.COLOR_WHITE)

            # 体力とスコアの表示
            pyxel.text(5, 5, f"Life: {self.health}", pyxel.COLOR_WHITE)
            pyxel.text(5, 15, f"Score: {self.score}", pyxel.COLOR_WHITE)

    def make_cut(self):
        if len(self.cut_angles) < self.target_cuts:
            # カット位置を現在の直線の角度で決定
            angle = self.cut_line_angle  # 現在の直線の角度でカット
            self.cut_angles.append(angle)
            self.cuts += 1
            self.target_cuts_remaining -= 1  # 目標のカット数を1つ減らす

    def calculate_health(self):
        if len(self.cut_angles) == self.target_cuts:
            # カット後の処理
            if self.cut_angles:  # cut_anglesが空でない場合にのみ面積を計算
                slice_areas = self.calculate_areas()
                max_area = max(slice_areas)
                min_area = min(slice_areas)
                area_difference = max_area / min_area

                if self.target_cuts < 7:
                    self.bonus = 1
                elif self.target_cuts // 2 == self.target_cuts / 2:
                    self.bonus = 2
                else:
                    self.bonus = 3
                
                if (abs(area_difference-1)) < 0.01: 
                    self.score += 5 * self.bonus
                elif (abs(area_difference-1)) < 0.1:
                    self.score += 3 * self.bonus          
                elif (abs(area_difference-1)) < (self.target_cuts/20):
                    self.score += 2 * self.bonus
                elif (abs(area_difference-1)) < (self.target_cuts/10):
                    self.score += 1 * self.bonus
                else:
                    self.health -= 1
                    

                self.is_paused = True  # ゲーム一時停止

                # self.cut_angles.clear() を削除（カットの痕跡をリセットしない）
                self.cuts = 0


    def calculate_areas(self):
        # 角度を0～2πに正規化してソート
        angles = [(angle + 2 * math.pi) % (2 * math.pi) for angle in self.cut_angles]  # 正規化
        angles.sort()  # 角度を昇順にソート
        angles.append(angles[0] + 2 * math.pi)  # 最初の角度を追加して円を閉じる

        areas = []
        for i in range(1, len(angles)):
            angle_diff = angles[i] - angles[i - 1]
            area = 0.5 * PIZZA_RADIUS**2 * angle_diff
            areas.append(area)

        return areas

if __name__ == "__main__":
    PizzaGame()
