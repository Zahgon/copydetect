"""This module contains functions for tokenizing/filtering code
as well as generic functions for detecting overlap between two
documents.
"""

import logging
import warnings
from typing import Dict, List

from pygments import lexers, token
import pygments.util
import numpy as np
from markupsafe import escape

# if the C extention is available, use it. For almost all use cases
# the speed difference is not significant so if the C extention isn't
# found copydetect will silenty switch to the python implementation.
try:
    from .winnow import _winnow
except (ModuleNotFoundError, ImportError):
    from .pywinnow import _winnow

def filter_code(code, filename, language=None):
    """Tokenize and filter a code document. Replace variable names with
    V, function names with F, object names with O, and strings with S.
    Return the filtered document and a list of offsets indicating how
    many characters were removed by filtering at each index in the
    resulting document where filtering occured (this is used later to
    highlight the original code using plagiarism detection results on
    the filtered code)
    """
    pass

def hashed_kgrams(string, k):
    """Return hashes of all k-grams in a string"""
    pass

def winnow(hashes, window_size, remove_duplicates=True):
    """implementation of the robust winnowing algorithm decribed in
    https://theory.stanford.edu/~aiken/publications/papers/sigmod03.pdf
    Returns a list of selected hashes and the indexes of those hashes.
    """
    pass

def get_copied_slices(idx, k):
    """Given k and a list of indexes detected by
    find_fingerprint_overlap, generates a list of slices where the
    copied code begins and ends. Returns a 2D array where the first
    dimension is slice start locations and the second dimension is
    slice end locations.
    """
    if len(idx) == 0:
        return np.array([[],[]])

    # determine the gaps between slices (called skips)
    sorted_idx = np.sort(idx)
    next_idx = np.concatenate([sorted_idx[1:], [0]])
    skips = np.where(next_idx - sorted_idx > k - 1)[0]

    # use the elements around the gaps to compute slice start/ends
    slice_starts = np.concatenate([[sorted_idx[0]], sorted_idx[skips + 1]])
    slice_ends = np.concatenate([sorted_idx[skips]+k, [sorted_idx[-1]+k]])

    return np.array([slice_starts, slice_ends])

def get_document_fingerprints(doc, k, window_size, boilerplate=None):
    """Given a document, computes all k-gram hashes and uses the
    winnowing algorithm to reduce their number. Optionally takes a
    list of boilerplate hashes to remove from the winnowed list.
    Returns the selected hashes and their indexes in the original list
    """
    pass

def find_fingerprint_overlap(hashes1, hashes2, idx1, idx2):
    """Finds the indexes of overlapping values between two lists of
    hashes. Returns two lists of indexes, one for the first hash list
    and one for the second. The indexes of the original hashes are
    provided in case boilerplate results in gaps.
    """
    intersection = hashes1.intersection(hashes2)
    if len(intersection) > 0:
        overlap_1 = np.concatenate([np.array(idx1[i]) for i in intersection])
        overlap_2 = np.concatenate([np.array(idx2[i]) for i in intersection])
        return overlap_1.flatten(), overlap_2.flatten()
    else:
        return np.array([], dtype=int), np.array([], dtype=int)

def highlight_overlap(doc, slices, left_hl, right_hl,
                      truncate=-1, escape_html=False):
    """Highlights copied code in a document given the slices containing
    copied code and strings to use for the highlight start and end.
    Returns the document annoted with the highlight strings as well as
    the percentage of code which was highlighted. If truncate is set to
    an integer, everything not within that many lines of highlighted
    code will be replaced with "..."
    """
    if slices.shape[0] > 0:
        hl_percent = np.sum(slices[1] - slices[0])/len(doc)
    else:
        warnings.warn("empty slices array")
        return doc, 0

    new_doc = ""
    current_idx = 0
    for slice_idx in range(slices.shape[1]):
        start_idx = slices[0,slice_idx]
        end_idx = slices[1,slice_idx]

        if escape_html:
            pre_highlight = str(escape(doc[current_idx:start_idx]))
            highlighted = left_hl+str(escape(doc[start_idx:end_idx]))+right_hl
        else:
            pre_highlight = doc[current_idx:start_idx]
            highlighted = left_hl + doc[start_idx:end_idx] + right_hl

        if truncate >= 0:
            lines = pre_highlight.split("\n")
            if slice_idx != 0 and len(lines) > truncate*2:
                pre_highlight = ("\n".join(lines[:truncate+1]) + "\n\n...\n\n"
                                 + "\n".join(lines[-truncate - 1:]))
            elif len(lines) > truncate:
                pre_highlight = "\n".join(lines[-truncate - 1:])

        new_doc += pre_highlight + highlighted
        current_idx = end_idx

    if escape_html:
        post_highlight = str(escape(doc[current_idx:]))
    else:
        post_highlight = doc[current_idx:]

    if truncate >= 0:
        lines = post_highlight.split("\n")
        if len(lines) > truncate:
            post_highlight = "\n".join(lines[:truncate])
    new_doc += post_highlight

    return new_doc, hl_percent

def get_token_coverage(idx: Dict[int, List[int]], k: int, token_len: int):
    """Determines the number of tokens in the original document which
    are included in the winnowed indices
    """
    pass
