"""
Extra features - not for master
"""
import bt
#import ffn
import pandas as pd
#from matplotlib import pyplot as plt


class StrategyLoaded(bt.core.Strategy):
    """
    Dummy class for loading strategies' data from file
    """

    def __init__(self, data, positions):
        self.data = data
        self._positions = positions

    @property
    def prices(self):
        return self.data['price']

    @property
    def values(self):
        return self.data['value']

    @property
    def fees(self):
        return self.data['fees']

    @property
    def positions(self):
        return self._positions


class BacktestLoaded(bt.backtest.Backtest):
    """
    Dummy class for loading backtests' data from file
    """

    def __init__(self, name, data, positions, weights, herfindahl):
        self.name = name
        self.data = pd.DataFrame()
        self._strategy = StrategyLoaded(data, positions)

        self._weights = weights
        self._sweights = weights
        self._herfindahl = herfindahl
        self.stats = self.strategy.prices.calc_perf_stats()

    @property
    def strategy(self):
        return self._strategy

    @property
    def weights(self):
        return self._weights

    @property
    def security_weigths(self):
        return self._sweights

    @property
    def herfindahl_index(self):
        return self._herfindahl


def save_results(results, fname, positions=False, weights=False, herfindahl=False,
                 complevel=5, complib='blosc'):
    """
    Function that saves the following data to HDF5 file:
    - strategy's data (price, value, cash, fees),
    - positions for each security (if positions==True)
    - weights of each security (if weights==True)
    - Herfindahl index (if herfindahl==True)

    Convention for key-names in file:
        /backtest-name/data
        /backtest-name/positions
        /backtest-name/weights
        /backtest-name/herfindahl
    """

    for bst_name in results.backtests:
        bst = results.backtests[bst_name]
        bst.strategy.data.to_hdf(fname, bst.name+'/data',
                                 complevel=complevel, complib=complib)
        if positions:
            bst.strategy.positions.to_hdf(fname, bst.name+'/positions',
                                          complevel=complevel, complib=complib)
        if weights:
            bst.security_weights.to_hdf(fname, bst.name+'/weights',
                                        complevel=complevel, complib=complib)
        if herfindahl:
            bst.herfindahl_index.to_hdf(fname, bst.name+'/herfindahl',
                                        complevel=complevel, complib=complib)


def read_results(fname):
    """
    Read backtests' results from HDF5 file

    Convention for key-names in file:
        /backtest-name/data
        /backtest-name/positions
        /backtest-name/weights
        /backtest-name/herfindahl
    """

    # Get all keys and unique names of backtests
    st = pd.HDFStore(fname)
    keys = st.keys()
    st.close()

    bst_names = list(set([k.split('/')[1] for k in keys]))

    backtests = []
    for bn in bst_names:

        df_data = pd.read_hdf(fname, '/%s/data' %(bn))
        try:
            df_positions = pd.read_hdf(fname, '/%s/positions' %(bn))
        except KeyError:
            df_positions = pd.DataFrame()

        try:
            df_sec_weights = pd.read_hdf(fname, '/%s/weights' %(bn))
        except KeyError:
            df_sec_weights = pd.DataFrame()

        try:
            df_herfindahl = pd.read_hdf(fname, '/%s/herfindahl' %(bn))
        except KeyError:
            df_herfindahl = pd.DataFrame()

        bt0 = BacktestLoaded(bn, df_data, df_positions, df_sec_weights,
                             df_herfindahl)
        backtests.append(bt0)

    return bt.backtest.Result(*backtests)
