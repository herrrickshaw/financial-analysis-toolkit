"""finmodel.managerial_costing against hand calculations, plus the defining properties: ABC absorbs exactly the
overhead pool, EOQ minimises total cost (ordering cost = holding cost at the optimum), and high-low equals
least squares on perfectly linear data."""
import math

import pytest

from finmodel import managerial_costing as M


def _abc():
    activities = [{"name": "setups", "cost_pool": 60000, "driver_total": 300},
                  {"name": "machining", "cost_pool": 140000, "driver_total": 7000}]
    products = [{"name": "standard", "units": 10000, "direct_costs": 300000, "machine_hours": 5000,
                 "drivers": {"setups": 60, "machining": 5000}},
                {"name": "custom", "units": 1000, "direct_costs": 50000, "machine_hours": 2000,
                 "drivers": {"setups": 240, "machining": 2000}}]
    return activities, products


def test_abc_rates_absorption_and_cross_subsidy():
    out = M.activity_based_costing(*_abc(), traditional_basis="machine_hours")
    assert out["activity_rates"] == {"setups": 200, "machining": 20}
    assert out["overhead_absorbed"] == pytest.approx(out["overhead_pool"])
    std, cus = out["products"]
    assert std["abc_overhead"] == 60 * 200 + 5000 * 20
    assert cus["abc_unit_cost"] == pytest.approx((50000 + 48000 + 40000) / 1000)
    # a machine-hour rate undercosts the setup-heavy custom product
    assert cus["traditional_minus_abc_unit_cost"] < 0 < std["traditional_minus_abc_unit_cost"]


def test_abc_rejects_unassigned_driver_volume():
    acts, prods = _abc()
    prods[0]["drivers"]["setups"] = 50
    with pytest.raises(ValueError):
        M.activity_based_costing(acts, prods)


def test_cost_behavior_high_low_and_regression():
    out = M.cost_behavior([100, 200, 300, 400], [1500, 2000, 2500, 3000])
    assert out["high_low"] == pytest.approx({"variable_rate": 5, "fixed_cost": 1000})
    assert out["regression"]["variable_rate"] == pytest.approx(5)
    assert out["regression"]["r_squared"] == pytest.approx(1)
    noisy = M.cost_behavior([100, 200, 300, 400], [1500, 2100, 2400, 3000])
    assert noisy["regression"]["r_squared"] < 1


def test_cogm_and_cogs_schedule():
    out = M.cost_of_goods_manufactured(20000, 100000, 15000, direct_labor=80000, manufacturing_overhead=60000,
                                       wip_begin=10000, wip_end=12000, finished_goods_begin=30000,
                                       finished_goods_end=25000, units_completed=5000)
    assert out["direct_materials_used"] == 105000
    assert out["total_manufacturing_cost"] == 245000
    assert out["cogm"] == 243000
    assert out["cogs"] == 248000
    assert out["cogm_per_unit"] == pytest.approx(48.6)
    m = M.cost_of_goods_sold(50000, 200000, 60000, freight_in=5000, purchase_returns_and_discounts=3000, revenue=400000)
    assert m["cogs"] == 192000 and m["gross_margin"] == pytest.approx(0.52)


def test_product_costs_and_target_costing():
    p = M.product_costs(40000, 30000, 20000, units=1000, selling_expenses=5000, administrative_expenses=7000)
    assert (p["prime_cost"], p["conversion_cost"], p["product_cost_per_unit"], p["period_costs"]) == (70000, 50000, 90, 12000)
    t = M.target_costing(target_price=100, target_margin=0.25, current_unit_cost=82)
    assert t["allowable_cost"] == 75 and t["cost_gap"] == 7
    assert M.target_costing(100, 0.25, margin_on="cost")["allowable_cost"] == pytest.approx(80)


def test_eoq_is_the_cost_minimum():
    out = M.economic_order_quantity(annual_demand=12000, order_cost=50, unit_cost=20, holding_cost_rate=0.25,
                                    lead_time_days=10, safety_stock=100)
    assert out["eoq"] == pytest.approx(math.sqrt(2 * 12000 * 50 / 5))
    assert out["annual_ordering_cost"] == pytest.approx(out["eoq"] / 2 * 5)     # equal at the optimum
    assert out["reorder_point"] == pytest.approx(12000 / 365 * 10 + 100)

    def total(q):
        return 12000 / q * 50 + q / 2 * 5
    assert total(out["eoq"]) < min(total(out["eoq"] * 0.9), total(out["eoq"] * 1.1))
    with pytest.raises(ValueError):
        M.economic_order_quantity(100, 10)
