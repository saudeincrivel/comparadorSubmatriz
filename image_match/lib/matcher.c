#include <inttypes.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Configurable base and mod for polynomial rolling hash */
static const uint64_t HASH_BASE = 91138233ULL;
static const uint64_t HASH_MOD = 1000000007ULL; /* prime */

/* Pair (row, col) result */
typedef struct {
  size_t row;
  size_t col;
} MatchPos;

/* fast modular exponentiation */
static uint64_t mod_pow(uint64_t base, size_t exp, uint64_t mod) {
  uint64_t res = 1 % mod;
  uint64_t b = base % mod;
  while (exp) {
    if (exp & 1)
      res = (res * b) % mod;
    b = (b * b) % mod;
    exp >>= 1;
  }
  return res;
}

/* LPS for KMP on arrays of uint64_t */
static void computeLPS_u64(const uint64_t *pat, size_t M, size_t *lps) {
  size_t len = 0;
  lps[0] = 0;
  size_t i = 1;
  while (i < M) {
    if (pat[i] == pat[len]) {
      lps[i++] = ++len;
    } else {
      if (len != 0) {
        len = lps[len - 1];
      } else {
        lps[i++] = 0;
      }
    }
  }
}

/* KMP search: find occurrences of pattern (len M) inside text (len N).
   Returns number of matches written into out_count and writes starting indices
   into matches[]. matches array must have capacity max_matches. */
static size_t KMPsearch_u64(const uint64_t *text, size_t N,
                            const uint64_t *pattern, size_t M, size_t *matches,
                            size_t max_matches) {
  if (M == 0 || N < M)
    return 0;
  size_t *lps = (size_t *)malloc(M * sizeof(size_t));
  if (!lps)
    return 0;
  computeLPS_u64(pattern, M, lps);

  size_t i = 0, j = 0, count = 0;
  while (i < N) {
    if (text[i] == pattern[j]) {
      i++;
      j++;
      if (j == M) {
        if (count < max_matches)
          matches[count] = i - j;
        count++;
        j = lps[j - 1];
      }
    } else {
      if (j != 0)
        j = lps[j - 1];
      else
        i++;
    }
  }

  free(lps);
  /* We might have found more matches than max_matches; caller should provision
     enough capacity. Return actual count (not truncated). The caller will
     typically cap stored matches to max_matches. */
  return count;
}

