import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import yfinance as yf
import riskfolio as rp
import matplotlib.pyplot as pl
import streamlit as st

def mc_opt(mv, returns, weights):
    def GBMsimulator(seed, So, mu, sigma, Cov, T, N):
        """
        Parameters
        seed:   seed of simulation
        So:     initial stocks' price
        mu:     expected return
        sigma:  volatility
        Cov:    covariance matrix
        T:      time period
        N:      number of increments
        """

        np.random.seed(seed)
        dim = np.size(So)
        t = np.linspace(0., T, int(N))
        A = np.linalg.cholesky(Cov)
        S = np.zeros([dim, int(N)])
        S[:, 0] = So['weights']
        for i in range(1, int(N)):
            drift = (mu - 0.5 * sigma**2) * (t[i] - t[i-1])
            Z = np.random.normal(0., 1., dim)
            diffusion = np.matmul(A, Z) * (np.sqrt(t[i] - t[i-1]))
            S[:, i] = S[:, i-1]*np.exp(drift + diffusion)
        return S, t

    # returns = asset_returns
    # returns

    cov_mat = 252*returns.cov()
    mu = np.mean(returns, axis=0).values*252  # Annualise the daily values
    sigma = np.std(returns, axis=0).values*np.sqrt(252) # Annualise the daily values

    seed = 22

    dim = len(weights);
    T = 36 / 12;
    N_SIMS = 1000  # 12 month horizon

    PORTFOLIO_VALUE = mv

    S0 = weights

    N_steps = int(T * 252)

    assets, time = GBMsimulator(seed, S0, mu, sigma, cov_mat, T, N_steps)

    # Number of Simulations

    np.random.seed(seed)

    Simulated_Paths = np.zeros([N_SIMS, dim, N_steps])

    Simulated_Paths[0, :, :] = assets

    # sim_prog = st.progress(1)

    for k in range(1, N_SIMS):
        # if k % N_SIMS / 100 == 0:
        #     sim_prog.progress(k / N_SIMS + 1 / N_SIMS * 100)
        seed = int(np.random.uniform(1, 2 ** 32 - 1, 1))
        Simulated_Paths[k, :, :] = GBMsimulator(seed, S0, mu, sigma, cov_mat, T, N_steps)[0]

    Simul_Last_Values = Simulated_Paths[:, :, (N_steps - 1)]
    # display(Simul_Last_Values.shape)
    # Simul_Last_Portf_Values = w.transpose().values*Simul_Last_Values
    # display(Simul_Last_Portf_Values.shape)
    X = pd.DataFrame(Simul_Last_Values).sum(axis=1)


    print('Portfolio Value Histogram:')
    # ax.figure()
    # ax.hist(X,bins=100, density=True, stacked=True)
    # ax.xlabel('Portfolio Value')
    # ax.ylabel('Probability Density Function')
    # # pl.show()
    # st.pyplot(pl.show())

    fig, ax = plt.subplots()
    ax.hist(X,bins=100, density=True, stacked=True)
    pl.xlabel('Portfolio Value')
    pl.ylabel('Probability Density Function')
    c1, c2, c3 = st.columns([1, 1, 1])

    with c2:
        st.pyplot(fig)
        st.write('The average value of your portfolio in 3 years based off of this simulation is: ' + str(np.mean(X)))

