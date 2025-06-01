import random
import os
import pygame

class Deck:
    suits = ['S', 'H', 'D', 'C']  # 黑桃、紅心、方塊、梅花
    ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']

    def __init__(self):
        self.cards = [rank + suit for suit in self.suits for rank in self.ranks]
        self.card_images = {}

    def shuffle(self):
        random.shuffle(self.cards)

    def deal_player_hands(self, num_players=2, cards_per_player=2):
        hands = []
        for _ in range(num_players):
            hand = []
            for _ in range(cards_per_player):
                hand.append(self.cards.pop(0))
            hands.append(hand)
        return hands

    def deal_community_cards(self, community_cards, deal_index, last_deal_time, interval=3000):
        """發公牌：前三張一起，之後每interval毫秒一張，最多五張"""
        now = pygame.time.get_ticks()
        if deal_index == 0 and len(community_cards) < 3:
            for _ in range(3):
                community_cards.append(self.cards.pop(0))
            deal_index = 3
            last_deal_time = now
        elif deal_index < 5 and now - last_deal_time >= interval:
            community_cards.append(self.cards.pop(0))
            deal_index += 1
            last_deal_time = now
        return deal_index, last_deal_time

    def load_card_images(self, img_folder="assets/img", size=(80, 120)):
        """載入所有撲克牌圖片，回傳字典 {卡牌名稱: 圖片物件}"""
        self.card_images = {}
        for suit in self.suits:
            for rank in self.ranks:
                card_name = rank + suit
                img_path = os.path.join(img_folder, f"{card_name}.png")
                if os.path.exists(img_path):
                    img = pygame.image.load(img_path)
                    img = pygame.transform.scale(img, size)
                    self.card_images[card_name] = img
                else:
                    print(f"警告：找不到圖片 {img_path}")
                back_path = os.path.join(img_folder, "back.jpg")

        if os.path.exists(back_path):
            back_img = pygame.image.load(back_path)
            back_img = pygame.transform.scale(back_img, size)
            self.card_images["BACK"] = back_img
        else:
            print(f"警告：找不到圖片 {back_path}")

        return self.card_images     