/* Primary function:
   text: pointer to N x M matrix (row-major) => element at (r,c) is text[r*M +
   c] pattern: pointer to R x C matrix (row-major) => pattern[r*C + c] Returns
   dynamically allocated MatchPos* (caller must free). *out_count receives
   number of found matches.
*/
MatchPos *find_2d_matches_by_column_hash(const uint8_t *text, size_t N,
                                         size_t M, const uint8_t *pattern,
                                         size_t R, size_t C,
                                         size_t *out_count) {
  *out_count = 0;
  if (!text || !pattern || N == 0 || M == 0 || R == 0 || C == 0)
    return NULL;
  if (R > N || C > M)
    return NULL;

  /* Precompute base^(R-1) used to remove the top element from a length-R column
   * hash */
  uint64_t top_pow = mod_pow(HASH_BASE, R - 1, HASH_MOD);

  /* Compute pattern column hashes: length C */
  uint64_t *pat_col_hash = (uint64_t *)malloc(C * sizeof(uint64_t));
  if (!pat_col_hash)
    return NULL;
  for (size_t c = 0; c < C; ++c) {
    uint64_t h = 0;
    for (size_t r = 0; r < R; ++r) {
      uint64_t v = (uint64_t)pattern[r * C + c];
      h = (h * HASH_BASE + v) % HASH_MOD;
    }
    pat_col_hash[c] = h;
  }

  /* Compute initial top-strip column hashes for the large matrix (columns
   * 0..M-1), using rows 0..R-1 */
  uint64_t *strip_col_hash = (uint64_t *)malloc(M * sizeof(uint64_t));
  if (!strip_col_hash) {
    free(pat_col_hash);
    return NULL;
  }

  for (size_t c = 0; c < M; ++c) {
    uint64_t h = 0;
    for (size_t r = 0; r < R; ++r) {
      uint64_t v = (uint64_t)text[r * M + c];
      h = (h * HASH_BASE + v) % HASH_MOD;
    }
    strip_col_hash[c] = h;
  }

  /* Prepare dynamic result array */
  size_t cap = 64;
  MatchPos *results = (MatchPos *)malloc(cap * sizeof(MatchPos));
  if (!results) {
    free(pat_col_hash);
    free(strip_col_hash);
    return NULL;
  }
  size_t found = 0;

  /* temporary storage for KMP matches (column indices). We must give KMP enough
     capacity: worst-case number of starting columns available is M - C + 1 per
     row. Use that as capacity. */
  size_t max_col_matches = (M >= C) ? (M - C + 1) : 0;
  size_t *col_matches = (size_t *)malloc(max_col_matches * sizeof(size_t));
  if (!col_matches) {
    free(pat_col_hash);
    free(strip_col_hash);
    free(results);
    return NULL;
  }

  /* For each vertical position of the R-strip (top_row 0..N-R) */
  for (size_t top_row = 0; top_row <= N - R; ++top_row) {
    /* KMP search the C-length pat_col_hash inside M-length strip_col_hash.
       KMPsearch_u64 returns the total count of matches (could be >
       max_col_matches), but it writes up to max_col_matches indices into
       col_matches. We will use written ones only.
    */
    size_t actual_matches = 0;
    if (M >= C) {
      /* we set max_matches param so KMP stores up to max_col_matches entries */
      actual_matches = KMPsearch_u64(strip_col_hash, M, pat_col_hash, C,
                                     col_matches, max_col_matches);
      /* actual_matches may be greater than max_col_matches; only indices stored
         are up to max_col_matches. In practice, KMPsearch_u64 returns the
         number of matches; we will iterate over the stored ones
         (min(actual_matches, max_col_matches)). This is safe because pattern
         length C and text length M give at most M-C+1 starting positions, which
         equals max_col_matches and KMPsearch_u64 was given that exact storage
         capacity; so actual_matches <= max_col_matches normally. */
    }

    size_t stored =
        (actual_matches <= max_col_matches) ? actual_matches : max_col_matches;
    for (size_t k = 0; k < stored; ++k) {
      size_t col_start = col_matches[k];
      /* store (top_row, col_start) */
      if (found >= cap) {
        cap *= 2;
        MatchPos *tmp = (MatchPos *)realloc(results, cap * sizeof(MatchPos));
        if (!tmp) {
          /* out of memory: cleanup and return what we have so far */
          free(pat_col_hash);
          free(strip_col_hash);
          free(col_matches);
          *out_count = found;
          return results;
        }
        results = tmp;
      }
      results[found].row = top_row;
      results[found].col = col_start;
      found++;
    }

    /* If there are more rows below, roll the strip down by 1 row: update each
     * column hash in O(1) */
    if (top_row < N - R) {
      size_t remove_row =
          top_row; /* index of row being removed from top of each column */
      size_t add_row =
          top_row + R; /* index of new row being appended at bottom */
      for (size_t c = 0; c < M; ++c) {
        uint64_t old_val = (uint64_t)text[remove_row * M + c];
        uint64_t new_val = (uint64_t)text[add_row * M + c];

        /* subtract old_val * top_pow */
        uint64_t to_sub = (old_val * top_pow) % HASH_MOD;
        uint64_t h = strip_col_hash[c];
        /* (h + HASH_MOD - to_sub) % HASH_MOD */
        if (h >= to_sub)
          h = h - to_sub;
        else
          h = (h + HASH_MOD - to_sub);

        /* multiply by base and add new_val */
        h = (h * HASH_BASE + new_val) % HASH_MOD;
        strip_col_hash[c] = h;
      }
    }
  }

  free(pat_col_hash);
  free(strip_col_hash);
  free(col_matches);

  /* shrink results array to exact size */
  if (found == 0) {
    free(results);
    results = NULL;
  } else {
    MatchPos *tmp = (MatchPos *)realloc(results, found * sizeof(MatchPos));
    if (tmp)
      results = tmp;
  }
  *out_count = found;
  return results;
}

// /* Example usage */
#ifdef DEMO_MAIN
int main(void) {
  /* Example: large matrix 5x6, pattern 2x3 */
  uint8_t text[] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 2, 3, 4, 5, 6,
                    7, 8, 9, 1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 2, 3}; /* N=5, M=6 */

  uint8_t pattern[] = {9, 1, 2, 6,
                       7, 8}; /* R=2, C=3  -> columns are [9,6], [1,7], [2,8] */

  size_t N = 5, M = 6, R = 2, C = 3;
  size_t count = 0;
  MatchPos *matches =
      find_2d_matches_by_column_hash(text, N, M, pattern, R, C, &count);

  printf("Matches: %zu\n", count);
  for (size_t i = 0; i < count; ++i) {
    printf("(%zu, %zu)\n", matches[i].row, matches[i].col);
  }
  free(matches);
  return 0;
}
#endif

#include <stdlib.h>

#ifdef _WIN32
#define API __declspec(dllexport)
#else
#define API
#endif

/* Exposed version for Python */
API size_t match_positions(const uint8_t *text, size_t N, size_t M,
                           const uint8_t *pat, size_t R, size_t C,
                           MatchPos **out_ptr) {
  size_t count;
  MatchPos *res = find_2d_matches_by_column_hash(text, N, M, pat, R, C, &count);
  *out_ptr = res;
  return count;
}

/* Python will call this to free the results */
API void free_results(MatchPos *ptr) { free(ptr); }
