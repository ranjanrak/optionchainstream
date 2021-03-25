"""
@author: rakeshr
"""

"""
Calculate implied volatility for required call or put option 
contract based on reverse Black and Scholes formula
"""

import numpy as np
from scipy.stats import norm

"""
Param defination:
opt_type = 'CALL' or 'PUT'
s = Spot Price
k =  Strike Price
t = Days to expiration in days
rfr = Risk-free Rate(% to be divided by 100). Considering fix 0.04 here
sigma = volatility
div = Annual dividend rate. Default to zero.
price = Known option price. Needed for implied_volatility function
"""


def d_one(s, k, t, rfr, sigma, div=0):
    """differential 1 calculation"""
    d_1 = (np.log(s / k) +
           (rfr - div + sigma ** 2 / 2) * t) / (sigma * np.sqrt(t))
    return d_1


def d_two(s, k, t, rfr, sigma, div=0):
    """differential 2 calculation"""
    d_2 = d_one(s, k, t, rfr, sigma, div) - sigma * np.sqrt(t)
    return d_2


def nd_one(opt_type, s, k, t, rfr, sigma, div=0):
    """nd1 calculation"""
    if opt_type == 'CALL':
        nd_1 = norm.cdf(d_one(s, k, t, rfr, sigma, div), 0, 1)
    elif opt_type == 'PUT':
        nd_1 = norm.cdf(-d_one(s, k, t, rfr, sigma, div), 0, 1)
    return nd_1


def nd_two(opt_type, s, k, t, rfr, sigma, div=0):
    """nd2 calculation"""
    if opt_type == 'CALL':
        nd_2 = norm.cdf(d_two(s, k, t, rfr, sigma, div), 0, 1)
    elif opt_type == 'PUT':
        nd_2 = norm.cdf(-d_two(s, k, t, rfr, sigma, div), 0, 1)
    return nd_2


def option_price(opt_type, s, k, t, rfr, sigma, div=0):
    """Market option price for request contract"""
    opt_type = opt_type.upper()
    t /= 365
    if opt_type == 'CALL':
        price = (s * np.exp(-div * t) *
                 nd_one(opt_type, s, k, t, rfr, sigma, div)
                 - k * np.exp(-rfr * t) *
                 nd_two(opt_type, s, k, t, rfr, sigma, div))
    elif opt_type == 'PUT':
        price = (k * np.exp(-rfr * t) *
                 nd_two(opt_type, s, k, t, rfr, sigma, div)
                 - s * np.exp(-div * t) *
                 nd_one(opt_type, s, k, t, rfr, sigma, div))
    return price


def option_vega(s, k, t, rfr, sigma, div=0):
    """option vega"""
    t /= 365
    vega = (.01 * s * np.exp(-div * t) * np.sqrt(t)
            * norm.pdf(d_one(s, k, t, rfr, sigma, div)))
    return vega


def implied_volatility(opt_type, s, k, t, rfr, price, div=0):
    """implied volatility approximation using black and scholes calculation"""
   
    #Epsilon is generally defined as a small positive number
    epsilon = 0.00000001 # measure of the dividend risk
    sigma = 1.0

    def black_scholes(opt_type, s, k, t, rfr, sigma, price, epsilon, div=0):
        diff = option_price(opt_type, s, k, t, rfr, sigma, div) - price
        while diff > epsilon:
            sigma = (sigma -
                     (option_price(opt_type, s, k, t, rfr, sigma, div) - price) /
                     (option_vega(s, k, t, rfr, sigma, div) * 100))
            diff = np.abs(
                    option_price(opt_type, s, k, t, rfr, sigma, div) - price)
        return sigma

    iv = black_scholes(opt_type, s, k, t, rfr, sigma, price, epsilon, div)
    return round((iv*100), 2)