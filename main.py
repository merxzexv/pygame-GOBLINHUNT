import pygame
from sys import exit
from random import randint
import math

pygame.init()

WIDTH, HEIGHT = 960, 600
GROUND_Y = 500

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("GoblinSlayer")
clock = pygame.time.Clock()

# Player Graphic
player_img = pygame.image.load("assets/player.png").convert_alpha()
player_img = pygame.transform.scale(player_img, (60, 90))

# Font
font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 24)

# Images
images = {
    "goblin2": pygame.image.load("assets/goblin2.png").convert_alpha(),
    "boss1": pygame.image.load("assets/bossgoblinwave1.png").convert_alpha(),
    "boss2": pygame.image.load("assets/bossgoblinwave2.png").convert_alpha(),
    "boss3": pygame.image.load("assets/bossgoblinwave3.png").convert_alpha(),
    "boss4": pygame.image.load("assets/bossgoblinwave4.png").convert_alpha(),
    "boss5": pygame.image.load("assets/bossgoblinwave5.png").convert_alpha(),
}

effect_images = {
    "bullet": pygame.transform.scale(pygame.image.load("assets/bullet.png").convert_alpha(), (20, 20)),
    "fireball": pygame.transform.scale(pygame.image.load("assets/fireball.png").convert_alpha(), (80, 80)),
    "shield": pygame.transform.scale(pygame.image.load("assets/shield.png").convert_alpha(), (40, 40)),
    "heal": pygame.transform.scale(pygame.image.load("assets/add.png").convert_alpha(), (30, 30)),
    "lightning": pygame.transform.scale(pygame.image.load("assets/lightning.png").convert_alpha(), (50, 50)),
    "freeze": pygame.transform.scale(pygame.image.load("assets/freezing.png").convert_alpha(), (60, 60)),
    "necro_fx": pygame.transform.scale(pygame.image.load("assets/necromancer.png").convert_alpha(), (40, 40)),
    "ammo": pygame.transform.scale(pygame.image.load("assets/ammo.png").convert_alpha(), (30, 30))
}

BASE_DAMAGE = {
    "goblin2": 10,
    "boss1": 15,
    "boss2": 30,
    "boss3": 50,
    "boss4": 60,
    "boss5": 80
}

SIZE_MULT = {
    "small": 1.10,
    "vary": 1.15,
    "big": 1.20,
    "very_big": 1.30
}

UPGRADE_CONFIG = {
    "dmg_add": 5,
    "firerate_sub": 2,
    "firerate_min": 3,
    "cost_mult": 1.5,
    "ammo_cost": 40,
    "heal_amount": 20,
    "base_dmg_cost": 100,
    "base_firerate_cost": 100,
    "base_heal_cost": 50,
    "base_restore_cost": 200
}


def enemy(img, size, count, spd, hp, typ):
    final_dmg = int(BASE_DAMAGE[img] * SIZE_MULT[size])
    return {
        "img": img,
        "size": size,
        "count": count,
        "spd": spd,
        "hp": hp,
        "dmg": final_dmg,
        "type": typ
    }


waves = {
    1: [
        enemy("goblin2", "small", 5, 2.0, 30, "basic"),
        enemy("boss1", "big", 1, 1.0, 100, "shield"),
    ],
    2: [
        enemy("goblin2", "small", 3, 2.0, 30, "basic"),
        enemy("boss1", "big", 2, 1.0, 100, "shield"),
        enemy("boss2", "very_big", 2, 1.5, 150, "healer"),
    ],
    3: [
        enemy("goblin2", "small", 3, 2.0, 30, "basic"),
        enemy("boss1", "big", 2, 1.0, 100, "shield"),
        enemy("boss2", "very_big", 1, 1.5, 150, "healer"),
        enemy("boss3", "very_big", 1, 3.0, 150, "kamikaze"),
    ],
    4: [
        enemy("goblin2", "small", 3, 2.0, 30, "basic"),
        enemy("boss1", "big", 2, 1.0, 100, "shield"),
        enemy("boss2", "very_big", 2, 1.5, 80, "healer"),
        enemy("boss3", "very_big", 2, 4.0, 50, "kamikaze"),
        enemy("boss4", "big", 1, 0.8, 200, "necromancer"),
    ],
    5: [
        enemy("goblin2", "small", 5, 2.0, 40, "basic"),
        enemy("boss1", "big", 3, 1.0, 120, "shield"),
        enemy("boss2", "very_big", 2, 1.5, 100, "healer"),
        enemy("boss3", "very_big", 2, 5.0, 60, "kamikaze"),
        enemy("boss4", "very_big", 2, 0.8, 200, "necromancer"),
        enemy("boss5", "very_big", 1, 0.5, 450, "necromancer")
    ],
}

