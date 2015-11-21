from google.appengine.api import memcache

def get(key):
	return memcache.get(key)

def add(key, value, d=60):
	return memcache.add(key, value, 60)
