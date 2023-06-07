import pathlib
import hashlib
import subprocess

root = pathlib.Path(__file__).parent.parent


def ready():
    if get_stored_hash() == compute_hash():
        return True
    else:
        return False


def get_hash_path():
    return root / "data_wizard" / "static" / "srchash.txt"


def get_stored_hash():
    return get_hash_path().read_text()


def set_stored_hash(value):
    return get_hash_path().write_text(value)


def compute_hash(log=False):
    sha = hashlib.sha256()

    def add_files(pattern):
        for path in sorted(root.glob(pattern)):
            if log:
                print(" ", path.relative_to(root))
            sha.update(path.read_bytes())

    add_files("packages/*/src/**/*.js")
    add_files("packages/*/package.json")

    return sha.hexdigest()


def log_hash():
    print("Computing hash...")
    new_hash = compute_hash(log=True)
    print("Old Hash:", get_stored_hash())
    print("New Hash:", new_hash)


def build():
    subprocess.check_call(["npm", "install"])
    subprocess.check_call(["npm", "run", "build"])
    set_stored_hash(compute_hash())


if __name__ == "__main__":
    if ready():
        print("No changes since last build.")
    else:
        log_hash()
        build()
