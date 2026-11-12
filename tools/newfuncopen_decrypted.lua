local E_FUNC_NEIGONG			= 1	-- 内功功能([1809-1016])
local E_FUNC_TRAINING_VITALITY	= 2	-- 炼气([131-4027]), 气力副本(copymenu.lua), 材料挑战标签(copymenu.lua)
local E_FUNC_KONGFU				= 3	-- 自创武功功能([1809-1012]), 武功副本(copymenu.lua)
local E_FUNC_RUNE				= 4	-- 神纹功能([131-1507])
local E_FUNC_SYNDICATE			= 5	-- 帮派功能([1809-1004])
local E_FUNC_FORGE				= 6	-- 锻造([1809-1000])
local E_FUNC_SUB_PROFESSION		= 7	-- 副职业功能([131-3009])
local E_FUNC_AWAKEN 			= 8	-- 职业觉醒功能
local E_FUNC_METE 				= 9	-- (转世)血脉
local E_FUNC_PHASE 				= 10-- 境界(职业入职,晋升,境界)
local E_FUNC_INSTANCE_BUTTON 	= 11-- 主界面副本按钮([1812-6163])
local E_FUNC_HW 				= 12-- 百兵谱
local E_FUNC_ETHERSUIT 			= 13-- 境界装备([131-1508][2012-2028])
local E_FUNC_ETHERCORE 			= 14-- 境界魂石([1809-1021])
local E_FUNC_ETHERSPIRIT 		= 15-- 契约灵([2012-2029])
local E_FUNC_ARENA 				= 16-- 竞技场([1812-1001])
local E_FUNC_EVENTPAGE 			= 17-- 网页按钮([1812-1007])
local E_FUNC_RUNE_FUBEN 		= 18-- 神纹副本（部分玩家有数据，不能使用）
local E_FUNC_RUNE_UPGRADE 		= 19-- 神纹升级, 神纹分解(runesys.lua)
local E_FUNC_RUNE_FUSE	 		= 20-- 神纹合成(runesys.lua)
--------------------------------------------------
local E_FUNC_FORGE_LEVEL			= 21	-- 锻造(装备升级)
local E_FUNC_FORGE_QUALITY			= 22	-- 锻造(装备品质)
local E_FUNC_FORGE_COMPOSE			= 23	-- 锻造(装备追加)
local E_FUNC_FORGE_COMPOSE_MOUNT	= 24	-- 锻造(装备马匹追加)
local E_FUNC_FORGE_GEM				= 25	-- 锻造(宝石)
local E_FUNC_FORGE_ENCHANT_BLESS	= 26	-- 锻造(加持/神佑/降级)
local E_FUNC_FORGE_REFINERY			= 27	-- 锻造(淬炼/固化)
local E_FUNC_FORGE_SOUL				= 28	-- 锻造(神魂/固化)
local E_FUNC_FORGE_PERFECTION		= 29	-- 锻造(神品精炼)
--------------------------------------------------
local E_FUNC_PHASEBATTLE		= 30-- 境界打宝(copymenu.lua)
local E_FUNC_TOWER 				= 31-- 通天塔(copymenu.lua)
local E_FUNC_NINJA 				= 32-- 忍法帖
local E_FUNC_OTHER 				= 33-- 其他职业觉醒
local E_FUNC_JINGPO = 34 -- 精魄
local E_FUNC_XIAKE 				= 35-- 侠客觉醒
local E_FUNC_YinCang			= 1000-- 隐藏copymenu
-----server_func定义：
--1、后续12之后需的有新增都按程序定义的local E_XXX = XX来配置server_func
--2、旧server_func外部已经对不上了，但是funcflag已经打上了，1-12位的server_func不要去改动，会影响功能开放，按以下配置
--server_func=1			E_FUNC_SUB_PROFESSION 副职业功能
--server_func=2			E_FUNC_KONGFU 自创武功功能
--server_func=3			E_FUNC_SYNDICATE 帮派功能
--server_func=4			E_FUNC_TRAINING_VITALITY 炼气
--server_func=5			E_FUNC_RUNE 神纹功能
--server_func=6			E_FUNC_FORGE 锻造功能
--server_func=7			E_FUNC_NEIGONG 内功功能
--server_func=8			E_FUNC_AWAKEN 职业觉醒功能 外部未使用
--server_func=9			E_FUNC_METE 转世功能
--server_func=10		E_FUNC_PHASE 境界功能
--server_func=11		E_FUNC_INSTANCE_BUTTON 副本按钮开启
--server_func=12		E_FUNC_HW 百兵谱开启

-- 职业编号参考
-- 1	勇士
-- 2	战士
-- 4	弓手
-- 5	忍者
-- 6	武僧
-- 7	海盗
-- 8	小龙
-- 9	雷神
-- 13	水道
-- 14	火道
-- 16	铁扇


local DlgInfo = {
	-- 功能图标光效
	["Effect"] = "xgnkaiqi_tbzd",
	["EffectX"] = 65,
	["EffectY"] = 130,
	-- 窗口入场光效
	["EnterEffect"] = "xgnkfts",
	["EnterEffectX"] = 508,
	["EnterEffectY"] = 200,
	["EnterTime"] = 1000,
	["EnterEffectOblique"]=true,
	-- 自动关闭时间
	["CloseTime"] = 2000,
	-- 溜光特效
	["BindFuncEffect"] = "",
	-- 功能ID最大值
	['FuncIDMax'] = 100,	
	["NewUIPosX"] = 1000,
	["NewUIPosY"] = 190,
	["UIPosX"] = 1000,
	["UIPosY"] = 190,
	-- 预告之前的按钮状态 1:隐藏 2:灰化
	["BindLockStatus"] = 1,
	-- 预告之中的按钮状态 1:隐藏 2:灰化
	["BindTipStatus"] = 1,
}

