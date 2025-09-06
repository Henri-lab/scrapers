from .config import BossConfig
from .auth import BossAuth
from .browser import BossBrowser
from .url_builder import BossUrlBuilder
from .data_processor import BossDataProcessor
from .scraper import BossScraper
from .boss_scraper import BossJobScraper, search_boss_jobs, test_scraper

__all__ = [
    'BossConfig',
    'BossAuth', 
    'BossBrowser',
    'BossUrlBuilder',
    'BossDataProcessor',
    'BossScraper',
    'BossJobScraper',
    'search_boss_jobs',
    'test_scraper'
]

__version__ = '2.0.0'