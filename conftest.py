# pytest configuration for canonical aget/
#
# Excludes templates/ directory from collection — TEMPLATE_unit_test.py matches
# pytest's default *_test.py glob but contains {placeholder} substitutions
# (it is a template artifact, not a runnable test).
#
# gh#1279 fix 2026-05-16 (v3.18 Gate 1 T1.4)
collect_ignore_glob = ["templates/*"]
