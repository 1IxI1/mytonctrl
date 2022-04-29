#!/usr/bin/env python3
# -*- coding: utf_8 -*-

from mypylib.mypylib import *
from mypyconsole.mypyconsole import *
from mytoncore import *

local = MyPyClass(__file__)
console = MyPyConsole()
ton = MyTonCore()

def Init():
	# Load translate table
	local.InitTranslator(local.buffer.get("myDir") + "translate.json")

	# Create user console
	console.name = "MyTonCtrl"
	console.startFunction = PreUp

	console.AddItem("update", Update, local.Translate("update_cmd"))
	console.AddItem("upgrade", Upgrade, local.Translate("upgrade_cmd"))
	console.AddItem("installer", Installer, local.Translate("installer_cmd"))
	console.AddItem("status", PrintStatus, local.Translate("status_cmd"))
	console.AddItem("seqno", Seqno, local.Translate("seqno_cmd"))
	console.AddItem("getconfig", GetConfig, local.Translate("getconfig_cmd"))

	console.AddItem("nw", CreatNewWallet, local.Translate("nw_cmd"))
	console.AddItem("aw", ActivateWallet, local.Translate("aw_cmd"))
	console.AddItem("wl", PrintWalletsList, local.Translate("wl_cmd"))
	console.AddItem("iw", ImportWallet, local.Translate("iw_cmd"))
	console.AddItem("swv", SetWalletVersion, local.Translate("swv_cmd"))
	console.AddItem("ew", ExportWallet, local.Translate("ex_cmd"))
	console.AddItem("dw", DeleteWallet, local.Translate("dw_cmd"))

	console.AddItem("vas", ViewAccountStatus, local.Translate("vas_cmd"))
	console.AddItem("vah", ViewAccountHistory, local.Translate("vah_cmd"))
	console.AddItem("mg", MoveCoins, local.Translate("mg_cmd"))
	console.AddItem("mgtp", MoveCoinsThroughProxy, local.Translate("mgtp_cmd"))

	console.AddItem("nb", CreatNewBookmark, local.Translate("nb_cmd"))
	console.AddItem("bl", PrintBookmarksList, local.Translate("bl_cmd"))
	console.AddItem("db", DeleteBookmark, local.Translate("db_cmd"))

	# console.AddItem("nr", CreatNewAutoTransferRule, local.Translate("nr_cmd")) # "Добавить правило автопереводов в расписание / Create new auto transfer rule"
	# console.AddItem("rl", PrintAutoTransferRulesList, local.Translate("rl_cmd")) # "Показать правила автопереводов / Show auto transfer rule list"
	# console.AddItem("dr", DeleteAutoTransferRule, local.Translate("dr_cmd")) # "Удалить правило автопереводов из расписания / Delete auto transfer rule"

	console.AddItem("nd", NewDomain, local.Translate("nd_cmd"))
	console.AddItem("dl", PrintDomainsList, local.Translate("dl_cmd"))
	console.AddItem("vds", ViewDomainStatus, local.Translate("vds_cmd"))
	console.AddItem("dd", DeleteDomain, local.Translate("dd_cmd"))

	console.AddItem("ol", PrintOffersList, local.Translate("ol_cmd"))
	console.AddItem("vo", VoteOffer, local.Translate("vo_cmd"))
	console.AddItem("od", OfferDiff, local.Translate("od_cmd"))

	console.AddItem("el", PrintElectionEntriesList, local.Translate("el_cmd"))
	console.AddItem("ve", VoteElectionEntry, local.Translate("ve_cmd"))
	console.AddItem("vl", PrintValidatorList, local.Translate("vl_cmd"))
	console.AddItem("cl", PrintComplaintsList, local.Translate("cl_cmd"))
	console.AddItem("vc", VoteComplaint, local.Translate("vc_cmd"))

	console.AddItem("get", GetSettings, local.Translate("get_cmd"))
	console.AddItem("set", SetSettings, local.Translate("set_cmd"))
	console.AddItem("xrestart", Xrestart, local.Translate("xrestart_cmd"))
	console.AddItem("xlist", Xlist, local.Translate("xlist_cmd"))
	console.AddItem("gpk", GetPubKey, local.Translate("gpk_cmd"))
	console.AddItem("ssoc", SignShardOverlayCert, local.Translate("ssoc_cmd"))
	console.AddItem("isoc", ImportShardOverlayCert, local.Translate("isoc_cmd"))
	
	console.AddItem("new_nomination_controller", NewNominationController, local.Translate("new_controller_cmd"))
	console.AddItem("deposit_to_nomination_controller", DepositToNominationController, local.Translate("deposit_to_controller_cmd"))
	console.AddItem("new_restricted_wallet", NewRestrictedWallet, local.Translate("new_restricted_wallet_cmd"))
	console.AddItem("request_from_nomination_controller", RequestFromNominationController, local.Translate("request_from_nomination_controller_cmd"))
	
	console.AddItem("new_pool", NewPool, local.Translate("new_pool_cmd"))
	console.AddItem("pools_list", PrintPoolsList, local.Translate("pools_list_cmd"))
	console.AddItem("get_pool_data", GetPoolData, local.Translate("get_pool_data_cmd"))
	console.AddItem("activate_pool", ActivatePool, local.Translate("activate_pool_cmd"))
	console.AddItem("deposit_to_pool", DepositToPool, local.Translate("deposit_to_pool_cmd"))
	console.AddItem("withdraw_from_pool", WithdrawFromPool, local.Translate("withdraw_from_pool_cmd"))
	console.AddItem("delete_pool", DeletePool, local.Translate("delete_pool_cmd"))
	console.AddItem("update_validator_set", UpdateValidatorSet, local.Translate("update_validator_set_cmd"))

	# console.AddItem("pt", PrintTest, "PrintTest")
	# console.AddItem("sl", sl, "sl")

	local.db["config"]["logLevel"] = "debug"
	local.db["config"]["isLocaldbSaving"] = True
	local.Run()
