# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : easyJN.py
# Time       ：2021/8/19 22:56
# Author     ：郝景龙
# version    ：python 3.9
"""

import os
import sys
import ctypes
import _thread
from tkinter import Tk
from tkinter.scrolledtext import ScrolledText
import pyperclip
import time

WIDTH = 300  # 窗口宽
HEIGHT = 400  # 窗口高
ANSWER_PATH = 'std_answers.txt'  # 标准答案路径


def resource_path(relative_path):  # 获取(临时)资源路径
    if getattr(sys, 'frozen', False):  # 是否Bundle Resource
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def read_problems(text):  # 监控剪切板，读取试题并显示最终答案
    raw_head = '一:判断题（每小题2分）\n'
    start_tag = '入学测试(current)'
    end_tag = 'Copyright © 2021 All Rights Reserved. 江南大学 版权所有'
    recent_value = pyperclip.paste()
    while True:
        tmp_value = pyperclip.paste()
        if tmp_value != recent_value:
            if start_tag in tmp_value and end_tag in tmp_value:
                raw = tmp_value
                break
            else:
                recent_value = tmp_value
        time.sleep(0.1)
    raw = raw[raw.find(raw_head) + len(raw_head):]
    lines = raw.split('\n')
    i = 0
    problems = []
    for line in lines:
        if len(line) > 2 and line[0].isdigit():
            index = line.find(':')
            if index != -1:
                if line[:index].isdigit():
                    problems.append(line[index + 1:])
                    i += 1
    std_answers = read_std_answers()  # 读取标准答案
    questions = get_questions(std_answers)  # 根据标答创建questions字典
    patterns = get_longest_patterns(problems)  # 计算每个题目的最长模式串
    answers = print_answers_to_list(patterns, questions)  # 输出答案到列表
    text.configure(state='normal')
    text.delete('1.0', 'end')
    for line in answers:
        text.insert("end", line)
    text.configure(state='disabled')


def get_longest_patterns(problems):  # 计算每个题目可用于搜索的最长模式串
    longest_patterns = []
    for p in problems:
        for ch in '_（）()':
            p = p.replace(ch, ' ')
        p = p.split()
        l_pattern = max(p, key=lambda x: len(x))
        longest_patterns.append(l_pattern)
    return longest_patterns


def read_std_answers():  # 将标准答案从“std_answers.txt”文件里读取到列表answers
    txt_path = resource_path(ANSWER_PATH)
    try:
        with open(txt_path, 'r', encoding='utf-8') as file:
            raw = file.read()
            lines = raw.split('\n')
    except IOError:
        exit(-1)
    i = 0
    answers = []
    for line in lines:
        if len(line) > 2 and line[0].isdigit():
            index = line.find('、')
            if index != -1:
                if line[:index].isdigit():
                    answers.append(line)
                    i += 1
    return answers


def get_questions(std_answers):  # 从标准答案里解析出来题目和对应的答案，最终返回以题目为键答案为值的字典questions
    questions = dict()
    for std_a in std_answers:
        answers = ''
        std = std_a
        while '（' in std_a:
            left = std_a.find('（')
            right = std_a.find('）')
            answer = std_a[left + 1:right].strip()
            for ch in answer:
                if ch in 'ABCD√×EFGHIJK':
                    pass
                else:
                    break
            else:
                if ch == '√':
                    answers += '对'
                elif ch == '×':
                    answers += '错'
                else:
                    answers += answer
            std_a = std_a[right + 1:]
        else:
            questions[std] = answers
    return questions


def print_answers_to_list(patterns, questions):  # 输出答案到列表
    answers = []
    num = 1
    for T in patterns:
        for question, answer in questions.items():
            if T in question:  # 假如匹配到了题目  --↘
                answers.append('{:<4}{}\n'.format(num, answer))  # 则输出答案
                num += 1
                break
        else:
            answers.append('{:<4}{}\n'.format(num, '无'))
            num += 1
        if (num - 1) % 5 == 0:
            answers.append('\n')
    return answers


def mk_window():  # 创建窗口对象
    root = Tk()
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    # 调用api获得当前的缩放因子
    ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
    # 设置缩放因子
    root.tk.call('tk', 'scaling', ScaleFactor / 75)
    root.title("EasyJN")
    root.resizable(True, True)
    root.geometry("{}x{}+{}+{}".  # 初始化窗口大小和位置
                  format(WIDTH, HEIGHT, int(root.winfo_screenwidth() * ScaleFactor / 100 - WIDTH) // 2,
                         int(root.winfo_screenheight() * ScaleFactor / 100 - HEIGHT) // 2))
    root.attributes("-topmost", True)
    return root


if __name__ == '__main__':
    # 查询结果用GUI显示
    root = mk_window()
    text = ScrolledText(root, width=WIDTH, height=HEIGHT, font=('Times', 17))
    text.insert("end", '使用方法:\n')  # 插入文本
    text.insert("end", '进入考试界面后先按下Ctrl+A，\n然后再按下Ctrl+C，\n答案便会自动弹出。')
    text.configure(state='disabled')
    text.pack()
    _thread.start_new_thread(read_problems, (text,))  # 启动监测线程
    root.mainloop()  # 进入主消息循环 
