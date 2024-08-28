# Generated by fragment (with the help of ariadne-codegen)
# Source: queries/

from typing import Any, Dict, List, Optional

from .add_ledger_entry import AddLedgerEntry
from .add_ledger_entry_runtime import AddLedgerEntryRuntime
from .async_client import AsyncFragmentClient
from .create_custom_link import CreateCustomLink
from .create_ledger import CreateLedger
from .enums import ReadBalanceConsistencyMode
from .get_ledger import GetLedger
from .get_ledger_account_balance import GetLedgerAccountBalance
from .get_ledger_account_lines import GetLedgerAccountLines
from .get_ledger_entry import GetLedgerEntry
from .get_schema import GetSchema
from .get_workspace import GetWorkspace
from .input_types import (
    CreateLedgerInput,
    CurrencyMatchInput,
    CustomAccountInput,
    CustomTxInput,
    LedgerEntriesFilterSet,
    LedgerEntryGroupBalanceFilterSet,
    LedgerEntryGroupInput,
    LedgerEntryTagInput,
    LedgerLineInput,
    LedgerLinesFilterSet,
    SchemaInput,
    UpdateLedgerEntryInput,
    UpdateLedgerInput,
)
from .list_ledger_account_balances import ListLedgerAccountBalances
from .list_ledger_accounts import ListLedgerAccounts
from .list_ledger_entries import ListLedgerEntries
from .list_ledger_entry_group_balances import ListLedgerEntryGroupBalances
from .list_multi_currency_ledger_account_balances import (
    ListMultiCurrencyLedgerAccountBalances,
)
from .reconcile_tx import ReconcileTx
from .reconcile_tx_runtime import ReconcileTxRuntime
from .store_schema import StoreSchema
from .store_schema_again import StoreSchemaAgain
from .sync_custom_accounts import SyncCustomAccounts
from .sync_custom_txs import SyncCustomTxs
from .update_ledger import UpdateLedger
from .update_ledger_entry import UpdateLedgerEntry


def gql(q: str) -> str:
    return q


