#!/usr/bin/env python3
"""Back-calculate a packaged food's ingredient shares from its EU label.

Usage: python label_backcalc.py spec.json [--sweep]
Needs numpy + scipy (a scratch venv: python3 -m venv v && v/bin/pip install numpy scipy).

spec.json:
{
  "target": {"prot":32,"fat":12,"sat":4.9,"carb":41,"sug":29,"fib":0.4,"salt":1.2,"kcal":385},
  "ingredients": [                      # in LABEL ORDER (descending weight)
    {"name":"milkprot","comp":[82,1.5,1,4,4,0,0.3],
     "sweep":{"0":[70,80,88]}},          # optional: index -> alternative values
    {"name":"coating","comp":[4.6,30,17,57,54,3,0.1],"exclude_from_filling":true},
    {"name":"glycerol","comp":[0,0,0,99.5,0,0,0],"polyol":true},
    {"name":"darkchoc","comp":[6,33,20,52,46,7,0],"fixed":5},
    {"name":"flavour","comp":[0,0,0,0,0,0,0],"bounds":[0.3,1]}
  ]
}
comp order: protein, fat, saturated, carbohydrate, sugars, fibre, salt (g/100 g).
Polyols count as carbohydrate but 2.4 kcal/g. Salt is weighted x3, fibre x0.3.
"""
import itertools, json, sys
import numpy as np
from scipy.optimize import minimize

KEYS = ['prot', 'fat', 'sat', 'carb', 'sug', 'fib', 'salt']
W = np.array([1, 1, 1, 1, 1, 0.3, 3])


def fit(ings, target):
    A = np.array([i['comp'] for i in ings], float).T / 100
    T = np.array([target[k] for k in KEYS], float)
    pol = np.array([1.0 if i.get('polyol') else 0.0 for i in ings])

    def kcal(x):
        p, f, s, c, sg, fb, sl = A @ x
        g = float((pol * x * A[3]).sum())
        return 4 * p + 9 * f + 4 * (c - g) + 2.4 * g + 2 * fb

    def obj(x):
        r = (A @ x - T) * W
        e = ((kcal(x) - target['kcal']) / 10) ** 2 if 'kcal' in target else 0
        return float(r @ r) + e

    n = len(ings)
    cons = [{'type': 'eq', 'fun': lambda x: x.sum() - 100}]
    for i in range(n - 1):
        cons.append({'type': 'ineq', 'fun': lambda x, i=i: x[i] - x[i + 1]})
    for i, ing in enumerate(ings):
        if 'fixed' in ing:
            cons.append({'type': 'eq', 'fun': lambda x, i=i, v=ing['fixed']: x[i] - v})
    bounds = [tuple(i.get('bounds', (0, 100))) for i in ings]
    x0 = np.linspace(2, 0.5, n); x0 = x0 / x0.sum() * 100
    r = minimize(obj, x0, bounds=bounds, constraints=cons, method='SLSQP')
    return r.x, A, T, kcal


def report(ings, x, A, T, kcal):
    for i, v in zip(ings, x):
        print(f"  {i['name']:14s} {v:6.1f} g/100 g")
    print('  model', np.round(A @ x, 1), round(kcal(x)), 'kcal')
    print('  label', T)
    keep = np.array([not i.get('exclude_from_filling') for i in ings])
    if not keep.all():
        tot = x[keep].sum()
        print(f'\n  part being cloned = {tot:.1f}% of product; per 100 g of it:')
        for i, v in zip(ings, x):
            if not i.get('exclude_from_filling'):
                print(f"    {i['name']:14s} {100 * v / tot:5.1f}")
        xf = np.where(keep, x, 0)
        print('    macros', np.round(A @ xf / tot * 100, 1), round(kcal(xf) / tot * 100), 'kcal')


def main():
    spec = json.load(open(sys.argv[1]))
    ings, target = spec['ingredients'], spec['target']
    x, A, T, kcal = fit(ings, target)
    print('Best fit:'); report(ings, x, A, T, kcal)
    if '--sweep' not in sys.argv:
        return
    axes = [(ii, int(k), vals) for ii, i in enumerate(ings) for k, vals in i.get('sweep', {}).items()]
    rows = []
    for combo in itertools.product(*[a[2] for a in axes]):
        trial = json.loads(json.dumps(ings))
        for (ii, k, _), v in zip(axes, combo):
            trial[ii]['comp'][k] = v
        x, A, T, _ = fit(trial, target)
        rows.append((np.abs(A @ x - T).max(), *x))
    o = np.array(rows); good = o[o[:, 0] < 1.5]
    print(f'\nSweep: {len(o)} scenarios, {len(good)} within 1.5 g of every label value')
    for j, i in enumerate(ings):
        v = good[:, j + 1] if len(good) else o[:, j + 1]
        print(f"  {i['name']:14s} min {v.min():5.1f}  median {np.median(v):5.1f}  max {v.max():5.1f}")


if __name__ == '__main__':
    main()