#end define

def PreUp():
	CheckMytonctrlUpdate()
	# CheckTonUpdate()
#end define

def Installer(args):
	args = ["python3", "/usr/src/mytonctrl/mytoninstaller.py"]
	subprocess.run(args)
#end define

def SetArgsByArgs(runArgs, args):
	if len(args) == 1:
		buff = args[0]
		if "https://" in buff:
			runArgs += ["-r", buff]
		else:
			runArgs += ["-b", buff]
	elif len(args) == 2:
		runArgs += ["-r", args[0]]
		runArgs += ["-b", args[1]]
	return runArgs
#end define

def Update(args):
	runArgs = ["bash", "/usr/src/mytonctrl/scripts/update.sh"]
	runArgs = SetArgsByArgs(runArgs, args)
	
	exitCode = RunAsRoot(runArgs)
	if exitCode == 0:
		text = "Update - {green}OK{endc}"
	else:
		text = "Update - {red}Error{endc}"
	ColorPrint(text)
	local.Exit()
#end define

def Upgrade(args):
	runArgs = ["bash", "/usr/src/mytonctrl/scripts/upgrade.sh"]
	runArgs = SetArgsByArgs(runArgs, args)
	
	exitCode = RunAsRoot(["python3", "/usr/src/mytonctrl/scripts/upgrade.py"])
	exitCode += RunAsRoot(runArgs)
	if exitCode == 0:
		text = "Upgrade - {green}OK{endc}"
	else:
		text = "Upgrade - {red}Error{endc}"
	ColorPrint(text)
#end define

def CheckMytonctrlUpdate():
	gitPath = local.buffer.get("myDir")
	result = CheckGitUpdate(gitPath)
	if result is True:
		ColorPrint(local.Translate("mytonctrl_update_available"))
#end define

def CheckTonUpdate():
	gitPath = "/usr/src/ton"
	result = CheckGitUpdate(gitPath)
	if result is True:
		ColorPrint(local.Translate("ton_update_available"))
#end define

def PrintTest(args):
	print(json.dumps(local.buffer, indent=2))
#end define

def sl(args):
	Slashing(ton)
#end define

def PrintStatus(args):
	opt = None
	if len(args) == 1:
		opt = args[0]
	adnlAddr = ton.GetAdnlAddr()
	rootWorkchainEnabledTime_int = ton.GetRootWorkchainEnabledTime()
	config34 = ton.GetConfig34()
	config36 = ton.GetConfig36()
	totalValidators = config34["totalValidators"]
	onlineValidators = None
	validatorEfficiency = None
	if opt != "fast":
		onlineValidators = ton.GetOnlineValidators()
		validatorEfficiency = ton.GetValidatorEfficiency()
	if onlineValidators:
		onlineValidators = len(onlineValidators)
	oldStartWorkTime = config36.get("startWorkTime")
	if oldStartWorkTime is None:
		oldStartWorkTime = config34.get("startWorkTime")
	shardsNumber = ton.GetShardsNumber()
	validatorStatus = ton.GetValidatorStatus()
	config15 = ton.GetConfig15()
	config17 = ton.GetConfig17()
	fullConfigAddr = ton.GetFullConfigAddr()
	fullElectorAddr = ton.GetFullElectorAddr()
	startWorkTime = ton.GetActiveElectionId(fullElectorAddr)
	validatorIndex = ton.GetValidatorIndex()
	validatorWallet = ton.GetValidatorWallet()
	dbSize = ton.GetDbSize()
	dbUsage = ton.GetDbUsage()
	memoryInfo = GetMemoryInfo()
	swapInfo = GetSwapInfo()
	offersNumber = ton.GetOffersNumber()
	complaintsNumber = ton.GetComplaintsNumber()
	statistics = ton.GetSettings("statistics")
	tpsAvg = ton.GetStatistics("tpsAvg", statistics)
	netLoadAvg = ton.GetStatistics("netLoadAvg", statistics)
	disksLoadAvg = ton.GetStatistics("disksLoadAvg", statistics)
	disksLoadPercentAvg = ton.GetStatistics("disksLoadPercentAvg", statistics)
	if validatorWallet is not None:
		validatorAccount = ton.GetAccount(validatorWallet.addrB64)
	else:
		validatorAccount = None
	PrintTonStatus(startWorkTime, totalValidators, onlineValidators, shardsNumber, offersNumber, complaintsNumber, tpsAvg)
	PrintLocalStatus(adnlAddr, validatorIndex, validatorEfficiency, validatorWallet, validatorAccount, validatorStatus, dbSize, dbUsage, memoryInfo, swapInfo, netLoadAvg, disksLoadAvg, disksLoadPercentAvg)
	PrintTonConfig(fullConfigAddr, fullElectorAddr, config15, config17)
	PrintTimes(rootWorkchainEnabledTime_int, startWorkTime, oldStartWorkTime, config15)
#end define

