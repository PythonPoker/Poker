import pygame
from enum import Enum, auto

# 按鈕參數
BUTTON_WIDTH = 100
BUTTON_HEIGHT = 50
BUTTON_GAP = 20

class PlayerAction(Enum):
    FOLD = auto()
    CHECK = auto()
    CALL = auto()
    RAISE = auto()

    def get_button_rects(WIDTH, HEIGHT):
        """產生右下角的按鈕區塊"""
        total_width = 4 * BUTTON_WIDTH + 3 * BUTTON_GAP
        start_x = WIDTH - total_width -40   # 右邊留40像素邊距
        y = HEIGHT - BUTTON_HEIGHT - 80     # 下方留40像素邊距
        return [
            (PlayerAction.FOLD,  pygame.Rect(start_x + 0 * (BUTTON_WIDTH + BUTTON_GAP), y, BUTTON_WIDTH, BUTTON_HEIGHT)),
            (PlayerAction.CHECK, pygame.Rect(start_x + 1 * (BUTTON_WIDTH + BUTTON_GAP), y, BUTTON_WIDTH, BUTTON_HEIGHT)),
            (PlayerAction.CALL,  pygame.Rect(start_x + 2 * (BUTTON_WIDTH + BUTTON_GAP), y, BUTTON_WIDTH, BUTTON_HEIGHT)),
            (PlayerAction.RAISE, pygame.Rect(start_x + 3 * (BUTTON_WIDTH + BUTTON_GAP), y, BUTTON_WIDTH, BUTTON_HEIGHT)),
        ]

    def get_player_action(buttons, mouse_pos, mouse_pressed):
        """
        根據按鈕區域與滑鼠狀態，回傳玩家選擇的行動
        buttons: [(PlayerAction, pygame.Rect), ...]
        mouse_pos: 滑鼠座標
        mouse_pressed: 滑鼠按下狀態
        """
        if mouse_pressed[0]:  # 左鍵
            for action, rect in buttons:
                if rect.collidepoint(mouse_pos):
                    return action
        return None

    def draw_action_buttons(screen, font, button_rects):
        """
        在畫面上繪製行動按鈕
        button_rects: [(PlayerAction, pygame.Rect), ...]
        """
        colors = {
            PlayerAction.FOLD:  (200, 50, 50),    # 紅色
            PlayerAction.CHECK: (180, 180, 180),  # 灰色
            PlayerAction.CALL:  (50, 150, 200),   # 藍色
            PlayerAction.RAISE: (50, 200, 100),   # 綠色
        }
        labels = {
            PlayerAction.FOLD:  "FOLD",
            PlayerAction.CHECK: "CHECK",
            PlayerAction.CALL:  "CALL",
            PlayerAction.RAISE: "RAISE",
        }
        for action, rect in button_rects:
            pygame.draw.rect(screen, colors[action], rect)
            text = font.render(labels[action], True, (0, 0, 0))
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)