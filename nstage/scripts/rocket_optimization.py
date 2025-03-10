import time
import numpy as np
import matplotlib.pyplot as plt
from nstage import Nstage
from scipy.optimize import root_scalar
from deap import base, creator, tools, algorithms

vf = 3000  # exhaust velocity in m/s
beta = np.array([0.5, 0.3, 0.2])  # Stage weights
epsilon = np.array([0.08, 0.10, 0.15])  # Structure mass fraction
alpha = np.array([1.1, 1.2, 1.3])  # Stage efficiency
solvers = ['newton', 'bisection', 'secant', 'scipy', 'genetic']
results = {}

def Nstage(vf, beta, epsilon, alpha, solver='newton', tol=1e-9, max_iter=100):
    def f(p):
        return vf + np.sum(beta * np.log(epsilon + alpha * (1 - epsilon) * p))

    def df(p):
        return np.sum(alpha * beta / (epsilon + alpha * (1 - epsilon) * p))

    if solver == 'newton':
        p = 0.1
        for _ in range(max_iter):
            f_p, df_p = f(p), df(p)
            if abs(f_p) < tol:
                return p
            p -= f_p / df_p
        raise ValueError("Newton's method did not converge.")

    elif solver == 'bisection':
        a, b = 0, 1
        if f(a) * f(b) > 0:
            raise ValueError("Bisection method requires bracketing.")
        for _ in range(max_iter):
            p = (a + b) / 2
            if abs(f(p)) < tol:
                return p
            if f(a) * f(p) < 0:
                b = p
            else:
                a = p
        raise ValueError("Bisection method did not converge.")

    elif solver == 'secant':
        p0, p1 = 0.1, 0.9
        for _ in range(max_iter):
            f_p0, f_p1 = f(p0), f(p1)
            if abs(f_p1) < tol:
                return p1
            p_new = p1 - f_p1 * (p1 - p0) / (f_p1 - f_p0)
            p0, p1 = p1, p_new
        raise ValueError("Secant method did not converge.")

    elif solver == 'scipy':
        sol = root_scalar(f, bracket=[0, 1], method='brentq', xtol=tol)
        if sol.converged:
            return sol.root
        raise ValueError("SciPy root-finding method did not converge.")

    elif solver == 'genetic':
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)
        toolbox = base.Toolbox()
        toolbox.register("attr_float", np.random.uniform, 0, 1)
        toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_float, n=1)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        toolbox.register("evaluate", lambda ind: (abs(f(ind[0])),))
        toolbox.register("mate", tools.cxBlend, alpha=0.5)
        toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=0.1, indpb=0.2)
        toolbox.register("select", tools.selTournament, tournsize=3)

        pop = toolbox.population(n=100)
        algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=50, verbose=False)
        return tools.selBest(pop, k=1)[0][0]

    else:
        raise ValueError("Invalid solver selection.")

for solver in solvers:
    start_time = time.time()
    try:
        p_opt = Nstage(vf, beta, epsilon, alpha, solver=solver)
        elapsed_time = time.time() - start_time
        results[solver] = {'p_opt': p_opt, 'time': elapsed_time}
        print(f"{solver.capitalize()} Method: p_opt = {p_opt:.6f}, Time: {elapsed_time:.6f} sec")
    except ValueError as e:
        print(f"{solver.capitalize()} Method: {str(e)}")
        results[solver] = {'p_opt': None, 'time': None}

# Note: Plotting code is omitted as it's not needed for the .py file, but you can include it if desired.
