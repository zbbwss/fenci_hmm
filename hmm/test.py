# -*- coding: utf-8 -*-
# Created by 'Zhou Bingbing'  on 2019/6/24


# class LMM():
#     def __init__(self, dic_path):
#         self.dictionary = set()
#         self.maximum = 0
#         # 读取词典
#         with open(dic_path, 'r', encoding='utf8') as f:
#             for line in f:
#                 line = line.strip()
#                 if not line:
#                     continue
#                 self.dictionary.add(line)
#                 if len(line) > self.maximum:
#                     self.maximum = len(line)
#
#     def cut(self, text):
#         result = []
#         index = len(text)
#         while index > 0:
#             word = None
#             for size in range(self.maximum, 0, -1):
#                 if index - size < 0:
#                     continue
#                 piece = text[(index - size):index]
#                 if piece in self.dictionary:
#                     word = piece
#                     result.append(word)
#                     index =index-size
#                     break
#             if word is None:
#                 index -= 1
#         return result[::-1]
# class RMM():
#     def __init__(self, dic_path):
#         self.dictionary = set()
#         self.maximum = 0
#         # 读取词典
#         with open(dic_path, 'r', encoding='utf8') as f:
#             for line in f:
#                 line = line.strip()
#                 if not line:
#                     continue
#                 self.dictionary.add(line)
#                 if len(line) > self.maximum:
#                     self.maximum = len(line)
#
#     def cut(self, text):
#         result = []
#         index = len(text)
#         while index > 0:
#             word = None
#             for size in range(0,self.maximum):
#                 if index - size < 0:
#                     continue
#                 piece = text[:index-size]
#                 if piece in self.dictionary:
#                     word = piece
#                     result.append(word)
#                     text = text[(index - size):index]
#                     break
#             if word is None:
#                 index -= 1
#         return result
#
# def main():
#     text='南京市长汪峰'
#     tokenizer1=RMM('./正反向匹配分词/chinese_word.txt')
#     tokenizer2=LMM('./正反向匹配分词/chinese_word.txt')
#     res1=tokenizer1.cut(text)
#     res2=tokenizer2.cut(text)
#     if len(res1)>len(res2):
#         return res2
#     else:
#         return res1
# # print(main())
# '''维护词库'''
# res=[]
# with open('cilin.txt','r',encoding='utf-8') as f:
#
#     for i in f.readlines():
#         line=i.strip().split(' ')[1:]
#         res.extend(line)
#     res1=list(set(res))
# with open('chinese_word.txt','w',encoding='utf-8') as ff:
#
#     for line in res1:
#         ff.write(line+"\n")
'''HMM 进行分词 '''


