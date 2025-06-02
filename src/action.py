import pygame
from enum import Enum, auto

# 按鈕參數
BUTTON_WIDTH = 100
BUTTON_HEIGHT = 50
BUTTON_GAP = 20

class PlayerAction(Enum):
    FOLD = auto()
    CALL_OR_CHECK = auto()
    BET_OR_RAISE = auto()

    @staticmethod
    def get_button_rects(WIDTH, HEIGHT):
        """產生右下角的按鈕區塊（三個）"""
        total_width = 3 * BUTTON_WIDTH + 2 * BUTTON_GAP
        start_x = WIDTH - total_width - 40
        y = HEIGHT - BUTTON_HEIGHT - 80
        return [
            (PlayerAction.FOLD, pygame.Rect(start_x + 0 * (BUTTON_WIDTH + BUTTON_GAP), y, BUTTON_WIDTH, BUTTON_HEIGHT)),
            (PlayerAction.CALL_OR_CHECK, pygame.Rect(start_x + 1 * (BUTTON_WIDTH + BUTTON_GAP), y, BUTTON_WIDTH, BUTTON_HEIGHT)),
            (PlayerAction.BET_OR_RAISE, pygame.Rect(start_x + 2 * (BUTTON_WIDTH + BUTTON_GAP), y, BUTTON_WIDTH, BUTTON_HEIGHT)),
        ]

    @staticmethod
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

    @staticmethod
    def draw_action_buttons(screen, font, button_rects, player_bets, current_player, players):
        """
        在畫面上繪製行動按鈕
        button_rects: [(PlayerAction, pygame.Rect), ...]
        player_bets: 當前每位玩家的下注額
        current_player: 當前玩家編號
        players: 玩家物件列表（用於判斷籌碼）
        """
        colors = {
            PlayerAction.FOLD:  (200, 50, 50),    # 紅色
            PlayerAction.CALL_OR_CHECK: (50, 150, 200),   # 藍色
            PlayerAction.BET_OR_RAISE: (50, 200, 100),   # 綠色
        }
        labels = {
            PlayerAction.FOLD:  "FOLD",
            PlayerAction.CALL_OR_CHECK: "CALL",  # 預設
            PlayerAction.BET_OR_RAISE: "RAISE", # 預設
        }
        # 動態決定 CALL_OR_CHECK 按鈕的文字
        max_bet = max(player_bets)
        if player_bets[current_player] < max_bet:
            labels[PlayerAction.CALL_OR_CHECK] = "CALL"
            colors[PlayerAction.CALL_OR_CHECK] = (50, 150, 200)  # 藍色
        else:
            labels[PlayerAction.CALL_OR_CHECK] = "CHECK"
            colors[PlayerAction.CALL_OR_CHECK] = (180, 180, 180)  # 灰色

        # 動態決定 BET_OR_RAISE 按鈕的文字
        if max_bet == 0 and players[current_player].chips > 0:
            labels[PlayerAction.BET_OR_RAISE] = "BET"
            colors[PlayerAction.BET_OR_RAISE] = (255, 215, 0)  # 黃色
        elif players[current_player].chips > 0:
            labels[PlayerAction.BET_OR_RAISE] = "RAISE"
            colors[PlayerAction.BET_OR_RAISE] = (50, 200, 100)  # 綠色
        else:
            labels[PlayerAction.BET_OR_RAISE] = "ALL IN"
            colors[PlayerAction.BET_OR_RAISE] = (160, 0, 0)  # 黃色

        for action, rect in button_rects:
            pygame.draw.rect(screen, colors[action], rect)
            text = font.render(labels[action], True, (0, 0, 0))
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)