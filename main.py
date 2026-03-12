import arcade
import random


class MainMenu(arcade.View):
    def __init__(self):
        super().__init__()

        self.background = arcade.load_texture("MainMenu.Art.png")
        self.play_texture = arcade.load_texture("MainMenu.Play.png")
        self.quit_texture = arcade.load_texture("MainMenu.Ragequit.png")

        bg_scale = 1000 / 60
        self.background_sprite = arcade.Sprite(self.background, scale=bg_scale, center_x=500, center_y=500)

        btn_scale = 10.0
        self.play_sprite = arcade.Sprite(self.play_texture, scale=btn_scale, center_x=200, center_y=500)
        self.quit_sprite = arcade.Sprite(self.quit_texture, scale=btn_scale, center_x=200, center_y=350)


        self.all_sprites_list = arcade.SpriteList()
        self.all_sprites_list.append(self.background_sprite)
        self.all_sprites_list.append(self.play_sprite)
        self.all_sprites_list.append(self.quit_sprite)


    def on_draw(self):
        self.clear()
        self.all_sprites_list.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        if self.play_sprite.collides_with_point((x, y)):
            difficulty_view = DifficultyView()
            self.window.show_view(difficulty_view)
        elif self.quit_sprite.collides_with_point((x, y)):
            arcade.close_window()


