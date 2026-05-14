"""
Demonstrates performance improvements over the baseline ecosystem operation
by implementing:
  1. Nearest-pizza allocation   (replaces first-come-first-served)
  2. Multiple chargers          (bot picks the nearest one)
  3. Per-bot-type charge thresholds (tuned to each bot's speed/battery profile)
  4. Opportunistic charging     (top-up when passing close to a charger)

KPIs are collected after each run and printed as a formatted comparison table.
"""
VIEW_BOTS_WINDOW_WHEN_RUNNNIG = 0
WEEKS = 5   # higher = more accurate kpi, reasonable range 4(month)-52(year)

import matplotlib

matplotlib.use('Agg') if not VIEW_BOTS_WINDOW_WHEN_RUNNNIG else None

from robots.ecosystem.factory import ecofactory
from robots.ecosystem.ecosystem import distance   # Euclidean distance helper
import random as rng


def nearest(bot, candidates):
    # take the bot and get the coords of the closes candidate
    candidates = list(candidates)
    if not candidates:
        return None
    return min(candidates, key=lambda c: distance(bot.coordinates, c.coordinates))


def collect_kpis(es, label):
    bots = es.bots()

    total_delivered   = sum(b.units_delivered  for b in bots)
    total_weight      = sum(b.weight_delivered for b in bots)
    total_distance    = round(sum(b.distance   for b in bots), 2)
    total_energy      = round(sum(b.energy     for b in bots), 2)
    broken_bots       = sum(1 for b in bots if b.status == 'broken')

    # Efficiency is pizzas delivered per unit of energy
    efficiency = round(total_delivered / total_energy, 4) if total_energy else 0

    return {
        'run':            label,
        'delivered':      total_delivered,
        'weight_kg':      total_weight,
        'distance':       total_distance,
        'energy':         total_energy,
        'broken_bots':    broken_bots,
        'efficiency':     efficiency,
    }


def print_kpi_table(results):
    headers = [
        'run', 
        'delivered', 
        'weight_kg', 
        'distance', 
        'energy',
        'broken_bots', 
        'efficiency'
    ]

    col_w = {
        h: max(len(h), max(len(str(r[h])) for r in results))
        for h in headers
    }

    separator = '+-' + '-+-'.join('-' * col_w[h] for h in headers) + '-+'
    header_row = '| ' + ' | '.join(f"{h:<{col_w[h]}}" for h in headers) + ' |'

    print('\n' + '=' * len(separator))
    print('  KPI COMPARISON TABLE')
    print('=' * len(separator))
    print(separator)
    print(header_row)
    print(separator)
    for r in results:
        row = '| ' + ' | '.join(f"{str(r[h]):<{col_w[h]}}" for h in headers) + ' |'
        print(row)
    print(separator)

    # Delta summary vs baseline (first row)
    if len(results) > 1:
        baseline = results[0]
        print('\n  IMPROVEMENT OVER BASELINE')
        print('  ' + '-' * 40)
        numeric = ['delivered', 'weight_kg', 'distance', 'energy', 'efficiency']
        for r in results[1:]:
            print(f"\n  {r['run']} vs {baseline['run']}:")
            for key in numeric:
                b_val = baseline[key]
                r_val = r[key]
                if b_val:
                    pct = round(100 * (r_val - b_val) / b_val, 1)
                    direction = '▲' if pct > 0 else '▼'
                    print(f"    {key:<14} {b_val:>10} → {r_val:>10}   {direction} {abs(pct)}%")


