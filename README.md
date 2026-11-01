# CICO E-Wallet Application

A Python-based digital wallet application developed using Tkinter. It allows users to register, log in, manage their wallet balance, send and receive money, cash in, cash out, and pay bills through a graphical user interface.

## Project Description

CICO E-Wallet is an educational digital wallet system designed to demonstrate basic financial transactions using Python and Object-Oriented Programming (OOP).

The application uses local file storage to save user information, wallet balances, and transaction records. Each user's registered Philippine mobile number also serves as their CICO Account Number.

## Features

- **User Registration** – Create an account using a name, email address, phone number, and password.
- **User Login** – Log in using an email address or registered phone number.
- **Dashboard** – View account information, wallet balance, and available services.
- **Send Money** – Transfer money to another registered CICO user using their CICO Account Number.
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

## Installation and Setup

### 1. Install Python

Download and install Python from:

https://www.python.org/downloads/

Make sure Python is added to your system PATH.

### 2. Open the Project Folder

Open a terminal or command prompt and navigate to the CICO E-Wallet project directory.

### 3. Run the Application

Execute the following command:

```bash
python main.py
```

The CICO E-Wallet application should open in a new window.

## How to Use

1. Open the application.
2. Register a new account if you do not have an existing account.
3. Enter your login credentials.
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

The registered phone number serves as the user's CICO Account Number.

**Important:** Do not manually delete or modify the database files because doing so may cause users to lose their saved account information, wallet balances, or transaction history.

## Object-Oriented Programming Concepts

The application demonstrates the following OOP concepts:

- **Classes and Objects** – Used to organize wallet operations and GUI components.
- **Encapsulation** – Wallet operations and related data are managed within the Wallet class.
- **Modularity** – Different application functions are separated into individual Python files.
- **Code Reusability** – Shared interface components and styling are reused throughout the application.

## Project Purpose

This project was developed as an educational demonstration of Python programming, Object-Oriented Programming, graphical user interface development, file handling, and basic digital wallet operations.

## Disclaimer

CICO E-Wallet is intended for educational and demonstration purposes only. It uses local file storage and is not connected to actual banks, payment gateways, or financial institutions. It is not intended for real-money transactions.
