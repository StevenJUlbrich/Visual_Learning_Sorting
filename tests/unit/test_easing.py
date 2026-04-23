"""TC-A5: Easing function math tests.

Pure math — no Pygame import required.
"""

import pytest

from visualizer.views.easing import ease_in_out_quad, ease_out_cubic, sine_arc

# --- ease_in_out_quad ---


@pytest.mark.unit
def test_ease_in_out_quad_boundary_zero() -> None:
    assert ease_in_out_quad(0.0) == 0.0


@pytest.mark.unit
def test_ease_in_out_quad_boundary_one() -> None:
    assert ease_in_out_quad(1.0) == 1.0


@pytest.mark.unit
def test_ease_in_out_quad_clamp_high() -> None:
    assert ease_in_out_quad(1.5) == ease_in_out_quad(1.0)


@pytest.mark.unit
def test_ease_in_out_quad_clamp_low() -> None:
    assert ease_in_out_quad(-0.5) == ease_in_out_quad(0.0)


@pytest.mark.unit
def test_ease_in_out_quad_symmetry_midpoint() -> None:
    assert ease_in_out_quad(0.5) == 0.5


@pytest.mark.unit
def test_ease_in_out_quad_non_linear() -> None:
    assert ease_in_out_quad(0.2) != 0.2
    assert ease_in_out_quad(0.8) != 0.8


@pytest.mark.unit
def test_ease_in_out_quad_acceleration() -> None:
    # First half: slower than linear (ease-in)
    assert ease_in_out_quad(0.2) < 0.2


@pytest.mark.unit
def test_ease_in_out_quad_deceleration() -> None:
    # Second half: faster than linear (ease-out)
    assert ease_in_out_quad(0.8) > 0.8


# --- ease_out_cubic ---


@pytest.mark.unit
def test_ease_out_cubic_boundary_zero() -> None:
    assert ease_out_cubic(0.0) == 0.0


@pytest.mark.unit
def test_ease_out_cubic_boundary_one() -> None:
    assert ease_out_cubic(1.0) == 1.0


@pytest.mark.unit
def test_ease_out_cubic_clamp_high() -> None:
    assert ease_out_cubic(1.5) == ease_out_cubic(1.0)


@pytest.mark.unit
def test_ease_out_cubic_clamp_low() -> None:
    assert ease_out_cubic(-0.5) == ease_out_cubic(0.0)


@pytest.mark.unit
def test_ease_out_cubic_non_linear() -> None:
    assert ease_out_cubic(0.5) != 0.5


@pytest.mark.unit
def test_ease_out_cubic_fast_start() -> None:
    # Ease-out: starts fast, so early values exceed linear
    assert ease_out_cubic(0.2) > 0.2


# --- sine_arc ---


@pytest.mark.unit
def test_sine_arc_boundary_zero() -> None:
    assert sine_arc(0.0) == 0.0


@pytest.mark.unit
def test_sine_arc_boundary_one() -> None:
    assert sine_arc(1.0) == pytest.approx(0.0, abs=1e-15)


@pytest.mark.unit
def test_sine_arc_clamp_high() -> None:
    assert sine_arc(1.5) == sine_arc(1.0)


@pytest.mark.unit
def test_sine_arc_clamp_low() -> None:
    assert sine_arc(-0.5) == sine_arc(0.0)


@pytest.mark.unit
def test_sine_arc_peak() -> None:
    assert sine_arc(0.5) == pytest.approx(1.0)


@pytest.mark.unit
def test_sine_arc_symmetry() -> None:
    assert sine_arc(0.25) == pytest.approx(sine_arc(0.75))


@pytest.mark.unit
def test_sine_arc_non_linear() -> None:
    assert sine_arc(0.25) != 0.5
