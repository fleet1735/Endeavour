# -*- coding: utf-8 -*-
# Backward-compat wrapper for Phase 2 migration.
# Redirects to endeavour.data.loader
from endeavour.data.loader import main as _main

if __name__ == "__main__":
    _main()
