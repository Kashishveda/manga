import aiohttp
import asyncio
from bs4 import BeautifulSoup
import json
import os

class MangaTracker:
    def __init__(self, manga_names, manga_urls, debug=False):
        self.manga_names = manga_names
        self.manga_chapters_file = 'manga_chapters.json'
        self.chapter_info = self.load_chapter_info()
        self.telegram_token = os.getenv("TELEGRAM_TOKEN")  # This fetches the secret value
        self.chat_id = os.getenv("CHAT_ID")                # This fetches the chat ID
        self.manga_urls = manga_urls
        self.debug = debug

    def log(self, message):  # Custom logging method
        if self.debug:
            print(message)

    def load_chapter_info(self):
        try:
            with open(self.manga_chapters_file, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            # Initialize chapter info for each manga
            return {name: 0 for name in self.manga_names}

    def save_chapter_info(self):
        with open(self.manga_chapters_file, 'w') as file:
            json.dump(self.chapter_info, file)

    async def fetch(self, session, url):
        try:
            async with session.get(url) as response:
                return await response.text()
        except Exception as e:
            self.log(f"Error fetching data from {url}: {e}")
            return None

    async def parse_site(self, site_name, url, session):
        html_content = await self.fetch(session, url)
        if not html_content:
            return {}

        soup = BeautifulSoup(html_content, 'html.parser')
        latest_chapters = {}

        # Iterate over all manga names and try to extract chapter info from the single HTML page
        for manga_name in self.manga_names:
            manga_element = soup.find('a', title=manga_name)
            if manga_element:
                if site_name == "manganato":
                    chapter_element = manga_element.find_next('p', class_='a-h item-chapter')
                elif site_name == "demonmanga":
                    chapter_element = manga_element.find_next('div', class_='flex flex-row chap-date justify-space-between')

                if chapter_element:
                    latest_chapter_link = chapter_element.find('a')
                    latest_chapter_text = latest_chapter_link.text.strip()

                    if "Chapter " in latest_chapter_text:
                        try:
                            latest_chapter_number = float(latest_chapter_text.split("Chapter ")[1].split(":")[0].strip())
                            latest_chapters[manga_name] = latest_chapter_number
                            self.log(f"Latest chapter for {manga_name} on {site_name}: {latest_chapter_number}")
                        except (IndexError, ValueError) as e:
                            self.log(f"Error extracting chapter number from '{latest_chapter_text}' for '{manga_name}' on {site_name}: {e}")
                    else:
                        self.log(f"Unexpected format in chapter info for '{manga_name}' on {site_name}: {latest_chapter_text}")
            else:
                self.log(f"Manga '{manga_name}' not found on {site_name}.")
        
        return site_name, latest_chapters

    async def send_telegram_message(self, message):
        """Send a message to the Telegram bot asynchronously."""
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    self.log(f"Message sent successfully: {message}")
                else:
                    self.log(f"Failed to send message. Status code: {response.status}, Response: {await response.text()}")

    async def check_mangas(self):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for site_name, url in self.manga_urls.items():
                self.log(f"Checking {site_name}...")
                task = asyncio.create_task(self.parse_site(site_name, url, session))
                tasks.append(task)

            # Gather results for all sites
            results = await asyncio.gather(*tasks)

            for site_name, result in results:
                for manga_name, latest_chapter in result.items():
                    stored_chapter = self.chapter_info.get(manga_name, 0)

                    if latest_chapter > stored_chapter:
                        message = f"Git: Update available for '{manga_name}': Chapter {latest_chapter} is now out! Check {site_name}"
                        await self.send_telegram_message(message)
                        self.chapter_info[manga_name] = latest_chapter  # Update stored chapter

        self.save_chapter_info()

# Running the tracker
manga_names = [
    # List of manga names...
    "A Modern Man Who Got Transmigrated Into the Murim World",
    "Absolute Sword Sense",
    "Academy’s Genius Swordsman",
    "Against the Gods",
    "Apotheosis",
    "Arcane Sniper",
    "Becoming the Sacheon Dang's Swordsmaster-Rank Young Lord",
    "Black Corporation: Joseon",
    "Bloodhound’s Regression Instinct",
    "Chronicles of the Demon Faction",
    "Cosmic Heavenly Demon 3077",
    "Cultivating the supreme dantian",
    "Death God",
    "Doctor’s Rebirth",
    "Doupo Cangqiong",
    "Dragon Prince Yuan",
    "Dragon-Devouring Mage",
    "Genius of the Unique Lineage",
    "Global Martial Arts",
    "God of Martial Arts",
    "Healing Life Through Camping In Another World",
    "Heavenly Grand Archive’s Young Master",
    "Heavenly Inquisition Sword (Nine Heavens Swordmaster)",
    "Holy Emperor's Grandson Is a Necromancer",
    "How the Pro in His Past Life Sucks the Sweet Honey",
    "I'm Being Raised By Villains",
    "I Work Nine To Five In The Immortal Cultivation World",
    "Infinite Mage",
    "Insanely Talented Player",
    "Keep A Low Profile, Sect Leader!",
    "King of Manifestations",
    "Legend of Star General",
    "Lightning Degree",
    "Lord of Destiny Wheel",
    "Magic Academy’s Genius Blinker",    
    "Magic Emperor",
    "Margrave’s Bastard Son was The Emperor", 
    "Martial God Regressed to Level 2",
    "Martial inverse",
    "Martial Peak",  
    "Murim Login",
    "My Clone is the Space Bug King",
    "My Lucky Encounter From The Game Turned Into Reality",
    "My Ruined Academy",
    "My School Life Pretending To Be a Worthless Person",
    "Nano Machine",
    "Necromancer's Evolutionary Traits",
    "Overgeared",
    "Paranoid Mage",
    "Path of the Shaman",
    "Player Who Returned 10,000 Years Later",
    "Ranker Who Lives A Second Time",
    "Reborn As A Monster",
    "Records of the Swordsman Scholar",
    "Regressor Instruction Manual",
    "Regressor of the Fallen family",
    "Release That Witch",
    "Return of the Frozen Player",
    "Return of the Mount Hua Sect",
    "Return of the Legendary Spear Knight",
    "Revenge of the Sword Clan's Hound",
    "Snake Ancestor",
    "Solo Farming in the Tower",
    "Solo Max-Level Newbie",
    "Song Baek",
    "Soul Land V",
    "Starting From Today I'll Work As A City Lord",
    "Swallowed Star",
    "Sword Fanatic Wanders Through The Night",
    "Swordmaster’s Youngest Son", 
    "Surviving the Game as a Barbarian", 
    "Surviving as a Mage in a Magic Academy",
    "Tale of a Scribe Who Retires to the Countryside", 
    "Talent Copycat",
    "Tales of Demons and Gods",
    "Talent-Swallowing Magician",
    "Terminally-Ill Genius Dark Knight",
    "The Archmage's Restaurant",
    "The Count’s Youngest Son is A Player",
    "The Crown Prince That Sells Medicine",
    "The Dark Magician Transmigrates After 66666 Years",
    "The Devil Butler",
    "The Extra’s Academy Survival Guide",
    "The Greatest Estate Designer",
    "The Hero Returns",
    "The Heavenly Demon Can't Live a Normal Life",
    "The Indomitable Martial King",
    "The Knight King Who Returned With a God",
    "The Magic Genius of the Marquis",
    "The Max Level Hero has Returned!",
    "The Nebula's Civilization",
    "The Primal Hunter",
    "The Lone Necromancer",
    "The Lord's Coins Aren't Decreasing?!",
    "The Reborn Young Lord Is An Assassin",
    "The Return of The Disaster-Class Hero",
    "The Twin Swords Of The Sima Clan",
    "The Tutorial Is Too Hard",
    "The Ultimate of All Ages",
    "To Hell With Being A Saint, I’m A Doctor",
    "Transcension Academy",
    "Warrior Grandpa and Grandmaster daughter",
    "Warrior Grandpa and Supreme Granddaughter",
    "World’s Greatest Senior Disciple",
    "Yuan Zun"
]

manga_urls = {
    "demonmanga": "https://ciorti.online/lastupdates.php",
    "manganato": "https://manganato.com/"
}

tracker = MangaTracker(manga_names, manga_urls, debug=False)
asyncio.run(tracker.check_mangas())
