'''
游戏名称：爱恩斯坦棋
作者：李悦乔
'''

import random
import numpy as np
import pygame

PLAYER_RED = 1
PLAYER_BLUE = -1
HORIZONTAL = 0
VERTICAL = 1

startLayout = np.ndarray((720,6), dtype="int")
redLayoutOrder  = [[0,0], [1,0], [0,1], [2,0], [1,1], [0,2]]
blueLayoutOrder = [[4,4], [3,4], [4,3], [2,4], [3,3], [4,2]]
def NextPermutation(a):
    b = a
    idx = 99
    ''' 爬山，找到掉下来的地方 '''
    for i in range(5, 0, -1):
        if a[i]>a[i-1]:
            idx = i-1
            break
    if idx > 10:
        return b
    ''' 找到比a[idx]大一点点的数的位置 '''
    idx2 = idx
    for i in range(5, idx, -1):
        if a[i]>a[idx]:
            idx2 = i
            break
    b[idx], b[idx2] = b[idx2], b[idx]
    i=0
    while idx+1+i < 5-i:
        b[idx+1+i], b[5-i] = b[5-i], b[idx+1+i]
        i += 1
    return b

'''生成1~6的随机数'''
def RollADice():
    return random.randint(1, 6)

'''得到一个随机的25个元素的向量'''
def mat_gen():
    digit1 = random.randint(-6, -1)
    digit2 = random.randint(1, 6)
    arr = [0 for i in range(23)]
    arr.extend([i for i in range(-6, 0) if i != digit1])
    arr.extend([i for i in range(1, 7) if i != digit2])

    def shuffle(lst):
        for i in range(len(lst) - 1, 0, -1):
            p = random.randint(0, i)
            lst[i], lst[p] = lst[p], lst[i]
        return lst

    arr = shuffle(arr)[0:23]
    arr.append(digit1)
    arr.append(digit2)
    result_arr = shuffle(arr)

    return result_arr

