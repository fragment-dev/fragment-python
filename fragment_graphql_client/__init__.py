# Generated by fragment (with the help of ariadne-codegen)

from .add_ledger_entry import (
    AddLedgerEntry,
    AddLedgerEntryAddLedgerEntryAddLedgerEntryResult,
    AddLedgerEntryAddLedgerEntryAddLedgerEntryResultEntry,
    AddLedgerEntryAddLedgerEntryAddLedgerEntryResultLines,
    AddLedgerEntryAddLedgerEntryAddLedgerEntryResultLinesAccount,
    AddLedgerEntryAddLedgerEntryBadRequestError,
    AddLedgerEntryAddLedgerEntryInternalError,
)
from .add_ledger_entry_runtime import (
    AddLedgerEntryRuntime,
    AddLedgerEntryRuntimeAddLedgerEntryAddLedgerEntryResult,
    AddLedgerEntryRuntimeAddLedgerEntryAddLedgerEntryResultEntry,
    AddLedgerEntryRuntimeAddLedgerEntryAddLedgerEntryResultLines,
    AddLedgerEntryRuntimeAddLedgerEntryAddLedgerEntryResultLinesAccount,
    AddLedgerEntryRuntimeAddLedgerEntryBadRequestError,
    AddLedgerEntryRuntimeAddLedgerEntryInternalError,
)
from .async_client import AsyncFragmentClient
from .base_model import BaseModel, Upload
from .client import Client
from .create_custom_link import (
    CreateCustomLink,
    CreateCustomLinkCreateCustomLinkBadRequestError,
    CreateCustomLinkCreateCustomLinkCreateCustomLinkResult,
    CreateCustomLinkCreateCustomLinkCreateCustomLinkResultLink,
    CreateCustomLinkCreateCustomLinkInternalError,
)
from .create_ledger import (
    CreateLedger,
    CreateLedgerCreateLedgerBadRequestError,
    CreateLedgerCreateLedgerCreateLedgerResult,
    CreateLedgerCreateLedgerCreateLedgerResultLedger,
    CreateLedgerCreateLedgerCreateLedgerResultLedgerSchema,
    CreateLedgerCreateLedgerInternalError,
)
from .enums import (
    BalanceUpdateConsistencyMode,
    CurrencyCode,
    CurrencyMode,
    ExternalTransferType,
    ExternalTxSource,
    IncreaseEnv,
    LedgerAccountTypes,
    LedgerLinesConsistencyMode,
    LedgerMigrationStatus,
    LedgerTypes,
    ReadBalanceConsistencyMode,
    SceneEventType,
    SchemaConsistencyMode,
    StripeEnv,
    TxType,
    UnitEnv,
)
from .get_ledger import GetLedger, GetLedgerLedger
from .get_ledger_account_balance import (
    GetLedgerAccountBalance,
    GetLedgerAccountBalanceLedgerAccount,
)
from .get_ledger_account_lines import (
    GetLedgerAccountLines,
    GetLedgerAccountLinesLedgerAccount,
    GetLedgerAccountLinesLedgerAccountLines,
    GetLedgerAccountLinesLedgerAccountLinesNodes,
    GetLedgerAccountLinesLedgerAccountLinesPageInfo,
)
from .get_ledger_entry import (
    GetLedgerEntry,
    GetLedgerEntryLedgerEntry,
    GetLedgerEntryLedgerEntryLines,
    GetLedgerEntryLedgerEntryLinesNodes,
    GetLedgerEntryLedgerEntryLinesNodesAccount,
)
from .get_schema import GetSchema, GetSchemaSchema, GetSchemaSchemaVersion
from .get_workspace import GetWorkspace, GetWorkspaceWorkspace
from .input_types import (
    ChartOfAccountsInput,
    CreateCustomCurrencyInput,
    CreateLedgerAccountInput,
    CreateLedgerAccountsInput,
    CreateLedgerInput,
    CurrencyFilter,
    CurrencyMatchInput,
    CustomAccountInput,
    CustomTxInput,
    DateFilter,
    DateTimeFilter,
    EntryGroupMatchInput,
    ExternalAccountFilter,
    ExternalAccountMatchInput,
    GroupBalanceAccountFilter,
    Int96ConditionInput,
    Int96Filter,
    LedgerAccountConditionInput,
    LedgerAccountConsistencyConfigInput,
    LedgerAccountFilter,
    LedgerAccountGroupConsistencyConfigInput,
    LedgerAccountMatchInput,
    LedgerAccountsFilterSet,
    LedgerAccountTypeFilter,
    LedgerEntriesFilterSet,
    LedgerEntryConditionInput,
    LedgerEntryFilter,
    LedgerEntryGroupBalanceFilterSet,
    LedgerEntryGroupInput,
    LedgerEntryGroupMatchInput,
    LedgerEntryGroupsFilterSet,
    LedgerEntryInput,
    LedgerEntryMatchInput,
    LedgerEntryTagInput,
    LedgerLineInput,
    LedgerLineMatchInput,
    LedgerLinesFilterSet,
    LedgerMatchInput,
    LedgersFilterSet,
    LedgerTypeFilter,
    LinkMatchInput,
    SceneEntryInput,
    SceneEventInput,
    SceneInput,
    SchemaConditionInput,
    SchemaConsistencyConfigInput,
    SchemaCurrencyMatchInput,
    SchemaExternalAccountMatchInput,
    SchemaInput,
    SchemaInt96ConditionInput,
    SchemaLedgerAccountInput,
    SchemaLedgerAccountMatchInput,
    SchemaLedgerEntriesInput,
    SchemaLedgerEntryConditionInput,
    SchemaLedgerEntryGroupInput,
    SchemaLedgerEntryInput,
    SchemaLedgerEntryTagInput,
    SchemaLedgerLineInput,
    SchemaMatchInput,
    SchemaTxMatchInput,
    StringFilter,
    StringMatchFilter,
    TagFilter,
    TagMatchInput,
    TxMatchInput,
    TxTypeFilter,
    UpdateLedgerAccountInput,
    UpdateLedgerEntryInput,
    UpdateLedgerInput,
)
from .list_ledger_account_balances import (
    ListLedgerAccountBalances,
    ListLedgerAccountBalancesLedger,
    ListLedgerAccountBalancesLedgerLedgerAccounts,
    ListLedgerAccountBalancesLedgerLedgerAccountsNodes,
    ListLedgerAccountBalancesLedgerLedgerAccountsPageInfo,
)
from .list_ledger_accounts import (
    ListLedgerAccounts,
    ListLedgerAccountsLedger,
    ListLedgerAccountsLedgerLedgerAccounts,
    ListLedgerAccountsLedgerLedgerAccountsNodes,
    ListLedgerAccountsLedgerLedgerAccountsPageInfo,
)
from .list_ledger_entries import (
    ListLedgerEntries,
    ListLedgerEntriesLedger,
    ListLedgerEntriesLedgerLedgerEntries,
    ListLedgerEntriesLedgerLedgerEntriesNodes,
    ListLedgerEntriesLedgerLedgerEntriesNodesLines,
    ListLedgerEntriesLedgerLedgerEntriesNodesLinesNodes,
    ListLedgerEntriesLedgerLedgerEntriesNodesLinesNodesAccount,
    ListLedgerEntriesLedgerLedgerEntriesPageInfo,
)
from .list_ledger_entry_group_balances import (
    ListLedgerEntryGroupBalances,
    ListLedgerEntryGroupBalancesLedgerEntryGroup,
    ListLedgerEntryGroupBalancesLedgerEntryGroupBalances,
    ListLedgerEntryGroupBalancesLedgerEntryGroupBalancesNodes,
    ListLedgerEntryGroupBalancesLedgerEntryGroupBalancesNodesAccount,
    ListLedgerEntryGroupBalancesLedgerEntryGroupBalancesNodesCurrency,
    ListLedgerEntryGroupBalancesLedgerEntryGroupBalancesPageInfo,
)
from .list_multi_currency_ledger_account_balances import (
    ListMultiCurrencyLedgerAccountBalances,
    ListMultiCurrencyLedgerAccountBalancesLedger,
    ListMultiCurrencyLedgerAccountBalancesLedgerLedgerAccounts,
    ListMultiCurrencyLedgerAccountBalancesLedgerLedgerAccountsNodes,
    ListMultiCurrencyLedgerAccountBalancesLedgerLedgerAccountsNodesBalances,
    ListMultiCurrencyLedgerAccountBalancesLedgerLedgerAccountsNodesBalancesNodes,
    ListMultiCurrencyLedgerAccountBalancesLedgerLedgerAccountsNodesBalancesNodesCurrency,
    ListMultiCurrencyLedgerAccountBalancesLedgerLedgerAccountsNodesChildBalances,
    ListMultiCurrencyLedgerAccountBalancesLedgerLedgerAccountsNodesChildBalancesNodes,
    ListMultiCurrencyLedgerAccountBalancesLedgerLedgerAccountsNodesChildBalancesNodesCurrency,
    ListMultiCurrencyLedgerAccountBalancesLedgerLedgerAccountsNodesOwnBalances,
    ListMultiCurrencyLedgerAccountBalancesLedgerLedgerAccountsNodesOwnBalancesNodes,
    ListMultiCurrencyLedgerAccountBalancesLedgerLedgerAccountsNodesOwnBalancesNodesCurrency,
    ListMultiCurrencyLedgerAccountBalancesLedgerLedgerAccountsPageInfo,
)
from .reconcile_tx import (
    ReconcileTx,
    ReconcileTxReconcileTxBadRequestError,
    ReconcileTxReconcileTxInternalError,
    ReconcileTxReconcileTxReconcileTxResult,
    ReconcileTxReconcileTxReconcileTxResultEntry,
    ReconcileTxReconcileTxReconcileTxResultLines,
    ReconcileTxReconcileTxReconcileTxResultLinesAccount,
)
from .reconcile_tx_runtime import (
    ReconcileTxRuntime,
    ReconcileTxRuntimeReconcileTxBadRequestError,
    ReconcileTxRuntimeReconcileTxInternalError,
    ReconcileTxRuntimeReconcileTxReconcileTxResult,
    ReconcileTxRuntimeReconcileTxReconcileTxResultEntry,
    ReconcileTxRuntimeReconcileTxReconcileTxResultLines,
    ReconcileTxRuntimeReconcileTxReconcileTxResultLinesAccount,
)
from .store_schema import (
    StoreSchema,
    StoreSchemaStoreSchemaBadRequestError,
    StoreSchemaStoreSchemaInternalError,
    StoreSchemaStoreSchemaStoreSchemaResult,
    StoreSchemaStoreSchemaStoreSchemaResultSchema,
    StoreSchemaStoreSchemaStoreSchemaResultSchemaVersion,
)
from .store_schema_again import (
    StoreSchemaAgain,
    StoreSchemaAgainStoreSchemaBadRequestError,
    StoreSchemaAgainStoreSchemaInternalError,
    StoreSchemaAgainStoreSchemaStoreSchemaResult,
    StoreSchemaAgainStoreSchemaStoreSchemaResultSchema,
    StoreSchemaAgainStoreSchemaStoreSchemaResultSchemaVersion,
)
from .sync_custom_accounts import (
    SyncCustomAccounts,
    SyncCustomAccountsSyncCustomAccountsBadRequestError,
    SyncCustomAccountsSyncCustomAccountsInternalError,
    SyncCustomAccountsSyncCustomAccountsSyncCustomAccountsResult,
    SyncCustomAccountsSyncCustomAccountsSyncCustomAccountsResultAccounts,
    SyncCustomAccountsSyncCustomAccountsSyncCustomAccountsResultAccountsCurrency,
)
from .sync_custom_txs import (
    SyncCustomTxs,
    SyncCustomTxsSyncCustomTxsBadRequestError,
    SyncCustomTxsSyncCustomTxsInternalError,
    SyncCustomTxsSyncCustomTxsSyncCustomTxsResult,
    SyncCustomTxsSyncCustomTxsSyncCustomTxsResultTxs,
)
from .update_ledger import (
    UpdateLedger,
    UpdateLedgerUpdateLedgerBadRequestError,
    UpdateLedgerUpdateLedgerInternalError,
    UpdateLedgerUpdateLedgerUpdateLedgerResult,
    UpdateLedgerUpdateLedgerUpdateLedgerResultLedger,
)
from .update_ledger_entry import (
    UpdateLedgerEntry,
    UpdateLedgerEntryUpdateLedgerEntryBadRequestError,
    UpdateLedgerEntryUpdateLedgerEntryInternalError,
    UpdateLedgerEntryUpdateLedgerEntryUpdateLedgerEntryResult,
    UpdateLedgerEntryUpdateLedgerEntryUpdateLedgerEntryResultEntry,
    UpdateLedgerEntryUpdateLedgerEntryUpdateLedgerEntryResultEntryGroups,
    UpdateLedgerEntryUpdateLedgerEntryUpdateLedgerEntryResultEntryLines,
    UpdateLedgerEntryUpdateLedgerEntryUpdateLedgerEntryResultEntryLinesNodes,
    UpdateLedgerEntryUpdateLedgerEntryUpdateLedgerEntryResultEntryLinesNodesAccount,
    UpdateLedgerEntryUpdateLedgerEntryUpdateLedgerEntryResultEntryTags,
)