## ORIGINAL ecosystem without optimisation
def run_baseline(duration_weeks=1): ## arg = how long to simulate
    es = ecofactory(robots=3, droids=3, drones=3,
                    chargers=[55, 20], pizzas=9)

    es.display(show=(1 if VIEW_BOTS_WINDOW_WHEN_RUNNNIG else 0))          # no GUI for benchmarking
    es.messages_on = False
    es.duration = f"{duration_weeks} week"

    charger          = es.chargers()[0]
    charge_threshold = 0.20
    home             = [40, 20, 0]

    while es.active:
        for bot in es.bots():

            # Charging decision
            if bot.soc / bot.max_soc < charge_threshold and bot.station is None:
                bot.charge(charger)

            # Pizza allocation: first-come-first-served 
            if bot.activity == 'idle':
                for pizza in es.deliverables():
                    if pizza.status == 'ready':
                        bot.deliver(pizza)
                        break

            # Move toward destination
            if not bot.destination and bot.coordinates[:2] != home[:2]:
                bot.target_destination = home
            if bot.target_destination:
                bot.move()

        es.update()

    return es


# Rationale:
#   Robot  – slowest (speed 1), largest battery (750).  Needs higher threshold because it takes longest to reach a charger.
#   Droid  – medium speed (2), medium battery (480).  Moderate threshold.
#   Drone  – fastest (speed 3), smallest battery (180) AND pays 1.5× energy penalty for flight.  Needs the highest threshold to avoid running dry before reaching a charger.
CHARGE_THRESHOLDS = {
    'Robot': 0.25,
    'Droid': 0.20,
    'Drone': 0.35,
}

# if a charger is closer than distance AND the bot's battery is below this number, focus on charging.
OPPORTUNISTIC_DISTANCE  = 8.0
OPPORTUNISTIC_SOC_LIMIT = 0.75  # only if below 75 % charge


def run_optimised(duration_weeks=1):
    # Two chargers spread across the arena instead of one central charger
    es = ecofactory(robots=3, droids=3, drones=3,
                    chargers=(
                        [20+rng.randint(-5,5), 10+rng.randint(-5,5)], ## randomise the coordinates a little 
                        [60+rng.randint(-5,5), 30+rng.randint(-5,5)],
                        [40+rng.randint(-5,5), 20+rng.randint(-5,5)]
                    ), pizzas=9)

    es.display(show=(1 if VIEW_BOTS_WINDOW_WHEN_RUNNNIG else 0))
    es.messages_on = False
    es.duration = f"{duration_weeks} week"

    home = [40, 20, 0]

    while es.active:
        chargers = es.chargers()   # refresh each hour in case chargers change

        for bot in es.bots():

            # 1. charging threshold based on bot type
            threshold = CHARGE_THRESHOLDS.get(bot.kind, 0.20)
            soc_fraction = bot.soc / bot.max_soc

            if soc_fraction < threshold and bot.station is None:
                best_charger = nearest(bot, chargers)
                if best_charger:
                    bot.charge(best_charger)

            # 2. Opportunistic charging 
            elif bot.station is None and soc_fraction < OPPORTUNISTIC_SOC_LIMIT:
                for charger in chargers:
                    if distance(bot.coordinates, charger.coordinates) <= OPPORTUNISTIC_DISTANCE:
                        bot.charge(charger)
                        break

            # 3. Nearest-pizza allocation
            if bot.activity == 'idle':
                ready_pizzas = [p for p in es.deliverables() if p.status == 'ready']
                best_pizza = nearest(bot, ready_pizzas)
                if best_pizza:
                    bot.deliver(best_pizza)

            if not bot.destination and bot.coordinates[:2] != home[:2]:
                bot.target_destination = home
            if bot.target_destination:
                bot.move()

        es.update()

    return es



if __name__ == '__main__':

    print(f"\nRunning BASELINE for {WEEKS} week(s)…")
    es_base = run_baseline(duration_weeks=WEEKS)
    kpi_base = collect_kpis(es_base, label='baseline')
    print("  Baseline complete.")

    print(f"\nRunning OPTIMISED for {WEEKS} week(s)…")
    es_opt = run_optimised(duration_weeks=WEEKS)
    kpi_opt = collect_kpis(es_opt, label='optimised')
    print("  Optimised complete.")

    print_kpi_table([kpi_base, kpi_opt])