SIZE_MAP = {
    "small": (60, 60),
    "big": (150, 150),
    "very_big": (250, 250)
}

MONEY_MAP = {
    "small": 10,
    "big": 45,
    "very_big": 95,
    "vary": 20
}

# State dicts
player = {}
abilities = {}
effects = {}
game = {}
upgrades = {}
projectiles = {}


def reset_game():
    global player, abilities, effects, game, upgrades, projectiles

    player = {
        "hp": 700,
        "max_hp": 700,
        "gold": 0,
        "dmg": 10,
        "reload": 15,
        "px": 10,
        "py": GROUND_Y - 90,
        "ammo": 50,
        "max_ammo": 50
    }

    abilities = {
        "fireball": True,
        "lightning": True,
        "freeze": True
    }

    effects = {
        "freeze_cd": 0,
        "lightning_cd": 0
    }

    game = {
        "wave": 1,
        "state": "playing",
        "goblins": [],
        "dead": [],
        "spawn_cd": 0,
        "heal_cd": 0,
        "raise_cd": 0
    }

    upgrades = {
        "dmg_cost": UPGRADE_CONFIG["base_dmg_cost"],
        "firerate_cost": UPGRADE_CONFIG["base_firerate_cost"],
        "heal_cost": UPGRADE_CONFIG["base_heal_cost"],
        "restore_cost": UPGRADE_CONFIG["base_restore_cost"]
    }

    projectiles = {
        "bullets": [],
        "fireballs": [],
        "shot_cd": 0
    }


reset_game()
game["state"] = "intro"


def spawn_wave():
    current_x = WIDTH
    for e in waves[game["wave"]]:
        for _ in range(e["count"]):
            if e["size"] == "vary":
                size = (randint(40, 120),) * 2
                gold = MONEY_MAP["vary"]
            else:
                size = SIZE_MAP[e["size"]]
                gold = MONEY_MAP[e["size"]]

            img_scaled = pygame.transform.scale(images[e["img"]], size)

            game["goblins"].append({
                "img": img_scaled,
                "rect": img_scaled.get_rect(bottomleft=(current_x, GROUND_Y)),
                "spd": e["spd"],
                "hp": e["hp"],
                "max_hp": e["hp"],
                "type": e["type"],
                "gold": gold,
                "dmg": e["dmg"],
                "hit": False,
                "dir": -1
            })
            current_x += size[0] // 2
    game["wave"] += 1


def buy_upgrade(upgrade_type):
    if upgrade_type == "dmg" and player["gold"] >= upgrades["dmg_cost"]:
        player["gold"] -= upgrades["dmg_cost"]
        player["dmg"] += UPGRADE_CONFIG["dmg_add"]
        upgrades["dmg_cost"] = int(upgrades["dmg_cost"] * UPGRADE_CONFIG["cost_mult"])
    elif upgrade_type == "firerate" and player["gold"] >= upgrades["firerate_cost"]:
        if player["reload"] > UPGRADE_CONFIG["firerate_min"]:
            player["gold"] -= upgrades["firerate_cost"]
            player["reload"] -= UPGRADE_CONFIG["firerate_sub"]
            upgrades["firerate_cost"] = int(upgrades["firerate_cost"] * UPGRADE_CONFIG["cost_mult"])
    elif upgrade_type == "ammo" and player["gold"] >= UPGRADE_CONFIG["ammo_cost"]:
        if player["ammo"] < player["max_ammo"]:
            player["gold"] -= UPGRADE_CONFIG["ammo_cost"]
            player["ammo"] = player["max_ammo"]
    elif upgrade_type == "heal" and player["gold"] >= upgrades["heal_cost"]:
        if player["hp"] < player["max_hp"]:
            player["gold"] -= upgrades["heal_cost"]
            player["hp"] = min(player["max_hp"], player["hp"] + UPGRADE_CONFIG["heal_amount"])
    elif upgrade_type == "restore" and player["gold"] >= upgrades["restore_cost"]:
        if not (abilities["fireball"] and abilities["lightning"] and abilities["freeze"]):
            player["gold"] -= upgrades["restore_cost"]
            abilities["fireball"] = True
            abilities["lightning"] = True
            abilities["freeze"] = True


