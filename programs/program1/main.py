#!/usr/bin/env python3
"""
Sample Python Program 1 - Twitch Channel Points Miner Demo
This program simulates a Twitch channel points mining application.
"""

import time
import random
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class TwitchMinerDemo:
    def __init__(self):
        self.streamers = [
            "streamer_gaming", "tech_streamer", "music_channel", 
            "art_creator", "just_chatting_stream"
        ]
        self.points_collected = 0
        self.active_streams = []
        self.watch_streak = 0
        
    def check_online_streams(self):
        """Check which streamers are currently online"""
        # Simulate streamers going online/offline
        online_streamers = []
        for streamer in self.streamers:
            if random.random() > 0.6:  # 40% chance of being online
                online_streamers.append(streamer)
        
        # Update active streams
        new_streams = set(online_streamers) - set(self.active_streams)
        ended_streams = set(self.active_streams) - set(online_streamers)
        
        for stream in new_streams:
            logger.info(f"🔴 {stream} перешел в онлайн!")
            
        for stream in ended_streams:
            logger.info(f"⚫ {stream} завершил трансляцию")
            
        self.active_streams = online_streamers
        return online_streamers
    
    def collect_points(self):
        """Simulate collecting channel points"""
        if not self.active_streams:
            return 0
            
        points_earned = 0
        for stream in self.active_streams:
            # Simulate different point earning scenarios
            base_points = random.randint(10, 50)
            bonus_points = 0
            
            # Watch streak bonus
            if self.watch_streak > 0:
                bonus_points += random.randint(5, 15)
                
            # Random bonus events
            if random.random() < 0.1:  # 10% chance
                bonus_points += random.randint(50, 200)
                logger.info(f"💰 Бонус очки от {stream}: +{bonus_points}")
            
            total = base_points + bonus_points
            points_earned += total
            
            if total > base_points:
                logger.info(f"⭐ {stream}: +{total} очков (базовые: {base_points}, бонус: {bonus_points})")
            else:
                logger.debug(f"{stream}: +{total} очков")
        
        self.points_collected += points_earned
        if points_earned > 0:
            logger.info(f"Собрано очков: +{points_earned} | Всего: {self.points_collected}")
        
        return points_earned
    
    def check_predictions(self):
        """Simulate prediction betting"""
        if random.random() < 0.15:  # 15% chance of prediction
            stream = random.choice(self.active_streams) if self.active_streams else "random_stream"
            bet_amount = random.randint(10, 100)
            
            logger.info(f"🎯 Новое предсказание на {stream} - ставка: {bet_amount} очков")
            
            # Simulate prediction result after some time
            if random.random() > 0.5:  # 50% chance to win
                winnings = bet_amount * random.uniform(1.2, 3.0)
                logger.info(f"🎉 Предсказание выиграно! +{winnings:.0f} очков")
                self.points_collected += int(winnings)
            else:
                logger.info(f"❌ Предсказание проиграно: -{bet_amount} очков")
                self.points_collected = max(0, self.points_collected - bet_amount)
    
    def check_drops(self):
        """Simulate Twitch drops"""
        if random.random() < 0.05:  # 5% chance of drop
            games = ["Game Alpha", "Beta Shooter", "Indie Puzzle", "Racing Pro"]
            game = random.choice(games)
            logger.info(f"📦 Дроп получен для игры: {game}")
    
    def update_watch_streak(self):
        """Update watch streak"""
        if self.active_streams:
            self.watch_streak += 1
            if self.watch_streak % 10 == 0:
                logger.info(f"🔥 Достигнута серия просмотра: {self.watch_streak} дней")
        else:
            if self.watch_streak > 0:
                logger.warning("⚠️ Серия просмотра прервана - нет активных трансляций")
                self.watch_streak = 0

def main():
    """Main program loop"""
    logger.info("🚀 Twitch Channel Points Miner запущен")
    logger.info("Инициализация системы сбора очков...")
    
    miner = TwitchMinerDemo()
    cycle_count = 0
    
    try:
        while True:
            cycle_count += 1
            logger.info(f"=== Цикл мониторинга {cycle_count} ===")
            
            # Check for online streams
            online_streams = miner.check_online_streams()
            logger.info(f"Активных трансляций: {len(online_streams)}")
            
            if online_streams:
                # Collect channel points
                miner.collect_points()
                
                # Check for predictions
                miner.check_predictions()
                
                # Check for drops
                miner.check_drops()
                
                # Update watch streak
                miner.update_watch_streak()
            else:
                logger.info("Ожидание онлайн трансляций...")
            
            # Generate periodic statistics
            if cycle_count % 5 == 0:
                logger.info(f"📊 Статистика: {miner.points_collected} очков, серия: {miner.watch_streak} дней")
            
            # Simulate chat activity
            if random.random() < 0.2 and online_streams:  # 20% chance
                stream = random.choice(online_streams)
                logger.info(f"💬 Активность в чате: {stream}")
            
            # Wait before next cycle
            wait_time = random.uniform(3, 8)
            logger.debug(f"Ожидание {wait_time:.1f}с до следующего цикла...")
            time.sleep(wait_time)
            
    except KeyboardInterrupt:
        logger.info("Получен сигнал завершения")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {str(e)}")
        raise
    finally:
        logger.info("Twitch Channel Points Miner завершает работу...")
        logger.info(f"Итоговая статистика:")
        logger.info(f"- Всего очков собрано: {miner.points_collected}")
        logger.info(f"- Серия просмотра: {miner.watch_streak} дней")
        logger.info(f"- Циклов выполнено: {cycle_count}")

if __name__ == "__main__":
    main()