--FuncInfo 的功能配置可添加tip_order表示预告排序
--摇杆服配置 新功能开启提示框配置
local FuncInfo = {
	-- 内功功能
	[E_FUNC_NEIGONG] = {
		-- 映射的服务端功能ID 1:副职业 2:江湖 3:爵位 4:炼气
		server_func = 7,
        -- 功能对应图片Ani
        img = "ipbtnnormal",
		-- 功能对应的名称(cn_res)
		name= "STR_NEWFUNCOPEN_DESC_1",
		-- 功能说明(cn_res)
		-- desc="STR_NEWFUNCOPEN_DESC_1",
		-- 开启条件说明(cn_res)
		condition="STR_NEWFUNCOPEN_CONDITION_EMPTY",
		-- 功能开启条件
		-- 等级
		enable_lev=290,
		-- 职业
		enable_pro={},		
		--职业等级
		enable_pro_lev=0,
		-- 转世
		enable_mete = 2,
		-- 任务ID
		enable_task=0,
		--排序
		show_order=0,
		-- 功能界面ID
		idd={
			672
		},
    },
	-- 炼气
    [E_FUNC_TRAINING_VITALITY] = {
		-- 映射的服务端功能ID 1:副职业 2:江湖 3:爵位 4:炼气
		server_func=4,
        -- 功能对应图片Ani
        img = "lqbtnnormal",
		-- 功能对应的名称(cn_res)
		name= "STR_NEWFUNCOPEN_DESC_2",
		-- 功能说明(cn_res)
		-- desc="STR_NEWFUNCOPEN_DESC_2",
		-- 开启条件说明(cn_res)
		condition="STR_NEWFUNCOPEN_CONDITION_EMPTY",
		-- 功能开启条件
		-- 等级
		enable_lev=210,
		-- 职业
		enable_pro={},		
		--职业等级
		enable_pro_lev=0,
		-- 转世
		enable_mete = 1,
		-- 任务ID
		enable_task=0,
		--排序
		show_order=0,
		-- 功能界面ID
		idd={
			588
		},
    },
	-- 自创武功功能
	[E_FUNC_KONGFU] = {
		-- 映射的服务端功能ID 1:副职业 2:江湖 3:爵位 4:炼气
		server_func=2,
        -- 功能对应图片Ani
        img = "jianghubtnnormal",
		-- 功能对应的名称(cn_res)
		name= "STR_NEWFUNCOPEN_DESC_3",
		-- 功能说明(cn_res)
		-- desc="STR_NEWFUNCOPEN_DESC_3",
		-- 开启条件说明(cn_res)
		condition="STR_NEWFUNCOPEN_CONDITION_EMPTY",
		-- 功能开启条件
		-- 等级
		enable_lev=270,
		-- 职业
		enable_pro={},
		--职业等级
		enable_pro_lev=0,
		-- 转世
		enable_mete = 2,
		-- 任务ID
		enable_task=0,
		-- 境界
		enable_phase=0,
		--排序
		show_order=0,
		-- 功能界面ID
		idd={
			619
		},
    },
	-- 神纹功能
	[E_FUNC_RUNE] = {
		-- 映射的服务端功能ID 1:副职业 2:江湖 3:爵位 4:炼气
		server_func=5,
        -- 功能对应图片Ani
        img = "shenbtnnormal",
		-- 功能对应的名称(cn_res)
		name= "STR_NEWFUNCOPEN_DESC_4",
		-- 功能说明(cn_res)
		-- desc="STR_NEWFUNCOPEN_DESC_4",
		-- 开启条件说明(cn_res)
		condition="STR_NEWFUNCOPEN_CONDITION_EMPTY",
		-- 功能开启条件
		-- 等级
		enable_lev=1,
		-- 职业
		enable_pro={},
		--职业等级
		enable_pro_lev=0,
		-- 转世
		enable_mete = 0,
		-- 任务ID
		enable_task=5109,
		-- 境界
		enable_phase=0,
		--排序
		show_order=0,
		-- 功能界面ID
		idd={
			3800
		},
    },
	-- 帮派功能
	[E_FUNC_SYNDICATE] = {
		-- 映射的服务端功能ID 1:副职业 2:江湖 3:爵位 4:炼气
		server_func=3,
        -- 功能对应图片Ani
        img = "bangpaibtnnormal",
		-- 功能对应的名称(cn_res)
		name= "STR_NEWFUNCOPEN_DESC_5",
		-- 功能说明(cn_res)
		-- desc="STR_NEWFUNCOPEN_DESC_5",
		-- 开启条件说明(cn_res)
		condition="STR_NEWFUNCOPEN_CONDITION_EMPTY",
		-- 功能开启条件
		-- 等级
		enable_lev=80,
		-- 职业
		enable_pro={},		
		--职业等级
		enable_pro_lev=0,
		-- 转世
		enable_mete = 0,
		-- 任务ID
		enable_task=0,
		-- 境界
		enable_phase=0,
		--排序
		show_order=0,
		-- 功能界面ID
		idd={
			387
		},
    },
	-- 锻造功能
	[E_FUNC_FORGE] = {
		-- 映射的服务端功能ID 1:副职业 2:江湖 3:爵位 4:炼气
		server_func=6,
        -- 功能对应图片Ani
        img = "forgingbtnnormal",
		-- 功能对应的名称(cn_res)
		name= "STR_NEWFUNCOPEN_DESC_6",
		-- 功能说明(cn_res)
		-- desc="STR_NEWFUNCOPEN_DESC_6",
		-- 开启条件说明(cn_res)
		condition="STR_NEWFUNCOPEN_CONDITION_EMPTY",
		-- 功能开启条件
		-- 等级
		enable_lev=25,
		-- 职业
		enable_pro={},		
		--职业等级
		enable_pro_lev=0,
		-- 转世
		enable_mete = 0,
		-- 任务ID
		enable_task=0,
		-- 境界
		enable_phase=0,
		--排序
		show_order=0,
		-- 功能界面ID
		idd={
			634
		},
    },
	-- 副职业功能
	[E_FUNC_SUB_PROFESSION] = {
		-- 映射的服务端功能ID 1:副职业 2:江湖 3:爵位 4:炼气
		server_func=1,
        -- 功能对应图片Ani
        img = "xgnkaiqi_fuzhiyepic",
		-- 功能对应的名称(cn_res)
		name= "STR_NEWFUNCOPEN_DESC_7",
		-- 功能说明(cn_res)
		-- desc="STR_NEWFUNCOPEN_DESC_7",
		-- 开启条件说明(cn_res)
		condition="STR_NEWFUNCOPEN_CONDITION_EMPTY",
		-- 功能开启条件
		-- 等级
		enable_lev=55,
		-- 职业
		enable_pro={},		
		--职业等级
		enable_pro_lev=0,
		-- 转世
		enable_mete = 0,
		-- 任务ID
		enable_task=0,
		-- 境界
		enable_phase=0,
		--排序
		show_order=0,
		-- 功能界面ID
		idd={
			594
		},
    },
	-- -- 职业觉醒功能
	-- [E_FUNC_AWAKEN] = {
		-- -- 映射的服务端功能ID 1:副职业 2:江湖 3:爵位 4:炼气
		-- -- server_func=0,
        -- -- 功能对应图片Ani
        -- img = "xgnkaiqi_juexingpic",
		-- -- 功能对应的名称(cn_res)
		-- name= "STR_NEWFUNCOPEN_DESC_8",
		-- -- 功能说明(cn_res)
		-- desc="STR_NEWFUNCOPEN_DESC_8",
		-- -- 开启条件说明(cn_res)
		-- condition="STR_NEWFUNCOPEN_CONDITION_8",
		-- -- 功能开启条件
		-- -- 等级
		-- enable_lev=49,
		-- -- 职业
		-- enable_pro={},
		-- -- 职业等级
		-- enable_pro_lev=0,
		-- -- 转世
		-- enable_mete = 0,
		-- -- 任务ID
		-- enable_task=0,
		-- -- 境界
		-- enable_phase = 0,
		-- -- 排序
		-- show_order=0,
		-- -- 功能界面ID
		-- idd={},
    -- },
	-- 转世功能
	[E_FUNC_METE] = {
		--境界大等级
		-- enable_phase_big_level=2,
		--境界小等级
		-- enable_phase_small_level=1,
		-- 映射的服务端功能ID 1:副职业 2:江湖 3:爵位 4:炼气
		server_func=9,
        -- 功能对应图片Ani
        img = "xmrkbtnnormal",
		-- 功能对应的名称(cn_res)
		name= "STR_NEWFUNCOPEN_DESC_9",
		-- 功能说明(cn_res)
		-- desc="STR_NEWFUNCOPEN_DESC_9",
		-- 开启条件说明(cn_res)
		condition="STR_NEWFUNCOPEN_CONDITION_EMPTY",
		-- 等级
		enable_lev=130,
		-- 职业
		enable_pro={},
		-- 职业等级
		enable_pro_lev=0,
		-- 转世
		enable_mete = 0,
		-- 任务ID
		enable_task=7669,
		-- 境界
		enable_phase = 0,
		-- 排序
		show_order=0,
		-- 功能界面ID
		idd={},
    },
	-- 境界功能
	[E_FUNC_PHASE] = {
		-- 映射的服务端功能ID 1:副职业 2:江湖 3:爵位 4:炼气
		server_func=10,
        -- 功能对应图片Ani
        img = "jjbtnnormal",
		-- 功能对应的名称(cn_res)
		name= "STR_NEWFUNCOPEN_DESC_10",
		-- 功能说明(cn_res)
		-- desc="STR_NEWFUNCOPEN_DESC_10",
		-- 开启条件说明(cn_res)
		condition="STR_NEWFUNCOPEN_CONDITION_10",
		-- 等级
		enable_lev=1,
		-- 职业
		enable_pro={},
		-- 职业等级
		enable_pro_lev=0,
		-- 转世
		enable_mete = 0,
		-- 任务ID
		enable_task=13588,
		-- 境界
		enable_phase = 0,
		-- 排序
		show_order=0,
		-- 功能界面ID
		idd={},
    },

	-- 副本按钮开启
	[E_FUNC_INSTANCE_BUTTON] = {
		-- 映射的服务端功能ID 1:副职业 2:江湖 3:爵位 4:炼气
		server_func=11,
        -- 功能对应图片Ani
        img = "tzbtnnormal",
		-- 功能对应的名称(cn_res)
		name= "STR_NEWFUNCOPEN_DESC_11",
		-- 功能说明(cn_res)
		-- desc="STR_NEWFUNCOPEN_DESC_11",
		-- 开启条件说明(cn_res)
		condition="STR_NEWFUNCOPEN_CONDITION_EMPTY",
		-- 功能开启条件
		-- 等级
		enable_lev=23,
		-- 职业
		enable_pro={},		
		--职业等级
		enable_pro_lev=0,
		-- 转世
		enable_mete = 0,
		-- 任务ID
		enable_task=0,
		--排序
		show_order=0,
		-- 功能界面ID
		idd={
			2407
		},
    },
		-- 百兵谱开启
	[E_FUNC_HW] = {
		-- 映射的服务端功能ID 1:副职业 2:江湖 3:爵位 4:炼气
		server_func=12,
        -- 功能对应图片Ani
        img = "insbtnnormal",
		-- 功能对应的名称(cn_res)
		name= "STR_NEWFUNCOPEN_DESC_12",
		-- 功能说明(cn_res)
		-- desc="STR_NEWFUNCOPEN_DESC_12",
		-- 开启条件说明(cn_res)
		condition="STR_NEWFUNCOPEN_CONDITION_EMPTY",
		-- 功能开启条件
		-- 等级
		enable_lev=1,
		-- 职业
		enable_pro={1},		
		--职业等级
		enable_pro_lev=0,
		-- 转世
		enable_mete = 0,
		-- 任务ID
		enable_task=5395,
		--排序
		show_order=0,
		-- 功能界面ID
		idd={
			1018
		},
    },
		-- 忍法帖开启
	[E_FUNC_NINJA] = {
		-- 映射的服务端功能ID 1:副职业 2:江湖 3:爵位 4:炼气
		server_func=32,
        -- 功能对应图片Ani
        img = "insbtnnormal",
		-- 功能对应的名称(cn_res)
		name= "STR_NEWFUNCOPEN_DESC_32",
		-- 功能说明(cn_res)
		-- desc="STR_NEWFUNCOPEN_DESC_12",
		-- 开启条件说明(cn_res)
		condition="STR_NEWFUNCOPEN_CONDITION_EMPTY",
		-- 功能开启条件
		-- 等级
		enable_lev=60,
		-- 职业
		enable_pro={5},		
		--职业等级
		enable_pro_lev=0,
		-- 转世
		enable_mete = 0,
		-- 任务ID
		enable_task=8721,
		--排序
		show_order=0,
		-- 功能界面ID
		idd={
			1400
		},
    },
		-- 其他职业觉醒开启
	[E_FUNC_OTHER] = {
		-- 映射的服务端功能ID 1:副职业 2:江湖 3:爵位 4:炼气
		server_func=33,
        -- 功能对应图片Ani
        img = "insbtnnormal",
		-- 功能对应的名称(cn_res)
		name= "STR_NEWFUNCOPEN_DESC_33",
		-- 功能说明(cn_res)
		-- desc="STR_NEWFUNCOPEN_DESC_12",
		-- 开启条件说明(cn_res)
		condition="STR_NEWFUNCOPEN_CONDITION_EMPTY",
		-- 功能开启条件
		-- 等级
		enable_lev=999,
		-- 职业
		enable_pro={2,4,6,7,8,9,13,14,16},		
		--职业等级
		enable_pro_lev=0,
		-- 转世
		enable_mete = 0,
		-- 任务ID
		enable_task=8873,
		--排序
		show_order=0,
		-- 功能界面ID
		idd={
			1211
		},
    },
	-- 境界装备([131-1508][2012-2028])
	[E_FUNC_ETHERSUIT] = {
		-- 映射的服务端功能ID 1:副职业 2:江湖 3:爵位 4:炼气
		server_func=13,
        -- 功能对应图片Ani
        img = "pkcompetitionbtnnormal",
		-- 功能对应的名称(cn_res)
		name= "STR_NEWFUNCOPEN_DESC_13",
		-- 功能说明(cn_res)
		-- desc="STR_NEWFUNCOPEN_DESC_13",
		-- 开启条件说明(cn_res)
		condition="STR_NEWFUNCOPEN_CONDITION_EMPTY",
		-- 功能开启条件
		-- 等级
		enable_lev=1,
		-- 职业
		enable_pro={},		
		--职业等级
		enable_pro_lev=0,
		-- 转世
		enable_mete = 0,
		-- 任务ID
		enable_task=13766,
		-- 境界
		enable_phase=0,
		--排序
		show_order=0,
		-- 功能界面ID
		idd={
		},
    },

	-- 境界魂石([1809-1021])
	[E_FUNC_ETHERCORE] = {
		-- 映射的服务端功能ID 1:副职业 2:江湖 3:爵位 4:炼气
		server_func=14,
        -- 功能对应图片Ani
        img = "hunshibtnnormal",
		-- 功能对应的名称(cn_res)
		name= "STR_NEWFUNCOPEN_DESC_14",
		-- 功能说明(cn_res)
		-- desc="STR_NEWFUNCOPEN_DESC_14",
		-- 开启条件说明(cn_res)
		condition="STR_NEWFUNCOPEN_CONDITION_EMPTY",
		-- 功能开启条件
		-- 等级
		enable_lev=1,
		-- 职业
		enable_pro={},		
		--职业等级
		enable_pro_lev=0,
		-- 转世
		enable_mete = 0,
		-- 任务ID
		enable_task=13783,
		-- 境界
		enable_phase=0,
		--排序
		show_order=0,
		-- 功能界面ID
		idd={
		},
    },
	
	
	-- 契约灵([2012-2029])
	[E_FUNC_ETHERSPIRIT] = {
		-- 映射的服务端功能ID 1:副职业 2:江湖 3:爵位 4:炼气
		server_func=15,
        -- 功能对应图片Ani
        img = "jjzb_iconqyl",
		-- 功能对应的名称(cn_res)
		name= "STR_NEWFUNCOPEN_DESC_15",
		-- 功能说明(cn_res)
		-- desc="STR_NEWFUNCOPEN_DESC_15",
		-- 开启条件说明(cn_res)
		condition="STR_NEWFUNCOPEN_CONDITION_EMPTY",
		-- 功能开启条件
		-- 等级
		enable_lev=1,
		-- 职业
		enable_pro={},		
		--职业等级
		enable_pro_lev=0,
		-- 转世
		enable_mete = 0,
		-- 任务ID
		enable_task=13765,
		-- 境界
		enable_phase=0,
		--排序
		show_order=0,
		-- 功能界面ID
		idd={
		},
    },

	-- 竞技场([1812-1001])
	[E_FUNC_ARENA] = {
		-- 映射的服务端功能ID 1:副职业 2:江湖 3:爵位 4:炼气
		server_func=E_FUNC_ARENA,
        -- 功能对应图片Ani
        img = "pkcompetitionbtnnormal",
		-- 功能对应的名称(cn_res)
		name= "STR_NEWFUNCOPEN_DESC_16",
		-- 功能说明(cn_res)
		-- desc="STR_NEWFUNCOPEN_DESC_16",
		-- 开启条件说明(cn_res)
		condition="STR_NEWFUNCOPEN_CONDITION_EMPTY",
		-- 功能开启条件
		-- 等级
		enable_lev=129,
		-- 职业
		enable_pro={},
		--职业等级
		enable_pro_lev=0,
		-- 转世
		enable_mete = 0,
		-- 任务ID
		enable_task=0,
		-- 境界
		enable_phase=0,
		--排序
		show_order=0,
		-- 功能界面ID
		idd={
		},
    },

	-- 网页按钮([1812-1007])
	[E_FUNC_EVENTPAGE] = {
		-- 映射的服务端功能ID 1:副职业 2:江湖 3:爵位 4:炼气
		server_func=E_FUNC_EVENTPAGE,
        -- 功能对应图片Ani
        img = "xgnkaiqi_qiyuelingpic",
		-- 不做弹窗展示
		disable_show=1,
		-- 功能开启条件
		-- 等级
		enable_lev=90,
		-- 职业
		enable_pro={},
		--职业等级
		enable_pro_lev=0,
		-- 转世
		enable_mete = 0,
		-- 任务ID
		enable_task=0,
		-- 境界
		enable_phase=0,
		--排序
		show_order=0,
		-- 功能界面ID
		idd={
		},
    },

	-- 境界打宝
	[E_FUNC_PHASEBATTLE] = {
		server_func=E_FUNC_PHASEBATTLE,
		-- 功能对应图片Ani
		img = "xgnkaiqi_zyrzpic",
		-- 等级
		enable_lev=1,
		-- 职业
		enable_pro={},		
		--职业等级
		enable_pro_lev=0,
		-- 转世
		enable_mete = 0,
		-- 任务ID
		enable_task=13975,
		--排序
		show_order=0,
		--境界大等级
		enable_phase_big_level=1,
		--境界小等级
		enable_phase_small_level=1,
		-- 功能界面ID
		idd={},
		--不做弹窗提示
		disable_show = 1,
	},
	
	
	-- 锻造(装备升级)
	[E_FUNC_FORGE_LEVEL] = {
		-- 映射的服务端功能ID 1:副职业 2:江湖 3:爵位 4:炼气
		server_func=E_FUNC_FORGE_LEVEL,
        -- 功能对应图片Ani
        img = "forgingbtnnormal",
		-- 功能对应的名称(cn_res)
		name= "STR_NEWFUNCOPEN_DESC_21",
		-- 功能说明(cn_res)
		-- desc="STR_NEWFUNCOPEN_DESC_21",
		-- 开启条件说明(cn_res)
		condition="STR_NEWFUNCOPEN_CONDITION_EMPTY",
		-- 功能开启条件
		-- 等级
		enable_lev=25,
		-- 职业
		enable_pro={},		
		--职业等级
		enable_pro_lev=0,
		-- 转世
		enable_mete = 0,
		-- 任务ID
		enable_task=0,
		-- 境界
		enable_phase=0,
		--排序
		show_order=0,
		-- 功能界面ID
		idd={
			631
		},
    },
	
	-- 锻造(装备品质)
	[E_FUNC_FORGE_QUALITY] = {
		-- 映射的服务端功能ID 1:副职业 2:江湖 3:爵位 4:炼气
		server_func=E_FUNC_FORGE_QUALITY,
        -- 功能对应图片Ani
        img = "forgingbtnnormal",
		-- 功能对应的名称(cn_res)
		name= "STR_NEWFUNCOPEN_DESC_22",
		-- 功能说明(cn_res)
		-- desc="STR_NEWFUNCOPEN_DESC_22",
		-- 开启条件说明(cn_res)
		condition="STR_NEWFUNCOPEN_CONDITION_EMPTY",
		-- 功能开启条件
		-- 等级
		enable_lev=30,
		-- 职业
		enable_pro={},		
		--职业等级
		enable_pro_lev=0,
		-- 转世
		enable_mete = 0,
		-- 任务ID
		enable_task=0,
		-- 境界
		enable_phase=0,
		--排序
		show_order=0,
		-- 功能界面ID
		idd={
			632
		},
    },
	
	-- 锻造(装备追加)
	[E_FUNC_FORGE_COMPOSE] = {
		-- 映射的服务端功能ID 1:副职业 2:江湖 3:爵位 4:炼气
		server_func=E_FUNC_FORGE_COMPOSE,
        -- 功能对应图片Ani
        img = "forgingbtnnormal",
		-- 功能对应的名称(cn_res)
		name= "STR_NEWFUNCOPEN_DESC_23",
		-- 功能说明(cn_res)
		-- desc="STR_NEWFUNCOPEN_DESC_23",
		-- 开启条件说明(cn_res)
		condition="STR_NEWFUNCOPEN_CONDITION_EMPTY",
		-- 功能开启条件
		-- 等级
		enable_lev=35,
		-- 职业
		enable_pro={},		
		--职业等级
		enable_pro_lev=0,
		-- 转世
		enable_mete = 0,
		-- 任务ID
		enable_task=0,
		-- 境界
		enable_phase=0,
		--排序
		show_order=0,
		-- 功能界面ID
		idd={
			335
		},
    },

	-- 锻造(装备马匹追加)
	[E_FUNC_FORGE_COMPOSE_MOUNT] = {
		-- 映射的服务端功能ID 1:副职业 2:江湖 3:爵位 4:炼气
		server_func=E_FUNC_FORGE_COMPOSE_MOUNT,
        -- 功能对应图片Ani
        img = "forgingbtnnormal",
		-- 功能对应的名称(cn_res)
		name= "STR_NEWFUNCOPEN_DESC_24",
		-- 功能说明(cn_res)
		-- desc="STR_NEWFUNCOPEN_DESC_24",
		-- 开启条件说明(cn_res)
		condition="STR_NEWFUNCOPEN_CONDITION_EMPTY",
		-- 功能开启条件
		-- 等级
		enable_lev=40,
		-- 职业
		enable_pro={},		
		--职业等级
		enable_pro_lev=0,
		-- 转世
		enable_mete = 0,
		-- 任务ID
		enable_task=0,
		-- 境界
		enable_phase=0,
		--排序
		show_order=0,
		-- 功能界面ID
		idd={
			377
		},
    },

	-- 锻造(宝石)
	[E_FUNC_FORGE_GEM] = {
		-- 映射的服务端功能ID 1:副职业 2:江湖 3:爵位 4:炼气
		server_func=E_FUNC_FORGE_GEM,
        -- 功能对应图片Ani
        img = "forgingbtnnormal",
		-- 功能对应的名称(cn_res)
		name= "STR_NEWFUNCOPEN_DESC_25",
		-- 功能说明(cn_res)
		-- desc="STR_NEWFUNCOPEN_DESC_25",
		-- 开启条件说明(cn_res)
		condition="STR_NEWFUNCOPEN_CONDITION_25",
		-- 功能开启条件
		-- 等级
		enable_lev=50,
		-- 职业
		enable_pro={},		
		--职业等级
		enable_pro_lev=0,
		-- 转世
		enable_mete = 0,
		-- 任务ID
		enable_task=0,
		-- 境界
		enable_phase=0,
		--排序
		show_order=0,
		-- 功能界面ID
		idd={
			229,422,438
		},
    },

	-- 锻造(加持)
	[E_FUNC_FORGE_ENCHANT_BLESS] = {
		-- 映射的服务端功能ID 1:副职业 2:江湖 3:爵位 4:炼气
		server_func=E_FUNC_FORGE_ENCHANT_BLESS,
        -- 功能对应图片Ani
        img = "forgingbtnnormal",
		-- 不做弹窗展示
		disable_show=1,
		-- 功能开启条件
		-- 等级
		enable_lev=95,
		-- 职业
		enable_pro={},		
		--职业等级
		enable_pro_lev=0,
		-- 转世
		enable_mete = 0,
		-- 任务ID
		enable_task=0,
		-- 境界
		enable_phase=0,
		--排序
		show_order=0,
		-- 功能界面ID
		idd={
			105,426,506
		},
    },

	-- 锻造(淬炼/固化)
	[E_FUNC_FORGE_REFINERY] = {
		-- 映射的服务端功能ID 1:副职业 2:江湖 3:爵位 4:炼气
		server_func=E_FUNC_FORGE_REFINERY,
        -- 功能对应图片Ani
        img = "forgingbtnnormal",
		-- 不做弹窗展示
		disable_show=1,
		-- 功能开启条件
		-- 等级
		enable_lev=130,
		-- 职业
		enable_pro={},		
		--职业等级
		enable_pro_lev=0,
		-- 转世
		enable_mete = 0,
		-- 任务ID
		enable_task=0,
		-- 境界
		enable_phase=0,
		--排序
		show_order=0,
		-- 功能界面ID
		idd={
			633
		},
    },
	
	-- 锻造(神魂/固化)
	[E_FUNC_FORGE_SOUL] = {
		-- 映射的服务端功能ID 1:副职业 2:江湖 3:爵位 4:炼气
		server_func=E_FUNC_FORGE_SOUL,
        -- 功能对应图片Ani
        img = "forgingbtnnormal",
		-- 不做弹窗展示
		disable_show=1,
		-- 功能开启条件
		-- 等级
		enable_lev=250,
		-- 职业
		enable_pro={},		
		--职业等级
		enable_pro_lev=0,
		-- 转世
		enable_mete = 1,
		-- 任务ID
		enable_task=0,
		-- 境界
		enable_phase=0,
		--排序
		show_order=0,
		-- 功能界面ID
		idd={
			455
		},
    },
	
	-- 锻造(神品精炼)
	[E_FUNC_FORGE_PERFECTION] = {
		-- 映射的服务端功能ID 1:副职业 2:江湖 3:爵位 4:炼气
		server_func=E_FUNC_FORGE_PERFECTION,
        -- 功能对应图片Ani
        img = "forgingbtnnormal",
		-- 不做弹窗展示
		disable_show=1,
		-- 功能开启条件
		-- 等级
		enable_lev=180,
		-- 职业
		enable_pro={},		
		--职业等级
		enable_pro_lev=0,
		-- 转世
		enable_mete = 1,
		-- 任务ID
		enable_task=0,
		-- 境界
		enable_phase=0,
		--排序
		show_order=0,
		-- 功能界面ID
		idd={
			784,789,785,786
		},
    },

	-- 通天塔
	[E_FUNC_TOWER] = {
		server_func=E_FUNC_TOWER,
		-- 功能对应图片Ani
		img = "sstbtnnormal",
		-- 等级
		enable_lev=23,
		-- 职业
		enable_pro={},		
		--职业等级
		enable_pro_lev=0,
		-- 转世
		enable_mete = 0,
		-- 任务ID
		enable_task=0,
		--排序
		show_order=0,
		-- 功能界面ID
		idd={},
		--不做弹窗提示
		disable_show = 1,
	},
	
	-- 神纹升级, 神纹分解(runesys.lua)
	[E_FUNC_RUNE_UPGRADE] = {
		server_func=E_FUNC_RUNE_UPGRADE,
		-- 功能对应图片Ani
		img = "shenbtnnormal",
		-- 功能对应的名称(cn_res)
		name= "STR_NEWFUNCOPEN_DESC_19",
		-- 功能说明(cn_res)
		-- desc="STR_NEWFUNCOPEN_DESC_19",
		-- 开启条件说明(cn_res)
		condition="STR_NEWFUNCOPEN_CONDITION_EMPTY",
		-- 功能开启条件
		-- 等级
		enable_lev=1,
		-- 职业
		enable_pro={},
		--职业等级
		enable_pro_lev=0,
		-- 转世
		enable_mete = 0,
		-- 任务ID
		enable_task=14037,
		-- 境界
		enable_phase=0,
		--排序
		show_order=0,
		-- 功能界面ID
		idd={
		},
	},
	
	-- 神纹升级, 神纹分解(runesys.lua)
	[E_FUNC_RUNE_FUSE] = {
		server_func=E_FUNC_RUNE_FUSE,
		-- 功能对应图片Ani
		img = "shenbtnnormal",
		-- 功能对应的名称(cn_res)
		name= "STR_NEWFUNCOPEN_DESC_20",
		-- 功能说明(cn_res)
		-- desc="STR_NEWFUNCOPEN_DESC_20",
		-- 开启条件说明(cn_res)
		condition="STR_NEWFUNCOPEN_CONDITION_EMPTY",
		-- 功能开启条件
		-- 等级
		enable_lev=80,
		-- 职业
		enable_pro={},
		--职业等级
		enable_pro_lev=0,
		-- 转世
		enable_mete = 1,
		-- 任务ID
		enable_task=5898,
		-- 境界
		enable_phase=0,
		--排序
		show_order=0,
		-- 功能界面ID
		idd={
		},
	},

    -- 精魄开启
    [E_FUNC_JINGPO] = {
		-- 映射的服务端功能ID
        server_func = 34,
        -- 功能对应图片Ani
        img = "insbtnnormal",
        -- 功能对应的名称(cn_res)
        name = "STR_NEWFUNCOPEN_DESC_34",
        -- 功能说明(cn_res)
        -- desc="STR_NEWFUNCOPEN_DESC_12",
        -- 开启条件说明(cn_res)
        condition = "STR_NEWFUNCOPEN_CONDITION_EMPTY",
        -- 功能开启条件
        -- 等级
        enable_lev = 220,
        -- 职业
        enable_pro = {},
        -- 职业等级
        enable_pro_lev = 0,
        -- 转世
        enable_mete = 0,
        -- 任务ID
        enable_task = 9019,
        -- 排序
        show_order = 0,
        -- 功能界面ID
        idd = {3824}
    },
		-- 侠客觉醒开启
	[E_FUNC_XIAKE] = {
		-- 映射的服务端功能ID 1:副职业 2:江湖 3:爵位 4:炼气
		server_func=35,
        -- 功能对应图片Ani
        img = "insbtnnormal",
		-- 功能对应的名称(cn_res)
		name= "STR_NEWFUNCOPEN_DESC_35",
		-- 功能说明(cn_res)
		-- desc="STR_NEWFUNCOPEN_DESC_12",
		-- 开启条件说明(cn_res)
		condition="STR_NEWFUNCOPEN_CONDITION_EMPTY",
		-- 功能开启条件
		-- 等级
		enable_lev=1,
		-- 职业
		enable_pro={3},		
		--职业等级
		enable_pro_lev=0,
		-- 转世
		enable_mete = 0,
		-- 任务ID
		enable_task=9099,
		--排序
		show_order=0,
		-- 功能界面ID
		idd={
			2701
		},
    },
}