def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game["state"] == "playing":
                    game["state"] = "exit_menu"
                else:
                    game["state"] = "playing"

            if game["state"] == "exit_menu":
                if event.key == pygame.K_q:
                    pygame.quit()
                    exit()
                continue

            if game["state"] == "intro":
                if event.key == pygame.K_SPACE:
                    game["state"] = "playing"
                if event.key == pygame.K_q:
                    pygame.quit()
                    exit()
                continue

            if game["state"] == "dead":
                if event.key == pygame.K_s:
                    reset_game()
                if event.key == pygame.K_q:
                    pygame.quit()
                    exit()
                continue

            # Abilities
            if event.key == pygame.K_f and abilities["fireball"]:
                abilities["fireball"] = False
                projectiles["fireballs"].append({"rect": pygame.Rect(player["px"] + 60, player["py"] + 10, 80, 80)})

            if event.key == pygame.K_l and abilities["lightning"]:
                abilities["lightning"] = False
                effects["lightning_cd"] = 60 * 6

            if event.key == pygame.K_z and abilities["freeze"]:
                abilities["freeze"] = False
                effects["freeze_cd"] = 60 * 8

            # Upgrades / Shops
            if event.key == pygame.K_1: buy_upgrade("dmg")
            if event.key == pygame.K_2: buy_upgrade("firerate")
            if event.key == pygame.K_r: buy_upgrade("ammo")
            if event.key == pygame.K_3: buy_upgrade("heal")
            if event.key == pygame.K_4: buy_upgrade("restore")


def handle_shooting(keys):
    if keys[pygame.K_SPACE] and player["ammo"] > 0:
        projectiles["shot_cd"] += 1
        if projectiles["shot_cd"] >= player["reload"]:
            projectiles["shot_cd"] = 0
            player["ammo"] -= 1
            dmg = randint(int(player["dmg"] * 0.5), int(player["dmg"] * 1.5))
            vx = 15
            vy = 0
            projectiles["bullets"].append({
                "x": player["px"] + 60.0,
                "y": player["py"] + 40.0,
                "vx": vx,
                "vy": vy,
                "dmg": dmg,
                "rect": pygame.Rect(player["px"] + 60, player["py"] + 40, 10, 10)
            })
    else:
        projectiles["shot_cd"] = player["reload"]


def update_projectiles():
    for b in projectiles["bullets"]:
        b["x"] += b["vx"]
        b["y"] += b["vy"]
        b["rect"].x = int(b["x"])
        b["rect"].y = int(b["y"])

    # Remove bullets that fly off-screen
    active_bullets = []
    for b in projectiles["bullets"]:
        if -50 <= b["rect"].x <= WIDTH + 50 and -50 <= b["rect"].y <= HEIGHT + 50:
            active_bullets.append(b)
    projectiles["bullets"] = active_bullets

    for f in projectiles["fireballs"]:
        f["rect"].x += 10
    projectiles["fireballs"] = [f for f in projectiles["fireballs"] if f["rect"].x < WIDTH]

    if not projectiles["fireballs"]:
        for g in game["goblins"]:
            if "f_hit" in g:
                del g["f_hit"]


def update_spawns():
    if not game["goblins"] and game["wave"] <= 5:
        game["spawn_cd"] += 1
        if game["spawn_cd"] >= 30:
            game["spawn_cd"] = 0
            spawn_wave()


