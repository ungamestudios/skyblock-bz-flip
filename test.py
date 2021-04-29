import hashlib
data='temp'.encode('utf-8')
hash=hashlib.sha256()
hash.update(data)
print(hash.digest())