-- 遍历数组
function IsInTable(value, tbl)
	for k,v in ipairs(tbl) do
	  if v == value then
	  return true;
	  end
	end
	return false;
end

local function GetDlgInfo(key, default)
	local ret = DlgInfo[key]
	if (ret == nil) then
		return default
	end
	return ret
end

local function GetFuncInfo(id, key, default)
	local tInfo = FuncInfo[id]
	
	if (tInfo == nil) then
		return default
	end
	
	local ret = tInfo[key]
	if (ret == nil) then
		return default
	end
	
	return ret
end

-- 返回窗口ID对应的功能ID
local function GetFuncIDByDialog(idd)
	for k , v in pairs(FuncInfo) do
		-- 
		if ((v["idd"] ~= nil) and (#(v["idd"]) > 0) and IsInTable(idd, v["idd"])) then
			return k
		end
	end
	
	return 0
end

-- 检查功能是否开启，功能未找到也返回true
-- 客户端根据该函数判定功能是否开启，如不符合预期，请检查该函数是否出错
-- 功能id，等级，职业,职业等级,物品ID,任务ID
local function TestShowCondition(id, lev, pro, pro_lev, mete, power)

	--[[
	local tInfo = FuncInfo

    if (not tInfo[id]) then
        return true
	-- 等级
    elseif (lev < tInfo[id].show_lev) then
        return false
	-- 职业
	elseif ((tInfo[id].show_pro ~= nil)and (#(tInfo[id].show_pro) > 0) and ~IsInTable(pro,tInfo[id].show_pro)) then
		return false
	-- 职业等级
	elseif ((tInfo[id].show_pro_lev ~= nil) and (pro_lev < tInfo[id].show_pro_lev)) then
		return false
	elseif ((tInfo[id].show_power ~= nil) and (power < tInfo[id].show_power)) then
		return false
    end
	]]
	
    return true
end

-- 检查功能是否开启，功能未找到也返回true
-- bigPhaseLevel 境界大等级
-- smallPhaseLevel 境界小等级
local function TestEnableConditionByPhase(id, bigPhaseLevel,smallPhaseLevel)
	local tInfo = FuncInfo
	
	if (not tInfo[id]) then
        return true
	end
	
	-- 境界
	if (tInfo[id].enable_phase_big_level ~= nil and tInfo[id].enable_phase_small_level ~= nil) then
		if bigPhaseLevel < tInfo[id].enable_phase_big_level then
			return false
		end
		
		if bigPhaseLevel == tInfo[id].enable_phase_big_level then
			if smallPhaseLevel < tInfo[id].enable_phase_small_level then
				return false
			end
		end 
	end
	
	return true
end

-- 检查功能是否开启，功能未找到也返回true
-- 客户端根据该函数判定功能是否开启，如不符合预期，请检查该函数是否出错
-- 功能id，等级，职业,职业等级,转世, 是否已完成相应的任务
-- old_server_flag 旧的服务器功能标志位
-- new_server_flag 新的服务器功能标志位
local function TestEnableCondition(id, lev, pro, pro_lev, mete, finish_task, old_server_flag, new_server_flag)

	local tInfo = FuncInfo
	
	if (not tInfo[id]) then
        return true
	end
	
	-- 最大等级,当前实际等级=转数*最大等级+lev
	local max_lev = 130
	local enable_mete = tInfo[id].enable_mete
	local enable_lev = tInfo[id].enable_lev
	
	-- 功能启用实际等级要求=转世*最大等级 + enable_lev
	if enable_mete == nil then
		enable_mete = 0
	end	
	enable_lev = enable_mete * max_lev + enable_lev

	-- 玩家当前等级=转世*最大等级 + lev
	if mete == nil then
		mete = 0
	end	
	
	-- 特转以上，都视为2转
	if mete >= 3 then
		mete = 2
	end	
	
	lev = mete * max_lev + lev	
	
	
	if old_server_flag == nil then
		old_server_flag = 0
	end
	
	if new_server_flag == nil then
		new_server_flag = 0
	end
	
	if (not tInfo[id]) then
        return true
	end
	
	-- 任务未完成&标志位未标记 => 未开启
	if (finish_task == false) and (old_server_flag == 0) and (new_server_flag == 0) then
		return false
	end
	
	-- 等级不满足&标志位未标记 => 未开启
	if (lev < enable_lev) and (old_server_flag == 0) and (new_server_flag == 0) then
		return false
	end
	
	-- 职业不满足时,标志位不参与判断
	if ((tInfo[id].enable_pro~=nil) and (#(tInfo[id].enable_pro) > 0) and (false == IsInTable(pro,tInfo[id].enable_pro))) then
		return false
	end

	-- 职业等级不满足时,标志位不参与判断
	if ((tInfo[id].enable_pro_lev ~= nil) and (pro_lev < tInfo[id].enable_pro_lev)) then
		return false
	end
	-- 境界
	--elseif ((tInfo[id].enable_phase ~= nil) and (phase < tInfo[id].enable_phase)) then
	--	return false
	
    return true
end


local function Unload()
	GetDlgInfo 			= nil
    GetFuncInfo 		= nil
	TestShowCondition	= nil
	TestEnableCondition = nil
end

local NewFuncOpenCfg= {
    GetDlgInfo = GetDlgInfo,
	GetFuncInfo = GetFuncInfo,
	GetFuncIDByDialog = GetFuncIDByDialog,
    TestShowCondition = TestShowCondition,
	TestEnableCondition = TestEnableCondition,
	GetFuncIDByDialog = GetFuncIDByDialog,
	TestEnableConditionByPhase = TestEnableConditionByPhase,
    Unload = Unload,
}

-- global
NewFuncOpenCfg_GetFuncIDByDialog = NewFuncOpenCfg.GetFuncIDByDialog
NewFuncOpenCfg_GetDlgInfo = NewFuncOpenCfg.GetDlgInfo
NewFuncOpenCfg_GetFuncInfo = NewFuncOpenCfg.GetFuncInfo
NewFuncOpenCfg_TestShowCondition = NewFuncOpenCfg.TestShowCondition
NewFuncOpenCfg_TestEnableCondition = NewFuncOpenCfg.TestEnableCondition
NewFuncOpenCfg_TestEnableConditionByPhase = NewFuncOpenCfg.TestEnableConditionByPhase
NewFuncOpenCfg_Unload = NewFuncOpenCfg.Unload

return NewFuncOpenCfg