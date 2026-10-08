"""
Unit tests for ReAssist Service Layer & AWS integrations
"""

import os
import unittest
from unittest.mock import MagicMock, patch
import pytest

from src.core.storage import LocalStorageProvider, S3StorageProvider, get_storage_provider
from src.services.storage_service import StorageService
from src.services.model_routing_service import ModelRoutingService
from src.services.export_service import ExportService
from src.services.observability_service import ObservabilityService
from src.router.agent_router import AgentRouter, ModelTier


class TestStorageLayer(unittest.TestCase):
    def setUp(self):
        self.test_dir = "data/test_storage"
        self.provider = LocalStorageProvider(base_dir=self.test_dir)
        self.service = StorageService(provider=self.provider)

    def tearDown(self):
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_save_and_read_local_file(self):
        path = "test_doc.txt"
        content = "Hello ReAssist Storage"
        saved_ref = self.provider.save_file(content, path)
        self.assertTrue(os.path.exists(saved_ref))
        read_back = self.provider.read_file(path).decode("utf-8")
        self.assertEqual(read_back, content)

    def test_sha256_calculation(self):
        hash1 = StorageService.calculate_sha256("test content")
        hash2 = StorageService.calculate_sha256(b"test content")
        self.assertEqual(hash1, hash2)
        self.assertEqual(len(hash1), 64)

    def test_store_document_metadata(self):
        meta = self.service.store_document(
            content=b"Sample PDF Content",
            filename="paper.pdf",
            workspace_id="ws_123"
        )
        self.assertIn("blob_url", meta)
        self.assertIn("file_hash", meta)
        self.assertEqual(meta["filename"], "paper.pdf")
        self.assertEqual(meta["size_bytes"], len(b"Sample PDF Content"))


class TestModelRoutingService(unittest.TestCase):
    def setUp(self):
        self.router = AgentRouter(provider="bedrock")
        self.service = ModelRoutingService(provider="bedrock")

    def test_agent_tier_mapping(self):
        # Tier 1 fast model
        grader_model = self.service.get_agent_model("grader")
        self.assertEqual(grader_model, "anthropic.claude-3-haiku-20240307-v1:0")

        # Tier 3 frontier model for complex query
        synth_model = self.service.get_agent_model("synthesizer", query_complexity=5)
        self.assertEqual(synth_model, "anthropic.claude-3-5-sonnet-20240620-v1:0")

    def test_routing_decision(self):
        res = self.service.route_query("simple query", log_decision=False)
        self.assertIn("decision", res)
        self.assertIn("suggested_tier", res)
        self.assertIn("tier_dispatch", res)


class TestExportService(unittest.TestCase):
    def setUp(self):
        self.service = ExportService()
        self.sample_papers = [
            {
                "title": "Attention Is All You Need",
                "authors": ["Vaswani", "Shazeer", "Parmar"],
                "year": "2017",
                "source": "NeurIPS",
                "pdf_url": "https://arxiv.org/abs/1706.03762"
            }
        ]

    def test_generate_bibtex(self):
        bibtex = self.service.generate_bibtex(self.sample_papers)
        self.assertIn("@article{", bibtex)
        self.assertIn("Attention Is All You Need", bibtex)
        self.assertIn("Vaswani and Shazeer and Parmar", bibtex)

    def test_generate_markdown_dossier(self):
        sample_result = {
            "papers": self.sample_papers,
            "synthesis": "Transformer models replaced RNNs.",
            "gaps": "Long-context computational limits.",
            "ideas": [{"title": "Linear Attention", "hypothesis": "O(N) complexity"}],
            "techniques": "State Space Models",
            "guidance": "Start with small benchmark."
        }
        md = self.service.generate_markdown_dossier(sample_result, "Transformers")
        self.assertIn("# Research Intelligence Dossier: Transformers", md)
        self.assertIn("Transformer models replaced RNNs.", md)
        self.assertIn("BibTeX Citations", md)


class TestObservabilityService(unittest.TestCase):
    def setUp(self):
        self.service = ObservabilityService()

    def test_telemetry_formatting(self):
        timings = {
            "search": {"latency_ms": 1200, "input_tokens": 500, "output_tokens": 150},
            "summarizer": {"latency_ms": 2500, "input_tokens": 2000, "output_tokens": 400},
        }
        res = self.service.format_agent_telemetry(timings, model_name="gpt-4o-mini")
        self.assertEqual(res["total_latency_ms"], 3700)
        self.assertEqual(res["total_input_tokens"], 2500)
        self.assertEqual(res["total_output_tokens"], 550)
        self.assertTrue(res["total_cost_usd"] > 0)
        self.assertEqual(len(res["traces"]), 2)


if __name__ == "__main__":
    unittest.main()
