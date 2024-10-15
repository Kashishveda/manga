import requests
from bs4 import BeautifulSoup
import json
import telegram

class MangaTracker:
    def __init__(self, manga_names, manga_urls, debug=False):
        self.manga_names = manga_names
        self.manga_chapters_file = 'manga_chapters.json'
        self.chapter_info = self.load_chapter_info()
        self.telegram_token = "7710671633:AAFlEecPu60ZSauYAw-J_9q28nRVxP0F1BY"
        self.chat_id = "7829963464"
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
            
    def send_telegram_message(self, message):
        """Send a message to the Telegram bot."""
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message
        }
        response = requests.post(url, json=payload) # Optional: To check the response
        
        # Optional: Log the status of the response
        if response.status_code == 200:
            self.log(f"Message sent successfully: {message}")
        else:
            self.log(f"Failed to send message. Status code: {response.status_code}, Response: {response.text}")

    def get_latest_chapter(self, manga_name, site_name, url):
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find manga element
            manga_element = soup.find('a', title=manga_name)
            if manga_element:
                # Check which site we are using and extract chapter info accordingly
                if site_name == "manganato":
                    chapter_element = manga_element.find_next('p', class_='a-h item-chapter')
                elif site_name == "demonmanga":
                    chapter_element = manga_element.find_next('div', class_='flex flex-row chap-date justify-space-between')

                if chapter_element:
                    latest_chapter_link = chapter_element.find('a')
                    latest_chapter_text = latest_chapter_link.text.strip()

                    # Ensure the chapter text contains "Chapter"
                    if "Chapter " in latest_chapter_text:
                        try:
                            # Extract chapter number and handle both integer and decimal numbers
                            latest_chapter_number = float(latest_chapter_text.split("Chapter ")[1].split(":")[0].strip())
                            self.log(f"Latest chapter for {manga_name} on {site_name}: {latest_chapter_number}")
                            return latest_chapter_number
                        except (IndexError, ValueError) as e:
                            self.log(f"Error extracting chapter number from '{latest_chapter_text}' for '{manga_name}' on {site_name}: {e}")
                            return None
                    else:
                        self.log(f"Unexpected format in chapter info for '{manga_name}' on {site_name}: {latest_chapter_text}")
                        return None
                else:
                    self.log(f"No chapter info found for '{manga_name}' on {site_name}.")
                    return None
            else:
                self.log(f"Manga '{manga_name}' not found on {site_name}.")
                return None

        except Exception as e:
            self.log(f"Error retrieving data for '{manga_name}' on {site_name}: {e}")
            return None

    def check_mangas(self):
        for site_name, url in self.manga_urls.items():
            self.log(f"Checking {site_name}...")
            for manga_name in self.manga_names:
                latest_chapter = self.get_latest_chapter(manga_name, site_name, url)
                if latest_chapter is not None:
                    stored_chapter = self.chapter_info.get(manga_name, 0)

                    if latest_chapter > stored_chapter:
                        message = f"Update available for '{manga_name}': Chapter {latest_chapter} is now out! Check {site_name}"
                        self.send_telegram_message(message)
                        self.chapter_info[manga_name] = latest_chapter  # Update stored chapter

        self.save_chapter_info()


manga_names = [
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
    "Cultivating the supreme dantian",
    "Death God",
    "Doctor’s Rebirth",
    "Doupo Cangqiong",
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
    "Dragon Prince Yuan",
    "Yuan Zun"
    ]

manga_urls = {
    "demonmanga": "https://ciorti.online/lastupdates.php",
    "manganato": "https://manganato.com/"
}

tracker = MangaTracker(manga_names, manga_urls, debug=True)
tracker.check_mangas()
