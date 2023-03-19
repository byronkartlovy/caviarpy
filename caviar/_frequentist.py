import numpy as np
from scipy.optimize import minimize


def mle_fit(returns, model, quantile, caviar_func):
    """
    :param: returns (array): a series of daily returns
    :returns: scipy optimize result
    """
    params, bounds = initiate_params(model)
    result = minimize(neg_log_likelihood, params,
                      args=(returns, quantile, caviar_func), bounds=bounds)

    return result.x


def initiate_params(model):
    """
    generate the initial estimate of tau and betas

    for the bounds and constraints:
    The symmetric and igarch of these respond symmetrically to past returns,
    whereas the second allows the response to positive and negative returns
    to be different. All three are mean-reverting in the sense that
    the coefficient on the lagged VaR is not constrained to be 1.
    """
    # bounds for tau, intercept
    bounds = [(1e-4, None), (None, None)]
    if model == 'igarch':
        bounds += [(0, 1), (0, 1)]
    elif model == 'symmetric':
        # b1 for lagged var, b2 for abs(lagged return)
        bounds += [(0, 1), (0, 1)]
    elif model == 'asymmetric':
        # b1 for lagged var, b2 for (lagged return)^+, b3 for (lagged return)^-
        bounds = [(0, 1), (0, 1), (0, 1)]
    else:  # adaptive
        pass

    # number of parameters
    p = len(bounds)

    return np.random.uniform(0, 1, p), bounds


def neg_log_likelihood(params, returns, quantile, caviar_func):
    """
    :param: returns (array): a series of daily returns
    :param: betas (array): a series of coefficients
    :param: caviar_func (callable function): a CAViaR function that returns VaR
    :returns: negative log likelihood
    """
    T = len(returns)

    tau = params[0]
    betas = params[1:]

    sigmas = caviar_func(returns, betas)

    llh = (1 - T) * np.log(tau)
    for t in range(1, T):
        llh -= 1 / tau * max((quantile - 1) * (returns[t] - sigmas[t]),
                             quantile * (returns[t] - sigmas[t]))

    return -llh