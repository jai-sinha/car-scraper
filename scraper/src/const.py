from pathlib import Path
import json

ROOT_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = ".car_cache"

with open(ROOT_DIR/'keys'/'keys.json') as f:
	dict = json.load(f)
	GOOGLE_API_KEY = dict["google"]