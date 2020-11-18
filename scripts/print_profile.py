"""Prints cProfile."""
# Standard Python Libraries
import pstats
import sys

profile_file = sys.argv[1]

p = pstats.Stats(profile_file)
# p.strip_dirs()
p.sort_stats("cumtime")
p.print_stats()
