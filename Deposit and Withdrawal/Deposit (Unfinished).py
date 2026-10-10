import re
import tkinter as tk
from dataclasses import dataclass
from datetime import datetime
from decimal import InvalidOperation, Decimal
from tkinter import messagebox, ttk


cash = "₱"
bal = "1000.00"
max = Decimal("100000")

def money(value : Decimal) -> str:
    return f"{cash}{value:,.2f}"

def analyze_amount(text: str) -> Decimal:
    try:
        amount = Decimal(text.strip()) 
   
    except InvalidOperation:
        raise ValueError("Enter Valid Amount.")
    if not amount.is_finite or amount <= 0:
        raise ValueError("Amount should be greater than 0")
    if amount.as_tuple().exponent < -2:
        raise ValueError("Amount should only have 2 decimal places")
    if amount > max:
        raise ValueError("The max amount is only 100000 Pesos")
    return amount

@dataclass
class transaction:
   ref: str
   kind:str
   amount: Decimal
   method: str
   details: str
   bal_aft: str
   
class Wallet:
    def __init__(self, opening_bal: str = "0.00"):
        self.bal = Decimal(opening_bal)    
        self.hist: list[transaction] = []     
        
    def record(self, kind, amount, method, details) -> transaction:
        tx = transaction(
            ref = f"TXN-{len(self.hist) + 1:05d}",
            kind = kind,
            amount = amount,
            method = method,
            details = details,
            timestamp = datetime.now(),
            bal_aft = self.bal,
        )
        self.hist.append(tx)
        return tx
    
    def deposit(self, amount: Decimal, method: str, details: str) -> transaction:
        if amount <= 0:
            raise ValueError("Deposit must be greater than zero")
        self.bal += amount
        return self._record("Deposit: ", amount, method, details)
        
    def withdraw(self, amount: Decimal, method: str, details: str) -> transaction:
        if amount <= 0:
            raise ValueError("Withdrawal must be greater than zero")
        self.bal -= amount
        return self._record("Withdrawal: ", amount, method, details)
    
# GUI PART

FORMS = {
    "deposit": {
        "tab": "Deposit (Cash in)",
        "heading" : "Cash out",
        "Method label "
    }
}


        
        