def PrintTonStatus(startWorkTime, totalValidators, onlineValidators, shardsNumber, offersNumber, complaintsNumber, tpsAvg):
	tps1 = tpsAvg[0]
	tps5 = tpsAvg[1]
	tps15 = tpsAvg[2]
	allValidators = totalValidators
	newOffers = offersNumber.get("new")
	allOffers = offersNumber.get("all")
	newComplaints = complaintsNumber.get("new")
	allComplaints = complaintsNumber.get("all")
	tps1_text = bcolors.Green(tps1)
	tps5_text = bcolors.Green(tps5)
	tps15_text = bcolors.Green(tps15)
	tps_text = local.Translate("ton_status_tps").format(tps1_text, tps5_text, tps15_text)
	onlineValidators_text = GetColorInt(onlineValidators, border=allValidators*2/3, logic="more")
	allValidators_text = bcolors.Yellow(allValidators)
	validators_text = local.Translate("ton_status_validators").format(onlineValidators_text, allValidators_text)
	shards_text = local.Translate("ton_status_shards").format(bcolors.Green(shardsNumber))
	newOffers_text = bcolors.Green(newOffers)
	allOffers_text = bcolors.Yellow(allOffers)
	offers_text = local.Translate("ton_status_offers").format(newOffers_text, allOffers_text)
	newComplaints_text = bcolors.Green(newComplaints)
	allComplaints_text = bcolors.Yellow(allComplaints)
	complaints_text = local.Translate("ton_status_complaints").format(newComplaints_text, allComplaints_text)

	if startWorkTime == 0:
		election_text = bcolors.Yellow("closed")
	else:
		election_text = bcolors.Green("open")
	election_text = local.Translate("ton_status_election").format(election_text)

	ColorPrint(local.Translate("ton_status_head"))
	print(tps_text)
	print(validators_text)
	print(shards_text)
	print(offers_text)
	print(complaints_text)
	print(election_text)
	print()
#end define

def PrintLocalStatus(adnlAddr, validatorIndex, validatorEfficiency, validatorWallet, validatorAccount, validatorStatus, dbSize, dbUsage, memoryInfo, swapInfo, netLoadAvg, disksLoadAvg, disksLoadPercentAvg):
	if validatorWallet is None:
		return
	walletAddr = validatorWallet.addrB64
	walletBalance = validatorAccount.balance
	cpuNumber = psutil.cpu_count()
	loadavg = GetLoadAvg()
	cpuLoad1 = loadavg[0]
	cpuLoad5 = loadavg[1]
	cpuLoad15 = loadavg[2]
	netLoad1 = netLoadAvg[0]
	netLoad5 = netLoadAvg[1]
	netLoad15 = netLoadAvg[2]
	validatorOutOfSync = validatorStatus.get("outOfSync")
	mytoncoreStatus_bool = GetServiceStatus("mytoncore")
	validatorStatus_bool = GetServiceStatus("validator")

	validatorIndex_text = GetColorInt(validatorIndex, 0, logic="more")
	validatorIndex_text = local.Translate("local_status_validator_index").format(validatorIndex_text)
	validatorEfficiency_text = GetColorInt(validatorEfficiency, 10, logic="more", ending=" %")
	validatorEfficiency_text = local.Translate("local_status_validator_efficiency").format(validatorEfficiency_text)
	adnlAddr_text = local.Translate("local_status_adnl_addr").format(bcolors.Yellow(adnlAddr))
	walletAddr_text = local.Translate("local_status_wallet_addr").format(bcolors.Yellow(walletAddr))
	walletBalance_text = local.Translate("local_status_wallet_balance").format(bcolors.Green(walletBalance))

	# CPU status
	cpuNumber_text = bcolors.Yellow(cpuNumber)
	cpuLoad1_text = GetColorInt(cpuLoad1, cpuNumber, logic="less")
	cpuLoad5_text = GetColorInt(cpuLoad5, cpuNumber, logic="less")
	cpuLoad15_text = GetColorInt(cpuLoad15, cpuNumber, logic="less")
	cpuLoad_text = local.Translate("local_status_cpu_load").format(cpuNumber_text, cpuLoad1_text, cpuLoad5_text, cpuLoad15_text)
	
	# Memory status
	memoryUsage = memoryInfo.get("usage")
	memoryUsagePercent = memoryInfo.get("usagePercent")
	swapUsage = swapInfo.get("usage")
	swapUsagePercent = swapInfo.get("usagePercent")
	memoryUsage_text = GetColorInt(memoryUsage, 100, logic="less", ending=" Gb")
	memoryUsagePercent_text = GetColorInt(memoryUsagePercent, 90, logic="less", ending="%")
	swapUsage_text = GetColorInt(swapUsage, 100, logic="less", ending=" Gb")
	swapUsagePercent_text = GetColorInt(swapUsagePercent, 90, logic="less", ending="%")
	memory_text = local.Translate("local_status_memory_load").format(memoryUsage_text, memoryUsagePercent_text)
	swap_text = local.Translate("local_status_swap_load").format(swapUsage_text, swapUsagePercent_text)

	# Network status
	netLoad1_text = GetColorInt(netLoad1, 300, logic="less")
	netLoad5_text = GetColorInt(netLoad5, 300, logic="less")
	netLoad15_text = GetColorInt(netLoad15, 300, logic="less")
	netLoad_text = local.Translate("local_status_net_load").format(netLoad1_text, netLoad5_text, netLoad15_text)
	
	# Disks status
	disksLoad_data = list()
	for key, item in disksLoadAvg.items():
		diskLoad1_text = bcolors.Green(item[0])
		diskLoad5_text = bcolors.Green(item[1])
		diskLoad15_text = bcolors.Green(item[2])
		diskLoadPercent1_text = GetColorInt(disksLoadPercentAvg[key][0], 80, logic="less", ending="%")
		diskLoadPercent5_text = GetColorInt(disksLoadPercentAvg[key][1], 80, logic="less", ending="%")
		diskLoadPercent15_text = GetColorInt(disksLoadPercentAvg[key][2], 80, logic="less", ending="%")
		buff = "{}, {}"
		buff = "{}{}:[{}{}{}]{}".format(bcolors.cyan, key, bcolors.default, buff, bcolors.cyan, bcolors.endc)
		disksLoad_buff = buff.format(diskLoad15_text, diskLoadPercent15_text)
		disksLoad_data.append(disksLoad_buff)
	disksLoad_data = ", ".join(disksLoad_data)
	disksLoad_text = local.Translate("local_status_disks_load").format(disksLoad_data)

	# Thread status
	mytoncoreStatus_text = local.Translate("local_status_mytoncore_status").format(GetColorStatus(mytoncoreStatus_bool))
	validatorStatus_text = local.Translate("local_status_validator_status").format(GetColorStatus(validatorStatus_bool))
	validatorOutOfSync_text = local.Translate("local_status_validator_out_of_sync").format(GetColorInt(validatorOutOfSync, 20, logic="less", ending=" s"))
	dbSize_text = GetColorInt(dbSize, 1000, logic="less", ending=" Gb")
	dbUsage_text = GetColorInt(dbUsage, 80, logic="less", ending="%")
	dbStatus_text = local.Translate("local_status_db").format(dbSize_text, dbUsage_text, cyan=bcolors.cyan, endc=bcolors.endc)

	ColorPrint(local.Translate("local_status_head"))
	print(validatorIndex_text)
	print(validatorEfficiency_text)
	print(adnlAddr_text)
	print(walletAddr_text)
	print(walletBalance_text)
	print(cpuLoad_text)
	print(netLoad_text)
	print(disksLoad_text)
	print(mytoncoreStatus_text)
	print(validatorStatus_text)
	print(validatorOutOfSync_text)
	print(dbStatus_text)
	print(memory_text)
	print(swap_text)
	print()