class Client(AsyncFragmentClient):
    async def store_schema(self, schema: SchemaInput, **kwargs: Any) -> StoreSchema:
        query = gql(
            """
            mutation storeSchema($schema: SchemaInput!) {
              storeSchema(schema: $schema) {
                __typename
                ... on StoreSchemaResult {
                  schema {
                    key
                    name
                    version {
                      created
                      version
                    }
                  }
                }
                ... on Error {
                  code
                  message
                  retryable
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {"schema": schema}
        response = await self.execute(
            query=query, operation_name="storeSchema", variables=variables, **kwargs
        )
        data = self.get_data(response)
        return StoreSchema.model_validate(data)

    async def store_schema_again(
        self, schema: SchemaInput, **kwargs: Any
    ) -> StoreSchemaAgain:
        query = gql(
            """
            mutation storeSchemaAgain($schema: SchemaInput!) {
              storeSchema(schema: $schema) {
                __typename
                ... on StoreSchemaResult {
                  schema {
                    key
                    name
                    version {
                      created
                      version
                    }
                  }
                }
                ... on Error {
                  code
                  message
                  retryable
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {"schema": schema}
        response = await self.execute(
            query=query,
            operation_name="storeSchemaAgain",
            variables=variables,
            **kwargs
        )
        data = self.get_data(response)
        return StoreSchemaAgain.model_validate(data)

    async def create_ledger(
        self, ik: Any, ledger: CreateLedgerInput, schema_key: Any, **kwargs: Any
    ) -> CreateLedger:
        query = gql(
            """
            mutation createLedger($ik: SafeString!, $ledger: CreateLedgerInput!, $schemaKey: SafeString!) {
              createLedger(ik: $ik, ledger: $ledger, schema: {key: $schemaKey}) {
                __typename
                ... on CreateLedgerResult {
                  ledger {
                    id
                    ik
                    name
                    created
                    schema {
                      key
                    }
                  }
                  isIkReplay
                }
                ... on Error {
                  code
                  message
                  retryable
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {
            "ik": ik,
            "ledger": ledger,
            "schemaKey": schema_key,
        }
        response = await self.execute(
            query=query, operation_name="createLedger", variables=variables, **kwargs
        )
        data = self.get_data(response)
        return CreateLedger.model_validate(data)

    async def add_ledger_entry(
        self,
        ik: Any,
        ledger_ik: Any,
        type: str,
        parameters: Any,
        posted: Optional[Any] = None,
        tags: Optional[List[LedgerEntryTagInput]] = None,
        groups: Optional[List[LedgerEntryGroupInput]] = None,
        **kwargs: Any
    ) -> AddLedgerEntry:
        query = gql(
            """
            mutation addLedgerEntry($ik: SafeString!, $ledgerIk: SafeString!, $type: String!, $posted: DateTime, $parameters: JSON!, $tags: [LedgerEntryTagInput!], $groups: [LedgerEntryGroupInput!]) {
              addLedgerEntry(
                ik: $ik
                entry: {ledger: {ik: $ledgerIk}, type: $type, posted: $posted, parameters: $parameters, tags: $tags, groups: $groups}
              ) {
                __typename
                ... on AddLedgerEntryResult {
                  isIkReplay
                  entry {
                    type
                    id
                    ik
                    posted
                    created
                  }
                  lines {
                    id
                    amount
                    account {
                      path
                    }
                  }
                }
                ... on Error {
                  code
                  message
                  retryable
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {
            "ik": ik,
            "ledgerIk": ledger_ik,
            "type": type,
            "posted": posted,
            "parameters": parameters,
            "tags": tags,
            "groups": groups,
        }
        response = await self.execute(
            query=query, operation_name="addLedgerEntry", variables=variables, **kwargs
        )
        data = self.get_data(response)
        return AddLedgerEntry.model_validate(data)

    async def add_ledger_entry_runtime(
        self,
        ik: Any,
        type: str,
        ledger_ik: Any,
        lines: List[LedgerLineInput],
        posted: Optional[Any] = None,
        tags: Optional[List[LedgerEntryTagInput]] = None,
        groups: Optional[List[LedgerEntryGroupInput]] = None,
        **kwargs: Any
    ) -> AddLedgerEntryRuntime:
        query = gql(
            """
            mutation addLedgerEntryRuntime($ik: SafeString!, $type: String!, $ledgerIk: SafeString!, $posted: DateTime, $lines: [LedgerLineInput!]!, $tags: [LedgerEntryTagInput!], $groups: [LedgerEntryGroupInput!]) {
              addLedgerEntry(
                ik: $ik
                entry: {type: $type, ledger: {ik: $ledgerIk}, posted: $posted, lines: $lines, tags: $tags, groups: $groups}
              ) {
                __typename
                ... on AddLedgerEntryResult {
                  isIkReplay
                  entry {
                    type
                    id
                    ik
                    posted
                    created
                  }
                  lines {
                    id
                    amount
                    account {
                      path
                    }
                  }
                }
                ... on Error {
                  code
                  message
                  retryable
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {
            "ik": ik,
            "type": type,
            "ledgerIk": ledger_ik,
            "posted": posted,
            "lines": lines,
            "tags": tags,
            "groups": groups,
        }
        response = await self.execute(
            query=query,
            operation_name="addLedgerEntryRuntime",
            variables=variables,
            **kwargs
        )
        data = self.get_data(response)
        return AddLedgerEntryRuntime.model_validate(data)

    async def reconcile_tx(
        self,
        ledger_ik: Any,
        type: str,
        parameters: Any,
        tags: Optional[List[LedgerEntryTagInput]] = None,
        groups: Optional[List[LedgerEntryGroupInput]] = None,
        **kwargs: Any
    ) -> ReconcileTx:
        query = gql(
            """
            mutation reconcileTx($ledgerIk: SafeString!, $type: String!, $parameters: JSON!, $tags: [LedgerEntryTagInput!], $groups: [LedgerEntryGroupInput!]) {
              reconcileTx(
                entry: {ledger: {ik: $ledgerIk}, type: $type, parameters: $parameters, tags: $tags, groups: $groups}
              ) {
                __typename
                ... on ReconcileTxResult {
                  entry {
                    id
                    ik
                    date
                    posted
                    created
                    description
                  }
                  lines {
                    id
                    amount
                    account {
                      path
                    }
                    externalTxId
                  }
                }
                ... on Error {
                  code
                  message
                  retryable
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {
            "ledgerIk": ledger_ik,
            "type": type,
            "parameters": parameters,
            "tags": tags,
            "groups": groups,
        }
        response = await self.execute(
            query=query, operation_name="reconcileTx", variables=variables, **kwargs
        )
        data = self.get_data(response)
        return ReconcileTx.model_validate(data)

    async def reconcile_tx_runtime(
        self,
        ledger_ik: Any,
        type: str,
        lines: List[LedgerLineInput],
        tags: Optional[List[LedgerEntryTagInput]] = None,
        groups: Optional[List[LedgerEntryGroupInput]] = None,
        **kwargs: Any
    ) -> ReconcileTxRuntime:
        query = gql(
            """
            mutation reconcileTxRuntime($ledgerIk: SafeString!, $type: String!, $lines: [LedgerLineInput!]!, $tags: [LedgerEntryTagInput!], $groups: [LedgerEntryGroupInput!]) {
              reconcileTx(
                entry: {ledger: {ik: $ledgerIk}, type: $type, lines: $lines, tags: $tags, groups: $groups}
              ) {
                __typename
                ... on ReconcileTxResult {
                  entry {
                    id
                    ik
                    date
                    posted
                    created
                    description
                  }
                  lines {
                    id
                    amount
                    account {
                      path
                    }
                    externalTxId
                  }
                }
                ... on Error {
                  code
                  message
                  retryable
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {
            "ledgerIk": ledger_ik,
            "type": type,
            "lines": lines,
            "tags": tags,
            "groups": groups,
        }
        response = await self.execute(
            query=query,
            operation_name="reconcileTxRuntime",
            variables=variables,
            **kwargs
        )
        data = self.get_data(response)
        return ReconcileTxRuntime.model_validate(data)

    async def update_ledger_entry(
        self,
        entry_ik: Any,
        ledger_ik: Any,
        update: UpdateLedgerEntryInput,
        **kwargs: Any
    ) -> UpdateLedgerEntry:
        query = gql(
            """
            mutation updateLedgerEntry($entryIk: SafeString!, $ledgerIk: SafeString!, $update: UpdateLedgerEntryInput!) {
              updateLedgerEntry(
                ledgerEntry: {ik: $entryIk, ledger: {ik: $ledgerIk}}
                update: $update
              ) {
                __typename
                ... on UpdateLedgerEntryResult {
                  entry {
                    id
                    ik
                    posted
                    created
                    description
                    lines {
                      nodes {
                        id
                        amount
                        account {
                          path
                        }
                      }
                    }
                    groups {
                      key
                      value
                    }
                    tags {
                      key
                      value
                    }
                  }
                }
                ... on Error {
                  code
                  message
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {
            "entryIk": entry_ik,
            "ledgerIk": ledger_ik,
            "update": update,
        }
        response = await self.execute(
            query=query,
            operation_name="updateLedgerEntry",
            variables=variables,
            **kwargs
        )
        data = self.get_data(response)
        return UpdateLedgerEntry.model_validate(data)

    async def update_ledger(
        self, ledger_ik: Any, update: UpdateLedgerInput, **kwargs: Any
    ) -> UpdateLedger:
        query = gql(
            """
            mutation updateLedger($ledgerIk: SafeString!, $update: UpdateLedgerInput!) {
              updateLedger(ledger: {ik: $ledgerIk}, update: $update) {
                __typename
                ... on UpdateLedgerResult {
                  ledger {
                    id
                    ik
                    name
                  }
                }
                ... on Error {
                  code
                  message
                  retryable
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {"ledgerIk": ledger_ik, "update": update}
        response = await self.execute(
            query=query, operation_name="updateLedger", variables=variables, **kwargs
        )
        data = self.get_data(response)
        return UpdateLedger.model_validate(data)

    async def create_custom_link(
        self, name: str, ik: Any, **kwargs: Any
    ) -> CreateCustomLink:
        query = gql(
            """
            mutation createCustomLink($name: String!, $ik: SafeString!) {
              createCustomLink(name: $name, ik: $ik) {
                __typename
                ... on CreateCustomLinkResult {
                  link {
                    id
                    name
                    created
                  }
                  isIkReplay
                }
                ... on Error {
                  code
                  message
                  retryable
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {"name": name, "ik": ik}
        response = await self.execute(
            query=query,
            operation_name="createCustomLink",
            variables=variables,
            **kwargs
        )
        data = self.get_data(response)
        return CreateCustomLink.model_validate(data)

    async def sync_custom_accounts(
        self, link_id: str, accounts: List[CustomAccountInput], **kwargs: Any
    ) -> SyncCustomAccounts:
        query = gql(
            """
            mutation syncCustomAccounts($linkId: ID!, $accounts: [CustomAccountInput!]!) {
              syncCustomAccounts(link: {id: $linkId}, accounts: $accounts) {
                __typename
                ... on SyncCustomAccountsResult {
                  accounts {
                    id
                    externalId
                    name
                    currency {
                      code
                      customCurrencyId
                    }
                  }
                }
                ... on Error {
                  code
                  message
                  retryable
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {"linkId": link_id, "accounts": accounts}
        response = await self.execute(
            query=query,
            operation_name="syncCustomAccounts",
            variables=variables,
            **kwargs
        )
        data = self.get_data(response)
        return SyncCustomAccounts.model_validate(data)

    async def sync_custom_txs(
        self, link_id: str, txs: List[CustomTxInput], **kwargs: Any
    ) -> SyncCustomTxs:
        query = gql(
            """
            mutation syncCustomTxs($linkId: ID!, $txs: [CustomTxInput!]!) {
              syncCustomTxs(link: {id: $linkId}, txs: $txs) {
                __typename
                ... on SyncCustomTxsResult {
                  txs {
                    __typename
                    linkId
                    id
                    externalId
                    externalAccountId
                    amount
                    description
                    posted
                  }
                }
                ... on Error {
                  code
                  message
                  retryable
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {"linkId": link_id, "txs": txs}
        response = await self.execute(
            query=query, operation_name="syncCustomTxs", variables=variables, **kwargs
        )
        data = self.get_data(response)
        return SyncCustomTxs.model_validate(data)

    async def get_ledger(self, ik: Any, **kwargs: Any) -> GetLedger:
        query = gql(
            """
            query getLedger($ik: SafeString!) {
              ledger(ledger: {ik: $ik}) {
                id
                ik
                name
                created
                balanceUTCOffset
              }
            }
            """
        )
        variables: Dict[str, object] = {"ik": ik}
        response = await self.execute(
            query=query, operation_name="getLedger", variables=variables, **kwargs
        )
        data = self.get_data(response)
        return GetLedger.model_validate(data)

    async def get_ledger_entry(
        self, ik: Any, ledger_ik: Any, **kwargs: Any
    ) -> GetLedgerEntry:
        query = gql(
            """
            query getLedgerEntry($ik: SafeString!, $ledgerIk: SafeString!) {
              ledgerEntry(ledgerEntry: {ik: $ik, ledger: {ik: $ledgerIk}}) {
                id
                ik
                posted
                created
                description
                lines {
                  nodes {
                    id
                    amount
                    account {
                      path
                    }
                  }
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {"ik": ik, "ledgerIk": ledger_ik}
        response = await self.execute(
            query=query, operation_name="getLedgerEntry", variables=variables, **kwargs
        )
        data = self.get_data(response)
        return GetLedgerEntry.model_validate(data)

    async def list_ledger_accounts(
        self,
        ledger_ik: Any,
        after: Optional[str] = None,
        first: Optional[int] = None,
        before: Optional[str] = None,
        **kwargs: Any
    ) -> ListLedgerAccounts:
        query = gql(
            """
            query listLedgerAccounts($ledgerIk: SafeString!, $after: String, $first: Int, $before: String) {
              ledger(ledger: {ik: $ledgerIk}) {
                id
                ik
                name
                created
                ledgerAccounts(after: $after, first: $first, before: $before) {
                  nodes {
                    id
                    path
                    name
                    type
                    created
                  }
                  pageInfo {
                    hasNextPage
                    endCursor
                    hasPreviousPage
                    startCursor
                  }
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {
            "ledgerIk": ledger_ik,
            "after": after,
            "first": first,
            "before": before,
        }
        response = await self.execute(
            query=query,
            operation_name="listLedgerAccounts",
            variables=variables,
            **kwargs
        )
        data = self.get_data(response)
        return ListLedgerAccounts.model_validate(data)

    async def list_ledger_account_balances(
        self,
        ledger_ik: Any,
        after: Optional[str] = None,
        first: Optional[int] = None,
        before: Optional[str] = None,
        balance_currency: Optional[CurrencyMatchInput] = None,
        balance_at: Optional[Any] = None,
        own_balance_consistency_mode: Optional[ReadBalanceConsistencyMode] = None,
        **kwargs: Any
    ) -> ListLedgerAccountBalances:
        query = gql(
            """
            query listLedgerAccountBalances($ledgerIk: SafeString!, $after: String, $first: Int, $before: String, $balanceCurrency: CurrencyMatchInput, $balanceAt: LastMoment, $ownBalanceConsistencyMode: ReadBalanceConsistencyMode) {
              ledger(ledger: {ik: $ledgerIk}) {
                id
                ik
                name
                created
                ledgerAccounts(after: $after, first: $first, before: $before) {
                  nodes {
                    id
                    path
                    name
                    type
                    created
                    ownBalance(
                      currency: $balanceCurrency
                      at: $balanceAt
                      consistencyMode: $ownBalanceConsistencyMode
                    )
                    childBalance(currency: $balanceCurrency, at: $balanceAt)
                    balance(currency: $balanceCurrency, at: $balanceAt)
                  }
                  pageInfo {
                    hasNextPage
                    endCursor
                    hasPreviousPage
                    startCursor
                  }
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {
            "ledgerIk": ledger_ik,
            "after": after,
            "first": first,
            "before": before,
            "balanceCurrency": balance_currency,
            "balanceAt": balance_at,
            "ownBalanceConsistencyMode": own_balance_consistency_mode,
        }
        response = await self.execute(
            query=query,
            operation_name="listLedgerAccountBalances",
            variables=variables,
            **kwargs
        )
        data = self.get_data(response)
        return ListLedgerAccountBalances.model_validate(data)

    async def list_multi_currency_ledger_account_balances(
        self,
        ledger_ik: Any,
        after: Optional[str] = None,
        first: Optional[int] = None,
        before: Optional[str] = None,
        balance_at: Optional[Any] = None,
        own_balances_consistency_mode: Optional[ReadBalanceConsistencyMode] = None,
        **kwargs: Any
    ) -> ListMultiCurrencyLedgerAccountBalances:
        query = gql(
            """
            query listMultiCurrencyLedgerAccountBalances($ledgerIk: SafeString!, $after: String, $first: Int, $before: String, $balanceAt: LastMoment, $ownBalancesConsistencyMode: ReadBalanceConsistencyMode) {
              ledger(ledger: {ik: $ledgerIk}) {
                id
                ik
                name
                created
                ledgerAccounts(after: $after, first: $first, before: $before) {
                  nodes {
                    id
                    path
                    name
                    type
                    created
                    ownBalances(at: $balanceAt, consistencyMode: $ownBalancesConsistencyMode) {
                      nodes {
                        currency {
                          code
                          customCurrencyId
                        }
                        amount
                      }
                    }
                    childBalances(at: $balanceAt) {
                      nodes {
                        currency {
                          code
                          customCurrencyId
                        }
                        amount
                      }
                    }
                    balances(at: $balanceAt) {
                      nodes {
                        currency {
                          code
                          customCurrencyId
                        }
                        amount
                      }
                    }
                  }
                  pageInfo {
                    hasNextPage
                    endCursor
                    hasPreviousPage
                    startCursor
                  }
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {
            "ledgerIk": ledger_ik,
            "after": after,
            "first": first,
            "before": before,
            "balanceAt": balance_at,
            "ownBalancesConsistencyMode": own_balances_consistency_mode,
        }
        response = await self.execute(
            query=query,
            operation_name="listMultiCurrencyLedgerAccountBalances",
            variables=variables,
            **kwargs
        )
        data = self.get_data(response)
        return ListMultiCurrencyLedgerAccountBalances.model_validate(data)

    async def get_ledger_account_lines(
        self,
        path: str,
        ledger_ik: Any,
        after: Optional[str] = None,
        first: Optional[int] = None,
        before: Optional[str] = None,
        filter: Optional[LedgerLinesFilterSet] = None,
        **kwargs: Any
    ) -> GetLedgerAccountLines:
        query = gql(
            """
            query getLedgerAccountLines($path: String!, $ledgerIk: SafeString!, $after: String, $first: Int, $before: String, $filter: LedgerLinesFilterSet) {
              ledgerAccount(ledgerAccount: {ledger: {ik: $ledgerIk}, path: $path}) {
                id
                path
                lines(after: $after, first: $first, before: $before, filter: $filter) {
                  nodes {
                    id
                    posted
                    created
                    amount
                    description
                  }
                  pageInfo {
                    hasNextPage
                    endCursor
                    hasPreviousPage
                    startCursor
                  }
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {
            "path": path,
            "ledgerIk": ledger_ik,
            "after": after,
            "first": first,
            "before": before,
            "filter": filter,
        }
        response = await self.execute(
            query=query,
            operation_name="getLedgerAccountLines",
            variables=variables,
            **kwargs
        )
        data = self.get_data(response)
        return GetLedgerAccountLines.model_validate(data)

    async def get_ledger_account_balance(
        self,
        path: str,
        ledger_ik: Any,
        balance_currency: Optional[CurrencyMatchInput] = None,
        balance_at: Optional[Any] = None,
        own_balance_consistency_mode: Optional[ReadBalanceConsistencyMode] = None,
        **kwargs: Any
    ) -> GetLedgerAccountBalance:
        query = gql(
            """
            query getLedgerAccountBalance($path: String!, $ledgerIk: SafeString!, $balanceCurrency: CurrencyMatchInput, $balanceAt: LastMoment, $ownBalanceConsistencyMode: ReadBalanceConsistencyMode) {
              ledgerAccount(ledgerAccount: {ledger: {ik: $ledgerIk}, path: $path}) {
                id
                path
                ownBalance(
                  currency: $balanceCurrency
                  at: $balanceAt
                  consistencyMode: $ownBalanceConsistencyMode
                )
              }
            }
            """
        )
        variables: Dict[str, object] = {
            "path": path,
            "ledgerIk": ledger_ik,
            "balanceCurrency": balance_currency,
            "balanceAt": balance_at,
            "ownBalanceConsistencyMode": own_balance_consistency_mode,
        }
        response = await self.execute(
            query=query,
            operation_name="getLedgerAccountBalance",
            variables=variables,
            **kwargs
        )
        data = self.get_data(response)
        return GetLedgerAccountBalance.model_validate(data)

    async def get_schema(
        self, key: Any, version: Optional[int] = None, **kwargs: Any
    ) -> GetSchema:
        query = gql(
            """
            query getSchema($key: SafeString!, $version: Int) {
              schema(schema: {key: $key, version: $version}) {
                key
                name
                version {
                  created
                  version
                  json
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {"key": key, "version": version}
        response = await self.execute(
            query=query, operation_name="getSchema", variables=variables, **kwargs
        )
        data = self.get_data(response)
        return GetSchema.model_validate(data)

    async def list_ledger_entries(
        self,
        ledger_ik: Any,
        after: Optional[str] = None,
        first: Optional[int] = None,
        before: Optional[str] = None,
        filter: Optional[LedgerEntriesFilterSet] = None,
        **kwargs: Any
    ) -> ListLedgerEntries:
        query = gql(
            """
            query listLedgerEntries($ledgerIk: SafeString!, $after: String, $first: Int, $before: String, $filter: LedgerEntriesFilterSet) {
              ledger(ledger: {ik: $ledgerIk}) {
                ledgerEntries(after: $after, first: $first, before: $before, filter: $filter) {
                  nodes {
                    ik
                    type
                    posted
                    lines {
                      nodes {
                        amount
                        account {
                          path
                        }
                      }
                    }
                  }
                  pageInfo {
                    hasNextPage
                    endCursor
                    hasPreviousPage
                    startCursor
                  }
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {
            "ledgerIk": ledger_ik,
            "after": after,
            "first": first,
            "before": before,
            "filter": filter,
        }
        response = await self.execute(
            query=query,
            operation_name="listLedgerEntries",
            variables=variables,
            **kwargs
        )
        data = self.get_data(response)
        return ListLedgerEntries.model_validate(data)

    async def get_workspace(self, **kwargs: Any) -> GetWorkspace:
        query = gql(
            """
            query getWorkspace {
              workspace {
                id
                name
              }
            }
            """
        )
        variables: Dict[str, object] = {}
        response = await self.execute(
            query=query, operation_name="getWorkspace", variables=variables, **kwargs
        )
        data = self.get_data(response)
        return GetWorkspace.model_validate(data)

    async def list_ledger_entry_group_balances(
        self,
        ledger_ik: Any,
        group_key: Any,
        group_value: Any,
        consistency_mode: Optional[ReadBalanceConsistencyMode] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
        first: Optional[int] = None,
        last: Optional[int] = None,
        filter: Optional[LedgerEntryGroupBalanceFilterSet] = None,
        **kwargs: Any
    ) -> ListLedgerEntryGroupBalances:
        query = gql(
            """
            query listLedgerEntryGroupBalances($ledgerIk: SafeString!, $groupKey: SafeString!, $groupValue: SafeString!, $consistencyMode: ReadBalanceConsistencyMode = use_account, $after: String, $before: String, $first: Int, $last: Int, $filter: LedgerEntryGroupBalanceFilterSet) {
              ledgerEntryGroup(
                ledgerEntryGroup: {ledger: {ik: $ledgerIk}, key: $groupKey, value: $groupValue}
              ) {
                key
                value
                created
                balances(
                  after: $after
                  before: $before
                  first: $first
                  last: $last
                  filter: $filter
                ) {
                  nodes {
                    account {
                      path
                    }
                    currency {
                      code
                      customCurrencyId
                    }
                    ownBalance(consistencyMode: $consistencyMode)
                  }
                  pageInfo {
                    hasNextPage
                    endCursor
                    hasPreviousPage
                    startCursor
                  }
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {
            "ledgerIk": ledger_ik,
            "groupKey": group_key,
            "groupValue": group_value,
            "consistencyMode": consistency_mode,
            "after": after,
            "before": before,
            "first": first,
            "last": last,
            "filter": filter,
        }
        response = await self.execute(
            query=query,
            operation_name="listLedgerEntryGroupBalances",
            variables=variables,
            **kwargs
        )
        data = self.get_data(response)
        return ListLedgerEntryGroupBalances.model_validate(data)
