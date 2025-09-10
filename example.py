from importsim.hello import world

world.greet()
print(world.MESSAGE)

print("-" * 20)

from importsim.api.v1 import users

users.greet()
print(users.MESSAGE)