#end define

def GetColorInt(data, border, logic, ending=None):
	if data is None:
		result = bcolors.Green("n/a")
	elif logic == "more":
		if data >= border:
			result = bcolors.Green(data, ending)
		else:
			result = bcolors.Red(data, ending)
	elif logic == "less":
		if data <= border:
			result = bcolors.Green(data, ending)
		else:
			result = bcolors.Red(data, ending)
	return result
#end define

def GetColorStatus(input):
	if input == True:
		result = bcolors.Green("working")
	else:
		result = bcolors.Red("not working")
	return result
#end define

def PrintTonConfig(fullConfigAddr, fullElectorAddr, config15, config17):
	validatorsElectedFor = config15["validatorsElectedFor"]
	electionsStartBefore = config15["electionsStartBefore"]
	electionsEndBefore = config15["electionsEndBefore"]
	stakeHeldFor = config15["stakeHeldFor"]
	minStake = config17["minStake"]
	maxStake = config17["maxStake"]

	fullConfigAddr_text = local.Translate("ton_config_configurator_addr").format(bcolors.Yellow(fullConfigAddr))
	fullElectorAddr_text = local.Translate("ton_config_elector_addr").format(bcolors.Yellow(fullElectorAddr))
	validatorsElectedFor_text = bcolors.Yellow(validatorsElectedFor)
	electionsStartBefore_text = bcolors.Yellow(electionsStartBefore)
	electionsEndBefore_text = bcolors.Yellow(electionsEndBefore)
	stakeHeldFor_text = bcolors.Yellow(stakeHeldFor)
	elections_text = local.Translate("ton_config_elections").format(validatorsElectedFor_text, electionsStartBefore_text, electionsEndBefore_text, stakeHeldFor_text)
	minStake_text = bcolors.Yellow(minStake)
	maxStake_text = bcolors.Yellow(maxStake)
	stake_text = local.Translate("ton_config_stake").format(minStake_text, maxStake_text)

	ColorPrint(local.Translate("ton_config_head"))
	print(fullConfigAddr_text)
	print(fullElectorAddr_text)
	print(elections_text)
	print(stake_text)
	print()
#end define

def PrintTimes(rootWorkchainEnabledTime_int, startWorkTime, oldStartWorkTime, config15):
	validatorsElectedFor = config15["validatorsElectedFor"]
	electionsStartBefore = config15["electionsStartBefore"]
	electionsEndBefore = config15["electionsEndBefore"]

	if startWorkTime == 0:
		startWorkTime = oldStartWorkTime
	#end if

	# Calculate time
	startValidation = startWorkTime
	endValidation = startWorkTime + validatorsElectedFor
	startElection = startWorkTime - electionsStartBefore
	endElection = startWorkTime - electionsEndBefore
	startNextElection = startElection + validatorsElectedFor

	# timestamp to datetime
	rootWorkchainEnabledTime = Timestamp2Datetime(rootWorkchainEnabledTime_int)
	startValidationTime = Timestamp2Datetime(startValidation)
	endValidationTime = Timestamp2Datetime(endValidation)
	startElectionTime = Timestamp2Datetime(startElection)
	endElectionTime = Timestamp2Datetime(endElection)
	startNextElectionTime = Timestamp2Datetime(startNextElection)

	# datetime to color text
	rootWorkchainEnabledTime_text = local.Translate("times_root_workchain_enabled_time").format(bcolors.Yellow(rootWorkchainEnabledTime))
	startValidationTime_text = local.Translate("times_start_validation_time").format(GetColorTime(startValidationTime, startValidation))
	endValidationTime_text = local.Translate("times_end_validation_time").format(GetColorTime(endValidationTime, endValidation))
	startElectionTime_text = local.Translate("times_start_election_time").format(GetColorTime(startElectionTime, startElection))
	endElectionTime_text = local.Translate("times_end_election_time").format(GetColorTime(endElectionTime, endElection))
	startNextElectionTime_text = local.Translate("times_start_next_election_time").format(GetColorTime(startNextElectionTime, startNextElection))

	ColorPrint(local.Translate("times_head"))
	print(rootWorkchainEnabledTime_text)
	print(startValidationTime_text)
	print(endValidationTime_text)
	print(startElectionTime_text)
	print(endElectionTime_text)
	print(startNextElectionTime_text)
#end define

def GetColorTime(datetime, timestamp):
	newTimestamp = GetTimestamp()
	if timestamp > newTimestamp:
		result = bcolors.Green(datetime)
	else:
		result = bcolors.Yellow(datetime)
	return result
