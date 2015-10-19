from google.appengine.api import memcache

def get(key):
    "Retrieves key from cache store"
	return memcache.get(key)

def add(key, value, d=60):
    "Adds key and value from cache store. d refers to time in seconds"
	return memcache.add(key, value, 60)
