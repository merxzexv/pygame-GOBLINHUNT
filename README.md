# Goblin Slayer

A 2D Pygame game where you survive endless goblin hordes using weapons, abilities, and upgrades.

## Features

* Player starts with 700 max HP.
* Endless waves that become harder over time.
* Multiple enemy types (Base Damage values):

  * **Goblins** (Base DMG: 10) – Fast and common.
  * **Shield Bosses** (Base DMG: 15) – Take reduced bullet damage.
  * **Healers** (Base DMG: 30) – Heal nearby enemies.
  * **Kamikazes** (Base DMG: 50) – Rush the player and explode.
  * **Necromancers** (Base DMG: 60-80) – Revive defeated goblins.

* **Size Modifiers & Gold Yield**: 
  An enemy's size affects their final damage output and how much gold they drop:
  * **Small** (+10% Damage) – Drops 10 Gold
  * **Varying** (+15% Damage) – Drops 15 Gold
  * **Big** (+20% Damage) – Drops 30 Gold
  * **Very Big** (+30% Damage) – Drops 100 Gold

* Special abilities (each requires a shop restore after a single use):

  * **Fireball** – Shoots a massive fireball that pierces enemies and cuts their max HP by 50%.
  * **Lightning** – Summons a thunderstorm that periodically stuns all enemies on screen.
  * **Freeze** – Freezes all enemies completely in place for several seconds.
* Gold-based upgrade system for damage, fire rate, health, and ability restoration.

## Controls

| Key   | Action                |
| ----- | --------------------- |
| Space | Shoot                 |
| R     | Reload Ammo           |
| F     | Fireball              |
| L     | Lightning Storm       |
| Z     | Freeze                |
| Esc   | Pause                 |
| S     | Restart (after death) |
| Q     | Quit                  |

## Shop

| Key | Upgrade            | Cost         | Details                                          |
| --- | ------------------ | ------------ | ------------------------------------------------ |
| 1   | Increase damage    | 100 Gold     | Costs 1.5x more each time. Adds +5 Damage.       |
| 2   | Increase fire rate | 100 Gold     | Costs 1.5x more each time. Reduces shoot delay.  |
| 3   | Restore health     | 50 Gold      | Restores 20 HP. Fixed cost.                      |
| 4   | Restore abilities  | 200 Gold     | Recharges all three abilities. Fixed cost.       |
| R   | Reload Ammo        | 40 Gold      | Instantly maxes out your ammo (50). Fixed cost.  |

## Requirements

* Pygame

## Installation

```bash
pip install -r requirements.txt
python main.py
```
