from __future__ import annotations

import json

from analisis_agave_tesis import FIGS_EN, STATS_JSON, build_stats, generate_figures


def main() -> None:
    stats = build_stats()
    STATS_JSON.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    generate_figures(stats, "en")
    print(f"Wrote English figures in {FIGS_EN}")


if __name__ == "__main__":
    main()
