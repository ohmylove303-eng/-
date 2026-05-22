"""시각화 레이어/사용자 정의/콘솔 테스트."""
import unittest

from kafas.viz.layers import STANDARD_LAYERS, LayerSpec
from kafas.viz.custom import LayerConfig, default_config_for
from kafas.viz.console import PANELS, FORBIDDEN_INTERACTIONS


class TestViz(unittest.TestCase):
    def test_standard_layers_count(self):
        self.assertGreaterEqual(len(STANDARD_LAYERS), 12)

    def test_custom_forbidden_keyword(self):
        cfg = default_config_for("commander")
        bad = LayerSpec(
            "fire_control_panel", "사격제원 패널", "Firing Solution",
            True, True, "internal", 100,
        )
        with self.assertRaises(ValueError):
            cfg.add_custom(bad)

    def test_custom_must_be_display_only(self):
        cfg = default_config_for("commander")
        bad = LayerSpec(
            "ok_layer", "보조", "Aux",
            True, False, "internal", 100,
        )
        with self.assertRaises(ValueError):
            cfg.add_custom(bad)

    def test_resolve_includes_defaults(self):
        cfg = default_config_for("analyst")
        out = cfg.resolve()
        ids = [l.layer_id for l in out]
        self.assertIn("terrain", ids)
        self.assertIn("target_candidates", ids)

    def test_console_no_forbidden_interaction(self):
        for panel in PANELS:
            for inter in panel.interactions:
                self.assertNotIn(inter, FORBIDDEN_INTERACTIONS)


if __name__ == "__main__":
    unittest.main()
