#!/usr/bin/env python3
import os
import gc
import sys
import time
import ctypes
import psutil
import yaml
import logging

logging.basicConfig(level=logging.INFO, format="[MEMORY_MGR] %(asctime)s - %(levelname)s - %(message)s")


class CacheCleanerEngine:
    def __init__(self, config_path: str = "config/control_params.yaml"):
        with open(config_path, 'r') as f:
            self.cfg = yaml.safe_load(f)['memory_manager']

        self.threshold = self.cfg['ram_critical_threshold_percent']
        self.target_free_mb = self.cfg['target_free_ram_mb']
        self.drop_caches_enabled = self.cfg.get('enable_linux_drop_caches', True)

    def force_python_gc(self) -> int:
        """Forces full generation 0, 1, and 2 Python garbage collection."""
        collected = gc.collect()
        logging.info(f"Garbage collector freed {collected} unreferenced objects.")
        return collected

    def trim_glibc_heap(self):
        """Forces the C runtime allocator (glibc) to release free memory back to OS."""
        try:
            libc = ctypes.CDLL("libc.so.6")
            libc.malloc_trim(0)
            logging.info("Triggered malloc_trim(0) to reclaim heap space.")
        except Exception as e:
            logging.warning(f"Unable to run malloc_trim: {e}")

    def drop_linux_pagecache(self):
        """Clears Linux kernel pagecache, dentries, and inodes if running with elevated privileges."""
        if not self.drop_caches_enabled:
            return

        try:
            if os.path.exists("/proc/sys/vm/drop_caches"):
                with open("/proc/sys/vm/drop_caches", "w") as f:
                    f.write("3\n")
                logging.info("Flushed Linux kernel PageCache, Dentries, and Inodes.")
        except PermissionError:
            logging.warning("Insufficient permissions to write to /proc/sys/vm/drop_caches. (Run with sudo)")
        except Exception as e:
            logging.error(f"Failed to drop OS caches: {e}")

    def purge_temp_and_pycache(self):
        """Scans and clears local pycache and temporary buffer directories."""
        for root, dirs, files in os.walk("."):
            for d in dirs:
                if d == "__pycache__":
                    pycache_path = os.path.join(root, d)
                    try:
                        for f in os.listdir(pycache_path):
                            os.remove(os.path.join(pycache_path, f))
                    except Exception:
                        pass

    def optimize_memory(self, force: bool = False):
        """Evaluates RAM pressure and executes aggressive memory recovery if threshold is breached."""
        mem = psutil.virtual_memory()
        used_percent = mem.percent
        free_mb = mem.available / (1024 * 1024)

        if used_percent >= self.threshold or free_mb < self.target_free_mb or force:
            logging.warning(
                f"High RAM usage detected: {used_percent}% used ({free_mb:.1f} MB available). Initiating Cache Clean...")

            # Step 1: Python GC
            self.force_python_gc()

            # Step 2: C-level memory trim
            self.trim_glibc_heap()

            # Step 3: Temporary filesystem cache purge
            self.purge_temp_and_pycache()

            # Step 4: Kernel page cache drop
            self.drop_linux_pagecache()

            mem_after = psutil.virtual_memory()
            freed_mb = (mem_after.available - mem.available) / (1024 * 1024)
            logging.info(
                f"Optimization complete. Freed {freed_mb:.1f} MB RAM. Current available: {mem_after.available / (1024 * 1024):.1f} MB")
        else:
            logging.debug(f"Memory normal: {used_percent}% used.")

    def run_loop(self):
        """Continuous background optimization thread."""
        interval = self.cfg['check_interval_sec']
        logging.info(f"Starting Cache Cleaner Engine daemon (Interval: {interval}s)...")
        while True:
            self.optimize_memory()
            time.sleep(interval)


if __name__ == "__main__":
    cleaner = CacheCleanerEngine()
    cleaner.optimize_memory(force=True)