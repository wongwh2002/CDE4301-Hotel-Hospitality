import unittest

import numpy as np

from server.recognition import choose_match, normalized_embedding


class MatchingTests(unittest.TestCase):
    def test_accepts_a_strong_separated_candidate(self):
        self.assertEqual(choose_match({"Alice": 0.8, "Bob": 0.5}, 0.65, 0.1), ("Alice", 0.8, 0.5))

    def test_rejects_a_strong_but_ambiguous_candidate(self):
        self.assertEqual(choose_match({"Alice": 0.8, "Bob": 0.75}, 0.65, 0.1), ("Unknown", 0.8, 0.75))

    def test_rejects_a_low_score_even_with_a_large_margin(self):
        self.assertEqual(choose_match({"Alice": 0.6, "Bob": 0.1}, 0.65, 0.1)[0], "Unknown")

    def test_single_enrolled_identity_still_needs_to_pass_threshold(self):
        self.assertEqual(choose_match({"Alice": 0.8}, 0.65, 0.1), ("Alice", 0.8, None))
        self.assertEqual(choose_match({"Alice": 0.4}, 0.65, 0.1)[0], "Unknown")

    def test_empty_and_nonfinite_scores_do_not_become_matches(self):
        self.assertEqual(choose_match({}, 0.65, 0.1), ("Unknown", None, None))
        self.assertEqual(choose_match({"Alice": float("nan"), "Bob": float("inf")}, 0.65, 0.1),
                         ("Unknown", None, None))

    def test_embeddings_are_normalized_before_cosine_matching(self):
        embedding = normalized_embedding(np.full(512, 2.0))
        self.assertAlmostEqual(float(np.linalg.norm(embedding)), 1.0, places=5)
        self.assertEqual(embedding.dtype, np.float32)

    def test_invalid_embeddings_are_rejected(self):
        for embedding in (np.zeros(512), np.ones(128), np.full(512, np.nan), np.full(512, np.inf)):
            with self.subTest(shape=embedding.shape):
                with self.assertRaises(ValueError):
                    normalized_embedding(embedding)


if __name__ == "__main__":
    unittest.main()
