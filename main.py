import os
import random
import shutil
import time
from pathlib import Path

base_dir = Path("storage_test")
num_records = 100_000
min_size = 1024
max_size = 2048
chunk_size = 1000
random_reads = 1000
seed = 42


def clean_dir(path):
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)


def timer(fn):
    start = time.perf_counter()
    fn()
    return time.perf_counter() - start


def generate():
    random.seed(seed)
    return [os.urandom(random.randint(min_size, max_size))
            for _ in range(num_records)]


# --- single file ---

def write_single(records):
    path = base_dir / "single"
    clean_dir(path)
    file = path / "data.bin"

    index = []
    offset = 0
    with open(file, "wb") as f:
        for r in records:
            f.write(r)
            index.append((offset, len(r)))
            offset += len(r)
    return file, index


def read_single(file, index, random_mode=False):
    random.seed(seed)
    with open(file, "rb") as f:
        if random_mode:
            ids = random.sample(range(num_records), random_reads)
        else:
            ids = range(num_records)

        for i in ids:
            off, size = index[i]
            f.seek(off)
            f.read(size)


# --- chunked ---

def write_chunked(records):
    path = base_dir / "chunked"
    clean_dir(path)

    index = []
    for start in range(0, num_records, chunk_size):
        file = path / f"chunk_{start//chunk_size}.bin"
        offset = 0
        with open(file, "wb") as f:
            for r in records[start:start+chunk_size]:
                f.write(r)
                index.append((file, offset, len(r)))
                offset += len(r)
    return index


def read_chunked(index, random_mode=False):
    random.seed(seed)
    ids = (random.sample(range(num_records), random_reads)
           if random_mode else range(num_records))

    files = {}
    for i in ids:
        file, off, size = index[i]
        if file not in files:
            files[file] = open(file, "rb")
        f = files[file]
        f.seek(off)
        f.read(size)

    for f in files.values():
        f.close()


# --- individual files ---

def write_individual(records):
    path = base_dir / "individual"
    clean_dir(path)
    for i, r in enumerate(records):
        with open(path / f"rec_{i:06d}.bin", "wb") as f:
            f.write(r)
    return path


def read_individual(path, random_mode=False):
    random.seed(seed)
    ids = (random.sample(range(num_records), random_reads)
           if random_mode else range(num_records))

    for i in ids:
        with open(path / f"rec_{i:06d}.bin", "rb") as f:
            f.read()


# --- main ---

def main():
    clean_dir(base_dir)

    records = generate()

    print("single write")
    t = timer(lambda: write_single(records))
    file, idx1 = write_single(records)

    print("single seq", timer(lambda: read_single(file, idx1)))
    print("single rand", timer(lambda: read_single(file, idx1, True)))

    print("chunked write")
    idx2 = write_chunked(record )

    print("chunked seq", timer(lambda: read_chunked(idx2)))
    print("chunked rand", timer(lambda: read_chunked(idx2, True)))

    print("individual write")
    path = write_individual(records)

    print("individual seq", timer(lambda: read_individual(path)))
    print("individual rand", timer(lambda: read_individual(path, True)))


if __name__ == "__main__":
    main()