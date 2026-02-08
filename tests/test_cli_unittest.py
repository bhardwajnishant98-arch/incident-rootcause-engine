import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from app.cli import main


class TestCli(unittest.TestCase):
    def test_cli_outputs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "outputs"
            input_path = Path("data/examples.jsonl")
            args = [
                "--input",
                str(input_path),
                "--outdir",
                str(output_dir),
            ]

            with self.subTest("run-cli"):
                with mock.patch("sys.argv", ["app.cli"] + args):
                    main()

            analysis_path = output_dir / "analysis.json"
            report_path = output_dir / "report.md"
            csv_path = output_dir / "risk_register.csv"

            self.assertTrue(analysis_path.exists())
            self.assertTrue(report_path.exists())
            self.assertTrue(csv_path.exists())

            with csv_path.open("r", encoding="utf-8") as handle:
                header = handle.readline().strip()

            expected_columns = (
                "timestamp_utc,title,classification,severity,score,service_name,"
                "primary_rca_category,primary_rca_subcategory,top_control_gap,"
                "customer_impact,data_involved,regulatory_relevance,financial_loss_gbp,"
                "confidence,exec_summary_short"
            )
            self.assertEqual(header, expected_columns)

            analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
            self.assertIsInstance(analysis, list)


if __name__ == "__main__":
    unittest.main()