__all__ = [
    "AddLedgerEntry",
    "AddLedgerEntryAddLedgerEntryAddLedgerEntryResult",
    "AddLedgerEntryAddLedgerEntryAddLedgerEntryResultEntry",
    "AddLedgerEntryAddLedgerEntryAddLedgerEntryResultLines",
    "AddLedgerEntryAddLedgerEntryAddLedgerEntryResultLinesAccount",
    "AddLedgerEntryAddLedgerEntryBadRequestError",
    "AddLedgerEntryAddLedgerEntryInternalError",
    "AddLedgerEntryRuntime",
    "AddLedgerEntryRuntimeAddLedgerEntryAddLedgerEntryResult",
    "AddLedgerEntryRuntimeAddLedgerEntryAddLedgerEntryResultEntry",
    "AddLedgerEntryRuntimeAddLedgerEntryAddLedgerEntryResultLines",
    "AddLedgerEntryRuntimeAddLedgerEntryAddLedgerEntryResultLinesAccount",
    "AddLedgerEntryRuntimeAddLedgerEntryBadRequestError",
    "AddLedgerEntryRuntimeAddLedgerEntryInternalError",
    "AsyncFragmentClient",
    "BalanceUpdateConsistencyMode",
    "BaseModel",
    "ChartOfAccountsInput",
    "Client",
    "CreateCustomCurrencyInput",
    "CreateCustomLink",
    "CreateCustomLinkCreateCustomLinkBadRequestError",
    "CreateCustomLinkCreateCustomLinkCreateCustomLinkResult",
    "CreateCustomLinkCreateCustomLinkCreateCustomLinkResultLink",
    "CreateCustomLinkCreateCustomLinkInternalError",
    "CreateLedger",
    "CreateLedgerAccountInput",
    "CreateLedgerAccountsInput",
    "CreateLedgerCreateLedgerBadRequestError",
    "CreateLedgerCreateLedgerCreateLedgerResult",
    "CreateLedgerCreateLedgerCreateLedgerResultLedger",
    "CreateLedgerCreateLedgerCreateLedgerResultLedgerSchema",
    "CreateLedgerCreateLedgerInternalError",
    "CreateLedgerInput",
    "CurrencyCode",
    "CurrencyFilter",
    "CurrencyMatchInput",
    "CurrencyMode",
    "CustomAccountInput",
    "CustomTxInput",
    "DateFilter",
    "DateTimeFilter",
    "EntryGroupMatchInput",
    "ExternalAccountFilter",
    "ExternalAccountMatchInput",
    "ExternalTransferType",
    "ExternalTxSource",
    "GetLedger",
    "GetLedgerAccountBalance",
    "GetLedgerAccountBalanceLedgerAccount",
    "GetLedgerAccountLines",
    "GetLedgerAccountLinesLedgerAccount",
    "GetLedgerAccountLinesLedgerAccountLines",
    "GetLedgerAccountLinesLedgerAccountLinesNodes",
    "GetLedgerAccountLinesLedgerAccountLinesPageInfo",
    "GetLedgerEntry",
    "GetLedgerEntryLedgerEntry",
    "GetLedgerEntryLedgerEntryLines",
    "GetLedgerEntryLedgerEntryLinesNodes",
    "GetLedgerEntryLedgerEntryLinesNodesAccount",
    "GetLedgerLedger",
    "GetSchema",
    "GetSchemaSchema",
    "GetSchemaSchemaVersion",
    "GetWorkspace",
    "GetWorkspaceWorkspace",
    "GroupBalanceAccountFilter",
    "IncreaseEnv",
    "Int96ConditionInput",
    "Int96Filter",
    "LedgerAccountConditionInput",
    "LedgerAccountConsistencyConfigInput",
    "LedgerAccountFilter",
    "LedgerAccountGroupConsistencyConfigInput",
    "LedgerAccountMatchInput",
    "LedgerAccountTypeFilter",
    "LedgerAccountTypes",
    "LedgerAccountsFilterSet",
    "LedgerEntriesFilterSet",
    "LedgerEntryConditionInput",
    "LedgerEntryFilter",
    "LedgerEntryGroupBalanceFilterSet",
    "LedgerEntryGroupInput",
    "LedgerEntryGroupMatchInput",
    "LedgerEntryGroupsFilterSet",
    "LedgerEntryInput",
    "LedgerEntryMatchInput",
    "LedgerEntryTagInput",
    "LedgerLineInput",
    "LedgerLineMatchInput",
    "LedgerLinesConsistencyMode",
    "LedgerLinesFilterSet",
    "LedgerMatchInput",
    "LedgerMigrationStatus",
    "LedgerTypeFilter",
    "LedgerTypes",
    "LedgersFilterSet",
    "LinkMatchInput",
    "ListLedgerAccountBalances",
    "ListLedgerAccountBalancesLedger",
    "ListLedgerAccountBalancesLedgerLedgerAccounts",
    "ListLedgerAccountBalancesLedgerLedgerAccountsNodes",
    "ListLedgerAccountBalancesLedgerLedgerAccountsPageInfo",
    "ListLedgerAccounts",
    "ListLedgerAccountsLedger",
    "ListLedgerAccountsLedgerLedgerAccounts",
    "ListLedgerAccountsLedgerLedgerAccountsNodes",
    "ListLedgerAccountsLedgerLedgerAccountsPageInfo",
    "ListLedgerEntries",
    "ListLedgerEntriesLedger",
    "ListLedgerEntriesLedgerLedgerEntries",
    "ListLedgerEntriesLedgerLedgerEntriesNodes",
    "ListLedgerEntriesLedgerLedgerEntriesNodesLines",
    "ListLedgerEntriesLedgerLedgerEntriesNodesLinesNodes",
    "ListLedgerEntriesLedgerLedgerEntriesNodesLinesNodesAccount",
    "ListLedgerEntriesLedgerLedgerEntriesPageInfo",
    "ListLedgerEntryGroupBalances",
    "ListLedgerEntryGroupBalancesLedgerEntryGroup",
    "ListLedgerEntryGroupBalancesLedgerEntryGroupBalances",
    "ListLedgerEntryGroupBalancesLedgerEntryGroupBalancesNodes",
    "ListLedgerEntryGroupBalancesLedgerEntryGroupBalancesNodesAccount",
    "ListLedgerEntryGroupBalancesLedgerEntryGroupBalancesNodesCurrency",
    "ListLedgerEntryGroupBalancesLedgerEntryGroupBalancesPageInfo",
    "ListMultiCurrencyLedgerAccountBalances",
    "ListMultiCurrencyLedgerAccountBalancesLedger",
    "ListMultiCurrencyLedgerAccountBalancesLedgerLedgerAccounts",
    "ListMultiCurrencyLedgerAccountBalancesLedgerLedgerAccountsNodes",
    "ListMultiCurrencyLedgerAccountBalancesLedgerLedgerAccountsNodesBalances",
    "ListMultiCurrencyLedgerAccountBalancesLedgerLedgerAccountsNodesBalancesNodes",
    "ListMultiCurrencyLedgerAccountBalancesLedgerLedgerAccountsNodesBalancesNodesCurrency",
    "ListMultiCurrencyLedgerAccountBalancesLedgerLedgerAccountsNodesChildBalances",
    "ListMultiCurrencyLedgerAccountBalancesLedgerLedgerAccountsNodesChildBalancesNodes",
    "ListMultiCurrencyLedgerAccountBalancesLedgerLedgerAccountsNodesChildBalancesNodesCurrency",
    "ListMultiCurrencyLedgerAccountBalancesLedgerLedgerAccountsNodesOwnBalances",
    "ListMultiCurrencyLedgerAccountBalancesLedgerLedgerAccountsNodesOwnBalancesNodes",
    "ListMultiCurrencyLedgerAccountBalancesLedgerLedgerAccountsNodesOwnBalancesNodesCurrency",
    "ListMultiCurrencyLedgerAccountBalancesLedgerLedgerAccountsPageInfo",
    "ReadBalanceConsistencyMode",
    "ReconcileTx",
    "ReconcileTxReconcileTxBadRequestError",
    "ReconcileTxReconcileTxInternalError",
    "ReconcileTxReconcileTxReconcileTxResult",
    "ReconcileTxReconcileTxReconcileTxResultEntry",
    "ReconcileTxReconcileTxReconcileTxResultLines",
    "ReconcileTxReconcileTxReconcileTxResultLinesAccount",
    "ReconcileTxRuntime",
    "ReconcileTxRuntimeReconcileTxBadRequestError",
    "ReconcileTxRuntimeReconcileTxInternalError",
    "ReconcileTxRuntimeReconcileTxReconcileTxResult",
    "ReconcileTxRuntimeReconcileTxReconcileTxResultEntry",
    "ReconcileTxRuntimeReconcileTxReconcileTxResultLines",
    "ReconcileTxRuntimeReconcileTxReconcileTxResultLinesAccount",
    "SceneEntryInput",
    "SceneEventInput",
    "SceneEventType",
    "SceneInput",
    "SchemaConditionInput",
    "SchemaConsistencyConfigInput",
    "SchemaConsistencyMode",
    "SchemaCurrencyMatchInput",
    "SchemaExternalAccountMatchInput",
    "SchemaInput",
    "SchemaInt96ConditionInput",
    "SchemaLedgerAccountInput",
    "SchemaLedgerAccountMatchInput",
    "SchemaLedgerEntriesInput",
    "SchemaLedgerEntryConditionInput",
    "SchemaLedgerEntryGroupInput",
    "SchemaLedgerEntryInput",
    "SchemaLedgerEntryTagInput",
    "SchemaLedgerLineInput",
    "SchemaMatchInput",
    "SchemaTxMatchInput",
    "StoreSchema",
    "StoreSchemaAgain",
    "StoreSchemaAgainStoreSchemaBadRequestError",
    "StoreSchemaAgainStoreSchemaInternalError",
    "StoreSchemaAgainStoreSchemaStoreSchemaResult",
    "StoreSchemaAgainStoreSchemaStoreSchemaResultSchema",
    "StoreSchemaAgainStoreSchemaStoreSchemaResultSchemaVersion",
    "StoreSchemaStoreSchemaBadRequestError",
    "StoreSchemaStoreSchemaInternalError",
    "StoreSchemaStoreSchemaStoreSchemaResult",
    "StoreSchemaStoreSchemaStoreSchemaResultSchema",
    "StoreSchemaStoreSchemaStoreSchemaResultSchemaVersion",
    "StringFilter",
    "StringMatchFilter",
    "StripeEnv",
    "SyncCustomAccounts",
    "SyncCustomAccountsSyncCustomAccountsBadRequestError",
    "SyncCustomAccountsSyncCustomAccountsInternalError",
    "SyncCustomAccountsSyncCustomAccountsSyncCustomAccountsResult",
    "SyncCustomAccountsSyncCustomAccountsSyncCustomAccountsResultAccounts",
    "SyncCustomAccountsSyncCustomAccountsSyncCustomAccountsResultAccountsCurrency",
    "SyncCustomTxs",
    "SyncCustomTxsSyncCustomTxsBadRequestError",
    "SyncCustomTxsSyncCustomTxsInternalError",
    "SyncCustomTxsSyncCustomTxsSyncCustomTxsResult",
    "SyncCustomTxsSyncCustomTxsSyncCustomTxsResultTxs",
    "TagFilter",
    "TagMatchInput",
    "TxMatchInput",
    "TxType",
    "TxTypeFilter",
    "UnitEnv",
    "UpdateLedger",
    "UpdateLedgerAccountInput",
    "UpdateLedgerEntry",
    "UpdateLedgerEntryInput",
    "UpdateLedgerEntryUpdateLedgerEntryBadRequestError",
    "UpdateLedgerEntryUpdateLedgerEntryInternalError",
    "UpdateLedgerEntryUpdateLedgerEntryUpdateLedgerEntryResult",
    "UpdateLedgerEntryUpdateLedgerEntryUpdateLedgerEntryResultEntry",
    "UpdateLedgerEntryUpdateLedgerEntryUpdateLedgerEntryResultEntryGroups",
    "UpdateLedgerEntryUpdateLedgerEntryUpdateLedgerEntryResultEntryLines",
    "UpdateLedgerEntryUpdateLedgerEntryUpdateLedgerEntryResultEntryLinesNodes",
    "UpdateLedgerEntryUpdateLedgerEntryUpdateLedgerEntryResultEntryLinesNodesAccount",
    "UpdateLedgerEntryUpdateLedgerEntryUpdateLedgerEntryResultEntryTags",
    "UpdateLedgerInput",
    "UpdateLedgerUpdateLedgerBadRequestError",
    "UpdateLedgerUpdateLedgerInternalError",
    "UpdateLedgerUpdateLedgerUpdateLedgerResult",
    "UpdateLedgerUpdateLedgerUpdateLedgerResultLedger",
    "Upload",
]