#end define

def Seqno(args):
	try:
		walletName = args[0]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} seqno <wallet-name>")
		return
	wallet = ton.GetLocalWallet(walletName)
	seqno = ton.GetSeqno(wallet)
	print(walletName, "seqno:", seqno)
#end define

def CreatNewWallet(args):
	version = "v1"
	subwallet = 0
	try:
		if len(args) == 0:
			walletName = ton.GenerateWalletName()
			workchain = 0
		else:
			workchain = args[0]
			walletName = args[1]
		if len(args) > 2:
			version = args[2]
		if len(args) == 4:
			subwallet = args[3]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} nw <workchain-id> <wallet-name> [<version>]")
		return
	wallet = ton.CreateWallet(walletName, workchain, version, subwallet)
	table = list()
	table += [["Name", "Workchain", "Address"]]
	table += [[wallet.name, wallet.workchain, wallet.addrB64_init]]
	PrintTable(table)
#end define

def ActivateWallet(args):
	try:
		walletName = args[0]
	except Exception as err:
		walletName = "all"
	if walletName == "all":
		ton.WalletsCheck()
	else:
		wallet = ton.GetLocalWallet(walletName)
		if not os.path.isfile(wallet.bocFilePath):
			local.AddLog("Wallet {walletName} already activated".format(walletName=walletName), "warning")
			return
		ton.ActivateWallet(wallet)
	ColorPrint("ActivateWallet - {green}OK{endc}")
#end define

def PrintWalletsList(args):
	table = list()
	table += [["Name", "Status", "Balance", "Ver", "Wch", "Address"]]
	data = ton.GetWallets()
	if (data is None or len(data) == 0):
		print("No data")
		return
	for wallet in data:
		account = ton.GetAccount(wallet.addrB64)
		if account.status != "active":
			wallet.addrB64 = wallet.addrB64_init
		table += [[wallet.name, account.status, account.balance, wallet.version, wallet.workchain, wallet.addrB64]]
	PrintTable(table)
#end define

def ImportWalletFromFile(args):
	try:
		filePath = args[0]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} iw <wallet-path>")
		return
	if (".addr" in filePath):
		filePath = filePath.replace(".addr", '')
	if (".pk" in filePath):
		filePath = filePath.replace(".pk", '')
	if os.path.isfile(filePath + ".addr") == False:
		local.AddLog("ImportWalletFromFile error: Address file not found: " + filePath, "error")
		return
	if os.path.isfile(filePath + ".pk") == False:
		local.AddLog("ImportWalletFromFile error: Private key not found: " + filePath, "error")
		return
	if '/' in filePath:
		walletName = filePath[filePath.rfind('/')+1:]
	else:
		walletName = filePath
	copyfile(filePath + ".addr", ton.walletsDir + walletName + ".addr")
	copyfile(filePath + ".pk", ton.walletsDir + walletName + ".pk")
	ColorPrint("ImportWalletFromFile - {green}OK{endc}")
#end define

def ImportWallet(args):
	try:
		addr = args[0]
		key = args[1]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} iw <wallet-addr> <wallet-secret-key>")
		return
	name = ton.ImportWallet(addr, key)
	print("Wallet name:", name)
#end define

def SetWalletVersion(args):
	try:
		addr = args[0]
		version = args[1]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} swv <wallet-addr> <wallet-version>")
		return
	ton.SetWalletVersion(addr, version)
	ColorPrint("SetWalletVersion - {green}OK{endc}")
#end define

def ExportWallet(args):
	try:
		name = args[0]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} ew <wallet-name>")
		return
	addr, key = ton.ExportWallet(name)
	print("Wallet name:", name)
	print("Address:", addr)
	print("Secret key:", key)
#end define

def DeleteWallet(args):
	try:
		walletName = args[0]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} dw <wallet-name>")
		return
	wallet = ton.GetLocalWallet(walletName)
	wallet.Delete()
	ColorPrint("DeleteWallet - {green}OK{endc}")
#end define

def ViewAccountStatus(args):
	try:
		addr = args[0]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} vas <account-addr>")
		return
	addr = ton.GetDestinationAddr(addr)
	account = ton.GetAccount(addr)
	version = ton.GetWalletVersionFromHash(account.codeHash)
	statusTable = list()
	statusTable += [["Address", "Status", "Version", "Balance"]]
	statusTable += [[addr, account.status, version, account.balance]]
	historyTable = GetHistoryTable(addr, 10)
	PrintTable(statusTable)
	print()
	PrintTable(historyTable)
#end define

def ViewAccountHistory(args):
	try:
		addr = args[0]
		limit = int(args[1])
	except:
		ColorPrint("{red}Bad args. Usage:{endc} vah <account-addr> <limit>")
		return
	table = GetHistoryTable(addr, limit)
	PrintTable(table)
#end define

def GetHistoryTable(addr, limit):
	addr = ton.GetDestinationAddr(addr)
	account = ton.GetAccount(addr)
	history = ton.GetAccountHistory(account, limit)
	table = list()
	typeText = ColorText("{red}{bold}{endc}")
	table += [["Time", typeText, "Coins", "From/To"]]
	for message in history:
		if message.srcAddr is None:
			continue
		srcAddrFull = f"{message.srcWorkchain}:{message.srcAddr}"
		destAddFull = f"{message.destWorkchain}:{message.destAddr}"
		if srcAddrFull == account.addrFull:
			type = ColorText("{red}{bold}>>>{endc}")
			fromto = destAddFull
		else:
			type = ColorText("{blue}{bold}<<<{endc}")
			fromto = srcAddrFull
		fromto = ton.AddrFull2AddrB64(fromto)
		#datetime = Timestamp2Datetime(message.time, "%Y.%m.%d %H:%M:%S")
		datetime = timeago(message.time)
		table += [[datetime, type, message.value, fromto]]
	return table
