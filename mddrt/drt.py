import pandas as pd
from mddrt.drt_builder import DirectlyRootedTreeBuilder
from mddrt.drt_parameters import DirectlyRootedTreeParameters


class DirectlyRootedTree:
    def __init__(self, log: pd.DataFrame, params: DirectlyRootedTreeParameters) -> None:
        self.log = log
        self.params = params
        self.drt = DirectlyRootedTreeBuilder(self.log, self.params).get_tree()