class DifficultyView(arcade.View):
    def __init__(self):
        super().__init__()
        self.buttons = [
            {"text": "ЛЕГКАЯ", "rect": [400, 600, 200, 60], "agility": 700},
            {"text": "СРЕДНЯЯ", "rect": [400, 500, 200, 60], "agility": 350},
            {"text": "СЛОЖНАЯ", "rect": [400, 400, 200, 60], "agility": 100}
        ]

    def on_draw(self):
        self.clear()
        arcade.draw_text("Выберите сложность", 500, 700, arcade.color.WHITE, 30, anchor_x="center")
        for btn in self.buttons:
            x, y, w, h = btn["rect"]
            arcade.draw_rect_filled(arcade.rect.XYWH(x, y, w, h), arcade.color.GREEN)
            arcade.draw_text(btn["text"], x, y, arcade.color.WHITE, 20, anchor_x="center", anchor_y="center")

    def on_mouse_press(self, x, y, button, modifiers):
        for btn in self.buttons:
            x_btn, y_btn, w_btn, h_btn = btn["rect"]

            if (x_btn - w_btn // 2 <= x <= x_btn + w_btn // 2 and
                    y_btn - h_btn // 2 <= y <= y_btn + h_btn // 2):
                game_view = GameView(btn["agility"])
                game_view.setup()
                self.window.show_view(game_view)
                break


class GameOverView(arcade.View):
    def __init__(self, time_gameplay):
        super().__init__()
        self.time_gameplay = time_gameplay

    def on_draw(self):
        self.clear()
        arcade.draw_text(f"Сыгранное время: {int(self.time_gameplay)} секунд", 500, 500, arcade.color.RED, 60, anchor_x="center", anchor_y="center")
        arcade.draw_text("Нажмите клавишу ESC для выхода в меню", 500, 400, arcade.color.WHITE, 20, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            menu_view = MainMenu()
            self.window.show_view(menu_view)

    def on_mouse_press(self, x, y, button, modifiers):
        pass


class Visitor:
    def __init__(self):
        self.visitor_pos = {
            "visitor.f.png": [(126, 427), (470, 372)],
            "visitor.r.png": [(76, 930), (230, 726), (176, 330), (576, 216)],
            "visitor.b.png": [(126, 630), (470, 576)],
            "visitor.l.png": [(220, 930), (376, 726), (329, 330), (720, 216)]
        }
        self.occupied_positions = set()
        self.time_new_vis = 8
        self.minus_time = 0.08
        self.timer = 0
        self.visitors = arcade.SpriteList()
        self.time_to_order = 3
        self.timer_order = 0

    def update(self, delta_time):
        self.timer += delta_time
        if self.timer >= self.time_new_vis:
            self.timer = 0
            self.time_new_vis = max(1, self.time_new_vis - self.minus_time)
            self.spawn_visitor()
        self.visitors.update()

    def spawn_visitor(self):
        available_positions = []
        for direction, positions in self.visitor_pos.items():
            for pos in positions:
                if pos not in self.occupied_positions:
                    available_positions.append((direction, pos))
        if available_positions:
            direction, pos = random.choice(available_positions)
            sprite = arcade.Sprite(direction, scale=2.0)
            sprite.center_x = pos[0]
            sprite.center_y = pos[1]
            self.visitors.append(sprite)
            self.occupied_positions.add(pos)

    def remove_visitor(self, visitor):
        pos = (visitor.center_x, visitor.center_y)
        if pos in self.occupied_positions:
            self.occupied_positions.remove(pos)
        if visitor in self.visitors:
            self.visitors.remove(visitor)


class Chef:
    def __init__(self):
        self.animation = ["cook.png", "cook2.png"]
        self.center_x = 900
        self.center_y = 950
        self.timer = 0
        self.time_new_pos = 0.8
        self.curr_animation = 0
        self.chef = arcade.SpriteList()
        self.sprite = None

    def update(self, delta_time):
        if self.sprite:
            self.timer += delta_time
            if self.timer >= self.time_new_pos:
                self.timer = 0
                self.curr_animation = (self.curr_animation + 1) % 2
                self.sprite.texture = arcade.load_texture(self.animation[self.curr_animation])
        self.chef.update()

    def spawn_chef(self):
        self.sprite = arcade.Sprite(self.animation[self.curr_animation], scale=2.0)
        self.sprite.center_x = self.center_x
        self.sprite.center_y = self.center_y
        self.chef.append(self.sprite)


class Courier:
    def __init__(self, agility):
        self.time_gameplay = 0
        self.stamina_bar_width = 300
        self.stamina_bar_height = 60
        self.stamina_bar_color = arcade.color.BLUEBERRY
        self.center_x = 400
        self.center_y = 400
        self.animation_paths = {
            "front": ["MC.idle.F.png", "MC.walking1.F.png", "MC.walking2.F.png"],
            "right": ["MC.idle.R.png", "MC.walking1.R.png", "MC.walking2.R.png"],
            "bottom": ["MC.idle.B.png", "MC.walking1.B.png", "MC.walking2.B.png"],
            "left": ["MC.idle.L.png", "MC.walking1.L.png", "MC.walking2.L.png"]
        }
        self.animation = {}
        self.load_textures()
        self.direction = "front"
        self.frame = 0
        self.speed = 2
        self.agility = agility
        self.max_agility = agility
        self.used_agility = 0
        self.agility_count = 0
        self.frame_timer = 0
        self.frame_time = 0.15
        self.is_moving = False
        self.sprite = arcade.Sprite(scale=2.0)
        self.sprite.center_x = self.center_x
        self.sprite.center_y = self.center_y
        self.sprite.texture = self.animation[self.direction][self.frame]
        self.previous_x = self.center_x
        self.previous_y = self.center_y

    def load_textures(self):
        for direction, paths in self.animation_paths.items():
            self.animation[direction] = []
            for path in paths:
                texture = arcade.load_texture(path)
                self.animation[direction].append(texture)

    def update_animation(self, delta_time):
        dx = self.sprite.center_x - self.previous_x
        dy = self.sprite.center_y - self.previous_y
        if abs(dx) > 0 or abs(dy) > 0:
            self.is_moving = True
            if abs(dx) > abs(dy):
                if dx > 0:
                    self.direction = "right"
                else:
                    self.direction = "left"
            else:
                if dy > 0:
                    self.direction = "front"
                else:
                    self.direction = "bottom"
        else:
            self.is_moving = False
        self.previous_x = self.sprite.center_x
        self.previous_y = self.sprite.center_y
        if not self.is_moving:
            if self.frame != 0:
                self.frame = 0
                self.sprite.texture = self.animation[self.direction][self.frame]
            return
        self.frame_timer += delta_time
        if self.frame_timer >= self.frame_time:
            self.frame_timer = 0
            self.frame = (self.frame + 1) % 3
            self.sprite.texture = self.animation[self.direction][self.frame]

    def move(self, dx, dy):
        self.previous_x = self.sprite.center_x
        self.previous_y = self.sprite.center_y
        self.sprite.center_x += dx * self.speed
        self.sprite.center_y += dy * self.speed
        self.center_x = self.sprite.center_x
        self.center_y = self.sprite.center_y

    def draw(self):
        self.sprite.draw()


class GameView(arcade.View):
    def __init__(self, agility):
        super().__init__()
        self.courier = Courier(agility)
        self.visitor = Visitor()
        self.chef = Chef()
        self.keys = set()
        self.all_sprites = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.wall_list = None
        self.exit_list = None
        self.collision_list = None
        self.ground_list = None
        self.physics_engine = None
        self.accept_orders = []
        self.mi_distance = 10 ** 7
        self.paused = False

    def on_key_press(self, key, modifiers):
        if key == arcade.key.W:
            self.keys.add("w")
        if key == arcade.key.A:
            self.keys.add("a")
        if key == arcade.key.S:
            self.keys.add("s")
        if key == arcade.key.D:
            self.keys.add("d")
        if key == arcade.key.LSHIFT:
            self.keys.add("lshift")
        if key == arcade.key.E:
            self.keys.add("e")
        if key == arcade.key.ENTER:
            self.paused = not self.paused

    def on_key_release(self, key, modifiers):
        if key == arcade.key.W:
            self.keys.discard("w")
        if key == arcade.key.A:
            self.keys.discard("a")
        if key == arcade.key.S:
            self.keys.discard("s")
        if key == arcade.key.D:
            self.keys.discard("d")
        if key == arcade.key.LSHIFT:
            self.keys.discard("lshift")
        if key == arcade.key.E:
            self.keys.discard("e")

    def on_update(self, delta_time):
        self.courier.time_gameplay += delta_time
        if self.paused:
            return
        dx, dy = 0, 0
        if "w" in self.keys:
            dy += 1
        if "s" in self.keys:
            dy -= 1
        if "a" in self.keys:
            dx -= 1
        if "d" in self.keys:
            dx += 1
        if "lshift" in self.keys and self.courier.agility > 0:
            self.courier.speed = 4
            self.courier.used_agility += delta_time
            if self.courier.used_agility > 0.5:
                self.courier.agility -= 10
                self.courier.agility_count += 1
                self.courier.used_agility = 0
        else:
            self.courier.speed = 2
            self.courier.used_agility += delta_time
            if self.courier.used_agility > 0.5 and self.courier.agility < self.courier.max_agility:
                self.courier.agility += 10
                self.courier.agility_count -= 1
                self.courier.used_agility = 0
        if "e" in self.keys:
            self.mi_distance = 10 ** 7
            for visitor in self.visitor.visitors:
                dist = ((self.courier.center_x - visitor.center_x) ** 2 +
                        (self.courier.center_y - visitor.center_y) ** 2) ** 0.5
                if self.mi_distance > dist and dist <= 70:
                    if visitor not in self.accept_orders:
                        self.accept_orders.append(visitor)
        if "e" in self.keys and self.accept_orders:
            dist_to_chef = ((self.courier.center_x - self.chef.center_x) ** 2 +
                            (self.courier.center_y - self.chef.center_y) ** 2) ** 0.5
            if dist_to_chef <= 70 and self.visitor.timer_order >= self.visitor.time_to_order:
                self.visitor.timer_order = 0
                if self.accept_orders:
                    visitor_to_remove = self.accept_orders.pop(0)
                    if visitor_to_remove in self.visitor.visitors:
                        self.visitor.remove_visitor(visitor_to_remove)
        if self.accept_orders:
            if len(self.accept_orders) > 1:
                self.visitor.timer_order += delta_time
            elif len(self.accept_orders) == 1 and self.visitor.timer_order >= self.visitor.time_to_order:
                self.visitor.timer_order = self.visitor.time_to_order
            else:
                self.visitor.timer_order += delta_time
        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707
        self.courier.move(dx, dy)
        if self.physics_engine:
            self.physics_engine.update()
            self.courier.center_x = self.courier.sprite.center_x
            self.courier.center_y = self.courier.sprite.center_y
        self.courier.update_animation(delta_time)
        self.visitor.update(delta_time)
        self.chef.update(delta_time)
        self.all_sprites.update()
        if self.courier.agility <= 0:
            game_over_view = GameOverView(self.courier.time_gameplay)
            self.window.show_view(game_over_view)

    def setup(self):
        self.player_list = arcade.SpriteList()
        self.all_sprites = arcade.SpriteList()
        map_name = "игровая карта.tmx"
        tile_map = arcade.load_tilemap(map_name, scaling=3.12)
        self.wall_list = tile_map.sprite_lists["walls"]
        self.exit_list = tile_map.sprite_lists["exit"]
        self.collision_list = tile_map.sprite_lists["collision"]
        self.ground_list = tile_map.sprite_lists["floor"]
        self.courier.sprite.center_x = 800
        self.courier.sprite.center_y = 800
        self.courier.center_x = 800
        self.courier.center_y = 800
        self.courier.previous_x = 800
        self.courier.previous_y = 800
        self.player_list.append(self.courier.sprite)
        self.all_sprites.append(self.courier.sprite)
        self.chef.spawn_chef()
        self.physics_engine = arcade.PhysicsEngineSimple(self.courier.sprite, self.collision_list)

    def on_draw(self):
        self.clear()
        self.ground_list.draw()
        self.wall_list.draw()
        self.exit_list.draw()
        self.visitor.visitors.draw()
        self.chef.chef.draw()
        self.player_list.draw()
        arcade.draw_rect_outline(arcade.rect.XYWH(150, 200, 300, 60), self.courier.stamina_bar_color, 4)
        width = max(0, 300 * (self.courier.agility / self.courier.max_agility))
        arcade.draw_rect_filled(arcade.rect.XYWH(150, 200, width, 60), self.courier.stamina_bar_color)
        if self.paused:
            arcade.draw_text("ПАУЗА", 500, 900, arcade.color.YELLOW, 40, anchor_x="center")


def main():
    window = arcade.Window(1000, 1000, "Cafe Dash")
    menu_view = MainMenu()
    window.show_view(menu_view)
    arcade.run()


if __name__ == "__main__":
    main()