#end define

def MoveCoins(args):
	try:
		walletName = args[0]
		destination = args[1]
		amount = int(args[2])
		if len(args) > 3:
			flags = args[3:]
		else:
			flags = list()
	except:
		ColorPrint("{red}Bad args. Usage:{endc} mg <wallet-name> <account-addr | bookmark-name> <amount>")
		return
	wallet = ton.GetLocalWallet(walletName)
	destination = ton.GetDestinationAddr(destination)
	ton.MoveCoins(wallet, destination, amount, flags=flags)
	ColorPrint("MoveCoins - {green}OK{endc}")
#end define

def MoveCoinsThroughProxy(args):
	try:
		walletName = args[0]
		destination = args[1]
		amount = int(args[2])
	except:
		ColorPrint("{red}Bad args. Usage:{endc} mgtp <wallet-name> <account-addr | bookmark-name> <amount>")
		return
	wallet = ton.GetLocalWallet(walletName)
	destination = ton.GetDestinationAddr(destination)
	ton.MoveCoinsThroughProxy(wallet, destination, amount)
	ColorPrint("MoveCoinsThroughProxy - {green}OK{endc}")
#end define

def CreatNewBookmark(args):
	try:
		name = args[0]
		addr = args[1]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} nb <bookmark-name> <account-addr | domain-name>")
		return
	type = ton.GetStrType(addr)
	bookmark = dict()
	bookmark["name"] = name
	bookmark["type"] = type
	bookmark["addr"] = addr
	ton.AddBookmark(bookmark)
	ColorPrint("CreatNewBookmark - {green}OK{endc}")
#end define

def PrintBookmarksList(args):
	data = ton.GetBookmarks()
	if (data is None or len(data) == 0):
		print("No data")
		return
	table = list()
	table += [["Name", "Type", "Address / Domain", "Balance / Exp. date"]]
	for item in data:
		name = item.get("name")
		type = item.get("type")
		addr = item.get("addr")
		data = item.get("data")
		table += [[name, type, addr, data]]
	PrintTable(table)
#end define

def DeleteBookmark(args):
	try:
		name = args[0]
		type = args[1]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} db <bookmark-name> <bookmark-type>")
		return
	ton.DeleteBookmark(name, type)
	ColorPrint("DeleteBookmark - {green}OK{endc}")
#end define

# def CreatNewAutoTransferRule(args):
# 	try:
# 		name = args[0]
# 		addr = args[1]
# 	except:
# 		ColorPrint("{red}Bad args. Usage:{endc} nr <rule-name> <account-addr | domain-name>")
# 		return
# 	rule = dict()
# 	rule["name"] = name
# 	rule["addr"] = addr
# 	ton.AddAutoTransferRule(rule)
# 	ColorPrint("CreatNewAutoTransferRule - {green}OK{endc}")
# #end define

# def PrintAutoTransferRulesList(args):
# 	data = ton.GetRules()
# 	if (data is None or len(data) == 0):
# 		print("No data")
# 		return
# 	table = list()
# 	table += [["Name", "fix me"]]
# 	for item in data:
# 		table += [[item.get("name"), item.get("fix me")]]
# 	PrintTable(table)
# #end define

# def DeleteAutoTransferRule(args):
# 	print("fix me")
# #end define

def PrintOffersList(args):
	offers = ton.GetOffers()
	if "--json" in args:
		text = json.dumps(offers, indent=2)
		print(text)
	else:
		table = list()
		table += [["Hash", "Votes", "W/L", "Approved", "Is passed"]]
		for item in offers:
			hash = item.get("hash")
			votedValidators = len(item.get("votedValidators"))
			wins = item.get("wins")
			losses = item.get("losses")
			wl = "{0}/{1}".format(wins, losses)
			approvedPercent = item.get("approvedPercent")
			approvedPercent_text = "{0}%".format(approvedPercent)
			isPassed = item.get("isPassed")
			if "hash" not in args:
				hash = Reduct(hash)
			if isPassed == True:
				isPassed = bcolors.Green("true")
			if isPassed == False:
				isPassed = bcolors.Red("false")
			table += [[hash, votedValidators, wl, approvedPercent_text, isPassed]]
		PrintTable(table)
#end define

def VoteOffer(args):
	if len(args) == 0:
		ColorPrint("{red}Bad args. Usage:{endc} vo <offer-hash>")
		return
	for offerHash in args:
		offerHash = int(offerHash)
		ton.VoteOffer(offerHash)
	ColorPrint("VoteOffer - {green}OK{endc}")
#end define

def OfferDiff(args):
	try:
		offerHash = args[0]
		offerHash = int(offerHash)
	except:
		ColorPrint("{red}Bad args. Usage:{endc} od <offer-hash>")
		return
	ton.GetOfferDiff(offerHash)
#end define

def GetConfig(args):
	try:
		configId = args[0]
		configId = int(configId)
	except:
		ColorPrint("{red}Bad args. Usage:{endc} gc <config-id>")
		return
	data = ton.GetConfig(configId)
	text = json.dumps(data, indent=2)
	print(text)
#end define

def PrintComplaintsList(args):
	past = "past" in args
	complaints = ton.GetComplaints(past=past)
	if "--json" in args:
		text = json.dumps(complaints, indent=2)
		print(text)
	else:
		table = list()
		table += [["Election id", "ADNL", "Fine (part)", "Votes", "Approved", "Is passed"]]
		for key, item in complaints.items():
			electionId = item.get("electionId")
			adnl = item.get("adnl")
			suggestedFine = item.get("suggestedFine")
			suggestedFinePart = item.get("suggestedFinePart")
			Fine_text = "{0} ({1})".format(suggestedFine, suggestedFinePart)
			votedValidators = len(item.get("votedValidators"))
			approvedPercent = item.get("approvedPercent")
			approvedPercent_text = "{0}%".format(approvedPercent)
			isPassed = item.get("isPassed")
			if "adnl" not in args:
				adnl = Reduct(adnl)
			if isPassed == True:
				isPassed = bcolors.Green("true")
			if isPassed == False:
				isPassed = bcolors.Red("false")
			table += [[electionId, adnl, Fine_text, votedValidators, approvedPercent_text, isPassed]]
		PrintTable(table)