def update_status_effects():
    is_frozen = False
    if effects["freeze_cd"] > 0:
        effects["freeze_cd"] -= 1
        is_frozen = True

    is_lightning = False
    if effects["lightning_cd"] > 0:
        effects["lightning_cd"] -= 1
        if (effects["lightning_cd"] // 30) % 2 == 0:
            is_frozen = True
        is_lightning = True
    return is_frozen, is_lightning


def update_goblins(is_frozen):
    game["heal_cd"] += 1
    game["raise_cd"] += 1

    if not is_frozen:
        for g in game["goblins"]:
            spd = g["spd"]
            if g["type"] == "kamikaze":
                spd *= 1.5

            if g["dir"] == 1 and g["rect"].x > player["px"] + 100:
                g["dir"] = -1
                g["hit"] = False

            g["rect"].x += spd * g["dir"]

            if g["type"] == "healer" and game["heal_cd"] >= 60:
                for other in game["goblins"]:
                    if g != other and abs(g["rect"].x - other["rect"].x) < 150:
                        other["hp"] = min(other["max_hp"], other["hp"] + 5)

            if g["type"] == "necromancer" and game["raise_cd"] >= 180:
                if game["dead"]:
                    revive = game["dead"].pop(0)
                    revive["hp"] = revive["max_hp"] // 2
                    revive["rect"].bottomleft = (g["rect"].x, GROUND_Y)
                    revive["dir"] = -1
                    revive["hit"] = False
                    game["goblins"].append(revive)

        if game["heal_cd"] >= 60:
            game["heal_cd"] = 0
        if game["raise_cd"] >= 180:
            game["raise_cd"] = 0


def handle_collisions():
    for g in game["goblins"]:
        if g["rect"].colliderect(pygame.Rect(player["px"], player["py"], 60, 90)):
            if g["type"] == "kamikaze":
                player["hp"] -= g.get("dmg", 30)
                g["hp"] = 0
            else:
                if not g.get("hit"):
                    player["hp"] -= g.get("dmg", 10)
                    g["hit"] = True
                g["dir"] = 1

    for b in projectiles["bullets"][:]:
        hit = False
        for g in game["goblins"]:
            if g["rect"].colliderect(b["rect"]):
                dmg = b["dmg"]
                if g["type"] == "shield":
                    dmg /= 2
                g["hp"] -= dmg
                hit = True
                break
        if hit:
            projectiles["bullets"].remove(b)

    for f in projectiles["fireballs"]:
        for g in game["goblins"]:
            if g["rect"].colliderect(f["rect"]) and not g.get("f_hit"):
                g["hp"] -= g["max_hp"] * 0.5
                g["f_hit"] = True


def handle_deaths():
    alive = []
    for g in game["goblins"]:
        if g["hp"] <= 0:
            player["gold"] += g["gold"]
            if len(game["dead"]) < 10:
                if "f_hit" in g:
                    del g["f_hit"]
                game["dead"].append(g)
        else:
            alive.append(g)
    game["goblins"] = alive

    if player["hp"] <= 0:
        game["state"] = "dead"


def draw_game(is_frozen, is_lightning):
    screen.fill((255, 255, 255))
    pygame.draw.line(screen, (0, 0, 0), (0, GROUND_Y), (WIDTH, GROUND_Y), 2)
    screen.blit(player_img, (player["px"], player["py"]))

    for b in projectiles["bullets"]:
        screen.blit(effect_images["bullet"], (b["rect"].x - 5, b["rect"].y - 5))

    for f in projectiles["fireballs"]:
        screen.blit(effect_images["fireball"], f["rect"])

    wave_number = min(game["wave"] - 1, 5)
    wave_text = font.render(f"Wave {wave_number}", True, (0, 0, 0))
    screen.blit(wave_text, (WIDTH // 2 - wave_text.get_width() // 2, 150))

    bg_rect = (player["px"], player["py"] - 15, 60, 10)
    pygame.draw.rect(screen, (255, 0, 0), bg_rect)
    health_ratio = max(0, player["hp"] / player["max_hp"])
    fg_rect = (player["px"], player["py"] - 15, 60 * health_ratio, 10)
    pygame.draw.rect(screen, (0, 255, 0), fg_rect)

    draw_ammo_icon = True
    if player["ammo"] <= 0:
        if (pygame.time.get_ticks() // 250) % 2 == 0:
            draw_ammo_icon = False

    if draw_ammo_icon:
        screen.blit(effect_images["ammo"], (player["px"] + 15, player["py"] - 50))

    for g in game["goblins"]:
        screen.blit(g["img"], g["rect"])

        if g["type"] == "shield":
            screen.blit(effect_images["shield"], (g["rect"].centerx - 20, g["rect"].top - 25))
        elif g["type"] == "healer" and game["heal_cd"] > 30:
            screen.blit(effect_images["heal"], (g["rect"].centerx - 15, g["rect"].top - 30))
        elif g["type"] == "necromancer" and game["raise_cd"] > 150:
            screen.blit(effect_images["necro_fx"], (g["rect"].centerx - 20, g["rect"].top - 40))
        if is_lightning:
            screen.blit(effect_images["lightning"], (g["rect"].centerx - 25, g["rect"].centery - 25))
        elif is_frozen:
            screen.blit(effect_images["freeze"], (g["rect"].centerx - 30, g["rect"].centery - 30))

        g_ratio = max(0, g["hp"] / g["max_hp"])
        pygame.draw.rect(screen, (255, 0, 0), (g["rect"].x, g["rect"].y - 10, g["rect"].width, 5))
        pygame.draw.rect(screen, (0, 255, 0), (g["rect"].x, g["rect"].y - 10, g["rect"].width * g_ratio, 5))

    money_text = small_font.render(f"Gold: {player['gold']}", True, (0, 100, 0))
    screen.blit(money_text, (10, 10))
    stats_text = small_font.render(
        f"Dmg: {player['dmg']} | Fire Delay: {player['reload']} | Ammo: {player['ammo']}/{player['max_ammo']}", True,
        (0, 0, 0))
    screen.blit(stats_text, (10, 30))

    upgrades_text1 = small_font.render(
        f"[1] +Dmg ({upgrades['dmg_cost']})  [2] +FireRate ({upgrades['firerate_cost']})",
        True, (0, 0, 255))
    upgrades_text2 = small_font.render(
        f"[3] Heal ({upgrades['heal_cost']})  [4] Restore Abilities ({upgrades['restore_cost']})  [R] Reload Ammo ({UPGRADE_CONFIG['ammo_cost']})",
        True, (0, 0, 255))
    screen.blit(upgrades_text1, (10, 50))
    screen.blit(upgrades_text2, (10, 70))

    f_str = '1' if abilities["fireball"] else 'USED'
    l_str = '1' if abilities["lightning"] else 'USED'
    z_str = '1' if abilities["freeze"] else 'USED'
    abilities_text = small_font.render(f"F: Fireball ({f_str}) | L: Lightning ({l_str}) | Z: Freeze ({z_str})", True,
                                       (150, 0, 150))
    screen.blit(abilities_text, (WIDTH - 450, 10))

    if is_frozen:
        freeze_text = font.render(f"FROZEN: {effects['freeze_cd'] // 60}s", True, (0, 200, 255))
        screen.blit(freeze_text, (WIDTH // 2 - 100, 70))
    elif is_lightning:
        lightning_text = font.render(f"LIGHTNING: {effects['lightning_cd'] // 60}s", True, (200, 200, 0))
        screen.blit(lightning_text, (WIDTH // 2 - 100, 70))

    pygame.display.update()


def draw_menus():
    if game["state"] == "exit_menu":
        s = pygame.Surface((WIDTH, HEIGHT))
        s.set_alpha(128)
        s.fill((0, 0, 0))
        screen.blit(s, (0, 0))
        menu_text = font.render("GAME PAUSED - Press ESC to Resume, Q to Quit", True, (255, 255, 255))
        screen.blit(menu_text, (WIDTH // 2 - menu_text.get_width() // 2, HEIGHT // 2))
        pygame.display.update()

    elif game["state"] == "dead":
        screen.fill((0, 0, 0))
        dead_text = font.render("YOU DIED!, press S to start again", True, (255, 0, 0))
        screen.blit(dead_text, (WIDTH // 2 - dead_text.get_width() // 2, HEIGHT // 2))
        pygame.display.update()

    elif game["state"] == "intro":
        screen.fill((0, 0, 0))
        lines = [
            "GOBLIN SLAYER - HOW TO PLAY",
            "",
            "CONTROLS:",
            "  SPACE = Shoot   |   ESC = Pause   |   Q = Quit",
            "",
            "ABILITIES (Single Use until restored):",
            "  [F] Fireball - Pierces enemies and cuts max HP by 50%",
            "  [L] Lightning - Summons storm that periodically stuns enemies",
            "  [Z] Freeze - Freezes all enemies completely for several seconds",
            "",
            "UPGRADES:",
            "  [1] +Damage   |   [2] +Fire Rate   |   [3] Heal   |   [4] Restore Abilities   |   [R] Reload Ammo",
            "",
            "GOBLIN POWERS:",
            "  Basic Goblins - Fast and common",
            "  Shield Bosses - Takes half damage from bullets",
            "  Healers - Heals surrounding enemies",
            "  Kamikazes - Rushes the player and explodes",
            "  Necromancers - Revives defeated goblins",
            "",
            "Press SPACE to Start Game!"
        ]
        y = 30
        for line in lines:
            if "GOBLIN SLAYER" in line or "Press SPACE" in line:
                text_surf = font.render(line, True, (0, 255, 0) if "SPACE" in line else (255, 255, 0))
                y += 10
            elif line.isupper() and len(line) > 0:
                text_surf = small_font.render(line, True, (255, 100, 100))
                y += 5
            else:
                text_surf = small_font.render(line, True, (200, 200, 200))

            screen.blit(text_surf, (WIDTH // 2 - text_surf.get_width() // 2, y))
            y += 24

        pygame.display.update()


# --- MAIN GAME LOOP ---
while True:
    keys = pygame.key.get_pressed()

    handle_events()

    if game["state"] in ("exit_menu", "dead", "intro"):
        draw_menus()
        clock.tick(60)
        continue

    handle_shooting(keys)
    update_projectiles()
    update_spawns()

    is_frozen, is_lightning = update_status_effects()
    update_goblins(is_frozen)
    handle_collisions()
    handle_deaths()

    draw_game(is_frozen, is_lightning)

    clock.tick(60)
