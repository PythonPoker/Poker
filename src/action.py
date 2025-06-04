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
            (
                PlayerAction.FOLD,
                pygame.Rect(
                    start_x + 0 * (BUTTON_WIDTH + BUTTON_GAP),
                    y,
                    BUTTON_WIDTH,
                    BUTTON_HEIGHT,
                ),
            ),
            (
                PlayerAction.CALL_OR_CHECK,
                pygame.Rect(
                    start_x + 1 * (BUTTON_WIDTH + BUTTON_GAP),
                    y,
                    BUTTON_WIDTH,
                    BUTTON_HEIGHT,
                ),
            ),
            (
                PlayerAction.BET_OR_RAISE,
                pygame.Rect(
                    start_x + 2 * (BUTTON_WIDTH + BUTTON_GAP),
                    y,
                    BUTTON_WIDTH,
                    BUTTON_HEIGHT,
                ),
            ),
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
    def draw_action_buttons(
        screen,
        font,
        button_rects,
        player_bets,
        current_player,
        players,
        raise_input=None,
        min_raise=10,
        max_raise=1000,
        raise_button_text="RAISE",
        call_button_text="CALL",
    ):
        """
        在畫面上繪製行動按鈕
        raise_input: 若不為None，顯示在RAISE按鈕上方的輸入框
        min_raise, max_raise: 顯示於提示
        """
        colors = {
            PlayerAction.FOLD: (200, 50, 50),  # 紅色
            PlayerAction.CALL_OR_CHECK: (50, 150, 200),  # 藍色
            PlayerAction.BET_OR_RAISE: (50, 200, 100),  # 綠色
        }
        labels = {
            PlayerAction.FOLD: "FOLD",
            PlayerAction.CALL_OR_CHECK: call_button_text,  # 預設
            PlayerAction.BET_OR_RAISE: raise_button_text,  # 預設
        }

        # 動態顏色設定
        if call_button_text == "ALL-IN":
            colors[PlayerAction.CALL_OR_CHECK] = (180, 0, 0)
        elif call_button_text == "CALL":
            colors[PlayerAction.CALL_OR_CHECK] = (50, 150, 200)
        elif call_button_text == "CHECK":
            colors[PlayerAction.CALL_OR_CHECK] = (180, 180, 180)

        if raise_button_text == "ALL-IN":
            colors[PlayerAction.BET_OR_RAISE] = (180, 0, 0)
        elif raise_button_text == "BET":
            colors[PlayerAction.BET_OR_RAISE] = (255, 215, 0)
        elif raise_button_text == "RAISE":
            colors[PlayerAction.BET_OR_RAISE] = (50, 200, 100)

        for action, rect in button_rects:
            pygame.draw.rect(screen, colors[action], rect)
            text = font.render(labels[action], True, (0, 0, 0))
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)

            # 如果是BET_OR_RAISE且raise_input不為None，畫輸入框在按鈕上方
            if action == PlayerAction.BET_OR_RAISE and raise_input is not None:
                input_rect = pygame.Rect(rect.x, rect.y - 60, rect.width, 40)
                pygame.draw.rect(screen, (255, 255, 255), input_rect, 2)
                input_text = font.render(str(raise_input), True, (255, 255, 0))
                # 讓文字靠右顯示
                text_x = input_rect.right - input_text.get_width() - 10
                text_y = input_rect.y + 5
                screen.blit(input_text, (text_x, text_y))

    def handle_raise_input(event, current_text, min_raise, max_raise):
        """處理加注輸入框的事件，回傳新字串"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                return current_text[:-1]
            elif event.unicode.isdigit():
                # 限制長度避免太大
                if len(current_text) < 6:
                    return current_text + event.unicode
        return current_text

    @staticmethod
    def get_raise_input_rect(button_rects):
        """取得BET/RAISE按鈕上方的輸入框rect"""
        for action, rect in button_rects:
            if action == PlayerAction.BET_OR_RAISE:
                return pygame.Rect(rect.x, rect.y - 60, rect.width, 40)
        return None