#end define

def VoteComplaint(args):
	try:
		electionId = args[0]
		complaintHash = args[1]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} vc <election-id> <complaint-hash>")
		return
	ton.VoteComplaint(electionId, complaintHash)
	ColorPrint("VoteComplaint - {green}OK{endc}")
#end define

def NewDomain(args):
	try:
		domainName = args[0]
		walletName = args[1]
		adnlAddr = args[2]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} nd <domain-name> <wallet-name> <site-adnl-addr>")
		return
	domain = dict()
	domain["name"] = domainName
	domain["adnlAddr"] = adnlAddr
	domain["walletName"] = walletName
	ton.NewDomain(domain)
	ColorPrint("NewDomain - {green}OK{endc}")
#end define

def PrintDomainsList(args):
	data = ton.GetDomains()
	if (data is None or len(data) == 0):
		print("No data")
		return
	table = list()
	table += [["Domain", "Wallet", "Expiration date", "ADNL address"]]
	for item in data:
		domainName = item.get("name")
		walletName = item.get("walletName")
		endTime = item.get("endTime")
		endTime = Timestamp2Datetime(endTime, "%d.%m.%Y")
		adnlAddr = item.get("adnlAddr")
		table += [[domainName, walletName, endTime, adnlAddr]]
	PrintTable(table)
#end define

def ViewDomainStatus(args):
	try:
		domainName = args[0]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} vds <domain-name>")
		return
	domain = ton.GetDomain(domainName)
	endTime = domain.get("endTime")
	endTime = Timestamp2Datetime(endTime, "%d.%m.%Y")
	adnlAddr = domain.get("adnlAddr")
	table = list()
	table += [["Domain", "Expiration date", "ADNL address"]]
	table += [[domainName, endTime, adnlAddr]]
	PrintTable(table)
#end define

def DeleteDomain(args):
	try:
		domainName = args[0]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} dd <domain-name>")
		return
	ton.DeleteDomain(domainName)
	ColorPrint("DeleteDomain - {green}OK{endc}")
#end define

def PrintElectionEntriesList(args):
	past = "past" in args
	entries = ton.GetElectionEntries(past=past)
	if "--json" in args:
		text = json.dumps(entries, indent=2)
		print(text)
	else:
		table = list()
		table += [["ADNL", "Pubkey", "Wallet", "Stake", "Max-factor"]]
		for key, item in entries.items():
			adnl = item.get("adnlAddr")
			pubkey = item.get("pubkey")
			walletAddr = item.get("walletAddr")
			stake = item.get("stake")
			maxFactor = item.get("maxFactor")
			if "adnl" not in args:
				adnl = Reduct(adnl)
			if "pubkey" not in args:
				pubkey = Reduct(pubkey)
			if "wallet" not in args:
				walletAddr = Reduct(walletAddr)
			table += [[adnl, pubkey, walletAddr, stake, maxFactor]]
		PrintTable(table)
#end define

def VoteElectionEntry(args):
	Elections(ton)
	ColorPrint("VoteElectionEntry - {green}OK{endc}")
#end define

def PrintValidatorList(args):
	past = "past" in args
	validators = ton.GetValidatorsList(past=past)
	if "--json" in args:
		text = json.dumps(validators, indent=2)
		print(text)
	else:
		table = list()
		table += [["ADNL", "Pubkey", "Wallet", "Efficiency", "Online"]]
		for item in validators:
			adnl = item.get("adnlAddr")
			pubkey = item.get("pubkey")
			walletAddr = item.get("walletAddr")
			efficiency = item.get("efficiency")
			online = item.get("online")
			if "adnl" not in args:
				adnl = Reduct(adnl)
			if "pubkey" not in args:
				pubkey = Reduct(pubkey)
			if "wallet" not in args:
				walletAddr = Reduct(walletAddr)
			if "offline" in args and online != False:
				continue
			if online == True:
				online = bcolors.Green("true")
			if online == False:
				online = bcolors.Red("false")
			table += [[adnl, pubkey, walletAddr, efficiency, online]]
		PrintTable(table)
#end define

def Reduct(item):
	item = str(item)
	if item is None:
		result = None
	else:
		end = len(item)
		result = item[0:6] + "..." + item[end-6:end]
	return result
#end define

def GetSettings(args):
	try:
		name = args[0]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} get <settings-name>")
		return
	result = ton.GetSettings(name)
	print(json.dumps(result, indent=2))
#end define

def SetSettings(args):
	try:
		name = args[0]
		value = args[1]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} set <settings-name> <settings-value>")
		return
	result = ton.SetSettings(name, value)
	ColorPrint("SetSettings - {green}OK{endc}")
#end define

def Xrestart(inputArgs):
	if len(inputArgs) < 2:
		ColorPrint("{red}Bad args. Usage:{endc} xrestart <timestamp> <args>")
		return
	args = ["python3", "/usr/src/mytonctrl/scripts/xrestart.py"]
	args += inputArgs
	exitCode = RunAsRoot(args)
	if exitCode == 0:
		text = "Xrestart - {green}OK{endc}"
	else:
		text = "Xrestart - {red}Error{endc}"
	ColorPrint(text)
#end define

def Xlist(args):
	ColorPrint("Xlist - {green}OK{endc}")
#end define

