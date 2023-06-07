from .builder import ready, build


if ready():
    print("No changes since last build.")
else:
    build()
