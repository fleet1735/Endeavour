# -*- coding: utf-8 -*-
"""
cv.py — CV protocol helpers (Purged K-Fold, embargo, nested WF)
Contract: CVStampV2 literal must be used verbatim everywhere (SSOT).
"""

CV_STAMP_LITERAL = '{"purged_kfold":{"folds":5},"embargo_days":10,"nested_wf":{"windows":3},"seed":42}'

def cv_stamp_str() -> str:
    # Return exactly the SSOT literal (no spaces change, case-sensitive)
    return CV_STAMP_LITERAL
