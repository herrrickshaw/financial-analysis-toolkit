"""Managerial (cost) accounting — CFI's Activity Based Costing, Cost Behavior Analysis, Cost of Goods
Manufactured, Cost of Goods Sold, Product Costs, Target Costing and Economic Order Quantity templates. (The
university-style two-step driver allocation lives in ``finmodel.costing``; CVP / break-even in
``finmodel.breakeven``.)

  ABC              — activity rate = cost pool / total driver volume; each product absorbs rate x the driver
                     volume it consumes. Compared with a single plant-wide rate it shows which products the
                     traditional allocation over- or under-costs.
  Cost behaviour   — high-low method (two extreme activity points) and ordinary least squares over all points:
                     total cost = fixed + variable rate x activity.
  COGM / COGS      — DM used = opening DM + purchases - closing DM; total manufacturing cost = DM used + DL +
                     overhead; COGM = total manufacturing cost + opening WIP - closing WIP; COGS = opening FG +
                     COGM - closing FG.
  EOQ              — Harris (1913), "How Many Parts to Make at Once", Factory, The Magazine of Management
                     10(2): sqrt(2DS / H); reorder point = daily demand x lead time + safety stock."""
from __future__ import annotations

import math
from typing import Any, Dict, List, Mapping, Optional, Sequence

from .fin import safe_div


def activity_based_costing(activities: Sequence[Mapping[str, Any]], products: Sequence[Mapping[str, Any]],
                           traditional_basis: Optional[str] = None) -> Dict[str, Any]:
    """``activities``: [{"name", "cost_pool", "driver_total"}]; ``products``: [{"name", "units",
    "direct_costs", "drivers": {activity: volume}, optionally the traditional basis volume under
    ``traditional_basis`` (e.g. "machine_hours")}]."""
    rates = {a["name"]: a["cost_pool"] / a["driver_total"] for a in activities}
    for a in activities:   # every unit of driver must belong to some product, or overhead goes unabsorbed
        used = sum(p["drivers"].get(a["name"], 0) for p in products)
        if not math.isclose(used, a["driver_total"], rel_tol=1e-9):
            raise ValueError(f"activity {a['name']}: products consume {used} of {a['driver_total']} driver units")
    total_pool = sum(a["cost_pool"] for a in activities)
    plant_rate = None
    if traditional_basis:
        plant_rate = total_pool / sum(p[traditional_basis] for p in products)
    rows = []
    for p in products:
        oh = sum(rates[k] * v for k, v in p["drivers"].items())
        row = {"name": p["name"], "units": p["units"], "abc_overhead": oh, "abc_total_cost": p["direct_costs"] + oh,
               "abc_unit_cost": (p["direct_costs"] + oh) / p["units"]}
        if plant_rate is not None:
            trad = plant_rate * p[traditional_basis]
            row.update({"traditional_overhead": trad, "traditional_unit_cost": (p["direct_costs"] + trad) / p["units"],
                        "traditional_minus_abc_unit_cost": (trad - oh) / p["units"]})
        rows.append(row)
    return {"activity_rates": rates, "plantwide_rate": plant_rate, "products": rows,
            "overhead_absorbed": sum(r["abc_overhead"] for r in rows), "overhead_pool": total_pool}


def cost_behavior(activity: Sequence[float], total_cost: Sequence[float]) -> Dict[str, Any]:
    """High-low and least-squares splits of a mixed cost into fixed and variable parts."""
    if len(activity) != len(total_cost) or len(activity) < 2:
        raise ValueError("need at least two (activity, cost) pairs of equal length")
    hi = max(range(len(activity)), key=lambda i: activity[i])
    lo = min(range(len(activity)), key=lambda i: activity[i])
    v_hl = (total_cost[hi] - total_cost[lo]) / (activity[hi] - activity[lo])
    f_hl = total_cost[hi] - v_hl * activity[hi]
    n = len(activity)
    mx, my = sum(activity) / n, sum(total_cost) / n
    sxx = sum((x - mx) ** 2 for x in activity)
    sxy = sum((x - mx) * (y - my) for x, y in zip(activity, total_cost))
    v_ls = sxy / sxx
    f_ls = my - v_ls * mx
    ss_res = sum((y - (f_ls + v_ls * x)) ** 2 for x, y in zip(activity, total_cost))
    ss_tot = sum((y - my) ** 2 for y in total_cost)
    return {"high_low": {"variable_rate": v_hl, "fixed_cost": f_hl},
            "regression": {"variable_rate": v_ls, "fixed_cost": f_ls, "r_squared": 1 - ss_res / ss_tot if ss_tot else 1.0}}


