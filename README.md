# Pyteal Milestone Dapp

**NOTE**: This code is not audited and should not be used in production environment.

**NOTE**: This tutorial is not for beginners and assumes the reader is familiar with setting up a private algorand node and setting up testnet accounts.

### Resources
[Read about algorand sandbox](https://developer.algorand.org/tutorials/exploring-the-algorand-sandbox/)

[This tutorial also touches on using algorand sandbox and setting account](https://dappradar.com/blog/introduction-to-algorand-pyteal-smart-signature-development)

## Goal of Project and Concepts Covered.

1. To teach about **transacion fee pooling** on algorand.
2. **Inner Transactions**.
3. **Handling Errors** when interacting with smart contract via a python script.
4. **Writing unittest** for a samrt contract.

## Set Up Environment

**Docker Compose** _MUST_ be installed. [Instructions](https://docs.docker.com/compose/install/).

On a _Windows_ machine, **Docker Desktop** comes with the necessary tools. Please see the [Windows](#windows) section in getting started for more details.

**Warning**: Algorand Sandbox is _not_ meant for production environments and should _not_ be used to store secure Algorand keys. Updates may reset all the data and keys that are stored.

## Usage

Use the **sandbox** command to interact with the Algorand Sandbox.

```plain
sandbox commands:
  up    [config]  -> start the sandbox environment.
  down            -> tear down the sandbox environment.
```

Sandbox creates the following API endpoints:

- `algod`:
  - address: `http://localhost:4001`
  - token: `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`
- `kmd`:
  - address: `http://localhost:4002`
  - token: `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`
- `indexer`:
  - address: `http://localhost:8980`

## Getting Started

### Ubuntu and macOS

Make sure the docker daemon is running and docker-compose is installed.

Open a terminal and run:

```bash
git clone https://github.com/algorand/sandbox.git
```

In whatever local directory the sandbox should reside. Then:

```bash
cd sandbox
./sandbox up

It should run the released version of sandbox
```


This will run the `sandbox` shell script with the default configuration. See the [Basic Configuration](#basic-configuration) for other options.

### Dependencies

Install all project dependencies

Open a terminal and run:

```bash
 python3 pip -r requirements.txt
```

### Set Environment Variables

create a ```.env``` file in the root of the project and paste your environment variables as described in the ```.env.example``` file.

### Set Testnet Account

import 3 testnet accounts to the goal app by running this command:
```bash
./sandbox goal account import
```

### Fund Imported Testnet Account

```
./sandbox goal clerk send -a {amount} -f {provided accounts in goal} -t {imported accounts}
```

### For more information on how to use alglorand sandbox visit. [sandox][./sandbox goal clerk send -a 200000000 -f client -t EJNUGTF56QWEQWZGRKGCF7U4QY2UDJ2GXYCCZFSHDFKDLW2XE7MCJNKP7E]
### For more information on how to use alglorand sandbox. [sandox]()

## Run the App
 Open a terminal in project directory and run

 ```bash
 cd src
 python3 deploy.py
 ```
