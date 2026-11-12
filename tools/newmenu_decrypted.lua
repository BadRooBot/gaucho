local NewMenuInfo = 
{
	Effect = "",--"zjm_rktb"
	InitX = 240, --第一个坐标X
	InitY = 0, --第一个坐标Y 
	OffsetX = 80, --偏移X
	OffsetY = 83,  --偏移Y
	LineNum = 4,   --行数
	--从1开始，越小越靠前 -1表示不做排序，并且隐藏
	[1013] = 1, --角色
	[1014] = 2, --背包
	[1006] = 3, --技能
	[1000] = 4, --锻造
	[1008] = -1, --邮件
	[1004] = 6, --帮派
	[1017] = 7, --排行
	[1011] = 8, --衣柜
	[1015] = 9, --龙魂
	[1016] = 10, --内功
	[1001] = -1, --任务
	[1007] = -1, --组队
	[1012] = 5, --江湖
	[1005] = -1, --索引
	[1010] = -1, --索引
	[1003] = -1, --好友
	[1009] = -1, --设置
	[1002] = -1, --礼包
	[1018] = 11, --兵魂
	[1400] = 12, --忍法帖
	[1211] = 13, --其他职业觉醒
	[1019] = 14, --境界
}

local ActivityMenuInfo = 
{
	InitX = 600, --第一个坐标X
	InitY = 1, --第一个坐标Y 
	OffsetX = 75, --偏移X
	OffsetY = 80,  --偏移Y
	LineNum = 9,   --行数
    --从1开始，越小越靠前 -1表示不做排序，并且隐藏
	[1003] = 1, --福利
	[1002] = 2, --每日
	[6163] = 3, --挑战
	[1007] = 4, --活动页面
	[1004] = 5, --充值
	[1008] = 6, --战令
	[1001] = 7, --竞技场
	[1010] = 8, --回归按钮
	[1011] = 9, --许愿仙境
	[1012] = 10, --0元购
	TimeOffsetX=10,--活动时间标题
	TimeOffsetY=20,--活动时间标题
}

local function GetNewMenuInfo(idx)
	return NewMenuInfo[idx]
end

local function GetAcitvityMenuInfo(idx)
	return ActivityMenuInfo[idx]
end


local NewMenu = {
    GetNewMenuInfo = GetNewMenuInfo,
	GetAcitvityMenuInfo = GetAcitvityMenuInfo,
}

-- global
NewMenu_GetNewMenuInfo = NewMenu.GetNewMenuInfo
NewMenu_GetActivityMenuInfo = GetAcitvityMenuInfo

return NewMenu
