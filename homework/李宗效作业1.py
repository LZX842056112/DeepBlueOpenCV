'''
2974.最小数字游戏
你有一个下标从 0 开始、长度为 偶数 的整数数组 nums ，同时还有一个空数组 arr 。Alice 和 Bob 决定玩一个游戏，游戏中每一轮 Alice 和 Bob 都会各自执行一次操作。游戏规则如下：
每一轮，Alice 先从 nums 中移除一个 最小 元素，然后 Bob 执行同样的操作。
接着，Bob 会将移除的元素添加到数组 arr 中，然后 Alice 也执行同样的操作。
游戏持续进行，直到 nums 变为空。
返回结果数组 arr 。

'''


class Solution:
    def numberGame(self, nums):
        nums.sort()
        for i in range(0, len(nums), 2):
            nums[i], nums[i + 1] = nums[i + 1], nums[i]
        return nums


'''
2798. 满足目标工作时长的员工数目
公司里共有 n 名员工，按从 0 到 n - 1 编号。每个员工 i 已经在公司工作了 hours[i] 小时。
公司要求每位员工工作 至少 target 小时。
给你一个下标从 0 开始、长度为 n 的非负整数数组 hours 和一个非负整数 target 。
请你用整数表示并返回工作至少 target 小时的员工数。
'''


class Solution2:
    def numberOfEmployeesWhoMetTarget(self, hours, target: int) -> int:
        return sum(1 for i in hours if i >= target)
