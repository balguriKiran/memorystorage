from fastapi import FastAPI
import requests
import os
from dotenv import load_dotenv
from cachetools import TTLCache

# Load environment variables
load_dotenv()

AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME")
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")

app = FastAPI()

# Headers for Airtable API
HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

# In-memory cache (max 100 items, expire after 10 minutes)
cache = TTLCache(maxsize=100, ttl=600)

@app.post("/store_memory")
def store_memory(memory: str, tags: str = "", importance: str = "", notes: str = ""):
    """Stores a memory in Airtable and caches it"""
    data = {
        "fields": {
            "Memory": memory,
            "Tags": tags,
            "Importance": importance,
            "Additional Notes": notes
        }
    }
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
    response = requests.post(url, json=data, headers=HEADERS)
    result = response.json()
    
    if "id" in result:
        cache[result["id"]] = result  # Store in cache
    
    return result

@app.get("/get_memories")
def get_memories():
    """Retrieves stored memories from cache or Airtable"""
    if cache:  # If cache is not empty, return cached data
        return {"cached_memories": list(cache.values())}

    # If cache is empty (or expired), fetch from Airtable
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
    response = requests.get(url, headers=HEADERS)
    data = response.json()

    # Update cache with fresh data
    for record in data.get("records", []):
        cache[record["id"]] = record

    return {"fetched_from_airtable": data.get("records", [])}
