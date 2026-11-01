# CICO E-Wallet Application

A Python-based digital wallet application developed using Tkinter. It allows users to register, log in, manage their wallet balance, send and receive money, cash in, cash out, and pay bills through a graphical user interface.

## Project Description

CICO E-Wallet is an educational digital wallet system designed to demonstrate basic financial transactions using Python and Object-Oriented Programming (OOP).

The application uses local file storage to save user information, wallet balances, and transaction records. Each user's registered Philippine mobile number also serves as their CICO Account Number.

## Features

- **User Registration** – Create an account using a name, email address, phone number, and password.
- **User Login** – Log in using an email address or registered phone number.
- **Account Verification** – Verify user identity when performing protected transactions.
- **Session Management** – Manage the currently logged-in user's session.
- **Dashboard** – View account information, wallet balance, and available services.
- **Send Money** – Transfer money to another registered CICO user.
- **Cash In** – Add funds to the wallet.
- **Cash Out** – Withdraw funds from the wallet.
- **Bill Payments** – Pay bills through available categories and service providers.
- **Transaction History** – View previous transactions and their details.
- **Transaction Receipts** – Display transaction information and reference numbers.
- **Data Persistence** – Save user accounts, wallet balances, and transaction records locally.

## Technologies Used

- Python
- Tkinter
- JSON
- TXT
- hashlib
- decimal
- datetime
- os
- secrets

## Project Folder Structure

```text
CICO-E-WALLET/
│
├── main.py
├── wallet.py
├── receipt.py
├── verification.py
├── session.py
├── README.md
│
├── database/
│   ├── users.txt
│   └── wallets.json
│
└── ui/
    ├── __init__.py
    ├── account_store.py
    ├── register.py
    ├── login.py
    ├── dashboard.py
    ├── sendmoney.py
    ├── cashin.py
    ├── cashout.py
    ├── billpayments.py
    ├── service_ui.py
    └── theme.py
```

## Description of Important Files

| File | Description |
|---|---|
| `main.py` | Starts the application and manages screen navigation. |
| `wallet.py` | Handles wallet balances, deposits, withdrawals, and transfers. |
| `receipt.py` | Manages transaction receipts and transaction history. |
| `verification.py` | Handles user verification for protected wallet operations. |
| `session.py` | Manages the currently logged-in user's session. |
| `account_store.py` | Manages account registration and authentication data. |
| `register.py` | Provides the registration interface. |
| `login.py` | Provides the login interface. |
| `dashboard.py` | Displays wallet information and available services. |
| `sendmoney.py` | Handles money transfers. |
| `cashin.py` | Handles wallet deposits. |
| `cashout.py` | Handles wallet withdrawals. |
| `billpayments.py` | Handles bill payments. |
| `service_ui.py` | Provides shared service window functionality. |
| `theme.py` | Contains shared interface colors and styling. |
| `users.txt` | Stores registered user information in JSON format. |
| `wallets.json` | Stores wallet balances and transaction records. |

## Installation and Setup

### 1. Install Python

Download Python from:

https://www.python.org/downloads/

Make sure Python is added to your system PATH.

### 2. Open the Project Folder

Open a terminal or command prompt inside the CICO E-Wallet project directory.

### 3. Run the Application

```bash
python main.py
```

## How to Use

1. Open the application.
2. Register a new account or use an existing account.
3. Log in using your credentials.
4. Access the dashboard.
5. Select the wallet service you want to use.
6. Follow the instructions displayed in the selected service window.
7. Check your wallet balance and transaction history.

## Database Information

The application uses local files to store its data.

| File | Purpose |
|---|---|
| `database/users.txt` | Stores registered user information. |
| `database/wallets.json` | Stores wallet balances and transaction records. |

The registered phone number also serves as the user's CICO Account Number.

**Important:** Do not manually delete or modify the database files because doing so may cause loss of account information, wallet balances, or transaction history.

## Object-Oriented Programming Concepts

The application demonstrates:

- **Classes and Objects** – Organize wallet operations and graphical interface components.
- **Encapsulation** – Manage wallet-related data and operations within classes.
- **Modularity** – Separate application functions into individual Python files.
- **Code Reusability** – Reuse shared interface components and styling.

## Project Purpose

This project was developed as an educational demonstration of Python programming, Object-Oriented Programming, graphical user interface development, file handling, session management, verification, and basic digital wallet operations.

## Disclaimer

CICO E-Wallet is intended for educational and demonstration purposes only. It uses local file storage and is not connected to actual banks, payment gateways, or financial institutions. It is not intended for real-money transactions.
## Disclaimer

CICO E-Wallet is intended for educational and demonstration purposes only. It uses local file storage and is not connected to actual banks, payment gateways, or financial institutions. It is not intended for real-money transactions.