class HMM(object):
    def __init__(self):
        import os

        # 主要是用于存取算法中间结果，不用每次都训练模型
        self.model_file = './data1/hmm_model.pkl'

        # 状态值集合
        self.state_list = ['B', 'M', 'E', 'S']
        # 参数加载,用于判断是否需要重新加载model_file
        self.load_para = False
    # 用于加载已计算的中间结果，当需要重新训练时，需初始化清空结果
    def try_load_model(self, trained):
        if trained:
            import pickle
            with open(self.model_file, 'rb') as f:
                self.A_dic = pickle.load(f)
                self.B_dic = pickle.load(f)
                self.Pi_dic = pickle.load(f)
                self.load_para = True

        else:
            # 状态转移概率（状态->状态的条件概率）
            self.A_dic = {}
            # 发射概率（状态->词语的条件概率）
            self.B_dic = {}
            # 状态的初始概率
            self.Pi_dic = {}
            self.load_para = False

    # 计算转移概率、发射概率以及初始概率
    def train(self, path):
        # 重置几个概率矩阵
        self.try_load_model(False)
        # 统计状态出现次数，求p(o)
        Count_dic = {}
        # 初始化参数
        def init_parameters():
            for state in self.state_list:
                self.A_dic[state] = {s: 0.0 for s in self.state_list}
                self.Pi_dic[state] = 0.0
                self.B_dic[state] = {}
                Count_dic[state] = 0

        def makeLabel(text):
            out_text = []
            if len(text) == 1:
                out_text.append('S')
            else:
                out_text += ['B'] + ['M'] * (len(text) - 2) + ['E']
            return out_text

        init_parameters()
        line_num = -1
        # 观察者集合，主要是字以及标点等
        words = set()
        with open(path, encoding='utf8') as f:
            for line in f:
                line_num += 1
                line = line.strip()
                if not line:
                    continue
                word_list = [i for i in line if i != ' ']
                words |= set(word_list)  # 更新字的集合 字集合

                linelist = line.split() #分词

                line_state = []
                for w in linelist:
                    line_state.extend(makeLabel(w)) #[b,s,e,m,b,s,e,m,b,s,e,m]
                assert len(word_list) == len(line_state)
                for k, v in enumerate(line_state):
                    Count_dic[v] += 1 #统计状态出现的次数
                    if k == 0:
                        self.Pi_dic[v] += 1  # 每个句子的第一个字的状态，用于计算初始状态概率
                    else:
                        self.A_dic[line_state[k - 1]][v] += 1  # 计算转移概率
                        self.B_dic[line_state[k]][word_list[k]] = \
                            self.B_dic[line_state[k]].get(word_list[k], 0) + 1.0  # 计算发射概率 #这一块堪看成一个矩阵
        print(Count_dic)
        self.Pi_dic = {k: v * 1.0 / line_num for k, v in self.Pi_dic.items()} #状态  概率
        self.A_dic = {k: {k1: v1 / Count_dic[k] for k1, v1 in v.items()}
                      for k, v in self.A_dic.items()}
        # 加1平滑
        # print(self.B_dic)
        self.B_dic = {k: {k1: (v1 + 1) / Count_dic[k] for k1, v1 in v.items()}
                      for k, v in self.B_dic.items()}
        # print(self.B_dic)
        # print(self.B_dic)
        # 序列化
        import pickle
        with open(self.model_file, 'wb') as f:
            pickle.dump(self.A_dic, f)
            pickle.dump(self.B_dic, f)
            pickle.dump(self.Pi_dic, f)
        return self

    def viterbi(self, text, states, start_p, trans_p, emit_p):
        V = [{}]
        path = {}
        for y in states: #['B', 'M', 'E', 'S']
            V[0][y] = start_p[y] * emit_p[y].get(text[0], 0) #开始概率    发射概率
            path[y] = [y]
        for t in range(1, len(text)):
            V.append({})
            newpath = {}
            # 检验训练的发射概率矩阵中是否有该字
            neverSeen = text[t] not in emit_p['S'].keys() and \
                        text[t] not in emit_p['M'].keys() and \
                        text[t] not in emit_p['E'].keys() and \
                        text[t] not in emit_p['B'].keys()
            for y in states:#['B', 'M', 'E', 'S']
                emitP = emit_p[y].get(text[t], 0) if not neverSeen else 1.0  # 设置未知字单独成词   #发射概率是我们根据统计 与现场输入的结果得到
                #V=[{'M': 0.0, 'B': 0.0008479575355477435, 'E': 0.0, 'S': 0.00024068043618878063}]
                (prob, state) = max( [(V[t - 1][y0] * trans_p[y0].get(y, 0) *emitP, y0)for y0 in states if V[t - 1][y0] > 0])
                V[t][y] = prob
                newpath[y] = path[state] + [y] #上一个状态的路径最大集合+当前状态最大路径
            path = newpath
        if emit_p['M'].get(text[-1], 0) > emit_p['S'].get(text[-1], 0):
            (prob, state) = max([(V[len(text) - 1][y], y) for y in ('E', 'M')])
        else:
            (prob, state) = max([(V[len(text) - 1][y], y) for y in states])
        return (prob, path[state])

    def cut(self, text):
        import os
        if not self.load_para:
            self.try_load_model(os.path.exists(self.model_file))
        prob, pos_list = self.viterbi(text, self.state_list, self.Pi_dic, self.A_dic, self.B_dic)
        print(pos_list)
        begin, next = 0, 0
        for i, char in enumerate(text):
            pos = pos_list[i]
            if pos == 'B':
                begin = i
            elif pos == 'E':
                yield text[begin: i + 1]
                next = i + 1
            elif pos == 'S':
                yield char
                next = i + 1
        if next < len(text):
            yield text[next:]

hmm = HMM()
# hmm.train('./HMM数据集/trainCorpus.txt_utf8')
text = '泛微网络科技股份有限公司'
res = hmm.cut(text)
print(text)
print(str(list(res)))

