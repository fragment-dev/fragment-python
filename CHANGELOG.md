# Changelog

All notable changes to `fragment-python` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

Releases prior to `1.0.0` were published before this changelog was added and
are not documented here.

## [1.0.0]

### Changed

- `GetLedgerAccountBalance` now returns total `balance` (self + children)
  instead of `ownBalance`.
- `ListLedgerAccountBalances` and `ListMultiCurrencyLedgerAccountBalances`
  now accept `consistencyMode` on `childBalance`, `childBalances`,
  `balance`, and `balances` fields.

### Removed

- `GetLedgerAccountBalanceWithChildRollup` has been removed.

### How to Upgrade

1. Upgrade your schema to use total balance consistency.
2. Edit your schema JSON. Change `ownBalanceUpdates` to
   `totalBalanceUpdates` in the ledger account consistency config.
3. Change `ownBalance` to `totalBalance` in entry conditions.
4. Ensure the schema has only one of `ownBalanceUpdates` or
   `totalBalanceUpdates`.
5. Deploy the new schema.
6. You can now set `consistencyConfig.totalBalanceUpdates: strong` on any
   account in the tree, and its balance will be strongly consistent.
7. Upgrade `fragment-python` to the latest version.
8. Change `$ownBalanceConsistencyMode` to `$balanceConsistencyMode`.
9. Use `GetLedgerAccountBalance` instead of
   `GetLedgerAccountBalanceWithChildRollup`.