# 游戏状态类
# 用于管理棋子、规则
class GameState:

    def __init__(self, draw=False):
        self.gameboard = np.zeros((5,5), dtype="int")
        self.draw = draw
        if draw:
            pygame.init()
            screen_size = (400, 500)
            self.screen = pygame.display.set_mode(screen_size)
            pygame.display.set_caption('Einstein')
        startLayout[0] = [1, 2, 3, 4, 5, 6]
        for i in range(1, 720):
            startLayout[i] = NextPermutation(startLayout[i-1])

    '''初始化游戏'''
    def InitializeGame(self, red_start, blue_start, start_player):
        self.gameboard = np.zeros((5,5), dtype="int")
        self.redHelper  = np.zeros((7, 2), dtype="int")
        self.blueHelper = np.zeros((7, 2), dtype="int")
        self.dice = RollADice()
        self.player = start_player
        for i in range(6):
            '''  红  '''
            v = startLayout[red_start][i]   #v=[1~6]
            row = redLayoutOrder[i][0]      #row=[0~4]
            col = redLayoutOrder[i][1]      #col=[0~4]
            self.gameboard[row, col]  = v
            self.redHelper[v, 0] = row
            self.redHelper[v, 1] = col
            '''  蓝  '''
            v = startLayout[blue_start][i]   #v=[1~6]
            row = blueLayoutOrder[i][0]
            col = blueLayoutOrder[i][1]
            self.gameboard[row, col]  = -v   # 蓝方的子为负数
            self.blueHelper[v, 0] = row
            self.blueHelper[v, 1] = col

        self.available_list = np.array([1,4])
        self.available_filter = np.array([0,1,0,0,1,0])
        return self.FromGameboardToData()

    '''得到一个随机的棋盘'''
    def GetRandomGame(self):
        '''得到一个随机的25个元素的向量'''
        arr = mat_gen()
        self.gameboard = np.asmatrix(np.reshape(arr, [5, 5]))
        self.redHelper  = np.array([[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1]])
        self.blueHelper = np.array([[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1]])
        self.dice = RollADice()
        self.player = PLAYER_RED
        for row in range(5):
            for col in range(5):
                '''  红  '''
                v = self.gameboard[row, col]
                if v>0:                         #v=[1~6]
                    self.redHelper[v, 0] = row
                    self.redHelper[v, 1] = col
                '''  蓝  '''
                if v < 0:                       # v=[-1~-6]
                    self.blueHelper[-v, 0] = row
                    self.blueHelper[-v, 1] = col
        # return self.FromGameboardToData(), self.AvailableInput(arr)
        # return self.FromGameboardToData(), self.IsFirstActionAvailable(arr)
        return self.FromGameboardToSimplifiedData(), self.AvailableInput(arr)
        # return self.FromGameboardToSimplifiedData(), self.IsFirstActionAvailable(arr)
        # return self.FromGameboardToSimplifiedData(), self.IsChessExist(arr)

    '''根据数组式的棋盘数据计算合法的输入'''
    def AvailableInput(self, arr):
        if (self.dice in arr):
            return np.array([0, 1, 0, 0, 1, 0])
        res = np.zeros([6])
        smallerChess = self.dice - 1
        while smallerChess >= 1 and smallerChess not in arr:
            smallerChess -= 1
        if smallerChess >= 1:
            res[0] = 1
            res[3] = 1
        largerChess = self.dice + 1
        while largerChess <= 6 and largerChess not in arr:
            largerChess += 1
        if largerChess <= 6:
            res[2] = 1
            res[5] = 1
        return res

    '''获取合法的输入'''
    def AvailableInputFromGameboard(self):
        return self.available_filter, self.available_list

    '''根据棋盘的原始数据计算合法的输入'''
    def __MakeAvailableInputData(self):
        chess = self.dice
        player = self.player
        helper = self.redHelper if player==PLAYER_RED else self.blueHelper
        chessExist = self.__chessExist(helper, chess)
        self.available_filter = np.array([0, 0, 0, 0, 0, 0])
        self.available_list = np.array([], dtype='int')
        smallerChess=0
        largerChess=7
        # 如果没有骰子的棋，就看有没有比骰子更小或者更大的棋
        if not chessExist:
            # 看有没有比骰子更小的棋
            smallerChess = chess - 1
            while smallerChess >= 1 and not self.__chessExist(helper, smallerChess):
                smallerChess -= 1
            # 看有没有比骰子更大的棋
            largerChess = chess + 1
            while largerChess <= 6 and not self.__chessExist(helper, largerChess):
                largerChess += 1
        # 如果有比骰子更小的棋，就设置可以向左右走
        if smallerChess >= 1 and self.__CanMoveHorizontal(smallerChess):
            self.__AppendToAvaiableInput(0)
        # 如果有骰子的棋，就设置可以向左右走
        if chessExist and self.__CanMoveHorizontal(chess):
            self.__AppendToAvaiableInput(1)
        # 如果有比骰子更大的棋，就设置可以向左右走
        if largerChess <= 6 and self.__CanMoveHorizontal(largerChess):
            self.__AppendToAvaiableInput(2)
        # 如果有比骰子更小的棋，就设置可以向 上下 走
        if smallerChess >= 1 and self.__CanMoveVertical(smallerChess):
            self.__AppendToAvaiableInput(3)
        # 如果有骰子的棋，就设置可以向 上下 走
        if chessExist and self.__CanMoveVertical(chess):
            self.__AppendToAvaiableInput(4)
        # 如果有比骰子更大的棋，就设置可以向 上下 走
        if largerChess <= 6 and self.__CanMoveVertical(largerChess):
            self.__AppendToAvaiableInput(5)

    def __AppendToAvaiableInput(self, num):
        self.available_filter[num]=1
        self.available_list = np.append(self.available_list, num)

    '''随机选择行为'''
    def GetRandomActionIndex(self):
        len = np.alen(self.available_list)
        if len==0:
            print("dice: ", self.dice)
            print(self.gameboard)
            return self.available_list[random.randrange(len)]
        else:
            return self.available_list[random.randrange(len)]

    '''根据参考概率数组选择行为。'''
    def GetActionIndex(self, reference_readout):
        return self.available_list[np.argmax(reference_readout[self.available_filter==1])]

    '''根据棋盘计算第一种选择是否合法'''
    def IsFirstActionAvailable(self, arr):
        if (self.dice in arr):
            return [0, 1]
        smallerChess = self.dice - 1
        while smallerChess >= 1 and smallerChess not in arr:
            smallerChess -= 1
        if smallerChess >= 1:
            return [1, 0]
        else:
            return [0, 1]

    '''根据棋盘计算第一种选择是否合法
       这个版本是没用的，因为不是one-hot的形式，不能训练
    '''
    def IsFirstActionAvailable_boolVersion(self, arr):
        if (self.dice in arr):
            return [0]
        smallerChess = self.dice - 1
        while smallerChess >= 1 and smallerChess not in arr:
            smallerChess -= 1
        if smallerChess >= 1:
            return [1]
        else:
            return [0]

    '''根据棋盘计算第一种选择是否合法'''
    def IsChessExist(self, arr):
        if (self.dice in arr):
            return [1, 0]
        else:
            return [0, 1]

    def __CanMoveHorizontal(self, chess):
        return (self.player == PLAYER_RED and self.redHelper[chess, 1] < 4) or (
            self.player == PLAYER_BLUE and self.blueHelper[chess, 1] > 0)

    def __CanMoveVertical(self, chess):
        return (self.player == PLAYER_RED and self.redHelper[chess, 0] < 4) or (
            self.player == PLAYER_BLUE and self.blueHelper[chess, 0] > 0)

    '''将棋盘转换为输入数据'''
    def FromGameboardToData(self):
        if self.draw:
            self.DrawGame()
        """
        14层：
        0~5，表示红方每个棋子的位置以及它的右边、下边有没有子的层，
        6~11，表示蓝方每个棋子的位置以及它的左边、上边有没有子的层，
        0~11层，空白记为0，红方的子记为正数，蓝方的子记为负数。
        12层，表示得到的骰子点数（1~6），整层数值一样。
        13层，表示轮到谁走。全PLAYER_RED表示红方，全PLAYER_BLUE表示蓝方。
        """
        output = np.zeros((5,5,14), dtype="float")
        for i in range(6):
            redRow = self.redHelper[i+1, 0]
            redColumn =self.redHelper[i+1, 1]
            if redRow>=0 and redColumn>=0:
                output[redRow, redColumn, i] = self.gameboard[redRow,redColumn]
                if redRow<4:
                    output[redRow+1, redColumn, i] = self.gameboard[redRow+1,redColumn]
                if redColumn<4:
                    output[redRow, redColumn+1, i] = self.gameboard[redRow,redColumn+1]
            blueRow = self.blueHelper[i + 1, 0]
            blueColumn = self.blueHelper[i + 1, 1]
            if blueRow>=0 and blueColumn>=0:
                output[blueRow, blueColumn, i+6] = self.gameboard[blueRow, blueColumn]
                if blueRow > 0:
                    output[blueRow - 1, blueColumn, i+6] = self.gameboard[blueRow - 1, blueColumn]
                if blueColumn > 0:
                    output[blueRow, blueColumn - 1, i+6] = self.gameboard[blueRow, blueColumn - 1]
        output[:, :, 12] = self.dice
        output[:, :, 13] = self.player
        return output

    '''将棋盘转换为输入数据'''
    def FromGameboardToSimplifiedData(self):
        if self.draw:
            self.DrawGame()
        """
        2层结构：
        """
        output = np.zeros((5,5,2), dtype="float")
        output[:, :, 0] = self.gameboard
        output[:, :, 1] = self.dice
        # for i in range(6):
        #     redRow = self.redHelper[i+1, 0]
        #     redColumn =self.redHelper[i+1, 1]
        #     if redRow>=0 and redColumn>=0:
        #         output[redRow, redColumn, 0] = self.gameboard[redRow,redColumn]
        #     blueRow = self.blueHelper[i + 1, 0]
        #     blueColumn = self.blueHelper[i + 1, 1]
        #     if blueRow>=0 and blueColumn>=0:
        #         output[blueRow, blueColumn, i+6] = self.gameboard[blueRow, blueColumn]
        #         if blueRow > 0:
        #             output[blueRow - 1, blueColumn, i+6] = self.gameboard[blueRow - 1, blueColumn]
        #         if blueColumn > 0:
        #             output[blueRow, blueColumn - 1, i+6] = self.gameboard[blueRow, blueColumn - 1]
        # output[:, :, 1] = self.dice
        return output

    '''返回“非法”结果'''
    def Illegal(self):
        return np.zeros((5,5,14)), -1, True

    '''执行一步变化'''
    def ChangeGameboard(self, number, dir):
        """
        :param number: 要处理的数值, [1~6]
        :param dir: 方向，HORIZONTAL 或者 VERTICAL
        :return: 
        """
        helper = self.redHelper if self.player==PLAYER_RED else self.blueHelper
        direction = 1 if self.player == PLAYER_RED else -1
        '''当前位置'''
        row, col = helper[number]
        '''下一个位置'''
        next_row, next_col = (row+direction, col) if dir==VERTICAL else (row, col+direction)
        '''下一个位置上的值'''
        x = self.gameboard[next_row, next_col]
        '''如果下一个位置有棋，那么将被顶掉'''
        if x!=0:
            next_helper = self.redHelper if x>0 else self.blueHelper
            if x<0: x=-x
            next_helper[x]=[-1,-1]
        '''设置棋盘上的值'''
        self.gameboard[row, col], self.gameboard[next_row, next_col] = 0, self.gameboard[row, col]
        '''设置helper的值'''
        helper[number] = [next_row, next_col]

        '''如果有输赢'''
        if self.player==PLAYER_RED:
            if next_row==4 and next_col==4:
                return self.FromGameboardToData(), 1, True
            #蓝方全没了就赢
            redWin = True
            for i in range(1, 7):
                if self.blueHelper[i,0]>=0:
                    redWin = False
                    break
            if redWin:
                return self.FromGameboardToData(), 1, True
        elif self.player==PLAYER_BLUE:
            if next_row==0 and next_col==0:
                return self.FromGameboardToData(), 1, True
            #红方全没了就赢
            blueWin = True
            for i in range(1, 7):
                if self.redHelper[i,0]>=0:
                    blueWin = False
                    break
            if blueWin:
                return self.FromGameboardToData(), 1, True

        '''扔个骰子，设置下一个玩家，然后生成Input数据结构（14层结构）'''
        self.dice = RollADice()
        self.player = -self.player
        self.__MakeAvailableInputData()
        return self.FromGameboardToData(), 0.01, False

    '''判断某个棋子是否在棋盘上'''
    def __chessExist(self, helper, chess):
        return helper[chess,0]>=0 and helper[chess,1]>=0

    '''根据ActionArray执行逻辑'''
    def step_in_mind(self, actionArray):
        '''
        a_t有6种行为，前三种表示往左（右）走，后三种表示往上（下）走
        每组三个行为分别表示比骰子小的数、骰子数、比骰子大的数
        '''
        act_idx = np.argmax(actionArray)
        chess = self.dice
        helper = self.redHelper if self.player==PLAYER_RED else self.blueHelper
        direction = 1 if self.player==PLAYER_RED else -1

        if self.__chessExist(helper, chess):
            if act_idx!=1 and act_idx!=4:
                return self.Illegal()
            if act_idx==1 and (helper[chess,1]+direction<0 or helper[chess,1]+direction>4):
                return self.Illegal()
            if act_idx==1:
                return self.ChangeGameboard(chess, HORIZONTAL)
            if act_idx==4 and (helper[chess,0]+direction<0 or helper[chess,0]+direction>4):
                return self.Illegal()
            if act_idx==4:
                return self.ChangeGameboard(chess, VERTICAL)

        ''' 来到这里，表示骰子所表示的棋子是不存在的 '''
        if act_idx==1 or act_idx==4:
            return self.Illegal()

        smallerChess = chess-1
        while smallerChess>=1 and not self.__chessExist(helper, smallerChess):
            smallerChess -= 1
        if smallerChess>=1:
            if act_idx==0 and (helper[smallerChess,1]+direction<0 or helper[smallerChess,1]+direction>4):
                return self.Illegal()
            if act_idx==0:
                return self.ChangeGameboard(smallerChess, HORIZONTAL)
            if act_idx==3 and (helper[smallerChess,0]+direction<0 or helper[smallerChess,0]+direction>4):
                return self.Illegal()
            if act_idx==3:
                return self.ChangeGameboard(smallerChess, VERTICAL)
        ''' 来到这里，表示比骰子值小的棋子是不存在的，或者act_idx为2或者5 '''
        if act_idx==0 or act_idx==3:
            return self.Illegal()

        ''' 来到这里，表示act_idx为2或者5 '''
        largerChess = chess+1
        while largerChess<=6 and not self.__chessExist(helper, largerChess):
            largerChess += 1
        if largerChess<=6:
            if act_idx==2 and (helper[largerChess,1]+direction<0 or helper[largerChess,1]+direction>4):
                return self.Illegal()
            if act_idx==2:
                return self.ChangeGameboard(largerChess, HORIZONTAL)
            if act_idx==5 and (helper[largerChess,0]+direction<0 or helper[largerChess,0]+direction>4):
                return self.Illegal()
            if act_idx==5:
                return self.ChangeGameboard(largerChess, VERTICAL)
        ''' 来到这里，表示比骰子值大的棋子是不存在的 '''
        return self.Illegal()

    '''绘制游戏'''
    def DrawGame(self):
        pygame.event.pump()
        self.screen.fill((255, 255, 255))

        ''' 计算可选行为集合 '''
        option = []
        theHelper = self.blueHelper if self.player==PLAYER_BLUE else self.redHelper
        dice = self.dice
        if self.__chessExist(theHelper, dice):
            option = [dice]
        else:
            smallerChess = dice - 1
            while smallerChess >= 1 and not self.__chessExist(theHelper, smallerChess):
                smallerChess -= 1
            if smallerChess >= 1:
                option.append(smallerChess)
            largerChess = dice + 1
            while largerChess <= 6 and not self.__chessExist(theHelper, largerChess):
                largerChess += 1
            if largerChess <= 6:
                option.append(largerChess)

        '''' 绘制内容 '''
        for r in range(5):
            for c in range(5):
                rect = (c*80, r*80, c*80+80, r*80+80)
                color = self.gameboard[r,c]
                if color == 0:
                    pygame.draw.rect(self.screen, (200,200,200), rect, 0)
                elif color > 0:
                    pygame.draw.rect(self.screen, (200, 50, 50), rect, 0)
                else:
                    pygame.draw.rect(self.screen, (50, 50, 200), rect, 0)

                if color!=0:
                    numColor = (0,0,0)
                    if self.player==PLAYER_BLUE and -color in option:
                        numColor=(218,178,115)
                    if self.player==PLAYER_RED  and  color in option:
                        numColor=(218,178,115)
                    self.show_text((c*80+35,r*80+30), '%d'% (color if color>0 else -color), numColor, font_size=40)

        pygame.draw.rect(self.screen, (255, 255, 255), (0,400,400,500), 0)
        self.show_text((0+20,400+20), u'(%d) %s rolled a dice and get %d' % (self.dice, u'BLUE' if self.player==PLAYER_BLUE else u'RED', self.dice), (200, 50, 200), font_size=32)
        pygame.display.update()

    '''绘制文本'''
    def show_text(self, pos, text, color, font_bold=False, font_size=60, font_italic=False):
        # 获取系统字体，并设置文字大小
        cur_font = pygame.font.SysFont("宋体", font_size)
        # 设置是否加粗属性
        cur_font.set_bold(font_bold)
        # 设置是否斜体属性
        cur_font.set_italic(font_italic)
        # 设置文字内容
        text_fmt = cur_font.render(text, 1, color)
        # 绘制文字
        self.screen.blit(text_fmt, pos)