def GetPubKey(args):
	adnlAddr = ton.GetAdnlAddr()
	pubkey = ton.GetPubKey(adnlAddr)
	print("pubkey:", pubkey)
#end define

def SignShardOverlayCert(args):
	try:
		adnl = args[0]
		pubkey = args[0]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} ssoc <pubkey>")
		return
	ton.SignShardOverlayCert(adnl, pubkey)
#end define

def ImportShardOverlayCert(args):
	ton.ImportShardOverlayCert()
#end define

def NewNominationController(args):
	try:
		name = args[0]
		nominatorAddr = args[1]
		rewardShare = args[2]
		coverAbility = args[3]
		workchain = -1
		subwallet = 0
	except:
		ColorPrint("{red}Bad args. Usage:{endc} new_controller <controller-name> <nominator-addr> <reward-share> <cover-ability>")
		return
	ton.CreateNominationController(name, nominatorAddr, workchain, subwallet, rewardShare, coverAbility)
	ColorPrint("NewNominationController - {green}OK{endc}")
#end define

def DepositToNominationController(args):
	try:
		walletName = args[0]
		destination = args[1]
		amount = args[2]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} add_to_nomination_controller <wallet-name> <controller-addr> <amount>")
		return
	destination = ton.GetDestinationAddr(destination)
	ton.DepositToNominationController(walletName, destination, amount)
	ColorPrint("DepositToNominationController - {green}OK{endc}")
#end define

def RequestFromNominationController(args):
	try:
		walletName = args[0]
		destination = args[1]
		amount = args[2]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} request_from_nomination_controller <wallet-name> <controller-addr> <amount>")
		return
	destination = ton.GetDestinationAddr(destination)
	ton.RequestFromNominationController(walletName, destination, amount)
	ColorPrint("RequestFromNominationController - {green}OK{endc}")
#end define

def NewRestrictedWallet(args):
	try:
		workchain = args[0]
		name = args[1]
		ownerAddr = args[2]
		subwallet = 0
	except:
		ColorPrint("{red}Bad args. Usage:{endc} new_restricted_wallet <workchain-id> <wallet-name> <owner-addr>")
		return
	ton.CreateRestrictedWallet(name, ownerAddr, workchain, subwallet)
	ColorPrint("NewRestrictedWallet - {green}OK{endc}")
#end define

def NewPool(args):
	try:
		poolName = args[0]
		if len(args) == 1:
			validatorRewardShare = 4000
			maxNominatorsCount = 10
			minValidatorStake = 100
			minNominatorStake = 100
		else:
			validatorRewardShare = args[1]
			maxNominatorsCount = args[2]
			minValidatorStake = args[3]
			minNominatorStake = args[4]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} new_pool <pool-name> [<validator-reward-share> <max-nominators-count> <min-validator-stake> <min-nominator-stake>]")
		return
	ton.CreatePool(poolName, validatorRewardShare, maxNominatorsCount, minValidatorStake, minNominatorStake)
	ColorPrint("NewPool - {green}OK{endc}")
#end define

def ActivatePool(args):
	try:
		poolName = args[0]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} activate_pool <pool-name>")
		return
	pool = ton.GetLocalPool(poolName)
	if not os.path.isfile(pool.bocFilePath):
		local.AddLog(f"Pool {poolName} already activated", "warning")
		return
	ton.ActivatePool(pool)
	ColorPrint("ActivatePool - {green}OK{endc}")
#end define

def PrintPoolsList(args):
	table = list()
	table += [["Name", "Status", "Balance", "Address"]]
	data = ton.GetPools()
	if (data is None or len(data) == 0):
		print("No data")
		return
	for pool in data:
		account = ton.GetAccount(pool.addrB64)
		if account.status != "active":
			pool.addrB64 = pool.addrB64_init
		table += [[pool.name, account.status, account.balance, pool.addrB64]]
	PrintTable(table)
#end define

def GetPoolData(args):
	try:
		poolName = args[0]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} get_pool_data <pool-name | pool-addr>")
		return
	if ton.IsAddr(poolName):
		poolAddr = poolName
	else:
		pool = ton.GetLocalPool(poolName)
		poolAddr = pool.addrB64
	poolData = ton.GetPoolData(poolAddr)
	print(json.dumps(poolData, indent=4))
#end define

def DepositToPool(args):
	try:
		walletName = args[0]
		pollAddr = args[1]
		amount = int(args[2])
	except:
		ColorPrint("{red}Bad args. Usage:{endc} deposit_to_pool <wallet-name> <pool-addr> <amount>")
		return
	ton.DepositToPool(walletName, pollAddr, amount)
	ColorPrint("DepositToPool - {green}OK{endc}")
#end define

def WithdrawFromPool(args):
	try:
		walletName = args[0]
		poolAddr = args[1]
		amount = args[2]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} withdraw_from_pool <wallet-name> <pool-addr> <amount>")
		return
	poolAddr = ton.GetDestinationAddr(poolAddr)
	ton.WithdrawFromPool(walletName, poolAddr, amount)
	ColorPrint("WithdrawFromPool - {green}OK{endc}")
#end define

def DeletePool(args):
	try:
		poolName = args[0]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} delete_pool <pool-name>")
		return
	pool = ton.GetLocalPool(poolName)
	pool.Delete()
	ColorPrint("DeletePool - {green}OK{endc}")
#end define

def UpdateValidatorSet(args):
	try:
		poolAddr = args[0]
	except:
		ColorPrint("{red}Bad args. Usage:{endc} update_validator_set <pool-addr>")
		return
	wallet = self.GetValidatorWallet()
	self.PoolUpdateValidatorSet(poolAddr, wallet)
	ColorPrint("DeletePool - {green}OK{endc}")
#end define


###
### Start of the program
###

if __name__ == "__main__":
	Init()
	console.Run()
#end if
