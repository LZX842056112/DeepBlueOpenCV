'''
3211. 生成不含相邻零的二进制字符串
给你一个正整数 n。
如果一个二进制字符串 x 的所有长度为 2 的子字符串中包含 至少 一个 "1"，则称 x 是一个 有效 字符串。
返回所有长度为 n 的 有效 字符串，可以以任意顺序排列。
'''


class Solution:
    def validStrings(self, n):
        strlist = ["0", "1"]
        for i in range(1, n):
            newlist = []
            for s in strlist:
                if s[-1] == "0":
                    newlist.append(s + "1")
                else:
                    newlist.append(s + "0")
                    newlist.append(s + "1")
            strlist = newlist
        return strlist


'''
3248. 矩阵中的蛇
大小为 n x n 的矩阵 grid 中有一条蛇。蛇可以朝 四个可能的方向 移动。矩阵中的每个单元格都使用位置进行标识： grid[i][j] = (i * n) + j。
蛇从单元格 0 开始，并遵循一系列命令移动。
给你一个整数 n 表示 grid 的大小，另给你一个字符串数组 commands，其中包括 "UP"、"RIGHT"、"DOWN" 和 "LEFT"。题目测评数据保证蛇在整个移动过程中将始终位于 grid 边界内。
返回执行 commands 后蛇所停留的最终单元格的位置。
'''


class Solution2:
    def finalPositionOfSnake(self, n, commands):
        table = {"UP": -n, "DOWN": n, "LEFT": -1, "RIGHT": 1}
        return sum(table[command] for command in commands)
