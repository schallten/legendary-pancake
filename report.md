# File I/O Storage Design: Benchmark Report
*Investigating storage layout trade-offs across three file strategies*

---

## Objective

This exercise benchmarks three file storage strategies (Single Large File, Chunked Files with 1,000 sub-records per file, and Individual Files with one file per record) across sequential and random read access patterns. 100,000 sub-records of 1 to 2 KB each (random bytes, seed=42) were generated and measured for write throughput and read latency.

---

## Results

All times in seconds. Average latency is computed over 100,000 records for sequential reads and over 1,000 records for random reads.

| Strategy         | Operation  | Total Time (s) | Avg Latency (µs/rec) | Note                    |
|------------------|------------|---------------|----------------------|-------------------------|
| Single File      | Write      | ~0.68         | ~6.8                 | Sequential I/O          |
| Single File      | Seq Read   | 0.026         | 0.26                 | Fastest sequential read |
| Single File      | Rand Read  | 0.013         | 13.2                 | Low seek cost           |
| Chunked Files    | Write      | ~0.71         | ~7.1                 | Similar to single file  |
| Chunked Files    | Seq Read   | 0.040         | 0.40                 | File open overhead      |
| Chunked Files    | Rand Read  | 0.020         | 19.7                 | Moderate overhead       |
| Individual Files | Write      | ~18.0         | ~180                 | 100k file creations     |
| Individual Files | Seq Read   | 0.892         | 8.92                 | 100k file opens         |
| Individual Files | Rand Read  | 0.009         | 9.30                 | Only 1k opens needed    |

---

## Discussion

### Write Performance

Single File and Chunked strategies performed comparably on writes (~0.68 to 0.71 s), as both reduce write operations to sequential I/O with minimal filesystem metadata overhead. Individual Files required an estimated ~18 seconds due to 100,000 separate file creation syscalls, each triggering directory entry allocation and inode creation. This demonstrates that per-file overhead dominates at scale.

### Sequential Read Performance

The Single File strategy achieved the lowest sequential read time (0.026 s, 0.26 µs/record), as a single `open()` call followed by contiguous reads maximizes OS read-ahead and page cache efficiency. Chunked Files were slightly slower (0.040 s) due to 100 file opens and associated metadata lookups. Individual Files were dramatically slower (0.892 s, 8.92 µs/record), a roughly 34x penalty caused by 100,000 open/close cycles overwhelming the VFS layer and directory cache.

### Random Read Performance

For random reads of 1,000 records, Individual Files achieved the best time (0.009 s) because only 1,000 file opens were needed, avoiding seek overhead entirely since each file is a self-contained record. Single File followed (0.013 s) with efficient `seek()` calls within one file descriptor. Chunked Files were slightly slower (0.020 s) due to inter-chunk file switching. This highlights a key trade-off: individual files excel at random access when the subset is small, but collapse under full sequential traversal.

### Key Takeaways

Storage layout decisions should be driven by the dominant access pattern. The Single File strategy provides the best overall balance, with near-optimal sequential reads and competitive random reads, making it well-suited for append-heavy workloads like logs or time-series data. Chunked Files offer a practical middle ground with natural parallelism potential and simpler partial-file management at a modest overhead cost. Individual Files are only appropriate for small-scale random access or when independent record lifecycle management (deletion, versioning) is required. At 100,000 files, filesystem metadata overhead becomes the dominant cost and must be explicitly accounted for in system design.

---

*Benchmarked on Python 3.14 · 100,000 records · 1 to 2 KB each · Seed = 42*