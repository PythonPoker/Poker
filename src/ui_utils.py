import pygame

class UIUtils:
    
    @staticmethod
    def draw_chip_text(screen, font, chips, start_x, y, card_height):
        chip_text = font.render(f"Chips: {chips}", True, (255, 255, 255))
        chip_text_x = start_x - 180
        chip_text_y = y + card_height // 2 - chip_text.get_height() // 2
        screen.blit(chip_text, (chip_text_x, chip_text_y))

    def draw_bet_text(screen, font, bet, start_x, y, hand, card_height, player_index):
        bet_text = font.render(f"{bet}", True, (0, 255, 255))
        bet_text_x = start_x + (len(hand) * 80 - bet_text.get_width()) // 2
        bet_text_y = y - bet_text.get_height() - 10 if player_index == 0 else y + card_height + 10
        screen.blit(bet_text, (bet_text_x, bet_text_y))

    def draw_hand(screen, hand, card_images, start_x, y, show_hand):
        for j, card in enumerate(hand):
            img = card_images[card] if show_hand else card_images["BACK"]
            x = start_x + j * 80
            screen.blit(img, (x, y))

    def draw_hand_type(screen, font, hand_type, start_x, y, hand, card_height):
        rect_x = start_x
        rect_y = y + card_height - 40
        rect_width = len(hand) * 80
        rect_height = 40
        pygame.draw.rect(
            screen, (60, 60, 60), (rect_x, rect_y, rect_width, rect_height)
        )
        text = font.render(hand_type, True, (255, 255, 255))
        text_x = rect_x + (rect_width - text.get_width()) // 2
        text_y = rect_y + (rect_height - text.get_height()) // 2
        screen.blit(text, (text_x, text_y))

    def draw_action_dot(screen, is_current, start_x, y, hand, card_height):
        if is_current:
            dot_radius = 15
            dot_x = start_x + len(hand) * 80 + 30
            dot_y = y + card_height // 2
            pygame.draw.circle(screen, (255, 215, 0), (dot_x, dot_y), dot_radius)

    def draw_action_on_hand(screen, last_action, start_x, y, hand, card_height):
        if last_action:
            action_font = pygame.font.SysFont(None, 24)
            action_text = action_font.render(last_action, True, (255, 255, 255))
            hand_width = len(hand) * 80
            hand_height = card_height
            action_bg_width = action_text.get_width() + 12
            action_bg_height = action_text.get_height() + 6
            action_bg_x = start_x + (hand_width - action_bg_width) // 2
            action_bg_y = y + (hand_height - action_bg_height) // 2
            pygame.draw.rect(
                screen, (0, 0, 0),
                (action_bg_x, action_bg_y, action_bg_width, action_bg_height),
                border_radius=8
            )
            action_text_x = action_bg_x + (action_bg_width - action_text.get_width()) // 2
            action_text_y = action_bg_y + (action_bg_height - action_text.get_height()) // 2
            screen.blit(action_text, (action_text_x, action_text_y))

    def draw_community_cards(screen, card_images, community_cards, community_card_positions):
        for idx, card in enumerate(community_cards):
            img = card_images[card]
            pos = community_card_positions[idx]
            screen.blit(img, pos)

    def draw_pot_text(screen, font, pot, community_card_positions, width):
        pot_text = font.render(f"Pot: {pot}", True, (255, 255, 0))
        pot_x = width // 2 - pot_text.get_width() // 2
        pot_y = community_card_positions[0][1] - 40
        screen.blit(pot_text, (pot_x, pot_y))

    @staticmethod
    def get_bet_text_pos(start_x, y, hand, card_height, game_setting):
        """
        計算下注額顯示在手牌下方、靠近中心的位置
        """
        hand_width = len(hand) * 80
        hand_center_x = start_x + hand_width // 2
        hand_center_y = y + card_height // 2

        W, H = game_setting["WIDTH"], game_setting["HEIGHT"]
        center_x, center_y = W // 2, H // 2

        bet_text_offset = 200  # 距離中心的偏移量，可自行調整
        dx = center_x - hand_center_x
        dy = center_y - hand_center_y
        length = (dx ** 2 + dy ** 2) ** 0.5
        if length == 0:
            bet_x, bet_y = hand_center_x, hand_center_y
        else:
            bet_x = int(hand_center_x + dx / length * bet_text_offset)
            bet_y = int(hand_center_y + dy / length * bet_text_offset)
        return bet_x, bet_y

    @staticmethod
    def get_community_card_positions(game_setting):
        """
        回傳一個長度為5的list，每個元素是公牌的(x, y)座標
        """
        W, H = game_setting["WIDTH"], game_setting["HEIGHT"]
        CARD_W, CARD_H = game_setting["CARD_WIDTH"], game_setting["CARD_HEIGHT"]
        positions = [
            (W // 2 - 2 * 100 - CARD_W // 2, H // 2 - CARD_H // 2),
            (W // 2 - 100 - CARD_W // 2,     H // 2 - CARD_H // 2),
            (W // 2 - CARD_W // 2,           H // 2 - CARD_H // 2),
            (W // 2 + 100 - CARD_W // 2,     H // 2 - CARD_H // 2),
            (W // 2 + 2 * 100 - CARD_W // 2, H // 2 - CARD_H // 2),
        ]
        return positions

    @staticmethod
    def draw_bet_text_on_hand_edge_toward_community(
        screen, font, bet, start_x, y, hand, card_height, game_setting
    ):
        """
        將下注額顯示在手牌邊緣，朝向公牌方向
        """
        # 計算手牌中心
        hand_width = len(hand) * 80
        hand_height = card_height
        hand_center_x = start_x + hand_width // 2
        hand_center_y = y + hand_height // 2

        # 計算公牌中心
        community_positions = UIUtils.get_community_card_positions(game_setting)
        num_community = 5
        cx = sum([pos[0] + game_setting["CARD_WIDTH"] // 2 for pos in community_positions[:num_community]]) / num_community
        cy = sum([pos[1] + game_setting["CARD_HEIGHT"] // 2 for pos in community_positions[:num_community]]) / num_community

        # 計算方向向量
        dx = cx - hand_center_x
        dy = cy - hand_center_y
        length = (dx ** 2 + dy ** 2) ** 0.5
        if length == 0:
            edge_x, edge_y = hand_center_x, hand_center_y
        else:
            # 偏移手牌寬度/2 + 18px（讓數字在手牌外圍一點點）
            offset = hand_width // 2 + 18
            edge_x = int(hand_center_x + dx / length * offset)
            edge_y = int(hand_center_y + dy / length * offset)

        bet_text = font.render(f"{bet}", True, (0, 255, 255))
        bet_text_rect = bet_text.get_rect(center=(edge_x, edge_y))
        screen.blit(bet_text, bet_text_rect)