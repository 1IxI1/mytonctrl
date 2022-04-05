#!/usr/bin/env python3
# -*- coding: utf_8 -*-l

import crc16
import struct
import random
import hashlib
import requests
from mypylib.mypylib import *

local = MyPyClass(__file__)

class LiteClient:
	def __init__(self):
		self.appPath = None
		self.configPath = None
		self.pubkeyPath = None
		self.addr = None
		self.ton = None # magic
	#end define

	def Run(self, cmd, **kwargs):
		index = kwargs.get("index")
		timeout = kwargs.get("timeout", 3)
		useLocalLiteServer = kwargs.get("useLocalLiteServer", True)
		validatorStatus = self.ton.GetValidatorStatus()
		validatorOutOfSync = validatorStatus.get("outOfSync")
		args = [self.appPath, "--global-config", self.configPath, "--verbosity", "0", "--cmd", cmd]
		if index is not None:
			index = str(index)
			args += ["-i", index]
		elif useLocalLiteServer and self.pubkeyPath and validatorOutOfSync < 20:
			args = [self.appPath, "--addr", self.addr, "--pub", self.pubkeyPath, "--verbosity", "0", "--cmd", cmd]
		else:
			liteServers = local.db.get("liteServers")
			if liteServers is not None:
				index = random.choice(liteServers)
				index = str(index)
				args += ["-i", index]
		#end if

		process = subprocess.run(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
		output = process.stdout.decode("utf-8")
		err = process.stderr.decode("utf-8")
		if len(err) > 0:
			local.AddLog("args: {args}".format(args=args), "error")
			raise Exception("LiteClient error: {err}".format(err=err))
		return output
	#end define
#end class

class ValidatorConsole:
	def __init__(self):
		self.appPath = None
		self.privKeyPath = None
		self.pubKeyPath = None
		self.addr = None
	#end define

	def Run(self, cmd, **kwargs):
		timeout = kwargs.get("timeout", 3)
		if self.appPath is None or self.privKeyPath is None or self.pubKeyPath is None:
			raise Exception("ValidatorConsole error: Validator console is not settings")
		args = [self.appPath, "-k", self.privKeyPath, "-p", self.pubKeyPath, "-a", self.addr, "-v", "0", "--cmd", cmd]
		process = subprocess.run(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
		output = process.stdout.decode("utf-8")
		err = process.stderr.decode("utf-8")
		if len(err) > 0:
			local.AddLog("args: {args}".format(args=args), "error")
			raise Exception("ValidatorConsole error: {err}".format(err=err))
		return output
	#end define
#end class

class Fift:
	def __init__(self):
		self.appPath = None
		self.libsPath = None
		self.smartcontsPath = None
	#end define

	def Run(self, args, **kwargs):
		timeout = kwargs.get("timeout", 3)
		for i in range(len(args)):
			args[i] = str(args[i])
		includePath = self.libsPath + ':' + self.smartcontsPath
		args = [self.appPath, "-I", includePath, "-s"] + args
		process = subprocess.run(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
		output = process.stdout.decode("utf-8")
		err = process.stderr.decode("utf-8")
		if len(err) > 0:
			local.AddLog("args: {args}".format(args=args), "error")
			raise Exception("Fift error: {err}".format(err=err))
		return output
	#end define
#end class

class Miner:
	def __init__(self):
		self.appPath = None
	#end define

	def Run(self, args):
		for i in range(len(args)):
			args[i] = str(args[i])
		args = [self.appPath] + args
		process = subprocess.run(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		output = process.stdout.decode("utf-8")
		err = process.stderr.decode("utf-8")
		# if len(err) > 0:
		# 	local.AddLog("args: {args}".format(args=args), "error")
		# 	raise Exception("Miner error: {err}".format(err=err))
		return err
	#end define
#end class

class Wallet:
	def __init__(self):
		self.name = None
		self.path = None
		self.addrFilePath = None
		self.privFilePath = None
		self.bocFilePath = None
		self.fullAddr = None
		self.workchain = None
		self.addr_hex = None
		self.addr = None
		self.addr_init = None
		self.oldseqno = None
		self.account = None
		self.subwallet = None
		self.version = None
	#end define

	def Refresh(self):
		buff = self.fullAddr.split(':')
		self.workchain = buff[0]
		self.addr_hex = buff[1]
		self.privFilePath = self.path + ".pk"
		if self.version and "h" in self.version:
			self.addrFilePath = self.path + str(self.subwallet) + ".addr"
			self.bocFilePath = self.path + str(self.subwallet) + "-query.boc"
		else:
			self.addrFilePath = self.path + ".addr"
			self.bocFilePath = self.path + "-query.boc"
	#end define

	def Delete(self):
		os.remove(self.addrFilePath)
		os.remove(self.privFilePath)
	#end define
#end class

class Account:
	def __init__(self):
		self.addr = None
		self.addrHex = None
		self.status = "empty"
		self.balance = 0
		self.lt = None
		self.hash = None
		self.codeHash = None
	#end define
#end class

class Domain(dict):
	def __init__(self):
		self["name"] = None
		self["adnlAddr"] = None
		self["walletName"] = None
	#end define
#end class

class Block():
	def __init__(self, str):
		self.workchain = None
		self.shardchain = None
		self.seqno = None
		self.rootHash = None
		self.fileHash = None
		self.ParsBlock(str)
	#end define
	
	def ParsBlock(self, str):
		buff = str.split(':')
		self.rootHash = buff[1]
		self.fileHash = buff[2]
		buff = buff[0]
		buff = buff.replace('(', '')
		buff = buff.replace(')', '')
		buff = buff.split(',')
		self.workchain = int(buff[0])
		self.shardchain = buff[1]
		self.seqno = int(buff[2])
	#end define
	
	def __str__ (self):
		result = f"({self.workchain},{self.shardchain},{self.seqno}):{self.rootHash}:{self.fileHash}"
		return result
	#end define
	
	def __repr__ (self):
		result = f"({self.workchain},{self.shardchain},{self.seqno}):{self.rootHash}:{self.fileHash}"
		return result
	#end define
	
	def __eq__(self, other):
		if other is None:
			return False
		return self.rootHash == other.rootHash and self.fileHash == other.fileHash
	#end define
#end class

class Trans():
	def __init__(self, block, id, addrHex, lt, hash):
		self.block = block
		self.id = id
		self.addrHex = addrHex
		self.lt = lt
		self.hash = hash
	#end define
	
	def __str__ (self):
		return str(self.__dict__)
	#end define
	
	def __repr__ (self):
		return str(self.__dict__)
	#end define
	
	def __eq__(self, other):
		if other is None:
			return False
		return self.hash == other.hash
	#end define
#end class

class Message():
	def __init__(self):
		self.block = None
		self.type = None
		self.time = None
		self.src = None
		self.dest = None
		self.value = None
		self.body = None
		self.comment = None
		self.ihr_fee = None
		self.fwd_fee = None
		self.total_fees = None
		self.ihr_disabled = None
	#end define
	
	def __str__ (self):
		return str(self.__dict__)
	#end define
	
	def __repr__ (self):
		return str(self.__dict__)
	#end define
	
	def __eq__(self, other):
		if other is None:
			return False
		return self.hash == other.hash
	#end define
#end class

class MyTonCore():
	def __init__(self):
		self.walletsDir = None
		self.contractsDir = None
		self.tempDir = None

		self.liteClient = LiteClient()
		self.validatorConsole = ValidatorConsole()
		self.fift = Fift()
		self.miner = Miner()

		self.Refresh()
		self.Init()
	#end define

	def Init(self):
		# Check all directorys
		os.makedirs(self.walletsDir, exist_ok=True)
		os.makedirs(self.contractsDir, exist_ok=True)
	#end define

	def Refresh(self):
		local.dbLoad()
		self.walletsDir = local.buffer.get("myWorkDir") + "wallets/"
		self.contractsDir = local.buffer.get("myWorkDir") + "contracts/"
		self.tempDir = local.buffer.get("myTempDir")

		liteClient = local.db.get("liteClient")
		if liteClient is not None:
			self.liteClient.ton = self # magic
			self.liteClient.appPath = liteClient["appPath"]
			self.liteClient.configPath = liteClient["configPath"]
			liteServer = liteClient.get("liteServer")
			if liteServer is not None:
				self.liteClient.pubkeyPath = liteServer["pubkeyPath"]
				self.liteClient.addr = "{0}:{1}".format(liteServer["ip"], liteServer["port"])
		#end if

		validatorConsole = local.db.get("validatorConsole")
		if validatorConsole is not None:
			self.validatorConsole.appPath = validatorConsole["appPath"]
			self.validatorConsole.privKeyPath = validatorConsole["privKeyPath"]
			self.validatorConsole.pubKeyPath = validatorConsole["pubKeyPath"]
			self.validatorConsole.addr = validatorConsole["addr"]
		#end if

		fift = local.db.get("fift")
		if fift is not None:
			self.fift.appPath = fift["appPath"]
			self.fift.libsPath = fift["libsPath"]
			self.fift.smartcontsPath = fift["smartcontsPath"]
		#end if

		miner = local.db.get("miner")
		if miner is not None:
			self.miner.appPath = miner["appPath"]
			# set powAddr "kf8guqdIbY6kpMykR8WFeVGbZcP2iuBagXfnQuq0rGrxgE04"
			# set minerAddr "kQAXRfNYUkFtecUg91zvbUkpy897CDcE2okhFxAlOLcM3_XD"
		#end if

		# Check config file
		self.CheckConfigFile(fift, liteClient)
	#end define

	def CheckConfigFile(self, fift, liteClient):
		mconfigPath = local.buffer.get("localdbFileName")
		backupPath = mconfigPath + ".backup"
		if fift is None or liteClient is None:
			local.AddLog("The config file is broken", "warning")
			if os.path.isfile(backupPath):
				local.AddLog("Restoring the configuration file", "info")
				args = ["cp", backupPath, mconfigPath]
				subprocess.run(args)
				self.Refresh()
		elif os.path.isfile(backupPath) == False:
			local.AddLog("Create backup config file", "info")
			args = ["cp", mconfigPath, backupPath]
			subprocess.run(args)
	#end define

	def GetVarFromWorkerOutput(self, text, search):
		if ':' not in search:
			search += ':'
		if search is None or text is None:
			return None
		if search not in text:
			return None
		start = text.find(search) + len(search)
		count = 0
		bcount = 0
		textLen = len(text)
		end = textLen
		for i in range(start, textLen):
			letter = text[i]
			if letter == '(':
				count += 1
				bcount += 1
			elif letter == ')':
				count -= 1
			if letter == ')' and count < 1:
				end = i + 1
				break
			elif letter == '\n' and count < 1:
				end = i
				break
		result = text[start:end]
		if count != 0 and bcount == 0:
			result = result.replace(')', '')
		return result
	#end define

	def GetSeqno(self, wallet):
		local.AddLog("start GetSeqno function", "debug")
		cmd = "runmethod {addr} seqno".format(addr=wallet.addr)
		result = self.liteClient.Run(cmd)
		if "cannot run any methods" in result:
			return None
		if "result" not in result:
			return 0
		seqno = self.GetVarFromWorkerOutput(result, "result")
		seqno = seqno.replace(' ', '')
		seqno = Pars(seqno, '[', ']')
		seqno = int(seqno)
		return seqno
	#end define

	def GetAccount(self, addr):
		local.AddLog("start GetAccount function", "debug")
		account = Account()
		cmd = "getaccount {addr}".format(addr=addr)
		result = self.liteClient.Run(cmd)
		storage = self.GetVarFromWorkerOutput(result, "storage")
		if storage is None:
			return account
		addr = self.GetVarFromWorkerOutput(result, "addr")
		workchain = self.GetVar(addr, "workchain_id")
		address = self.GetVar(addr, "address")
		addrHex = "{}:{}".format(workchain, xhex2hex(address))
		balance = self.GetVarFromWorkerOutput(storage, "balance")
		grams = self.GetVarFromWorkerOutput(balance, "grams")
		value = self.GetVarFromWorkerOutput(grams, "value")
		state = self.GetVarFromWorkerOutput(storage, "state")
		code_buff = self.GetVarFromWorkerOutput(state, "code")
		data_buff = self.GetVarFromWorkerOutput(state, "data")
		code = self.GetVarFromWorkerOutput(code_buff, "value")
		data = self.GetVarFromWorkerOutput(data_buff, "value")
		code = self.GetBody(code)
		data = self.GetBody(data)
		codeHash = self.GetCodeHash(code)
		status = Pars(state, "account_", '\n')
		account.addr = self.HexAddr2Base64Addr(addrHex)
		account.addrHex = addrHex
		account.status = status
		account.balance = ng2g(value)
		account.lt = Pars(result, "lt = ", ' ')
		account.hash = Pars(result, "hash = ", '\n')
		account.codeHash = codeHash
		return account
	#end define
	
	def GetCodeHash(self, code):
		if code is None:
			return
		codeBytes = bytes.fromhex(code)
		codeHash = hashlib.sha256(codeBytes).hexdigest()
		return codeHash
	#end define

	def GetAccountHistory_old(self, account, limit):
		local.AddLog("start GetAccountHistory_old function", "debug")
		lt=account.lt
		hash=account.hash
		history = list()
		ready = 0
		while True:
			cmd = "lasttrans {addr} {lt} {hash}".format(addr=account.addr, lt=lt, hash=hash)
			result = self.liteClient.Run(cmd)
			buff =  Pars(result, "previous transaction has", '\n')
			lt = Pars(buff, "lt ", ' ')
			hash = Pars(buff, "hash ", ' ')
			arr = result.split("transaction #0")
			for item in arr:
				ready += 1
				if "from block" not in item:
					continue
				if "VALUE:" not in item:
					continue
				block = Pars(item, "from block ", '\n')
				time = Pars(item, "time=", ' ')
				time = int(time)
				outmsg = Pars(item, "outmsg_cnt=", '\n')
				outmsg = int(outmsg)
				if outmsg == 1:
					item = Pars(item, "outbound message")
				buff = dict()
				buff["block"] = block
				buff["time"] = time
				buff["outmsg"] = outmsg
				buff["from"] = Pars(item, "FROM: ", ' ').lower()
				buff["to"] = Pars(item, "TO: ", ' ').lower()
				value = Pars(item, "VALUE:", '\n')
				if '+' in value: # wtf?
					value = value[:value.find('+')] # wtf? `-1:0000000000000000000000000000000000000000000000000000000000000000 1583059577 1200000000+extra`
				buff["value"] = ng2g(value)
				history.append(buff)
			if lt is None or ready >= limit:
				return history
	#end define
	
	def GetAccountHistory_old2(self, account, limit):
		local.AddLog("start GetAccountHistory_old2 function", "debug")
		lt=account.lt
		hash=account.hash
		history = list()
		ready = 0
		while True:
			cmd = "lasttransdump {addr} {lt} {hash}".format(addr=account.addr, lt=lt, hash=hash)
			result = self.liteClient.Run(cmd)
			buff =  Pars(result, "previous transaction has", '\n')
			lt = Pars(buff, "lt ", ' ')
			hash = Pars(buff, "hash ", ' ')
			arr = result.split("transaction #")
			for item in arr:
				ready += 1
				if "from block" not in item:
					continue
				if "VALUE:" not in item:
					continue
				block = Pars(item, "from block ", ' ')
				time = Pars(item, "time=", ' ')
				time = int(time)
				outmsg = Pars(item, "outmsg_cnt=", '\n')
				outmsg = int(outmsg)
				if outmsg == 1:
					item = Pars(item, "outbound message")
				#end if
				
				in_msg = self.GetVarFromWorkerOutput(result, "in_msg")
				ihr_disabled = Pars(in_msg, "ihr_disabled:", ' ')
				bounce = Pars(in_msg, "bounce:", ' ')
				bounced = Pars(in_msg, "bounced:", '\n')
				src_buff = self.GetVarFromWorkerOutput(in_msg, "src")
				src_buff2 = self.GetVarFromWorkerOutput(src_buff, "address")
				src = xhex2hex(src_buff2)
				dest_buff = self.GetVarFromWorkerOutput(in_msg, "dest")
				dest_buff2 = self.GetVarFromWorkerOutput(dest_buff, "address")
				dest = xhex2hex(dest_buff2)
				value_buff = self.GetVarFromWorkerOutput(in_msg, "value")
				grams_buff = self.GetVarFromWorkerOutput(value_buff, "grams")
				ngrams = self.GetVarFromWorkerOutput(grams_buff, "value")
				if ngrams is None:
					grams = None
				else:
					grams = ng2g(ngrams)
				ihr_fee_buff = self.GetVarFromWorkerOutput(in_msg, "ihr_fee")
				ihr_fee = self.GetVarFromWorkerOutput(ihr_fee_buff, "value")
				fwd_fee_buff = self.GetVarFromWorkerOutput(in_msg, "fwd_fee")
				fwd_fee = self.GetVarFromWorkerOutput(fwd_fee_buff, "value")
				body_buff = self.GetVarFromWorkerOutput(in_msg, "body")
				body_buff2 = self.GetVarFromWorkerOutput(body_buff, "value")
				body = self.GetBody(body_buff2)
				comment = self.GetComment(body)

				total_fees_buff = self.GetVarFromWorkerOutput(result, "total_fees")
				total_fees = self.GetVarFromWorkerOutput(total_fees_buff, "value")
				storage_ph_buff = self.GetVarFromWorkerOutput(result, "storage_ph")
				storage_ph_buff2 = self.GetVarFromWorkerOutput(storage_ph_buff, "value")
				storage_ph = self.GetVarFromWorkerOutput(storage_ph_buff2, "value")
				credit_ph_buff = self.GetVarFromWorkerOutput(result, "credit_ph")
				credit_ph_buff2 = self.GetVarFromWorkerOutput(credit_ph_buff, "value")
				credit_ph = self.GetVarFromWorkerOutput(credit_ph_buff2, "value")
				compute_ph = self.GetVarFromWorkerOutput(result, "compute_ph")
				gas_fees_buff = self.GetVarFromWorkerOutput(compute_ph, "gas_fees")
				gas_fees = self.GetVarFromWorkerOutput(gas_fees_buff, "value")
				gas_used_buff = self.GetVarFromWorkerOutput(compute_ph, "gas_used")
				gas_used = self.GetVarFromWorkerOutput(gas_used_buff, "value")
				gas_limit_buff = self.GetVarFromWorkerOutput(compute_ph, "gas_limit")
				gas_limit = self.GetVarFromWorkerOutput(gas_limit_buff, "value")
				vm_init_state_hash_buff = Pars(result, "vm_init_state_hash:", ' ')
				vm_init_state_hash = xhex2hex(vm_init_state_hash_buff)
				vm_final_state_hash_buff = Pars(result, "vm_final_state_hash:", ')')
				vm_final_state_hash = xhex2hex(vm_final_state_hash_buff)
				action_list_hash_buff = Pars(result, "action_list_hash:", '\n')
				action_list_hash = xhex2hex(action_list_hash_buff)
				output = dict()
				output["block"] = block
				output["time"] = time
				output["outmsg"] = outmsg
				output["from"] = Pars(item, "FROM: ", ' ').lower()
				output["to"] = Pars(item, "TO: ", ' ').lower()
				output["ihr_disabled"] = ihr_disabled
				output["bounce"] = bounce
				output["bounced"] = bounced
				output["src"] = src
				output["dest"] = dest
				output["grams"] = grams
				output["body"] = body
				output["comment"] = comment
				output["ihr_fee"] = ihr_fee
				output["fwd_fee"] = fwd_fee
				output["total_fees"] = total_fees
				output["storage_ph"] = storage_ph
				output["credit_ph"] = credit_ph
				output["gas_used"] = gas_used
				output["vm_init_state_hash"] = vm_init_state_hash
				output["vm_final_state_hash"] = vm_final_state_hash
				output["action_list_hash"] = action_list_hash
				value = Pars(item, "VALUE:", '\n')
				output["value"] = ng2g(value)
				history.append(output)
			if lt is None or ready >= limit:
				return history
	#end define
	
	def GetAccountHistory(self, account, limit):
		local.AddLog("start GetAccountHistory function", "debug")
		lt = account.lt
		hash = account.hash
		history = list()
		while True:
			data, lt, hash = self.LastTransDump(account.addr, lt, hash)
			history += data
			if lt is None or len(history) >= limit:
				return history
	#end define
	
	def LastTransDump(self, addr, lt, hash, count=10):
		history = list()
		cmd = f"lasttransdump {addr} {lt} {hash} {count}"
		result = self.liteClient.Run(cmd)
		data = self.Result2Dict(result)
		prevTrans = self.GetKeyFromDict(data, "previous transaction")
		prevTransLt = self.GetVar(prevTrans, "lt")
		prevTransHash = self.GetVar(prevTrans, "hash")
		for key, item in data.items():
			if "transaction #" not in key:
				continue
			block_str = Pars(key, "from block ", ' ')
			description = self.GetKeyFromDict(item, "description")
			type = self.GetVar(description, "trans_")
			time = self.GetVarFromDict(item, "time")
			#outmsg = self.GetVarFromDict(item, "outmsg_cnt")
			total_fees = self.GetVarFromDict(item, "total_fees.grams.value")
			messages = self.GetMessagesFromTransaction(item)
			transData = dict()
			transData["type"] = type
			transData["block"] = Block(block_str)
			transData["time"] = time
			#transData["outmsg"] = outmsg
			transData["total_fees"] = total_fees
			history += self.ParsMessages(messages, transData)
		return history, prevTransLt, prevTransHash
	#end define
	
	def ParsMessages(self, messages, transData):
		history = list()
		#for item in messages:
		for data in messages:
			src = None
			dest = None
			ihr_disabled = self.GetVarFromDict(data, "message.ihr_disabled")
			bounce = self.GetVarFromDict(data, "message.bounce")
			bounced = self.GetVarFromDict(data, "message.bounced")
			
			workchain = self.GetVarFromDict(data, "message.info.src.workchain_id")
			address = self.GetVarFromDict(data, "message.info.src.address")
			if address:
				src = "{}:{}".format(workchain, xhex2hex(address))
			#end if
			
			workchain = self.GetVarFromDict(data, "message.info.dest.workchain_id")
			address = self.GetVarFromDict(data, "message.info.dest.address")
			if address:
				dest = "{}:{}".format(workchain, xhex2hex(address))
			#end if
			
			grams = self.GetVarFromDict(data, "message.info.value.grams.value")
			ihr_fee = self.GetVarFromDict(data, "message.info.ihr_fee.value")
			fwd_fee = self.GetVarFromDict(data, "message.info.fwd_fee.value")
			import_fee = self.GetVarFromDict(data, "message.info.import_fee.value")
			
			#body = self.GetVarFromDict(data, "message.body.value")
			message = self.GetItemFromDict(data, "message")
			body = self.GetItemFromDict(message, "body")
			value = self.GetItemFromDict(body, "value")
			body = self.GetBodyFromDict(value)
			comment = self.GetComment(body)
			
			#storage_ph
			#credit_ph
			#compute_ph.gas_fees
			#compute_ph.gas_used
			#compute_ph.gas_limit
			
			message = Message()
			message.type = transData.get("type")
			message.block = transData.get("block")
			message.time = transData.get("time")
			#message.outmsg = transData.get("outmsg")
			message.total_fees = ng2g(transData.get("total_fees"))
			message.ihr_disabled = ihr_disabled
			message.bounce = bounce
			message.bounced = bounced
			message.src = src
			message.dest = dest
			message.value = ng2g(grams)
			message.body = body
			message.comment = comment
			message.ihr_fee = ng2g(ihr_fee)
			message.fwd_fee = ng2g(fwd_fee)
			#message.storage_ph = storage_ph
			#message.credit_ph = credit_ph
			#message.compute_ph = compute_ph
			history.append(message)
		#end for
		return history
	#end define
	
	
	
	def GetMessagesFromTransaction(self, data):
		result = list()
		for key, item in data.items():
			if ("inbound message" in key or
			"outbound message" in key):
				result.append(item)
		#end for
		return result
	#end define
	
	def GetBody(self, buff):
		if buff is None:
			return
		#end if
		
		body = ""
		arr = buff.split('\n')
		for item in arr:
			if "x{" not in item:
				continue
			buff = Pars(item, '{', '}')
			buff = buff.replace('_', '')
			if len(buff)%2 == 1:
				buff = "0" + buff
			body += buff
		#end for
		return body
	#end define
	
	def GetBodyFromDict(self, buff):
		if buff is None:
			return
		#end if
		
		body = ""
		for item in buff:
			if "x{" not in item:
				continue
			buff = Pars(item, '{', '}')
			buff = buff.replace('_', '')
			if len(buff)%2 == 1:
				buff = "0" + buff
			body += buff
		#end for
		if body == "":
			body = None
		return body
	#end define
	
	def GetComment(self, body):
		if body is None:
			return
		#end if
		
		start = body[:8]
		data = body[8:]
		result = None
		if start == "00000000":
			buff = bytes.fromhex(data)
			try:
				result = buff.decode("utf-8")
			except: pass
		return result
	#end define

	def GetDomainAddr(self, domainName):
		cmd = "dnsresolve {domainName} -1".format(domainName=domainName)
		result = self.liteClient.Run(cmd)
		if "not found" in result:
			raise Exception("GetDomainAddr error: domain \"{domainName}\" not found".format(domainName=domainName))
		resolver = Pars(result, "next resolver", '\n')
		buff = resolver.replace(' ', '')
		buffList = buff.split('=')
		fullHexAddr = buffList[0]
		addr = buffList[1]
		return addr
	#end define

	def GetDomainEndTime(self, domainName):
		local.AddLog("start GetDomainEndTime function", "debug")
		buff = domainName.split('.')
		subdomain = buff.pop(0)
		dnsDomain = ".".join(buff)
		dnsAddr = self.GetDomainAddr(dnsDomain)

		cmd = "runmethod {addr} getexpiration \"{subdomain}\"".format(addr=dnsAddr, subdomain=subdomain)
		result = self.liteClient.Run(cmd)
		result = Pars(result, "result:", '\n')
		result = Pars(result, "[", "]")
		result = result.replace(' ', '')
		result = int(result)
		return result
	#end define

	def GetDomainAdnlAddr(self, domainName):
		local.AddLog("start GetDomainAdnlAddr function", "debug")
		cmd = "dnsresolve {domainName} 1".format(domainName=domainName)
		result = self.liteClient.Run(cmd)
		lines = result.split('\n')
		for line in lines:
			if "adnl address" in line:
				adnlAddr = Pars(line, "=", "\n")
				adnlAddr = adnlAddr.replace(' ', '')
				adnlAddr = adnlAddr
				return adnlAddr
	#end define

	def GetLocalWallet(self, walletName, version=None, subwallet=None):
		local.AddLog("start GetLocalWallet function", "debug")
		if walletName is None:
			return None
		walletPath = self.walletsDir + walletName
		if version and "h" in version:
			wallet = self.GetHighWalletFromFile(walletPath, subwallet, version)
		else:
			wallet = self.GetWalletFromFile(walletPath, version)
		return wallet
	#end define

	def GetWalletFromFile(self, filePath, version):
		local.AddLog("start GetWalletFromFile function", "debug")
		# Check input args
		if (".addr" in filePath):
			filePath = filePath.replace(".addr", '')
		if (".pk" in filePath):
			filePath = filePath.replace(".pk", '')
		if os.path.isfile(filePath + ".pk") == False:
			raise Exception("GetWalletFromFile error: Private key not found: " + filePath)
		#end if

		# Create wallet object
		wallet = Wallet()
		wallet.version = version
		wallet.path = filePath
		if '/' in filePath:
			wallet.name = filePath[filePath.rfind('/')+1:]
		else:
			wallet.name = filePath
		#end if

		addrFilePath = filePath + ".addr"
		self.AddrFile2Wallet(wallet, addrFilePath)
		self.WalletVersion2Wallet(wallet)
		return wallet
	#end define

	def GetHighWalletFromFile(self, filePath, subwallet, version):
		local.AddLog("start GetHighWalletFromFile function", "debug")
		# Check input args
		if (".addr" in filePath):
			filePath = filePath.replace(".addr", '')
		if (".pk" in filePath):
			filePath = filePath.replace(".pk", '')
		if os.path.isfile(filePath + ".pk") == False:
			raise Exception("GetHighWalletFromFile error: Private key not found: " + filePath)
		#end if

		# Create wallet object
		wallet = Wallet()
		wallet.subwallet = subwallet
		wallet.version = version
		wallet.path = filePath
		if '/' in filePath:
			wallet.name = filePath[filePath.rfind('/')+1:]
		else:
			wallet.name = filePath
		#end if

		addrFilePath = filePath + str(subwallet) + ".addr"
		self.AddrFile2Wallet(wallet, addrFilePath)
		self.WalletVersion2Wallet(wallet)
		return wallet
	#end define

	def AddrFile2Wallet(self, wallet, addrFilePath):
		#args = ["show-addr.fif", filePath]
		#result = self.fift.Run(args)
		#wallet.fullAddr = Pars(result, "Source wallet address = ", '\n').replace(' ', '')
		#buff = self.GetVarFromWorkerOutput(result, "Bounceable address (for later access)")
		#wallet.addr = buff.replace(' ', '')
		#buff = self.GetVarFromWorkerOutput(result, "Non-bounceable address (for init only)")
		#wallet.addr_init = buff.replace(' ', '')

		file = open(addrFilePath, "rb")
		data = file.read()
		addr_hex = data[:32].hex()
		workchain = struct.unpack("i", data[32:])[0]
		wallet.fullAddr = str(workchain) + ":" + addr_hex
		wallet.addr = self.HexAddr2Base64Addr(wallet.fullAddr)
		wallet.addr_init = self.HexAddr2Base64Addr(wallet.fullAddr, False)
		wallet.Refresh()
	#end define
	
	def WalletVersion2Wallet(self, wallet):
		local.AddLog("start WalletVersion2Wallet function", "debug")
		if wallet.version is not None:
			return
		walletsVersionList = self.GetWalletsVersionList()
		account = self.GetAccount(wallet.addr)
		version = walletsVersionList.get(wallet.addr)
		if version is None:
			version = self.GetWalletVersionFromHash(account.codeHash)
		if version is None:
			local.AddLog("Wallet version not found: " + wallet.addr, "error")
			return
		#end if
		
		self.SetWalletVersion(wallet.addr, version)
		wallet.version = version
	#end define
	
	def SetWalletVersion(self, addr, version):
		walletsVersionList = self.GetWalletsVersionList()
		walletsVersionList[addr] = version
		local.dbSave()
	#end define
	
	def GetWalletVersionFromHash(self, inputHash):
		local.AddLog("start GetWalletVersionFromHash function", "debug")
		arr = dict()
		arr["v1r1"] = "d670136510daff4fee1889b8872c4c1e89872ffa1fe58a23a5f5d99cef8edf32"
		arr["v1r2"] = "2705a31a7ac162295c8aed0761cc6e031ab65521dd7b4a14631099e02de99e18"
		arr["v1r3"] = "c3b9bb03936742cfbb9dcdd3a5e1f3204837f613ef141f273952aa41235d289e"
		arr["v2r1"] = "fa44386e2c445f1edf64702e893e78c3f9a687a5a01397ad9e3994ee3d0efdbf"
		arr["v2r2"] = "d5e63eff6fa268d612c0cf5b343c6674b7312c58dfd9ffa1b536f2014a919164"
		arr["v3r1"] = "4505c335cb60f221e58448c71595bb6d7c980c01a798b392ebb53d86cb6061dc"
		arr["v3r2"] = "8a6d73bdd8704894f17d8c76ce6139034b8a51b1802907ca36283417798a219b"
		arr["v4"] = "7ae380664c513769eaa5c94f9cd5767356e3f7676163baab66a4b73d5edab0e5"
		arr["hv1"] = "fc8e48ed7f9654ba76757f52cc6031b2214c02fab9e429ffa0340f5575f9f29c"
		for version, hash in arr.items():
			if hash == inputHash:
				return version
		#end for
	#end define
	
	def GetWalletsVersionList(self):
		bname = "walletsVersionList"
		walletsVersionList = local.db.get(bname)
		if walletsVersionList is None:
			walletsVersionList = dict()
			local.db[bname] = walletsVersionList
		return walletsVersionList
	#end define

	def GetFullConfigAddr(self):
		# get buffer
		timestamp = GetTimestamp()
		fullConfigAddr = local.buffer.get("fullConfigAddr")
		fullConfigAddr_time = local.buffer.get("fullConfigAddr_time")
		if fullConfigAddr:
			diffTime = timestamp - fullConfigAddr_time
			if diffTime < 10:
				return fullConfigAddr
		#end if

		local.AddLog("start GetFullConfigAddr function", "debug")
		result = self.liteClient.Run("getconfig 0")
		configAddr_hex = self.GetVarFromWorkerOutput(result, "config_addr:x")
		fullConfigAddr = "-1:{configAddr_hex}".format(configAddr_hex=configAddr_hex)
		local.buffer["fullConfigAddr"] = fullConfigAddr
		local.buffer["fullConfigAddr_time"] = timestamp
		return fullConfigAddr
	#end define

	def GetFullElectorAddr(self):
		# Get buffer
		timestamp = GetTimestamp()
		fullElectorAddr = local.buffer.get("fullElectorAddr")
		fullElectorAddr_time = local.buffer.get("fullElectorAddr_time")
		if fullElectorAddr:
			diffTime = timestamp - fullElectorAddr_time
			if diffTime < 10:
				return fullElectorAddr
		#end if

		# Get data
		local.AddLog("start GetFullElectorAddr function", "debug")
		result = self.liteClient.Run("getconfig 1")
		electorAddr_hex = self.GetVarFromWorkerOutput(result, "elector_addr:x")
		fullElectorAddr = "-1:{electorAddr_hex}".format(electorAddr_hex=electorAddr_hex)

		# Set buffer
		local.buffer["fullElectorAddr"] = fullElectorAddr
		local.buffer["fullElectorAddr_time"] = timestamp
		return fullElectorAddr
	#end define

	def GetFullMinterAddr(self):
		# Get buffer
		timestamp = GetTimestamp()
		fullMinterAddr = local.buffer.get("fullMinterAddr")
		fullMinterAddr_time = local.buffer.get("fullMinterAddr_time")
		if fullMinterAddr:
			diffTime = timestamp - fullMinterAddr_time
			if diffTime < 10:
				return fullMinterAddr
		#end if

		local.AddLog("start GetFullMinterAddr function", "debug")
		result = self.liteClient.Run("getconfig 2")
		minterAddr_hex = self.GetVarFromWorkerOutput(result, "minter_addr:x")
		fullMinterAddr = "-1:{minterAddr_hex}".format(minterAddr_hex=minterAddr_hex)

		# Set buffer
		local.buffer["fullMinterAddr"] = fullMinterAddr
		local.buffer["fullMinterAddr_time"] = timestamp
		return fullMinterAddr
	#end define

	def GetFullDnsRootAddr(self):
		# get buffer
		timestamp = GetTimestamp()
		fullDnsRootAddr = local.buffer.get("fullDnsRootAddr")
		fullDnsRootAddr_time = local.buffer.get("fullDnsRootAddr_time")
		if fullDnsRootAddr:
			diffTime = timestamp - fullDnsRootAddr_time
			if diffTime < 10:
				return fullDnsRootAddr
		#end if

		local.AddLog("start GetFullDnsRootAddr function", "debug")
		result = self.liteClient.Run("getconfig 4")
		dnsRootAddr_hex = self.GetVarFromWorkerOutput(result, "dns_root_addr:x")
		fullDnsRootAddr = "-1:{dnsRootAddr_hex}".format(dnsRootAddr_hex=dnsRootAddr_hex)
		local.buffer["fullDnsRootAddr"] = fullDnsRootAddr
		local.buffer["fullDnsRootAddr_time"] = timestamp
		return fullDnsRootAddr
	#end define

	def GetActiveElectionId(self, fullElectorAddr):
		# get buffer
		timestamp = GetTimestamp()
		activeElectionId = local.buffer.get("activeElectionId")
		activeElectionId_time = local.buffer.get("activeElectionId_time")
		if activeElectionId:
			diffTime = timestamp - activeElectionId_time
			if diffTime < 10:
				return activeElectionId
		#end if

		local.AddLog("start GetActiveElectionId function", "debug")
		cmd = "runmethod {fullElectorAddr} active_election_id".format(fullElectorAddr=fullElectorAddr)
		result = self.liteClient.Run(cmd)
		activeElectionId = self.GetVarFromWorkerOutput(result, "result")
		activeElectionId = activeElectionId.replace(' ', '')
		activeElectionId = Pars(activeElectionId, '[', ']')
		activeElectionId = int(activeElectionId)
		local.buffer["activeElectionId"] = activeElectionId
		local.buffer["activeElectionId_time"] = timestamp
		return activeElectionId
	#end define

	def GetValidatorsElectedFor(self):
		local.AddLog("start GetValidatorsElectedFor function", "debug")
		config15 = self.GetConfig15()
		return config15["validatorsElectedFor"]
	#end define

	def GetMinStake(self):
		local.AddLog("start GetMinStake function", "debug")
		config17 = self.GetConfig17()
		return config17["minStake"]
	#end define

	def GetRootWorkchainEnabledTime(self):
		local.AddLog("start GetRootWorkchainEnabledTime function", "debug")
		config12 = self.GetConfig12()
		result = config12["workchains"]["root"]["enabledSince"]
		return result
	#end define

	def GetTotalValidators(self):
		local.AddLog("start GetTotalValidators function", "debug")
		config34 = self.GetConfig34()
		result = config34["totalValidators"]
		return result
	#end define

	def GetLastBlock(self):
		block = None
		cmd = "last"
		result = self.liteClient.Run(cmd)
		lines = result.split('\n')
		for line in lines:
			if "latest masterchain block" in line:
				buff = line.split(' ')
				block = Block(buff[7])
				break
		return block
	#end define
	
	def GetInitBlock_new(self):
		#block = self.GetLastBlock()
		#cmd = f"gethead {block}"
		#result = self.liteClient.Run(cmd)
		#seqno =  Pars(result, "prev_key_block_seqno=", '\n')
		statesDir = "/var/ton-work/db/archive/states"
		os.chdir(statesDir)
		files = filter(os.path.isfile, os.listdir(statesDir))
		files = [os.path.join(statesDir, f) for f in files] # add path to each file
		files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
		for fileName in files:
			buff = fileName.split('_')
			seqno = int(buff[1])
			workchain = int(buff[2])
			if workchain != -1:
				continue
			shardchain = int(buff[3])
			data = self.GetBlockHead(workchain, shardchain, seqno)
			return data
	#end define
	
	def GetInitBlock(self):
		block = self.GetLastBlock()
		cmd = f"gethead {block}"
		result = self.liteClient.Run(cmd)
		seqno =  Pars(result, "prev_key_block_seqno=", '\n')
		data = self.GetBlockHead(-1, 8000000000000000, seqno)
		return data
	#end define
	
	def GetBlockHead(self, workchain, shardchain, seqno):
		block = GetBlock(workchain, shardchain, seqno)
		data = dict()
		data["seqno"] = block.seqno
		data["rootHash"] = block.rootHash
		data["fileHash"] = block.fileHash
		return data
	#end define
	
	def GetBlock(self, workchain, shardchain, seqno):
		cmd = "byseqno {workchain}:{shardchain} {seqno}"
		cmd = cmd.format(workchain=workchain, shardchain=shardchain, seqno=seqno)
		result = self.liteClient.Run(cmd)
		block_str =  Pars(result, "block header of ", ' ')
		block = Block(block_str)
		return block
	#end define

	def GetTransactions(self, block):
		transactions = list()
		cmd = "listblocktrans {block} 999999".format(block=block)
		result = self.liteClient.Run(cmd)
		lines = result.split('\n')
		for line in lines:
			if "transaction #" in line:
				buff = line.split(' ')
				trans_id = buff[1]
				trans_id = trans_id.replace('#', '')
				trans_id = trans_id.replace(':', '')
				trans_account = buff[3]
				trans_lt = buff[5]
				trans_hash = buff[7]
				#trans = {"id": trans_id, "account": trans_account, "lt": trans_lt, "hash": trans_hash}
				addrHex = f"{block.workchain}:{trans_account}"
				trans = Trans(block, trans_id, addrHex, trans_lt, trans_hash)
				transactions.append(trans)
		return transactions
	#end define

	def GetTrans(self, trans):
		messageList, prevTransLt, prevTransHash = self.LastTransDump(trans.addrHex, trans.lt, trans.hash, count=1)
		return messageList
	#end define

	def TryGetTransactionsNumber(self, block):
		errText = None
		for i in range(3):
			time.sleep(i)
			try:
				transNum = self.GetTransactionsNumber(block)
				return transNum
			except Exception as err:
				errText = str(err)
		local.AddLog("TryGetTransactionsNumber error: " + errText, "error")
	#end define

	def GetTransactionsNumber(self, block):
		transactions = self.GetTransactions(block)
		transNum = len(transactions)
		return transNum
	#end define

	def GetShards(self, block=None):
		shards = list()
		if block:
			cmd = "allshards {block}".format(block=block)
		else:
			cmd = "allshards"
		result = self.liteClient.Run(cmd)
		lines = result.split('\n')
		for line in lines:
			if "shard #" in line:
				buff = line.split(' ')
				shard_id = buff[1]
				shard_id = shard_id.replace('#', '')
				shard_block = Block(buff[3])
				shard = {"id": shard_id, "block": shard_block}
				shards.append(shard)
		return shards
	#end define

	def GetShardsNumber(self, block=None):
		shards = self.GetShards(block)
		shardsNum = len(shards)
		return shardsNum
	#end define

	def GetValidatorStatus(self):
		# get buffer
		timestamp = GetTimestamp()
		validatorStatus = local.buffer.get("validatorStatus")
		if validatorStatus:
			diffTime = timestamp - validatorStatus.get("unixtime")
			if diffTime < 10:
				return validatorStatus
		#end if

		# local.AddLog("start GetValidatorStatus function", "debug")
		validatorStatus = dict()
		try:
			validatorStatus["isWorking"] = True
			result = self.validatorConsole.Run("getstats")
			validatorStatus["unixtime"] = int(Pars(result, "unixtime", '\n'))
			validatorStatus["masterchainblocktime"] = int(Pars(result, "masterchainblocktime", '\n'))
			validatorStatus["stateserializermasterchainseqno"] = int(Pars(result, "stateserializermasterchainseqno", '\n'))
			validatorStatus["shardclientmasterchainseqno"] = int(Pars(result, "shardclientmasterchainseqno", '\n'))
			buff = Pars(result, "masterchainblock", '\n')
			validatorStatus["masterchainblock"] = self.GVS_GetItemFromBuff(buff)
			buff = Pars(result, "gcmasterchainblock", '\n')
			validatorStatus["gcmasterchainblock"] = self.GVS_GetItemFromBuff(buff)
			buff = Pars(result, "keymasterchainblock", '\n')
			validatorStatus["keymasterchainblock"] = self.GVS_GetItemFromBuff(buff)
			buff = Pars(result, "rotatemasterchainblock", '\n')
			validatorStatus["rotatemasterchainblock"] = self.GVS_GetItemFromBuff(buff)
			validatorStatus["transNum"] = local.buffer.get("transNum", -1)
			validatorStatus["blocksNum"] = local.buffer.get("blocksNum", -1)
			validatorStatus["masterBlocksNum"] = local.buffer.get("masterBlocksNum", -1)
		except:
			validatorStatus["isWorking"] = False
			validatorStatus["unixtime"] = timestamp
			validatorStatus["masterchainblocktime"] = 0
		validatorStatus["outOfSync"] = validatorStatus["unixtime"] - validatorStatus["masterchainblocktime"]
		local.buffer["validatorStatus"] = validatorStatus # set buffer
		return validatorStatus
	#end define

	def GVS_GetItemFromBuff(self, buff):
		buffList = buff.split(':')
		buff2 = buffList[0]
		buff2 = buff2.replace(' ', '')
		buff2 = buff2.replace('(', '')
		buff2 = buff2.replace(')', '')
		buffList2 = buff2.split(',')
		item = buffList2[2]
		item = int(item)
		return item
	#end define

	def GetConfigs(self):
		configs = local.buffer.get("configs")
		if configs is None:
			configs = dict()
			local.buffer["configs"] = configs
		return configs
	#end define

	def GetConfigsTimestamps(self):
		configsTimestamps = local.buffer.get("configsTimestamps")
		if configsTimestamps is None:
			configsTimestamps = dict()
			local.buffer["configsTimestamps"] = configsTimestamps
		return configsTimestamps
	#end define

	def GetConfig(self, configId):
		# get buffer
		timestamp = GetTimestamp()
		configs = self.GetConfigs()
		configsTimestamps = self.GetConfigsTimestamps()
		config = configs.get(configId)
		configTimestamp = configsTimestamps.get(configId)
		if config:
			diffTime = timestamp - configTimestamp
			if diffTime < 60:
				return config
		#end if

		text = "start GetConfig function ({})".format(configId)
		local.AddLog(text, "debug")
		cmd = "getconfig {configId}".format(configId=configId)
		result = self.liteClient.Run(cmd)
		start = result.find("ConfigParam")
		text = result[start:]
		data = self.Tlb2Json(text)
		# write buffer
		configs[configId] = data
		configsTimestamps[configId] = timestamp
		return data
	#end define

	def GetConfig12_old(self):
		# get buffer
		timestamp = GetTimestamp()
		config12 = local.buffer.get("config12")
		if config12:
			diffTime = timestamp - config12.get("timestamp")
			if diffTime < 60:
				return config12
		#end if

		local.AddLog("start GetConfig12 function", "debug")
		config12 = dict()
		config12["timestamp"] = timestamp
		config12["workchains"] = dict()
		config12["workchains"]["root"] = dict()
		result = self.liteClient.Run("getconfig 12")
		workchains = self.GetVarFromWorkerOutput(result, "workchains")
		workchain_root = self.GetVarFromWorkerOutput(workchains, "root")
		config12["workchains"]["root"]["enabledSince"] = int(Pars(workchain_root, "enabled_since:", ' '))
		local.buffer["config12"] = config12 # set buffer
		return config12
	#end define

	def GetConfig12(self):
		config = self.GetConfig(12)
		enabled_since = config["workchains"]["root"]["node"]["value"]["enabled_since"]
		config12 = {"workchains": {"root": {"enabledSince": enabled_since}}}
		return config12
	#end define

	def GetConfig15_old(self):
		# get buffer
		timestamp = GetTimestamp()
		config15 = local.buffer.get("config15")
		if config15:
			diffTime = timestamp - config15.get("timestamp")
			if diffTime < 60:
				return config15
		#end if

		local.AddLog("start GetConfig15 function", "debug")
		config15 = dict()
		config15["timestamp"] = timestamp
		result = self.liteClient.Run("getconfig 15")
		config15["validatorsElectedFor"] = int(Pars(result, "validators_elected_for:", ' '))
		config15["electionsStartBefore"] = int(Pars(result, "elections_start_before:", ' '))
		config15["electionsEndBefore"] = int(Pars(result, "elections_end_before:", ' '))
		config15["stakeHeldFor"] = int(Pars(result, "stake_held_for:", ')'))
		local.buffer["config15"] = config15 # set buffer
		return config15
	#end define

	def GetConfig15(self):
		config = self.GetConfig(15)
		config15 = dict()
		config15["validatorsElectedFor"] = config["validators_elected_for"]
		config15["electionsStartBefore"] = config["elections_start_before"]
		config15["electionsEndBefore"] = config["elections_end_before"]
		config15["stakeHeldFor"] = config["stake_held_for"]
		return config15
	#end define

	def GetConfig17_old(self):
		# get buffer
		timestamp = GetTimestamp()
		config17 = local.buffer.get("config17")
		if config17:
			diffTime = timestamp - config17.get("timestamp")
			if diffTime < 60:
				return config17
		#end if

		local.AddLog("start GetConfig17 function", "debug")
		config17 = dict()
		config17["timestamp"] = timestamp
		result = self.liteClient.Run("getconfig 17")
		minStake = self.GetVarFromWorkerOutput(result, "min_stake")
		minStake = self.GetVarFromWorkerOutput(minStake, "value")
		config17["minStake"] = ng2g(minStake)
		maxStake = self.GetVarFromWorkerOutput(result, "max_stake")
		maxStake = self.GetVarFromWorkerOutput(maxStake, "value")
		config17["maxStake"] = ng2g(maxStake)
		maxStakeFactor = self.GetVarFromWorkerOutput(result, "max_stake_factor")
		config17["maxStakeFactor"] = int(maxStakeFactor)
		local.buffer["config17"] = config17 # set buffer
		return config17
	#end define

	def GetConfig17(self):
		config = self.GetConfig(17)
		config17 = dict()
		config17["minStake"] = ng2g(config["min_stake"]["amount"]["value"])
		config17["maxStake"] = ng2g(config["max_stake"]["amount"]["value"])
		config17["maxStakeFactor"] = config["max_stake_factor"]
		return config17
	#end define

	def GetConfig32(self):
		# get buffer
		timestamp = GetTimestamp()
		config32 = local.buffer.get("config32")
		if config32:
			diffTime = timestamp - config32.get("timestamp")
			if diffTime < 60:
				return config32
		#end if

		local.AddLog("start GetConfig32 function", "debug")
		config32 = dict()
		config32["timestamp"] = timestamp
		result = self.liteClient.Run("getconfig 32")
		config32["totalValidators"] = int(Pars(result, "total:", ' '))
		config32["startWorkTime"] = int(Pars(result, "utime_since:", ' '))
		config32["endWorkTime"] = int(Pars(result, "utime_until:", ' '))
		lines = result.split('\n')
		validators = list()
		for line in lines:
			if "public_key:" in line:
				validatorAdnlAddr = Pars(line, "adnl_addr:x", ')')
				pubkey = Pars(line, "pubkey:x", ')')
				if config32["totalValidators"] > 1:
					validatorWeight = int(Pars(line, "weight:", ' '))
				else:
					validatorWeight = int(Pars(line, "weight:", ')'))
				buff = dict()
				buff["adnlAddr"] = validatorAdnlAddr
				buff["pubkey"] = pubkey
				buff["weight"] = validatorWeight
				validators.append(buff)
		config32["validators"] = validators
		local.buffer["config32"] = config32 # set buffer
		return config32
	#end define

	def GetConfig34(self):
		# get buffer
		timestamp = GetTimestamp()
		config34 = local.buffer.get("config34")
		if config34:
			diffTime = timestamp - config34.get("timestamp")
			if diffTime < 60:
				return config34
		#end if

		local.AddLog("start GetConfig34 function", "debug")
		config34 = dict()
		config34["timestamp"] = timestamp
		result = self.liteClient.Run("getconfig 34")
		config34["totalValidators"] = int(Pars(result, "total:", ' '))
		config34["startWorkTime"] = int(Pars(result, "utime_since:", ' '))
		config34["endWorkTime"] = int(Pars(result, "utime_until:", ' '))
		config34["totalWeight"] = int(Pars(result, "total_weight:", ' '))
		lines = result.split('\n')
		validators = list()
		for line in lines:
			if "public_key:" in line:
				validatorAdnlAddr = Pars(line, "adnl_addr:x", ')')
				pubkey = Pars(line, "pubkey:x", ')')
				if config34["totalValidators"] > 1:
					validatorWeight = int(Pars(line, "weight:", ' '))
				else:
					validatorWeight = int(Pars(line, "weight:", ')'))
				buff = dict()
				buff["adnlAddr"] = validatorAdnlAddr
				buff["pubkey"] = pubkey
				buff["weight"] = validatorWeight
				validators.append(buff)
		config34["validators"] = validators
		local.buffer["config34"] = config34 # set buffer
		return config34
	#end define

	def GetConfig36(self):
		# get buffer
		timestamp = GetTimestamp()
		config36 = local.buffer.get("config36")
		if config36:
			diffTime = timestamp - config36.get("timestamp")
			if diffTime < 60:
				return config36
		#end if

		local.AddLog("start GetConfig36 function", "debug")
		config36 = dict()
		config36["timestamp"] = timestamp
		try:
			result = self.liteClient.Run("getconfig 36")
			config36["totalValidators"] = int(Pars(result, "total:", ' '))
			config36["startWorkTime"] = int(Pars(result, "utime_since:", ' '))
			config36["endWorkTime"] = int(Pars(result, "utime_until:", ' '))
			lines = result.split('\n')
			validators = list()
			for line in lines:
				if "public_key:" in line:
					validatorAdnlAddr = Pars(line, "adnl_addr:x", ')')
					pubkey = Pars(line, "pubkey:x", ')')
					validatorWeight = Pars(line, "weight:", ' ')
					buff = dict()
					buff["adnlAddr"] = validatorAdnlAddr
					buff["pubkey"] = pubkey
					buff["weight"] = validatorWeight
					validators.append(buff)
			config36["validators"] = validators
		except:
			config36["validators"] = list()
		local.buffer["config36"] = config36 # set buffer
		return config36
	#end define

	def CreateNewKey(self):
		local.AddLog("start CreateNewKey function", "debug")
		result = self.validatorConsole.Run("newkey")
		key = Pars(result, "created new key ", '\n')
		return key
	#end define

	def GetPubKeyBase64(self, key):
		local.AddLog("start GetPubKeyBase64 function", "debug")
		result = self.validatorConsole.Run("exportpub " + key)
		validatorPubkey_b64 = Pars(result, "got public key: ", '\n')
		return validatorPubkey_b64
	#end define
	
	def GetPubKey(self, key):
		local.AddLog("start GetPubKey function", "debug")
		pubkey_b64 = self.GetPubKeyBase64(key)
		buff = pubkey_b64.encode("utf-8")
		buff = base64.b64decode(buff)
		buff = buff[4:]
		pubkey_hex = buff.hex()
		pubkey_hex = pubkey_hex.upper()
		return pubkey_hex
	#end define

	def AddKeyToValidator(self, key, startWorkTime, endWorkTime):
		local.AddLog("start AddKeyToValidator function", "debug")
		output = False
		cmd = "addpermkey {key} {startWorkTime} {endWorkTime}".format(key=key, startWorkTime=startWorkTime, endWorkTime=endWorkTime)
		result = self.validatorConsole.Run(cmd)
		if ("success" in result):
			output = True
		return output
	#end define

	def AddKeyToTemp(self, key, endWorkTime):
		local.AddLog("start AddKeyToTemp function", "debug")
		output = False
		result = self.validatorConsole.Run("addtempkey {key} {key} {endWorkTime}".format(key=key, endWorkTime=endWorkTime))
		if ("success" in result):
			output = True
		return output
	#end define

	def AddAdnlAddrToValidator(self, adnlAddr):
		local.AddLog("start AddAdnlAddrToValidator function", "debug")
		output = False
		result = self.validatorConsole.Run("addadnl {adnlAddr} 0".format(adnlAddr=adnlAddr))
		if ("success" in result):
			output = True
		return output
	#end define

	def GetAdnlAddr(self):
		local.AddLog("start GetAdnlAddr function", "debug")
		adnlAddr = local.db.get("adnlAddr")
		return adnlAddr
	#end define

	def AttachAdnlAddrToValidator(self, adnlAddr, key, endWorkTime):
		local.AddLog("start AttachAdnlAddrToValidator function", "debug")
		output = False
		result = self.validatorConsole.Run("addvalidatoraddr {key} {adnlAddr} {endWorkTime}".format(adnlAddr=adnlAddr, key=key, endWorkTime=endWorkTime))
		if ("success" in result):
			output = True
		return output
	#end define

	def CreateConfigProposalRequest(self, offerHash, validatorIndex):
		local.AddLog("start CreateConfigProposalRequest function", "debug")
		fileName = self.tempDir + "proposal_validator-to-sign.req"
		args = ["config-proposal-vote-req.fif", "-i", validatorIndex, offerHash, fileName]
		result = self.fift.Run(args)
		fileName = Pars(result, "Saved to file ", '\n')
		resultList = result.split('\n')
		i = 0
		start_index = 0
		for item in resultList:
			if "Creating a request to vote for configuration proposal" in item:
				start_index = i
			i += 1
		var1 = resultList[start_index + 1]
		var2 = resultList[start_index + 2] # var2 not using
		return var1
	#end define

	def CreateComplaintRequest(self, electionId , complaintHash, validatorIndex):
		local.AddLog("start CreateComplaintRequest function", "debug")
		fileName = self.tempDir + "complaint_validator-to-sign.req"
		args = ["complaint-vote-req.fif", validatorIndex, electionId, complaintHash, fileName]
		result = self.fift.Run(args)
		fileName = Pars(result, "Saved to file ", '\n')
		resultList = result.split('\n')
		i = 0
		start_index = 0
		for item in resultList:
			if "Creating a request to vote for complaint" in item:
				start_index = i
			i += 1
		var1 = resultList[start_index + 1]
		var2 = resultList[start_index + 2] # var2 not using
		return var1
	#end define

	def PrepareComplaint(self, electionId, inputFileName):
		local.AddLog("start PrepareComplaint function", "debug")
		fileName = self.tempDir + "complaint-msg-body.boc"
		args = ["envelope-complaint.fif", electionId, inputFileName, fileName]
		result = self.fift.Run(args)
		fileName = Pars(result, "Saved to file ", ')')
		return fileName
	#end define

	def CreateElectionRequest(self, wallet, startWorkTime, adnlAddr, maxFactor):
		local.AddLog("start CreateElectionRequest function", "debug")
		fileName = self.tempDir + str(startWorkTime) + "_validator-to-sign.bin"
		args = ["validator-elect-req.fif", wallet.addr, startWorkTime, maxFactor, adnlAddr, fileName]
		result = self.fift.Run(args)
		fileName = Pars(result, "Saved to file ", '\n')
		resultList = result.split('\n')
		i = 0
		start_index = 0
		for item in resultList:
			if "Creating a request to participate in validator elections" in item:
				start_index = i
			i += 1
		var1 = resultList[start_index + 1]
		var2 = resultList[start_index + 2] # var2 not using
		return var1
	#end define

	def GetValidatorSignature(self, validatorKey, var1):
		local.AddLog("start GetValidatorSignature function", "debug")
		cmd = "sign {validatorKey} {var1}".format(validatorKey=validatorKey, var1=var1)
		result = self.validatorConsole.Run(cmd)
		validatorSignature = Pars(result, "got signature ", '\n')
		return validatorSignature
	#end define

	def SignElectionRequestWithValidator(self, wallet, startWorkTime, adnlAddr, validatorPubkey_b64, validatorSignature, maxFactor):
		local.AddLog("start SignElectionRequestWithValidator function", "debug")
		fileName = self.tempDir + str(startWorkTime) + "_validator-query.boc"
		args = ["validator-elect-signed.fif", wallet.addr, startWorkTime, maxFactor, adnlAddr, validatorPubkey_b64, validatorSignature, fileName]
		result = self.fift.Run(args)
		pubkey = Pars(result, "validator public key ", '\n')
		fileName = Pars(result, "Saved to file ", '\n')
		return pubkey, fileName
	#end define

	def SignBocWithWallet(self, wallet, bocPath, destAddr, coins, **kwargs):
		local.AddLog("start SignBocWithWallet function", "debug")
		subwallet = kwargs.get("subwallet", 0)
		seqno = self.GetSeqno(wallet)
		resultFilePath = self.tempDir + wallet.name + "_wallet-query"
		if "v1" in wallet.version:
			fiftScript = "wallet.fif"
			args = [fiftScript, wallet.path, destAddr, seqno, coins, "-B", bocPath, resultFilePath]
		elif "v2" in wallet.version:
			fiftScript = "wallet-v2.fif"
			args = [fiftScript, wallet.path, destAddr, seqno, coins, "-B", bocPath, resultFilePath]
		elif "v3" in wallet.version:
			fiftScript = "wallet-v3.fif"
			args = [fiftScript, wallet.path, destAddr, subwallet, seqno, coins, "-B", bocPath, resultFilePath]
		result = self.fift.Run(args)
		resultFilePath = Pars(result, "Saved to file ", ")")
		return resultFilePath
	#end define

	def SendFile(self, filePath, wallet=None, **kwargs):
		local.AddLog("start SendFile function: " + filePath, "debug")
		wait = kwargs.get("wait", True)
		duplicateSendfile = local.db.get("duplicateSendfile", True)
		if not os.path.isfile(filePath):
			raise Exception("SendFile error: no such file '{filePath}'".format(filePath=filePath))
		if wait and wallet:
			wallet.oldseqno = self.GetSeqno(wallet)
		self.liteClient.Run("sendfile " + filePath)
		if duplicateSendfile:
			self.liteClient.Run("sendfile " + filePath, useLocalLiteServer=False)
			self.liteClient.Run("sendfile " + filePath, useLocalLiteServer=False)
		if wait and wallet:
			self.WaitTransaction(wallet)
		os.remove(filePath)
	#end define

	def WaitTransaction(self, wallet, ex=True):
		local.AddLog("start WaitTransaction function", "debug")
		for i in range(10): # wait 30 sec
			time.sleep(3)
			seqno = self.GetSeqno(wallet)
			if seqno != wallet.oldseqno:
				return
		if ex:
			raise Exception("WaitTransaction error: time out")
	#end define

	def GetReturnedStake(self, fullElectorAddr, wallet):
		local.AddLog("start GetReturnedStake function", "debug")
		cmd = "runmethod {fullElectorAddr} compute_returned_stake 0x{addr_hex}".format(fullElectorAddr=fullElectorAddr, addr_hex=wallet.addr_hex)
		result = self.liteClient.Run(cmd)
		returnedStake = self.GetVarFromWorkerOutput(result, "result")
		returnedStake = returnedStake.replace(' ', '')
		returnedStake = Pars(returnedStake, '[', ']')
		returnedStake = ng2g(returnedStake)
		return returnedStake
	#end define

	def RecoverStake(self):
		local.AddLog("start RecoverStake function", "debug")
		resultFilePath = self.tempDir + "recover-query"
		args = ["recover-stake.fif", resultFilePath]
		result = self.fift.Run(args)
		resultFilePath = Pars(result, "Saved to file ", '\n')
		return resultFilePath
	#end define

	def GetStake(self, account):
		stake = local.db.get("stake")
		stakePercent = local.db.get("stakePercent", 99)
		vconfig = self.GetValidatorConfig()
		validators = vconfig.get("validators")
		if stake is None:
			sp = stakePercent / 100
			if sp > 1 or sp < 0:
				local.AddLog("Wrong stakePercent value. Using default stake.", "warning")
			elif len(validators) == 0:
				stake = int(account.balance*sp/2)
			elif len(validators) > 0:
				stake = int(account.balance*sp)
		return stake
	#end define

	def GetMaxFactor(self):
		# Either use defined maxFactor, or set maximal allowed by config17
		maxFactor = local.db.get("maxFactor")
		if maxFactor is None:
			config17 = self.GetConfig17()
			maxFactor = config17["maxStakeFactor"] / 65536
		maxFactor = round(maxFactor, 1)
		return maxFactor
	#end define
	
	def GetNominationControllerLastSentStakeTime(self, addr):
		cmd = "runmethodfull {addr} all_data".format(addr=addr)
		result = self.liteClient.Run(cmd)
		buff = self.Result2List(result)
		return buff[-1]
	#end define
	
	def IsNominationControllerReadyToStake(self, addr):
		now = GetTimestamp()
		config15 = self.GetConfig15()
		lastSentStakeTime = self.GetNominationControllerLastSentStakeTime(addr)
		stakeFreezeDelay = config15["validatorsElectedFor"] + config15["stakeHeldFor"]
		result = lastSentStakeTime + stakeFreezeDelay < now
		return result
	#end define
	
	def IsNominationControllerReadyToVote(self, addr):
		vwl = self.GetValidatorsWalletsList()
		result = addr in vwl
		return result
	#end define
	
	def GetNominationController(self, mode):
		local.AddLog("start GetNominationController function", "debug")
		nominationControllerList = ["nomination_controller_001", "nomination_controller_002"]
		for item in nominationControllerList:
			wallet = self.GetLocalWallet(item)
			if mode == "stake" and self.IsNominationControllerReadyToStake(wallet.addr):
				return wallet
			if mode == "vote" and self.IsNominationControllerReadyToVote(wallet.addr):
				return wallet
	#end define
	
	def GetValidatorWallet(self, mode="stake"):
		local.AddLog("start GetValidatorWallet function", "debug")
		useNominationController = local.db.get("useNominationController")
		if useNominationController is True:
			wallet = self.GetNominationController(mode)
		else:
			walletName = local.db.get("validatorWalletName")
			wallet = self.GetLocalWallet(walletName)
		return wallet
	#end define

	def ElectionEntry(self):
		wallet = self.GetValidatorWallet()
		if wallet is None:
			raise Exception("Validator wallet not fond")
		#end if

		local.AddLog("start ElectionEntry function", "debug")
		# Check if validator is not synchronized
		validatorStatus = self.GetValidatorStatus()
		validatorOutOfSync = validatorStatus.get("outOfSync")
		if validatorOutOfSync > 60:
			local.AddLog("Validator is not synchronized", "error")
			return
		#end if

		# Get startWorkTime and endWorkTime
		fullElectorAddr = self.GetFullElectorAddr()
		startWorkTime = self.GetActiveElectionId(fullElectorAddr)

		# Check if elections started
		if (startWorkTime == 0):
			local.AddLog("Elections have not yet begun", "info")
			return
		#end if

		# Get ADNL address
		adnlAddr = self.GetAdnlAddr()

		# Check if election entry already completed
		entries = self.GetElectionEntries()
		if adnlAddr in entries:
			local.AddLog("Elections entry already completed", "info")
			return
		#end if

		# Get account balance and minimum stake
		account = self.GetAccount(wallet.addr)
		minStake = self.GetMinStake()

		# Calculate stake
		stake = self.GetStake(account)

		# Check if we have enough coins
		balance = account.balance
		if minStake > stake:
			text = "Stake less than the minimum stake. Minimum stake: {minStake}".format(minStake=minStake)
			local.AddLog(text, "error")
			return
		if stake > balance:
			text = "You don't have enough coins. stake: {stake}, wallet balance: {balance}".format(stake=stake, balance=balance)
			local.AddLog(text, "error")
			return
		#end if

		# Calculate endWorkTime
		validatorsElectedFor = self.GetValidatorsElectedFor()
		endWorkTime = startWorkTime + validatorsElectedFor + 300 # 300 sec - margin of seconds

		# Create keys
		validatorKey = self.GetValidatorKeyByTime(startWorkTime, endWorkTime)
		validatorPubkey_b64  = self.GetPubKeyBase64(validatorKey)

		# Attach ADNL addr to validator
		self.AttachAdnlAddrToValidator(adnlAddr, validatorKey, endWorkTime)

		# Create fift's
		maxFactor = self.GetMaxFactor()
		var1 = self.CreateElectionRequest(wallet, startWorkTime, adnlAddr, maxFactor)
		validatorSignature = self.GetValidatorSignature(validatorKey, var1)
		validatorPubkey, resultFilePath = self.SignElectionRequestWithValidator(wallet, startWorkTime, adnlAddr, validatorPubkey_b64, validatorSignature, maxFactor)

		# Send boc file to TON
		resultFilePath = self.SignBocWithWallet(wallet, resultFilePath, fullElectorAddr, stake)
		self.SendFile(resultFilePath, wallet)

		# Save vars to json file
		self.SaveElectionVarsToJsonFile(wallet=wallet, account=account, stake=stake, maxFactor=maxFactor, fullElectorAddr=fullElectorAddr, startWorkTime=startWorkTime, validatorsElectedFor=validatorsElectedFor, endWorkTime=endWorkTime, validatorKey=validatorKey, validatorPubkey_b64=validatorPubkey_b64, adnlAddr=adnlAddr, var1=var1, validatorSignature=validatorSignature, validatorPubkey=validatorPubkey)

		local.AddLog("ElectionEntry completed. Start work time: " + str(startWorkTime))
	#end define

	def GetValidatorKeyByTime(self, startWorkTime, endWorkTime):
		local.AddLog("start GetValidatorKeyByTime function", "debug")
		# Check temp key
		vconfig = self.GetValidatorConfig()
		validators = vconfig.get("validators")
		for item in validators:
			if item.get("election_date") == startWorkTime:
				validatorKey_b64 = item.get("id")
				validatorKey = base64.b64decode(validatorKey_b64).hex()
				validatorKey = validatorKey.upper()
				return validatorKey
		#end for

		# Create temp key
		validatorKey = self.CreateNewKey()
		self.AddKeyToValidator(validatorKey, startWorkTime, endWorkTime)
		self.AddKeyToTemp(validatorKey, endWorkTime)
		return validatorKey
	#end define

	def ReturnStake(self):
		wallet = self.GetValidatorWallet()
		if wallet is None:
			raise Exception("Validator wallet not fond")
		#end if
		
		local.AddLog("start ReturnStake function", "debug")
		fullElectorAddr = self.GetFullElectorAddr()
		returnedStake = self.GetReturnedStake(fullElectorAddr, wallet)
		if returnedStake == 0:
			local.AddLog("You have nothing on the return stake", "debug")
			return
		resultFilePath = self.RecoverStake()
		resultFilePath = self.SignBocWithWallet(wallet, resultFilePath, fullElectorAddr, 1)
		self.SendFile(resultFilePath, wallet)
		local.AddLog("ReturnStake completed")
	#end define

	def SaveElectionVarsToJsonFile(self, **kwargs):
		local.AddLog("start SaveElectionVarsToJsonFile function", "debug")
		fileName = self.tempDir + str(kwargs.get("startWorkTime")) + "_ElectionEntry.json"
		wallet = kwargs.get("wallet")
		account = kwargs.get("account")
		arr = {"wallet":wallet.__dict__, "account":account.__dict__}
		del kwargs["wallet"]
		del kwargs["account"]
		arr.update(kwargs)
		string = json.dumps(arr, indent=4)
		file = open(fileName, 'w')
		file.write(string)
		file.close()
	#ned define

	def CreateWallet(self, name, workchain=0, version="v1", subwallet=None):
		local.AddLog("start CreateWallet function", "debug")
		walletPath = self.walletsDir + name
		if os.path.isfile(walletPath + ".pk") and subwallet is None:
			local.AddLog("CreateWallet error: Wallet already exists: " + name, "warning")
		else:
			if "v1" in version:
				fiftScript = "new-wallet.fif"
				args = [fiftScript, workchain, walletPath]
			if "v2" in version:
				fiftScript = "new-wallet-v2.fif"
				args = [fiftScript, workchain, walletPath]
			if "v3" in version:
				fiftScript = "new-wallet-v3.fif"
				args = [fiftScript, workchain, subwallet, walletPath]
			result = self.fift.Run(args)
			if "Creating new" not in result:
				raise Exception("CreateWallet error")
			#end if
		wallet = self.GetLocalWallet(name, version)
		self.SetWalletVersion(wallet.addr, version)
		return wallet
	#end define

	def CreateHighWallet(self, name, subwallet=1, workchain=0, version="hv1"):
		local.AddLog("start CreateHighWallet function", "debug")
		walletPath = self.walletsDir + name
		if os.path.isfile(walletPath + ".pk") and os.path.isfile(walletPath + str(subwallet) + ".addr"):
			local.AddLog("CreateHighWallet error: Wallet already exists: " + name + str(subwallet), "warning")
		else:
			args = ["new-highload-wallet.fif", workchain, subwallet, walletPath]
			result = self.fift.Run(args)
			if "Creating new high-load wallet" not in result:
				raise Exception("CreateHighWallet error")
			#end if
		hwallet = self.GetLocalWallet(name, version, subwallet)
		self.SetWalletVersion(hwallet.addr, version)
		return hwallet
	#end define

	def ActivateWallet(self, wallet, ex=True):
		local.AddLog("start ActivateWallet function", "debug")
		for i in range(10):
			time.sleep(3)
			account = self.GetAccount(wallet.addr)
			if account.balance > 0:
				self.SendFile(wallet.bocFilePath, wallet)
				return
		if ex:
			raise Exception("ActivateWallet error: time out")
	#end define
	
	def ImportWallet(self, addr, key):
		workchain, addr_hex = self.ParseBase64Addr(addr)
		workchain_bytes = int.to_bytes(workchain, 4, "big", signed=True)
		addr_bytes = bytes.fromhex(addr_hex)
		key_bytes = base64.b64decode(key)
		
		walletName = self.GenerateWalletName()
		walletPath = self.walletsDir + walletName
		file = open(walletPath + ".addr", 'wb')
		file.write(addr_bytes + workchain_bytes)
		file.close()
		
		file = open(walletPath + ".pk", 'wb')
		file.write(key_bytes)
		file.close()
		
		return walletName
	#end define
	
	def ExportWallet(self, walletName):
		wallet = self.GetLocalWallet(walletName)
		
		file = open(wallet.privFilePath, 'rb')
		data = file.read()
		file.close()
		key = base64.b64encode(data).decode("utf-8")
		
		return wallet.addr, key
	#end define

	def GetWalletsNameList(self):
		local.AddLog("start GetWalletsNameList function", "debug")
		walletsNameList = list()
		for fileName in os.listdir(self.walletsDir):
			if fileName.endswith(".addr"):
				fileName = fileName[:fileName.rfind('.')]
				pkFileName = self.walletsDir + fileName + ".pk"
				if os.path.isfile(pkFileName):
					walletsNameList.append(fileName)
		walletsNameList.sort()
		return walletsNameList
	#end define

	def GetWallets(self):
		local.AddLog("start GetWallets function", "debug")
		wallets = list()
		walletsNameList = self.GetWalletsNameList()
		for walletName in walletsNameList:
			wallet = self.GetLocalWallet(walletName)
			wallets.append(wallet)
		return wallets
	#end define

	def GenerateWalletName(self):
		local.AddLog("start GenerateWalletName function", "debug")
		index = 1
		index_str = str(index).rjust(3, '0')
		walletPrefix = "wallet_"
		indexList = list()
		walletName = walletPrefix + index_str
		walletsNameList = self.GetWalletsNameList()
		if walletName in walletsNameList:
			for item in walletsNameList:
				if item.startswith(walletPrefix):
					try:
						index = item[item.rfind('_')+1:]
						index = int(index)
						indexList.append(index)
					except: pass
			index = max(indexList) + 1
			index_str = str(index).rjust(3, '0')
			walletName = walletPrefix + index_str
		return walletName
	#end define

	def WalletsCheck(self):
		local.AddLog("start WalletsCheck function", "debug")
		wallets = self.GetWallets()
		for wallet in wallets:
			if os.path.isfile(wallet.bocFilePath):
				account = self.GetAccount(wallet.addr)
				if account.balance > 0:
					self.SendFile(wallet.bocFilePath, wallet)
	#end define

	def GetValidatorConfig(self):
		local.AddLog("start GetValidatorConfig function", "debug")
		result = self.validatorConsole.Run("getconfig")
		string = Pars(result, "---------", "--------")
		vconfig = json.loads(string)
		return vconfig
	#end define

	def MoveCoins(self, wallet, dest, coins, **kwargs):
		local.AddLog("start MoveCoins function", "debug")
		flags = kwargs.get("flags")
		wait = kwargs.get("wait", True)
		subwallet = kwargs.get("subwallet", 0)
		if coins == "all":
			mode = 130
			coins = 0
		elif coins == "alld":
			mode = 160
			coins = 0
		else:
			mode = 3
		#end if
		
		seqno = self.GetSeqno(wallet)
		resultFilePath = local.buffer.get("myTempDir") + wallet.name + "_wallet-query"
		if "v1" in wallet.version:
			fiftScript = "wallet.fif"
			args = [fiftScript, wallet.path, dest, seqno, coins, "-m", mode, resultFilePath]
		elif "v2" in wallet.version:
			fiftScript = "wallet-v2.fif"
			args = [fiftScript, wallet.path, dest, seqno, coins, "-m", mode, resultFilePath]
		elif "v3" in wallet.version:
			fiftScript = "wallet-v3.fif"
			args = [fiftScript, wallet.path, dest, subwallet, seqno, coins, "-m", mode, resultFilePath]
		if flags:
			args += flags
		result = self.fift.Run(args)
		savedFilePath = Pars(result, "Saved to file ", ")")
		self.SendFile(savedFilePath, wallet, wait=wait)
	#end define

	def MoveCoinsThroughProxy(self, wallet, dest, coins):
		local.AddLog("start MoveCoinsThroughProxy function", "debug")
		wallet1 = self.CreateWallet("proxy_wallet1", 0)
		wallet2 = self.CreateWallet("proxy_wallet2", 0)
		self.MoveCoins(wallet, wallet1.addr_init, coins)
		self.ActivateWallet(wallet1)
		self.MoveCoins(wallet1, wallet2.addr_init, "alld")
		self.ActivateWallet(wallet2)
		self.MoveCoins(wallet2, dest, "alld", flags=["-n"])
		wallet1.Delete()
		wallet2.Delete()
	#end define

	def MoveCoinsFromHW(self, wallet, destList, **kwargs):
		local.AddLog("start MoveCoinsFromHW function", "debug")
		flags = kwargs.get("flags")
		wait = kwargs.get("wait", True)

		if len(destList) == 0:
			local.AddLog("MoveCoinsFromHW warning: destList is empty, break function", "warning")
			return
		#end if

		orderFilePath = local.buffer.get("myTempDir") + wallet.name + "_order.txt"
		lines = list()
		for dest, coins in destList:
			lines.append("SEND {dest} {coins}".format(dest=dest, coins=coins))
		text = "\n".join(lines)
		file = open(orderFilePath, 'wt')
		file.write(text)
		file.close()

		if "v1" in wallet.version:
			fiftScript = "highload-wallet.fif"
		elif "v2" in wallet.version:
			fiftScript = "highload-wallet-v2.fif"
		seqno = self.GetSeqno(wallet)
		resultFilePath = local.buffer.get("myTempDir") + wallet.name + "_wallet-query"
		args = [fiftScript, wallet.path, wallet.subwallet, seqno, orderFilePath, resultFilePath]
		if flags:
			args += flags
		result = self.fift.Run(args)
		savedFilePath = Pars(result, "Saved to file ", ")")
		self.SendFile(savedFilePath, wallet, wait=wait)
	#end define

	def GetValidatorKey(self):
		vconfig = self.GetValidatorConfig()
		validators = vconfig["validators"]
		for validator in validators:
			validatorId = validator["id"]
			key_bytes = base64.b64decode(validatorId)
			validatorKey = key_bytes.hex().upper()
			timestamp = GetTimestamp()
			if timestamp > validator["election_date"]:
				return validatorKey
		raise Exception("GetValidatorKey error: validator key not found. Are you sure you are a validator?")
	#end define

	def GetElectionEntries(self):
		# Get buffer
		timestamp = GetTimestamp()
		electionEntries = local.buffer.get("electionEntries")
		electionEntries_time = local.buffer.get("electionEntries_time")
		if electionEntries:
			diffTime = timestamp - electionEntries_time
			if diffTime < 60:
				return electionEntries
		#end if

		# Check if the elections are open
		entries = dict()
		fullElectorAddr = self.GetFullElectorAddr()
		electionId = self.GetActiveElectionId(fullElectorAddr)
		if electionId == 0:
			return entries
		#end if

		# Get raw data
		local.AddLog("start GetElectionEntries function", "debug")
		cmd = "runmethodfull {fullElectorAddr} participant_list_extended".format(fullElectorAddr=fullElectorAddr)
		result = self.liteClient.Run(cmd)
		rawElectionEntries = self.Result2List(result)

		# Get json
		# Parser by @skydev (https://github.com/skydev0h)
		startWorkTime = rawElectionEntries[0]
		endElectionsTime = rawElectionEntries[1]
		minStake = rawElectionEntries[2]
		allStakes = rawElectionEntries[3]
		electionEntries = rawElectionEntries[4]
		wtf1 = rawElectionEntries[5]
		wtf2 = rawElectionEntries[6]
		for entry in electionEntries:
			if len(entry) == 0:
				continue

			# Create dict
			item = dict()
			adnlAddr = Dec2HexAddr(entry[1][3])
			item["adnlAddr"] = adnlAddr
			item["pubkey"] = Dec2HexAddr(entry[0])
			item["stake"] = ng2g(entry[1][0])
			item["maxFactor"] = round(entry[1][1] / 655.36) / 100.0
			item["walletAddr_hex"] = Dec2HexAddr(entry[1][2])
			item["walletAddr"] = self.HexAddr2Base64Addr("-1:"+item["walletAddr_hex"])
			entries[adnlAddr] = item
		#end for

		# Set buffer
		local.buffer["electionEntries"] = entries
		local.buffer["electionEntries_time"] = timestamp

		# Save elections
		electionId = str(electionId)
		saveElections = self.GetSaveElections()
		saveElections[electionId] = entries
		return entries
	#end define

	def GetSaveElections(self):
		timestamp = GetTimestamp()
		saveElections = local.db.get("saveElections")
		if saveElections is None:
			saveElections = dict()
			local.db["saveElections"] = saveElections
		buff = saveElections.copy()
		for key, item in buff.items():
			diffTime = timestamp - int(key)
			if diffTime > 604800:
				saveElections.pop(key)
		return saveElections
	#end define

	def GetSaveElectionEntries(self, electionId):
		electionId = str(electionId)
		saveElections = self.GetSaveElections()
		result = saveElections.get(electionId)
		return result
	#end define

	def GetOffers(self):
		local.AddLog("start GetOffers function", "debug")
		fullConfigAddr = self.GetFullConfigAddr()
		# Get raw data
		cmd = "runmethodfull {fullConfigAddr} list_proposals".format(fullConfigAddr=fullConfigAddr)
		result = self.liteClient.Run(cmd)
		rawOffers = self.Result2List(result)
		rawOffers = rawOffers[0]
		config34 = self.GetConfig34()
		totalWeight = config34.get("totalWeight")

		# Get json
		offers = list()
		for offer in rawOffers:
			if len(offer) == 0:
				continue
			hash = offer[0]
			subdata = offer[1]

			# Create dict
			# parser from: https://github.com/ton-blockchain/ton/blob/dab7ee3f9794db5a6d32c895dbc2564f681d9126/crypto/smartcont/config-code.fc#L607
			item = dict()
			item["config"] = dict()
			item["hash"] = hash
			item["endTime"] = subdata[0] # *expires*
			item["critFlag"] = subdata[1] # *critical*
			item["config"]["id"] = subdata[2][0] # *param_id*
			item["config"]["value"] = subdata[2][1] # *param_val*
			item["config"]["oldValueHash"] = subdata[2][2] # *param_hash*
			item["vsetId"] = subdata[3] # *vset_id*
			item["votedValidators"] = subdata[4] # *voters_list*
			weightRemaining = subdata[5] # *weight_remaining*
			item["roundsRemaining"] = subdata[6] # *rounds_remaining*
			item["wins"] = subdata[7] # *losses*
			item["losses"] = subdata[8] # *wins*
			requiredWeight = totalWeight * 3 / 4
			if len(item["votedValidators"]) == 0:
				weightRemaining = requiredWeight
			availableWeight = requiredWeight - weightRemaining
			item["weightRemaining"] = weightRemaining
			item["approvedPercent"] = round(availableWeight / totalWeight * 100, 3)
			item["isPassed"] = (weightRemaining < 0)
			offers.append(item)
		#end for
		return offers
	#end define

	def GetOfferDiff(self, offerHash):
		local.AddLog("start GetOfferDiff function", "debug")
		offer = self.GetOffer(offerHash)
		configId = offer["config"]["id"]
		configValue = offer["config"]["value"]

		if '{' in configValue or '}' in configValue:
			start = configValue.find('{') + 1
			end = configValue.find('}')
			configValue = configValue[start:end]
		#end if

		args = [self.liteClient.appPath, "--global-config", self.liteClient.configPath, "--verbosity", "0"]
		process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		time.sleep(1)

		fullConfigAddr = self.GetFullConfigAddr()
		cmd = "runmethodfull {fullConfigAddr} list_proposals".format(fullConfigAddr=fullConfigAddr)
		process.stdin.write(cmd.encode() + b'\n')
		process.stdin.flush()
		time.sleep(1)

		cmd = "dumpcellas ConfigParam{configId} {configValue}".format(configId=configId, configValue=configValue)
		process.stdin.write(cmd.encode() + b'\n')
		process.stdin.flush()
		time.sleep(1)

		process.terminate()
		text = process.stdout.read().decode()

		lines = text.split('\n')
		b = len(lines)
		for i in range(b):
			line = lines[i]
			if "dumping cells as values of TLB type" in line:
				a = i + 2
				break
		#end for

		for i in range(a, b):
			line = lines[i]
			if '(' in line:
				start = i
				break
		#end for

		for i in range(a, b):
			line = lines[i]
			if '>' in line:
				end = i
				break
		#end for

		buff = lines[start:end]
		text = "".join(buff)
		newData = self.Tlb2Json(text)
		newFileName = self.tempDir + "data1diff"
		file = open(newFileName, 'wt')
		newText = json.dumps(newData, indent=2)
		file.write(newText)
		file.close()

		oldData = self.GetConfig(configId)
		oldFileName = self.tempDir + "data2diff"
		file = open(oldFileName, 'wt')
		oldText = json.dumps(oldData, indent=2)
		file.write(oldText)
		file.close()

		print(oldText)
		args = ["diff", "--color", oldFileName, newFileName]
		subprocess.run(args)
	#end define

	def GetComplaints(self, electionId=None, past=False):
		# Get buffer
		timestamp = GetTimestamp()
		bname = "complaints" + str(past)
		bname2 = bname + "_time"
		complaints = local.buffer.get(bname)
		complaints_time = local.buffer.get(bname2)
		if complaints:
			diffTime = timestamp - complaints_time
			if diffTime < 60:
				return complaints
		#end if
		
		# Calculate complaints time
		complaints = dict()
		fullElectorAddr = self.GetFullElectorAddr()
		if electionId is None:
			config32 = self.GetConfig32()
			electionId = config32.get("startWorkTime")
			end = config32.get("endWorkTime")
			buff = end - electionId
		if past:
			electionId = electionId - buff
			saveComplaints = self.GetSaveComplaints()
			complaints = saveComplaints.get(str(electionId))
			return complaints
		#end if
		
		# Get raw data
		local.AddLog("start GetComplaints function", "debug")
		cmd = "runmethodfull {fullElectorAddr} list_complaints {electionId}".format(fullElectorAddr=fullElectorAddr, electionId=electionId)
		result = self.liteClient.Run(cmd)
		rawComplaints = self.Result2List(result)
		if rawComplaints is None:
			return complaints
		rawComplaints = rawComplaints[0]
		config34 = self.GetConfig34()
		totalWeight = config34.get("totalWeight")

		# Get json
		for complaint in rawComplaints:
			if len(complaint) == 0:
				continue
			chash = complaint[0]
			subdata = complaint[1]

			# Create dict
			# parser from: https://github.com/ton-blockchain/ton/blob/dab7ee3f9794db5a6d32c895dbc2564f681d9126/crypto/smartcont/elector-code.fc#L1149
			item = dict()
			buff = subdata[0] # *complaint*
			item["electionId"] = electionId
			item["hash"] = chash
			pubkey = Dec2HexAddr(buff[0]) # *validator_pubkey*
			adnl = self.GetAdnlFromPubkey(pubkey)
			item["pubkey"] = pubkey
			item["adnl"] = adnl
			item["description"] = buff[1] # *description*
			item["createdTime"] = buff[2] # *created_at*
			item["severity"] = buff[3] # *severity*
			rewardAddr = buff[4]
			rewardAddr = "-1:" + Dec2HexAddr(rewardAddr)
			rewardAddr = self.HexAddr2Base64Addr(rewardAddr)
			item["rewardAddr"] = rewardAddr # *reward_addr*
			item["paid"] = buff[5] # *paid*
			suggestedFine = buff[6] # *suggested_fine*
			item["suggestedFine"] = ng2g(suggestedFine)
			suggestedFinePart = buff[7] # *suggested_fine_part*
			item["suggestedFinePart"] = suggestedFinePart /256 *100
			votedValidators = subdata[1] # *voters_list*
			item["votedValidators"] = votedValidators
			item["vsetId"] = subdata[2] # *vset_id*
			weightRemaining = subdata[3] # *weight_remaining*
			requiredWeight = totalWeight * 2 / 3
			if len(votedValidators) == 0:
				weightRemaining = requiredWeight
			availableWeight = requiredWeight - weightRemaining
			item["weightRemaining"] = weightRemaining
			item["approvedPercent"] = round(availableWeight / totalWeight * 100, 3)
			item["isPassed"] = (weightRemaining < 0)
			pseudohash = pubkey + str(electionId)
			item["pseudohash"] = pseudohash
			complaints[pseudohash] = item
		#end for
		
		# Set buffer
		local.buffer[bname] = complaints
		local.buffer[bname2] = timestamp

		# Save complaints
		if len(complaints) > 0:
			electionId = str(electionId)
			saveComplaints = self.GetSaveComplaints()
			saveComplaints[electionId] = complaints
		return complaints
	#end define
	
	def GetSaveComplaints(self):
		timestamp = GetTimestamp()
		saveComplaints = local.db.get("saveComplaints")
		if type(saveComplaints) is not dict:
			saveComplaints = dict()
			local.db["saveComplaints"] = saveComplaints
		buff = saveComplaints.copy()
		for key, item in buff.items():
			diffTime = timestamp - int(key)
			if diffTime > 604800:
				saveComplaints.pop(key)
		return saveComplaints
	#end define

	def GetAdnlFromPubkey(self, inputPubkey):
		config32 = self.GetConfig32()
		validators = config32["validators"]
		for validator in validators:
			adnl = validator["adnlAddr"]
			pubkey = validator["pubkey"]
			if pubkey == inputPubkey:
				return adnl
	#end define

	def GetComplaintsNumber(self):
		local.AddLog("start GetComplaintsNumber function", "debug")
		result = dict()
		complaints = self.GetComplaints()
		votedComplaints = self.GetVotedComplaints()
		buff = 0
		for key, item in complaints.items():
			pubkey = item.get("pubkey")
			electionId = item.get("electionId")
			pseudohash = pubkey + str(electionId)
			if pseudohash in votedComplaints:
				continue
			buff += 1
		result["all"] = len(complaints)
		result["new"] = buff
		return result
	#end define

	def GetComplaint(self, electionId, complaintHash):
		local.AddLog("start GetComplaint function", "debug")
		complaints = self.GetComplaints(electionId)
		for key, item in complaints.items():
			if complaintHash == item.get("hash"):
				return item
		raise Exception("GetComplaint error: complaint not found.")
	#end define

	def SignProposalVoteRequestWithValidator(self, offerHash, validatorIndex, validatorPubkey_b64, validatorSignature):
		local.AddLog("start SignProposalVoteRequestWithValidator function", "debug")
		fileName = self.tempDir + "proposal_vote-msg-body.boc"
		args = ["config-proposal-vote-signed.fif", "-i", validatorIndex, offerHash, validatorPubkey_b64, validatorSignature, fileName]
		result = self.fift.Run(args)
		fileName = Pars(result, "Saved to file ", '\n')
		return fileName
	#end define

	def SignComplaintVoteRequestWithValidator(self, complaintHash, electionId, validatorIndex, validatorPubkey_b64, validatorSignature):
		local.AddLog("start SignComplaintRequestWithValidator function", "debug")
		fileName = self.tempDir + "complaint_vote-msg-body.boc"
		args = ["complaint-vote-signed.fif", validatorIndex, electionId, complaintHash, validatorPubkey_b64, validatorSignature, fileName]
		result = self.fift.Run(args)
		fileName = Pars(result, "Saved to file ", '\n')
		return fileName
	#end define

	def VoteOffer(self, offerHash):
		local.AddLog("start VoteOffer function", "debug")
		fullConfigAddr = self.GetFullConfigAddr()
		wallet = self.GetValidatorWallet(mode="vote")
		validatorKey = self.GetValidatorKey()
		validatorPubkey_b64 = self.GetPubKeyBase64(validatorKey)
		validatorIndex = self.GetValidatorIndex()
		offer = self.GetOffer(offerHash)
		if validatorIndex in offer.get("votedValidators"):
			local.AddLog("Proposal already has been voted", "debug")
			return
		var1 = self.CreateConfigProposalRequest(offerHash, validatorIndex)
		validatorSignature = self.GetValidatorSignature(validatorKey, var1)
		resultFilePath = self.SignProposalVoteRequestWithValidator(offerHash, validatorIndex, validatorPubkey_b64, validatorSignature)
		resultFilePath = self.SignBocWithWallet(wallet, resultFilePath, fullConfigAddr, 1.5)
		self.SendFile(resultFilePath, wallet)
		self.AddSaveOffer(offer)
	#end define

	def VoteComplaint(self, electionId, complaintHash):
		local.AddLog("start VoteComplaint function", "debug")
		complaintHash = int(complaintHash)
		fullElectorAddr = self.GetFullElectorAddr()
		wallet = self.GetValidatorWallet(mode="vote")
		validatorKey = self.GetValidatorKey()
		validatorPubkey_b64 = self.GetPubKeyBase64(validatorKey)
		validatorIndex = self.GetValidatorIndex()
		complaint = self.GetComplaint(electionId, complaintHash)
		votedValidators = complaint.get("votedValidators")
		pubkey = complaint.get("pubkey")
		if validatorIndex in votedValidators:
			local.AddLog("Complaint already has been voted", "info")
			return
		var1 = self.CreateComplaintRequest(electionId, complaintHash, validatorIndex)
		validatorSignature = self.GetValidatorSignature(validatorKey, var1)
		resultFilePath = self.SignComplaintVoteRequestWithValidator(complaintHash, electionId, validatorIndex, validatorPubkey_b64, validatorSignature)
		resultFilePath = self.SignBocWithWallet(wallet, resultFilePath, fullElectorAddr, 1.5)
		self.SendFile(resultFilePath, wallet)
		self.AddVotedComplaints(complaint)
	#end define

	def SaveComplaints(self, electionId):
		local.AddLog("start SaveComplaints function", "debug")
		filePrefix = self.tempDir + "scheck_"
		cmd = "savecomplaints {electionId} {filePrefix}".format(electionId=electionId, filePrefix=filePrefix)
		result = self.liteClient.Run(cmd)
		lines = result.split('\n')
		complaintsHashes = list()
		for line in lines:
			if "SAVE_COMPLAINT" in line:
				buff = line.split('\t')
				chash = buff[2]
				validatorPubkey = buff[3]
				createdTime = buff[4]
				filePath = buff[5]
				ok = self.CheckComplaint(filePath)
				if ok is True:
					complaintsHashes.append(chash)
		return complaintsHashes
	#end define

	def CheckComplaint(self, filePath):
		local.AddLog("start CheckComplaint function", "debug")
		cmd = "loadproofcheck {filePath}".format(filePath=filePath)
		result = self.liteClient.Run(cmd, timeout=30)
		lines = result.split('\n')
		ok = False
		for line in lines:
			if "COMPLAINT_VOTE_FOR" in line:
				buff = line.split('\t')
				chash = buff[1]
				ok_buff = buff[2]
				if ok_buff == "YES":
					ok = True
		return ok
	#end define

	def GetOnlineValidators(self):
		onlineValidators = list()
		data = self.GetValidatorsLoad()
		if len(data) == 0:
			return
		for key, item in data.items():
			online = item.get("online")
			if online is True:
				onlineValidators.append(item)
		return onlineValidators
	#end define

	def GetValidatorsLoad(self, start=None, end=None, timeDiff=2000, saveCompFiles=False):
		timestamp = GetTimestamp()
		if start is None or end is None:
			end = timestamp - 60
			start = end - timeDiff
		else:
			timeDiff = end - start
		# get buffer
		bname = "validatorsLoad_{timeDiff}".format(timeDiff=timeDiff)
		buff = local.buffer.get(bname)
		if buff:
			diffTime = timestamp - buff.get("timestamp")
			if diffTime < 60:
				data = buff.get("data")
				return data
		#end if

		text = "start GetValidatorsLoad function ({}, {})".format(start, end)
		local.AddLog(text, "debug")
		if saveCompFiles is True:
			filePrefix = self.tempDir + "checkload_{start}_{end}".format(start=start, end=end)
		else:
			filePrefix = ""
		cmd = "checkloadall {start} {end} {filePrefix}".format(end=end, start=start, filePrefix=filePrefix)
		result = self.liteClient.Run(cmd, timeout=30)
		lines = result.split('\n')
		data = dict()
		for line in lines:
			if "val" in line and "pubkey" in line:
				buff = line.split(' ')
				vid = buff[1]
				vid = vid.replace('#', '')
				vid = vid.replace(':', '')
				vid = int(vid)
				pubkey = buff[3]
				pubkey = pubkey.replace(',', '')
				blocksCreated_buff = buff[6]
				blocksCreated_buff = blocksCreated_buff.replace('(', '')
				blocksCreated_buff = blocksCreated_buff.replace(')', '')
				blocksCreated_buff = blocksCreated_buff.split(',')
				masterBlocksCreated = float(blocksCreated_buff[0])
				workBlocksCreated = float(blocksCreated_buff[1])
				blocksExpected_buff = buff[8]
				blocksExpected_buff = blocksExpected_buff.replace('(', '')
				blocksExpected_buff = blocksExpected_buff.replace(')', '')
				blocksExpected_buff = blocksExpected_buff.split(',')
				masterBlocksExpected = float(blocksExpected_buff[0])
				workBlocksExpected = float(blocksExpected_buff[1])
				if masterBlocksExpected == 0:
					mr = 0
				else:
					mr = masterBlocksCreated / masterBlocksExpected
				if workBlocksExpected == 0:
					wr = 0
				else:
					wr = workBlocksCreated / workBlocksExpected
				r = (mr + wr) / 2
				efficiency = round(r * 100, 2)
				if efficiency > 10:
					online = True
				else:
					online = False
				item = dict()
				item["id"] = vid
				item["pubkey"] = pubkey
				item["masterBlocksCreated"] = masterBlocksCreated
				item["workBlocksCreated"] = workBlocksCreated
				item["masterBlocksExpected"] = masterBlocksExpected
				item["workBlocksExpected"] = workBlocksExpected
				item["mr"] = mr
				item["wr"] = wr
				item["efficiency"] = efficiency
				item["online"] = online

				# Get complaint file
				index = lines.index(line)
				nextIndex = index + 2
				if nextIndex < len(lines):
					nextLine = lines[nextIndex]
					if "COMPLAINT_SAVED" in nextLine:
						buff = nextLine.split('\t')
						item["var1"] = buff[1]
						item["var2"] = buff[2]
						item["fileName"] = buff[3]
				data[vid] = item
		#end for

		# Write buffer
		buff = dict()
		buff["timestamp"] = timestamp
		buff["data"] = data
		local.buffer[bname] = buff

		return data
	#end define

	def GetValidatorsList(self, past=False):
		start = None
		end = None
		config = self.GetConfig34()
		if past:
			config = self.GetConfig32()
			start = config.get("startWorkTime")
			end = config.get("endWorkTime") - 60
		#end if
		validatorsLoad = self.GetValidatorsLoad(start, end)
		validators = config["validators"]
		electionId = config.get("startWorkTime")
		saveElectionEntries = self.GetSaveElectionEntries(electionId)
		for vid in range(len(validators)):
			validator = validators[vid]
			adnlAddr = validator["adnlAddr"]
			if len(validatorsLoad) > 0:
				validator["mr"] = validatorsLoad[vid]["mr"]
				validator["wr"] = validatorsLoad[vid]["wr"]
				validator["efficiency"] = validatorsLoad[vid]["efficiency"]
				validator["online"] = validatorsLoad[vid]["online"]
			if saveElectionEntries and adnlAddr in saveElectionEntries:
				validator["walletAddr"] = saveElectionEntries[adnlAddr]["walletAddr"]
		return validators
	#end define

	def CheckValidators(self, start, end):
		local.AddLog("start CheckValidators function", "debug")
		electionId = start
		complaints = self.GetComplaints(electionId)
		data = self.GetValidatorsLoad(start, end, saveCompFiles=True)
		fullElectorAddr = self.GetFullElectorAddr()
		wallet = self.GetValidatorWallet(mode="vote")

		# Check wallet and balance
		if wallet is None:
			raise Exception("Validator wallet not fond")
		account = self.GetAccount(wallet.addr)
		if account.balance < 300:
			raise Exception("Validator wallet balance must be greater than 300")
		for key, item in data.items():
			fileName = item.get("fileName")
			if fileName is None:
				continue
			var1 = item.get("var1")
			var2 = item.get("var2")
			pubkey = item.get("pubkey")
			pseudohash = pubkey + str(electionId)
			if pseudohash in complaints:
				continue
			# Create complaint
			fileName = self.PrepareComplaint(electionId, fileName)
			fileName = self.SignBocWithWallet(wallet, fileName, fullElectorAddr, 300)
			self.SendFile(fileName, wallet)
			local.AddLog("var1: {}, var2: {}, pubkey: {}, election_id: {}".format(var1, var2, pubkey, electionId), "debug")
	#end define

	def GetOffer(self, offerHash):
		local.AddLog("start GetOffer function", "debug")
		offers = self.GetOffers()
		for offer in offers:
			if offerHash == offer.get("hash"):
				return offer
		raise Exception("GetOffer error: offer not found.")
	#end define

	def GetOffersNumber(self):
		local.AddLog("start GetOffersNumber function", "debug")
		result = dict()
		offers = self.GetOffers()
		saveOffers = self.GetSaveOffers()
		buff = 0
		for offer in offers:
			offerHash = offer.get("hash")
			if offerHash in saveOffers:
				continue
			buff += 1
		result["all"] = len(offers)
		result["new"] = buff
		return result
	#end define

	def GetValidatorIndex(self, adnlAddr=None):
		config34 = self.GetConfig34()
		validators = config34.get("validators")
		if adnlAddr is None:
			adnlAddr = self.GetAdnlAddr()
		index = 0
		for validator in validators:
			searchAdnlAddr = validator.get("adnlAddr")
			if adnlAddr == searchAdnlAddr:
				return index
			index += 1
		local.AddLog("GetValidatorIndex warning: index not found.", "warning")
		return -1
	#end define

	def GetValidatorEfficiency(self, adnlAddr=None):
		local.AddLog("start GetValidatorEfficiency function", "debug")
		validators = self.GetValidatorsList()
		if adnlAddr is None:
			adnlAddr = self.GetAdnlAddr()
		for validator in validators:
			searchAdnlAddr = validator.get("adnlAddr")
			if adnlAddr == searchAdnlAddr:
				efficiency = validator.get("efficiency")
				return efficiency
		local.AddLog("GetValidatorEfficiency warning: efficiency not found.", "warning")
	#end define
	
	def GetDbUsage(self):
		path = "/var/ton-work/db"
		data = psutil.disk_usage(path)
		return data.percent
	#end define

	def GetDbSize(self, exceptions="log"):
		local.AddLog("start GetDbSize function", "debug")
		exceptions = exceptions.split()
		totalSize = 0
		path = "/var/ton-work/"
		for directory, subdirectory, files in os.walk(path):
			for file in files:
				buff = file.split('.')
				ext = buff[-1]
				if ext in exceptions:
					continue
				filePath = os.path.join(directory, file)
				totalSize += os.path.getsize(filePath)
		result = round(totalSize / 10**9, 2)
		return result
	#end define

	def Result2List(self, text):
		buff = Pars(text, "result:", "\n")
		if buff is None or "error" in buff:
			return
		buff = buff.replace(')', ']')
		buff = buff.replace('(', '[')
		buff = buff.replace(']', ' ] ')
		buff = buff.replace('[', ' [ ')
		buff = buff.replace('bits:', '')
		buff = buff.replace('refs:', '')
		buff = buff.replace('.', '')
		buff = buff.replace(';', '')
		arr = buff.split()

		# Get good raw data
		output = ""
		arrLen = len(arr)
		for i in range(arrLen):
			item = arr[i]
			# get next item
			if i+1 < arrLen:
				nextItem = arr[i+1]
			else:
				nextItem = None
			# add item to output
			if item == '[':
				output += item
			elif nextItem == ']':
				output += item
			elif '{' in item or '}' in item:
				output += "\"{item}\", ".format(item=item)
			elif i+1 == arrLen:
				output += item
			else:
				output += item + ', '
		#end for
		data = json.loads(output)
		return data
	#end define
	
	def Result2Dict(self, result):
		rawAny = False
		data = dict()
		tabSpaces = 2
		parenElementsList = list()
		lines = result.split('\n')
		for line in lines:
			firstSpacesCount = self.GetFirstSpacesCount(line)
			deep = firstSpacesCount // tabSpaces
			line = line.lstrip()
			if "raw@Any" in line:
				rawAny = True
			if rawAny == True and ')' in line:
				rawAny = False
			if line[:2] == "x{" and rawAny == False:
				continue
			if deep == 0:
				data[line] = dict()
				parenElementsList = [line]
			else:
				buff = data
				parenElementsList = parenElementsList[:deep]
				for item in parenElementsList:
					buff = buff[item]
				buff[line] = dict()
				parenElementsList.append(line)
			#end if
		#end for
		return data
	#end define
	
	def GetFirstSpacesCount(self, line):
		result = 0
		for item in line:
			if item == ' ':
				result += 1
			else:
				break
		#end for
		return result
	#end define
	
	def GetVarFromDict(self, data, search):
		arr = search.split('.')
		search2 = arr.pop()
		for search in arr:
			data = self.GetItemFromDict(data, search)
		text = self.GetKeyFromDict(data, search2)
		result = self.GetVar(text, search2)
		try:
			result = int(result)
		except: pass
		return result
	#end define
	
	def GetVar(self, text, search):
		if search is None or text is None:
			return
		if search not in text:
			return
		text = text[text.find(search) + len(search):]
		if text[0] in [':', '=', ' ']:
			text = text[1:]
		search2 = ')'
		if search2 in text:
			text = text[:text.find(search2)]
		search2 = ' '
		if search2 in text:
			text = text[:text.find(search2)]
		return text
	#end define
	
	def GetKeyFromDict(self, data, search):
		if data is None:
			return None
		for key, item in data.items():
			if search in key:
				return key
			#end if
		#end for
		return None
	#end define
	
	def GetItemFromDict(self, data, search):
		if data is None:
			return None
		for key, item in data.items():
			if search in key:
				return item
			#end if
		#end for
		return None
	#end define

	def NewDomain(self, domain):
		local.AddLog("start NewDomain function", "debug")
		domainName = domain["name"]
		buff = domainName.split('.')
		subdomain = buff.pop(0)
		dnsDomain = ".".join(buff)
		dnsAddr = self.GetDomainAddr(dnsDomain)
		wallet = self.GetLocalWallet(domain["walletName"])
		expireInSec = 700000 # fix me
		catId = 1 # fix me

		# Check if domain is busy
		domainEndTime = self.GetDomainEndTime(domainName)
		if domainEndTime > 0:
			raise Exception("NewDomain error: domain is busy")
		#end if

		fileName = self.tempDir + "dns-msg-body.boc"
		args = ["auto-dns.fif", dnsAddr, "add", subdomain, expireInSec, "owner", wallet.addr, "cat", catId, "adnl", domain["adnlAddr"], "-o", fileName]
		result = self.fift.Run(args)
		resultFilePath = Pars(result, "Saved to file ", ')')
		resultFilePath = self.SignBocWithWallet(wallet, resultFilePath, dnsAddr, 1.7)
		self.SendFile(resultFilePath, wallet)
		self.AddDomain(domain)
	#end define

	def AddDomain(self, domain):
		if "domains" not in local.db:
			local.db["domains"] = list()
		#end if
		local.db["domains"].append(domain)
		local.dbSave()
	#end define

	def GetDomains(self):
		domains = local.db.get("domains", list())
		for domain in domains:
			domainName = domain.get("name")
			domain["endTime"] = self.GetDomainEndTime(domainName)
		return domains
	#end define

	def GetDomain(self, domainName):
		domain = dict()
		domain["name"] = domainName
		domain["adnlAddr"] = self.GetDomainAdnlAddr(domainName)
		domain["endTime"] = self.GetDomainEndTime(domainName)
		return domain
	#end define

	def DeleteDomain(self, domainName):
		domains = local.db.get("domains")
		for domain in domains:
			if (domainName == domain.get("name")):
				domains.remove(domain)
				local.dbSave()
				return
		raise Exception("DeleteDomain error: Domain not found")
	#end define

	def GetAutoTransferRules(self):
		autoTransferRules = local.db.get("autoTransferRules")
		if autoTransferRules is None:
			autoTransferRules = list()
			local.db["autoTransferRules"] = autoTransferRules
		return autoTransferRules
	#end define

	def AddAutoTransferRule(self, rule):
		autoTransferRules = self.GetAutoTransferRules()
		autoTransferRules.append(rule)
		local.dbSave()
	#end define

	def AddBookmark(self, bookmark):
		if "bookmarks" not in local.db:
			local.db["bookmarks"] = list()
		#end if
		local.db["bookmarks"].append(bookmark)
		local.dbSave()
	#end define

	def GetBookmarks(self):
		bookmarks = local.db.get("bookmarks")
		if bookmarks is not None:
			for bookmark in bookmarks:
				self.WriteBookmarkData(bookmark)
		return bookmarks
	#end define

	def GetBookmarkAddr(self, type, name):
		bookmarks = local.db.get("bookmarks", list())
		for bookmark in bookmarks:
			bookmarkType = bookmark.get("type")
			bookmarkName = bookmark.get("name")
			bookmarkAddr = bookmark.get("addr")
			if (bookmarkType == type and bookmarkName == name):
				return bookmarkAddr
		raise Exception("GetBookmarkAddr error: Bookmark not found")
	#end define

	def DeleteBookmark(self, name, type):
		bookmarks = local.db.get("bookmarks")
		for bookmark in bookmarks:
			bookmarkType = bookmark.get("type")
			bookmarkName = bookmark.get("name")
			if (type == bookmarkType and name == bookmarkName):
				bookmarks.remove(bookmark)
				local.dbSave()
				return
		raise Exception("DeleteBookmark error: Bookmark not found")
	#end define

	def WriteBookmarkData(self, bookmark):
		type = bookmark.get("type")
		if type == "account":
			addr = bookmark.get("addr")
			account = self.GetAccount(addr)
			if account.status == "empty":
				data = "empty"
			else:
				data = account.balance
		elif type == "domain":
			domainName = bookmark.get("addr")
			endTime = self.GetDomainEndTime(domainName)
			if endTime == 0:
				data = "free"
			else:
				data = Timestamp2Datetime(endTime, "%d.%m.%Y")
		else:
			data = "null"
		bookmark["data"] = data
	#end define

	def GetSaveOffers(self):
		bname = "saveOffers"
		saveOffers = local.db.get(bname)
		if saveOffers is None:
			saveOffers = list()
			local.db[bname] = saveOffers
		return saveOffers
	#end define

	def AddSaveOffer(self, offer):
		offerHash = offer.get("hash")
		saveOffers = self.GetSaveOffers()
		if offerHash not in saveOffers:
			saveOffers.append(offerHash)
			local.dbSave()
	#end define

	def GetVotedComplaints(self):
		bname = "votedComplaints"
		votedComplaints = local.db.get(bname)
		if votedComplaints is None:
			votedComplaints = dict()
			local.db[bname] = votedComplaints
		return votedComplaints
	#end define

	def AddVotedComplaints(self, complaint):
		pseudohash = complaint.get("pseudohash")
		votedComplaints = self.GetVotedComplaints()
		if pseudohash not in votedComplaints:
			votedComplaints[pseudohash] = complaint
			local.dbSave()
	#end define

	def GetStrType(self, inputStr):
		if type(inputStr) is not str:
			result = None
		elif len(inputStr) == 48 and '.' not in inputStr:
			result = "account"
		elif ':' in inputStr:
			result = "account_hex"
		elif '.' in inputStr:
			result = "domain"
		else:
			result = "undefined"
		return result
	#end define

	def GetDestinationAddr(self, destination):
		destinationType = self.GetStrType(destination)
		if destinationType == "undefined":
			walletsNameList = self.GetWalletsNameList()
			if destination in walletsNameList:
				wallet = self.GetLocalWallet(destination)
				destination = wallet.addr
			else:
				destination = self.GetBookmarkAddr("account", destination)
		elif destinationType == "account_hex":
			destination = self.HexAddr2Base64Addr(destination)
		return destination
	#end define

	def HexAddr2Base64Addr(self, fullAddr, bounceable=True, testnet=False):
		buff = fullAddr.split(':')
		workchain = int(buff[0])
		addr_hex = buff[1]
		if len(addr_hex) != 64:
			raise Exception("HexAddr2Base64Addr error: Invalid length of hexadecimal address")
		#end if

		# Create base64 address
		b = bytearray(36)
		b[0] = 0x51 - bounceable * 0x40 + testnet * 0x80
		b[1] = workchain % 256
		b[2:34] = bytearray.fromhex(addr_hex)
		buff = bytes(b[:34])
		crc = crc16.crc16xmodem(buff)
		b[34] = crc >> 8
		b[35] = crc & 0xff
		result = base64.b64encode(b)
		result = result.decode()
		result = result.replace('+', '-')
		result = result.replace('/', '_')
		return result
	#end define
	
	def ParseBase64Addr(self, addr):
		buff = addr.replace('-', '+')
		buff = buff.replace('_', '/')
		buff = buff.encode()
		b = base64.b64decode(buff)
		bounceable_testnet = b[0:1]
		workchain_bytes = b[1:2]
		addr_bytes = b[2:34]
		crc_bytes = b[34:36]
		data = bytes(b[:34])
		crc = int.from_bytes(crc_bytes, "big")
		check_crc = crc16.crc16xmodem(data)
		if crc != check_crc:
			raise Exception("Base64Addr2HexAddr error: crc do not match")
		#end if
		
		workchain = int.from_bytes(workchain_bytes, "big", signed=True)
		addr_hex = addr_bytes.hex()
		return workchain, addr_hex
	#end define

	def GetNetLoadAvg(self, statistics=None):
		# statistics = self.GetSettings("statistics")
		if statistics is None:
			statistics = local.db.get("statistics")
		if statistics:
			netLoadAvg = statistics.get("netLoadAvg")
		else:
			netLoadAvg = [-1, -1, -1]
		return netLoadAvg
	#end define

	def GetTpsAvg(self, statistics=None):
		if statistics is None:
			statistics = local.db.get("statistics")
		if statistics:
			tpsAvg = statistics.get("tpsAvg")
		else:
			tpsAvg = [-1, -1, -1]
		return tpsAvg
	#end define

	def GetStatistics(self, name, statistics=None):
		if statistics is None:
			statistics = local.db.get("statistics")
		if statistics:
			data = statistics.get(name)
		else:
			data = [-1, -1, -1]
		return data
	#end define

	def GetSettings(self, name):
		local.dbLoad()
		result = local.db.get(name)
		return result
	#end define

	def SetSettings(self, name, data):
		try:
			data = json.loads(data)
		except: pass
		local.db[name] = data
		local.dbSave()
	#end define

	def Tlb2Json(self, text):
		# Заменить скобки
		start = 0
		end = len(text)
		if '=' in text:
			start = text.find('=')+1
		if "x{" in text:
			end = text.find("x{")
		text = text[start:end]
		text = text.strip()
		text = text.replace('(', '{')
		text = text.replace(')', '}')

		# Добавить кавычки к строкам (1 этап)
		buff = text
		buff = buff.replace('\r', ' ')
		buff = buff.replace('\n', ' ')
		buff = buff.replace('\t', ' ')
		buff = buff.replace('{', ' ')
		buff = buff.replace('}', ' ')
		buff = buff.replace(':', ' ')

		# Добавить кавычки к строкам (2 этап)
		buff2 = ""
		itemList = list()
		for item in list(buff):
			if item == ' ':
				if len(buff2) > 0:
					itemList.append(buff2)
					buff2 = ""
				itemList.append(item)
			else:
				buff2 += item
		#end for

		# Добавить кавычки к строкам (3 этап)
		i = 0
		for item in itemList:
			l = len(item)
			if item == ' ':
				pass
			elif item.isdigit() is False:
				c = '"'
				item2 = c + item + c
				text = text[:i] + item2 + text[i+l:]
				i += 2
			#end if
			i += l
		#end for

		# Обозначить тип объекта
		text = text.replace('{"', '{"_":"')

		# Расставить запятые
		while True:
			try:
				data = json.loads(text)
				break
			except json.JSONDecodeError as err:
				if "Expecting ',' delimiter" in err.msg:
					text = text[:err.pos] + ',' + text[err.pos:]
				elif "Expecting property name enclosed in double quotes" in err.msg:
					text = text[:err.pos] + '"_":' + text[err.pos:]
				else:
					print(text)
					raise err
		#end while

		return data
	#end define
	
	def SignShardOverlayCert(self, adnl, pubkey):
		local.AddLog("start SignShardOverlayCert function", "debug")
		fileName = self.tempDir + pubkey + ".cert"
		cmd = "signshardoverlaycert {workchain} {shardprefix} {pubkey} {expireat} {maxsize} {outfile}"
		cmd = cmd.format(workchain=-1, shardprefix=-9223372036854775808, pubkey=pubkey, expireat=172800, maxsize=8192, outfile=fileName)
		result = self.validatorConsole.Run(cmd)
		if "saved certificate" not in result:
			raise Exception("SignShardOverlayCert error: " + result)
		#end if
		
		file = open(fileName, 'rb')
		data = file.read()
		file.close()
		cert = base64.b64encode(data).decode("utf-8")
		
		destHex = "0:" + adnl
		destAddr = self.HexAddr2Base64Addr(destHex, bounceable=False)
		wallet = self.GetValidatorWallet(mode="vote")
		flags = ["--comment", cert]
		self.MoveCoins(wallet, destAddr, 0.001, flags=flags)
	#end define
	
	def ImportShardOverlayCert(self):
		local.AddLog("start ImportShardOverlayCert function", "debug")
		adnlAddr = self.GetAdnlAddr()
		pubkey = self.GetPubKey(adnlAddr)
		adnl = pubkey # adnl = adnlAddr
		fileName = self.tempDir + pubkey + ".cert"
		
		cert = None
		addrHex = "0:" + adnl
		addr = self.HexAddr2Base64Addr(addrHex)
		account = self.GetAccount(addr)
		history = self.GetAccountHistory(account, 10)
		vwl = self.GetValidatorsWalletsList()
		for message in history:
			src = message.src
			src = self.HexAddr2Base64Addr(src)
			if src not in vwl:
				continue
			comment = message.comment
			buff = comment.encode("utf-8")
			cert = base64.b64decode(buff)
			break
		#end for
		
		# Check certificate
		if cert is None:
			local.AddLog("ImportShardOverlayCert warning: certificate not found", "warning")
			return
		#end if
		
		file = open(fileName, 'wb')
		file.write(cert)
		file.close()
		
		self.ImportCertificate(pubkey, fileName)
	#end define
	
	def ImportCertificate(self, pubkey, fileName):
		local.AddLog("start ImportCertificate function", "debug")
		cmd = "importshardoverlaycert {workchain} {shardprefix} {pubkey} {certfile}"
		cmd = cmd.format(workchain=-1, shardprefix=-9223372036854775808, pubkey=pubkey, certfile=fileName)
		result = self.validatorConsole.Run(cmd)
	#end define
	
	def GetValidatorsWalletsList(self):
		result = list()
		vl = self.GetValidatorsList()
		for item in vl:
			walletAddr = item["walletAddr"]
			result.append(walletAddr)
		return result
	#end define
	
	def CreateNominationController(self, name, nominatorAddr, workchain=-1, subwallet=0, rewardShare=0, coverAbility=0):
		local.AddLog("start CreateNominationController function", "debug")
		walletPath = self.walletsDir + name
		contractPath = self.contractsDir + "nomination-contract/"
		if not os.path.isdir(contractPath):
			self.DownloadContract("https://github.com/EmelyanenkoK/nomination-contract")
		#end if
		
		fiftScript = contractPath + "scripts/new-nomination-controller.fif"
		args = [fiftScript, workchain, subwallet, nominatorAddr, rewardShare, coverAbility, walletPath]
		result = self.fift.Run(args)
		print("result:", result)
		version = "v3r3"
		wallet = self.GetLocalWallet(name, version)
		self.SetWalletVersion(wallet.addr, version)
	#end define
	
	def AddToNominationController(self, walletName, destAddr, amount):
		wallet = self.GetLocalWallet(walletName)
		bocPath = self.contractsDir + "nomination-contract/scripts/add-stake.boc"
		resultFilePath = self.SignBocWithWallet(wallet, bocPath, destAddr, amount)
		self.SendFile(resultFilePath, wallet)
	#end define
	
	def RequestFromNominationController(self, walletName, destAddr, amount):
		wallet = self.GetLocalWallet(walletName)
		fiftScript = self.contractsDir + "nomination-contract/scripts/request-stake.fif"
		bocPath = self.contractsDir + "nomination-contract/scripts/request-stake"
		args = [fiftScript, amount, bocPath]
		print("args:", args)
		result = self.fift.Run(args)
		bocPath = Pars(result, "Saved to file ", ")")
		print("result:", result)
		resultFilePath = self.SignBocWithWallet(wallet, bocPath, destAddr, 1)
		self.SendFile(resultFilePath, wallet)
	#end define
	
	def CreateRestrictedWallet(self, name, ownerAddr, workchain=0, subwallet=0):
		local.AddLog("start CreateRestrictedWallet function", "debug")
		walletPath = self.walletsDir + name
		contractPath = self.contractsDir + "nomination-contract/"
		if not os.path.isdir(contractPath):
			self.DownloadContract("https://github.com/EmelyanenkoK/nomination-contract")
		#end if
		
		fiftScript = contractPath + "scripts/new-restricted-wallet.fif"
		args = [fiftScript, workchain, subwallet, ownerAddr, walletPath]
		result = self.fift.Run(args)
		print("result:", result)
		version = "v3r4"
		wallet = self.GetLocalWallet(name, version)
		self.SetWalletVersion(wallet.addr, version)
	#end define
	
	def DownloadContract(self, url, branch=None):
		local.AddLog("start DownloadContract function", "debug")
		buff = url.split('/')
		gitPath = self.contractsDir + buff[-1] + '/'
		
		args = ["git", "clone", url]
		process = subprocess.run(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.contractsDir, timeout=30)
		
		if branch is not None:
			args = ["git", "checkout", branch]
			process = subprocess.run(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=gitPath, timeout=3)
		#end if
		
		if not os.path.isfile(gitPath + "build.sh"):
			return
		if not os.path.isfile("/usr/bin/func"):
			file = open("/usr/bin/func", 'wt')
			file.write("/usr/bin/ton/crypto/func $@")
			file.close()
		#end if
		
		os.makedirs(gitPath + "build", exist_ok=True)
		args = ["bash", "build.sh"]
		process = subprocess.run(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=gitPath, timeout=30)
		output = process.stdout.decode("utf-8")
		err = process.stderr.decode("utf-8")
		if len(err) > 0:
			raise Exception(err)
		#end if
	#end define
	
	def GetControllerData(self, controller):
		local.AddLog("start GetControllerData function", "debug")
		addr = controller.get("addr")
		account = self.GetAccount(addr)
		if account.status != "active":
			return
		cmd = "runmethod {addr} get_pool_data".format(addr=addr)
		result = self.liteClient.Run(cmd)
		data = self.Result2List(result)
		result = dict()
		result["vwc"] = data[0]
		result["vaddr_hash"] = data[1]
		result["nwc"] = data[2]
		result["naddr_hash"] = data[3]
		result["val_balance"] = data[4]
		result["nom_balance"] = data[5]
		result["val_request"] = data[6]
		result["nom_request"] = data[7]
		result["validator_reward_share"] = data[8]
		result["validator_cover_ability"] = data[9]
		controller["data"] = result
	#end define
#end class

class TonBlocksScanner():
	def __init__(self, ton, **kwargs):
		self.ton = ton
		self.prevMasterBlock = None
		self.prevShardsBlock = dict()
		self.blocksNum = 0
		self.transNum = 0
		self.nbr = kwargs.get("nbr") #NewBlockReaction
		self.ntr = kwargs.get("ntr") #NewTransReaction
		self.nmr = kwargs.get("nmr") #NewMessageReaction
	#end define
	
	def Run(self):
		self.StartThread(self.ScanBlocks, args=())
	#end define
	
	def StartThread(self, func, args):
		threading.Thread(target=func, args=args, name=func.__name__, daemon=True).start()
	#end define
	
	def ScanBlocks(self):
		while True:
			self.ScanBlock()
			time.sleep(1)
	#end define
	
	def ScanBlock(self):
		if self.ton.liteClient.pubkeyPath is None:
			raise Exception("ScanBlocks error: local liteserver is not configured, stop thread")
			exit()
		block = self.ton.GetLastBlock()
		self.SearchMissBlocks(block, self.prevMasterBlock)
		if block != self.prevMasterBlock:
			self.StartThread(self.ReadBlock, args=(block,))
			self.prevMasterBlock = block
	#end define

	def ReadBlock(self, block):
		self.StartThread(self.NewBlockReaction, args=(block,))
		shards = self.ton.GetShards(block)
		for shard in shards:
			self.StartThread(self.ReadShard, args=(shard,))
	#end define

	def ReadShard(self, shard):
		block = shard.get("block")
		prevBlock = self.GetShardPrevBlock(block.shardchain)
		self.SearchMissBlocks(block, prevBlock)
		#end if
		if block != prevBlock:
			self.StartThread(self.NewBlockReaction, args=(block,))
			self.SetShardPrevBlock(block)
	#end define
	
	def SearchMissBlocks(self, block, prevBlock):
		if prevBlock is None:
			return
		diff = block.seqno - prevBlock.seqno
		for i in range(1, diff):
			workchain = block.workchain
			shardchain = block.shardchain
			seqno = block.seqno - i
			self.StartThread(self.SearchBlock, args=(workchain, shardchain, seqno))
	#end define

	def SearchBlock(self, workchain, shardchain, seqno):
		block = self.ton.GetBlock(workchain, shardchain, seqno)
		self.StartThread(self.NewBlockReaction, args=(block,))
	#end define

	def GetShardPrevBlock(self, shardchain):
		prevBlock = self.prevShardsBlock.get(shardchain)
		return prevBlock
	#end define

	def SetShardPrevBlock(self, prevBlock):
		self.prevShardsBlock[prevBlock.shardchain] = prevBlock
	#end define

	def NewBlockReaction(self, block):
		#print(f"{bcolors.green} block: {bcolors.endc} {block}")
		self.blocksNum += 1
		if self.nbr:
			self.StartThread(self.nbr, args=(block,))
		transactions = self.ton.GetTransactions(block)
		for trans in transactions:
			self.StartThread(self.NewTransReaction, args=(trans,))
	#end define

	def NewTransReaction(self, trans):
		#print(f"{bcolors.magenta} trans: {bcolors.endc} {self.transNum}", "debug")
		self.transNum += 1
		if self.ntr:
			self.StartThread(self.ntr, args=(trans,))
		messageList = self.ton.GetTrans(trans)
		for message in messageList:
			self.NewMessageReaction(message)
	#end define

	def NewMessageReaction(self, message):
		if self.nmr:
			self.StartThread(self.nmr, args=(message,))
		#print(f"{bcolors.yellow} message: {bcolors.endc} {message}")
	#end define
#end class

def ng2g(ng):
	if ng is None:
		return
	return int(ng)/10**9
#end define

def Init():
	# Event reaction
	if ("-e" in sys.argv):
		x = sys.argv.index("-e")
		eventName = sys.argv[x+1]
		Event(eventName)
	#end if

	local.Run()
	
	# statistics
	local.buffer["transData"] = dict()
	local.buffer["network"] = [None]*15*6
	local.buffer["diskio"] = [None]*15*6
	
	# scan blocks
	local.buffer["masterBlocksList"] = list()
	local.buffer["prevShardsBlock"] = dict()
	local.buffer["blocksNum"] = 0
	local.buffer["transNum"] = 0
#end define

def Event(eventName):
	if eventName == "enableVC":
		EnableVcEvent()
	elif eventName == "validator down":
		ValidatorDownEvent()
	local.Exit()
#end define

def EnableVcEvent():
	local.AddLog("start EnableVcEvent function", "debug")
	# Создать новый кошелек для валидатора
	ton = MyTonCore()
	wallet = ton.CreateWallet("validator_wallet_001", -1)
	local.db["validatorWalletName"] = wallet.name

	# Создать новый ADNL адрес для валидатора
	adnlAddr = ton.CreateNewKey()
	ton.AddAdnlAddrToValidator(adnlAddr)
	local.db["adnlAddr"] = adnlAddr

	# Сохранить
	local.dbSave()
#end define

def ValidatorDownEvent():
	local.AddLog("start ValidatorDownEvent function", "debug")
	local.AddLog("Validator is down", "error")
#end define

def Elections(ton):
	ton.ReturnStake()
	ton.ElectionEntry()
#end define

def Statistics(scanner):
	ReadNetworkData()
	SaveNetworkStatistics()
	ReadTransData(scanner)
	SaveTransStatistics()
	ReadDiskData()
	SaveDiskStatistics()
#end define

def ReadDiskData():
	timestamp = GetTimestamp()
	disks = GetDisksList()
	buff = psutil.disk_io_counters(perdisk=True)
	data = dict()
	for name in disks:
		data[name] = dict()
		data[name]["timestamp"] = timestamp
		data[name]["busyTime"] = buff[name].busy_time
		data[name]["readBytes"] = buff[name].read_bytes
		data[name]["writeBytes"] = buff[name].write_bytes
		data[name]["readCount"] = buff[name].read_count
		data[name]["writeCount"] = buff[name].write_count
	#end for

	local.buffer["diskio"].pop(0)
	local.buffer["diskio"].append(data)
#end define

def SaveDiskStatistics():
	data = local.buffer["diskio"]
	data = data[::-1]
	zerodata = data[0]
	buff1 = data[1*6-1]
	buff5 = data[5*6-1]
	buff15 = data[15*6-1]
	if buff5 is None:
		buff5 = buff1
	if buff15 is None:
		buff15 = buff5
	#end if

	disksLoadAvg = dict()
	disksLoadPercentAvg = dict()
	iopsAvg = dict()
	disks = GetDisksList()
	for name in disks:
		if zerodata[name]["busyTime"] == 0:
			continue
		diskLoad1, diskLoadPercent1, iops1 = CalculateDiskStatistics(zerodata, buff1, name)
		diskLoad5, diskLoadPercent5, iops5 = CalculateDiskStatistics(zerodata, buff5, name)
		diskLoad15, diskLoadPercent15, iops15 = CalculateDiskStatistics(zerodata, buff15, name)
		disksLoadAvg[name] = [diskLoad1, diskLoad5, diskLoad15]
		disksLoadPercentAvg[name] = [diskLoadPercent1, diskLoadPercent5, diskLoadPercent15]
		iopsAvg[name] = [iops1, iops5, iops15]
	#end fore

	# save statistics
	statistics = local.db.get("statistics", dict())
	statistics["disksLoadAvg"] = disksLoadAvg
	statistics["disksLoadPercentAvg"] = disksLoadPercentAvg
	statistics["iopsAvg"] = iopsAvg
	local.db["statistics"] = statistics
#end define

def CalculateDiskStatistics(zerodata, data, name):
	if data is None:
		return None, None, None
	data = data[name]
	zerodata = zerodata[name]
	timeDiff = zerodata["timestamp"] - data["timestamp"]
	busyTimeDiff = zerodata["busyTime"] - data["busyTime"]
	diskReadDiff = zerodata["readBytes"] - data["readBytes"]
	diskWriteDiff = zerodata["writeBytes"] - data["writeBytes"]
	diskReadCountDiff = zerodata["readCount"] - data["readCount"]
	diskWriteCountDiff = zerodata["writeCount"] - data["writeCount"]
	diskLoadPercent = busyTimeDiff /1000 /timeDiff *100 # /1000 - to second, *100 - to percent
	diskLoadPercent = round(diskLoadPercent, 2)
	diskRead = diskReadDiff /timeDiff
	diskWrite = diskWriteDiff /timeDiff
	diskReadCount = diskReadCountDiff /timeDiff
	diskWriteCount = diskWriteCountDiff /timeDiff
	diskLoad = b2mb(diskRead + diskWrite)
	iops = round(diskReadCount + diskWriteCount, 2)
	return diskLoad, diskLoadPercent, iops
#end define

def GetDisksList():
	data = list()
	buff = os.listdir("/sys/block/")
	for item in buff:
		if "loop" in item:
			continue
		data.append(item)
	#end for
	data.sort()
	return data
#end define

def ReadNetworkData():
	timestamp = GetTimestamp()
	interfaceName = GetInternetInterfaceName()
	buff = psutil.net_io_counters(pernic=True)
	buff = buff[interfaceName]
	data = dict()
	data = dict()
	data["timestamp"] = timestamp
	data["bytesRecv"] = buff.bytes_recv
	data["bytesSent"] = buff.bytes_sent
	data["packetsSent"] = buff.packets_sent
	data["packetsRecv"] = buff.packets_recv

	local.buffer["network"].pop(0)
	local.buffer["network"].append(data)
#end define

def SaveNetworkStatistics():
	data = local.buffer["network"]
	data = data[::-1]
	zerodata = data[0]
	buff1 = data[1*6-1]
	buff5 = data[5*6-1]
	buff15 = data[15*6-1]
	if buff5 is None:
		buff5 = buff1
	if buff15 is None:
		buff15 = buff5
	#end if

	netLoadAvg = dict()
	ppsAvg = dict()
	networkLoadAvg1, ppsAvg1 = CalculateNetworkStatistics(zerodata, buff1)
	networkLoadAvg5, ppsAvg5 = CalculateNetworkStatistics(zerodata, buff5)
	networkLoadAvg15, ppsAvg15 = CalculateNetworkStatistics(zerodata, buff15)
	netLoadAvg = [networkLoadAvg1, networkLoadAvg5, networkLoadAvg15]
	ppsAvg = [ppsAvg1, ppsAvg5, ppsAvg15]

	# save statistics
	statistics = local.db.get("statistics", dict())
	statistics["netLoadAvg"] = netLoadAvg
	statistics["ppsAvg"] = ppsAvg
	local.db["statistics"] = statistics
#end define

def CalculateNetworkStatistics(zerodata, data):
	if data is None:
		return None, None
	timeDiff = zerodata["timestamp"] - data["timestamp"]
	bytesRecvDiff = zerodata["bytesRecv"] - data["bytesRecv"]
	bytesSentDiff = zerodata["bytesSent"] - data["bytesSent"]
	packetsRecvDiff = zerodata["packetsRecv"] - data["packetsRecv"]
	packetsSentDiff = zerodata["packetsSent"] - data["packetsSent"]
	bitesRecvAvg = bytesRecvDiff /timeDiff *8 
	bitesSentAvg = bytesSentDiff /timeDiff *8 
	packetsRecvAvg = packetsRecvDiff /timeDiff
	packetsSentAvg = packetsSentDiff /timeDiff
	netLoadAvg = b2mb(bitesRecvAvg + bitesSentAvg)
	ppsAvg = round(packetsRecvAvg + packetsSentAvg, 2)
	return netLoadAvg, ppsAvg
#end define

def ReadTransData(scanner):
	transData = local.buffer.get("transData")
	SetToTimeData(transData, scanner.transNum)
	ShortTimeData(transData)
#end define

def SetToTimeData(timeDataList, data):
	timenow = int(time.time())
	timeDataList[timenow] = data
#end define

def ShortTimeData(data, max=120, diff=20):
	if len(data) < max:
		return
	buff = data.copy()
	data.clear()
	keys = sorted(buff.keys(), reverse=True)
	for item in keys[:max-diff]:
		data[item] = buff[item]
#end define

def SaveTransStatistics():
	tps1 = GetTps(60)
	tps5 = GetTps(60*5)
	tps15 = GetTps(60*15)

	# save statistics
	statistics = local.db.get("statistics", dict())
	statistics["tpsAvg"] = [tps1, tps5, tps15]
	local.db["statistics"] = statistics
#end define

def GetDataPerSecond(data, timediff):
	if len(data) == 0:
		return
	timenow = sorted(data.keys())[-1]
	now = data.get(timenow)
	prev = GetItemFromTimeData(data, timenow-timediff)
	if prev is None:
		return
	diff = now - prev
	result = diff / timediff
	result = round(result, 2)
	return result
#end define

def GetItemFromTimeData(data, timeneed):
	if timeneed in data:
		result = data.get(timeneed)
	else:
		result = data[min(data.keys(), key=lambda k: abs(k-timeneed))]
	return result
#end define
	

def GetTps(timediff):
	data = local.buffer["transData"]
	tps = GetDataPerSecond(data, timediff)
	return tps
#end define

def GetBps(timediff):
	data = local.buffer["blocksData"]
	bps = GetDataPerSecond(data, timediff)
	return bps
#end define

def GetBlockTimeAvg(timediff):
	bps = GetBps(timediff)
	if bps is None or bps == 0:
		return
	result = 1/bps
	result = round(result, 2)
	return result
#end define

def Offers(ton):
	saveOffers = ton.GetSaveOffers()
	offers = ton.GetOffers()
	for offer in offers:
		offerHash = offer.get("hash")
		if offerHash in saveOffers:
			ton.VoteOffer(offerHash)
#end define

def Domains(ton):
	pass
#end define

def GetUname():
	data = os.uname()
	result = dict(zip('sysname nodename release version machine'.split(), data))
	result.pop("nodename")
	return result
#end define

def GetMemoryInfo():
	result = dict()
	data = psutil.virtual_memory()
	result["total"] = round(data.total / 10**9, 2)
	result["usage"] = round(data.used / 10**9, 2)
	result["usagePercent"] = data.percent
	return result
#end define

def GetSwapInfo():
	result = dict()
	data = psutil.swap_memory()
	result["total"] = round(data.total / 10**9, 2)
	result["usage"] = round(data.used / 10**9, 2)
	result["usagePercent"] = data.percent
	return result
#end define

def Telemetry(ton):
	sendTelemetry = local.db.get("sendTelemetry")
	if sendTelemetry is not True:
		return
	#end if

	# Get validator status
	data = dict()
	data["adnlAddr"] = ton.GetAdnlAddr()
	data["validatorStatus"] = ton.GetValidatorStatus()
	data["cpuNumber"] = psutil.cpu_count()
	data["cpuLoad"] = GetLoadAvg()
	data["netLoad"] = ton.GetStatistics("netLoadAvg")
	data["tps"] = ton.GetStatistics("tpsAvg")
	data["disksLoad"] = ton.GetStatistics("disksLoadAvg")
	data["disksLoadPercent"] = ton.GetStatistics("disksLoadPercentAvg")
	data["iops"] = ton.GetStatistics("iopsAvg")
	data["pps"] = ton.GetStatistics("ppsAvg")
	data["dbUsage"] = ton.GetDbUsage()
	data["memory"] = GetMemoryInfo()
	data["swap"] = GetSwapInfo()
	data["uname"] = GetUname()
	elections = local.TryFunction(ton.GetElectionEntries)
	complaints = local.TryFunction(ton.GetComplaints)

	# Get git hashes
	gitHashes = dict()
	gitHashes["mytonctrl"] = GetGitHash("/usr/src/mytonctrl")
	gitHashes["validator"] = GetGitHash("/usr/src/ton")
	data["gitHashes"] = gitHashes
	data["stake"] = local.db.get("stake")

	# Send data to toncenter server
	liteUrl_default = "https://validator.health.toncenter.com/report_status"
	liteUrl = local.db.get("telemetryLiteUrl", liteUrl_default)
	output = json.dumps(data)
	resp = requests.post(liteUrl, data=output, timeout=3)

	sendFullTelemetry = local.db.get("sendFullTelemetry")
	if sendFullTelemetry is not True:
		return
	#end if

	# Send full telemetry
	fullUrl_default = "https://validator.health.toncenter.com/report_validators"
	fullUrl = local.db.get("telemetryFullUrl", fullUrl_default)
	data = dict()
	config36 = ton.GetConfig36()
	data["currentValidators"] = ton.GetValidatorsList()
	data["nextValidators"] = config36.get("validators")
	data["elections"] = elections
	data["complaints"] = complaints

	output = json.dumps(data)
	resp = requests.post(fullUrl, data=output, timeout=3)
#end define

def Complaints(ton):
	validatorIndex = ton.GetValidatorIndex()
	if validatorIndex < 0:
		return
	#end if

	# Voting for complaints
	config32 = ton.GetConfig32()
	electionId = config32.get("startWorkTime")
	complaintsHashes = ton.SaveComplaints(electionId)
	complaints = ton.GetComplaints(electionId)
	for key, item in complaints.items():
		complaintHash = item.get("hash")
		complaintHash_hex = Dec2HexAddr(complaintHash)
		if complaintHash_hex in complaintsHashes:
			ton.VoteComplaint(electionId, complaintHash)
#end define

def Slashing(ton):
	isSlashing = local.db.get("isSlashing")
	if isSlashing is not True:
		return
	#end if

	# Creating complaints
	timestamp = GetTimestamp()
	slashTime = local.buffer.get("slashTime")
	config32 = ton.GetConfig32()
	start = config32.get("startWorkTime")
	end = config32.get("endWorkTime")
	local.AddLog("slashTime {}, start {}, end {}".format(slashTime, start, end), "debug")
	if slashTime != start:
		end -= 60
		ton.CheckValidators(start, end)
		local.buffer["slashTime"] = start
#end define

def ScanLiteServers(ton):
	# Считать список серверов
	filePath = ton.liteClient.configPath
	file = open(filePath, 'rt')
	text = file.read()
	file.close()
	data = json.loads(text)

	# Пройтись по серверам
	result = list()
	liteservers = data.get("liteservers")
	for index in range(len(liteservers)):
		try:
			ton.liteClient.Run("last", index=index)
			result.append(index)
		except: pass
	#end for

	# Записать данные в базу
	local.db["liteServers"] = result
#end define

def General():
	local.AddLog("start General function", "debug")
	ton = MyTonCore()
	scanner = TonBlocksScanner(ton)
	scanner.Run()

	# Запустить потоки
	local.StartCycle(Elections, sec=600, args=(ton, ))
	local.StartCycle(Statistics, sec=10, args=(scanner,))
	local.StartCycle(Offers, sec=600, args=(ton, ))
	local.StartCycle(Complaints, sec=600, args=(ton, ))
	local.StartCycle(Slashing, sec=600, args=(ton, ))
	local.StartCycle(Domains, sec=600, args=(ton, ))
	local.StartCycle(Telemetry, sec=60, args=(ton, ))
	local.StartCycle(ScanLiteServers, sec=60, args=(ton,))
	Sleep()
#end define

def Dec2HexAddr(dec):
	h = dec2hex(dec)
	hu = h.upper()
	h64 = hu.rjust(64, "0")
	return h64
#end define

def xhex2hex(x):
	try:
		b = x[1:]
		h = b.lower()
		return h
	except:
		return None
#end define

def hex2base64(h):
	b = bytes.fromhex(h)
	b64 = base64.b64encode(b)
	s = b64.decode("utf-8")
	return s
#end define




###
### Start of the program
###

if __name__ == "__main__":
	Init()
	General()
#end if
