#!/usr/bin/env python

import bcrypt

# passwd = b's$cret12'
passwd = 's$cret12'

salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(passwd.encode("utf-8"), salt)

print(salt)
print(hashed)