def cost_of_goods_manufactured(direct_materials_begin: float, direct_materials_purchases: float, direct_materials_end: float,
                               direct_labor: float, manufacturing_overhead: float, wip_begin: float, wip_end: float,
                               finished_goods_begin: Optional[float] = None, finished_goods_end: Optional[float] = None,
                               units_completed: Optional[float] = None) -> Dict[str, Any]:
    dm_used = direct_materials_begin + direct_materials_purchases - direct_materials_end
    tmc = dm_used + direct_labor + manufacturing_overhead
    cogm = tmc + wip_begin - wip_end
    out: Dict[str, Any] = {"direct_materials_used": dm_used, "total_manufacturing_cost": tmc, "cogm": cogm}
    if units_completed:
        out["cogm_per_unit"] = cogm / units_completed
    if finished_goods_begin is not None and finished_goods_end is not None:
        out["cogs"] = finished_goods_begin + cogm - finished_goods_end
    return out


def cost_of_goods_sold(beginning_inventory: float, purchases: float, ending_inventory: float, freight_in: float = 0.0,
                       purchase_returns_and_discounts: float = 0.0, revenue: Optional[float] = None) -> Dict[str, Any]:
    """Periodic-inventory COGS for a merchandiser = opening inventory + net purchases - closing inventory."""
    net_purchases = purchases + freight_in - purchase_returns_and_discounts
    available = beginning_inventory + net_purchases
    cogs = available - ending_inventory
    out: Dict[str, Any] = {"net_purchases": net_purchases, "goods_available_for_sale": available, "cogs": cogs}
    if revenue:
        out.update({"gross_profit": revenue - cogs, "gross_margin": (revenue - cogs) / revenue})
    return out


def product_costs(direct_materials: float, direct_labor: float, manufacturing_overhead: float, units: float,
                  selling_expenses: float = 0.0, administrative_expenses: float = 0.0) -> Dict[str, Any]:
    """Product (inventoriable) costs vs period costs, with prime and conversion cost per unit."""
    prime = direct_materials + direct_labor
    conversion = direct_labor + manufacturing_overhead
    product = direct_materials + direct_labor + manufacturing_overhead
    return {"prime_cost": prime, "conversion_cost": conversion, "product_cost": product,
            "product_cost_per_unit": product / units, "prime_cost_per_unit": prime / units,
            "conversion_cost_per_unit": conversion / units, "period_costs": selling_expenses + administrative_expenses}


def target_costing(target_price: float, target_margin: float, current_unit_cost: Optional[float] = None,
                   margin_on: str = "price") -> Dict[str, Any]:
    """Allowable cost = target price - required profit; ``margin_on="price"`` (profit as % of price, the usual
    convention) or ``"cost"`` (markup on cost). With the current cost, the cost-reduction gap to close."""
    if margin_on == "price":
        allowable = target_price * (1 - target_margin)
    elif margin_on == "cost":
        allowable = target_price / (1 + target_margin)
    else:
        raise ValueError("margin_on must be 'price' or 'cost'")
    out: Dict[str, Any] = {"target_price": target_price, "target_profit": target_price - allowable, "allowable_cost": allowable}
    if current_unit_cost is not None:
        out.update({"cost_gap": current_unit_cost - allowable, "required_reduction_pct": safe_div(current_unit_cost - allowable, current_unit_cost)})
    return out


def economic_order_quantity(annual_demand: float, order_cost: float, holding_cost_per_unit: Optional[float] = None,
                            unit_cost: Optional[float] = None, holding_cost_rate: Optional[float] = None,
                            lead_time_days: float = 0.0, safety_stock: float = 0.0, days_per_year: float = 365.0) -> Dict[str, Any]:
    """Harris EOQ. Holding cost either per unit per year, or ``holding_cost_rate`` x ``unit_cost``."""
    h = holding_cost_per_unit if holding_cost_per_unit is not None else (holding_cost_rate or 0) * (unit_cost or 0)
    if h <= 0:
        raise ValueError("holding cost must be positive")
    q = math.sqrt(2 * annual_demand * order_cost / h)
    ordering, holding = annual_demand / q * order_cost, q / 2 * h + safety_stock * h
    return {"eoq": q, "orders_per_year": annual_demand / q, "days_between_orders": days_per_year * q / annual_demand,
            "annual_ordering_cost": ordering, "annual_holding_cost": holding, "total_inventory_cost": ordering + holding,
            "reorder_point": annual_demand / days_per_year * lead_time_days + safety_stock}


_FUNCS = {f.__name__: f for f in (activity_based_costing, cost_behavior, cost_of_goods_manufactured, cost_of_goods_sold,
                                    product_costs, target_costing, economic_order_quantity)}


def from_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    unknown = [k for k in d if not str(k).startswith("_") and k not in _FUNCS]
    if unknown:
        raise KeyError(f"unknown function(s): {unknown}; available: {sorted(_FUNCS)}")
    return {k: _FUNCS[k](**v) for k, v in d.items() if not str(k).startswith("_")}
