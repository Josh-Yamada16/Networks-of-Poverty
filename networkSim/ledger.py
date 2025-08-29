import time
import uuid
import json
from typing import Optional, Dict, Any

import pandas as pd


class Ledger:
    """In-memory ledger backed by a pandas DataFrame.

    Usage:
        ledger = Ledger()
        ledger.record(iteration=0, from_node='A', to_node='B', amount=5.0, method='trade')
        ledger.to_csv('ledger.csv')
"""

    def __init__(self) -> None:
        cols = [
            "tx_id",
            "iteration",
            "ts",
            "from_node",
            "to_node",
            "amount",
            "method",
            "metadata",
        ]
        self.df = pd.DataFrame(columns=cols)

    def record(self,
               *,
               iteration: int,
               from_node: Optional[Any],
               to_node: Optional[Any],
               amount: float,
               method: Optional[str] = None,
               metadata: Optional[Dict] = None,
               tx_id: Optional[str] = None,
               ts: Optional[float] = None) -> str:
        """Append a transaction to the ledger and return its tx_id.

        Fields:
            iteration: simulation iteration index
            from_node / to_node: node identifiers (str or int)
            amount: numeric token amount (positive)
            method: short string describing the action
            metadata: optional dict (will be JSON-serialized)
        """
        if amount is None:
            raise ValueError("amount must be provided")
        tx_id = tx_id or str(uuid.uuid4())
        ts = ts or time.time()
        meta_json = json.dumps(metadata or {})
        row = {
            "tx_id": tx_id,
            "iteration": int(iteration),
            "ts": float(ts),
            "from_node": from_node,
            "to_node": to_node,
            "amount": float(amount),
            "method": method,
            "metadata": meta_json,
        }
        # append row
        self.df = pd.concat([self.df, pd.DataFrame([row])], ignore_index=True)
        return tx_id

    def get_iteration(self, iteration: int) -> pd.DataFrame:
        """Return a copy of the DataFrame rows for the given iteration."""
        return self.df[self.df["iteration"] == int(iteration)].copy()

    def query(self, where: Optional[str] = None) -> pd.DataFrame:
        """Return DataFrame filtered by a pandas-query string (optional)."""
        if where:
            return self.df.query(where).copy()
        return self.df.copy()

    def to_csv(self, path: str, index: bool = False) -> None:
        self.df.to_csv(path, index=index)

    def to_parquet(self, path: str, index: bool = False, engine: str = "pyarrow") -> None:
        # engine optional: 'pyarrow' or 'fastparquet'
        self.df.to_parquet(path, index=index, engine=engine)

    def to_jsonl(self, path: str) -> None:
        with open(path, "w", encoding="utf8") as f:
            for r in self.df.to_dict(orient="records"):
                f.write(json.dumps(r) + "\n")

    def clear(self) -> None:
        """Clear all ledger entries (in-memory)."""
        self.df = self.df.iloc[0:0].copy()

    def summary_by_iteration(self) -> pd.DataFrame:
        """Return a DataFrame aggregated by iteration with total sent and received per iteration."""
        df = self.df.copy()
        # total amount transacted in iteration
        agg = df.groupby("iteration").amount.sum().rename("total_transacted").reset_index()
        return agg

    def validate_money_conservation(self, balances_before: Dict[Any, float], balances_after: Dict[Any, float]) -> bool:
        """Quick check: sum of balances before == sum after (floating tolerance)."""
        s1 = sum(float(v) for v in balances_before.values())
        s2 = sum(float(v) for v in balances_after.values())
        return abs(s1 - s2) < 1e-6
