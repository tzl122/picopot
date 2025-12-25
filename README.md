# Solana Pico Hybrid Wallet

A minimal Solana hybrid wallet project using a Raspberry Pi Pico
to explore Ed25519 cryptography and cold-wallet design concepts.
In the current version, transaction signing and broadcasting
are handled on a laptop due to hardware and implementation limitations.

## Features
- Pure Python Ed25519 implementation on Raspberry Pi Pico
- Experimental cold-wallet architecture
- Laptop-based Solana transaction signing
- Lightweight and low-cost hardware setup
- Works with Solana Devnet and Mainnet

## Architecture (Current Version)

### Raspberry Pi Pico
- Ed25519 key generation experiments
- Offline cryptographic primitives
- Cold-wallet design testing

### Laptop
- Creates and signs Solana transactions
- Broadcasts transactions to the Solana network

> ⚠️ Transaction signing is currently performed on the laptop.  
> Pico-based transaction signing is a planned improvement.
